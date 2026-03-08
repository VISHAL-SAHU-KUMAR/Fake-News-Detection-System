import os
import httpx
from utils.logger import logger

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

async def search_fact_checks(query: str) -> list[dict]:
    if not GOOGLE_API_KEY:
        logger.warning("Google API key missing. Skipping fact check search.")
        return []
        
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {
        "query": query,
        "key": GOOGLE_API_KEY
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            claims = data.get("claims", [])
            results = []
            for claim in claims:
                claim_review = claim.get("claimReview", [])
                if claim_review:
                    review = claim_review[0]
                    results.append({
                        "title": review.get("title", claim.get("text", "Fact Check")),
                        "url": review.get("url"),
                        "publisher": review.get("publisher", {}).get("name"),
                        "type": "fact_check",
                        "rating": review.get("textualRating")
                    })
            return results
    except Exception as e:
        logger.error(f"Error fetching fact checks: {e}")
        return []
