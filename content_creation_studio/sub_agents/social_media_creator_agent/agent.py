from google.adk.agents import Agent
from content_creation_studio.config import MODEL_NAME, GENERATE_CONTENT_CONFIG
from content_creation_studio.callbacks import inject_current_date

social_media_creator_agent = Agent(
    name="social_media_creator_agent",
    model=MODEL_NAME,
    instruction="""
    Today's date is {{current_date}}. Anchor any time-sensitive references (trends, hashtags, "this year") to this date.

    You are a social media specialist. Create posts from: {{current_content}}

    Create:
    1. LinkedIn Post (150-200 words, professional)
    2. Twitter Thread (3 tweets, 280 chars each)
    3. Instagram Caption (100-150 words, with emojis and hashtags)

    Format with clear headers for each platform.
    """,
    tools=[],
    before_agent_callback=inject_current_date,
    generate_content_config=GENERATE_CONTENT_CONFIG,
    output_key="social_media_posts"
)
