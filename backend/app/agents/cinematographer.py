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
    """
    Cinematographer Agent: Analyzes shot composition and pacing adherence.
    
    v2.1.0 E1-T04: Now validates shot choices against emotional pacing rules
    and tracks style mode distribution.
    """
    if not state.panels:
        return state.model_copy(update={"shot_plan": None})

    # Analyze shot distribution
    shot_types = [p.get("shot_type", "Medium shot") for p in state.panels]
    shot_counts: Dict[str, int] = {}
    
    # New statistics for v2.1.0
    style_mode_counts: Dict[str, int] = {}
    pacing_adherence = {
        "matches": 0,
        "mismatches": 0,
        "critical_mismatches": 0,  # e.g. Confession not having close-up
        "notes": []
    }
    
    for i, p in enumerate(state.panels):
        # 1. Shot Distribution
        st_norm = p.get("shot_type", "medium shot").lower().strip()
        shot_counts[st_norm] = shot_counts.get(st_norm, 0) + 1
        
        # 2. Style Mode Distribution (E5-T02)
        sm = p.get("style_mode")
        if sm:
            style_mode_counts[sm] = style_mode_counts.get(sm, 0) + 1
            
        # 3. Pacing Adherence (E1-T04)
        analysis = p.get("pacing_analysis")
        if analysis:
            recommended = [t.lower() for t in analysis.get("recommended_shot_types", [])]
            # Simple substring match check (e.g. "close_up" in "extreme close-up")
            is_match = any(rec in st_norm or st_norm in rec for rec in recommended)
            
            if is_match:
                pacing_adherence["matches"] += 1
            else:
                pacing_adherence["mismatches"] += 1
                
                # Check for critical mismatch (high intensity)
                intensity = analysis.get("emotional_intensity", 5)
                sentiment = analysis.get("sentiment", "")
                
                if intensity >= 8:
                    pacing_adherence["critical_mismatches"] += 1
                    pacing_adherence["notes"].append(
                        f"Panel {i+1} ({sentiment}, Int:{intensity}): Used '{st_norm}', "
                        f"recommended {recommended}. Consider revising."
                    )

    total_shots = len(state.panels)
    unique_shots = len(shot_counts)
    most_common = max(shot_counts.values()) if shot_counts else 0
    variety_ratio = unique_shots / total_shots if total_shots else 0

    shot_plan = {
        "total_shots": total_shots,
        "unique_shot_types": unique_shots,
        "shot_distribution": shot_counts,
        "style_mode_distribution": style_mode_counts,
        "variety_ratio": round(variety_ratio, 2),
        "most_common_count": most_common,
        "pacing_adherence": pacing_adherence,
        "analyzed": True,
    }

    return state.model_copy(update={"shot_plan": shot_plan})
