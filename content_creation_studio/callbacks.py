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
from datetime import datetime, timezone
from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.genai import types

logger = logging.getLogger(__name__)

# Track agent start times for duration logging
_agent_execution_tracker: dict[str, float] = {}


def _extract_session_id(session) -> str:
    """Safely extract session ID from a session object."""
    if session is None:
        return "unknown"
    return getattr(session, 'id', getattr(session, 'session_id', 'unknown'))


# =============================================================================
# AGENT CALLBACKS
# =============================================================================

def inject_current_date(callback_context: CallbackContext) -> Optional[types.Content]:
    """Write today's UTC date into session state under `current_date`.

    Idempotent: the first agent to run in a session populates the value,
    every subsequent agent finds it already there and skips. Attached as
    `before_agent_callback` on every leaf agent that references
    {{current_date}} so prompts stay anchored to today instead of the
    model's training-data year.
    """
    if "current_date" not in callback_context.state:
        callback_context.state["current_date"] = (
            datetime.now(timezone.utc).date().isoformat()
        )
    return None


def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Logs when an agent starts execution and tracks start time.

    Returning None means: proceed with normal agent execution.
    Returning a types.Content would skip the agent entirely.
    """
    agent_name = callback_context.agent_name
    session = callback_context._invocation_context.session
    session_id = _extract_session_id(session)

    print(f"\n{'─'*50}")
    print(f"▶ AGENT START: {agent_name}")
    print(f"{'─'*50}")

    # Track start time for duration logging
    execution_key = f"{agent_name}:{session_id}"
    _agent_execution_tracker[execution_key] = time.time()

    return None  # Proceed normally


async def after_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Logs agent completion and auto-saves session to Memory.

    This callback demonstrates two key patterns:
    1. Observability: logging execution time
    2. Automation: auto-saving session to long-term memory

    Accesses memory_service and session from callback_context._invocation_context
    which is the robust pattern that works across all ADK versions.
    """
    callback_start_time = time.time()
    agent_name = "unknown"
    session_id = "unknown"

    try:
        memory_service = callback_context._invocation_context.memory_service
        session = callback_context._invocation_context.session

        agent_name = getattr(callback_context, 'agent_name', 'unknown')
        user_id = getattr(session, 'user_id', 'unknown') if session else 'unknown'
        session_id = _extract_session_id(session)

        # Log agent execution time
        execution_key = f"{agent_name}:{session_id}"
        if execution_key in _agent_execution_tracker:
            total_execution_time = time.time() - _agent_execution_tracker.pop(execution_key)
            print(f"\n{'─'*50}")
            print(f"■ AGENT DONE: {agent_name} ({total_execution_time:.1f}s)")
            print(f"{'─'*50}")
            if total_execution_time > 20:
                logger.warning("Slow agent: %s took %.2fs", agent_name, total_execution_time)
        else:
            print(f"\n{'─'*50}")
            print(f"■ AGENT DONE: {agent_name}")
            print(f"{'─'*50}")

        # Skip if no memory service configured
        if not memory_service:
            logger.debug("Memory service not available, skipping save")
            return None

        # Skip if no session
        if not session:
            logger.debug("Session not available, skipping save")
            return None

        # Save session to Memory
        try:
            events = getattr(session, 'events', [])
            logger.debug(
                "Saving session to memory (agent=%s, user=%s, events=%d)",
                agent_name, user_id, len(events)
            )

            if hasattr(memory_service, 'add_session_to_memory'):
                await memory_service.add_session_to_memory(session)
                print(f"  💾 Session saved to memory ({len(events)} events)")
            else:
                logger.debug("Memory service has no add_session_to_memory method")

        except Exception as save_error:
            logger.error("Memory save failed: %s", save_error)

    except Exception as e:
        logger.error("after_agent_callback error: %s", e)
    finally:
        duration = time.time() - callback_start_time
        if duration > 5:
            logger.warning("Slow callback: %s took %.2fs", agent_name, duration)

    return None  # Proceed normally


# =============================================================================
# MODEL CALLBACKS
# =============================================================================

BLOCKED_TOPICS = ["violence", "illegal", "harmful", "hate speech"]

def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Content safety guardrail that runs before every LLM call.

    Checks the prompt for blocked topics. If found, returns an LlmResponse
    directly (skipping the actual model call) with a safety message.
    Returning None means: proceed with the normal model call.
    """
    if llm_request.contents:
        last_content = llm_request.contents[-1]
        if last_content.parts:
            text = last_content.parts[0].text or ""
            text_lower = text.lower()
            for topic in BLOCKED_TOPICS:
                if topic in text_lower:
                    print(f"  🛡️ GUARDRAIL: Blocked request containing '{topic}'")
                    return LlmResponse(
                        content=types.Content(
                            parts=[types.Part.from_text(
                                text=f"I cannot generate content about '{topic}'. Please provide a different topic."
                            )],
                            role="model"
                        )
                    )
    return None  # Proceed with the model call


def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Logs model response metrics after each LLM call.

    Returning None means: use the model's response as-is.
    Returning a modified LlmResponse would replace the model's response.
    """
    agent_name = callback_context.agent_name
    if llm_response.content and llm_response.content.parts:
        text = llm_response.content.parts[0].text or ""
        word_count = len(text.split())
        print(f"  📊 Model output for {agent_name}: ~{word_count} words")
    return None  # Use model response as-is
