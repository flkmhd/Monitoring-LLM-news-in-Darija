"""
Configuration module for Veille LLM Agent System.
Loads and validates environment variables.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    
    # TheNewsAPI.com
    NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY", "")
    NEWSAPI_LIMIT: int = int(os.getenv("NEWSAPI_LIMIT", "20"))
    
    # Google Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Scheduling
    SCHEDULE_TIME: str = os.getenv("SCHEDULE_TIME", "09:00")
    TIMEZONE: str = os.getenv("TIMEZONE", "Europe/Paris")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # API Timeouts
    API_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    
    @classmethod
    def validate(cls) -> None:
        """Validate that all required environment variables are set."""
        required_vars = {
            "NEWSAPI_KEY": cls.NEWSAPI_KEY,
            "GEMINI_API_KEY": cls.GEMINI_API_KEY,
            "TELEGRAM_BOT_TOKEN": cls.TELEGRAM_BOT_TOKEN,
            "TELEGRAM_CHAT_ID": cls.TELEGRAM_CHAT_ID,
        }
        
        missing = [key for key, value in required_vars.items() if not value]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please copy .env.example to .env and fill in the values."
            )
    
    @classmethod
    def get_schedule_hour_minute(cls) -> tuple[int, int]:
        """Parse SCHEDULE_TIME into hour and minute."""
        try:
            hour, minute = cls.SCHEDULE_TIME.split(":")
            return int(hour), int(minute)
        except (ValueError, AttributeError):
            # Default to 9:00 AM if parsing fails
            return 9, 0


# Create a singleton instance
config = Config()
