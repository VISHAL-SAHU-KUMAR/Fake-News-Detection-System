import os
import httpx
from utils.logger import logger

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

async def search_news(query: str) -> list[dict]:
    if not NEWS_API_KEY:
        logger.warning("NewsAPI key missing. Skipping news search.")
        return []
        
    url = f"https://newsapi.org/v2/everything"
    # Basic relevance query to find related articles
    params = {
        "q": query,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for item in data.get("articles", []):
                articles.append({
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "publisher": item.get("source", {}).get("name"),
                    "type": "news"
                })
            return articles
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return []
