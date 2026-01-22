"""
Unit tests for the enhanced WebtoonEvaluator (v2.0.0).

Tests the new shot variety and visual dynamism scoring.
"""

import pytest
from app.models.story import WebtoonScript, WebtoonPanel, Character
from app.services.webtoon_evaluator import (
    WebtoonEvaluator,
    webtoon_evaluator,
    EVALUATION_WEIGHTS
)


@pytest.fixture
def sample_character():
    """Sample character for testing."""
    return Character(
        name="Ji-hoon",
        reference_tag="Ji-hoon(20s, athletic)",
        gender="male",
        age="25",
        visual_description="A young man with sharp features"
    )


@pytest.fixture
def sample_panel_medium():
    """Sample panel with medium shot."""
    return WebtoonPanel(
        panel_number=1,
        shot_type="Medium Shot",
        active_character_names=["Ji-hoon"],
        visual_prompt="A young man standing in a room looking thoughtful, medium framing, natural lighting, modern interior setting with subtle details",
        story_beat="Ji-hoon contemplates",
        character_frame_percentage=45,
        dialogue=[{"character": "Ji-hoon", "text": "I need to think about this."}]
    )


@pytest.fixture
def sample_panel_close():
    """Sample panel with close-up."""
    return WebtoonPanel(
        panel_number=2,
        shot_type="Close-up",
        active_character_names=["Ji-hoon"],
        visual_prompt="Close-up of Ji-hoon's face showing determination, dramatic lighting, intense expression, shallow depth of field",
        story_beat="Ji-hoon's determination",
        character_frame_percentage=80,
        dialogue=[{"character": "Ji-hoon", "text": "I've made my decision."}]
    )


@pytest.fixture
def sample_panel_wide():
    """Sample panel with wide shot."""
    return WebtoonPanel(
        panel_number=3,
        shot_type="Wide Shot",
        active_character_names=["Ji-hoon"],
        visual_prompt="Wide establishing shot of Ji-hoon in the city square, small figure against urban backdrop, afternoon lighting",
        story_beat="Ji-hoon in the city",
        character_frame_percentage=20,
        dialogue=[{"character": "Ji-hoon", "text": "This city never changes."}]
    )


@pytest.fixture
def sample_panel_detail():
    """Sample panel with detail shot."""
    return WebtoonPanel(
        panel_number=4,
        shot_type="Detail",
        active_character_names=[],
        visual_prompt="Close detail shot of a crumpled letter on the table, dramatic side lighting, shallow focus, emotional atmosphere",
        story_beat="The letter",
        character_frame_percentage=0,
        dialogue=[]
    )


@pytest.fixture
def varied_script(sample_character, sample_panel_medium, sample_panel_close, sample_panel_wide, sample_panel_detail):
    """Script with good shot variety."""
    # Create 8 panels with variety
    panels = [
        sample_panel_wide,  # wide - 20%
        sample_panel_medium,  # medium - 45%
        sample_panel_close,  # close - 80%
        sample_panel_detail,  # detail - 0%
    ]
    # Duplicate to get 8 panels
    for i, p in enumerate(panels.copy()):
        new_panel = WebtoonPanel(
            panel_number=i + 5,
            shot_type=p.shot_type,
            active_character_names=p.active_character_names,
            visual_prompt=p.visual_prompt,
            story_beat=p.story_beat,
            character_frame_percentage=p.character_frame_percentage,
            dialogue=p.dialogue
        )
        panels.append(new_panel)

    return WebtoonScript(characters=[sample_character], panels=panels)


@pytest.fixture
def monotonous_script(sample_character):
    """Script with no shot variety - all medium shots."""
    panels = [
        WebtoonPanel(
            panel_number=i + 1,
            shot_type="Medium Shot",
            active_character_names=["Ji-hoon"],
            visual_prompt="Medium shot of Ji-hoon in a room with standard composition and neutral lighting throughout",
            story_beat=f"Scene {i + 1}",
            character_frame_percentage=45,
            dialogue=[{"character": "Ji-hoon", "text": f"Line {i + 1}"}]
        )
        for i in range(8)
    ]
    return WebtoonScript(characters=[sample_character], panels=panels)


class TestEvaluationWeights:
    """Test evaluation weight configuration."""

    def test_weights_sum_to_one(self):
        """Weights should sum to 1.0."""
        total = sum(EVALUATION_WEIGHTS.values())
        assert abs(total - 1.0) < 0.001, f"Weights sum to {total}, expected 1.0"

    def test_new_metrics_included(self):
        """v2.0.0 metrics should be in weights."""
        assert "shot_variety" in EVALUATION_WEIGHTS
        assert "visual_dynamism" in EVALUATION_WEIGHTS

    def test_shot_variety_weight(self):
        """Shot variety should have 20% weight."""
        assert EVALUATION_WEIGHTS["shot_variety"] == 0.20

    def test_visual_dynamism_weight(self):
        """Visual dynamism should have 10% weight."""
        assert EVALUATION_WEIGHTS["visual_dynamism"] == 0.10


