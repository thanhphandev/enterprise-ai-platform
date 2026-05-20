import os
from typing import Optional, List
from pydantic_settings import BaseSettings

class LLMSettings(BaseSettings):
    # Primary LLM Settings (OpenAI Compatible)
    PRIMARY_LLM_API_KEY: str = "dummy"
    PRIMARY_LLM_BASE_URL: str = "https://api.openai.com/v1"
    DEFAULT_MODEL: str = "gpt-4o"
    
    # Fallback LLM Settings
    FALLBACK_LLM_API_KEY: str = "dummy"
    FALLBACK_LLM_BASE_URL: str = "https://api.groq.com/openai/v1"
    FALLBACK_MODEL: str = "llama3-8b-8192"
    
    # Resilience & Telemetry
    MAX_RETRIES: int = 3
    TIMEOUT_SECONDS: int = 15
    ENABLE_CACHING: bool = True
    ENABLE_TELEMETRY: bool = True
    
    # Redis Cache (Optional)
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    # Tavily Web Search
    TAVILY_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'

# Global instantiation
llm_settings = LLMSettings()
