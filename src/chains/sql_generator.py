"""
LangChain LCEL SQL Generation Chain.
"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import settings
from src.chains.prompts import SQL_GENERATION_SYSTEM_PROMPT


def get_sql_generation_chain(schema_summary: str, question: str) -> str:
    """
    Constructs the declarative LCEL chain:
    Input Dict -> Prompt Template -> Gemini LLM -> String Output Parser
    """

    llm = ChatGroq(
        model=settings.MODEL_NAME,
        groq_api_key=settings.GROQ_API_KEY,
        temperature=0.0
    )

    system_text = SQL_GENERATION_SYSTEM_PROMPT.replace("{schema}", schema_summary)

    messages = [
        SystemMessage(content=system_text),
        HumanMessage(content=f"Question: {question}\nSQL:")
    ]
    
    response = llm.invoke(messages)
    return response.content
