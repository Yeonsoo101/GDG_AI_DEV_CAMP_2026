# pyrefly: ignore [missing-import]
from google.adk.agents.llm_agent import Agent
from .sub_agent.English.agent import english_teacher_agent
from .sub_agent.Maths.agent import math_teacher_agent
from .sub_agent.Science.agent import science_teacher_agent
from .sub_agent.History.agent import history_teacher_agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='Main router agent that sends tasks to the appropriate sub-agents.',
    instruction="""
    You are the main agent that sends tasks to the appropriate sub-agents.
    Route user queries:
    - English queries to english_teacher_agent
    - Math queries to math_teacher_agent
    - Science queries to science_teacher_agent
    - History queries to history_teacher_agent

    If the query is not related to any of the above, respond directly.    
    """,
    sub_agents= [
        english_teacher_agent,
        math_teacher_agent,
        science_teacher_agent,
        history_teacher_agent
    ]
)
