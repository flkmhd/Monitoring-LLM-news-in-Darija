"""
Agent 2: Idea Extractor
Extracts innovative ideas from analyzed news articles.
"""

import json
import logging
from datetime import datetime

from models import Agent1Output, Agent2Output, Idea
from services.gemini_service import gemini_client
from prompts import PROMPT_AGENT_2

logger = logging.getLogger(__name__)


async def extract_ideas(analyzed_articles: Agent1Output) -> Agent2Output:
    """
    Extract innovative ideas from analyzed articles using Gemini.
    
    Args:
        analyzed_articles: Output from Agent 1 with analyzed articles
    
    Returns:
        Agent2Output with extracted ideas
    
    Raises:
        Exception: If Gemini call fails or response is invalid
    """
    logger.info(f"Agent 2: Extracting ideas from {len(analyzed_articles.articles)} articles")
    
    # Prepare articles data for the prompt
    articles_text = "\n\n".join([
        f"Article {i+1}:\n"
        f"Title: {article.title}\n"
        f"Category: {article.category}\n"
        f"Relevance Score: {article.technical_relevance_score}/10\n"
        f"Summary: {article.summary}\n"
        f"URL: {article.url}"
        for i, article in enumerate(analyzed_articles.articles)
    ])
    
    # Build the full prompt
    full_prompt = f"{PROMPT_AGENT_2}\n\nHere are the analyzed articles:\n\n{articles_text}"
    
    # Call Gemini
    try:
        response_text = await gemini_client.call_gemini(
            prompt=full_prompt,
            response_format="json",
            temperature=0.7  # Higher temperature for creative idea extraction
        )
        
        # Parse JSON response
        response_data = json.loads(response_text)
        
        # Validate and create Agent2Output
        agent_output = Agent2Output(**response_data)
        
        logger.info(f"Agent 2: Successfully extracted {len(agent_output.ideas)} ideas")
        return agent_output
        
    except json.JSONDecodeError as e:
        logger.error(f"Agent 2: Failed to parse JSON response: {e}")
        logger.error(f"Response text: {response_text[:500]}")
        raise Exception(f"Agent 2 failed: Invalid JSON response from Gemini")
    except Exception as e:
        logger.error(f"Agent 2: Error during idea extraction: {str(e)}")
        raise
