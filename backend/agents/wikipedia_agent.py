import httpx
from utils.logger import logger

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_HEADERS = {
    "User-Agent": "TruthLens/1.0 (https://truthlens.local; support@truthlens.local)",
    "Accept": "application/json",
}


async def search_wikipedia(query: str) -> list[dict]:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "utf8": "",
        "format": "json",
        "srlimit": 2
    }
    
    try:
        async with httpx.AsyncClient(
            headers=WIKIPEDIA_HEADERS,
            timeout=10.0,
            follow_redirects=True
        ) as client:
            response = await client.get(WIKIPEDIA_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            search_results = data.get("query", {}).get("search", [])
            articles = []
            for item in search_results:
                title = item.get("title")
                page_id = item.get("pageid")
                
                # Removing HTML tags in snippet
                snippet = item.get("snippet", "")
                import re
                snippet = re.sub(r'<[^>]+>', '', snippet)
                
                articles.append({
                    "title": title,
                    "url": f"https://en.wikipedia.org/?curid={page_id}",
                    "publisher": "Wikipedia",
                    "type": "wikipedia",
                    "snippet": snippet
                })
            return articles
    except Exception as e:
        logger.error(f"Error fetching Wikipedia: {e}")
        return []