class TestShotTypeNormalization:
    """Test shot type normalization."""

    def test_close_up_variations(self):
        """Various close-up formats should normalize to 'close'."""
        evaluator = WebtoonEvaluator()
        assert evaluator._normalize_shot_type("Close-up") == "close"
        assert evaluator._normalize_shot_type("close up") == "close"
        assert evaluator._normalize_shot_type("CLOSEUP") == "close"
        assert evaluator._normalize_shot_type("extreme close-up") == "close"
        assert evaluator._normalize_shot_type("close_up") == "close"

    def test_medium_variations(self):
        """Various medium shot formats should normalize to 'medium'."""
        evaluator = WebtoonEvaluator()
        assert evaluator._normalize_shot_type("Medium Shot") == "medium"
        assert evaluator._normalize_shot_type("medium") == "medium"
        assert evaluator._normalize_shot_type("medium close-up") == "medium"

    def test_wide_variations(self):
        """Various wide shot formats should normalize to 'wide'."""
        evaluator = WebtoonEvaluator()
        assert evaluator._normalize_shot_type("Wide Shot") == "wide"
        assert evaluator._normalize_shot_type("wide") == "wide"
        assert evaluator._normalize_shot_type("establishing shot") == "wide"
        assert evaluator._normalize_shot_type("extreme_wide") == "wide"

    def test_unknown_type(self):
        """Unknown types should return 'other'."""
        evaluator = WebtoonEvaluator()
        assert evaluator._normalize_shot_type("random type") == "other"
        assert evaluator._normalize_shot_type("") == "unknown"
        assert evaluator._normalize_shot_type(None) == "unknown"


class TestScoreShotVariety:
    """Test shot variety scoring."""

    def test_varied_script_high_score(self, varied_script):
        """Script with good variety should score high."""
        evaluator = WebtoonEvaluator()
        score, issues, feedback = evaluator.score_shot_variety(varied_script)

        assert score >= 7.0, f"Expected high score for varied script, got {score}"
        assert len(issues) < 3, "Varied script should have few issues"

    def test_monotonous_script_low_score(self, monotonous_script):
        """Script with no variety should score low."""
        evaluator = WebtoonEvaluator()
        score, issues, feedback = evaluator.score_shot_variety(monotonous_script)

        assert score < 7.0, f"Expected low score for monotonous script, got {score}"
        assert len(issues) > 0, "Should have variety issues"
        assert any("variety" in issue.lower() for issue in issues), "Should mention variety"

    def test_all_same_shot_type_penalized(self, sample_character):
        """100% same shot type should be heavily penalized."""
        panels = [
            WebtoonPanel(
                panel_number=i + 1,
                shot_type="Medium Shot",
                active_character_names=["Ji-hoon"],
                visual_prompt="Medium shot scene with adequate detail for generation",
                character_frame_percentage=45,
                dialogue=[{"character": "Ji-hoon", "text": "Text"}]
            )
            for i in range(10)
        ]
        script = WebtoonScript(characters=[sample_character], panels=panels)

        evaluator = WebtoonEvaluator()
        score, issues, feedback = evaluator.score_shot_variety(script)

        assert score < 6.0, f"100% same type should score low, got {score}"

    def test_missing_close_ups_flagged(self, sample_character):
        """Script without close-ups should be flagged."""
        # All wide shots
        panels = [
            WebtoonPanel(
                panel_number=i + 1,
                shot_type="Wide Shot",
                active_character_names=["Ji-hoon"],
                visual_prompt="Wide establishing shot with environment and character",
                character_frame_percentage=20,
                dialogue=[{"character": "Ji-hoon", "text": "Text"}]
            )
            for i in range(8)
        ]
        script = WebtoonScript(characters=[sample_character], panels=panels)

        evaluator = WebtoonEvaluator()
        score, issues, feedback = evaluator.score_shot_variety(script)

        assert any("close" in issue.lower() for issue in issues), "Should flag missing close-ups"

    def test_consecutive_same_type_penalized(self, sample_character):
        """3+ consecutive same shot types should be penalized."""
        panels = [
            WebtoonPanel(
                panel_number=1,
                shot_type="Wide Shot",
                visual_prompt="Wide shot scene one",
                character_frame_percentage=20,
                dialogue=[{"character": "Ji-hoon", "text": "A"}]
            ),
            WebtoonPanel(
                panel_number=2,
                shot_type="Medium Shot",
                visual_prompt="Medium shot scene two",
                character_frame_percentage=45,
                dialogue=[{"character": "Ji-hoon", "text": "B"}]
            ),
            WebtoonPanel(
                panel_number=3,
                shot_type="Medium Shot",
                visual_prompt="Medium shot scene three",
                character_frame_percentage=45,
                dialogue=[{"character": "Ji-hoon", "text": "C"}]
            ),
            WebtoonPanel(
                panel_number=4,
                shot_type="Medium Shot",
                visual_prompt="Medium shot scene four",
                character_frame_percentage=45,
                dialogue=[{"character": "Ji-hoon", "text": "D"}]
            ),
            WebtoonPanel(
                panel_number=5,
                shot_type="Close-up",
                visual_prompt="Close up scene five",
                character_frame_percentage=80,
                dialogue=[{"character": "Ji-hoon", "text": "E"}]
            ),
        ]
        script = WebtoonScript(characters=[sample_character], panels=panels)

        evaluator = WebtoonEvaluator()
        score, issues, feedback = evaluator.score_shot_variety(script)

        assert any("consecutive" in issue.lower() for issue in issues), "Should flag consecutive same types"


