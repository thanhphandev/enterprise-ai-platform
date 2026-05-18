from typing import Dict
from .base import BaseLLMProvider
from .providers.openai_compatible import OpenAICompatibleProvider
from .router import LLMRouter
from .config import llm_settings

class LLMFactory:
    """
    Enterprise LLM Factory.
    Creates instances of providers and sets up the High Availability Router.
    """
    
    @staticmethod
    def _create_provider(provider_type: str, api_key: str, base_url: str = None) -> BaseLLMProvider:
        provider_type = provider_type.lower()
        if provider_type in ["openai", "vllm", "ollama", "groq", "deepseek", "lmstudio"]:
            return OpenAICompatibleProvider(api_key=api_key, base_url=base_url)
        raise ValueError(f"Unsupported provider: {provider_type}")

    @classmethod
    def get_ha_router(cls, 
                      primary_type: str, primary_key: str, primary_url: str = None,
                      fallback_configs: Dict[str, dict] = None) -> LLMRouter:
        """
        Get a Highly Available LLM Router configured with Primary and Fallbacks.
        """
        primary = cls._create_provider(primary_type, primary_key, primary_url)
        
        fallbacks = {}
        if fallback_configs:
            for name, conf in fallback_configs.items():
                fallbacks[name] = cls._create_provider(
                    conf.get('type', 'openai'), 
                    conf.get('api_key'), 
                    conf.get('base_url')
                )
                
        return LLMRouter(primary_provider=primary, fallback_providers=fallbacks)
