"""
Veille LLM Agent System - FastAPI Backend

Main application with API endpoints and pipeline orchestration.
"""

import logging
import uuid
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from config import config
from models import PipelineExecution, PipelineStatus
from services.newsapi_service import fetch_latest_news
from services.telegram_service import telegram_service
from agents.news_fetcher import analyze_news
from agents.idea_extractor import extract_ideas
from agents.reflection_agent import validate_and_reflect
from agents.darija_translator import translate_to_darija
from utils import (
    format_telegram_message,
    log_pipeline_execution,
    save_execution_history,
    load_execution_history,
    get_last_execution,
    get_current_timestamp
)
from scheduler import setup_scheduler

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global state
pipeline_running = False
scheduler = None


async def run_full_pipeline() -> PipelineExecution:
    """
    Run the complete pipeline: fetch news → 4 agents → WhatsApp.
    
    Returns:
        PipelineExecution object with execution details
    
    Raises:
        Exception: If any step fails
    """
    global pipeline_running
    
    # Prevent concurrent executions
    if pipeline_running:
        logger.warning("Pipeline already running, skipping this execution")
        raise Exception("Pipeline is already running")
    
    execution_id = str(uuid.uuid4())
    execution = PipelineExecution(
        execution_id=execution_id,
        started_at=get_current_timestamp(),
        status="running"
    )
    
    try:
        pipeline_running = True
        logger.info(f"Starting pipeline execution: {execution_id}")
        log_pipeline_execution("pipeline", "started", {"execution_id": execution_id})
        
        # Step 1: Fetch news from TheNewsAPI
        log_pipeline_execution("fetch_news", "started")
        raw_articles = await fetch_latest_news()
        execution.articles_fetched = len(raw_articles)
        log_pipeline_execution("fetch_news", "completed", {"count": len(raw_articles)})
        print(f"\n{'='*80}")
        print(f"STEP 1: Fetched {len(raw_articles)} articles from TheNewsAPI")
        print(f"{'='*80}\n")
        
        # Step 2: Agent 1 - Analyze news
        log_pipeline_execution("agent_1", "started")
        agent1_output = await analyze_news(raw_articles)
        log_pipeline_execution("agent_1", "completed")
        print(f"\n{'='*80}")
        print(f"AGENT 1 OUTPUT: Analyzed {len(agent1_output.articles)} articles")
        print(f"{'='*80}")
        for i, article in enumerate(agent1_output.articles[:3], 1):  # Show first 3
            print(f"\nArticle {i}:")
            print(f"  Title: {article.title}")
            print(f"  Category: {article.category}")
            print(f"  Relevance Score: {article.technical_relevance_score}/10")
            print(f"  Summary: {article.summary[:150]}...")
        if len(agent1_output.articles) > 3:
            print(f"\n... and {len(agent1_output.articles) - 3} more articles")
        print(f"\n{'='*80}\n")
        
        # Step 3: Agent 2 - Extract ideas
        log_pipeline_execution("agent_2", "started")
        agent2_output = await extract_ideas(agent1_output)
        execution.ideas_extracted = len(agent2_output.ideas)
        log_pipeline_execution("agent_2", "completed", {"count": len(agent2_output.ideas)})
        print(f"\n{'='*80}")
        print(f"AGENT 2 OUTPUT: Extracted {len(agent2_output.ideas)} ideas")
        print(f"{'='*80}")
        for i, idea in enumerate(agent2_output.ideas[:3], 1):  # Show first 3
            print(f"\nIdea {i}:")
            print(f"  Title: {idea.title}")
            print(f"  Type: {idea.innovation_type}")
            print(f"  Impact Score: {idea.impact_score}/10")
            print(f"  Description: {idea.description[:150]}...")
        if len(agent2_output.ideas) > 3:
            print(f"\n... and {len(agent2_output.ideas) - 3} more ideas")
        print(f"\n{'='*80}\n")
        
        # Step 4: Agent 3 - Validate and select top 5
        log_pipeline_execution("agent_3", "started")
        agent3_output = await validate_and_reflect(agent2_output)
        log_pipeline_execution("agent_3", "completed")
        print(f"\n{'='*80}")
        print(f"AGENT 3 OUTPUT: Top {len(agent3_output.top_5_ideas)} Ideas")
        print(f"{'='*80}")
        for idea in agent3_output.top_5_ideas:
            print(f"\n#{idea.rank}: {idea.idea_title}")
            print(f"  Impact Score: {idea.impact_score}/10")
            print(f"  Why in Top 5: {idea.why_in_top_5[:150]}...")
            print(f"  Next Step: {idea.next_step}")
        print(f"\nReflection: {agent3_output.reflection}")
        print(f"\n{'='*80}\n")
        
        # Step 5: Agent 4 - Translate to Darija
        log_pipeline_execution("agent_4", "started")
        agent4_output = await translate_to_darija(agent3_output)
        log_pipeline_execution("agent_4", "completed")
        print(f"\n{'='*80}")
        print(f"AGENT 4 OUTPUT: Darija Translations")
        print(f"{'='*80}")
        for idea in agent4_output.top_5_explained:
            print(f"\n#{idea.rank}: {idea.title_english}")
            print(f"  Darija: {idea.darija_explanation}")
            print(f"  Source: {idea.source_url}")
        print(f"\n{'='*80}\n")
        
        # Step 6: Format and send Telegram message
        log_pipeline_execution("send_telegram", "started")
        message = format_telegram_message(agent4_output)
        success = await telegram_service.send_message(message)
        execution.telegram_sent = success
        
        if success:
            log_pipeline_execution("send_telegram", "completed")
            print("\n✅ Telegram message sent successfully!")
        else:
            log_pipeline_execution("send_telegram", "failed")
            print("\n❌ Failed to send Telegram message.")
        
        # Mark as completed
        execution.status = "completed"
        execution.completed_at = get_current_timestamp()
        
        logger.info(f"Pipeline execution completed: {execution_id}")
        log_pipeline_execution("pipeline", "completed", {"execution_id": execution_id})
        
    except Exception as e:
        execution.status = "failed"
        execution.error_message = str(e)
        execution.completed_at = get_current_timestamp()
        
        logger.error(f"Pipeline execution failed: {execution_id} - {str(e)}")
        log_pipeline_execution("pipeline", "failed", {
            "execution_id": execution_id,
            "error": str(e)
        })
        
        # Try to send error notification via Telegram
        try:
            error_message = (
                "⚠️ *ERREUR - Veille LLM*\n\n"
                f"Le pipeline a échoué:\n{str(e)}\n\n"
                f"Execution ID: {execution_id}\n"
                f"Timestamp: {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
            )
            await telegram_service.send_message(error_message)
        except:
            pass  # Don't fail if error notification fails
        
        raise
    
    finally:
        pipeline_running = False
        # Save execution to history
        save_execution_history(execution)
    
    return execution


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global scheduler
    
    # Startup
    logger.info("Starting Veille LLM Agent System")
    
    # Validate configuration
    try:
        config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        logger.warning("Scheduler will not start without valid configuration")
    
    # Set up scheduler
    scheduler = setup_scheduler(run_full_pipeline)
    scheduler.start()
    logger.info("Scheduler started")
    
    yield
    
    # Shutdown
    if scheduler:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    logger.info("Veille LLM Agent System stopped")


