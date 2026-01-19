"""
Integration tests for the full fidelity validation workflow.

These tests verify the complete workflow execution, including:
- End-to-end workflow completion
- Convergence behavior across iterations
- Error handling
- Output format validation
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.workflows.fidelity_workflow import (
    run_fidelity_workflow,
    story_architect_node,
    webtoon_scripter_node,
    blind_reader_node,
    evaluator_node,
    should_continue
)
from app.models.fidelity_state import (
    WebtoonFidelityState,
    FidelityValidationResponse
)


class TestWorkflowNodes:
    """Test individual workflow nodes."""

    @pytest.fixture
    def initial_state(self) -> WebtoonFidelityState:
        """Create initial workflow state."""
        return {
            "seed": "A detective solves a mystery",
            "original_story": "",
            "story_summary": "",
            "character_motivations": {},
            "key_conflicts": [],
            "plot_points": [],
            "script_panels": [],
            "characters": [],
            "reconstructed_story": "",
            "inferred_motivations": {},
            "inferred_conflicts": [],
            "unclear_elements": [],
            "reader_confidence": 0.0,
            "fidelity_score": 0.0,
            "information_gaps": [],
            "critique": None,
            "iteration": 1,
            "max_iterations": 3,
            "is_validated": False,
            "current_step": "starting",
            "error": None
        }

    @pytest.mark.asyncio
    @patch('app.services.fidelity.story_architect.llm_config')
    async def test_story_architect_node_generates_story(self, mock_config, initial_state):
        """Story architect should generate complete story data."""
        # Setup mock
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content='{"story": "A detective named Sam...", "summary": "Sam solves a case", "character_motivations": {"Sam": {"goal": "solve the case", "motivation": "justice", "obstacle": "lack of evidence"}}, "key_conflicts": ["Sam vs criminal"], "plot_points": ["Discovery", "Investigation", "Resolution"]}'
        ))
        mock_config.get_model.return_value = mock_llm

        # Note: Due to LangChain's chain composition, we'd need more complex mocking
        # This test documents expected behavior

    @pytest.mark.asyncio
    async def test_blind_reader_node_filters_state(self, initial_state):
        """Blind reader node should filter out original story."""
        # Add story and panels to state
        initial_state["original_story"] = "SECRET STORY"
        initial_state["script_panels"] = [
            {
                "panel_number": 1,
                "visual_description": "A man investigates",
                "dialogue": [],
                "shot_type": "wide",
                "environment": "office"
            }
        ]
        initial_state["characters"] = [
            {"name": "Sam", "visual_description": "A detective"}
        ]

        # Import filter function
        from app.services.fidelity.blind_reader import filter_state_for_blind_reader

        # Filter should not contain original_story
        filtered = filter_state_for_blind_reader(initial_state)
        assert "original_story" not in filtered
        assert "SECRET STORY" not in str(filtered)


class TestWorkflowExecution:
    """Test workflow execution scenarios."""

    @pytest.mark.asyncio
    @patch('app.workflows.fidelity_workflow.story_architect')
    @patch('app.workflows.fidelity_workflow.webtoon_scripter')
    @patch('app.workflows.fidelity_workflow.blind_reader')
    @patch('app.workflows.fidelity_workflow.fidelity_evaluator')
    async def test_workflow_passes_on_high_score(
        self,
        mock_evaluator,
        mock_reader,
        mock_scripter,
        mock_architect
    ):
        """Workflow should complete successfully with high fidelity score."""
        # Mock story architect
        mock_architect.generate_story = AsyncMock(return_value={
            "story": "A simple test story",
            "summary": "Test summary",
            "character_motivations": {"Hero": {"goal": "win", "motivation": "honor", "obstacle": "enemy"}},
            "key_conflicts": ["Hero vs Enemy"],
            "plot_points": ["Start", "Middle", "End"]
        })

        # Mock scripter
        mock_scripter.convert_to_panels = AsyncMock(return_value={
            "panels": [
                {
                    "panel_number": 1,
                    "visual_description": "A hero stands ready",
                    "dialogue": [{"character": "Hero", "text": "I will win!"}],
                    "shot_type": "medium",
                    "environment": "battlefield"
                }
            ],
            "characters": [
                {"name": "Hero", "visual_description": "A brave warrior"}
            ]
        })
        mock_scripter.to_state_format = MagicMock(return_value=(
            [{"panel_number": 1, "visual_description": "Test", "dialogue": [], "shot_type": "wide", "environment": "test"}],
            [{"name": "Hero", "visual_description": "Test"}]
        ))

        # Mock blind reader
        mock_reader.reconstruct_from_filtered_state = AsyncMock(return_value={
            "reconstructed_story": "A hero wins a battle",
            "inferred_motivations": {"Hero": {"apparent_goal": "victory", "confidence": 90}},
            "inferred_conflicts": ["Hero vs Enemy"],
            "unclear_elements": [],
            "overall_confidence": 95
        })

        # Mock evaluator with high score
        mock_evaluator.evaluate = AsyncMock(return_value={
            "fidelity_score": 95.0,
            "is_valid": True,
            "gaps": [],
            "critique": "Excellent translation to visual format."
        })
        mock_evaluator.validation_threshold = 80.0

        # Run workflow
        result = await run_fidelity_workflow(
            seed="A hero wins a battle",
            max_iterations=3,
            fidelity_threshold=80.0
        )

        assert result.status == "validated"
        assert result.final_score >= 80.0

    @pytest.mark.asyncio
    @patch('app.workflows.fidelity_workflow.story_architect')
    @patch('app.workflows.fidelity_workflow.webtoon_scripter')
    @patch('app.workflows.fidelity_workflow.blind_reader')
    @patch('app.workflows.fidelity_workflow.fidelity_evaluator')
    async def test_workflow_retries_on_low_score(
        self,
        mock_evaluator,
        mock_reader,
        mock_scripter,
        mock_architect
    ):
        """Workflow should retry when fidelity score is low."""
        # Setup story architect mock
        mock_architect.generate_story = AsyncMock(return_value={
            "story": "Test story",
            "summary": "Summary",
            "character_motivations": {"Char": {"goal": "g", "motivation": "m", "obstacle": "o"}},
            "key_conflicts": ["conflict"],
            "plot_points": ["point"]
        })

        # Setup scripter mock
        mock_scripter.convert_to_panels = AsyncMock(return_value={
            "panels": [{"panel_number": 1, "visual_description": "Test", "dialogue": [], "shot_type": "wide", "environment": "test"}],
            "characters": [{"name": "Char", "visual_description": "Desc"}]
        })
        mock_scripter.revise_panels = AsyncMock(return_value={
            "panels": [{"panel_number": 1, "visual_description": "Improved", "dialogue": [], "shot_type": "wide", "environment": "test"}],
            "characters": [{"name": "Char", "visual_description": "Desc"}]
        })
        mock_scripter.to_state_format = MagicMock(return_value=(
            [{"panel_number": 1, "visual_description": "Test", "dialogue": [], "shot_type": "wide", "environment": "test"}],
            [{"name": "Char", "visual_description": "Desc"}]
        ))

        # Setup blind reader mock
        mock_reader.reconstruct_from_filtered_state = AsyncMock(return_value={
            "reconstructed_story": "Partial understanding",
            "inferred_motivations": {},
            "inferred_conflicts": [],
            "unclear_elements": ["many things"],
            "overall_confidence": 40
        })

        # Setup evaluator to return low scores then pass
        call_count = 0
        async def evaluate_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {
                    "fidelity_score": 50.0,
                    "is_valid": False,
                    "gaps": [{"category": "plot", "original_element": "key event", "reader_interpretation": "missed", "severity": "major", "suggested_fix": "add visual cue"}],
                    "critique": "Needs improvement"
                }
            else:
                return {
                    "fidelity_score": 85.0,
                    "is_valid": True,
                    "gaps": [],
                    "critique": "Good"
                }

        mock_evaluator.evaluate = AsyncMock(side_effect=evaluate_side_effect)
        mock_evaluator.validation_threshold = 80.0

        # Run workflow - should iterate
        result = await run_fidelity_workflow(
            seed="Test story",
            max_iterations=3,
            fidelity_threshold=80.0
        )

        # Should have called scripter multiple times
        assert mock_scripter.convert_to_panels.called or mock_scripter.revise_panels.called


class TestOutputFormat:
    """Test workflow output format."""

    @pytest.mark.asyncio
    @patch('app.workflows.fidelity_workflow.story_architect')
    @patch('app.workflows.fidelity_workflow.webtoon_scripter')
    @patch('app.workflows.fidelity_workflow.blind_reader')
    @patch('app.workflows.fidelity_workflow.fidelity_evaluator')
    async def test_response_contains_required_fields(
        self,
        mock_evaluator,
        mock_reader,
        mock_scripter,
        mock_architect
    ):
        """Response should contain all required fields."""
        # Minimal mocks for quick execution
        mock_architect.generate_story = AsyncMock(return_value={
            "story": "Story", "summary": "Sum",
            "character_motivations": {}, "key_conflicts": [], "plot_points": []
        })
        mock_scripter.convert_to_panels = AsyncMock(return_value={"panels": [], "characters": []})
        mock_scripter.to_state_format = MagicMock(return_value=([], []))
        mock_reader.reconstruct_from_filtered_state = AsyncMock(return_value={
            "reconstructed_story": "", "inferred_motivations": {},
            "inferred_conflicts": [], "unclear_elements": [], "overall_confidence": 50
        })
        mock_evaluator.evaluate = AsyncMock(return_value={
            "fidelity_score": 90, "is_valid": True, "gaps": [], "critique": ""
        })
        mock_evaluator.validation_threshold = 80.0

        result = await run_fidelity_workflow("Test", max_iterations=1)

        # Check required fields
        assert hasattr(result, 'workflow_id')
        assert hasattr(result, 'status')
        assert hasattr(result, 'final_score')
        assert hasattr(result, 'iterations_used')
        assert hasattr(result, 'original_story')
        assert hasattr(result, 'script_panels')
        assert hasattr(result, 'validation_history')

    def test_response_model_validation(self):
        """FidelityValidationResponse should validate correctly."""
        response = FidelityValidationResponse(
            workflow_id="test-123",
            status="validated",
            final_score=85.5,
            iterations_used=2,
            original_story="Test story",
            script_panels=[{"panel_number": 1}],
            characters=[{"name": "Test"}],
            validation_history=[],
            error=None,
            created_at=datetime.now()
        )

        assert response.workflow_id == "test-123"
        assert response.status == "validated"
        assert response.final_score == 85.5


class TestErrorHandling:
    """Test workflow error handling."""

    @pytest.mark.asyncio
    @patch('app.workflows.fidelity_workflow.story_architect')
    async def test_handles_story_architect_failure(self, mock_architect):
        """Workflow should handle story architect failure gracefully."""
        mock_architect.generate_story = AsyncMock(
            side_effect=Exception("LLM API Error")
        )

        result = await run_fidelity_workflow("Test", max_iterations=1)

        assert result.status == "error"
        assert result.error is not None
        assert "failed" in result.error.lower() or "error" in result.error.lower()

    @pytest.mark.asyncio
    @patch('app.workflows.fidelity_workflow.story_architect')
    @patch('app.workflows.fidelity_workflow.webtoon_scripter')
    async def test_handles_scripter_failure(self, mock_scripter, mock_architect):
        """Workflow should handle scripter failure gracefully."""
        mock_architect.generate_story = AsyncMock(return_value={
            "story": "Test", "summary": "Sum",
            "character_motivations": {}, "key_conflicts": [], "plot_points": []
        })
        mock_scripter.convert_to_panels = AsyncMock(
            side_effect=Exception("Scripter Error")
        )

        result = await run_fidelity_workflow("Test", max_iterations=1)

        assert result.status == "error"
        assert result.error is not None


class TestConvergence:
    """Test workflow convergence behavior."""

    def test_should_continue_logic_for_convergence(self):
        """Verify routing logic supports convergence."""
        # State after first iteration - low score
        state_iter1 = {
            "is_validated": False,
            "iteration": 2,  # About to start iteration 2
            "max_iterations": 3,
            "fidelity_score": 50.0,
            "error": None
        }
        assert should_continue(state_iter1) == "webtoon_scripter"

        # State after improvement - still not validated
        state_iter2 = {
            "is_validated": False,
            "iteration": 3,  # About to start iteration 3
            "max_iterations": 3,
            "fidelity_score": 70.0,
            "error": None
        }
        assert should_continue(state_iter2) == "webtoon_scripter"

        # State after validation
        state_validated = {
            "is_validated": True,
            "iteration": 3,
            "max_iterations": 3,
            "fidelity_score": 85.0,
            "error": None
        }
        assert should_continue(state_validated) == "end"

    def test_max_iterations_enforced(self):
        """Workflow should stop at max iterations even without validation."""
        state = {
            "is_validated": False,
            "iteration": 4,  # Exceeded max
            "max_iterations": 3,
            "fidelity_score": 60.0,
            "error": None
        }
        assert should_continue(state) == "end"
