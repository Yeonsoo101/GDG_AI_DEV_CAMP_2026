from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from content_creation_studio.config import MODEL_NAME, RETRY_CONFIG

intake_agent = Agent(
    name="intake_agent",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY_CONFIG),
    instruction="""
    You are a content brief analyzer. From the user's request, identify:
    - Main topic
    - Target audience
    - Desired tone
    - Key SEO keywords (comma-separated)

    Output a structured brief in this exact format:
    Topic: <topic>
    Audience: <audience>
    Tone: <tone>
    Keywords: <keywords>
    """,
    output_key="content_brief"
)
