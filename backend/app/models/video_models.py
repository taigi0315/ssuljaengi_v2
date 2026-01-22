"""
Video generation models for Pydantic validation.
"""
from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.models.sfx import SFXBundle


class BubbleData(BaseModel):
    """Single dialogue bubble data."""
    text: str
    x: float = Field(..., ge=0, le=100, description="X position as percentage (0-100)")
    y: float = Field(..., ge=0, le=100, description="Y position as percentage (0-100)")
    width: Optional[float] = Field(default=30, ge=5, le=100, description="Width as percentage (5-100)")
    height: Optional[float] = Field(default=None, ge=5, le=100, description="Height as percentage (5-100)")
    character_name: Optional[str] = None


class VideoPanelData(BaseModel):
    """Panel data for video generation."""
    panel_number: int
    image_url: str
    bubbles: List[BubbleData] = []
    sfx_bundle: Optional[dict] = Field(
        default=None,
        description="Optional SFX bundle data for visual effects (serialized SFXBundle)"
    )


class GenerateVideoRequest(BaseModel):
    """Request to generate video from panels."""
    script_id: str
    panels: List[VideoPanelData]


class VideoConfig(BaseModel):
    """Configuration for video generation."""
    width: int = 1080
    height: int = 1920  # 9:16 ratio (vertical video for TikTok/Shorts/Reels)
    base_duration_ms: int = 350
    # bubble_duration_ms: int = 2750  # REMOVED: Replaced by dynamic duration
    min_bubble_duration_ms: int = 1500  # Minimum duration
    per_char_duration_ms: int = 50      # Added duration per character
    final_pause_ms: int = 350
    transition_duration_ms: int = 550  # Duration of scroll transition between panels
    fps: int = 30
    font_size: int = 47
    bubble_padding: int = 20
    bubble_bg_opacity: float = 0.35
    bubble_border_width: int = 5
    bubble_border_color: str = "#4a4a4a"
    bubble_text_color: str = "#000000"
    bubble_name_color: str = "#6b21a8"  # Purple-800
    crf: int = 18  # FFmpeg quality (lower = better)
