from google.adk.agents import Agent
from common.callbacks import inject_current_date
from google.adk.tools import FunctionTool
from common.retry import GENERATE_CONTENT_CONFIG
from agents.artifacts import (
    save_content_artifact,
    list_content_artifacts,
    load_content_artifact,
)

MODEL_NAME = "gemini-2.5-flash"

blog_post_writer_agent = Agent(
    name="blog_post_writer_agent",
    model=MODEL_NAME,
    instruction="""
    Today's date is {current_date}. Anchor any references to "now", "current year", or recent trends to this date.

    You are a professional blog writer. Create the final polished blog post from: {current_content}

    Enhance it to be publication-ready:
    - Ensure 800-1200 words
    - Add engaging subheadings
    - Include actionable tips
    - Strong call-to-action

    Output only the final blog post in markdown.
    """,
    tools=[        
        FunctionTool(save_content_artifact),
        FunctionTool(list_content_artifacts),],
    before_agent_callback=inject_current_date,
    generate_content_config=GENERATE_CONTENT_CONFIG,
    output_key="final_blog_post",  # Saves to session state["final_blog_post"]
)

root_agent = blog_post_writer_agent
