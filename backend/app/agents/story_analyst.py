# story_analyst.py
"""Story Analyst Agent

Analyzes the raw story script and extracts structured narrative elements.
"""

from pydantic import BaseModel
from typing import List, Dict

class StoryAnalystState(BaseModel):
    raw_story: str
    scenes: List[Dict] = []  # each dict contains scene metadata

def run(state: StoryAnalystState) -> StoryAnalystState:
    """Placeholder implementation – split story into scenes.
    In a real implementation this would call an LLM via LangChain.
    """
    # Very naive split by double newline as scene delimiter
    if not state.scenes:
        scenes = [s.strip() for s in state.raw_story.split("\n\n") if s.strip()]
        state.scenes = [{"scene_index": i, "text": txt} for i, txt in enumerate(scenes, start=1)]
    return state
