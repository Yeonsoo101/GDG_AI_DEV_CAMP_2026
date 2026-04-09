from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from tools import calculate_content_quality_score, QUALITY_THRESHOLD_MET
from config import MODEL_NAME

quality_checker_agent = Agent(
    name="quality_checker_agent",
    model=MODEL_NAME,
    instruction=f"""
    TODO: #REPLACE-quality-checker-instruction
    Write an instruction (this is an f-string, so use double braces for session state keys) that:
    1. Reads {{{{current_content}}}} from session state
    2. Estimates approximate word count, readability score (60+ is good),
       whether there are clear H2 headings, and whether there is a conclusion section
    3. Calls the `calculate_content_quality_score` tool with those four values
    4. If overall_score >= 70: responds with exactly '{QUALITY_THRESHOLD_MET}'
    5. Otherwise: responds with 'Quality score: [score]. Issues: [specific problems found]'
    """,
    tools=[FunctionTool(calculate_content_quality_score)],
    output_key="quality_feedback",  # Saves feedback to session state["quality_feedback"]
)

root_agent = quality_checker_agent
