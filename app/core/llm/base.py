from abc import ABC, abstractmethod
from typing import AsyncGenerator

from .schemas import ChatCompletionRequest, ChatCompletionResponse, ChatCompletionStreamResponse

class BaseLLMProvider(ABC):
    """
    Abstract Base Class for all LLM Providers.
    Any provider (OpenAI, Gemini, Local LLM, etc.) must implement these methods.
    """

    @abstractmethod
    async def generate_chat(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """
        Generate a complete chat response (non-streaming).
        """
        pass

    @abstractmethod
    async def stream_chat(self, request: ChatCompletionRequest) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        """
        Generate a streaming chat response.
        """
        pass
