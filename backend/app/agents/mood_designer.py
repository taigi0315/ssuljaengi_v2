# mood_designer.py
"""Mood Designer Agent

Assigns per‑scene moods based on panel content and emotional cues.
"""

from pydantic import BaseModel
from typing import List, Dict, Any

class MoodDesignerState(BaseModel):
    panels: List[Dict[str, Any]] | None = None
    mood_assignments: List[Dict[str, Any]] | None = None
    # Additional fields can be added as needed

async def run(state: MoodDesignerState) -> MoodDesignerState:
    """Placeholder implementation – uses the existing `mood_designer` service.

    In a full implementation this would call an LLM chain to infer moods.
    For now we reuse the `mood_designer.assign_moods` function.
    """
    if not state.panels:
        return state.model_copy(update={"error": "No panels provided", "mood_assignments": None})

    from app.services.mood_designer import mood_designer
    from app.models.story import WebtoonPanel

    # Convert dict panels to model instances
    panel_objs = [WebtoonPanel(**p) for p in state.panels]
    assignments = mood_designer.assign_moods(panel_objs)

    # Serialize assignments to simple dicts
    mood_data = []
    for a in assignments:
        mood_data.append({
            "panel_number": a.panel_number,
            "mood_name": a.mood.name,
            "intensity": a.mood.intensity,
            "detected_context": a.detected_context,
            "color_temperature": a.mood.color_temperature.value,
            "lighting_mood": a.mood.lighting_mood.value,
            "reasoning": a.reasoning,
        })

    return state.model_copy(update={"mood_assignments": mood_data})
