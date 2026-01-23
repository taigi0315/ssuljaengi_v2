"""
Modular Style System Models for Webtoon Enhancement.

This module provides a composable style system that separates:
- BaseStyle: The constant "medium" that defines the core art style
- SceneMood: Per-scene modifiers (color_temperature, saturation, lighting_mood)

This allows the overall art style to remain consistent while individual
scenes can have mood-appropriate visual adjustments.

v2.0.0: Initial implementation
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Enums for Style Configuration
# ============================================================================

class ColorTemperature(str, Enum):
    """Color temperature presets for scene mood."""
    COOL = "cool"              # Blue-ish, cold, distant
    NEUTRAL = "neutral"        # Balanced
    WARM = "warm"              # Golden, intimate, comfortable
    VERY_WARM = "very_warm"    # Sunset, romantic, nostalgic
    VERY_COOL = "very_cool"    # Icy, tense, melancholic


class SaturationLevel(str, Enum):
    """Saturation levels for scene mood."""
    DESATURATED = "desaturated"    # Muted, serious, flashback
    LOW = "low"                     # Subtle, contemplative
    NORMAL = "normal"               # Standard saturation
    HIGH = "high"                   # Vibrant, energetic
    VIVID = "vivid"                 # Intense, peak emotion


class LightingMood(str, Enum):
    """Lighting mood presets."""
    BRIGHT = "bright"              # Optimistic, cheerful
    SOFT = "soft"                  # Gentle, romantic
    DRAMATIC = "dramatic"          # High contrast, tension
    MOODY = "moody"                # Dark, emotional
    ETHEREAL = "ethereal"          # Dreamy, magical
    HARSH = "harsh"                # Stark, confrontational
    DIM = "dim"                    # Quiet, intimate
    GOLDEN_HOUR = "golden_hour"    # Romantic, nostalgic


class DetailLevel(str, Enum):
    """Level of visual detail in the scene."""
    MINIMAL = "minimal"        # Backgrounds simplified/blurred
    STANDARD = "standard"      # Normal level of detail
    HIGH = "high"              # Rich environmental detail
    FOCUS_CHARACTER = "focus_character"  # Detailed characters, simple background


class ExpressionStyle(str, Enum):
    """Character expression rendering style."""
    SUBTLE = "subtle"          # Micro-expressions, restrained
    NORMAL = "normal"          # Standard manga/manhwa expressions
    EXAGGERATED = "exaggerated"  # Over-the-top comedy expressions
    DRAMATIC = "dramatic"      # Intense emotional emphasis


class SpecialEffect(str, Enum):
    """Special visual effects for mood."""
    NONE = "none"
    SPARKLES = "sparkles"          # Romance, beauty
    BLOOM = "bloom"                # Dreamy, ethereal
    VIGNETTE = "vignette"          # Focus, dramatic
    PARTICLES = "particles"        # Magic, emotion
    RAIN = "rain"                  # Melancholy, tension
    LENS_FLARE = "lens_flare"      # Cinematic, bright
    SOFT_FOCUS = "soft_focus"      # Romantic, memory
    GRAIN = "grain"                # Nostalgic, flashback


class RenderingQuality(str, Enum):
    """Overall rendering quality level."""
    SKETCH = "sketch"          # Rough, artistic
    STANDARD = "standard"      # Normal webtoon quality
    HIGH = "high"              # Detailed rendering
    ULTRA = "ultra"            # Maximum detail


class LineQuality(str, Enum):
    """Line art quality and style."""
    THIN = "thin"              # Delicate, elegant
    MEDIUM = "medium"          # Standard
    THICK = "thick"            # Bold, impactful
    VARIED = "varied"          # Expressive variation


# ============================================================================
# Base Style Model (Constant throughout webtoon)
# ============================================================================

class BaseStyle(BaseModel):
    """
    The foundational art style that remains constant throughout the webtoon.

    This defines the "medium" - the core visual language including:
    - Art medium (digital cel-shading, painterly, etc.)
    - Base color palette tendencies
    - Line art quality
    - Overall rendering approach

    Think of this as selecting the "artist" or "studio style".
    """
    name: str = Field(
        ...,
        description="Name/identifier for this base style",
        min_length=1,
        max_length=100
    )

    # Core rendering approach
    medium_description: str = Field(
        ...,
        description="Description of the art medium (e.g., 'digital cel-shading, polished webtoon style')"
    )

    # Color palette base
    color_palette_base: str = Field(
        ...,
        description="Base color palette description (e.g., 'pastel warmth, creamy neutrals')"
    )

    # Line and rendering quality
    line_quality: LineQuality = Field(
        default=LineQuality.MEDIUM,
        description="Default line art quality"
    )

    rendering_quality: RenderingQuality = Field(
        default=RenderingQuality.HIGH,
        description="Default rendering quality level"
    )

    # Additional style descriptors
    style_keywords: List[str] = Field(
        default_factory=list,
        description="Additional style keywords (e.g., ['manhwa', 'fantasy', 'romantic'])"
    )

    # Reference to existing style name (for backward compatibility)
    legacy_style_key: Optional[str] = Field(
        default=None,
        description="Key in VISUAL_STYLE_PROMPTS for legacy compatibility"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Soft Romantic",
                "medium_description": "ultra-soft cel-shading, gentle gradient blending, polished webtoon art",
                "color_palette_base": "pastel warmth, creamy beiges, light pinks, soft peaches",
                "line_quality": "thin",
                "rendering_quality": "high",
                "style_keywords": ["romantic", "ethereal", "manhwa"],
                "legacy_style_key": "SOFT_ROMANTIC_WEBTOON"
            }
        }
    )


# ============================================================================
# Scene Mood Model (Varies per scene)
# ============================================================================

class SceneMood(BaseModel):
    """
    Per-scene visual mood modifiers that layer on top of the BaseStyle.

    This allows individual scenes to have mood-appropriate adjustments
    while maintaining the overall art style consistency.

    Think of this as "color grading" and "lighting setup" per scene.
    """
    name: str = Field(
        default="neutral",
        description="Name/identifier for this mood preset"
    )

    # Color adjustments
    color_temperature: ColorTemperature = Field(
        default=ColorTemperature.NEUTRAL,
        description="Color temperature shift for the scene"
    )

    saturation: SaturationLevel = Field(
        default=SaturationLevel.NORMAL,
        description="Saturation level for the scene"
    )

    # Lighting
    lighting_mood: LightingMood = Field(
        default=LightingMood.SOFT,
        description="Lighting mood for the scene"
    )

    # Detail and focus
    detail_level: DetailLevel = Field(
        default=DetailLevel.STANDARD,
        description="Level of visual detail"
    )

    # Character expression style
    expression_style: ExpressionStyle = Field(
        default=ExpressionStyle.NORMAL,
        description="How character expressions are rendered"
    )

    # Special effects
    special_effects: List[SpecialEffect] = Field(
        default_factory=list,
        description="Special visual effects to apply"
    )

    # Emotional intensity (1-10)
    intensity: int = Field(
        default=5,
        description="Emotional intensity of the scene (1-10)",
        ge=1,
        le=10
    )

    # Optional color accent (hex)
    accent_color: Optional[str] = Field(
        default=None,
        description="Optional accent color for the scene (hex code)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "romantic_tension",
                "color_temperature": "warm",
                "saturation": "normal",
                "lighting_mood": "soft",
                "detail_level": "focus_character",
                "expression_style": "subtle",
                "special_effects": ["sparkles", "soft_focus"],
                "intensity": 7,
                "accent_color": "#FFB6C1"
            }
        }
    )

    def to_prompt_modifiers(self) -> str:
        """
        Convert mood settings to prompt modifier text.

        Returns:
            String of visual modifiers for the image prompt
        """
        modifiers = []

        # Color temperature
        temp_map = {
            ColorTemperature.VERY_COOL: "cool blue color grading, icy atmosphere",
            ColorTemperature.COOL: "cool undertones, slight blue tint",
            ColorTemperature.NEUTRAL: "balanced color temperature",
            ColorTemperature.WARM: "warm golden tones, amber highlights",
            ColorTemperature.VERY_WARM: "sunset warmth, golden hour lighting",
        }
        modifiers.append(temp_map.get(self.color_temperature, ""))

        # Saturation
        sat_map = {
            SaturationLevel.DESATURATED: "desaturated colors, muted palette",
            SaturationLevel.LOW: "subtle muted colors",
            SaturationLevel.NORMAL: "",
            SaturationLevel.HIGH: "vibrant saturated colors",
            SaturationLevel.VIVID: "vivid intense colors, bold palette",
        }
        if sat_text := sat_map.get(self.saturation, ""):
            modifiers.append(sat_text)

        # Lighting
        light_map = {
            LightingMood.BRIGHT: "bright cheerful lighting",
            LightingMood.SOFT: "soft diffused lighting",
            LightingMood.DRAMATIC: "dramatic lighting, strong shadows",
            LightingMood.MOODY: "moody low-key lighting, deep shadows",
            LightingMood.ETHEREAL: "ethereal glowing light, dreamy atmosphere",
            LightingMood.HARSH: "harsh stark lighting, high contrast",
            LightingMood.DIM: "dim intimate lighting",
            LightingMood.GOLDEN_HOUR: "golden hour sunlight, warm rim lighting",
        }
        modifiers.append(light_map.get(self.lighting_mood, ""))

        # Detail level
        detail_map = {
            DetailLevel.MINIMAL: "simplified background, focus on characters",
            DetailLevel.STANDARD: "",
            DetailLevel.HIGH: "highly detailed environment",
            DetailLevel.FOCUS_CHARACTER: "detailed characters, soft background blur",
        }
        if detail_text := detail_map.get(self.detail_level, ""):
            modifiers.append(detail_text)

        # Expression style
        expr_map = {
            ExpressionStyle.SUBTLE: "subtle micro-expressions",
            ExpressionStyle.NORMAL: "",
            ExpressionStyle.EXAGGERATED: "exaggerated manga expressions",
            ExpressionStyle.DRAMATIC: "intense emotional expressions",
        }
        if expr_text := expr_map.get(self.expression_style, ""):
            modifiers.append(expr_text)

        # Special effects
        effect_map = {
            SpecialEffect.SPARKLES: "sparkle effects",
            SpecialEffect.BLOOM: "soft bloom glow",
            SpecialEffect.VIGNETTE: "subtle vignette",
            SpecialEffect.PARTICLES: "floating particles",
            SpecialEffect.RAIN: "rain atmosphere",
            SpecialEffect.LENS_FLARE: "lens flare",
            SpecialEffect.SOFT_FOCUS: "soft focus dreamy",
            SpecialEffect.GRAIN: "subtle film grain",
        }
        for effect in self.special_effects:
            if effect != SpecialEffect.NONE and effect in effect_map:
                modifiers.append(effect_map[effect])

        # Intensity affects emphasis
        if self.intensity >= 8:
            modifiers.append("heightened emotional atmosphere")
        elif self.intensity <= 3:
            modifiers.append("calm subdued atmosphere")

        # Filter empty strings and join
        return ", ".join(filter(None, modifiers))


# ============================================================================
# Mood Presets (Task 2.1.4)
# ============================================================================

MOOD_PRESETS: Dict[str, SceneMood] = {
    "neutral": SceneMood(
        name="neutral",
        color_temperature=ColorTemperature.NEUTRAL,
        saturation=SaturationLevel.NORMAL,
        lighting_mood=LightingMood.SOFT,
        detail_level=DetailLevel.STANDARD,
        expression_style=ExpressionStyle.NORMAL,
        special_effects=[],
        intensity=5
    ),

    "comedy": SceneMood(
        name="comedy",
        color_temperature=ColorTemperature.WARM,
        saturation=SaturationLevel.HIGH,
        lighting_mood=LightingMood.BRIGHT,
        detail_level=DetailLevel.MINIMAL,
        expression_style=ExpressionStyle.EXAGGERATED,
        special_effects=[],
        intensity=6
    ),

    "romantic_tension": SceneMood(
        name="romantic_tension",
        color_temperature=ColorTemperature.WARM,
        saturation=SaturationLevel.NORMAL,
        lighting_mood=LightingMood.SOFT,
        detail_level=DetailLevel.FOCUS_CHARACTER,
        expression_style=ExpressionStyle.SUBTLE,
        special_effects=[SpecialEffect.SPARKLES, SpecialEffect.SOFT_FOCUS],
        intensity=7,
        accent_color="#FFB6C1"  # Light pink
    ),

    "romantic_confession": SceneMood(
        name="romantic_confession",
        color_temperature=ColorTemperature.VERY_WARM,
        saturation=SaturationLevel.NORMAL,
        lighting_mood=LightingMood.GOLDEN_HOUR,
        detail_level=DetailLevel.FOCUS_CHARACTER,
        expression_style=ExpressionStyle.DRAMATIC,
        special_effects=[SpecialEffect.SPARKLES, SpecialEffect.BLOOM, SpecialEffect.PARTICLES],
        intensity=9,
        accent_color="#FFD700"  # Gold
    ),

    "serious_conflict": SceneMood(
        name="serious_conflict",
        color_temperature=ColorTemperature.COOL,
        saturation=SaturationLevel.LOW,
        lighting_mood=LightingMood.DRAMATIC,
        detail_level=DetailLevel.HIGH,
        expression_style=ExpressionStyle.DRAMATIC,
        special_effects=[SpecialEffect.VIGNETTE],
        intensity=8
    ),

    "sad_emotional": SceneMood(
        name="sad_emotional",
        color_temperature=ColorTemperature.COOL,
        saturation=SaturationLevel.DESATURATED,
        lighting_mood=LightingMood.MOODY,
        detail_level=DetailLevel.FOCUS_CHARACTER,
        expression_style=ExpressionStyle.DRAMATIC,
        special_effects=[SpecialEffect.VIGNETTE, SpecialEffect.RAIN],
        intensity=8,
        accent_color="#4169E1"  # Royal blue
    ),

    "flashback": SceneMood(
        name="flashback",
        color_temperature=ColorTemperature.WARM,
        saturation=SaturationLevel.DESATURATED,
        lighting_mood=LightingMood.SOFT,
        detail_level=DetailLevel.MINIMAL,
        expression_style=ExpressionStyle.SUBTLE,
        special_effects=[SpecialEffect.SOFT_FOCUS, SpecialEffect.GRAIN, SpecialEffect.VIGNETTE],
        intensity=5
    ),

    "climax": SceneMood(
        name="climax",
        color_temperature=ColorTemperature.NEUTRAL,
        saturation=SaturationLevel.VIVID,
        lighting_mood=LightingMood.DRAMATIC,
        detail_level=DetailLevel.HIGH,
        expression_style=ExpressionStyle.DRAMATIC,
        special_effects=[SpecialEffect.BLOOM, SpecialEffect.LENS_FLARE],
        intensity=10
    ),

    "peaceful": SceneMood(
        name="peaceful",
        color_temperature=ColorTemperature.WARM,
        saturation=SaturationLevel.NORMAL,
        lighting_mood=LightingMood.SOFT,
        detail_level=DetailLevel.HIGH,
        expression_style=ExpressionStyle.SUBTLE,
        special_effects=[SpecialEffect.BLOOM],
        intensity=3
    ),

    "mysterious": SceneMood(
        name="mysterious",
        color_temperature=ColorTemperature.VERY_COOL,
        saturation=SaturationLevel.LOW,
        lighting_mood=LightingMood.DIM,
        detail_level=DetailLevel.MINIMAL,
        expression_style=ExpressionStyle.SUBTLE,
        special_effects=[SpecialEffect.VIGNETTE, SpecialEffect.PARTICLES],
        intensity=6,
        accent_color="#483D8B"  # Dark slate blue
    ),

    "action": SceneMood(
        name="action",
        color_temperature=ColorTemperature.NEUTRAL,
        saturation=SaturationLevel.HIGH,
        lighting_mood=LightingMood.DRAMATIC,
        detail_level=DetailLevel.STANDARD,
        expression_style=ExpressionStyle.DRAMATIC,
        special_effects=[],
        intensity=8
    ),

    "tense": SceneMood(
        name="tense",
        color_temperature=ColorTemperature.COOL,
        saturation=SaturationLevel.LOW,
        lighting_mood=LightingMood.HARSH,
        detail_level=DetailLevel.FOCUS_CHARACTER,
        expression_style=ExpressionStyle.SUBTLE,
        special_effects=[SpecialEffect.VIGNETTE],
        intensity=7
    ),

    "dreamy": SceneMood(
        name="dreamy",
        color_temperature=ColorTemperature.WARM,
        saturation=SaturationLevel.LOW,
        lighting_mood=LightingMood.ETHEREAL,
        detail_level=DetailLevel.MINIMAL,
        expression_style=ExpressionStyle.SUBTLE,
        special_effects=[SpecialEffect.BLOOM, SpecialEffect.SOFT_FOCUS, SpecialEffect.SPARKLES],
        intensity=4
    ),
}


# ============================================================================
# Utility Functions
# ============================================================================

def get_mood_preset(name: str) -> SceneMood:
    """
    Get a mood preset by name.

    Args:
        name: Name of the mood preset

    Returns:
        SceneMood instance (returns neutral if name not found)
    """
    return MOOD_PRESETS.get(name.lower(), MOOD_PRESETS["neutral"])


def get_mood_for_intensity(intensity: int, context: str = "neutral") -> SceneMood:
    """
    Get an appropriate mood preset based on emotional intensity and context.

    Args:
        intensity: Emotional intensity (1-10)
        context: Scene context hint (e.g., "romantic", "conflict", "comedy")

    Returns:
        Appropriate SceneMood preset
    """
    context_lower = context.lower()

    # Map context + intensity to mood presets
    if "romantic" in context_lower or "love" in context_lower:
        if intensity >= 8:
            return MOOD_PRESETS["romantic_confession"]
        elif intensity >= 5:
            return MOOD_PRESETS["romantic_tension"]
        else:
            return MOOD_PRESETS["peaceful"]

    elif "conflict" in context_lower or "argument" in context_lower or "fight" in context_lower:
        if intensity >= 7:
            return MOOD_PRESETS["serious_conflict"]
        else:
            return MOOD_PRESETS["tense"]

    elif "sad" in context_lower or "cry" in context_lower or "emotional" in context_lower:
        return MOOD_PRESETS["sad_emotional"]

    elif "comedy" in context_lower or "funny" in context_lower or "humor" in context_lower:
        return MOOD_PRESETS["comedy"]

    elif "flashback" in context_lower or "memory" in context_lower or "past" in context_lower:
        return MOOD_PRESETS["flashback"]

    elif "action" in context_lower or "chase" in context_lower or "battle" in context_lower:
        return MOOD_PRESETS["action"]

    elif "mystery" in context_lower or "suspense" in context_lower or "secret" in context_lower:
        return MOOD_PRESETS["mysterious"]

    elif "dream" in context_lower or "fantasy" in context_lower:
        return MOOD_PRESETS["dreamy"]

    elif "climax" in context_lower or "peak" in context_lower:
        return MOOD_PRESETS["climax"]

    # Default based on intensity alone
    if intensity >= 9:
        return MOOD_PRESETS["climax"]
    elif intensity >= 7:
        return MOOD_PRESETS["serious_conflict"]
    elif intensity <= 3:
        return MOOD_PRESETS["peaceful"]
    else:
        return MOOD_PRESETS["neutral"]


def list_mood_presets() -> List[str]:
    """Return list of available mood preset names."""
    return list(MOOD_PRESETS.keys())


# ============================================================================
# Composed Style Model
# ============================================================================

class ComposedStyle(BaseModel):
    """
    A fully composed style combining BaseStyle and SceneMood.

    This is the final style object used for image generation,
    containing both the constant base style and the per-scene mood.
    """
    base_style: BaseStyle = Field(
        ...,
        description="The constant base art style"
    )

    scene_mood: SceneMood = Field(
        default_factory=lambda: MOOD_PRESETS["neutral"],
        description="The per-scene mood modifiers"
    )

    def to_prompt(self) -> str:
        """
        Generate the full style prompt combining base style and mood.

        Returns:
            Complete style prompt string for image generation
        """
        parts = []

        # Base style
        parts.append(f"[STYLE: {self.base_style.name}]")
        parts.append(self.base_style.medium_description)
        parts.append(f"color palette: {self.base_style.color_palette_base}")

        if self.base_style.style_keywords:
            parts.append(f"style keywords: {', '.join(self.base_style.style_keywords)}")

        # Quality settings
        parts.append(f"line quality: {self.base_style.line_quality.value}")
        parts.append(f"rendering: {self.base_style.rendering_quality.value} quality")

        # Scene mood modifiers
        mood_modifiers = self.scene_mood.to_prompt_modifiers()
        if mood_modifiers:
            parts.append(f"[MOOD: {self.scene_mood.name}] {mood_modifiers}")

        return ", ".join(filter(None, parts))

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "base_style": {
                    "name": "Soft Romantic",
                    "medium_description": "ultra-soft cel-shading, gentle gradient blending",
                    "color_palette_base": "pastel warmth, creamy neutrals",
                    "line_quality": "thin",
                    "rendering_quality": "high"
                },
                "scene_mood": {
                    "name": "romantic_tension",
                    "color_temperature": "warm",
                    "lighting_mood": "soft",
                    "intensity": 7
                }
            }
        }
    )


# ============================================================================
# Predefined Base Styles (matching existing VISUAL_STYLE_PROMPTS)
# ============================================================================

BASE_STYLES: Dict[str, BaseStyle] = {
    "soft_romantic": BaseStyle(
        name="Soft Romantic",
        medium_description="ultra-soft cel-shading, gentle gradient blending, luminous digital painting, polished contemporary webtoon art, clean fluid lineart",
        color_palette_base="pastel warmth, creamy beiges, warm neutrals, light pinks, soft peaches, gentle sky blues, subtle lavender",
        line_quality=LineQuality.THIN,
        rendering_quality=RenderingQuality.HIGH,
        style_keywords=["romantic", "ethereal", "manhwa", "soft"],
        legacy_style_key="SOFT_ROMANTIC_WEBTOON"
    ),

    "vibrant_fantasy": BaseStyle(
        name="Vibrant Fantasy",
        medium_description="clean sharp cel-shading, smooth gradient transitions, crisp digital comic illustration, polished fantasy manhwa style",
        color_palette_base="soft pastel palette with ethereal accents, light blues and purples, gentle pinks, warm golden highlights",
        line_quality=LineQuality.MEDIUM,
        rendering_quality=RenderingQuality.HIGH,
        style_keywords=["fantasy", "magical", "manhwa"],
        legacy_style_key="VIBRANT_FANTASY_WEBTOON"
    ),

    "dramatic_historical": BaseStyle(
        name="Dramatic Historical",
        medium_description="rich deep cel-shading, heavy gradient work, dramatic digital painting, elegant traditional-meets-digital style",
        color_palette_base="muted elegant colors, rich deep crimsons, indigo blues, antique golds, warm earth tones",
        line_quality=LineQuality.MEDIUM,
        rendering_quality=RenderingQuality.HIGH,
        style_keywords=["historical", "dramatic", "elegant", "manhwa"],
        legacy_style_key="DRAMATIC_HISTORICAL_WEBTOON"
    ),

    "bright_youthful": BaseStyle(
        name="Bright Youthful",
        medium_description="smooth gentle cel-shading, clean digital comic style, contemporary school webtoon rendering, approachable friendly art",
        color_palette_base="soft vibrant pastels, gentle sky blues, warm autumn yellows, light pinks, crisp whites",
        line_quality=LineQuality.MEDIUM,
        rendering_quality=RenderingQuality.STANDARD,
        style_keywords=["school", "youthful", "cheerful", "webtoon"],
        legacy_style_key="BRIGHT_YOUTHFUL_WEBTOON"
    ),

    "clean_modern": BaseStyle(
        name="Clean Modern",
        medium_description="crisp clean cel-shading, smooth professional gradient work, polished contemporary digital comic style",
        color_palette_base="modern color palette, warm neutrals, soft grays, desaturated sophisticated hues",
        line_quality=LineQuality.MEDIUM,
        rendering_quality=RenderingQuality.HIGH,
        style_keywords=["modern", "professional", "clean", "webtoon"],
        legacy_style_key="CLEAN_MODERN_WEBTOON"
    ),

    "emotive_luxury": BaseStyle(
        name="Emotive Luxury",
        medium_description="polished digital webtoon illustration, ultra-clean lineart, delicate expressive facial detailing, ornamental costume design",
        color_palette_base="soft pastel-dominant with jewel-tone accents, pink, lavender, rose, cool whites and blues",
        line_quality=LineQuality.THIN,
        rendering_quality=RenderingQuality.ULTRA,
        style_keywords=["luxury", "emotional", "romance", "fantasy", "manhwa"],
        legacy_style_key="EMOTIVE_LUXURY_WEBTOON"
    ),

    "operation_true_love": BaseStyle(
        name="Operation True Love",
        medium_description="high-end Korean webtoon/manhwa illustration, semi-realistic anime aesthetic, elegant character anatomy, cinematic romance-drama composition",
        color_palette_base="muted warm-neutral palette, earth tones, beige, caramel, charcoal, muted rose accents",
        line_quality=LineQuality.THIN,
        rendering_quality=RenderingQuality.ULTRA,
        style_keywords=["cinematic", "mature", "romance", "manhwa", "realistic"],
        legacy_style_key="OPERATION_TRUE_LOVE"
    ),

    "noir_romance": BaseStyle(
        name="Noir Romance",
        medium_description="premium digital manhwa illustration, semi-realistic anime proportions, sophisticated character design, mature romance-fantasy aesthetic",
        color_palette_base="desaturated earthy base with dramatic colored lighting, deep navy, slate gray, olive, burgundy",
        line_quality=LineQuality.THIN,
        rendering_quality=RenderingQuality.HIGH,
        style_keywords=["noir", "dramatic", "mature", "romance", "manhwa"],
        legacy_style_key="NOIR_ROMANCE_MANHWA"
    ),
}


def get_base_style(name: str) -> Optional[BaseStyle]:
    """
    Get a base style by name.

    Args:
        name: Name of the base style (case-insensitive, underscores/spaces/hyphens normalized)

    Returns:
        BaseStyle instance or None if not found
    """
    # Normalize the name
    normalized = name.lower().replace(" ", "_").replace("-", "_")
    return BASE_STYLES.get(normalized)


def list_base_styles() -> List[str]:
    """Return list of available base style names."""
    return list(BASE_STYLES.keys())
