"""
llm_service.py
--------------
Wrapper for the OpenAI Chat Model.
Configured to use 'structured_output' to enforce the Pydantic schema.
"""

from langchain_openai import ChatOpenAI
from src.core.config import get_settings
from src.core.schema import DiagnosticResult

settings = get_settings()

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=0, # Deterministic for industrial safety
            api_key=settings.OPENAI_API_KEY
        )
        # Bind the Pydantic model to the LLM immediately
        # This forces the LLM to ONLY speak in 'DiagnosticResult' JSON
        self.structured_llm = self.llm.with_structured_output(DiagnosticResult)

    def get_analyzer(self):
        return self.structured_llm

llm_service = LLMService()