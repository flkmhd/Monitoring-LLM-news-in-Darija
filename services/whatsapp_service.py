"""
Twilio WhatsApp service for sending messages.
"""

import logging
from typing import Optional
from twilio.rest import Client

from config import config

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service for sending WhatsApp messages via Twilio."""
    
    def __init__(self):
        """Initialize Twilio client."""
        self.client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        self.from_number = f"whatsapp:{config.TWILIO_PHONE_FROM}"
        logger.info("Initialized Twilio WhatsApp service")
    
    async def send_message(
        self,
        message: str,
        to_number: Optional[str] = None
    ) -> bool:
        """
        Send a WhatsApp message via Twilio.
        
        Args:
            message: The message text to send
            to_number: Recipient WhatsApp number (default: from config)
        
        Returns:
            True if message sent successfully, False otherwise
        """
        if to_number is None:
            to_number = config.WHATSAPP_TO_NUMBER
        
        # Ensure number is in WhatsApp format
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
        
        try:
            logger.info(f"Sending WhatsApp message to {to_number}")
            
            # Send message
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info(f"WhatsApp message sent successfully. SID: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            return False


# Create a singleton instance
whatsapp_service = WhatsAppService()
