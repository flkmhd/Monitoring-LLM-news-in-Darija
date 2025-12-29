"""
Google Gemini API service for LLM calls.
"""

import json
import logging
import asyncio
from typing import Any, Dict, Optional
import google.generativeai as genai

from config import config

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Google Gemini API with retry logic and error handling."""
    
    def __init__(self):
        """Initialize Gemini client with API key."""
        genai.configure(api_key=config.GEMINI_API_KEY)
        # Use gemini-2.5-flash which is stable and widely available
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        logger.info(f"Initialized Gemini client with model: gemini-2.5-flash")
    
    async def call_gemini(
        self,
        prompt: str,
        response_format: str = "json",
        temperature: float = 0.7,
        max_retries: int = None
    ) -> str:
        """
        Call Gemini API with retry logic.
        
        Args:
            prompt: The prompt to send to Gemini
            response_format: Expected format ("json" or "text")
            temperature: Sampling temperature (0.0 to 1.0)
            max_retries: Maximum retry attempts (default: from config)
        
        Returns:
            Response text from Gemini
        
        Raises:
            Exception: If all retries fail
        """
        if max_retries is None:
            max_retries = config.MAX_RETRIES
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Calling Gemini API (attempt {attempt + 1}/{max_retries})")
                
                # Configure generation
                generation_config = {
                    "temperature": temperature,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
                
                # Add JSON mode instruction if needed
                if response_format == "json":
                    full_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON, no markdown formatting, no explanations."
                else:
                    full_prompt = prompt
                
                # Make the API call (synchronous, so we run in executor)
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(
                        full_prompt,
                        generation_config=generation_config
                    )
                )
                
                # Extract text
                response_text = response.text
                
                # Validate JSON if expected
                if response_format == "json":
                    try:
                        # Try to parse to validate
                        json.loads(response_text)
                        logger.info("Successfully received valid JSON response from Gemini")
                    except json.JSONDecodeError as e:
                        logger.warning(f"Response is not valid JSON initially: {e}")
                        # Try to extract JSON from markdown code blocks
                        response_text = self._extract_json_from_markdown(response_text)
                        
                        # Validate again after extraction
                        try:
                            json.loads(response_text)
                            logger.info("Successfully extracted valid JSON from markdown")
                        except json.JSONDecodeError as e2:
                            logger.error(f"Failed to extract valid JSON: {e2}")
                            # If we can't parse it, we'll return it as is and let the caller handle the error
                            # or we could raise an exception here to trigger a retry
                            if attempt < max_retries - 1:
                                raise Exception(f"Failed to parse JSON response: {e2}") from e2
                
                return response_text
                
            except Exception as e:
                last_error = e
                logger.warning(f"Gemini API call failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
        
        # All retries failed
        logger.error(f"All {max_retries} attempts failed. Last error: {str(last_error)}")
        raise Exception(f"Gemini API call failed after {max_retries} attempts: {str(last_error)}")
    
    def _extract_json_from_markdown(self, text: str) -> str:
        """
        Extract JSON from markdown code blocks using regex.
        
        Args:
            text: Response text that might contain markdown
        
        Returns:
            Extracted JSON string or original text
        """
        import re
        
        # Pattern to find JSON blocks: ```json ... ``` or just ``` ... ```
        # We look for the content between the backticks
        pattern = r"```(?:json)?\s*(.*?)```"
        
        # Find all matches (DOTALL to match newlines)
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            # Return the first match, stripped of whitespace
            return matches[0].strip()
        
        return text.strip()


# Create a singleton instance
gemini_client = GeminiClient()
