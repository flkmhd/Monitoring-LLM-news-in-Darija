"""
Standalone script to run the Veille LLM Pipeline.
This script can be scheduled with Windows Task Scheduler or cron.
"""

import asyncio
import logging
import sys
from datetime import datetime

# Configure simple logging for the script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline_script.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("run_pipeline")

async def main():
    """Run the full pipeline standalone."""
    try:
        logger.info("="*50)
        logger.info("Starting scheduled pipeline execution")
        logger.info("="*50)
        
        # Import here to avoid issues if env vars aren't set during top-level import
        from main import run_full_pipeline
        from config import config
        
        # Validate config first
        config.validate()
        logger.info("Configuration validated")
        
        # Run the pipeline
        execution = await run_full_pipeline()
        
        logger.info("="*50)
        if execution.status == "completed":
            logger.info(f"✅ Pipeline completed successfully! ID: {execution.execution_id}")
            logger.info(f"Articles: {execution.articles_fetched}, Ideas: {execution.ideas_extracted}")
        else:
            logger.error(f"❌ Pipeline failed! ID: {execution.execution_id}")
            logger.error(f"Error: {execution.error_message}")
            sys.exit(1)
            
    except Exception as e:
        logger.critical(f"Verified critical error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
