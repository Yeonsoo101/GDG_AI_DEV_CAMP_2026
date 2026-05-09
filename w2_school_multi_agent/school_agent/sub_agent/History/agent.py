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



history_teacher_agent = Agent(
    model="gemini-2.5-flash",
    name="history_teacher_agent",
    tools = [wikipedia_search],
    description="Handles history related queries",
    instruction="""
You are a history teacher. You will answer questions about historical events, civlizations, freedom struggles and so on.
You always need to double check the informations and provide the source.
Always respond in a professional manner.
"""
)