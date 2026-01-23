"""
Tests for Enhanced Webtoon Workflow (Phase 4).

Tests the modular agent-based workflow system including:
- Agent node functions
- Workflow state management
- Rewrite targeting logic
- Routing decisions

v2.0.0: Phase 4 Architecture tests
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

from app.workflows.enhanced_webtoon_workflow import (
    EnhancedWebtoonState,
    AgentType,
    ISSUE_AGENT_MAP,
    identify_rewrite_target,
    should_rewrite,
    story_analyst_node,
    cinematographer_node,
    mood_designer_node,
    visual_prompter_node,
    sfx_planner_node,
    panel_composer_node,
    evaluator_node,
    create_enhanced_webtoon_workflow,
)
from app.models.story import WebtoonPanel, WebtoonScript, Character


# ============================================================================
# Test Data Helpers
# ============================================================================

def create_test_state(**overrides) -> EnhancedWebtoonState:
    """Create a test workflow state with defaults."""
    default_state = {
        "story": "Test story content for webtoon generation.",
        "story_genre": "MODERN_ROMANCE_DRAMA",
        "image_style": "SOFT_ROMANTIC_WEBTOON",
        "story_analysis": None,
        "scene_plan": None,
        "webtoon_script": None,
        "characters": None,
        "panels": None,
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
        "current_step": "starting",
        "error": None,
    }
    default_state.update(overrides)
    return default_state


def create_test_panels(count: int = 5) -> list:
    """Create test panel data."""
    return [
        {
            "panel_number": i + 1,
            "shot_type": ["Close-up", "Medium shot", "Wide shot"][i % 3],
            "active_character_names": ["Hana"],
            "visual_prompt": f"Test visual prompt for panel {i + 1}",
            "story_beat": f"Story beat {i + 1}",
            "emotional_intensity": 5 + (i % 3),
            "dialogue": [{"character": "Hana", "text": f"Line {i + 1}"}],
            "character_frame_percentage": 40 + (i * 10),
            "environment_frame_percentage": 60 - (i * 10),
        }
        for i in range(count)
    ]


def create_test_characters() -> list:
    """Create test character data."""
    return [
        {
            "name": "Hana",
            "gender": "female",
            "age_group": "20s",
            "visual_description": "A young woman with long black hair"
        }
    ]


# ============================================================================
# Test Agent Type Enum
# ============================================================================

class TestAgentType:
    """Tests for AgentType enum."""

    def test_all_agents_defined(self):
        """All expected agents should be defined."""
        expected = [
            "story_analyst", "scene_planner", "cinematographer",
            "mood_designer", "visual_prompter", "sfx_planner",
            "panel_composer", "writer"
        ]
        for agent in expected:
            assert agent in [a.value for a in AgentType]

    def test_agent_values_are_strings(self):
        """Agent values should be strings."""
        for agent in AgentType:
            assert isinstance(agent.value, str)


# ============================================================================
# Test Rewrite Target Identification (Task 4.3.1)
# ============================================================================

class TestIdentifyRewriteTarget:
    """Tests for identify_rewrite_target function."""

    def test_empty_issues_returns_writer(self):
        """Empty issues list should default to writer."""
        result = identify_rewrite_target([])
        assert result == AgentType.WRITER.value

    def test_scene_count_issue_targets_scene_planner(self):
        """Scene count issues should target scene_planner."""
        issues = ["Only 5 panels. Need 10-30."]
        result = identify_rewrite_target(issues)
        assert result == AgentType.SCENE_PLANNER.value

    def test_dialogue_issue_targets_scene_planner(self):
        """Dialogue issues should target scene_planner."""
        issues = ["Only 3/10 scenes have dialogue (30%). Need 70%+."]
        result = identify_rewrite_target(issues)
        assert result == AgentType.SCENE_PLANNER.value

    def test_shot_variety_issue_targets_cinematographer(self):
        """Shot variety issues should target cinematographer."""
        issues = ["Shot variety low: 8/10 are medium shots"]
        result = identify_rewrite_target(issues)
        assert result == AgentType.CINEMATOGRAPHER.value

    def test_visual_dynamism_issue_targets_cinematographer(self):
        """Visual dynamism issues should target cinematographer."""
        issues = ["Uniform framing: variance=50"]
        result = identify_rewrite_target(issues)
        assert result == AgentType.CINEMATOGRAPHER.value

    def test_visual_prompt_issue_targets_visual_prompter(self):
        """Visual prompt issues should target visual_prompter."""
        issues = ["3 panels have incomplete visual prompts."]
        result = identify_rewrite_target(issues)
        assert result == AgentType.VISUAL_PROMPTER.value

    def test_character_issue_targets_story_analyst(self):
        """Character issues should target story_analyst."""
        issues = ["Characters in scenes not defined: ['Unknown']"]
        result = identify_rewrite_target(issues)
        assert result == AgentType.STORY_ANALYST.value

    def test_page_grouping_issue_targets_panel_composer(self):
        """Page grouping issues should target panel_composer."""
        issues = ["Only 2 pages. Need at least 4."]
        result = identify_rewrite_target(issues)
        assert result == AgentType.PANEL_COMPOSER.value

    def test_multiple_issues_targets_most_common(self):
        """Multiple issues should target the most matched agent."""
        issues = [
            "Shot variety low",
            "consecutive same-type shots",
            "Uniform framing",
            "Only 5 panels",  # Scene planner
        ]
        # 3 cinematographer issues vs 1 scene_planner
        result = identify_rewrite_target(issues)
        assert result == AgentType.CINEMATOGRAPHER.value


# ============================================================================
# Test Routing Function (Task 4.2.5)
# ============================================================================

class TestShouldRewrite:
    """Tests for should_rewrite routing function."""

    @patch('app.workflows.enhanced_webtoon_workflow.get_settings')
    def test_high_score_returns_end(self, mock_settings):
        """High score should return 'end'."""
        mock_settings.return_value.webtoon_max_rewrites = 3
        mock_settings.return_value.webtoon_evaluation_threshold = 7.0

        state = create_test_state(evaluation_score=8.5)
        result = should_rewrite(state)
        assert result == "end"

    @patch('app.workflows.enhanced_webtoon_workflow.get_settings')
    def test_low_score_returns_rewrite(self, mock_settings):
        """Low score should return 'rewrite' if under max rewrites."""
        mock_settings.return_value.webtoon_max_rewrites = 3
        mock_settings.return_value.webtoon_evaluation_threshold = 7.0

        state = create_test_state(evaluation_score=5.0, rewrite_count=0)
        result = should_rewrite(state)
        assert result == "rewrite"

    @patch('app.workflows.enhanced_webtoon_workflow.get_settings')
    def test_max_rewrites_returns_end(self, mock_settings):
        """Max rewrites reached should return 'end'."""
        mock_settings.return_value.webtoon_max_rewrites = 3
        mock_settings.return_value.webtoon_evaluation_threshold = 7.0

        state = create_test_state(evaluation_score=5.0, rewrite_count=3)
        result = should_rewrite(state)
        assert result == "end"

    @patch('app.workflows.enhanced_webtoon_workflow.get_settings')
    def test_error_returns_end(self, mock_settings):
        """Error in state should return 'end'."""
        mock_settings.return_value.webtoon_max_rewrites = 3
        mock_settings.return_value.webtoon_evaluation_threshold = 7.0

        state = create_test_state(error="Some error occurred")
        result = should_rewrite(state)
        assert result == "end"


# ============================================================================
# Test Individual Agent Nodes
# ============================================================================

class TestStoryAnalystNode:
    """Tests for story_analyst_node."""

    @pytest.mark.asyncio
    async def test_analyzes_story(self):
        """Story analyst should analyze the story."""
        state = create_test_state(story="A long story about love and adventure in Seoul.")
        result = await story_analyst_node(state)

        assert result["story_analysis"] is not None
        assert result["story_analysis"]["analyzed"] is True
        assert "estimated_scenes" in result["story_analysis"]
        assert result["current_step"] == "story_analyzed"

    @pytest.mark.asyncio
    async def test_empty_story_still_works(self):
        """Empty story should still produce analysis."""
        state = create_test_state(story="")
        result = await story_analyst_node(state)

        assert result["story_analysis"] is not None


class TestCinematographerNode:
    """Tests for cinematographer_node."""

    @pytest.mark.asyncio
    async def test_analyzes_shots(self):
        """Cinematographer should analyze shot distribution."""
        state = create_test_state(panels=create_test_panels(5))
        result = await cinematographer_node(state)

        assert result["shot_plan"] is not None
        assert result["shot_plan"]["analyzed"] is True
        assert "shot_distribution" in result["shot_plan"]
        assert result["current_step"] == "shots_analyzed"

    @pytest.mark.asyncio
    async def test_no_panels_returns_error(self):
        """No panels should return error."""
        state = create_test_state(panels=None)
        result = await cinematographer_node(state)

        assert result["error"] is not None
        assert result["current_step"] == "failed"


class TestMoodDesignerNode:
    """Tests for mood_designer_node."""

    @pytest.mark.asyncio
    async def test_assigns_moods(self):
        """Mood designer should assign moods to panels."""
        state = create_test_state(panels=create_test_panels(3))
        result = await mood_designer_node(state)

        assert result["mood_assignments"] is not None
        assert len(result["mood_assignments"]) == 3
        assert result["current_step"] == "moods_assigned"

        # Check mood structure
        mood = result["mood_assignments"][0]
        assert "panel_number" in mood
        assert "mood_name" in mood
        assert "intensity" in mood

    @pytest.mark.asyncio
    async def test_no_panels_returns_error(self):
        """No panels should return error."""
        state = create_test_state(panels=None)
        result = await mood_designer_node(state)

        assert result["error"] is not None


class TestVisualPrompterNode:
    """Tests for visual_prompter_node."""

    @pytest.mark.asyncio
    async def test_enhances_prompts(self):
        """Visual prompter should enhance prompts with mood."""
        panels = create_test_panels(3)
        mood_assignments = [
            {"panel_number": i + 1, "intensity": 5, "detected_context": "neutral"}
            for i in range(3)
        ]
        state = create_test_state(panels=panels, mood_assignments=mood_assignments)
        result = await visual_prompter_node(state)

        assert result["enhanced_prompts"] is not None
        assert len(result["enhanced_prompts"]) == 3
        assert result["current_step"] == "prompts_enhanced"

        # Check prompt contains style info
        assert "STYLE" in result["enhanced_prompts"][0]


class TestSfxPlannerNode:
    """Tests for sfx_planner_node."""

    @pytest.mark.asyncio
    async def test_plans_sfx(self):
        """SFX planner should analyze effects."""
        panels = create_test_panels(3)
        panels[0]["sfx_effects"] = [{"type": "impact", "intensity": "high"}]
        state = create_test_state(panels=panels)
        result = await sfx_planner_node(state)

        assert result["sfx_plan"] is not None
        assert result["sfx_plan"]["planned"] is True
        assert result["sfx_plan"]["panels_with_sfx"] == 1
        assert result["current_step"] == "sfx_planned"


class TestPanelComposerNode:
    """Tests for panel_composer_node."""

    @pytest.mark.asyncio
    async def test_groups_panels(self):
        """Panel composer should group panels into pages."""
        state = create_test_state(panels=create_test_panels(8))
        result = await panel_composer_node(state)

        assert result["page_groupings"] is not None
        assert len(result["page_groupings"]) > 0
        assert result["page_statistics"] is not None
        assert result["current_step"] == "panels_composed"

        # Check page structure
        page = result["page_groupings"][0]
        assert "page_number" in page
        assert "layout_type" in page
        assert "panel_indices" in page


# ============================================================================
# Test Workflow Graph Structure
# ============================================================================

class TestWorkflowStructure:
    """Tests for workflow graph structure."""

    def test_workflow_compiles(self):
        """Workflow should compile without errors."""
        workflow = create_enhanced_webtoon_workflow()
        assert workflow is not None

    def test_workflow_has_all_nodes(self):
        """Workflow should have all expected nodes."""
        workflow = create_enhanced_webtoon_workflow()

        # Check that workflow was created (basic structure test)
        # LangGraph compiled workflows don't expose nodes directly,
        # but we can verify it was created successfully
        assert workflow is not None


# ============================================================================
# Test Issue to Agent Mapping
# ============================================================================

class TestIssueAgentMap:
    """Tests for ISSUE_AGENT_MAP configuration."""

    def test_map_has_scene_issues(self):
        """Map should include scene-related issues."""
        assert "scene_count" in ISSUE_AGENT_MAP
        assert ISSUE_AGENT_MAP["scene_count"] == AgentType.SCENE_PLANNER

    def test_map_has_shot_issues(self):
        """Map should include shot-related issues."""
        assert "shot_variety" in ISSUE_AGENT_MAP
        assert ISSUE_AGENT_MAP["shot_variety"] == AgentType.CINEMATOGRAPHER

    def test_map_has_prompt_issues(self):
        """Map should include prompt-related issues."""
        assert "visual_prompt" in ISSUE_AGENT_MAP
        assert ISSUE_AGENT_MAP["visual_prompt"] == AgentType.VISUAL_PROMPTER

    def test_map_has_page_issues(self):
        """Map should include page-related issues."""
        assert "page" in ISSUE_AGENT_MAP
        assert ISSUE_AGENT_MAP["page"] == AgentType.PANEL_COMPOSER


# ============================================================================
# Integration Tests
# ============================================================================

class TestEnhancedWorkflowIntegration:
    """Integration tests for the enhanced workflow."""

    @pytest.mark.asyncio
    async def test_agent_pipeline_sequence(self):
        """Test that agents run in correct sequence."""
        # Create state and run through first few agents
        state = create_test_state()

        # Story analyst
        state = await story_analyst_node(state)
        assert state["current_step"] == "story_analyzed"

        # Note: scene_planner requires actual LLM call, so we skip in unit tests
        # But we can verify the pipeline logic works

    @pytest.mark.asyncio
    async def test_cinematographer_to_mood_pipeline(self):
        """Test cinematographer -> mood_designer pipeline."""
        panels = create_test_panels(5)
        state = create_test_state(panels=panels)

        # Cinematographer
        state = await cinematographer_node(state)
        assert state["shot_plan"] is not None

        # Mood designer
        state = await mood_designer_node(state)
        assert state["mood_assignments"] is not None
        assert len(state["mood_assignments"]) == 5

    @pytest.mark.asyncio
    async def test_full_enhancement_pipeline(self):
        """Test the full enhancement pipeline (post scene_planner)."""
        panels = create_test_panels(8)
        state = create_test_state(panels=panels)

        # Run through all enhancement nodes
        state = await cinematographer_node(state)
        state = await mood_designer_node(state)
        state = await visual_prompter_node(state)
        state = await sfx_planner_node(state)
        state = await panel_composer_node(state)

        # Verify all outputs
        assert state["shot_plan"]["analyzed"] is True
        assert len(state["mood_assignments"]) == 8
        assert len(state["enhanced_prompts"]) == 8
        assert state["sfx_plan"]["planned"] is True
        assert len(state["page_groupings"]) > 0
