"""
Video generation models for Pydantic validation.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class BubbleData(BaseModel):
    """Single dialogue bubble data."""
    text: str
    x: float = Field(..., ge=0, le=100, description="X position as percentage (0-100)")
    y: float = Field(..., ge=0, le=100, description="Y position as percentage (0-100)")


class VideoPanelData(BaseModel):
    """Panel data for video generation."""
    panel_number: int
    image_url: str
    bubbles: List[BubbleData] = []


class GenerateVideoRequest(BaseModel):
    """Request to generate video from panels."""
    script_id: str
    panels: List[VideoPanelData]


class VideoConfig(BaseModel):
    """Configuration for video generation."""
    width: int = 1080
    height: int = 1920  # 9:16 ratio (vertical video for TikTok/Shorts/Reels)
    base_duration_ms: int = 250
    bubble_duration_ms: int = 2500
    final_pause_ms: int = 250
    transition_duration_ms: int = 1250  # Duration of scroll transition between panels
    fps: int = 30
    font_size: int = 47
    bubble_padding: int = 30
    bubble_bg_opacity: float = 0.35
    bubble_border_width: int = 5
    bubble_border_color: str = "#4a4a4a"
    bubble_text_color: str = "#000000"
    crf: int = 18  # FFmpeg quality (lower = better)
