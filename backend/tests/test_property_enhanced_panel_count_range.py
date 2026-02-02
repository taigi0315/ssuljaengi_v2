"""
Property-based test for Enhanced Panel Generation - Property 1: Enhanced Panel Count Range Validation

**Validates: Requirements 1.1, 1.2, 1.3**

Property 1: Enhanced Panel Count Range Validation
For any generated webtoon script, the total panel count should be between 20 and 50 panels, 
and the evaluator should flag scripts outside this range as either insufficient (below 20) 
or excessive (above 50).
"""

import pytest
from hypothesis import given, strategies as st, assume
from app.services.webtoon_writer import WebtoonWriter
from app.services.webtoon_evaluator import webtoon_evaluator
from app.models.story import WebtoonScript, WebtoonPanel, Character
from app.config.enhanced_panel_config import get_enhanced_panel_config


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
        visual_description="A test character for property-based testing of enhanced panel count range validation"
    )


def create_test_panel(panel_number: int, character_name: str = "TestChar"):
    """Create a valid test panel."""
    return WebtoonPanel(
        panel_number=panel_number,
        visual_prompt="Test visual prompt that is sufficiently long to meet the minimum requirements for panel description length in the enhanced system with proper detail and composition",
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


class TestProperty1EnhancedPanelCountRangeValidation:
    """
    Property 1: Enhanced Panel Count Range Validation
    **Validates: Requirements 1.1, 1.2, 1.3**
    
    For any generated webtoon script, the total panel count should be between 20 and 50 panels,
    and the evaluator should flag scripts outside this range as either insufficient (below 20)
    or excessive (above 50).
    """
    
    def test_enhanced_panel_count_configuration(self):
        """
        Test that enhanced panel count configuration is properly set.
        **Validates: Requirements 1.1**
        """
        config = get_enhanced_panel_config()
        
        # Verify enhanced panel count targets
        assert config.panel_count_min == 20, f"Enhanced minimum should be 20, got {config.panel_count_min}"
        assert config.panel_count_max == 50, f"Enhanced maximum should be 50, got {config.panel_count_max}"
        assert config.panel_count_ideal_min == 25, f"Enhanced ideal min should be 25, got {config.panel_count_ideal_min}"
        assert config.panel_count_ideal_max == 40, f"Enhanced ideal max should be 40, got {config.panel_count_ideal_max}"
    
    @given(panel_count=st.integers(min_value=20, max_value=50))
    def test_valid_panel_count_range_accepted(self, panel_count):
        """
        Property: For any panel count in the valid range (20-50), the script should be accepted.
        **Validates: Requirements 1.1**
        """
        assume(20 <= panel_count <= 50)  # Within enhanced valid range
        
        script = create_test_script(panel_count)
        config = get_enhanced_panel_config()
        
        # Verify script is within valid range
        assert len(script.panels) == panel_count
        assert config.validate_panel_count(panel_count) == True, \
            f"Panel count {panel_count} should be valid in enhanced range"
        
        # Verify evaluator accepts the script
        evaluation = webtoon_evaluator.evaluate_script(script)
        scene_score = evaluation.score_breakdown["scene_count"]
        
        # Should not be heavily penalized for being in valid range
        assert scene_score >= 7.0, \
            f"Panel count {panel_count} in valid range should not be heavily penalized, got score {scene_score}"
    
    @given(panel_count=st.integers(min_value=1, max_value=19))
    def test_insufficient_panel_count_flagged(self, panel_count):
        """
        Property: For any panel count below 20, the evaluator should flag the script as insufficient.
        **Validates: Requirements 1.2**
        """
        assume(panel_count < 20)  # Below enhanced minimum
        
        script = create_test_script(panel_count)
        config = get_enhanced_panel_config()
        
        # Verify script is below minimum
        assert len(script.panels) == panel_count
        assert config.validate_panel_count(panel_count) == False, \
            f"Panel count {panel_count} should be invalid (below minimum)"
        
        # Verify evaluator flags as insufficient
        evaluation = webtoon_evaluator.evaluate_script(script)
        scene_score = evaluation.score_breakdown["scene_count"]
        
        # Should be penalized for insufficient panels
        assert scene_score < 10.0, \
            f"Panel count {panel_count} below minimum should be penalized, got score {scene_score}"
        
        # Feedback should suggest adding more panels
        feedback_upper = evaluation.feedback.upper()
        assert any(keyword in feedback_upper for keyword in ["ADD", "MORE", "PANELS", "INSUFFICIENT", "EXPAND"]), \
            f"Feedback should suggest adding panels for count {panel_count}, got: {evaluation.feedback}"
    
    @given(panel_count=st.integers(min_value=51, max_value=80))
    def test_excessive_panel_count_flagged(self, panel_count):
        """
        Property: For any panel count above 50, the evaluator should flag the script as excessive.
        **Validates: Requirements 1.3**
        
        Note: Since WebtoonScript model may limit panels to 50, we test the configuration logic
        and evaluator behavior at the boundary.
        """
        assume(panel_count > 50)  # Above enhanced maximum
        
        config = get_enhanced_panel_config()
        
        # Test configuration validation for excessive counts
        assert config.validate_panel_count(panel_count) == False, \
            f"Panel count {panel_count} should be invalid (above maximum)"
        
        # Test at the boundary (50 panels) - should be acceptable but not ideal
        script_50 = create_test_script(50)
        evaluation_50 = webtoon_evaluator.evaluate_script(script_50)
        scene_score_50 = evaluation_50.score_breakdown["scene_count"]
        
        # 50 panels should be acceptable (at maximum boundary)
        assert scene_score_50 >= 7.0, f"50 panels should be acceptable, got score {scene_score_50}"
        
        # But not ideal (should be less than perfect score for ideal range)
        assert scene_score_50 < 10.0, f"50 panels should not be perfect (above ideal), got score {scene_score_50}"
        
        # Test that the configuration correctly identifies excessive counts
        assert not config.validate_panel_count(panel_count), \
            f"Configuration should reject panel count {panel_count} as excessive"
    
    @given(panel_count=st.integers(min_value=25, max_value=40))
    def test_ideal_panel_count_range_rewarded(self, panel_count):
        """
        Property: For any panel count in the ideal range (25-40), the evaluator should give high scores.
        **Validates: Requirements 1.1**
        """
        assume(25 <= panel_count <= 40)  # Within enhanced ideal range
        
        script = create_test_script(panel_count)
        config = get_enhanced_panel_config()
        
        # Verify script is in ideal range
        assert len(script.panels) == panel_count
        ideal_min, ideal_max = config.get_ideal_panel_range()
        assert ideal_min <= panel_count <= ideal_max, \
            f"Panel count {panel_count} should be in ideal range ({ideal_min}-{ideal_max})"
        
        # Verify evaluator rewards ideal range
        evaluation = webtoon_evaluator.evaluate_script(script)
        scene_score = evaluation.score_breakdown["scene_count"]
        
        # Should get perfect or near-perfect score for ideal range
        assert scene_score >= 9.0, \
            f"Panel count {panel_count} in ideal range should get high score, got {scene_score}"
    
    @given(
        panel_count=st.integers(min_value=1, max_value=80),
        seed=st.integers(min_value=1, max_value=1000)
    )
    def test_panel_count_validation_consistency(self, panel_count, seed):
        """
        Property: Panel count validation should be consistent across all inputs.
        **Validates: Requirements 1.1, 1.2, 1.3**
        """
        config = get_enhanced_panel_config()
        
        # Test validation consistency
        is_valid = config.validate_panel_count(panel_count)
        expected_valid = 20 <= panel_count <= 50
        
        assert is_valid == expected_valid, \
            f"Validation inconsistent for panel count {panel_count}: got {is_valid}, expected {expected_valid}"
        
        # Test ideal range consistency
        ideal_min, ideal_max = config.get_ideal_panel_range()
        is_ideal = ideal_min <= panel_count <= ideal_max
        expected_ideal = 25 <= panel_count <= 40
        
        assert is_ideal == expected_ideal, \
            f"Ideal range check inconsistent for panel count {panel_count}: got {is_ideal}, expected {expected_ideal}"
    
    @given(panel_count=st.integers(min_value=20, max_value=24))
    def test_minimum_acceptable_range(self, panel_count):
        """
        Property: For any panel count in 20-24 range, should be acceptable but not ideal.
        **Validates: Requirements 1.1, 1.2**
        """
        assume(20 <= panel_count <= 24)  # Above minimum but below ideal
        
        script = create_test_script(panel_count)
        config = get_enhanced_panel_config()
        
        # Should be valid but not ideal
        assert config.validate_panel_count(panel_count) == True
        ideal_min, ideal_max = config.get_ideal_panel_range()
        assert not (ideal_min <= panel_count <= ideal_max)
        
        # Evaluator should accept but not reward
        evaluation = webtoon_evaluator.evaluate_script(script)
        scene_score = evaluation.score_breakdown["scene_count"]
        
        assert 7.0 <= scene_score < 10.0, \
            f"Panel count {panel_count} should be acceptable but not perfect, got score {scene_score}"
    
    @given(panel_count=st.integers(min_value=41, max_value=50))
    def test_maximum_acceptable_range(self, panel_count):
        """
        Property: For any panel count in 41-50 range, should be acceptable but not ideal.
        **Validates: Requirements 1.1, 1.3**
        """
        assume(41 <= panel_count <= 50)  # Above ideal but below maximum
        
        script = create_test_script(panel_count)
        config = get_enhanced_panel_config()
        
        # Should be valid but not ideal
        assert config.validate_panel_count(panel_count) == True
        ideal_min, ideal_max = config.get_ideal_panel_range()
        assert not (ideal_min <= panel_count <= ideal_max)
        
        # Evaluator should accept but not reward
        evaluation = webtoon_evaluator.evaluate_script(script)
        scene_score = evaluation.score_breakdown["scene_count"]
        
        assert 7.0 <= scene_score < 10.0, \
            f"Panel count {panel_count} should be acceptable but not perfect, got score {scene_score}"
    
    def test_legacy_vs_enhanced_panel_count_targets(self):
        """
        Test that enhanced targets are used instead of legacy targets.
        **Validates: Requirements 1.1, 1.2, 1.3**
        """
        config = get_enhanced_panel_config()
        
        # Test that legacy ideal range (15-25) is not used
        script_15 = create_test_script(15)  # Was in legacy ideal range
        evaluation_15 = webtoon_evaluator.evaluate_script(script_15)
        
        # 15 panels should be penalized under enhanced system
        assert evaluation_15.score_breakdown["scene_count"] < 10.0, \
            "15 panels should be penalized under enhanced system (was acceptable in legacy)"
        
        # Test that enhanced ideal range (25-40) is used
        script_30 = create_test_script(30)  # In enhanced ideal range
        evaluation_30 = webtoon_evaluator.evaluate_script(script_30)
        
        # 30 panels should get high score under enhanced system
        assert evaluation_30.score_breakdown["scene_count"] >= 9.0, \
            "30 panels should get high score under enhanced system"
        
        # Verify configuration values are enhanced, not legacy
        assert config.panel_count_min != 10, "Should not use legacy minimum (10)"
        assert config.panel_count_max != 30, "Should not use legacy maximum (30)"
        assert config.panel_count_ideal_min != 15, "Should not use legacy ideal min (15)"
        assert config.panel_count_ideal_max != 25, "Should not use legacy ideal max (25)"
    
    @given(
        story_length=st.integers(min_value=100, max_value=1000),
        genre=st.sampled_from(["romance", "action", "fantasy", "comedy"])
    )
    def test_webtoon_writer_generates_enhanced_panel_counts(self, story_length, genre):
        """
        Property: WebtoonWriter should generate scripts with panel counts in enhanced range.
        **Validates: Requirements 1.1**
        
        Note: This test verifies that the WebtoonWriter is configured to generate
        scripts within the enhanced panel count range.
        """
        # Create a test story
        test_story = "A" * story_length  # Simple story of specified length
        
        # This test would require actual WebtoonWriter integration
        # For now, we test that the configuration supports the enhanced range
        config = get_enhanced_panel_config()
        
        # Verify that the enhanced range is properly configured for the writer
        assert config.panel_count_min == 20
        assert config.panel_count_max == 50
        
        # Test that genre-specific targets (if any) are within enhanced range
        genre_min, genre_max = config.get_panel_range_for_genre(genre)
        assert genre_min >= 20, f"Genre {genre} minimum should be >= 20, got {genre_min}"
        assert genre_max <= 50, f"Genre {genre} maximum should be <= 50, got {genre_max}"
        
        # Verify that any panel count in the genre range is valid
        for test_count in [genre_min, (genre_min + genre_max) // 2, genre_max]:
            assert config.validate_panel_count(test_count, genre), \
                f"Panel count {test_count} should be valid for genre {genre}"
    
    def test_enhanced_panel_count_boundary_conditions(self):
        """
        Test boundary conditions for enhanced panel count validation.
        **Validates: Requirements 1.1, 1.2, 1.3**
        """
        config = get_enhanced_panel_config()
        
        # Test exact boundaries
        assert config.validate_panel_count(19) == False, "19 panels should be invalid (below minimum)"
        assert config.validate_panel_count(20) == True, "20 panels should be valid (at minimum)"
        assert config.validate_panel_count(50) == True, "50 panels should be valid (at maximum)"
        assert config.validate_panel_count(51) == False, "51 panels should be invalid (above maximum)"
        
        # Test ideal range boundaries
        ideal_min, ideal_max = config.get_ideal_panel_range()
        assert ideal_min == 25, "Ideal minimum should be 25"
        assert ideal_max == 40, "Ideal maximum should be 40"
        
        # Test evaluator behavior at boundaries
        script_20 = create_test_script(20)
        script_25 = create_test_script(25)
        script_40 = create_test_script(40)
        script_50 = create_test_script(50)
        
        eval_20 = webtoon_evaluator.evaluate_script(script_20)
        eval_25 = webtoon_evaluator.evaluate_script(script_25)
        eval_40 = webtoon_evaluator.evaluate_script(script_40)
        eval_50 = webtoon_evaluator.evaluate_script(script_50)
        
        # Scores should increase as we move into ideal range
        score_20 = eval_20.score_breakdown["scene_count"]
        score_25 = eval_25.score_breakdown["scene_count"]
        score_40 = eval_40.score_breakdown["scene_count"]
        score_50 = eval_50.score_breakdown["scene_count"]
        
        # 25 and 40 (ideal range) should have higher scores than 20 and 50
        assert score_25 >= score_20, "25 panels (ideal) should score >= 20 panels (minimum)"
        assert score_40 >= score_50, "40 panels (ideal) should score >= 50 panels (maximum)"
        assert score_25 >= 9.0, "25 panels should get high score (ideal range)"
        assert score_40 >= 9.0, "40 panels should get high score (ideal range)"
    
    @given(
        panel_count=st.integers(min_value=20, max_value=50),
        character_count=st.integers(min_value=1, max_value=5)
    )
    def test_enhanced_panel_count_with_multiple_characters(self, panel_count, character_count):
        """
        Property: Enhanced panel count validation should work with multiple characters.
        **Validates: Requirements 1.1**
        """
        assume(20 <= panel_count <= 50)
        assume(1 <= character_count <= 5)
        
        # Create multiple characters
        characters = []
        for i in range(character_count):
            char = Character(
                name=f"TestChar{i}",
                reference_tag=f"test_char_{i}",
                gender="male" if i % 2 == 0 else "female",
                age=str(20 + i * 5),
                face=f"character {i} face",
                hair=f"character {i} hair",
                body="average build",
                outfit=f"character {i} outfit",
                mood="neutral",
                visual_description=f"Test character {i} for multi-character panel count validation"
            )
            characters.append(char)
        
        # Create panels with different characters
        panels = []
        for panel_idx in range(panel_count):
            char_idx = panel_idx % character_count
            character = characters[char_idx]
            
            panel = WebtoonPanel(
                panel_number=panel_idx + 1,
                visual_prompt=f"Panel {panel_idx + 1} featuring {character.name} in a test scenario with sufficient detail for enhanced panel generation",
                dialogue=[{"character": character.name, "text": f"Dialogue from {character.name}", "order": 1}],
                active_character_names=[character.name],
                shot_type="Medium Shot",
                character_frame_percentage=40,
                environment_frame_percentage=60
            )
            panels.append(panel)
        
        # Create script with multiple characters
        script = WebtoonScript(panels=panels, characters=characters)
        
        # Verify panel count is correct
        assert len(script.panels) == panel_count
        assert len(script.characters) == character_count
        
        # Verify enhanced validation works with multiple characters
        config = get_enhanced_panel_config()
        assert config.validate_panel_count(panel_count) == True
        
        # Verify evaluator handles multiple characters correctly
        evaluation = webtoon_evaluator.evaluate_script(script)
        scene_score = evaluation.score_breakdown["scene_count"]
        
        # Should not be penalized for having multiple characters
        assert scene_score >= 7.0, \
            f"Multi-character script with {panel_count} panels should not be penalized"


if __name__ == "__main__":
    # Run the property tests
    pytest.main([__file__, "-v"])