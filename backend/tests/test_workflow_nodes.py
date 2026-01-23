"""Mock-based integration tests for Enhanced Webtoon Workflow

Tests the workflow structure and agent connections without requiring API calls.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.workflows.enhanced_webtoon_workflow import (
    enhanced_webtoon_workflow,
    EnhancedWebtoonState,
    story_analyst_node,
    cinematographer_node,
    mood_designer_node,
    visual_prompter_node,
    sfx_planner_node,
    panel_composer_node,
)
from app.models.story import WebtoonScript, WebtoonPanel, Character


class TestWorkflowStructure:
    """Test workflow structure and connections without API calls."""

    def test_workflow_graph_structure(self):
        """Test that workflow graph is properly structured."""
        # Workflow should be compiled and ready
        assert enhanced_webtoon_workflow is not None
        
        # Check that nodes exist
        graph_dict = enhanced_webtoon_workflow.get_graph().to_json()
        assert graph_dict is not None
        
        print("\n✅ Workflow graph structure is valid")


    @pytest.mark.asyncio
    async def test_cinematographer_node_standalone(self):
        """Test cinematographer node with mock panel data."""
        state: EnhancedWebtoonState = {
            "story": "Test story",
            "story_genre": "MODERN_ROMANCE_DRAMA",
            "image_style": "SOFT_ROMANTIC_WEBTOON",
            "panels": [
                {"panel_number": 1, "shot_type": "Wide shot"},
                {"panel_number": 2, "shot_type": "Close-up"},
                {"panel_number": 3, "shot_type": "Medium shot"},
            ],
            "story_analysis": None,
            "scene_plan": None,
            "webtoon_script": None,
            "characters": None,
            "shot_plan": None,
            "mood_assignments": None,
            "enhanced_prompts": None,
            "sfx_plan": None,
            "page_groupings": None,
            "page_statistics": None,
            "evaluation_score": 0.0,
            "evaluation_feedback": "",
            "evaluation_issues": [],
            "score_breakdown": None,
            "rewrite_count": 0,
            "rewrite_history": [],
            "target_agent": None,
            "current_step": "start",
            "error": None,
        }

        result = await cinematographer_node(state)
        
        assert result is not None
        assert result.get("error") is None
        assert result.get("shot_plan") is not None
        assert result["shot_plan"]["total_shots"] == 3
        assert result["shot_plan"]["unique_shot_types"] == 3
        
        print("\n✅ Cinematographer node works standalone")


    @pytest.mark.asyncio
    async def test_mood_designer_node_standalone(self):
        """Test mood designer node with mock panel data."""
        panels = [
            {
                "panel_number": 1,
                "scene_description": "Happy moment",
                "emotional_intensity": 8,
                "dialogue": [],
                "visual_prompt": "Test prompt",
                "shot_type": "Medium shot",
                "active_character_names": [],
            }
        ]
        
        state: EnhancedWebtoonState = {
            "story": "Test",
            "story_genre": "MODERN_ROMANCE_DRAMA",
            "image_style": "SOFT_ROMANTIC_WEBTOON",
            "panels": panels,
            "story_analysis": None,
            "scene_plan": None,
            "webtoon_script": None,
            "characters": None,
            "shot_plan": None,
            "mood_assignments": None,
            "enhanced_prompts": None,
            "sfx_plan": None,
            "page_groupings": None,
            "page_statistics": None,
            "evaluation_score": 0.0,
            "evaluation_feedback": "",
            "evaluation_issues": [],
            "score_breakdown": None,
            "rewrite_count": 0,
            "rewrite_history": [],
            "target_agent": None,
            "current_step": "start",
            "error": None,
        }

        result = await mood_designer_node(state)
        
        assert result is not None
        assert result.get("error") is None
        assert result.get("mood_assignments") is not None
        assert len(result["mood_assignments"]) == 1
        
        print("\n✅ Mood Designer node works standalone")


    @pytest.mark.asyncio
    async def test_visual_prompter_node_standalone(self):
        """Test visual prompter node with mock data."""
        panels = [
            {
                "panel_number": 1,
                "visual_prompt": "A beautiful sunset",
            }
        ]
        
        mood_assignments = [
            {
                "panel_number": 1,
                "intensity": 7,
                "detected_context": "romantic",
            }
        ]
        
        state: EnhancedWebtoonState = {
            "story": "Test",
            "story_genre": "MODERN_ROMANCE_DRAMA",
            "image_style": "SOFT_ROMANTIC_WEBTOON",
            "panels": panels,
            "mood_assignments": mood_assignments,
            "story_analysis": None,
            "scene_plan": None,
            "webtoon_script": None,
            "characters": None,
            "shot_plan": None,
            "enhanced_prompts": None,
            "sfx_plan": None,
            "page_groupings": None,
            "page_statistics": None,
            "evaluation_score": 0.0,
            "evaluation_feedback": "",
            "evaluation_issues": [],
            "score_breakdown": None,
            "rewrite_count": 0,
            "rewrite_history": [],
            "target_agent": None,
            "current_step": "start",
            "error": None,
        }

        result = await visual_prompter_node(state)
        
        assert result is not None
        assert result.get("error") is None
        assert result.get("enhanced_prompts") is not None
        assert len(result["enhanced_prompts"]) == 1
        assert "STYLE & MOOD" in result["enhanced_prompts"][0]
        
        print("\n✅ Visual Prompter node works standalone")


    @pytest.mark.asyncio
    async def test_sfx_planner_node_standalone(self):
        """Test SFX planner node with mock data."""
        panels = [
            {
                "panel_number": 1,
                "sfx_effects": [{"type": "speed_lines"}],
            },
            {
                "panel_number": 2,
                "sfx_effects": [],
            }
        ]
        
        state: EnhancedWebtoonState = {
            "story": "Test",
            "story_genre": "MODERN_ROMANCE_DRAMA",
            "image_style": "SOFT_ROMANTIC_WEBTOON",
            "panels": panels,
            "story_analysis": None,
            "scene_plan": None,
            "webtoon_script": None,
            "characters": None,
            "shot_plan": None,
            "mood_assignments": None,
            "enhanced_prompts": None,
            "sfx_plan": None,
            "page_groupings": None,
            "page_statistics": None,
            "evaluation_score": 0.0,
            "evaluation_feedback": "",
            "evaluation_issues": [],
            "score_breakdown": None,
            "rewrite_count": 0,
            "rewrite_history": [],
            "target_agent": None,
            "current_step": "start",
            "error": None,
        }

        result = await sfx_planner_node(state)
        
        assert result is not None
        assert result.get("error") is None
        assert result.get("sfx_plan") is not None
        assert result["sfx_plan"]["panels_with_sfx"] == 1
        assert result["sfx_plan"]["total_panels"] == 2
        
        print("\n✅ SFX Planner node works standalone")


    @pytest.mark.asyncio
    async def test_panel_composer_node_standalone(self):
        """Test panel composer node with mock data."""
        panels = [
            {
                "panel_number": i,
                "scene_description": f"Scene {i}",
                "emotional_intensity": 5,
                "dialogue": [],
                "visual_prompt": "Test",
                "shot_type": "Medium shot",
                "active_character_names": [],
            }
            for i in range(1, 6)
        ]
        
        state: EnhancedWebtoonState = {
            "story": "Test",
            "story_genre": "MODERN_ROMANCE_DRAMA",
            "image_style": "SOFT_ROMANTIC_WEBTOON",
            "panels": panels,
            "story_analysis": None,
            "scene_plan": None,
            "webtoon_script": None,
            "characters": None,
            "shot_plan": None,
            "mood_assignments": None,
            "enhanced_prompts": None,
            "sfx_plan": None,
            "page_groupings": None,
            "page_statistics": None,
            "evaluation_score": 0.0,
            "evaluation_feedback": "",
            "evaluation_issues": [],
            "score_breakdown": None,
            "rewrite_count": 0,
            "rewrite_history": [],
            "target_agent": None,
            "current_step": "start",
            "error": None,
        }

        result = await panel_composer_node(state)
        
        assert result is not None
        assert result.get("error") is None
        assert result.get("page_groupings") is not None
        assert len(result["page_groupings"]) > 0
        
        print("\n✅ Panel Composer node works standalone")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