# Create FastAPI app
app = FastAPI(
    title="Veille LLM Agent System",
    description="AI-powered news monitoring for LLMs & new technologies",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Veille LLM Agent System",
        "timestamp": get_current_timestamp()
    }


@app.post("/trigger")
async def trigger_pipeline_manually():
    """Manually trigger the pipeline execution."""
    try:
        execution = await run_full_pipeline()
        return {
            "message": "Pipeline executed successfully",
            "execution": execution.model_dump()
        }
    except Exception as e:
        logger.error(f"Manual pipeline trigger failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_pipeline_status():
    """Get current pipeline status and last execution."""
    last_execution = get_last_execution()
    
    # Get next scheduled run
    next_run = None
    if scheduler:
        job = scheduler.get_job("daily_pipeline")
        if job and job.next_run_time:
            next_run = job.next_run_time.isoformat()
    
    status = PipelineStatus(
        is_running=pipeline_running,
        last_execution=PipelineExecution(**last_execution) if last_execution else None,
        next_scheduled_run=next_run
    )
    
    return status.model_dump()


@app.get("/history")
async def get_execution_history(limit: int = 10):
    """Get execution history."""
    if limit < 1 or limit > 50:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 50")
    
    history = load_execution_history(limit=limit)
    
    return {
        "count": len(history),
        "executions": history
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
