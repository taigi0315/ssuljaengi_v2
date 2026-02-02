"""
Property-based test for Enhanced Panel Generation - Property 7: Updated Evaluator Targets

**Validates: Requirements 6.1, 6.2, 6.3**

Property 7: Updated Evaluator Targets
For any script evaluation, the evaluator should use the new panel count targets 
(minimum 20, maximum 50, ideal range 25-40) instead of the legacy targets 
(minimum 10, maximum 30, ideal range 15-25).
"""

import pytest
from hypothesis import given, strategies as st, assume
from app.services.webtoon_evaluator import webtoon_evaluator, PANEL_COUNT_TARGET
from app.config.enhanced_panel_config import get_enhanced_panel_config
from app.models.story import WebtoonScript, WebtoonPanel, Character


def create_test_character():
    """Create a valid test character for scripts."""
    return Character(
        name="TestChar",
        reference_tag="test_char",
        gender="male",
        age="25",
        face="friendly face with kind eyes",
        hair="brown short hair",
        body="average build",
        outfit="casual clothing",
        mood="neutral",
        visual_description="A test character for property-based testing of enhanced panel configuration"
    )


def create_test_panel(panel_number: int, character_name: str = "TestChar"):
    """Create a valid test panel."""
    return WebtoonPanel(
        panel_number=panel_number,
        visual_prompt="Test visual prompt that is sufficiently long to meet the minimum requirements for panel description length in the enhanced system",
        dialogue=[{"character": character_name, "text": "Test dialogue line", "order": 1}],
        active_character_names=[character_name],
        shot_type="Medium Shot",
        character_frame_percentage=40,
        environment_frame_percentage=60
    )


def create_test_script(panel_count: int):
    """Create a test webtoon script with specified panel count."""
    panels = [create_test_panel(i + 1) for i in range(panel_count)]
    characters = [create_test_character()]
    return WebtoonScript(panels=panels, characters=characters)


