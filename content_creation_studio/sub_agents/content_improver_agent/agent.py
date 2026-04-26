from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from content_creation_studio.tools import exit_loop, QUALITY_THRESHOLD_MET
from content_creation_studio.config import MODEL_NAME, GENERATE_CONTENT_CONFIG
from content_creation_studio.callbacks import inject_current_date

content_improver_agent = Agent(
      name="content_improver_agent",
      model=MODEL_NAME,
      instruction=f"""
      Today's date is {{{{current_date}}}}. Keep any time-sensitive references aligned with this date.

      Current content: {{{{current_content}}}}
      Feedback: {{{{quality_feedback}}}}

      - IF feedback is '{QUALITY_THRESHOLD_MET}':
        1. Call the `exit_loop` tool to terminate the loop
        2. Then respond with: "Quality threshold met! Content approved."

      - ELSE: improve based on issues:
        * Expand if short (add examples, details, explanations)
        * Simplify if complex (shorter sentences, simpler words)
        * Add clear H2 headings if missing
        * Add a strong conclusion if missing

        Output the COMPLETE improved content in markdown.
      """,
      #tools=[FunctionTool(exit_loop)],
      tools=[exit_loop],
      before_agent_callback=inject_current_date,
      generate_content_config=GENERATE_CONTENT_CONFIG,
      output_key="current_content"
)