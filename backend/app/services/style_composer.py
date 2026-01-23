"""
Style Composer Service for Webtoon Enhancement.

This module provides functionality to compose visual styles by combining:
- BaseStyle (constant art style throughout webtoon)
- SceneMood (per-scene mood modifiers)

It also provides backward compatibility with the existing VISUAL_STYLE_PROMPTS system.

v2.0.0: Initial implementation
"""

import logging
from typing import Optional, List, Tuple

from app.models.style import (
    BaseStyle,
    SceneMood,
    ComposedStyle,
    MOOD_PRESETS,
    BASE_STYLES,
    get_base_style,
    get_mood_preset,
    get_mood_for_intensity,
)
from app.prompt.image_style import VISUAL_STYLE_PROMPTS


logger = logging.getLogger(__name__)


# ============================================================================
# Style Composition Functions (Task 2.2.2)
# ============================================================================

def compose_style(
    base_style: BaseStyle,
    scene_mood: Optional[SceneMood] = None
) -> str:
    """
    Compose a complete style prompt from BaseStyle and SceneMood.

    This is the primary style composition function that combines the constant
    base art style with per-scene mood modifiers to generate a complete
    style prompt string for image generation.

    Args:
        base_style: The base art style (constant throughout webtoon)
        scene_mood: Optional per-scene mood modifiers

    Returns:
        Complete style prompt string for image generation
    """
    if scene_mood is None:
        scene_mood = MOOD_PRESETS["neutral"]

    composed = ComposedStyle(base_style=base_style, scene_mood=scene_mood)
    return composed.to_prompt()


def compose_style_with_legacy(
    legacy_style_key: str,
    scene_mood: Optional[SceneMood] = None
) -> str:
    """
    Compose style using legacy VISUAL_STYLE_PROMPTS key with mood modifiers.

    This provides backward compatibility while adding mood variation support.
    It appends mood modifiers to the existing legacy style prompt.

    Args:
        legacy_style_key: Key from VISUAL_STYLE_PROMPTS (e.g., "SOFT_ROMANTIC_WEBTOON")
        scene_mood: Optional per-scene mood modifiers

    Returns:
        Complete style prompt string
    """
    # Get the legacy style prompt
    legacy_prompt = VISUAL_STYLE_PROMPTS.get(legacy_style_key, "")

    if not legacy_prompt:
        logger.warning(f"Legacy style key not found: {legacy_style_key}")
        return ""

    # If no mood specified, return legacy prompt as-is
    if scene_mood is None:
        return legacy_prompt.strip()

    # Append mood modifiers to legacy prompt
    mood_modifiers = scene_mood.to_prompt_modifiers()

    if mood_modifiers:
        return f"{legacy_prompt.strip()}\n\n[SCENE MOOD: {scene_mood.name}]\n{mood_modifiers}"
    else:
        return legacy_prompt.strip()


def get_style_for_scene(
    base_style_name: str,
    emotional_intensity: int = 5,
    scene_context: str = "neutral"
) -> str:
    """
    Get the appropriate style prompt for a scene based on emotional content.

    This is a convenience function that:
    1. Looks up the base style
    2. Determines appropriate mood from intensity and context
    3. Composes and returns the complete style prompt

    Args:
        base_style_name: Name of the base style (e.g., "soft_romantic")
        emotional_intensity: Emotional intensity of the scene (1-10)
        scene_context: Context hint (e.g., "romantic", "conflict", "comedy")

    Returns:
        Complete style prompt string, or empty string if base style not found
    """
    # Get base style
    base_style = get_base_style(base_style_name)

    if base_style is None:
        logger.warning(f"Base style not found: {base_style_name}")
        return ""

    # Get appropriate mood
    scene_mood = get_mood_for_intensity(emotional_intensity, scene_context)

    # Compose and return
    return compose_style(base_style, scene_mood)


def get_legacy_style_with_mood(
    legacy_style_key: str,
    emotional_intensity: int = 5,
    scene_context: str = "neutral"
) -> str:
    """
    Get legacy style prompt enhanced with mood modifiers.

    This maintains backward compatibility with existing code while
    adding mood variation support based on emotional intensity.

    Args:
        legacy_style_key: Key from VISUAL_STYLE_PROMPTS
        emotional_intensity: Emotional intensity of the scene (1-10)
        scene_context: Context hint (e.g., "romantic", "conflict")

    Returns:
        Complete style prompt string
    """
    # Get appropriate mood
    scene_mood = get_mood_for_intensity(emotional_intensity, scene_context)

    # Compose with legacy style
    return compose_style_with_legacy(legacy_style_key, scene_mood)


# ============================================================================
# Style Lookup Functions
# ============================================================================

def resolve_style_key_to_base(legacy_style_key: str) -> Optional[BaseStyle]:
    """
    Resolve a legacy style key to its corresponding BaseStyle.

    Args:
        legacy_style_key: Key from VISUAL_STYLE_PROMPTS

    Returns:
        Corresponding BaseStyle or None if not found
    """
    # Find base style with matching legacy key
    for name, base_style in BASE_STYLES.items():
        if base_style.legacy_style_key == legacy_style_key:
            return base_style

    return None


