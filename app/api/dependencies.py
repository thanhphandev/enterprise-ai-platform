import os
from fastapi import Request
from app.core.llm import LLMFactory
from app.core.llm.config import llm_settings
from app.core.rag import RAGPipeline

# Global instances (in a real app, this might be managed via a DI framework or App State)
_rag_pipeline = None

def get_rag_pipeline() -> RAGPipeline:
    global _rag_pipeline
    if _rag_pipeline is None:
        # Initialize HA Router using abstract configuration
        router = LLMFactory.get_ha_router(
            primary_type="openai", # This is just a key identifier
            primary_key=llm_settings.PRIMARY_LLM_API_KEY,
            primary_url=llm_settings.PRIMARY_LLM_BASE_URL,
            fallback_configs={
                "fallback": {
                    "type": "openai", # Treat fallback as OpenAI compatible as well
                    "api_key": llm_settings.FALLBACK_LLM_API_KEY,
                    "base_url": llm_settings.FALLBACK_LLM_BASE_URL
                }
            }
        )
        _rag_pipeline = RAGPipeline(llm_provider=router)
    return _rag_pipeline
