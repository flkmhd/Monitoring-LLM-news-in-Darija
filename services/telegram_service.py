"""
Telegram Bot service for sending messages.
"""

import logging
import httpx
from typing import Optional
from config import config

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for interacting with Telegram Bot API."""
    
    def __init__(self):
        """Initialize Telegram service."""
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not set. Messages will not be sent.")
            
    async def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """
        Send a message via Telegram Bot.
        
        Args:
            message: The text message to send
            parse_mode: 'Markdown', 'HTML', or None
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.bot_token or not self.chat_id:
            logger.error("Cannot send message: Telegram credentials missing")
            return False
            
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }
            
            async with httpx.AsyncClient(timeout=config.API_TIMEOUT) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    logger.info("Telegram message sent successfully")
                    return True
                else:
                    logger.error(f"Failed to send Telegram message: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")
            return False


# Create a singleton instance
telegram_service = TelegramService()
