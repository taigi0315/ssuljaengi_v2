"""
Property-based test for Enhanced Panel Generation - Property 3: Scene Panel Count Constraints

**Validates: Requirements 2.1, 2.4**

Property 3: Scene Panel Count Constraints
For any generated webtoon script, each scene should contain between 1 and 8 panels, 
and the sum of all scene panel counts should equal the total panel count within the target range.
"""

import pytest
from hypothesis import given, strategies as st, assume
from app.services.webtoon_writer import WebtoonWriter
from app.services.webtoon_evaluator import webtoon_evaluator
from app.models.story import WebtoonScript, WebtoonPanel, Character
from app.config.enhanced_panel_config import get_enhanced_panel_config
from typing import List, Dict


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
        visual_description="A test character for property-based testing of scene panel constraints"
    )


def create_test_panel(panel_number: int, scene_number: int, character_name: str = "TestChar"):
    """Create a valid test panel for a specific scene."""
    return WebtoonPanel(
        panel_number=panel_number,
        visual_prompt=f"Scene {scene_number} panel {panel_number}: Detailed visual composition with proper framing, lighting, and environmental context for enhanced panel generation testing",
        dialogue=[{"character": character_name, "text": f"Scene {scene_number} dialogue for panel {panel_number}", "order": 1}],
        active_character_names=[character_name],
        shot_type="Medium Shot",
        character_frame_percentage=40,
        environment_frame_percentage=60
    )


def create_script_with_scene_constraints(total_panels: int, scene_panel_counts: List[int]):
    """Create a test webtoon script with specified scene panel distribution."""
    # Verify scene panel counts sum to total
    if sum(scene_panel_counts) != total_panels:
        raise ValueError(f"Scene panel counts {scene_panel_counts} don't sum to {total_panels}")
    
    panels = []
    panel_number = 1
    
    for scene_idx, scene_panel_count in enumerate(scene_panel_counts, 1):
        for panel_in_scene in range(scene_panel_count):
            panel = create_test_panel(panel_number, scene_idx)
            panels.append(panel)
            panel_number += 1
    
    characters = [create_test_character()]
    return WebtoonScript(panels=panels, characters=characters)


