"""
Utility functions for the Veille LLM Agent System.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from models import Agent4Output, PipelineExecution

logger = logging.getLogger(__name__)

# Path to execution history file
HISTORY_FILE = Path("execution_history.json")


def format_telegram_message(top_ideas: Agent4Output) -> str:
    """
    Format the top 5 ideas in Darija as a Telegram message (Markdown).
    
    Args:
        top_ideas: Agent4Output with Darija explanations
    
    Returns:
        Formatted Telegram message with emojis and structure
    """
    message_parts = [
        "🚀 *TOP 5 IDÉES LLM/AI - AUJOURD'HUI*",
        "",
        "Voici les 5 idées les plus intéressantes du moment:",
        ""
    ]
    
    # Add each idea
    for idea in top_ideas.top_5_explained:
        emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][idea.rank - 1]
        
        message_parts.extend([
            f"{emoji} *{idea.title_english}*",
            f"{idea.darija_explanation}",
            f"🔗 [Source]({idea.source_url})",
            ""
        ])
    
    # Add footer
    message_parts.extend([
        "---",
        "💡 *Veille LLM Agent System*",
        f"📅 {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
    ])
    
    return "\n".join(message_parts)


def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    
    Returns:
        ISO formatted timestamp string
    """
    return datetime.now().isoformat()


def log_pipeline_execution(
    step: str,
    status: str,
    data: Dict[str, Any] = None
) -> None:
    """
    Log a pipeline execution step.
    
    Args:
        step: Name of the pipeline step
        status: Status ("started", "completed", "failed")
        data: Optional additional data to log
    """
    log_data = {
        "timestamp": get_current_timestamp(),
        "step": step,
        "status": status,
    }
    
    if data:
        log_data.update(data)
    
    if status == "started":
        logger.info(f"Pipeline step started: {step}")
    elif status == "completed":
        logger.info(f"Pipeline step completed: {step}")
    elif status == "failed":
        logger.error(f"Pipeline step failed: {step}", extra=log_data)
    
    # Log as JSON for structured logging
    logger.debug(json.dumps(log_data))


def save_execution_history(execution: PipelineExecution) -> None:
    """
    Save pipeline execution to history file.
    
    Args:
        execution: PipelineExecution object to save
    """
    try:
        # Load existing history
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = []
        
        # Add new execution
        history.append(execution.model_dump())
        
        # Keep only last 50 executions
        history = history[-50:]
        
        # Save back to file
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved execution history: {execution.execution_id}")
        
    except Exception as e:
        logger.error(f"Failed to save execution history: {str(e)}")


def load_execution_history(limit: int = 10) -> list[Dict[str, Any]]:
    """
    Load execution history from file.
    
    Args:
        limit: Maximum number of executions to return
    
    Returns:
        List of execution dictionaries (most recent first)
    """
    try:
        if not HISTORY_FILE.exists():
            return []
        
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
        
        # Return most recent first
        return history[-limit:][::-1]
        
    except Exception as e:
        logger.error(f"Failed to load execution history: {str(e)}")
        return []


def get_last_execution() -> Dict[str, Any] | None:
    """
    Get the most recent pipeline execution.
    
    Returns:
        Last execution dictionary or None if no history
    """
    history = load_execution_history(limit=1)
    return history[0] if history else None
