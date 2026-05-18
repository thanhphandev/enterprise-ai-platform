import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..exceptions import LLMRateLimitError, LLMConnectionError, LLMTimeoutError
from ..config import llm_settings

logger = logging.getLogger(__name__)

def log_retry_attempt(retry_state):
    """Log when a retry is happening."""
    logger.warning(
        f"Retrying LLM call. Attempt {retry_state.attempt_number} "
        f"after error: {retry_state.outcome.exception()}"
    )

def with_retry():
    """
    Decorator for robust LLM retries.
    Applies exponential backoff on rate limits and timeouts.
    """
    return retry(
        retry=(
            retry_if_exception_type(LLMRateLimitError) |
            retry_if_exception_type(LLMConnectionError) |
            retry_if_exception_type(LLMTimeoutError)
        ),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(llm_settings.MAX_RETRIES),
        before_sleep=log_retry_attempt,
        reraise=True
    )
