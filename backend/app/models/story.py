"""
Data models for story generation.

This module defines Pydantic models for story generation requests, responses,
workflow status tracking, and evaluation results.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# Story mood types
StoryMood = Literal["rofan", "modern_romance", "slice_of_life", "revenge", "high_teen"]


class StoryRequest(BaseModel):
    """
    Request model for story generation.
    
    Attributes:
        post_id: Unique identifier for the Reddit post
        post_title: Title of the Reddit post
        post_content: Content/body of the Reddit post
        mood: Story mood/style selection
        options: Optional configuration for story generation
    """
    post_id: str = Field(..., description="Reddit post ID")
    post_title: str = Field(..., description="Reddit post title", min_length=1)
    post_content: str = Field(..., description="Reddit post content")
    mood: StoryMood = Field(..., description="Story mood/style")
    options: Optional[dict] = Field(default=None, description="Optional generation options")


class Story(BaseModel):
    """
    Story model representing a generated story.
    
    Attributes:
        id: Unique identifier for the story
        content: The generated story text
        evaluation_score: Quality score from evaluator (1-10)
        rewrite_count: Number of times the story was rewritten
        created_at: Timestamp when the story was created
        metadata: Optional additional metadata
    """
    id: str = Field(..., description="Unique story ID")
    content: str = Field(..., description="Generated story content")
    evaluation_score: float = Field(..., description="Quality score (1-10)", ge=0, le=10)
    rewrite_count: int = Field(default=0, description="Number of rewrites", ge=0)
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")


class StoryResponse(BaseModel):
    """
    Response model for story retrieval.
    
    Attributes:
        story: The generated story
        generation_time: Time taken to generate the story (seconds)
        workflow_info: Information about the workflow execution
    """
    story: Story = Field(..., description="Generated story")
    generation_time: float = Field(..., description="Generation time in seconds", ge=0)
    workflow_info: dict = Field(..., description="Workflow execution details")


class WorkflowStatus(BaseModel):
    """
    Model for tracking workflow execution status.
    
    Attributes:
        workflow_id: Unique identifier for the workflow
        status: Current status of the workflow
        current_step: Current step being executed
        progress: Progress percentage (0.0 to 1.0)
        story_id: ID of the generated story (when completed)
        error: Error message (if failed)
    """
    workflow_id: str = Field(..., description="Unique workflow ID")
    status: Literal["started", "in_progress", "completed", "failed"] = Field(
        ..., description="Workflow status"
    )
    current_step: str = Field(..., description="Current workflow step")
    progress: float = Field(..., description="Progress (0.0 to 1.0)", ge=0.0, le=1.0)
    story_id: Optional[str] = Field(default=None, description="Story ID when completed")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class EvaluationResult(BaseModel):
    """
    Model for story evaluation results.
    
    Attributes:
        score: Overall quality score (1-10)
        feedback: Detailed feedback for improvement
        coherence: Coherence score (1-10)
        engagement: Engagement score (1-10)
        length_appropriate: Whether the length is appropriate
    """
    score: float = Field(..., description="Overall score (1-10)", ge=0, le=10)
    feedback: str = Field(..., description="Detailed feedback")
    coherence: float = Field(..., description="Coherence score (1-10)", ge=0, le=10)
    engagement: float = Field(..., description="Engagement score (1-10)", ge=0, le=10)
    length_appropriate: bool = Field(..., description="Is length appropriate")
