"""
Data models for story generation.

This module defines Pydantic models for story generation requests, responses,
workflow status tracking, and evaluation results.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal, List
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



class Character(BaseModel):
    name: str = Field(..., description="The name of the character.")
    visual_description: str = Field(..., description="A dense, comma-separated string describing hair, eyes, body, outfit, and vibe. This string will be re-used in every panel prompt.")

class WebtoonPanel(BaseModel):
    panel_number: int
    shot_type: str = Field(..., description="Camera angle (e.g., Low Angle, Dutch Angle, Close-up).")
    active_character_names: List[str] = Field(..., description="List of names of characters appearing in this specific panel.")
    visual_prompt: str = Field(..., description="The self-contained image generation prompt. MUST include the full physical description of the characters present, not just their names.")
    dialogue: Optional[str] = Field(None, description="Brief dialogue or SFX, if any.")

class WebtoonScript(BaseModel):
    characters: List[Character]
    panels: List[WebtoonPanel]


class CharacterImage(BaseModel):
    """
    Model for generated character images.
    
    Attributes:
        id: Unique identifier for the image
        character_name: Name of the character
        description: Visual description used to generate the image
        image_url: URL or base64 encoded image data
        created_at: Timestamp when the image was created
        is_selected: Whether this image is selected as the final version
    """
    id: str = Field(..., description="Unique image ID")
    character_name: str = Field(..., description="Character name")
    description: str = Field(..., description="Visual description used for generation")
    image_url: str = Field(..., description="Image URL or base64 data")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    is_selected: bool = Field(default=False, description="Is this the selected final image")


class WebtoonScriptResponse(BaseModel):
    """
    Response model for webtoon script with generated images.
    
    Attributes:
        script_id: Unique identifier for the script
        story_id: ID of the source story
        characters: List of characters with descriptions
        panels: List of scene panels
        character_images: Dictionary mapping character names to their generated images
        created_at: Timestamp when the script was created
    """
    script_id: str = Field(..., description="Unique script ID")
    story_id: str = Field(..., description="Source story ID")
    characters: List[Character] = Field(..., description="List of characters")
    panels: List[WebtoonPanel] = Field(..., description="List of scene panels")
    character_images: dict = Field(default_factory=dict, description="Character name to images mapping")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")


class GenerateWebtoonRequest(BaseModel):
    """
    Request model for webtoon script generation.
    
    Attributes:
        story_id: ID of the story to convert to webtoon script
    """
    story_id: str = Field(..., description="Story ID to convert")


class GenerateCharacterImageRequest(BaseModel):
    """
    Request model for character image generation.
    
    Attributes:
        script_id: ID of the webtoon script
        character_name: Name of the character
        description: Visual description for image generation
    """
    script_id: str = Field(..., description="Webtoon script ID")
    character_name: str = Field(..., description="Character name")
    description: str = Field(..., description="Visual description for generation")