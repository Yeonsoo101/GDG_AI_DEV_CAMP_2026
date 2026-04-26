from google.adk.agents import Agent
from content_creation_studio.config import MODEL_NAME, GENERATE_CONTENT_CONFIG
from content_creation_studio.callbacks import inject_current_date

content_drafter_agent = Agent(
    name="content_drafter_agent",
    model=MODEL_NAME,
    instruction="""
    Today's date is {{current_date}}. Anchor any references to "now", "current", or "this year" to this date.

    You are a content writer. Write a blog post: {{blog_topic}}

    Create a draft (400-600 words) with:
    - Engaging introduction
    - At least 2 H2 headings
    - A conclusion section

    Output only the blog post in markdown format.
    """,
    tools=[],
    before_agent_callback=inject_current_date,
    generate_content_config=GENERATE_CONTENT_CONFIG,
    output_key="current_content"
)
