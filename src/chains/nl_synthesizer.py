"""
LangChain LCEL Natural Language Synthesis Chain.
"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import settings
from src.chains.prompts import NL_SYNTHESIS_SYSTEM_PROMPT

def get_nl_synthesis_chain(question: str, query: str, results: list) -> str:
    """
    Constructs the synthesis chain:
    Context Dict -> Prompt Template -> Gemini LLM -> Clean Business Text
    """

    llm = ChatGroq(
        model=settings.MODEL_NAME,
        groq_api_key=settings.GROQ_API_KEY,
        temperature=0.2
    )

    system_text = (
        NL_SYNTHESIS_SYSTEM_PROMPT
        .replace("{question}", question)
        .replace("{query}", query)
        .replace("{results}", str(results))
    )
    
    messages = [
        SystemMessage(content=system_text),
        HumanMessage(content="Generate the business answer.")
    ]
    
    response = llm.invoke(messages)
    return response.content