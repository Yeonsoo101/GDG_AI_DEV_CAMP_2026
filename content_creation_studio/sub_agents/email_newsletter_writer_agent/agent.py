from google.adk.agents import Agent
from content_creation_studio.config import MODEL_NAME, GENERATE_CONTENT_CONFIG
from content_creation_studio.callbacks import inject_current_date

email_newsletter_writer_agent = Agent(
    name="email_newsletter_writer_agent",
    model=MODEL_NAME,
    instruction="""
    Today's date is {{current_date}}. Anchor any time-sensitive references (seasonal hooks, "this month", "this year") to this date.

    You are an email marketing specialist. Create a newsletter from: {{current_content}}

    Include:
    - Subject Line (compelling, 50-60 chars)
    - Preview Text (40-50 chars)
    - Body (300-400 words with CTA)

    Format with clear sections.
    """,
    tools=[],
    before_agent_callback=inject_current_date,
    generate_content_config=GENERATE_CONTENT_CONFIG,
    output_key="email_newsletter"
)
