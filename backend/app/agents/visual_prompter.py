# visual_prompter.py
"""Visual Prompter Agent

Enhances visual prompts with mood and style information for image generation.
"""

from pydantic import BaseModel
from typing import List, Dict, Any

class VisualPrompterState(BaseModel):
    panels: List[Dict[str, Any]] | None = None
    mood_assignments: List[Dict[str, Any]] | None = None
    image_style: str = "SOFT_ROMANTIC_WEBTOON"
    enhanced_prompts: List[str] | None = None
    # Additional fields can be added as needed

async def run(state: VisualPrompterState) -> VisualPrompterState:
    """Placeholder implementation – enhances prompts with mood and style.

    Combines base visual prompts from panels with mood modifiers and style keywords.
    Uses the existing `get_legacy_style_with_mood` function.
    """
    if not state.panels:
        return state.model_copy(update={"error": "No panels provided", "enhanced_prompts": None})

    from app.services.style_composer import get_legacy_style_with_mood

    mood_assignments = state.mood_assignments or []
    
    # Create mood lookup by panel_number
    mood_lookup = {m["panel_number"]: m for m in mood_assignments}

    enhanced_prompts = []
    for panel in state.panels:
        panel_num = panel.get("panel_number")
        base_prompt = panel.get("visual_prompt", "")
        mood_data = mood_lookup.get(panel_num, {})

        # Get composed style with mood
        intensity = mood_data.get("intensity", 5)
        context = mood_data.get("detected_context", "neutral")

        composed_style = get_legacy_style_with_mood(
            legacy_style_key=state.image_style,
            emotional_intensity=intensity,
            scene_context=context
        )

        # Combine base prompt with style
        enhanced = f"{base_prompt}\n\n[STYLE & MOOD]\n{composed_style}"
        enhanced_prompts.append(enhanced)

    return state.model_copy(update={"enhanced_prompts": enhanced_prompts})