def generate_valid_scene_distribution(total_panels: int, max_scenes: int = 25) -> List[int]:
    """Generate a valid scene panel distribution for testing."""
    if total_panels < 1:
        return []
    
    # Start with minimum 1 panel per scene
    min_scenes = max(1, total_panels // 8)  # At most 8 panels per scene
    max_scenes = min(max_scenes, total_panels)  # Can't have more scenes than panels
    
    # Choose number of scenes
    num_scenes = min(max_scenes, max(min_scenes, total_panels // 4))  # Average 4 panels per scene
    
    # Distribute panels across scenes
    scene_counts = [1] * num_scenes  # Start with 1 panel per scene
    remaining_panels = total_panels - num_scenes
    
    # Distribute remaining panels, respecting 8-panel limit per scene
    scene_idx = 0
    while remaining_panels > 0:
        if scene_counts[scene_idx] < 8:  # Don't exceed 8 panels per scene
            scene_counts[scene_idx] += 1
            remaining_panels -= 1
        scene_idx = (scene_idx + 1) % num_scenes
    
    return scene_counts


class TestProperty3ScenePanelCountConstraints:
    """
    Property 3: Scene Panel Count Constraints
    **Validates: Requirements 2.1, 2.4**
    
    For any generated webtoon script, each scene should contain between 1 and 8 panels,
    and the sum of all scene panel counts should equal the total panel count within the target range.
    """
    
    def test_enhanced_scene_panel_limits(self):
        """
        Test that enhanced scene panel limits are properly configured.
        **Validates: Requirements 2.1**
        """
        config = get_enhanced_panel_config()
        
        # Verify enhanced scene panel limits
        assert hasattr(config, 'max_panels_per_scene'), "Config should have max_panels_per_scene"
        assert config.max_panels_per_scene == 8, f"Max panels per scene should be 8, got {config.max_panels_per_scene}"
        
        # Verify minimum is still 1
        assert hasattr(config, 'min_panels_per_scene'), "Config should have min_panels_per_scene"
        assert config.min_panels_per_scene == 1, f"Min panels per scene should be 1, got {config.min_panels_per_scene}"
    
    @given(panels_per_scene=st.integers(min_value=1, max_value=8))
    def test_valid_scene_panel_counts_accepted(self, panels_per_scene):
        """
        Property: For any scene with 1-8 panels, the scene should be valid.
        **Validates: Requirements 2.1**
        """
        assume(1 <= panels_per_scene <= 8)  # Within enhanced scene limits
        
        config = get_enhanced_panel_config()
        
        # Create a full enhanced script (25 panels) with one scene having the specified count
        total_panels = 25  # Minimum enhanced panel count
        remaining_panels = total_panels - panels_per_scene
        
        # Create scene distribution with the test scene plus additional scenes
        scene_counts = [panels_per_scene]
        if remaining_panels > 0:
            additional_scenes = generate_valid_scene_distribution(remaining_panels, max_scenes=10)
            scene_counts.extend(additional_scenes)
        
        script = create_script_with_scene_constraints(total_panels, scene_counts)
        
        # Verify script structure
        assert len(script.panels) == total_panels
        
        # Verify scene panel count is within limits
        assert config.validate_scene_panel_count(panels_per_scene) == True, \
            f"Scene with {panels_per_scene} panels should be valid"
        
        # Verify the first scene has the correct panel count
        scene_1_panels = [p for p in script.panels if "Scene 1" in p.visual_prompt]
        assert len(scene_1_panels) == panels_per_scene, \
            f"First scene should have {panels_per_scene} panels, got {len(scene_1_panels)}"
    
    @given(panels_per_scene=st.integers(min_value=9, max_value=15))
    def test_excessive_scene_panel_counts_flagged(self, panels_per_scene):
        """
        Property: For any scene with more than 8 panels, the scene should be flagged as invalid.
        **Validates: Requirements 2.1**
        """
        assume(panels_per_scene > 8)  # Above enhanced scene limit
        
        config = get_enhanced_panel_config()
        
        # Test that configuration rejects excessive scene panel counts
        assert config.validate_scene_panel_count(panels_per_scene) == False, \
            f"Scene with {panels_per_scene} panels should be invalid (exceeds 8-panel limit)"
    
    @given(
        total_panels=st.integers(min_value=20, max_value=50),
        seed=st.integers(min_value=1, max_value=1000)
    )
    def test_scene_panel_sum_equals_total(self, total_panels, seed):
        """
        Property: For any valid script, the sum of scene panel counts should equal total panels.
        **Validates: Requirements 2.4**
        """
        assume(20 <= total_panels <= 50)  # Within enhanced panel range
        
        # Generate valid scene distribution
        scene_counts = generate_valid_scene_distribution(total_panels)
        
        # Verify each scene is within limits
        for i, count in enumerate(scene_counts):
            assert 1 <= count <= 8, f"Scene {i+1} has {count} panels, should be 1-8"
        
        # Verify sum equals total
        assert sum(scene_counts) == total_panels, \
            f"Scene panel counts {scene_counts} should sum to {total_panels}, got {sum(scene_counts)}"
        
        # Create script with this distribution
        script = create_script_with_scene_constraints(total_panels, scene_counts)
        
        # Verify script has correct total panels
        assert len(script.panels) == total_panels
        
        # Verify evaluator accepts properly distributed script
        evaluation = webtoon_evaluator.evaluate_script(script)
        
        # Should not be penalized for proper scene distribution
        assert evaluation.score >= 5.0, \
            f"Properly distributed script should not be heavily penalized"
    
    @given(
        total_panels=st.integers(min_value=25, max_value=40),
        max_scenes=st.integers(min_value=3, max_value=15)
    )
    def test_flexible_scene_structure_support(self, total_panels, max_scenes):
        """
        Property: For any valid panel count, flexible scene structures should be supported.
        **Validates: Requirements 2.1, 2.4**
        """
        assume(25 <= total_panels <= 40)  # Ideal panel range
        assume(3 <= max_scenes <= 15)
        
        # Generate scene distribution with specified constraints
        scene_counts = generate_valid_scene_distribution(total_panels, max_scenes)
        
        # Verify all constraints are met
        assert len(scene_counts) <= max_scenes, f"Should not exceed {max_scenes} scenes"
        assert all(1 <= count <= 8 for count in scene_counts), "All scenes should have 1-8 panels"
        assert sum(scene_counts) == total_panels, "Scene counts should sum to total panels"
        
        # Create and validate script
        script = create_script_with_scene_constraints(total_panels, scene_counts)
        config = get_enhanced_panel_config()
        
        # Verify each scene panel count is valid
        for count in scene_counts:
            assert config.validate_scene_panel_count(count) == True, \
                f"Scene with {count} panels should be valid"
        
        # Verify total panel count is valid
        assert config.validate_panel_count(total_panels) == True, \
            f"Total panel count {total_panels} should be valid"
    
    @given(
        scene_panel_counts=st.lists(
            st.integers(min_value=1, max_value=8),
            min_size=3,
            max_size=25
        )
    )
    def test_scene_panel_count_consistency(self, scene_panel_counts):
        """
        Property: Scene panel count validation should be consistent across all valid inputs.
        **Validates: Requirements 2.1**
        """
        assume(len(scene_panel_counts) >= 3)
        assume(all(1 <= count <= 8 for count in scene_panel_counts))
        
        total_panels = sum(scene_panel_counts)
        assume(20 <= total_panels <= 50)  # Within enhanced range
        
        config = get_enhanced_panel_config()
        
        # Test each scene panel count individually
        for i, count in enumerate(scene_panel_counts):
            assert config.validate_scene_panel_count(count) == True, \
                f"Scene {i+1} with {count} panels should be valid"
        
        # Test script creation with these scene counts
        script = create_script_with_scene_constraints(total_panels, scene_panel_counts)
        
        # Verify script structure
        assert len(script.panels) == total_panels
        
        # Verify evaluator consistency
        evaluation = webtoon_evaluator.evaluate_script(script)
        assert evaluation.score >= 4.0, "Valid scene distribution should not be heavily penalized"
    
    def test_scene_panel_count_boundary_conditions(self):
        """
        Test boundary conditions for scene panel count validation.
        **Validates: Requirements 2.1**
        """
        config = get_enhanced_panel_config()
        
        # Test exact boundaries
        assert config.validate_scene_panel_count(0) == False, "0 panels per scene should be invalid"
        assert config.validate_scene_panel_count(1) == True, "1 panel per scene should be valid"
        assert config.validate_scene_panel_count(8) == True, "8 panels per scene should be valid"
        assert config.validate_scene_panel_count(9) == False, "9 panels per scene should be invalid"
        
        # Test scripts at boundaries
        script_1_panel = create_script_with_scene_constraints(1, [1])
        script_8_panels = create_script_with_scene_constraints(8, [8])
        
        eval_1 = webtoon_evaluator.evaluate_script(script_1_panel)
        eval_8 = webtoon_evaluator.evaluate_script(script_8_panels)
        
        # Both should be acceptable (though may have other issues)
        assert eval_1.score >= 4.0, "1-panel scene should not be heavily penalized"
        assert eval_8.score >= 4.0, "8-panel scene should not be heavily penalized"
    
    @given(
        total_panels=st.integers(min_value=20, max_value=50),
        narrative_complexity=st.sampled_from(["simple", "moderate", "complex"])
    )
    def test_scene_panel_allocation_based_on_complexity(self, total_panels, narrative_complexity):
        """
        Property: Scene panel allocation should support different narrative complexities.
        **Validates: Requirements 2.1, 2.4**
        """
        assume(20 <= total_panels <= 50)
        
        # Generate scene distribution based on narrative complexity
        if narrative_complexity == "simple":
            # Simple stories: fewer panels per scene, more scenes
            target_panels_per_scene = 2
        elif narrative_complexity == "moderate":
            # Moderate stories: balanced panel distribution
            target_panels_per_scene = 4
        else:  # complex
            # Complex stories: more panels per scene for detailed development
            target_panels_per_scene = 6
        
        # Generate distribution favoring the target
        num_scenes = max(3, total_panels // target_panels_per_scene)
        scene_counts = generate_valid_scene_distribution(total_panels, num_scenes)
        
        # Verify constraints are met
        assert all(1 <= count <= 8 for count in scene_counts), "All scenes should be within 1-8 panel limits"
        assert sum(scene_counts) == total_panels, "Scene counts should sum to total panels"
        
        # Create and validate script
        script = create_script_with_scene_constraints(total_panels, scene_counts)
        config = get_enhanced_panel_config()
        
        # Verify all scene panel counts are valid
        for count in scene_counts:
            assert config.validate_scene_panel_count(count) == True
        
        # Verify total is valid
        assert config.validate_panel_count(total_panels) == True
    
    @given(
        total_panels=st.integers(min_value=20, max_value=50),
        character_count=st.integers(min_value=1, max_value=4)
    )
    def test_scene_panel_constraints_with_multiple_characters(self, total_panels, character_count):
        """
        Property: Scene panel constraints should work with multiple characters.
        **Validates: Requirements 2.1, 2.4**
        """
        assume(20 <= total_panels <= 50)
        assume(1 <= character_count <= 4)
        
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
                visual_description=f"Test character {i} for scene panel constraint testing"
            )
            characters.append(char)
        
        # Generate valid scene distribution
        scene_counts = generate_valid_scene_distribution(total_panels)
        
        # Create panels with different characters across scenes
        panels = []
        panel_number = 1
        
        for scene_idx, scene_panel_count in enumerate(scene_counts, 1):
            for panel_in_scene in range(scene_panel_count):
                char_idx = (panel_number - 1) % character_count
                character = characters[char_idx]
                
                panel = WebtoonPanel(
                    panel_number=panel_number,
                    visual_prompt=f"Scene {scene_idx} panel {panel_number}: Multi-character scene with {character.name} featuring detailed visual composition",
                    dialogue=[{"character": character.name, "text": f"Scene {scene_idx} dialogue from {character.name}", "order": 1}],
                    active_character_names=[character.name],
                    shot_type="Medium Shot",
                    character_frame_percentage=40,
                    environment_frame_percentage=60
                )
                panels.append(panel)
                panel_number += 1
        
        script = WebtoonScript(panels=panels, characters=characters)
        
        # Verify script structure
        assert len(script.panels) == total_panels
        assert len(script.characters) == character_count
        
        # Verify scene constraints are maintained with multiple characters
        config = get_enhanced_panel_config()
        for count in scene_counts:
            assert config.validate_scene_panel_count(count) == True
        
        # Verify evaluator handles multi-character scene constraints
        evaluation = webtoon_evaluator.evaluate_script(script)
        assert evaluation.score >= 4.0, "Multi-character script with valid scene constraints should not be heavily penalized"
    
    def test_legacy_vs_enhanced_scene_panel_limits(self):
        """
        Test that enhanced scene panel limits are used instead of legacy limits.
        **Validates: Requirements 2.1**
        """
        config = get_enhanced_panel_config()
        
        # Test that enhanced limit (8) is used instead of legacy limit (5)
        assert config.max_panels_per_scene == 8, "Should use enhanced limit (8), not legacy limit (5)"
        
        # Test that 6-8 panels per scene are now valid (were invalid in legacy system)
        for panel_count in [6, 7, 8]:
            assert config.validate_scene_panel_count(panel_count) == True, \
                f"{panel_count} panels per scene should be valid in enhanced system"
            
            # Create test script with this scene size
            script = create_script_with_scene_constraints(panel_count, [panel_count])
            evaluation = webtoon_evaluator.evaluate_script(script)
            
            # Should not be penalized for using enhanced limits
            assert evaluation.score >= 4.0, \
                f"Scene with {panel_count} panels should not be penalized in enhanced system"
        
        # Test that 9+ panels per scene are still invalid
        for panel_count in [9, 10, 12]:
            assert config.validate_scene_panel_count(panel_count) == False, \
                f"{panel_count} panels per scene should still be invalid"
    
    @given(
        total_panels=st.integers(min_value=20, max_value=50),
        scene_distribution_style=st.sampled_from(["uniform", "varied", "front_heavy", "back_heavy"])
    )
    def test_scene_panel_distribution_styles(self, total_panels, scene_distribution_style):
        """
        Property: Different scene panel distribution styles should all be valid.
        **Validates: Requirements 2.1, 2.4**
        """
        assume(20 <= total_panels <= 50)
        
        # Generate different distribution styles
        if scene_distribution_style == "uniform":
            # All scenes have similar panel counts
            panels_per_scene = total_panels // 5  # ~5 scenes
            panels_per_scene = max(1, min(8, panels_per_scene))
            num_scenes = total_panels // panels_per_scene
            scene_counts = [panels_per_scene] * num_scenes
            # Handle remainder
            remainder = total_panels - sum(scene_counts)
            for i in range(remainder):
                if scene_counts[i % len(scene_counts)] < 8:
                    scene_counts[i % len(scene_counts)] += 1
        
        elif scene_distribution_style == "varied":
            # Mix of different scene sizes
            scene_counts = []
            remaining = total_panels
            while remaining > 0:
                # Randomly choose scene size between 1-8, but don't exceed remaining
                scene_size = min(8, max(1, remaining // 2 if len(scene_counts) < 3 else remaining))
                scene_counts.append(scene_size)
                remaining -= scene_size
                if len(scene_counts) > 20:  # Safety limit
                    break
        
        elif scene_distribution_style == "front_heavy":
            # Larger scenes at the beginning
            scene_counts = []
            remaining = total_panels
            scene_size = 8
            while remaining > 0 and scene_size >= 1:
                if remaining >= scene_size:
                    scene_counts.append(scene_size)
                    remaining -= scene_size
                else:
                    scene_counts.append(remaining)
                    remaining = 0
                scene_size = max(1, scene_size - 1)
        
        else:  # back_heavy
            # Larger scenes at the end
            scene_counts = []
            remaining = total_panels
            scene_size = 1
            while remaining > 0 and scene_size <= 8:
                if remaining >= scene_size:
                    scene_counts.append(scene_size)
                    remaining -= scene_size
                else:
                    scene_counts.append(remaining)
                    remaining = 0
                scene_size = min(8, scene_size + 1)
        
        # Ensure all constraints are met
        scene_counts = [max(1, min(8, count)) for count in scene_counts if count > 0]
        
        # Adjust if sum doesn't match (due to rounding)
        current_sum = sum(scene_counts)
        if current_sum != total_panels:
            diff = total_panels - current_sum
            if diff > 0:
                # Add panels to scenes that can accommodate them
                for i in range(len(scene_counts)):
                    if diff <= 0:
                        break
                    can_add = min(diff, 8 - scene_counts[i])
                    scene_counts[i] += can_add
                    diff -= can_add
            else:
                # Remove panels from largest scenes
                while diff < 0 and scene_counts:
                    max_idx = scene_counts.index(max(scene_counts))
                    if scene_counts[max_idx] > 1:
                        scene_counts[max_idx] -= 1
                        diff += 1
                    else:
                        break
        
        # Final validation
        if sum(scene_counts) != total_panels or not all(1 <= count <= 8 for count in scene_counts):
            # Fallback to simple distribution
            scene_counts = generate_valid_scene_distribution(total_panels)
        
        # Verify constraints
        assert all(1 <= count <= 8 for count in scene_counts), f"All scenes should be 1-8 panels: {scene_counts}"
        assert sum(scene_counts) == total_panels, f"Scene counts should sum to {total_panels}: {scene_counts}"
        
        # Create and validate script
        script = create_script_with_scene_constraints(total_panels, scene_counts)
        config = get_enhanced_panel_config()
        
        # Verify all scene panel counts are valid
        for count in scene_counts:
            assert config.validate_scene_panel_count(count) == True
        
        # Verify evaluator accepts different distribution styles
        evaluation = webtoon_evaluator.evaluate_script(script)
        assert evaluation.score >= 4.0, f"Distribution style {scene_distribution_style} should not be heavily penalized"
    
    @given(
        total_panels=st.integers(min_value=20, max_value=50),
        iterations=st.integers(min_value=1, max_value=3)
    )
    def test_scene_panel_constraint_validation_deterministic(self, total_panels, iterations):
        """
        Property: Scene panel constraint validation should be deterministic.
        **Validates: Requirements 2.1, 2.4**
        """
        assume(20 <= total_panels <= 50)
        assume(1 <= iterations <= 3)
        
        config = get_enhanced_panel_config()
        
        # Test multiple iterations of the same validation
        for panel_count in range(1, 9):  # Test all valid scene panel counts
            results = []
            for _ in range(iterations):
                result = config.validate_scene_panel_count(panel_count)
                results.append(result)
            
            # All results should be identical (deterministic)
            assert all(r == results[0] for r in results), \
                f"Scene panel count validation for {panel_count} should be deterministic"
            
            # Expected result should be True for 1-8 panels
            expected = 1 <= panel_count <= 8
            assert results[0] == expected, \
                f"Scene panel count {panel_count} validation should be {expected}"
        
        # Test script creation determinism
        scene_counts = generate_valid_scene_distribution(total_panels)
        
        scripts = []
        for _ in range(iterations):
            script = create_script_with_scene_constraints(total_panels, scene_counts)
            scripts.append(script)
        
        # All scripts should have same structure
        for script in scripts[1:]:
            assert len(script.panels) == len(scripts[0].panels), "Script panel count should be deterministic"
            assert len(script.characters) == len(scripts[0].characters), "Script character count should be deterministic"


if __name__ == "__main__":
    # Run the property tests
    pytest.main([__file__, "-v"])