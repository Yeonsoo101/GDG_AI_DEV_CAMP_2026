from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from tools import count_words, calculate_readability_score, generate_hashtags
from config import MODEL_NAME

content_analyzer_agent = Agent(
    name="content_analyzer_agent",
    model=MODEL_NAME,
    instruction="""
    TODO: #REPLACE-content-analyzer-instruction
    Write an instruction that:
    1. Tells the agent it is a content analysis expert
    2. Uses its three tools to analyze the provided text:
       - count_words to count the total words
       - calculate_readability_score to measure readability
       - generate_hashtags with count=5 to suggest relevant hashtags
    3. Provides a clear, structured analysis report with all three results
    """,
    tools=[
        # TODO: #REPLACE-analyzer-tools
        # Add FunctionTool wrappers for the three analysis functions:
        # FunctionTool(count_words),
        # FunctionTool(calculate_readability_score),
        # FunctionTool(generate_hashtags),
    ],
)

root_agent = content_analyzer_agent
