"""
Agent 1: News Fetcher & Analyzer
Analyzes raw news articles and categorizes them by technical significance.
"""

import json
import logging
from typing import List, Dict, Any
from datetime import datetime

from models import Agent1Output, Article
from services.gemini_service import gemini_client
from prompts import PROMPT_AGENT_1

logger = logging.getLogger(__name__)


async def analyze_news(articles: List[Dict[str, Any]]) -> Agent1Output:
    """
    Analyze raw news articles using Gemini.
    
    Args:
        articles: List of raw article dictionaries from TheNewsAPI
    
    Returns:
        Agent1Output with analyzed and categorized articles
    
    Raises:
        Exception: If Gemini call fails or response is invalid
    """
    logger.info(f"Agent 1: Analyzing {len(articles)} news articles")
    
    # Prepare articles data for the prompt
    articles_text = "\n\n".join([
        f"Article {i+1}:\n"
        f"Title: {article['title']}\n"
        f"Source: {article['source']}\n"
        f"Published: {article['published_at']}\n"
        f"URL: {article['url']}\n"
        f"Description: {article['description']}"
        for i, article in enumerate(articles)
    ])
    
    # Build the full prompt
    full_prompt = f"{PROMPT_AGENT_1}\n\nHere are the articles to analyze:\n\n{articles_text}"
    
    # Call Gemini
    try:
        response_text = await gemini_client.call_gemini(
            prompt=full_prompt,
            response_format="json",
            temperature=0.5  # Lower temperature for more consistent analysis
        )
        
        # Parse JSON response
        response_data = json.loads(response_text)
        
        # Add current timestamp if not present
        if "processed_at" not in response_data:
            response_data["processed_at"] = datetime.now().isoformat()
        
        # Validate and create Agent1Output
        agent_output = Agent1Output(**response_data)
        
        logger.info(f"Agent 1: Successfully analyzed {len(agent_output.articles)} articles")
        return agent_output
        
    except json.JSONDecodeError as e:
        logger.error(f"Agent 1: Failed to parse JSON response: {e}")
        logger.error(f"Response text: {response_text[:500]}")
        raise Exception(f"Agent 1 failed: Invalid JSON response from Gemini")
    except Exception as e:
        logger.error(f"Agent 1: Error during analysis: {str(e)}")
        raise
