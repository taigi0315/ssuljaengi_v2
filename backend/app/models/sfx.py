"""
SFX (Sound/Visual Effects) Models for Webtoon Enhancement.

This module defines Pydantic models for various visual effects that can be
applied to webtoon panels during video generation:
- ImpactText: Onomatopoeia text like "CRASH!", "THUMP!"
- MotionEffect: Speed lines, blur, impact bursts
- ScreenEffect: Flash, shake, vignette
- EmotionalEffect: Sparkles, hearts, dark aura

v2.0.0: Initial implementation
"""

from enum import Enum
from typing import Optional, Union, List, Literal, Tuple
from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Enums for SFX Types
# ============================================================================

class ImpactTextStyle(str, Enum):
    """Style variations for impact text."""
    BOLD = "bold"              # Strong, heavy text
    SHAKY = "shaky"            # Trembling/vibrating text
    EXPLOSIVE = "explosive"    # Radiating/burst effect
    SOFT = "soft"              # Gentle, rounded text
    SHARP = "sharp"            # Angular, aggressive text
    COMIC = "comic"            # Classic comic book style


class ImpactTextSize(str, Enum):
    """Size options for impact text."""
    SMALL = "small"        # Subtle effect
    MEDIUM = "medium"      # Standard size
    LARGE = "large"        # Prominent effect
    MASSIVE = "massive"    # Screen-dominating


class ImpactTextAnimation(str, Enum):
    """Animation types for impact text."""
    NONE = "none"          # Static display
    POP = "pop"            # Quick scale in
    SHAKE = "shake"        # Vibrate in place
    GROW = "grow"          # Gradual scale up
    FLASH = "flash"        # Blink/flash in
    BOUNCE = "bounce"      # Bouncy entrance


class MotionEffectType(str, Enum):
    """Types of motion effects."""
    SPEED_LINES = "speed_lines"      # Classic manga speed lines
    BLUR = "blur"                    # Motion blur
    IMPACT_BURST = "impact_burst"    # Radial impact lines
    ZOOM_LINES = "zoom_lines"        # Converging focus lines
    WIND_LINES = "wind_lines"        # Flowing wind effect


class MotionDirection(str, Enum):
    """Direction of motion effects."""
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    CENTER = "center"      # Converging to center
    RADIAL = "radial"      # Radiating outward


class EffectIntensity(str, Enum):
    """Intensity levels for effects."""
    SUBTLE = "subtle"      # Barely noticeable
    MEDIUM = "medium"      # Standard visibility
    INTENSE = "intense"    # Very prominent


class ScreenEffectType(str, Enum):
    """Types of screen-wide effects."""
    FLASH = "flash"            # White flash
    SHAKE = "shake"            # Screen shake
    VIGNETTE = "vignette"      # Dark edges
    COLOR_SHIFT = "color_shift"  # Color tint change
    BLUR = "blur"              # Full screen blur
    DARKEN = "darken"          # Fade to dark


class EmotionalEffectType(str, Enum):
    """Types of emotional visual effects."""
    SPARKLES = "sparkles"      # Shimmering sparkles
    HEARTS = "hearts"          # Floating hearts
    FLOWERS = "flowers"        # Flower petals
    DARK_AURA = "dark_aura"    # Dark menacing aura
    SWEAT_DROP = "sweat_drop"  # Anime sweat drop
    BLUSH = "blush"            # Blushing cheeks effect
    ANGER_VEIN = "anger_vein"  # Throbbing vein
    SHOCK_LINES = "shock_lines"  # Surprised reaction lines
    TEARS = "tears"            # Tear drops
    GLOW = "glow"              # Ethereal glow


class EmotionalEffectPosition(str, Enum):
    """Positioning for emotional effects."""
    AROUND_CHARACTER = "around_character"  # Surrounding the character
    BACKGROUND = "background"              # In the background
    CORNER = "corner"                      # Corner of frame
    OVERLAY = "overlay"                    # Full frame overlay
    FACE = "face"                          # On character's face


