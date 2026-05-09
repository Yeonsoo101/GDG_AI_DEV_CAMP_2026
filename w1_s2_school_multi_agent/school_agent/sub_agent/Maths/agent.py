from google.adk.agents.llm_agent import Agent
from sympy import sympify, SympifyError

def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    """
    try:
        result = sympify(expression)
        return str(result)
    except SympifyError as e:
        return f"Error: {e}"
        
math_teacher_agent = Agent(
    model="gemini-2.5-flash",
    name="math_teacher_agent",
    tools = [calculator],
    description="Handles Maths related queries",
    instruction="""
You are a Math teacher. You will answer questions about Algebra, Geometry, Calculs and etc.
Always double check the calculations and steps. There should be no mistake.
Always respond in a clear and step-by-step manner.
"""
)