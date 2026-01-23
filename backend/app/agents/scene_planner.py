# scene_planner.py
"""Scene Planner Agent

Generates a scene plan (beats, panel layout) from the raw story.
"""

from pydantic import BaseModel
from typing import List, Dict, Any

class ScenePlannerState(BaseModel):
    story: str
    story_genre: str = "MODERN_ROMANCE_DRAMA"
    image_style: str = "SOFT_ROMANTIC_WEBTOON"
    scene_plan: Dict[str, Any] | None = None
    # Additional fields can be added as needed

async def run(state: ScenePlannerState) -> ScenePlannerState:
    """Placeholder implementation – delegates to the existing monolithic writer.

    In a full implementation this would call a dedicated LLM chain to produce a
    structured scene plan. For now we reuse `webtoon_writer.convert_story_to_script`
    to obtain a script and extract basic statistics.
    """
    from app.services.webtoon_writer import webtoon_writer

    script = await webtoon_writer.convert_story_to_script(
        state.story, state.story_genre, state.image_style
    )
    # Simple scene plan: total panels and character count
    scene_plan = {
        "total_panels": len(script.panels),
        "character_count": len(script.characters),
        "planned": True,
    }
    return state.copy(update={"scene_plan": scene_plan})
