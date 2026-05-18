import time
import logging
from functools import wraps
from ..config import llm_settings

logger = logging.getLogger(__name__)

import inspect

def with_telemetry(func):
    """
    Decorator for tracking latency and usage metrics of LLM calls.
    Supports both standard async functions and async generators (streaming).
    """
    if inspect.isasyncgenfunction(func):
        @wraps(func)
        async def async_generator_wrapper(*args, **kwargs):
            if not llm_settings.ENABLE_TELEMETRY:
                async for item in func(*args, **kwargs):
                    yield item
                return

            start_time = time.time()
            logger.info("LLM Stream Call Started")
            try:
                async for item in func(*args, **kwargs):
                    yield item
                latency_ms = int((time.time() - start_time) * 1000)
                logger.info(f"LLM Stream Call Completed | Latency: {latency_ms}ms")
            except Exception as e:
                latency_ms = int((time.time() - start_time) * 1000)
                logger.error(f"LLM Stream Call Failed | Latency: {latency_ms}ms | Error: {str(e)}")
                raise
        return async_generator_wrapper
    else:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not llm_settings.ENABLE_TELEMETRY:
                return await func(*args, **kwargs)

            start_time = time.time()
            
            try:
                response = await func(*args, **kwargs)
                latency_ms = int((time.time() - start_time) * 1000)
                
                # Simple heuristic for telemetry: if it's a streaming response, we can't count tokens upfront.
                # For standard responses, log the usage.
                if hasattr(response, 'usage') and response.usage:
                    usage = response.usage
                    logger.info(
                        f"LLM Call Success | Latency: {latency_ms}ms | "
                        f"Tokens: {usage.get('prompt_tokens', 0)} prompt, "
                        f"{usage.get('completion_tokens', 0)} completion"
                    )
                else:
                    logger.info(f"LLM Call Success | Latency: {latency_ms}ms")
                    
                return response
                
            except Exception as e:
                latency_ms = int((time.time() - start_time) * 1000)
                logger.error(f"LLM Call Failed | Latency: {latency_ms}ms | Error: {str(e)}")
                raise

        return wrapper
