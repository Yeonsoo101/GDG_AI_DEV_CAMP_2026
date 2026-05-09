"""
Callbacks for the Content Creation Studio.

ADK supports 6 callback types that intercept agent execution at key points:
  - before_agent_callback / after_agent_callback
  - before_model_callback / after_model_callback
  - before_tool_callback / after_tool_callback

Return None to proceed normally, or return a specific object to override behavior.
"""

import time
import logging
from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.genai import types

logger = logging.getLogger(__name__)

# Track agent start times for duration logging
_agent_execution_tracker: dict[str, float] = {}

BLOCKED_TOPICS = ["violence", "illegal", "harmful", "hate speech"]


def _extract_session_id(session) -> str:
    """Safely extract session ID from a session object. PROVIDED — do not modify."""
    if session is None:
        return "unknown"
    return getattr(session, 'id', getattr(session, 'session_id', 'unknown'))


# =============================================================================
# AGENT CALLBACKS
# =============================================================================

def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    agent_name = callback_context.agent_name
    session = callback_context._invocation_context.session
    session_id = _extract_session_id(session)
    print(f"\n{'─'*50}")
    print(f"▶ AGENT START: {agent_name}")
    print(f"{'─'*50}")
    execution_key = f"{agent_name}:{session_id}"
    _agent_execution_tracker[execution_key] = time.time()
    return None  # Proceed normally


async def after_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    try:
        memory_service = callback_context._invocation_context.memory_service
        session = callback_context._invocation_context.session
        agent_name = getattr(callback_context, 'agent_name', 'unknown')
        session_id = _extract_session_id(session)
        execution_key = f"{agent_name}:{session_id}"
        if execution_key in _agent_execution_tracker:
            total_execution_time = time.time() - _agent_execution_tracker.pop(execution_key)
            print(f"\n{'─'*50}")
            print(f"■ AGENT DONE: {agent_name} ({total_execution_time:.1f}s)")
            print(f"{'─'*50}")
            if total_execution_time > 20:
                logger.warning("Slow agent: %s took %.2fs", agent_name, total_execution_time)
        if memory_service and hasattr(memory_service, 'add_session_to_memory'):
            events = getattr(session, 'events', [])
            await memory_service.add_session_to_memory(session)
            print(f"  💾 Session saved to memory ({len(events)} events)")
    except Exception as e:
        logger.error("after_agent_callback error: %s", e)
    return None


# =============================================================================
# MODEL CALLBACKS
# =============================================================================
BLOCKED_TOPICS = ["violence", "illegal", "harmful", "hate speech"]

def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    agent_name = callback_context.agent_name
    print(f"  🤖 Calling model for {agent_name}...")
    for content in reversed(llm_request.contents or []):
        if content.role == "user":
            for part in (content.parts or []):
                text = (part.text or "").lower()
                for topic in BLOCKED_TOPICS:
                    if topic in text:
                        print(f"  🛡️ GUARDRAIL: Blocked request containing '{topic}'")
                        return LlmResponse(
                            content=types.Content(
                                parts=[types.Part.from_text(
                                    text=f"I cannot generate content about '{topic}'. Please provide a different topic."
                                )],
                                role="model"
                            )
                        )
            break  # only check the most recent user message
    return None  # Proceed with the model call


def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse
) -> Optional[LlmResponse]:
    agent_name = callback_context.agent_name
    if llm_response.content and llm_response.content.parts:
        text = llm_response.content.parts[0].text or ""
        word_count = len(text.split())
        print(f"  ✅ Model responded for {agent_name}: ~{word_count} words")
    else:
        print(f"  ⚠️ Model responded for {agent_name} with empty content")
    return None  # Use the model response as-is
def before_tool_callback(
    callback_context: CallbackContext,
    tool_call: types.ToolCall
) -> None:
    agent_name = callback_context.agent_name
    tool_name = tool_call.function_call.name
    print(f"  🛠️  TOOL START: {agent_name} calling {tool_name}...")


def after_tool_callback(
    callback_context: CallbackContext,
    tool_response: types.ToolResponse
) -> None:
    agent_name = callback_context.agent_name
    tool_name = tool_response.function_response.name
    print(f"  🏁 TOOL DONE: {agent_name} finished {tool_name}")    