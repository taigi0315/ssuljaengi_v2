"""
Multi-Panel Prompt Templates for Webtoon Enhancement.

This module provides prompt templates and formatting functions for generating
multi-panel webtoon pages in a single API call.

Key features:
- Structured panel-by-panel prompt format
- Support for 2-5 panels per page
- Integration with mood and style systems
- Character reference handling

v2.0.0: Initial implementation (Phase 3.1)
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass


# ============================================================================
# Multi-Panel Prompt Template (Task 3.1.2)
# ============================================================================

MULTI_PANEL_TEMPLATE = """A vertical webtoon-style comic page with a 9:16 aspect ratio,
featuring {panel_count} distinct horizontal panels stacked vertically.
The art style is {style_description}.

{panel_descriptions}

{style_keywords}. Thin black panel borders separating each panel clearly.

CRITICAL REQUIREMENTS:
- Generate exactly {panel_count} horizontal panels stacked vertically
- Each panel must be clearly separated by thin black borders
- Maintain consistent character appearance across all panels
- 9:16 vertical aspect ratio for the entire page
- No letterboxing or device frames

CRITICAL - NO TEXT OR SPEECH BUBBLES:
- DO NOT render any text, words, letters, or characters in any language
- DO NOT create speech bubbles, thought bubbles, dialogue boxes, or chat bubbles
- DO NOT add captions, subtitles, onomatopoeia (like "BANG", "POW"), or any written content
- Show character emotions through FACIAL EXPRESSIONS and BODY LANGUAGE only
- The dialogue will be added as an overlay AFTER image generation by a separate system
- NO TEXT. NO BUBBLES. EXPRESSIONS ONLY."""


MULTI_PANEL_WITH_REFERENCES_TEMPLATE = """A vertical webtoon-style comic page with a 9:16 aspect ratio,
featuring {panel_count} distinct horizontal panels stacked vertically.
The art style is {style_description}.

CHARACTER REFERENCES (maintain exact appearance in all panels):
{character_references}

{panel_descriptions}

{style_keywords}. Thin black panel borders separating each panel clearly.

CRITICAL REQUIREMENTS:
- Generate exactly {panel_count} horizontal panels stacked vertically
- Each panel must be clearly separated by thin black borders
- Characters MUST match the provided reference images exactly
- Maintain consistent character appearance across all panels
- 9:16 vertical aspect ratio for the entire page
- No letterboxing or device frames

