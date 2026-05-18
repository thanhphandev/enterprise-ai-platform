import logging
import httpx
import openai
from typing import AsyncGenerator

from ..base import BaseLLMProvider
from ..schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionStreamResponse,
    ChatCompletionChoice,
    ChoiceMessage,
    ChatCompletionStreamChoice,
    DeltaMessage,
    ChatCompletionMessageToolCall,
    FunctionCall
)
from ..exceptions import (
    LLMConnectionError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMAuthenticationError,
    LLMProviderError
)
from ..config import llm_settings
from ..decorators.retry import with_retry
from ..decorators.cache import with_cache
from ..decorators.telemetry import with_telemetry

logger = logging.getLogger(__name__)

class OpenAICompatibleProvider(BaseLLMProvider):
    """
    Production-ready OpenAI compatible provider.
    Includes Retries, Telemetry, Caching, and proper Exception mapping.
    """

    def __init__(self, api_key: str, base_url: str = None):
        self.provider_name = "OpenAI-Compatible"
        timeout = httpx.Timeout(llm_settings.TIMEOUT_SECONDS)
        
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=0  # Disable internal retries, we handle it via Tenacity
        )

    def _map_exceptions(self, e: Exception):
        """Map OpenAI exceptions to Domain Exceptions"""
        if isinstance(e, openai.RateLimitError):
            raise LLMRateLimitError(f"Rate limited by provider: {str(e)}")
        elif isinstance(e, openai.APITimeoutError):
            raise LLMTimeoutError(f"Provider timeout: {str(e)}")
        elif isinstance(e, openai.AuthenticationError):
            raise LLMAuthenticationError(f"Auth failed: {str(e)}")
        elif isinstance(e, openai.APIConnectionError):
            raise LLMConnectionError(f"Connection failed: {str(e)}")
        else:
            raise LLMProviderError(f"Unknown provider error: {str(e)}")

    @with_retry()
    @with_cache
    @with_telemetry
    async def generate_chat(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        request_dict = request.model_dump(exclude_none=True)
        try:
            response = await self.client.chat.completions.create(**request_dict)
        except Exception as e:
            self._map_exceptions(e)
            
        choices = []
        for choice in response.choices:
            # Map tool calls if present
            tool_calls = None
            if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                tool_calls = []
                for tc in choice.message.tool_calls:
                    tool_calls.append(ChatCompletionMessageToolCall(
                        id=tc.id,
                        type=tc.type,
                        function=FunctionCall(
                            name=tc.function.name,
                            arguments=tc.function.arguments
                        )
                    ))

            choices.append(ChatCompletionChoice(
                index=choice.index,
                message=ChoiceMessage(
                    role=choice.message.role,
                    content=choice.message.content,
                    tool_calls=tool_calls
                ),
                finish_reason=choice.finish_reason
            ))

        return ChatCompletionResponse(
            id=response.id,
            created=response.created,
            model=response.model,
            choices=choices,
            usage=response.usage.model_dump() if response.usage else None
        )

    @with_retry()
    @with_telemetry
    async def stream_chat(self, request: ChatCompletionRequest) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        request_dict = request.model_dump(exclude_none=True)
        request_dict["stream"] = True

        try:
            stream = await self.client.chat.completions.create(**request_dict)
        except Exception as e:
            self._map_exceptions(e)

        try:
            async for chunk in stream:
                choices = []
                for choice in chunk.choices:
                    tool_calls = None
                    if hasattr(choice.delta, 'tool_calls') and choice.delta.tool_calls:
                        tool_calls = []
                        for tc in choice.delta.tool_calls:
                            # Streamed tool calls can be dict-like or objects, convert safely
                            tc_dict = tc if isinstance(tc, dict) else tc.model_dump()
                            tool_calls.append(tc_dict)

                    choices.append(ChatCompletionStreamChoice(
                        index=choice.index,
                        delta=DeltaMessage(
                            role=choice.delta.role,
                            content=choice.delta.content,
                            tool_calls=tool_calls
                        ),
                        finish_reason=choice.finish_reason
                    ))
                
                yield ChatCompletionStreamResponse(
                    id=chunk.id,
                    created=chunk.created,
                    model=chunk.model,
                    choices=choices
                )
        except Exception as e:
            self._map_exceptions(e)
