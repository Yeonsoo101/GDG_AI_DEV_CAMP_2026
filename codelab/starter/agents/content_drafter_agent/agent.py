from google.adk.agents import Agent
MODEL_NAME = "gemini-2.5-flash"

content_drafter_agent = Agent(
    name="content_drafter_agent",
    model=MODEL_NAME,
    instruction="""
    TODO: #REPLACE-content-drafter-instruction
    Write an instruction that:
    1. Tells the agent it is a content writer
    2. References {{blog_topic}} to read the researched title from session state
       (ADK substitutes {{blog_topic}} with the value from session state automatically)
    3. Asks for a draft of 400-600 words with:
       - An engaging introduction
       - At least 2 H2 headings (## Heading)
       - A conclusion section
    4. Instructs the agent to output ONLY the blog post in markdown format
    """,
    tools=[],
    output_key="current_content",  # Saves to session state["current_content"]
)

root_agent = content_drafter_agent