class TestScoreVisualDynamism:
    """Test visual dynamism scoring."""

    def test_varied_framing_high_score(self, varied_script):
        """Script with varied frame percentages should score high."""
        evaluator = WebtoonEvaluator()
        score, issues, feedback = evaluator.score_visual_dynamism(varied_script)

        assert score >= 7.0, f"Expected high score for dynamic framing, got {score}"

    def test_uniform_framing_low_score(self, monotonous_script):
        """Script with uniform framing should score low."""
        evaluator = WebtoonEvaluator()
        score, issues, feedback = evaluator.score_visual_dynamism(monotonous_script)

        assert score < 8.0, f"Expected lower score for uniform framing, got {score}"
        # Should flag the uniformity
        assert any("uniform" in issue.lower() or "variance" in issue.lower() for issue in issues)

    def test_missing_close_framing_flagged(self, sample_character):
        """Script without close framing should be flagged."""
        # All wide/medium framing
        panels = [
            WebtoonPanel(
                panel_number=i + 1,
                shot_type="Wide Shot" if i % 2 == 0 else "Medium Shot",
                visual_prompt="Scene with moderate framing composition",
                character_frame_percentage=30 if i % 2 == 0 else 45,
                dialogue=[{"character": "Ji-hoon", "text": "Text"}]
            )
            for i in range(8)
        ]
        script = WebtoonScript(characters=[sample_character], panels=panels)

        evaluator = WebtoonEvaluator()
        score, issues, feedback = evaluator.score_visual_dynamism(script)

        assert any("close" in fb.lower() or "70%" in fb for fb in feedback), "Should suggest close framing"

    def test_missing_wide_framing_flagged(self, sample_character):
        """Script without wide framing should be flagged."""
        # All close framing
        panels = [
            WebtoonPanel(
                panel_number=i + 1,
                shot_type="Close-up",
                visual_prompt="Close up shot with character prominent in frame",
                character_frame_percentage=80,
                dialogue=[{"character": "Ji-hoon", "text": "Text"}]
            )
            for i in range(8)
        ]
        script = WebtoonScript(characters=[sample_character], panels=panels)

        evaluator = WebtoonEvaluator()
        score, issues, feedback = evaluator.score_visual_dynamism(script)

        assert any("wide" in fb.lower() or "30%" in fb for fb in feedback), "Should suggest wide framing"


class TestEvaluateScript:
    """Test full script evaluation with new metrics."""

    def test_evaluation_includes_new_scores(self, varied_script):
        """Evaluation should include shot_variety and visual_dynamism."""
        evaluator = WebtoonEvaluator()
        result = evaluator.evaluate_script(varied_script)

        assert result.score_breakdown is not None
        assert "shot_variety" in result.score_breakdown
        assert "visual_dynamism" in result.score_breakdown

    def test_varied_script_scores_well(self, varied_script):
        """A well-varied script should score above threshold."""
        evaluator = WebtoonEvaluator()
        result = evaluator.evaluate_script(varied_script)

        # Should be valid (above 7.0 threshold by default)
        assert result.score >= 6.0, f"Varied script should score well, got {result.score}"
        assert result.score_breakdown["shot_variety"] >= 6.0

    def test_monotonous_script_penalized(self, monotonous_script):
        """A monotonous script should be penalized by new metrics."""
        evaluator = WebtoonEvaluator()
        result = evaluator.evaluate_script(monotonous_script)

        # shot_variety should be low
        assert result.score_breakdown["shot_variety"] < 7.0
        # Should have variety-related issues
        assert any("variety" in issue.lower() or "shot" in issue.lower() for issue in result.issues)

    def test_feedback_includes_variety_suggestions(self, monotonous_script):
        """Feedback should include variety suggestions for monotonous script."""
        evaluator = WebtoonEvaluator()
        result = evaluator.evaluate_script(monotonous_script)

        assert "SHOT VARIETY" in result.feedback or "close" in result.feedback.lower()


class TestGlobalInstance:
    """Test the global evaluator instance."""

    def test_global_instance_exists(self):
        """Global instance should be available."""
        assert webtoon_evaluator is not None
        assert isinstance(webtoon_evaluator, WebtoonEvaluator)

    def test_global_instance_has_new_methods(self):
        """Global instance should have v2.0.0 methods."""
        assert hasattr(webtoon_evaluator, "score_shot_variety")
        assert hasattr(webtoon_evaluator, "score_visual_dynamism")
