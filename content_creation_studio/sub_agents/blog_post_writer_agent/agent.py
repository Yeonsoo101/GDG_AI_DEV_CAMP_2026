from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from content_creation_studio.config import MODEL_NAME, RETRY_CONFIG

blog_post_writer_agent = Agent(
    name="blog_post_writer_agent",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY_CONFIG),
    instruction="""
    You are a professional blog writer. Create the final polished blog post from: {{current_content}}

    Enhance it to be publication-ready:
    - Ensure 800-1200 words
    - Add engaging subheadings
    - Include actionable tips
    - Strong call-to-action

    Output only the final blog post in markdown.
    """,
    tools=[],
    output_key="final_blog_post"
)