CRITICAL - NO TEXT OR SPEECH BUBBLES:
- DO NOT render any text, words, letters, or characters in any language
- DO NOT create speech bubbles, thought bubbles, dialogue boxes, or chat bubbles
- DO NOT add captions, subtitles, onomatopoeia (like "BANG", "POW"), or any written content
- Show character emotions through FACIAL EXPRESSIONS and BODY LANGUAGE only
- The dialogue will be added as an overlay AFTER image generation by a separate system
- NO TEXT. NO BUBBLES. EXPRESSIONS ONLY."""


# Panel description format for each panel
PANEL_DESCRIPTION_FORMAT = """Panel {panel_number}: {shot_type} of {subject}. {description}{mood_hint}"""


# ============================================================================
# Panel Data Structure
# ============================================================================

@dataclass
class PanelData:
    """Data for a single panel in a multi-panel page."""
    panel_number: int
    shot_type: str
    subject: str
    description: str
    characters: List[str]
    emotional_intensity: int = 5
    mood_context: str = "neutral"

    def to_prompt_line(self, include_mood: bool = True) -> str:
        """Convert to a single line for the multi-panel prompt."""
        mood_hint = ""
        if include_mood and self.mood_context != "neutral":
            mood_hint = f" [{self.mood_context} mood]"

        return PANEL_DESCRIPTION_FORMAT.format(
            panel_number=self.panel_number,
            shot_type=self.shot_type,
            subject=self.subject,
            description=self.description,
            mood_hint=mood_hint
        )


# ============================================================================
# Prompt Formatting Functions (Task 3.1.3)
# ============================================================================

def format_multi_panel_prompt(
    panels: List[PanelData],
    style_description: str,
    style_keywords: str = "High resolution, clean line art, professional webtoon quality",
    character_references: Optional[Dict[str, str]] = None
) -> str:
    """
    Format a multi-panel prompt from panel data.

    This is the main entry point for creating multi-panel generation prompts.

    Args:
        panels: List of PanelData objects (2-5 panels)
        style_description: Art style description (e.g., "soft romantic manhwa style")
        style_keywords: Additional style keywords for the prompt
        character_references: Optional dict mapping character names to descriptions

    Returns:
        Formatted prompt string for multi-panel generation

    Raises:
        ValueError: If panel count is not between 2 and 5
    """
    if not panels:
        raise ValueError("At least one panel is required")

    if len(panels) > 5:
        raise ValueError("Maximum 5 panels per page supported")

    # Format panel descriptions
    panel_descriptions = "\n".join(
        panel.to_prompt_line(include_mood=True)
        for panel in panels
    )

    # Choose template based on whether we have character references
    if character_references:
        char_ref_text = "\n".join(
            f"- {name}: {desc}"
            for name, desc in character_references.items()
        )
        return MULTI_PANEL_WITH_REFERENCES_TEMPLATE.format(
            panel_count=len(panels),
            style_description=style_description,
            character_references=char_ref_text,
            panel_descriptions=panel_descriptions,
            style_keywords=style_keywords
        )
    else:
        return MULTI_PANEL_TEMPLATE.format(
            panel_count=len(panels),
            style_description=style_description,
            panel_descriptions=panel_descriptions,
            style_keywords=style_keywords
        )


def format_panels_from_shots(
    shots: List[Dict[str, Any]],
    style_description: str,
    style_keywords: str = "High resolution, clean line art, professional webtoon quality",
    character_references: Optional[Dict[str, str]] = None
) -> str:
    """
    Format a multi-panel prompt from shot data (from cinematographer).

    Convenience function that converts shot dictionaries to PanelData
    and formats the prompt.

    Args:
        shots: List of shot dictionaries with keys:
            - shot_type: Camera shot type
            - subject: Main subject of the shot
            - visual_prompt or description: Visual description
            - active_character_names or characters: Characters in shot
            - emotional_intensity: 1-10 scale
            - mood_context or detected_context: Mood hint
        style_description: Art style description
        style_keywords: Additional style keywords
        character_references: Optional character reference descriptions

    Returns:
        Formatted prompt string
    """
    panels = []

    for i, shot in enumerate(shots, start=1):
        # Extract shot data with fallbacks
        shot_type = shot.get("shot_type", "Medium shot")
        subject = shot.get("subject", "characters")
        description = shot.get("visual_prompt") or shot.get("description", "")
        characters = shot.get("active_character_names") or shot.get("characters", [])
        intensity = shot.get("emotional_intensity", 5)
        mood = shot.get("mood_context") or shot.get("detected_context", "neutral")

        panel = PanelData(
            panel_number=i,
            shot_type=shot_type,
            subject=subject,
            description=description,
            characters=characters if isinstance(characters, list) else [characters],
            emotional_intensity=intensity,
            mood_context=mood
        )
        panels.append(panel)

    return format_multi_panel_prompt(
        panels=panels,
        style_description=style_description,
        style_keywords=style_keywords,
        character_references=character_references
    )


def format_panels_from_webtoon_panels(
    webtoon_panels: List[Any],  # List[WebtoonPanel]
    style_description: str,
    style_keywords: str = "High resolution, clean line art, professional webtoon quality",
    character_references: Optional[Dict[str, str]] = None
) -> str:
    """
    Format a multi-panel prompt from WebtoonPanel objects.

    Args:
        webtoon_panels: List of WebtoonPanel model objects
        style_description: Art style description
        style_keywords: Additional style keywords
        character_references: Optional character reference descriptions

    Returns:
        Formatted prompt string
    """
    panels = []

    for i, wp in enumerate(webtoon_panels, start=1):
        # Build subject from characters
        chars = getattr(wp, "active_character_names", []) or []
        subject = ", ".join(chars) if chars else "scene"

        panel = PanelData(
            panel_number=i,
            shot_type=getattr(wp, "shot_type", "Medium shot"),
            subject=subject,
            description=getattr(wp, "visual_prompt", ""),
            characters=chars,
            emotional_intensity=getattr(wp, "emotional_intensity", 5),
            mood_context="neutral"  # Will be set by mood designer
        )
        panels.append(panel)

    return format_multi_panel_prompt(
        panels=panels,
        style_description=style_description,
        style_keywords=style_keywords,
        character_references=character_references
    )


# ============================================================================
# Utility Functions
# ============================================================================

def get_recommended_panel_count(panel_type: str) -> int:
    """
    Get recommended panel count based on scene type.

    Args:
        panel_type: Type of scene (action, dialogue, emotional, establishing)

    Returns:
        Recommended number of panels for this scene type
    """
    recommendations = {
        "action": 4,
        "dialogue": 3,
        "emotional": 2,
        "establishing": 2,
        "climax": 1,  # Single full-page panel
        "transition": 3,
        "default": 3
    }
    return recommendations.get(panel_type.lower(), 3)


def validate_panel_prompt(prompt: str) -> Dict[str, Any]:
    """
    Validate a multi-panel prompt for common issues.

    Args:
        prompt: The generated prompt string

    Returns:
        Dict with validation results:
            - is_valid: bool
            - issues: list of issue strings
            - panel_count: detected panel count
    """
    issues = []
    panel_count = 0

    # Check for panel markers
    import re
    panel_matches = re.findall(r'Panel \d+:', prompt)
    panel_count = len(panel_matches)

    if panel_count == 0:
        issues.append("No panel markers found (Panel N:)")
    elif panel_count == 1:
        issues.append("Only 1 panel found - use single panel generation instead")
    elif panel_count > 5:
        issues.append(f"Too many panels ({panel_count}) - maximum is 5")

    # Check for aspect ratio mention
    if "9:16" not in prompt:
        issues.append("Missing 9:16 aspect ratio specification")

    # Check for panel border instruction
    if "border" not in prompt.lower():
        issues.append("Missing panel border instruction")

    # Check for style description
    if "style" not in prompt.lower():
        issues.append("Missing style description")

    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "panel_count": panel_count
    }
