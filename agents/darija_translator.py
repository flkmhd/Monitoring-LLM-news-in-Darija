"""
Agent 4: Darija Translator
Translates top 5 ideas to Moroccan Darija with clear explanations.
"""

import json
import logging
from datetime import datetime

from models import Agent3Output, Agent4Output, ExplainedIdea
from services.gemini_service import gemini_client
from prompts import PROMPT_AGENT_4

logger = logging.getLogger(__name__)


async def translate_to_darija(top_ideas: Agent3Output) -> Agent4Output:
    """
    Translate top 5 ideas to Moroccan Darija using Gemini.
    
    Args:
        top_ideas: Output from Agent 3 with top 5 ideas
    
    Returns:
        Agent4Output with Darija translations
    
    Raises:
        Exception: If Gemini call fails or response is invalid
    """
    logger.info(f"Agent 4: Translating {len(top_ideas.top_5_ideas)} ideas to Darija")
    
    # Prepare ideas data for the prompt
    ideas_text = "\n\n".join([
        f"Idea #{idea.rank}:\n"
        f"Title: {idea.idea_title}\n"
        f"Impact Score: {idea.impact_score}/10\n"
        f"Why in Top 5: {idea.why_in_top_5}\n"
        f"Next Step: {idea.next_step}\n"
        f"Source URL: {idea.article_url}"
        for idea in top_ideas.top_5_ideas
    ])
    
    # Build the full prompt
    full_prompt = f"{PROMPT_AGENT_4}\n\nHere are the top 5 ideas to translate:\n\n{ideas_text}"
    
    # Call Gemini
    try:
        response_text = await gemini_client.call_gemini(
            prompt=full_prompt,
            response_format="json",
            temperature=0.8  # Higher temperature for natural, conversational Darija
        )
        
        # Parse JSON response
        response_data = json.loads(response_text)
        
        # Validate and create Agent4Output
        agent_output = Agent4Output(**response_data)
        
        logger.info(f"Agent 4: Successfully translated {len(agent_output.top_5_explained)} ideas to Darija")
        return agent_output
        
    except json.JSONDecodeError as e:
        logger.error(f"Agent 4: Failed to parse JSON response: {e}")
        logger.error(f"Response text: {response_text[:500]}")
        raise Exception(f"Agent 4 failed: Invalid JSON response from Gemini")
    except Exception as e:
        logger.error(f"Agent 4: Error during translation: {str(e)}")
        raise
