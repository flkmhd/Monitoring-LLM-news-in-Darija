"""
Scheduler configuration for daily pipeline execution.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from config import config

logger = logging.getLogger(__name__)


def setup_scheduler(pipeline_func):
    """
    Set up APScheduler for daily pipeline execution.
    
    Args:
        pipeline_func: Async function to run (the pipeline)
    
    Returns:
        Configured AsyncIOScheduler instance
    """
    # Create scheduler
    scheduler = AsyncIOScheduler()
    
    # Get schedule time
    hour, minute = config.get_schedule_hour_minute()
    
    # Create cron trigger for daily execution
    tz = timezone(config.TIMEZONE)
    trigger = CronTrigger(
        hour=hour,
        minute=minute,
        timezone=tz
    )
    
    # Add job
    scheduler.add_job(
        pipeline_func,
        trigger=trigger,
        id="daily_pipeline",
        name="Daily LLM News Pipeline",
        replace_existing=True
    )
    
    logger.info(
        f"Scheduler configured: Daily execution at {hour:02d}:{minute:02d} {config.TIMEZONE}"
    )
    
    return scheduler
