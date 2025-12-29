"""
Pydantic models for data validation throughout the agent pipeline.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


# ============================================================================
# Agent 1: News Fetcher Models
# ============================================================================

class Article(BaseModel):
    """Analyzed news article with categorization and scoring."""
    title: str
    url: str
    source: str
    published_at: str
    summary: str
    category: str = Field(..., description="breakthrough|trend|update|application")
    technical_relevance_score: int = Field(..., ge=0, le=10)


class Agent1Output(BaseModel):
    """Output from Agent 1: News analysis."""
    articles: List[Article]
    processed_at: str


# ============================================================================
# Agent 2: Idea Extractor Models
# ============================================================================

class Idea(BaseModel):
    """Extracted innovation idea from news articles."""
    title: str
    description: str
    source_article_url: str
    innovation_type: str
    impact_score: int = Field(..., ge=0, le=10)
    technical_difficulty: int = Field(..., ge=0, le=10)
    use_cases: List[str]
    why_interesting: str


class Agent2Output(BaseModel):
    """Output from Agent 2: Idea extraction."""
    ideas: List[Idea]
    total_extracted: int


# ============================================================================
# Agent 3: Reflection Agent Models
# ============================================================================

class TopIdea(BaseModel):
    """Top-ranked idea with validation and next steps."""
    rank: int = Field(..., ge=1, le=5)
    idea_title: str
    article_url: str
    impact_score: int = Field(..., ge=0, le=10)
    why_in_top_5: str
    next_step: str


class Agent3Output(BaseModel):
    """Output from Agent 3: Top 5 selection with reflection."""
    top_5_ideas: List[TopIdea]
    reflection: str


# ============================================================================
# Agent 4: Darija Translator Models
# ============================================================================

class ExplainedIdea(BaseModel):
    """Idea explained in Moroccan Darija."""
    rank: int = Field(..., ge=1, le=5)
    title_english: str
    darija_explanation: str
    source_url: str


class Agent4Output(BaseModel):
    """Output from Agent 4: Darija translations."""
    top_5_explained: List[ExplainedIdea]


# ============================================================================
# Pipeline Execution Models
# ============================================================================

class PipelineExecution(BaseModel):
    """Record of a complete pipeline execution."""
    execution_id: str
    started_at: str
    completed_at: Optional[str] = None
    status: str = Field(..., description="running|completed|failed")
    error_message: Optional[str] = None
    articles_fetched: int = 0
    ideas_extracted: int = 0
    telegram_sent: bool = False


class PipelineStatus(BaseModel):
    """Current status of the pipeline."""
    is_running: bool
    last_execution: Optional[PipelineExecution] = None
    next_scheduled_run: Optional[str] = None