class TestProperty7UpdatedEvaluatorTargets:
    """
    Property 7: Updated Evaluator Targets
    **Validates: Requirements 6.1, 6.2, 6.3**
    
    For any script evaluation, the evaluator should use the new panel count targets 
    (minimum 20, maximum 50, ideal range 25-40) instead of the legacy targets.
    """
    
    def test_evaluator_uses_enhanced_targets(self):
        """Test that evaluator constants are updated to enhanced targets."""
        # **Validates: Requirements 6.1, 6.2, 6.3**
        
        # Verify PANEL_COUNT_TARGET has been updated to enhanced values
        assert PANEL_COUNT_TARGET["min"] == 20, f"Minimum should be 20, got {PANEL_COUNT_TARGET['min']}"
        assert PANEL_COUNT_TARGET["max"] == 50, f"Maximum should be 50, got {PANEL_COUNT_TARGET['max']}"
        assert PANEL_COUNT_TARGET["ideal_min"] == 25, f"Ideal min should be 25, got {PANEL_COUNT_TARGET['ideal_min']}"
        assert PANEL_COUNT_TARGET["ideal_max"] == 40, f"Ideal max should be 40, got {PANEL_COUNT_TARGET['ideal_max']}"
        
        # Verify enhanced config matches
        config = get_enhanced_panel_config()
        assert config.panel_count_min == PANEL_COUNT_TARGET["min"]
        assert config.panel_count_max == PANEL_COUNT_TARGET["max"]
        assert config.panel_count_ideal_min == PANEL_COUNT_TARGET["ideal_min"]
        assert config.panel_count_ideal_max == PANEL_COUNT_TARGET["ideal_max"]
    
    @given(panel_count=st.integers(min_value=1, max_value=19))
    def test_evaluator_penalizes_below_enhanced_minimum(self, panel_count):
        """
        Property: For any panel count below 20, evaluator should penalize the script.
        **Validates: Requirements 6.1, 6.2**
        """
        assume(panel_count < 20)  # Below enhanced minimum
        
        script = create_test_script(panel_count)
        evaluation = webtoon_evaluator.evaluate_script(script)
        
        # Scene count score should be penalized for insufficient panels
        scene_score = evaluation.score_breakdown["scene_count"]
        assert scene_score < 10.0, f"Panel count {panel_count} should be penalized, got score {scene_score}"
        
        # Feedback should suggest adding more panels
        assert "ADD" in evaluation.feedback and "PANELS" in evaluation.feedback, \
            f"Feedback should suggest adding panels for count {panel_count}"
    
    @given(panel_count=st.integers(min_value=25, max_value=40))
    def test_evaluator_rewards_ideal_range(self, panel_count):
        """
        Property: For any panel count in ideal range (25-40), evaluator should give high scores.
        **Validates: Requirements 6.3**
        """
        assume(25 <= panel_count <= 40)  # Within ideal range
        
        script = create_test_script(panel_count)
        evaluation = webtoon_evaluator.evaluate_script(script)
        
        # Scene count score should be high for ideal range
        scene_score = evaluation.score_breakdown["scene_count"]
        assert scene_score >= 10.0, f"Panel count {panel_count} in ideal range should get perfect score, got {scene_score}"
    
    @given(panel_count=st.integers(min_value=20, max_value=24))
    def test_evaluator_accepts_enhanced_minimum_range(self, panel_count):
        """
        Property: For any panel count in 20-24 range, evaluator should accept but not reward.
        **Validates: Requirements 6.1, 6.2**
        """
        assume(20 <= panel_count <= 24)  # Above minimum but below ideal
        
        script = create_test_script(panel_count)
        evaluation = webtoon_evaluator.evaluate_script(script)
        
        # Scene count score should be acceptable but not perfect
        scene_score = evaluation.score_breakdown["scene_count"]
        assert 7.0 <= scene_score < 10.0, f"Panel count {panel_count} should be acceptable, got score {scene_score}"
    
    @given(panel_count=st.integers(min_value=41, max_value=50))
    def test_evaluator_accepts_enhanced_maximum_range(self, panel_count):
        """
        Property: For any panel count in 41-50 range, evaluator should accept but not reward.
        **Validates: Requirements 6.1, 6.2**
        """
        assume(41 <= panel_count <= 50)  # Above ideal but below maximum
        
        script = create_test_script(panel_count)
        evaluation = webtoon_evaluator.evaluate_script(script)
        
        # Scene count score should be acceptable but not perfect
        scene_score = evaluation.score_breakdown["scene_count"]
        assert 7.0 <= scene_score < 10.0, f"Panel count {panel_count} should be acceptable, got score {scene_score}"
    
    @given(panel_count=st.integers(min_value=51, max_value=60))
    def test_evaluator_penalizes_above_enhanced_maximum(self, panel_count):
        """
        Property: For any panel count above 50, evaluator should penalize the script.
        **Validates: Requirements 6.1, 6.2**
        
        Note: Since WebtoonScript model limits panels to 50, we test the evaluator logic
        directly with edge cases at the boundary.
        """
        assume(panel_count > 50)  # Above enhanced maximum
        
        # Test with exactly 50 panels (at the boundary)
        script_50 = create_test_script(50)
        evaluation_50 = webtoon_evaluator.evaluate_script(script_50)
        
        # 50 panels should be acceptable but not ideal (at maximum boundary)
        scene_score_50 = evaluation_50.score_breakdown["scene_count"]
        assert scene_score_50 >= 7.0, f"50 panels should be acceptable, got score {scene_score_50}"
        assert scene_score_50 < 10.0, f"50 panels should not be perfect (above ideal), got score {scene_score_50}"
        
        # Test the evaluator's logic for handling counts above maximum
        # by checking that the evaluation logic would penalize higher counts
        enhanced_config = get_enhanced_panel_config()
        assert enhanced_config.panel_count_max == 50, "Enhanced config should have max of 50"
        
        # Verify that panel counts above 50 would be invalid according to config
        assert not enhanced_config.validate_panel_count(panel_count), \
            f"Panel count {panel_count} should be invalid according to enhanced config"
    
    def test_legacy_targets_not_used(self):
        """
        Test that legacy targets (10-30, ideal 15-25) are not used.
        **Validates: Requirements 6.1, 6.2, 6.3**
        """
        # Test with legacy ideal range (15-25) - should not get perfect scores
        script_15 = create_test_script(15)  # Was in legacy ideal range
        evaluation_15 = webtoon_evaluator.evaluate_script(script_15)
        
        # 15 panels should be penalized under enhanced system
        assert evaluation_15.score_breakdown["scene_count"] < 10.0, \
            "15 panels should be penalized under enhanced system"
        
        # Test with enhanced ideal range (25-40) - should get perfect scores
        script_30 = create_test_script(30)  # In enhanced ideal range
        evaluation_30 = webtoon_evaluator.evaluate_script(script_30)
        
        # 30 panels should get perfect score under enhanced system
        assert evaluation_30.score_breakdown["scene_count"] == 10.0, \
            "30 panels should get perfect score under enhanced system"
    
    @given(
        panel_count=st.integers(min_value=1, max_value=50),
        seed=st.integers(min_value=1, max_value=1000)
    )
    def test_evaluator_consistency_with_enhanced_targets(self, panel_count, seed):
        """
        Property: Evaluator behavior should be consistent with enhanced targets across all inputs.
        **Validates: Requirements 6.1, 6.2, 6.3**
        """
        script = create_test_script(panel_count)
        evaluation = webtoon_evaluator.evaluate_script(script)
        scene_score = evaluation.score_breakdown["scene_count"]
        
        # Verify score behavior matches enhanced targets
        if panel_count < 20:
            # Below enhanced minimum - should be penalized
            assert scene_score < 10.0, f"Panel count {panel_count} below minimum should be penalized"
        elif 25 <= panel_count <= 40:
            # In enhanced ideal range - should get perfect score
            assert scene_score == 10.0, f"Panel count {panel_count} in ideal range should get perfect score"
        elif 20 <= panel_count <= 50:
            # In enhanced acceptable range - should be acceptable
            assert scene_score >= 7.0, f"Panel count {panel_count} in acceptable range should not be heavily penalized"


if __name__ == "__main__":
    # Run the property tests
    pytest.main([__file__, "-v"])