class EmotionalEffectAnimation(str, Enum):
    """Animation types for emotional effects."""
    FLOAT = "float"        # Gentle floating
    BURST = "burst"        # Quick burst appearance
    PULSE = "pulse"        # Pulsing/throbbing
    DRIFT = "drift"        # Drifting movement
    STATIC = "static"      # No animation


class SFXTiming(str, Enum):
    """When the SFX should appear."""
    ON_ENTER = "on_enter"          # When panel first appears
    WITH_DIALOGUE = "with_dialogue"  # Synced with dialogue
    ON_EXIT = "on_exit"            # When panel transitions out
    CONTINUOUS = "continuous"      # Throughout panel duration


# ============================================================================
# SFX Models
# ============================================================================

class ImpactText(BaseModel):
    """
    Impact text effect (onomatopoeia) like "CRASH!", "THUMP!", "WHOOSH!".

    Used for action sounds, emotional impacts, and dramatic moments.
    """
    text: str = Field(
        ...,
        description="The impact text to display (e.g., 'CRASH!', 'THUMP!', 'GASP!')",
        min_length=1,
        max_length=20
    )
    style: ImpactTextStyle = Field(
        default=ImpactTextStyle.BOLD,
        description="Visual style of the text"
    )
    position: Tuple[float, float] = Field(
        default=(0.5, 0.5),
        description="Position as (x_percent, y_percent) from 0.0-1.0"
    )
    size: ImpactTextSize = Field(
        default=ImpactTextSize.MEDIUM,
        description="Size of the text"
    )
    color: str = Field(
        default="#FFFFFF",
        description="Text color as hex code"
    )
    outline_color: str = Field(
        default="#000000",
        description="Outline/stroke color as hex code"
    )
    rotation: int = Field(
        default=0,
        description="Rotation in degrees (-45 to 45 typical)",
        ge=-180,
        le=180
    )
    animation: ImpactTextAnimation = Field(
        default=ImpactTextAnimation.POP,
        description="Entry animation type"
    )
    timing: SFXTiming = Field(
        default=SFXTiming.ON_ENTER,
        description="When to show this effect"
    )
    duration_ms: int = Field(
        default=500,
        description="How long to display (milliseconds)",
        ge=100,
        le=3000
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "CRASH!",
                "style": "explosive",
                "position": [0.7, 0.3],
                "size": "large",
                "color": "#FF0000",
                "outline_color": "#000000",
                "rotation": -15,
                "animation": "pop",
                "timing": "on_enter",
                "duration_ms": 500
            }
        }
    )


class MotionEffect(BaseModel):
    """
    Motion effect like speed lines, blur, or impact bursts.

    Used for action scenes, movement, and dynamic moments.
    """
    type: MotionEffectType = Field(
        ...,
        description="Type of motion effect"
    )
    direction: MotionDirection = Field(
        default=MotionDirection.CENTER,
        description="Direction of the motion effect"
    )
    intensity: EffectIntensity = Field(
        default=EffectIntensity.MEDIUM,
        description="How prominent the effect is"
    )
    duration_ms: int = Field(
        default=300,
        description="How long the effect lasts (milliseconds)",
        ge=100,
        le=2000
    )
    timing: SFXTiming = Field(
        default=SFXTiming.ON_ENTER,
        description="When to show this effect"
    )
    color: Optional[str] = Field(
        default=None,
        description="Optional color override (hex code)"
    )
    opacity: float = Field(
        default=0.7,
        description="Opacity of the effect (0.0-1.0)",
        ge=0.0,
        le=1.0
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "speed_lines",
                "direction": "left",
                "intensity": "intense",
                "duration_ms": 400,
                "timing": "on_enter",
                "opacity": 0.8
            }
        }
    )


