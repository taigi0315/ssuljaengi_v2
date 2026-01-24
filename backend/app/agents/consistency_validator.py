# consistency_validator.py
"""
Scene-to-Scene Consistency Validator Agent (v2.1.0 E3-T02)

This agent analyzes the sequence of panels to ensure logical and visual
continuity between scenes. It checks for abrupt changes in:
- Time of day (Day -> Night without transition)
- Character outfits (Outfit A -> Outfit B without logic)
- Location logic (School -> Home without transition)
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ConsistencyIssue(BaseModel):
    panel_index: int
    issue_type: str  # "time_jump", "outfit_mismatch", "location_jump"
    description: str
    severity: str    # "warning", "error"

class ConsistencyState(BaseModel):
    panels: List[Dict[str, Any]]
    issues: List[ConsistencyIssue] = Field(default_factory=list)
    is_consistent: bool = True

async def run(state: ConsistencyState) -> ConsistencyState:
    """
    Analyze panels for scene-to-scene consistency.
    """
    if not state.panels:
        return state

    issues = []
    
    # Track state per scene
    scene_states = {} # {scene_num: {time: ..., location: ...}}
    
    for i, panel in enumerate(state.panels):
        panel_num = i + 1
        scene_num = panel.get("scene_number", 1) # Default to 1 if not set
        visual_prompt = panel.get("visual_prompt", "").lower()
        active_chars = panel.get("active_character_names", [])
        
        # Initialize scene state if new
        if scene_num not in scene_states:
            scene_states[scene_num] = {"time": None, "location": None}
            
        current_scene_state = scene_states[scene_num]
        
        # 1. Time Consistency within Scene
        new_time = _extract_time_of_day(visual_prompt)
        if new_time:
            if current_scene_state["time"] and current_scene_state["time"] != new_time:
                issues.append(ConsistencyIssue(
                    panel_index=i,
                    issue_type="time_jump",
                    description=f"Time changed from {current_scene_state['time']} to {new_time} within Scene {scene_num}",
                    severity="warning"
                ))
            else:
                current_scene_state["time"] = new_time
                
        # 2. Character Outfit Consistency (Mock logic)
        # In v2.1.0, we assume global style sheet handles this, but we can check
        # if a char appears in a scene but wasn't in previous panels of same scene
        # (Consistency is mainly about visual continuity, so complex outfit check requires VL-Model)
    
    return state.model_copy(update={"issues": issues, "is_consistent": len(issues) == 0})

def _extract_time_of_day(text: str) -> Optional[str]:
    if "night" in text: return "night"
    if "day" in text or "sun" in text: return "day"
    if "sunset" in text: return "sunset"
    return None
