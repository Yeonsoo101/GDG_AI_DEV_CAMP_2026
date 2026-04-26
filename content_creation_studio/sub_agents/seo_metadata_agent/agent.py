from google.adk.agents import Agent
from content_creation_studio.config import MODEL_NAME, GENERATE_CONTENT_CONFIG
from content_creation_studio.callbacks import inject_current_date

seo_metadata_agent = Agent(
    name="seo_metadata_agent",
    model=MODEL_NAME,
    instruction="""
    Today's date is {{current_date}}. Use this when a year/recency signal belongs in the metadata (e.g. focus keyword for the current year).

    You are an SEO specialist. Generate metadata based on: {{current_content}}

    Create:
    1. Meta Title (50-60 chars)
    2. Meta Description (150-160 chars)
    3. URL Slug
    4. Focus Keyword
    5. 5 Related Keywords

    Format as readable markdown with bold labels, not JSON.
    """,
    tools=[],
    before_agent_callback=inject_current_date,
    generate_content_config=GENERATE_CONTENT_CONFIG,
    output_key="seo_metadata"
)
