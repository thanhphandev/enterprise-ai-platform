class LLMProviderError(Exception):
    """Base exception for all LLM-related errors."""
    pass

class LLMConnectionError(LLMProviderError):
    """Raised when the connection to the provider fails."""
    pass

class LLMTimeoutError(LLMProviderError):
    """Raised when the request times out."""
    pass

class LLMRateLimitError(LLMProviderError):
    """Raised when the provider rate limits the request (HTTP 429)."""
    pass

class LLMAuthenticationError(LLMProviderError):
    """Raised when API key or authentication fails (HTTP 401/403)."""
    pass

class LLMConfigurationError(LLMProviderError):
    """Raised when there is a configuration error."""
    pass
