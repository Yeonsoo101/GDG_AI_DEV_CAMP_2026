from google.adk.agents.llm_agent import Agent
from wikipediaapi import Wikipedia

def wikipedia_search(query:str ) -> str:
    """
    Search Wikipedia for a query and return the summary.
    """
    wiki = Wikipedia(user_agent='school-agent/1.0', language='en')
    page = wiki.page(query)
    if page.exists():
        return page.summary[:1500]
    else:
        return f"Page not found for {query} on Wikipedia"
        
science_teacher_agent = Agent(
    model="gemini-2.5-flash",
    name="science_teacher_agent",
    tools = [wikipedia_search],
    description="Handles science related queries",
    instruction="""
You are a science teacher. You will answer questions about physics, chemistry, biology and etc.
Always answer questions based on scientific knowledge and provide sources. .
Always respond in a professional manner.
"""
)