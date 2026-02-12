from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from content_creation_studio.config import MODEL_NAME, RETRY_CONFIG

topic_research_agent = Agent(
    name="topic_research_agent",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY_CONFIG),
    instruction="""
    You are a topic research expert. Based on the user's request,
    use search to find trending angles and select the SINGLE BEST specific blog post title.
    Output format: Just the title, nothing else.

    Example: "10 AI Tools That Save Small Businesses 20 Hours Per Week"
    """,
    tools=[google_search],
    output_key="blog_topic"
)
