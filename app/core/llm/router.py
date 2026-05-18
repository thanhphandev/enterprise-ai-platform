import logging
from typing import AsyncGenerator, Dict

from .base import BaseLLMProvider
from .schemas import ChatCompletionRequest, ChatCompletionResponse, ChatCompletionStreamResponse
from .exceptions import LLMProviderError, LLMRateLimitError, LLMConnectionError, LLMTimeoutError

logger = logging.getLogger(__name__)

class LLMRouter(BaseLLMProvider):
    """
    Router that handles High Availability (HA) across multiple LLM Providers.
    If the primary provider fails (timeout, rate limit, server error), it automatically
    falls back to secondary providers.
    """
    def __init__(self, primary_provider: BaseLLMProvider, fallback_providers: Dict[str, BaseLLMProvider]):
        self.primary = primary_provider
        self.fallbacks = fallback_providers

    async def _execute_with_fallback(self, method_name: str, request: ChatCompletionRequest, is_stream: bool = False):
        errors = []
        
        # 1. Try Primary
        try:
            logger.info(f"Router: Routing request to Primary Provider")
            method = getattr(self.primary, method_name)
            return await method(request) if not is_stream else method(request)
        except (LLMRateLimitError, LLMConnectionError, LLMTimeoutError, LLMProviderError) as e:
            logger.error(f"Router: Primary Provider failed: {str(e)}")
            errors.append(str(e))
            
        # 2. Try Fallbacks
        for name, provider in self.fallbacks.items():
            try:
                logger.warning(f"Router: Routing request to Fallback Provider [{name}]")
                method = getattr(provider, method_name)
                return await method(request) if not is_stream else method(request)
            except Exception as e:
                logger.error(f"Router: Fallback Provider [{name}] failed: {str(e)}")
                errors.append(str(e))
                
        # 3. All failed
        raise LLMProviderError(f"Router: All providers failed. Errors: {errors}")

    async def generate_chat(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        return await self._execute_with_fallback("generate_chat", request, is_stream=False)

    async def stream_chat(self, request: ChatCompletionRequest) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        # For streams, we need to await the generator initialization
        generator = await self._execute_with_fallback("stream_chat", request, is_stream=True)
        async for chunk in generator:
            yield chunk
