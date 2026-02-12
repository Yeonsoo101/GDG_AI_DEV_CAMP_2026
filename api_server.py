"""FastAPI server to expose the content creation agent."""

import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

# Load environment variables
load_dotenv()

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.genai.types import Content, Part

# Import agents
from content_creation_studio.agent import root_agent, full_content_workflow, content_analyzer_agent

# Map sub-agent names to frontend channel names.
# With sub_agents (not AgentTool), inner events propagate — each agent's
# final response arrives as a separate event with its own author.
CHANNEL_MAP = {
    "blog_post_writer_agent": "blog_post",
    "social_media_creator_agent": "social_media",
    "email_newsletter_writer_agent": "email_newsletter",
    "seo_metadata_agent": "seo_metadata",
}

# Initialize FastAPI app
app = FastAPI(title="Content Creation Studio API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
APP_NAME = "content_creation_studio"
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
memory_service = InMemoryMemoryService()
logging_plugin = LoggingPlugin()


class ContentRequest(BaseModel):
    """Request model for content creation."""
    topic: str
    target_audience: str
    tone: str
    keywords: str
    session_id: Optional[str] = None


class AnalyzeRequest(BaseModel):
    """Request model for text analysis."""
    text: str


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Content Creation Studio API is running",
    }


@app.post("/api/create-content")
async def create_content(request: ContentRequest):
    """
    Run through root_agent (master orchestrator) — same path as deployed Agent Engine.
    Orchestrator delegates to content_creation_tool (AgentTool → full_content_workflow).
    """
    try:
        user_id = "web_user_001"

        query = (
            f"Create a complete content package for:\n"
            f"- Topic: {request.topic}\n"
            f"- Target Audience: {request.target_audience}\n"
            f"- Tone: {request.tone}\n"
            f"- Keywords: {request.keywords}"
        )

        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
        )

        runner = Runner(
            agent=root_agent,
            session_service=session_service,
            artifact_service=artifact_service,
            memory_service=memory_service,
            plugins=[logging_plugin],
            app_name=APP_NAME,
        )

        async def generate():
            """Stream events from the workflow. With sub_agents, inner events
            propagate — each content agent emits its own event with a distinct author."""
            try:
                event_count = 0
                channels_received = set()

                yield f"data: {json.dumps({'type': 'status', 'message': 'Starting content creation...', 'session_id': session.id})}\n\n"

                async for event in runner.run_async(
                    user_id=user_id,
                    session_id=session.id,
                    new_message=Content(parts=[Part(text=query)], role="user")
                ):
                    event_count += 1
                    author = getattr(event, 'author', 'system')

                    # Check if this event is from a content channel agent
                    channel = CHANNEL_MAP.get(author)

                    if channel and event.content and event.content.parts:
                        text = event.content.parts[0].text
                        if text:
                            channels_received.add(channel)
                            yield f"data: {json.dumps({'type': 'content_piece', 'channel': channel, 'content': text})}\n\n"
                    elif not event.is_final_response():
                        # Progress updates for intermediate events
                        event_data = {'type': 'event', 'event_id': event_count, 'author': author}
                        yield f"data: {json.dumps(event_data)}\n\n"

                if channels_received:
                    yield f"data: {json.dumps({'type': 'complete', 'session_id': session.id})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'No content received from agents', 'retryable': True})}\n\n"

            except Exception as e:
                error_message = str(e)
                if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
                    friendly = "The AI service is temporarily busy. Please wait a moment and try again."
                    retryable = True
                elif "TaskGroup" in error_message:
                    friendly = "Some content channels had issues during generation. Please try again."
                    retryable = True
                elif "500" in error_message or "503" in error_message:
                    friendly = "The AI service experienced a temporary issue. Please try again."
                    retryable = True
                else:
                    friendly = "An unexpected error occurred. Please try again."
                    retryable = False
                print(f"Error detail: {error_message}")
                yield f"data: {json.dumps({'type': 'error', 'message': friendly, 'retryable': retryable})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-text")
async def analyze_text(request: AnalyzeRequest):
    """Run content_analyzer_agent directly."""
    try:
        user_id = "web_user_001"
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id
        )

        runner = Runner(
            agent=content_analyzer_agent,
            session_service=session_service,
            artifact_service=artifact_service,
            memory_service=memory_service,
            plugins=[logging_plugin],
            app_name=APP_NAME,
        )

        final_response = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=Content(parts=[Part(text=f"Analyze this text:\n\n{request.text}")], role="user")
        ):
            if event.is_final_response() and event.content and event.content.parts:
                text = event.content.parts[0].text
                if text:
                    final_response = text
                    break

        if not final_response:
            return {"status": "error", "analysis": "Could not analyze the text. Please try again."}

        return {"status": "success", "analysis": final_response}

    except Exception as e:
        error_message = str(e)
        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            raise HTTPException(status_code=503, detail="The AI service is temporarily busy. Please try again.")
        raise HTTPException(status_code=500, detail="An error occurred during analysis. Please try again.")


class MemorySearchRequest(BaseModel):
    query: str


@app.post("/api/memory/save/{session_id}")
async def save_session_to_memory(session_id: str):
    """Save a session's conversation to long-term memory."""
    try:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id="web_user_001",
            session_id=session_id
        )
        await memory_service.add_session_to_memory(session)
        return {"status": "success", "message": f"Session {session_id} saved to memory"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memory/search")
async def search_memory(request: MemorySearchRequest):
    """Search long-term memory for past conversations."""
    try:
        results = await memory_service.search_memory(
            app_name=APP_NAME,
            user_id="web_user_001",
            query=request.query
        )
        memories = []
        if results and results.memories:
            for memory in results.memories:
                if memory.content and memory.content.parts:
                    memories.append(memory.content.parts[0].text)
        return {"query": request.query, "memories": memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/artifacts/{session_id}")
async def list_artifacts(session_id: str):
    """List all artifacts saved during a session."""
    try:
        filenames = await artifact_service.list_artifact_keys(
            app_name=APP_NAME,
            user_id="web_user_001",
            session_id=session_id
        )
        return {"session_id": session_id, "artifacts": filenames}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/artifacts/{session_id}/{filename}")
async def get_artifact(session_id: str, filename: str):
    """Retrieve a specific artifact by filename."""
    try:
        artifact = await artifact_service.load_artifact(
            app_name=APP_NAME,
            user_id="web_user_001",
            session_id=session_id,
            filename=filename
        )
        if artifact and artifact.text:
            return {"filename": filename, "content": artifact.text}
        raise HTTPException(status_code=404, detail=f"Artifact '{filename}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    if not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not found in environment variables!")
        exit(1)

    print("Starting Content Creation Studio API Server")
    print("Server will be available at: http://localhost:8000")
    print("API Docs at: http://localhost:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000)
