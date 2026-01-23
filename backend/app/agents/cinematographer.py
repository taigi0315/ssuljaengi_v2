# cinematographer.py
"""Cinematographer Agent

Analyzes panel shot types and provides a shot plan summary.
"""

from pydantic import BaseModel
from typing import List, Dict, Any

class CinematographerState(BaseModel):
    panels: List[Dict[str, Any]] | None = None
    shot_plan: Dict[str, Any] | None = None
    # Additional fields can be added as needed

async def run(state: CinematographerState) -> CinematographerState:
    """Placeholder implementation – analyzes shot distribution.

    In a full implementation this would invoke an LLM or rule‑based system to
    suggest shot composition improvements. For now we compute simple statistics
    from the existing panel data.
    """
    if not state.panels:
        return state.model_copy(update={"error": "No panels provided", "shot_plan": None})

    # Analyze shot distribution (mirrors cinematographer_node logic)
    shot_types = [p.get("shot_type", "Medium shot") for p in state.panels]
    shot_counts: Dict[str, int] = {}
    for st in shot_types:
        normalized = st.lower().strip()
        shot_counts[normalized] = shot_counts.get(normalized, 0) + 1

    total_shots = len(state.panels)
    unique_shots = len(shot_counts)
    most_common = max(shot_counts.values()) if shot_counts else 0
    variety_ratio = unique_shots / total_shots if total_shots else 0

    shot_plan = {
        "total_shots": total_shots,
        "unique_shot_types": unique_shots,
        "shot_distribution": shot_counts,
        "variety_ratio": round(variety_ratio, 2),
        "most_common_count": most_common,
        "analyzed": True,
    }

    return state.model_copy(update={"shot_plan": shot_plan})
