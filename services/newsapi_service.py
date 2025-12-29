"""
TheNewsAPI.com service for fetching latest AI/LLM news.
"""

import httpx
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from config import config

logger = logging.getLogger(__name__)


async def fetch_latest_news(
    keywords: List[str] = None,
    limit: int = None
) -> List[Dict[str, Any]]:
    """
    Fetch latest news articles from TheNewsAPI.com.
    
    Args:
        keywords: List of keywords to search for (default: LLM-related terms)
        limit: Maximum number of articles to fetch (default: from config)
    
    Returns:
        List of article dictionaries with title, url, source, published_at, description
    
    Raises:
        httpx.HTTPError: If API request fails
    """
    if keywords is None:
        keywords = ["AI", "LLM", "GPT", "Claude", "Gemini", "AI agents", "large language model"]
    
    if limit is None:
        limit = config.NEWSAPI_LIMIT
    
    # Calculate date range (last 7 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Build API request
    url = "https://api.thenewsapi.com/v1/news/all"
    
    params = {
        "api_token": config.NEWSAPI_KEY,
        "search": " OR ".join(keywords),
        "language": "en",
        "published_after": start_date.strftime("%Y-%m-%d"),
        "published_before": end_date.strftime("%Y-%m-%d"),
        "limit": limit,
        "sort": "published_at",
    }
    
    logger.info(f"Fetching news from TheNewsAPI with keywords: {keywords}")
    
    current_page = 1
    all_articles = []
    
    try:
        async with httpx.AsyncClient(timeout=config.API_TIMEOUT) as client:
            while len(all_articles) < limit:
                # Update params for current page
                params["page"] = current_page
                
                logger.info(f"Fetching page {current_page}...")
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                page_articles = data.get("data", [])
                
                if not page_articles:
                    logger.info("No more articles found.")
                    break
                
                # Add to total collection
                all_articles.extend(page_articles)
                
                # Check if we've reached the end of results (less than 3 items usually means last page on free tier)
                # But safer to just check if we got what we asked for, though free tier is weird.
                # If we got 0 items, we handle it above. 
                # If we keep getting items, we continue.
                # Safety break to avoid infinite loops if something goes wrong
                if current_page >= 10: 
                    logger.warning("Reached maximum pagination limit (10 pages). Stopping.")
                    break
                    
                current_page += 1
            
            # Trim to exact limit
            all_articles = all_articles[:limit]
            
            logger.info(f"Successfully fetched {len(all_articles)} articles (requested limit: {limit})")
            
            # Transform to our format
            transformed_articles = []
            for article in all_articles:
                transformed_articles.append({
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", ""),
                    "published_at": article.get("published_at", ""),
                    "description": article.get("description", ""),
                })
            
            return transformed_articles
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching news: {e.response.status_code} - {e.response.text}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Request error fetching news: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching news: {str(e)}")
        raise
