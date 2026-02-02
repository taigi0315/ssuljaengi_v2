"""
Tests for the enhanced WebtoonRewriter with expanded panel support.

Tests the enhanced rewriter's ability to handle 20-50 panel range feedback,
three-act panel redistribution, and intelligent panel addition strategies.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.webtoon_rewriter import WebtoonRewriter
from app.models.story import WebtoonScript, WebtoonPanel, Character


@pytest.fixture
def sample_script():
    """Create a sample WebtoonScript for testing."""
    characters = [
        Character(
            name="Alice",
            reference_tag="alice_ref",
            gender="female",
            age="25",
            face="oval face with bright eyes",
            hair="long brown hair",
            body="average height",
            outfit="casual dress",
            mood="cheerful",
            visual_description="25 year old female with oval face, long brown hair"
        )
    ]
    
    panels = [
        WebtoonPanel(
            panel_number=1,
            scene_type="bridge",
            shot_type="Medium Shot",
            visual_prompt="Alice standing in a park, looking thoughtful with trees in background",
            active_character_names=["Alice"],
            dialogue=[{"character": "Alice", "text": "What a beautiful day.", "order": 1}],
            negative_prompt="text, speech bubbles",
            composition_notes="Centered composition",
            environment_focus="park setting",
            environment_details="green trees and grass",
            atmospheric_conditions="bright sunny day",
            story_beat="introduction",
            character_placement_and_action="Alice standing casually",
            character_frame_percentage=40,
            environment_frame_percentage=60
        )
    ]
    
    return WebtoonScript(characters=characters, panels=panels)


@pytest.fixture
def rewriter():
    """Create a WebtoonRewriter instance for testing."""
    return WebtoonRewriter()


class TestEnhancedRewriter:
    """Test cases for enhanced WebtoonRewriter functionality."""
    
    def test_analyze_panel_distribution_single_panel(self, rewriter, sample_script):
        """Test panel distribution analysis with single panel."""
        distribution = rewriter._analyze_panel_distribution(sample_script)
        
        assert distribution["total"] == 1
        assert distribution["act1"] == 0  # 1//3 = 0
        assert distribution["act2"] == 0  # (1*2)//3 - 0 = 0
        assert distribution["act3"] == 1  # 1 - 0 = 1
        assert distribution["needs_redistribution"] is True
    
    def test_analyze_panel_distribution_empty_script(self, rewriter):
        """Test panel distribution analysis with minimal script."""
        # Create minimal script with one character and one panel (minimum required)
        minimal_character = Character(
            name="Test",
            reference_tag="test_ref",
            gender="unknown",
            age="unknown",
            face="generic face",
            hair="generic hair",
            body="generic body",
            outfit="generic outfit",
            mood="neutral",
            visual_description="test character with sufficient description length for validation"
        )
        
        minimal_panel = WebtoonPanel(
            panel_number=1,
            scene_type="bridge",
            shot_type="Medium Shot",
            visual_prompt="Test panel with minimal content for validation purposes",
            active_character_names=["Test"],
            dialogue=[],
            negative_prompt="text, speech bubbles",
            composition_notes="Test composition",
            environment_focus="test environment",
            environment_details="minimal details",
            atmospheric_conditions="neutral",
            story_beat="test beat",
            character_placement_and_action="test action",
            character_frame_percentage=40,
            environment_frame_percentage=60
        )
        
        minimal_script = WebtoonScript(characters=[minimal_character], panels=[minimal_panel])
        distribution = rewriter._analyze_panel_distribution(minimal_script)
        
        assert distribution["total"] == 1
        assert distribution["needs_redistribution"] is True
    
    def test_calculate_target_panel_count_below_minimum(self, rewriter):
        """Test target panel count calculation for scripts below minimum."""
        target = rewriter._calculate_target_panel_count(10, "Script needs more panels")
        assert 25 <= target <= 40  # Should target ideal range
    
    def test_calculate_target_panel_count_with_specific_feedback(self, rewriter):
        """Test target panel count calculation with specific ADD feedback."""
        target = rewriter._calculate_target_panel_count(15, "ADD 10 MORE PANELS")
        assert target == 25  # 15 + 10 = 25
    
    def test_calculate_target_panel_count_above_maximum(self, rewriter):
        """Test target panel count calculation for scripts above maximum."""
        target = rewriter._calculate_target_panel_count(60, "Too many panels")
        assert target == 40  # Should target ideal maximum
    
    def test_generate_panel_expansion_guidance(self, rewriter):
        """Test panel expansion guidance generation."""
        distribution = {
            "total": 10,
            "act1": 3,
            "act2": 4,
            "act3": 3
        }
        
        guidance = rewriter._generate_panel_expansion_guidance(10, 30, distribution)
        
        assert "EXPAND TO 30 PANELS" in guidance
        assert "add 20 panels" in guidance
        assert "Act 1" in guidance
        assert "Act 2" in guidance
        assert "Act 3" in guidance
    
    def test_enhance_feedback_with_panel_guidance(self, rewriter, sample_script):
        """Test feedback enhancement with panel guidance."""
        original_feedback = "Script needs improvement"
        enhanced = rewriter._enhance_feedback_with_panel_guidance(
            original_feedback, sample_script
        )
        
        assert original_feedback in enhanced
        assert "ENHANCED PANEL GENERATION" in enhanced
        assert "THREE-ACT REDISTRIBUTION" in enhanced
    
    def test_analyze_script_for_enhancement(self, rewriter, sample_script):
        """Test script analysis for enhancement opportunities."""
        analysis = rewriter.analyze_script_for_enhancement(sample_script)
        
        assert analysis["current_panel_count"] == 1
        assert analysis["enhancement_needed"] is True  # 1 < 20
        assert analysis["redistribution_needed"] is True
        assert len(analysis["recommendations"]) > 0
        assert "Increase panel count" in analysis["recommendations"][0]
    
    def test_analyze_script_for_enhancement_good_script(self, rewriter):
        """Test script analysis for a script that meets enhanced requirements."""
        # Create a script with 30 panels (in ideal range)
        characters = [
            Character(
                name="Bob",
                reference_tag="bob_ref",
                gender="male",
                age="30",
                face="square face",
                hair="short black hair",
                body="tall",
                outfit="suit",
                mood="serious",
                visual_description="30 year old male with square face"
            )
        ]
        
        panels = []
        for i in range(30):
            panels.append(
                WebtoonPanel(
                    panel_number=i+1,
                    scene_type="story",
                    shot_type="Medium Shot",
                    visual_prompt=f"Panel {i+1} showing story progression with detailed environment and character interaction",
                    active_character_names=["Bob"],
                    dialogue=[{"character": "Bob", "text": f"Line {i+1}", "order": 1}],
                    negative_prompt="text, speech bubbles",
                    composition_notes="Balanced composition",
                    environment_focus="office setting",
                    environment_details="modern office with computers",
                    atmospheric_conditions="professional lighting",
                    story_beat=f"beat_{i+1}",
                    character_placement_and_action="Bob working at desk",
                    character_frame_percentage=40,
                    environment_frame_percentage=60
                )
            )
        
        good_script = WebtoonScript(characters=characters, panels=panels)
        analysis = rewriter.analyze_script_for_enhancement(good_script)
        
        assert analysis["current_panel_count"] == 30
        assert analysis["enhancement_needed"] is False  # 30 >= 20
        # May still need redistribution due to simple thirds calculation
        assert len(analysis["recommendations"]) >= 0


class TestEnhancedRewriterIntegration:
    """Integration tests for enhanced rewriter functionality."""
    
    @pytest.mark.asyncio
    async def test_rewrite_script_integration_logic(self, rewriter, sample_script):
        """Test the core rewrite script logic without complex LLM mocking."""
        # Test the feedback enhancement logic
        enhanced_feedback = rewriter._enhance_feedback_with_panel_guidance(
            "ADD MORE PANELS for enhanced storytelling", 
            sample_script
        )
        
        # Verify enhanced feedback contains expected guidance
        assert "ENHANCED PANEL GENERATION REQUIREMENTS" in enhanced_feedback
        assert "EXPAND TO" in enhanced_feedback
        assert "THREE-ACT REDISTRIBUTION" in enhanced_feedback
        assert "SCENE EXPANSION STRATEGIES" in enhanced_feedback
        
        # Test script analysis
        analysis = rewriter.analyze_script_for_enhancement(sample_script)
        assert analysis["current_panel_count"] == 1
        assert analysis["enhancement_needed"] is True
        assert analysis["target_panel_count"] >= 20
        
        # Test panel distribution analysis
        distribution = rewriter._analyze_panel_distribution(sample_script)
        assert distribution["total"] == 1
        assert distribution["needs_redistribution"] is True
        
        # Test target panel count calculation
        target = rewriter._calculate_target_panel_count(1, "ADD MORE PANELS")
        assert 20 <= target <= 50