import json
import logging
from functools import wraps
import hashlib
from ..config import llm_settings

logger = logging.getLogger(__name__)

# Basic in-memory cache for demonstration. 
# In production, replace this with a Redis client (e.g., aioredis)
_MEMORY_CACHE = {}

def compute_cache_key(args, kwargs) -> str:
    """Compute a deterministic hash for the request to use as cache key."""
    # The first arg is usually `self` (provider), the second is the request
    request_obj = args[1] if len(args) > 1 else kwargs.get("request")
    if not request_obj:
        return "default_key"
        
    # Serialize request to JSON and hash it
    req_dump = request_obj.model_dump(exclude={"temperature", "top_p"}) # Ignore variance params for key
    req_str = json.dumps(req_dump, sort_keys=True)
    return hashlib.md5(req_str.encode('utf-8')).hexdigest()

def with_cache(func):
    """
    Decorator for caching LLM responses.
    Reduces latency to 0ms and saves tokens for repeated exact prompts.
    Does not cache streaming responses.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not llm_settings.ENABLE_CACHING:
            return await func(*args, **kwargs)
            
        cache_key = compute_cache_key(args, kwargs)
        
        # Cache Hit
        if cache_key in _MEMORY_CACHE:
            logger.info(f"LLM Cache Hit for key: {cache_key[:8]}...")
            return _MEMORY_CACHE[cache_key]
            
        # Cache Miss
        response = await func(*args, **kwargs)
        
        # Only cache non-streaming responses
        # If it's a generator (streaming), we skip caching for simplicity
        if hasattr(response, 'choices') and not getattr(response, 'stream', False):
            _MEMORY_CACHE[cache_key] = response
            logger.info(f"LLM Cache Miss. Saved to cache key: {cache_key[:8]}...")
            
        return response

    return wrapper
