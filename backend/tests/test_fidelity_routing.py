"""
Tests for fidelity workflow routing logic.

These tests verify the conditional routing behavior:
- When to continue the validation loop
- When to exit (validated or max iterations)
"""

import pytest
from app.workflows.fidelity_workflow import should_continue
from app.models.fidelity_state import WebtoonFidelityState


class TestShouldContinue:
    """Test the should_continue routing function."""

    @pytest.fixture
    def base_state(self) -> WebtoonFidelityState:
        """Create a base state for testing."""
        return {
            "seed": "test",
            "original_story": "test story",
            "story_summary": "summary",
            "character_motivations": {},
            "key_conflicts": [],
            "plot_points": [],
            "script_panels": [],
            "characters": [],
            "reconstructed_story": "",
            "inferred_motivations": {},
            "inferred_conflicts": [],
            "unclear_elements": [],
            "reader_confidence": 0.5,
            "fidelity_score": 50.0,
            "information_gaps": [],
            "critique": "Some critique",
            "iteration": 1,
            "max_iterations": 3,
            "is_validated": False,
            "current_step": "evaluator_complete",
            "error": None
        }

    def test_returns_end_when_validated(self, base_state):
        """Pass immediately when is_validated is True."""
        base_state["is_validated"] = True
        base_state["fidelity_score"] = 90.0
        result = should_continue(base_state)
        assert result == "end"

    def test_returns_end_when_max_iterations_reached(self, base_state):
        """Stop when iteration > max_iterations."""
        base_state["is_validated"] = False
        base_state["iteration"] = 4  # > max_iterations (3)
        base_state["max_iterations"] = 3
        result = should_continue(base_state)
        assert result == "end"

    def test_returns_end_when_at_max_iterations(self, base_state):
        """Stop when iteration == max_iterations + 1."""
        base_state["is_validated"] = False
        base_state["iteration"] = 4
        base_state["max_iterations"] = 3
        result = should_continue(base_state)
        assert result == "end"

    def test_returns_end_on_error(self, base_state):
        """Stop when there's an error."""
        base_state["error"] = "Something went wrong"
        result = should_continue(base_state)
        assert result == "end"

    def test_returns_scripter_when_not_validated_with_iterations(self, base_state):
        """Continue loop when validation failed and iterations remain."""
        base_state["is_validated"] = False
        base_state["iteration"] = 2
        base_state["max_iterations"] = 3
        result = should_continue(base_state)
        assert result == "webtoon_scripter"

    def test_returns_scripter_on_first_iteration(self, base_state):
        """Continue loop on first failed iteration."""
        base_state["is_validated"] = False
        base_state["iteration"] = 1
        base_state["max_iterations"] = 3
        result = should_continue(base_state)
        assert result == "webtoon_scripter"

    def test_validation_takes_priority_over_iteration(self, base_state):
        """If validated, exit even if iterations remain."""
        base_state["is_validated"] = True
        base_state["iteration"] = 1
        base_state["max_iterations"] = 5
        result = should_continue(base_state)
        assert result == "end"

    def test_error_takes_priority_over_validation(self, base_state):
        """If error exists, exit even if validated."""
        base_state["is_validated"] = True
        base_state["error"] = "Some error"
        result = should_continue(base_state)
        assert result == "end"

    def test_error_takes_priority_over_iterations(self, base_state):
        """If error exists, exit even if iterations remain."""
        base_state["is_validated"] = False
        base_state["iteration"] = 1
        base_state["max_iterations"] = 5
        base_state["error"] = "Some error"
        result = should_continue(base_state)
        assert result == "end"


class TestIterationCounting:
    """Test iteration counter behavior."""

    @pytest.fixture
    def state(self) -> WebtoonFidelityState:
        """Create a state for iteration testing."""
        return {
            "seed": "test",
            "original_story": "test",
            "story_summary": "summary",
            "character_motivations": {},
            "key_conflicts": [],
            "plot_points": [],
            "script_panels": [],
            "characters": [],
            "reconstructed_story": "",
            "inferred_motivations": {},
            "inferred_conflicts": [],
            "unclear_elements": [],
            "reader_confidence": 0.5,
            "fidelity_score": 50.0,
            "information_gaps": [],
            "critique": "critique",
            "iteration": 1,
            "max_iterations": 3,
            "is_validated": False,
            "current_step": "test",
            "error": None
        }

    def test_continues_at_iteration_1(self, state):
        """First iteration should continue."""
        state["iteration"] = 1
        assert should_continue(state) == "webtoon_scripter"

    def test_continues_at_iteration_2(self, state):
        """Second iteration should continue."""
        state["iteration"] = 2
        assert should_continue(state) == "webtoon_scripter"

    def test_continues_at_iteration_3(self, state):
        """Third iteration should continue (max=3, iteration=3 means we're starting 3rd)."""
        state["iteration"] = 3
        assert should_continue(state) == "webtoon_scripter"

    def test_stops_after_max_iterations(self, state):
        """Stop when iteration exceeds max."""
        state["iteration"] = 4
        state["max_iterations"] = 3
        assert should_continue(state) == "end"

    def test_handles_custom_max_iterations(self, state):
        """Respect custom max_iterations setting."""
        state["max_iterations"] = 5
        state["iteration"] = 4
        assert should_continue(state) == "webtoon_scripter"

        state["iteration"] = 6
        assert should_continue(state) == "end"


class TestEdgeCases:
    """Test edge cases in routing logic."""

    @pytest.fixture
    def state(self) -> WebtoonFidelityState:
        """Create a minimal state."""
        return {
            "seed": "test",
            "original_story": "test",
            "story_summary": "summary",
            "character_motivations": {},
            "key_conflicts": [],
            "plot_points": [],
            "script_panels": [],
            "characters": [],
            "reconstructed_story": "",
            "inferred_motivations": {},
            "inferred_conflicts": [],
            "unclear_elements": [],
            "reader_confidence": 0.5,
            "fidelity_score": 0.0,
            "information_gaps": [],
            "critique": None,
            "iteration": 1,
            "max_iterations": 3,
            "is_validated": False,
            "current_step": "test",
            "error": None
        }

    def test_handles_zero_score(self, state):
        """Handle fidelity score of 0."""
        state["fidelity_score"] = 0.0
        state["is_validated"] = False
        assert should_continue(state) == "webtoon_scripter"

    def test_handles_perfect_score(self, state):
        """Handle fidelity score of 100."""
        state["fidelity_score"] = 100.0
        state["is_validated"] = True
        assert should_continue(state) == "end"

    def test_handles_boundary_score(self, state):
        """Handle score exactly at threshold (80)."""
        state["fidelity_score"] = 80.0
        state["is_validated"] = True  # Should be validated at 80
        assert should_continue(state) == "end"

    def test_handles_just_below_threshold(self, state):
        """Handle score just below threshold."""
        state["fidelity_score"] = 79.9
        state["is_validated"] = False
        assert should_continue(state) == "webtoon_scripter"

    def test_handles_empty_error_string(self, state):
        """Empty string error should not trigger exit."""
        state["error"] = ""  # Empty string, not None
        # Empty string is falsy, so should continue
        assert should_continue(state) == "webtoon_scripter"

    def test_handles_none_error(self, state):
        """None error should not trigger exit."""
        state["error"] = None
        assert should_continue(state) == "webtoon_scripter"

    def test_handles_whitespace_error(self, state):
        """Whitespace-only error triggers exit (truthy string)."""
        state["error"] = "   "  # Whitespace is still truthy
        assert should_continue(state) == "end"
