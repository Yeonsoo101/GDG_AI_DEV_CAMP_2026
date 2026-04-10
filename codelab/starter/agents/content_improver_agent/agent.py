from google.adk.agents import Agent
from .tools import exit_loop, QUALITY_THRESHOLD_MET
MODEL_NAME = "gemini-2.5-flash"

content_improver_agent = Agent(
    name="content_improver_agent",
    model=MODEL_NAME,
    instruction=f"""
    TODO: #REPLACE-content-improver-instruction
    Write an instruction (this is an f-string, so use double braces for session state keys) that:
    1. Reads {{{{current_content}}}} and {{{{quality_feedback}}}} from session state
    2. IF quality_feedback equals '{QUALITY_THRESHOLD_MET}':
         - Calls the `exit_loop` tool to signal the LoopAgent to stop iterating
         - Then responds: "Quality threshold met! Content approved."
    3. ELSE (quality needs improvement):
         - Improves the content based on the specific issues in quality_feedback:
           * Expand if too short (add examples, details, explanations)
           * Simplify if too complex (use shorter sentences and simpler words)
           * Add clear H2 headings if missing
           * Add a strong conclusion if missing
         - Outputs the COMPLETE improved content in markdown
    """,
    tools=[exit_loop],  # exit_loop sets tool_context.actions.escalate = True to break the loop
    output_key="current_content",  # Overwrites the previous draft in session state
)

root_agent = content_improver_agent
