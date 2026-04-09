from google.adk.agents import Agent
from config import MODEL_NAME

social_media_creator_agent = Agent(
    name="social_media_creator_agent",
    model=MODEL_NAME,
    instruction="""
    TODO: #REPLACE-social-media-creator-instruction
    Write an instruction that:
    1. Reads {{current_content}} from session state
    2. Creates posts for three platforms:
       - LinkedIn Post: 150-200 words, professional tone
       - Twitter Thread: 3 tweets, max 280 characters each
       - Instagram Caption: 100-150 words, with emojis and hashtags
    3. Formats the output with a clear header for each platform
    """,
    tools=[],
    output_key="social_media_posts",  # Saves to session state["social_media_posts"]
)

root_agent = social_media_creator_agent
