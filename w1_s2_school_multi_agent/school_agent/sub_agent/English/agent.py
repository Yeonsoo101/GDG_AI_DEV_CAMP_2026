from google.adk.agents.llm_agent import Agent
from deep_translator import GoogleTranslator

def translator(text: str, target_language = "en") ->str:
    """
    Translates text to the target language. Defaults to English
    """
    try: 
        translated = GoogleTranslator(source="auto", target=target_language).translate(text)
        return translated
    except Exception as e:
        return f"Error: {e}"


english_teacher_agent = Agent(
    model="gemini-2.5-flash",
    name="english_teacher_agent",
    tools = [translator],
    description="Handles English related queries",
    instruction="""
You are an English teacher. You will answer questions about grammar, essay, literatrue and etc.
Also you will check users' essays and give suggestions.
Always respond in a professional manner.
"""
)