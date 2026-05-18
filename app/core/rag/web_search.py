from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)

class WebSearchService:
    """
    Service for executing web searches using DuckDuckGo Search API (free, no key required).
    """
    def __init__(self):
        pass

    def search(self, query: str, max_results: int = 5) -> str:
        logger.info(f"Executing web search for query: '{query}'")
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                if not results:
                    return "Không tìm thấy kết quả tìm kiếm nào trên Internet."
                
                formatted_results = []
                for i, r in enumerate(results, 1):
                    title = r.get("title", "No Title")
                    body = r.get("body", r.get("snippet", ""))
                    href = r.get("href", r.get("link", ""))
                    formatted_results.append(f"[{i}] {title}\nLink: {href}\nNội dung: {body}\n")
                
                return "\n---\n".join(formatted_results)
        except Exception as e:
            logger.error(f"Error during DuckDuckGo search: {e}")
            return f"Lỗi khi thực hiện tìm kiếm trên Internet: {str(e)}"