class ScreenEffect(BaseModel):
    """
    Screen-wide effect like flash, shake, or vignette.

    Used for dramatic moments, impacts, and atmosphere.
    """
    type: ScreenEffectType = Field(
        ...,
        description="Type of screen effect"
    )
    intensity: EffectIntensity = Field(
        default=EffectIntensity.MEDIUM,
        description="How strong the effect is"
    )
    duration_ms: int = Field(
        default=200,
        description="How long the effect lasts (milliseconds)",
        ge=50,
        le=2000
    )
    timing: SFXTiming = Field(
        default=SFXTiming.ON_ENTER,
        description="When to show this effect"
    )
    color: Optional[str] = Field(
        default=None,
        description="Color for color_shift effect (hex code)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "flash",
                "intensity": "intense",
                "duration_ms": 150,
                "timing": "on_enter"
            }
        }
    )


class EmotionalEffect(BaseModel):
    """
    Emotional visual effect like sparkles, hearts, or dark aura.

    Used to convey character emotions and mood.
    """
    type: EmotionalEffectType = Field(
        ...,
        description="Type of emotional effect"
    )
    position: EmotionalEffectPosition = Field(
        default=EmotionalEffectPosition.AROUND_CHARACTER,
        description="Where to place the effect"
    )
    animation: EmotionalEffectAnimation = Field(
        default=EmotionalEffectAnimation.FLOAT,
        description="How the effect animates"
    )
    intensity: EffectIntensity = Field(
        default=EffectIntensity.MEDIUM,
        description="How prominent the effect is"
    )
    timing: SFXTiming = Field(
        default=SFXTiming.CONTINUOUS,
        description="When to show this effect"
    )
    duration_ms: int = Field(
        default=1000,
        description="How long the effect lasts (milliseconds)",
        ge=200,
        le=5000
    )
    color: Optional[str] = Field(
        default=None,
        description="Optional color override (hex code)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "sparkles",
                "position": "around_character",
                "animation": "float",
                "intensity": "medium",
                "timing": "continuous",
                "duration_ms": 2000
            }
        }
    )


# ============================================================================
# Union Type for All SFX
# ============================================================================

# Type alias for any SFX effect
SFXEffect = Union[ImpactText, MotionEffect, ScreenEffect, EmotionalEffect]


class SFXBundle(BaseModel):
    """
    A bundle of SFX effects for a single panel.

    Allows combining multiple effects for complex visual moments.
    """
    panel_number: int = Field(
        ...,
        description="Panel number this bundle applies to",
        ge=1
    )
    impact_texts: List[ImpactText] = Field(
        default_factory=list,
        description="Impact text effects for this panel"
    )
    motion_effects: List[MotionEffect] = Field(
        default_factory=list,
        description="Motion effects for this panel"
    )
    screen_effects: List[ScreenEffect] = Field(
        default_factory=list,
        description="Screen effects for this panel"
    )
    emotional_effects: List[EmotionalEffect] = Field(
        default_factory=list,
        description="Emotional effects for this panel"
    )

    @property
    def total_effects(self) -> int:
        """Total number of effects in this bundle."""
        return (
            len(self.impact_texts) +
            len(self.motion_effects) +
            len(self.screen_effects) +
            len(self.emotional_effects)
        )

    @property
    def has_effects(self) -> bool:
        """Check if bundle has any effects."""
        return self.total_effects > 0

    def get_all_effects(self) -> List[SFXEffect]:
        """Get all effects as a flat list."""
        effects: List[SFXEffect] = []
        effects.extend(self.impact_texts)
        effects.extend(self.motion_effects)
        effects.extend(self.screen_effects)
        effects.extend(self.emotional_effects)
        return effects

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "panel_number": 5,
                "impact_texts": [
                    {"text": "SLAM!", "style": "bold", "position": [0.8, 0.2]}
                ],
                "motion_effects": [
                    {"type": "impact_burst", "direction": "radial", "intensity": "intense"}
                ],
                "screen_effects": [
                    {"type": "shake", "intensity": "medium", "duration_ms": 200}
                ],
                "emotional_effects": []
            }
        }
    )


