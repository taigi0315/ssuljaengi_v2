"""Agents package for modular webtoon generation workflow.

Each agent is a specialized module responsible for a specific aspect of webtoon creation:
- story_analyst: Extracts key information from the raw story
- scene_planner: Plans scene structure and beats
- cinematographer: Analyzes shot types and compositions
- mood_designer: Assigns per-scene moods based on emotional content
- visual_prompter: Enhances visual prompts with mood and style
- sfx_planner: Plans visual effects for panels
- panel_composer: Groups panels into pages for multi-panel generation

All agents follow the same pattern:
1. Define a Pydantic State model with input/output fields
2. Implement an async `run(state) -> state` function
3. Can be used standalone or integrated into LangGraph workflows
"""

from .story_analyst import StoryAnalystState, run as story_analyst_run
from .scene_planner import ScenePlannerState, run as scene_planner_run
from .cinematographer import CinematographerState, run as cinematographer_run
from .mood_designer import MoodDesignerState, run as mood_designer_run
from .visual_prompter import VisualPrompterState, run as visual_prompter_run
from .sfx_planner import SFXPlannerState, run as sfx_planner_run
from .panel_composer import PanelComposerState, run as panel_composer_run

__all__ = [
    "StoryAnalystState",
    "story_analyst_run",
    "ScenePlannerState",
    "scene_planner_run",
    "CinematographerState",
    "cinematographer_run",
    "MoodDesignerState",
    "mood_designer_run",
    "VisualPrompterState",
    "visual_prompter_run",
    "SFXPlannerState",
    "sfx_planner_run",
    "PanelComposerState",
    "panel_composer_run",
]