def get_available_styles() -> List[Tuple[str, str, str]]:
    """
    Get list of all available styles with their identifiers.

    Returns:
        List of tuples: (base_style_name, display_name, legacy_key)
    """
    styles = []
    for name, base_style in BASE_STYLES.items():
        styles.append((
            name,
            base_style.name,
            base_style.legacy_style_key or ""
        ))
    return styles


def get_available_moods() -> List[Tuple[str, str, int]]:
    """
    Get list of all available mood presets.

    Returns:
        List of tuples: (mood_name, description, default_intensity)
    """
    moods = []
    for name, mood in MOOD_PRESETS.items():
        description = f"{mood.lighting_mood.value} lighting, {mood.color_temperature.value} tones"
        moods.append((name, description, mood.intensity))
    return moods


# ============================================================================
# Style Composition for Multi-Panel Pages
# ============================================================================

def compose_styles_for_panels(
    base_style_name: str,
    panels_data: List[dict]
) -> List[str]:
    """
    Compose style prompts for multiple panels with varying moods.

    This is useful for multi-panel generation where each panel may have
    different emotional intensity and context.

    Args:
        base_style_name: Name of the base style to use for all panels
        panels_data: List of dicts with keys: emotional_intensity, scene_context

    Returns:
        List of style prompt strings, one per panel
    """
    base_style = get_base_style(base_style_name)

    if base_style is None:
        logger.warning(f"Base style not found: {base_style_name}")
        return [""] * len(panels_data)

    style_prompts = []

    for panel_data in panels_data:
        intensity = panel_data.get("emotional_intensity", 5)
        context = panel_data.get("scene_context", "neutral")

        scene_mood = get_mood_for_intensity(intensity, context)
        prompt = compose_style(base_style, scene_mood)
        style_prompts.append(prompt)

    return style_prompts


def compose_unified_style_for_page(
    base_style_name: str,
    panels_data: List[dict]
) -> Tuple[str, str]:
    """
    Compose a unified style for a multi-panel page.

    For multi-panel generation where all panels are in one image,
    this determines the dominant mood across all panels and returns
    a single unified style prompt plus mood modifiers.

    Args:
        base_style_name: Name of the base style
        panels_data: List of dicts with keys: emotional_intensity, scene_context

    Returns:
        Tuple of (base_style_prompt, mood_modifiers_string)
    """
    base_style = get_base_style(base_style_name)

    if base_style is None:
        logger.warning(f"Base style not found: {base_style_name}")
        return ("", "")

    # Calculate dominant intensity (weighted average, biased toward peaks)
    intensities = [p.get("emotional_intensity", 5) for p in panels_data]

    if intensities:
        # Use max intensity as it determines the page's emotional peak
        dominant_intensity = max(intensities)
    else:
        dominant_intensity = 5

    # Determine dominant context
    contexts = [p.get("scene_context", "neutral") for p in panels_data]
    context_counts = {}
    for ctx in contexts:
        context_counts[ctx] = context_counts.get(ctx, 0) + 1

    dominant_context = max(context_counts, key=context_counts.get) if context_counts else "neutral"

    # Get mood for dominant emotional state
    scene_mood = get_mood_for_intensity(dominant_intensity, dominant_context)

    # Generate base style prompt (without mood)
    base_prompt = f"{base_style.medium_description}, color palette: {base_style.color_palette_base}"

    if base_style.style_keywords:
        base_prompt += f", {', '.join(base_style.style_keywords)}"

    base_prompt += f", {base_style.line_quality.value} lines, {base_style.rendering_quality.value} quality"

    # Generate mood modifiers
    mood_modifiers = scene_mood.to_prompt_modifiers()

    return (base_prompt, mood_modifiers)


# ============================================================================
# Global Instance
# ============================================================================

class StyleComposer:
    """
    Style composer service class for dependency injection.

    Provides the same functionality as module-level functions
    but as a class instance for frameworks that prefer DI.
    """

    def __init__(self, default_base_style: str = "soft_romantic"):
        """
        Initialize the style composer.

        Args:
            default_base_style: Default base style name to use
        """
        self._default_base_style = default_base_style

    def compose(
        self,
        base_style_name: Optional[str] = None,
        scene_mood_name: Optional[str] = None,
        emotional_intensity: int = 5,
        scene_context: str = "neutral"
    ) -> str:
        """
        Compose a style prompt.

        Args:
            base_style_name: Base style name (uses default if None)
            scene_mood_name: Specific mood preset name (auto-selects if None)
            emotional_intensity: Emotional intensity (1-10)
            scene_context: Scene context hint

        Returns:
            Complete style prompt string
        """
        style_name = base_style_name or self._default_base_style

        if scene_mood_name:
            scene_mood = get_mood_preset(scene_mood_name)
        else:
            scene_mood = get_mood_for_intensity(emotional_intensity, scene_context)

        return get_style_for_scene(style_name, scene_mood.intensity, scene_context)

    def compose_for_panels(
        self,
        panels_data: List[dict],
        base_style_name: Optional[str] = None
    ) -> List[str]:
        """
        Compose style prompts for multiple panels.

        Args:
            panels_data: List of panel data dicts
            base_style_name: Base style name (uses default if None)

        Returns:
            List of style prompt strings
        """
        style_name = base_style_name or self._default_base_style
        return compose_styles_for_panels(style_name, panels_data)


# Create default instance
style_composer = StyleComposer()
