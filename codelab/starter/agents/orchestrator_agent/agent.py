import os
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

from google.adk.agents import SequentialAgent, LoopAgent, ParallelAgent, Agent
from google.adk.tools import preload_memory_tool
MODEL_NAME = "gemini-2.5-flash"
MAX_IMPROVEMENT_ITERATIONS = int(os.getenv("MAX_IMPROVEMENT_ITERATIONS", "2"))
from common.retry import GENERATE_CONTENT_CONFIG

from .callbacks import (
    before_agent_callback,
    after_agent_callback,
    before_model_callback,
    after_model_callback,
)
from agents.topic_research_agent.agent import topic_research_agent
from agents.content_drafter_agent.agent import content_drafter_agent
from agents.quality_checker_agent.agent import quality_checker_agent
from agents.content_improver_agent.agent import content_improver_agent
from agents.blog_post_writer_agent.agent import blog_post_writer_agent
from agents.social_media_creator_agent.agent import social_media_creator_agent
from agents.email_newsletter_writer_agent.agent import email_newsletter_writer_agent
from agents.seo_metadata_agent.agent import seo_metadata_agent
from agents.content_analyzer_agent.agent import content_analyzer_agent


# --- Step 8: Sequential — Research and Draft ---

# Create a SequentialAgent named "research_and_draft_workflow"
# with sub_agents=[topic_research_agent, content_drafter_agent]
research_and_draft_workflow = SequentialAgent(
    name="research_and_draft_workflow",
    sub_agents=[topic_research_agent, content_drafter_agent],
)  # Replace this line


# --- Step 10: Loop — Quality Improvement ---
# TODO: #REPLACE-quality-improvement-loop
# Create a LoopAgent named "quality_improvement_loop"
# with sub_agents=[quality_checker_agent, content_improver_agent]
# and max_iterations=MAX_IMPROVEMENT_ITERATIONS
quality_improvement_loop = LoopAgent(
    name="quality_improvement_loop",
    sub_agents=[quality_checker_agent, content_improver_agent],
    max_iterations=MAX_IMPROVEMENT_ITERATIONS,
)


# --- Step 11: Parallel — Multi-Channel Content Creation ---
# TODO: #REPLACE-parallel-content-creation
# Create a ParallelAgent named "parallel_content_creation"
# with sub_agents=[blog_post_writer_agent, social_media_creator_agent,
#                  email_newsletter_writer_agent, seo_metadata_agent]
# agents/orchestrator_agent/agent.py

parallel_content_creation = ParallelAgent(
    name="parallel_content_creation",
    sub_agents=[
        blog_post_writer_agent,
        social_media_creator_agent,
        email_newsletter_writer_agent,
        seo_metadata_agent,
    ],
)


# --- Step 12: Full Content Workflow ---
# TODO: #REPLACE-full-content-workflow
# Create a SequentialAgent named "full_content_workflow"
# with sub_agents=[research_and_draft_workflow, quality_improvement_loop,
#                  parallel_content_creation]
# agents/orchestrator_agent/agent.py

full_content_workflow = SequentialAgent(
    name="full_content_workflow",
    sub_agents=[
        research_and_draft_workflow,   # Phase 1: research → draft
        quality_improvement_loop,      # Phase 2: check → improve (loop)
        parallel_content_creation,     # Phase 3: 4 formats in parallel
    ],
)




# --- Step 13: Root Agent (Orchestrator) ---
# agents/orchestrator_agent/agent.py

orchestrator_agent = Agent(
    name="orchestrator_agent",
    model=MODEL_NAME,
    instruction="""
    You are the Content Creation Studio orchestrator. Delegate tasks to specialists.

    Past conversations from long-term memory are automatically loaded before each turn.
    Use this context to provide continuity across sessions.

    - For FULL content creation (topic research -> draft -> improve -> multi-channel content),
      transfer to `full_content_workflow`. Pass the complete user request with topic,
      audience, tone, and keywords.

    - For ANALYZING existing text (readability, word count, hashtags),
      transfer to `content_analyzer_agent`.

    Always delegate to the appropriate agent.
    """,
    sub_agents=[full_content_workflow, content_analyzer_agent],
    # tools=[preload_memory_tool.PreloadMemoryTool()],
    generate_content_config=GENERATE_CONTENT_CONFIG,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)

root_agent = orchestrator_agent

