import logging
import httpx
from ..llm.config import llm_settings

logger = logging.getLogger(__name__)

class WebSearchService:
    """
    Service for executing web searches using Tavily Search API.
    """
    def __init__(self):
        self.api_key = llm_settings.TAVILY_API_KEY
        self.url = "https://api.tavily.com/search"

    def search(self, query: str, max_results: int = 5) -> str:
        logger.info(f"Executing Tavily web search for query: '{query}'")
        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": max_results
            }
            response = httpx.post(self.url, json=payload, timeout=15.0)
            if response.status_code != 200:
                logger.error(f"Tavily search API error: {response.status_code} - {response.text}")
                return f"Lỗi khi thực hiện tìm kiếm trên Internet: HTTP {response.status_code}"
                
            data = response.json()
            results = data.get("results", [])
            if not results:
                return "Không tìm thấy kết quả tìm kiếm nào trên Internet."
                
            formatted_results = []
            for i, r in enumerate(results, 1):
                title = r.get("title", "No Title")
                href = r.get("url", "")
                body = r.get("content", "")
                formatted_results.append(f"[{i}] {title}\nLink: {href}\nNội dung: {body}\n")
                
            return "\n---\n".join(formatted_results)
        except Exception as e:
            logger.error(f"Error during Tavily search: {e}")
            return f"Lỗi khi thực hiện tìm kiếm trên Internet: {str(e)}"
