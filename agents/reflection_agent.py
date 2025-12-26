"""
Agent 3: Reflection & Validation
Selects and validates the top 5 ideas with reflection.
"""

import json
import logging
from datetime import datetime

from models import Agent2Output, Agent3Output, TopIdea
from services.gemini_service import gemini_client
from prompts import PROMPT_AGENT_3

logger = logging.getLogger(__name__)


async def validate_and_reflect(ideas: Agent2Output) -> Agent3Output:
    """
    Validate ideas and select top 5 using Gemini.
    
    Args:
        ideas: Output from Agent 2 with extracted ideas
    
    Returns:
        Agent3Output with top 5 ideas and reflection
    
    Raises:
        Exception: If Gemini call fails or response is invalid
    """
    logger.info(f"Agent 3: Validating and selecting top 5 from {len(ideas.ideas)} ideas")
    
    # Prepare ideas data for the prompt
    ideas_text = "\n\n".join([
        f"Idea {i+1}:\n"
        f"Title: {idea.title}\n"
        f"Description: {idea.description}\n"
        f"Innovation Type: {idea.innovation_type}\n"
        f"Impact Score: {idea.impact_score}/10\n"
        f"Technical Difficulty: {idea.technical_difficulty}/10\n"
        f"Use Cases: {', '.join(idea.use_cases)}\n"
        f"Why Interesting: {idea.why_interesting}\n"
        f"Source: {idea.source_article_url}"
        for i, idea in enumerate(ideas.ideas)
    ])
    
    # Build the full prompt
    full_prompt = f"{PROMPT_AGENT_3}\n\nHere are the extracted ideas:\n\n{ideas_text}"
    
    # Call Gemini
    try:
        response_text = await gemini_client.call_gemini(
            prompt=full_prompt,
            response_format="json",
            temperature=0.6  # Moderate temperature for balanced selection
        )
        
        # Parse JSON response
        response_data = json.loads(response_text)
        
        # Validate and create Agent3Output
        agent_output = Agent3Output(**response_data)
        
        logger.info(f"Agent 3: Successfully selected top {len(agent_output.top_5_ideas)} ideas")
        return agent_output
        
    except json.JSONDecodeError as e:
        logger.error(f"Agent 3: Failed to parse JSON response: {e}")
        logger.error(f"Response text: {response_text[:500]}")
        raise Exception(f"Agent 3 failed: Invalid JSON response from Gemini")
    except Exception as e:
        logger.error(f"Agent 3: Error during validation: {str(e)}")
        raise
