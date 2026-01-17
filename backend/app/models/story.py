"""
Data models for story generation.

This module defines Pydantic models for story generation requests, responses,
workflow status tracking, and evaluation results.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime


# Story mood types
StoryMood = Literal["MODERN_ROMANCE_DRAMA_MANHWA", "FANTASY_ROMANCE_MANHWA", "HISTORY_SAGEUK_ROMANCE", "ACADEMY_SCHOOL_LIFE", "ISEKAI_OTOME_FANTASY"]


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
    """
    Character model with detailed physical and personality attributes.
    
    The LLM generates these fields from the story. They should all be populated.
    """
    name: str = Field(
        ..., 
        description="The name of the character.",
        min_length=1,
        max_length=100
    )
    gender: str = Field(
        ..., 
        description="Gender of the character (e.g., male, female, non-binary).",
        min_length=1,
        max_length=50
    )
    age: str = Field(
        ..., 
        description="Age of the character (e.g., '20', '30', '40').",
        min_length=1,
        max_length=50
    )
    face: str = Field(
        ..., 
        description="Facial features including jawline, face shape, eye color, skin tone, and distinctive features.",
        min_length=5,
        max_length=500
    )
    hair: str = Field(
        ..., 
        description="Hair description including length, color, style, and texture.",
        min_length=3,
        max_length=300
    )
    body: str = Field(
        ..., 
        description="Body type, build, height, and physical characteristics.",
        min_length=3,
        max_length=300
    )
    outfit: str = Field(
        ..., 
        description="Clothing, accessories, and overall style.",
        min_length=3,
        max_length=500
    )
    mood: str = Field(
        ..., 
        description="Character's typical mood, personality vibe, or demeanor.",
        min_length=3,
        max_length=200
    )
    visual_description: str = Field(
        ..., 
        description="Complete visual description combining all attributes. Used for image generation.",
        min_length=20,
        max_length=2000
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ji-hoon",
                "gender": "male",
                "face": "sharp jawline, dark brown eyes, olive skin tone, high cheekbones",
                "hair": "short black hair, neatly styled with slight wave",
                "body": "tall athletic build, broad shoulders, lean muscular frame",
                "outfit": "tailored navy suit with white dress shirt, silver watch",
                "mood": "confident and charismatic with a hint of mystery",
                "visual_description": "A tall man with sharp jawline, dark brown eyes, olive skin, high cheekbones, short black hair neatly styled with slight wave, athletic build with broad shoulders and lean muscular frame, wearing a tailored navy suit with white dress shirt and silver watch, confident and charismatic demeanor with a hint of mystery"
            }
        }



class WebtoonPanel(BaseModel):
    """
    Webtoon panel with scene description and dialogue.
    
    Each panel represents a single frame in the webtoon with
    camera angle, characters, visual description, and optional dialogue.
    """
    panel_number: int = Field(
        ..., 
        description="Sequential panel number starting from 1.",
        ge=1,
        le=100
    )
    shot_type: str = Field(
        default="Medium Shot", 
        description="Camera angle (e.g., Low Angle, Dutch Angle, Close-up, Wide Shot, Bird's Eye).",
        max_length=100
    )
    active_character_names: List[str] = Field(
        default_factory=list, 
        description="List of character names appearing in this panel.",
        max_items=10
    )
    visual_prompt: str = Field(
        default="", 
        description="Self-contained image generation prompt with full character descriptions, not just names.",
        max_length=2000
    )
    dialogue: Optional[str] = Field(
        None, 
        description="Character dialogue or sound effects for this panel.",
        max_length=500
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "panel_number": 1,
                "shot_type": "Medium Shot",
                "active_character_names": ["Ji-hoon", "Hana"],
                "visual_prompt": "Medium shot of a tall man with sharp jawline, dark brown eyes, olive skin (Ji-hoon) standing across from a woman with long wavy brown hair, bright green eyes (Hana) in a modern office with glass windows in the background, soft natural lighting",
                "dialogue": "Ji-hoon: 'We need to talk about what happened.'"
            }
        }


class WebtoonScript(BaseModel):
    """
    Complete webtoon script with characters and panels.
    
    Contains all character definitions and sequential panels
    for the webtoon story.
    """
    characters: List[Character] = Field(
        ..., 
        description="List of all characters in the webtoon.",
        min_items=1,
        max_items=20
    )
    panels: List[WebtoonPanel] = Field(
        ..., 
        description="List of sequential panels (8-16 recommended).",
        min_items=1,
        max_items=50
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "characters": [
                    {
                        "name": "Ji-hoon",
                        "gender": "male",
                        "face": "sharp jawline, dark brown eyes, olive skin",
                        "hair": "short black hair, neatly styled",
                        "body": "tall athletic build, broad shoulders",
                        "outfit": "tailored navy suit with white shirt",
                        "mood": "confident and charismatic",
                        "visual_description": "A tall man with sharp jawline, dark brown eyes, olive skin, short black hair neatly styled, athletic build with broad shoulders, wearing a tailored navy suit with white shirt, confident demeanor"
                    }
                ],
                "panels": [
                    {
                        "panel_number": 1,
                        "shot_type": "Wide Shot",
                        "active_character_names": ["Ji-hoon"],
                        "visual_prompt": "Wide shot of a tall man with sharp jawline, dark brown eyes, olive skin (Ji-hoon) standing in a modern office",
                        "dialogue": "Ji-hoon: 'This is just the beginning.'"
                    }
                ]
            }
        }



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
        gender: Character gender for base style selection
        image_style: Image style/mood selection
    """
    script_id: str = Field(..., description="Webtoon script ID")
    character_name: str = Field(..., description="Character name")
    description: str = Field(..., description="Visual description for generation")
    gender: str = Field(..., description="Character gender (male/female)")
    image_style: Literal["MODERN_ROMANCE_DRAMA_MANHWA", "FANTASY_ROMANCE_MANHWA", "HISTORY_SAGEUK_ROMANCE", "ACADEMY_SCHOOL_LIFE", "ISEKAI_OTOME_FANTASY"] = Field(
        ..., description="Image style/genre selection"
    )