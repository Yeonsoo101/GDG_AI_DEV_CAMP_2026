from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool
from content_creation_studio.tools import exit_loop, QUALITY_THRESHOLD_MET
from content_creation_studio.config import MODEL_NAME, RETRY_CONFIG

content_improver_agent = Agent(
      name="content_improver_agent",
      model=Gemini(model=MODEL_NAME, retry_options=RETRY_CONFIG),
      instruction=f"""
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
      output_key="current_content"
)