# ============================================================================
# SFX Trigger Mapping (for auto-suggestions)
# ============================================================================

# Maps emotions/actions to suggested SFX effects
SFX_TRIGGERS = {
    # Emotions
    "surprise": [
        {"type": "impact_text", "text": "!", "style": "bold"},
        {"type": "screen", "effect": "flash", "intensity": "subtle"}
    ],
    "shock": [
        {"type": "impact_text", "text": "!!", "style": "explosive"},
        {"type": "emotional", "effect": "shock_lines"},
        {"type": "screen", "effect": "shake", "intensity": "medium"}
    ],
    "anger": [
        {"type": "motion", "effect": "speed_lines", "direction": "radial"},
        {"type": "emotional", "effect": "dark_aura"},
        {"type": "emotional", "effect": "anger_vein"}
    ],
    "love": [
        {"type": "emotional", "effect": "sparkles"},
        {"type": "emotional", "effect": "hearts"},
        {"type": "emotional", "effect": "blush"}
    ],
    "romantic": [
        {"type": "emotional", "effect": "flowers"},
        {"type": "emotional", "effect": "sparkles"},
        {"type": "screen", "effect": "vignette", "intensity": "subtle"}
    ],
    "fear": [
        {"type": "emotional", "effect": "sweat_drop"},
        {"type": "screen", "effect": "shake", "intensity": "subtle"},
        {"type": "screen", "effect": "darken"}
    ],
    "sad": [
        {"type": "emotional", "effect": "tears"},
        {"type": "screen", "effect": "vignette"},
        {"type": "screen", "effect": "color_shift", "color": "#4466AA"}
    ],
    "happy": [
        {"type": "emotional", "effect": "sparkles"},
        {"type": "emotional", "effect": "glow"}
    ],
    "nervous": [
        {"type": "emotional", "effect": "sweat_drop"},
        {"type": "motion", "effect": "speed_lines", "intensity": "subtle"}
    ],

    # Actions
    "impact": [
        {"type": "impact_text", "text": "CRASH!", "style": "explosive"},
        {"type": "motion", "effect": "impact_burst"},
        {"type": "screen", "effect": "shake", "intensity": "intense"},
        {"type": "screen", "effect": "flash"}
    ],
    "punch": [
        {"type": "impact_text", "text": "POW!", "style": "bold"},
        {"type": "motion", "effect": "speed_lines"},
        {"type": "screen", "effect": "shake"}
    ],
    "run": [
        {"type": "motion", "effect": "speed_lines", "direction": "left"},
        {"type": "motion", "effect": "blur", "intensity": "subtle"}
    ],
    "fall": [
        {"type": "impact_text", "text": "THUD!", "style": "bold"},
        {"type": "motion", "effect": "speed_lines", "direction": "down"},
        {"type": "screen", "effect": "shake"}
    ],
    "realization": [
        {"type": "impact_text", "text": "!", "style": "bold"},
        {"type": "screen", "effect": "flash", "intensity": "subtle"},
        {"type": "motion", "effect": "zoom_lines"}
    ],
    "comedy": [
        {"type": "emotional", "effect": "sweat_drop"},
        {"type": "impact_text", "text": "...", "style": "soft"}
    ],
    "dramatic_entrance": [
        {"type": "motion", "effect": "wind_lines"},
        {"type": "emotional", "effect": "glow"},
        {"type": "screen", "effect": "vignette"}
    ]
}


def get_suggested_sfx(emotion_or_action: str) -> List[dict]:
    """
    Get suggested SFX for an emotion or action.

    Args:
        emotion_or_action: Key like "anger", "impact", "love"

    Returns:
        List of suggested effect configurations
    """
    return SFX_TRIGGERS.get(emotion_or_action.lower(), [])
