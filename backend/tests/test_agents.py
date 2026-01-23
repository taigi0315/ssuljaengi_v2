"""Unit tests for Phase 4 Agents

Tests each agent module to ensure basic functionality works as expected.
"""

import pytest
from app.agents.story_analyst import StoryAnalystState, run as story_analyst_run
from app.agents.cinematographer import CinematographerState, run as cinematographer_run
from app.agents.mood_designer import MoodDesignerState, run as mood_designer_run
from app.agents.visual_prompter import VisualPrompterState, run as visual_prompter_run
from app.agents.sfx_planner import SFXPlannerState, run as sfx_planner_run
from app.agents.panel_composer import PanelComposerState, run as panel_composer_run


class TestStoryAnalyst:
    """Test Story Analyst agent."""

    @pytest.mark.asyncio
    async def test_story_analyst_basic(self):
        """Test basic story analysis."""
        state = StoryAnalystState(
            raw_story="Character A meets Character B at a coffee shop.\n\nThey talk about their dreams."
        )
        result = story_analyst_run(state)
        
        assert result.scenes is not None
        assert len(result.scenes) == 2
        assert result.scenes[0]["scene_index"] == 1
        assert "coffee shop" in result.scenes[0]["text"]


class TestCinematographer:
    """Test Cinematographer agent."""

    @pytest.mark.asyncio
    async def test_cinematographer_basic(self):
        """Test basic shot analysis."""
        panels = [
            {"panel_number": 1, "shot_type": "Wide shot"},
            {"panel_number": 2, "shot_type": "Close-up"},
            {"panel_number": 3, "shot_type": "Wide shot"},
        ]
        state = CinematographerState(panels=panels)
        result = await cinematographer_run(state)
        
        assert result.shot_plan is not None
        assert result.shot_plan["total_shots"] == 3
        assert result.shot_plan["unique_shot_types"] == 2
        assert result.shot_plan["analyzed"] is True


class TestMoodDesigner:
    """Test Mood Designer agent."""

    @pytest.mark.asyncio
    async def test_mood_designer_basic(self):
        """Test basic mood assignment."""
        panels = [
            {
                "panel_number": 1,
                "scene_description": "Happy moment",
                "emotional_intensity": 8,
                "dialogue": []
            }
        ]
        state = MoodDesignerState(panels=panels)
        result = await mood_designer_run(state)
        
        assert result.mood_assignments is not None
        assert len(result.mood_assignments) == 1
        assert result.mood_assignments[0]["panel_number"] == 1


class TestVisualPrompter:
    """Test Visual Prompter agent."""

    @pytest.mark.asyncio
    async def test_visual_prompter_basic(self):
        """Test basic prompt enhancement."""
        panels = [
            {
                "panel_number": 1,
                "visual_prompt": "A beautiful sunset scene"
            }
        ]
        mood_assignments = [
            {
                "panel_number": 1,
                "intensity": 7,
                "detected_context": "romantic"
            }
        ]
        state = VisualPrompterState(
            panels=panels,
            mood_assignments=mood_assignments,
            image_style="SOFT_ROMANTIC_WEBTOON"
        )
        result = await visual_prompter_run(state)
        
        assert result.enhanced_prompts is not None
        assert len(result.enhanced_prompts) == 1
        assert "STYLE & MOOD" in result.enhanced_prompts[0]


class TestSFXPlanner:
    """Test SFX Planner agent."""

    @pytest.mark.asyncio
    async def test_sfx_planner_basic(self):
        """Test basic SFX planning."""
        panels = [
            {
                "panel_number": 1,
                "sfx_effects": [{"type": "speed_lines"}]
            },
            {
                "panel_number": 2,
                "sfx_effects": []
            }
        ]
        state = SFXPlannerState(panels=panels)
        result = await sfx_planner_run(state)
        
        assert result.sfx_plan is not None
        assert result.sfx_plan["panels_with_sfx"] == 1
        assert result.sfx_plan["total_panels"] == 2
        assert result.sfx_plan["sfx_coverage"] == 0.5


class TestPanelComposer:
    """Test Panel Composer agent."""

    @pytest.mark.asyncio
    async def test_panel_composer_basic(self):
        """Test basic panel composition."""
        panels = [
            {
                "panel_number": i,
                "scene_description": f"Scene {i}",
                "emotional_intensity": 5,
                "dialogue": []
            }
            for i in range(1, 6)
        ]
        state = PanelComposerState(panels=panels)
        result = await panel_composer_run(state)
        
        assert result.page_groupings is not None
        assert len(result.page_groupings) > 0
        assert result.page_statistics is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
