"""
Unit tests for Multi-Panel Prompt Templates (Phase 3.1).

Tests the prompt formatting functions for multi-panel webtoon generation.

v2.0.0: Initial implementation
"""

import pytest
from app.prompt.multi_panel import (
    PanelData,
    format_multi_panel_prompt,
    format_panels_from_shots,
    format_panels_from_webtoon_panels,
    get_recommended_panel_count,
    validate_panel_prompt,
    MULTI_PANEL_TEMPLATE,
    MULTI_PANEL_WITH_REFERENCES_TEMPLATE,
)


# ============================================================================
# Test PanelData
# ============================================================================

class TestPanelData:
    """Tests for PanelData dataclass."""

    def test_basic_creation(self):
        """Test basic PanelData creation."""
        panel = PanelData(
            panel_number=1,
            shot_type="Close-up",
            subject="Hana",
            description="Looking surprised",
            characters=["Hana"],
        )
        assert panel.panel_number == 1
        assert panel.shot_type == "Close-up"
        assert panel.subject == "Hana"

    def test_default_values(self):
        """Test default values are set correctly."""
        panel = PanelData(
            panel_number=1,
            shot_type="Medium shot",
            subject="characters",
            description="Standing together",
            characters=[],
        )
        assert panel.emotional_intensity == 5
        assert panel.mood_context == "neutral"

    def test_to_prompt_line_basic(self):
        """Test basic prompt line generation."""
        panel = PanelData(
            panel_number=1,
            shot_type="Close-up",
            subject="Hana",
            description="Looking surprised with wide eyes",
            characters=["Hana"],
        )
        line = panel.to_prompt_line(include_mood=False)
        assert "Panel 1:" in line
        assert "Close-up" in line
        assert "Hana" in line
        assert "Looking surprised" in line

    def test_to_prompt_line_with_mood(self):
        """Test prompt line includes mood hint."""
        panel = PanelData(
            panel_number=2,
            shot_type="Wide shot",
            subject="Ji-hoon and Hana",
            description="Walking through the park",
            characters=["Ji-hoon", "Hana"],
            mood_context="romantic"
        )
        line = panel.to_prompt_line(include_mood=True)
        assert "[romantic mood]" in line

    def test_to_prompt_line_neutral_mood_hidden(self):
        """Test neutral mood is not shown in prompt."""
        panel = PanelData(
            panel_number=1,
            shot_type="Medium shot",
            subject="Scene",
            description="Test",
            characters=[],
            mood_context="neutral"
        )
        line = panel.to_prompt_line(include_mood=True)
        assert "[neutral mood]" not in line


# ============================================================================
# Test format_multi_panel_prompt
# ============================================================================

class TestFormatMultiPanelPrompt:
    """Tests for format_multi_panel_prompt function."""

    def test_basic_formatting(self):
        """Test basic multi-panel prompt formatting."""
        panels = [
            PanelData(1, "Close-up", "Hana", "Looking surprised", ["Hana"]),
            PanelData(2, "Wide shot", "Both", "Standing apart", ["Hana", "Ji-hoon"]),
            PanelData(3, "Medium shot", "Ji-hoon", "Reaching out", ["Ji-hoon"]),
        ]
        prompt = format_multi_panel_prompt(
            panels=panels,
            style_description="soft romantic manhwa style",
        )

        assert "3 distinct horizontal panels" in prompt
        assert "Panel 1:" in prompt
        assert "Panel 2:" in prompt
        assert "Panel 3:" in prompt
        assert "9:16" in prompt
        assert "soft romantic manhwa style" in prompt

    def test_panel_count_in_prompt(self):
        """Test that panel count is correctly reflected."""
        for count in [2, 3, 4, 5]:
            panels = [
                PanelData(i, "Medium shot", "Scene", "Description", [])
                for i in range(1, count + 1)
            ]
            prompt = format_multi_panel_prompt(panels, "test style")
            assert f"{count} distinct horizontal panels" in prompt

    def test_with_character_references(self):
        """Test formatting with character references."""
        panels = [
            PanelData(1, "Close-up", "Hana", "Smiling", ["Hana"]),
            PanelData(2, "Close-up", "Ji-hoon", "Surprised", ["Ji-hoon"]),
        ]
        char_refs = {
            "Hana": "Young woman with long black hair, gentle eyes",
            "Ji-hoon": "Tall man with sharp features, messy hair"
        }
        prompt = format_multi_panel_prompt(
            panels=panels,
            style_description="romantic webtoon",
            character_references=char_refs
        )

        assert "CHARACTER REFERENCES" in prompt
        assert "Hana:" in prompt
        assert "Ji-hoon:" in prompt
        assert "long black hair" in prompt

    def test_style_keywords_included(self):
        """Test that style keywords are included."""
        panels = [PanelData(1, "Medium", "Scene", "Test", [])]
        prompt = format_multi_panel_prompt(
            panels=panels,
            style_description="test",
            style_keywords="vibrant colors, detailed backgrounds"
        )
        assert "vibrant colors" in prompt
        assert "detailed backgrounds" in prompt

    def test_empty_panels_raises_error(self):
        """Test that empty panel list raises error."""
        with pytest.raises(ValueError, match="At least one panel"):
            format_multi_panel_prompt([], "test style")

    def test_too_many_panels_raises_error(self):
        """Test that more than 5 panels raises error."""
        panels = [PanelData(i, "Medium", "Scene", "Test", []) for i in range(1, 7)]
        with pytest.raises(ValueError, match="Maximum 5 panels"):
            format_multi_panel_prompt(panels, "test style")

    def test_critical_requirements_included(self):
        """Test that critical requirements section is included."""
        panels = [PanelData(1, "Medium", "Scene", "Test", [])]
        prompt = format_multi_panel_prompt(panels, "test style")

        assert "CRITICAL REQUIREMENTS" in prompt
        assert "thin black borders" in prompt.lower()
        assert "9:16" in prompt


# ============================================================================
# Test format_panels_from_shots
# ============================================================================

class TestFormatPanelsFromShots:
    """Tests for format_panels_from_shots function."""

    def test_basic_shot_conversion(self):
        """Test converting shot dictionaries to prompt."""
        shots = [
            {
                "shot_type": "Close-up",
                "subject": "Hana",
                "visual_prompt": "Looking surprised",
                "active_character_names": ["Hana"],
                "emotional_intensity": 7,
            },
            {
                "shot_type": "Wide shot",
                "subject": "Both characters",
                "description": "In the park",
                "characters": ["Hana", "Ji-hoon"],
            }
        ]
        prompt = format_panels_from_shots(shots, "romantic style")

        assert "2 distinct horizontal panels" in prompt
        assert "Panel 1:" in prompt
        assert "Panel 2:" in prompt

    def test_fallback_values(self):
        """Test that fallback values work for missing keys."""
        shots = [{"shot_type": "Medium shot"}]  # Minimal shot data
        prompt = format_panels_from_shots(shots, "test style")

        assert "Panel 1:" in prompt
        assert "Medium shot" in prompt

    def test_mood_context_extraction(self):
        """Test that mood context is extracted from shots."""
        shots = [
            {
                "shot_type": "Close-up",
                "subject": "Hana",
                "description": "Crying",
                "detected_context": "sad"
            }
        ]
        prompt = format_panels_from_shots(shots, "test style")
        assert "[sad mood]" in prompt


# ============================================================================
# Test format_panels_from_webtoon_panels
# ============================================================================

class TestFormatPanelsFromWebtoonPanels:
    """Tests for format_panels_from_webtoon_panels function."""

    def test_webtoon_panel_conversion(self):
        """Test converting WebtoonPanel objects to prompt."""
        from app.models.story import WebtoonPanel

        panels = [
            WebtoonPanel(
                panel_number=1,
                shot_type="Close-up",
                active_character_names=["Hana"],
                visual_prompt="Looking at the sunset with tears in her eyes",
                emotional_intensity=8,
            ),
            WebtoonPanel(
                panel_number=2,
                shot_type="Wide shot",
                active_character_names=["Hana", "Ji-hoon"],
                visual_prompt="Walking together on the beach",
                emotional_intensity=5,
            ),
        ]

        prompt = format_panels_from_webtoon_panels(panels, "romantic webtoon style")

        assert "2 distinct horizontal panels" in prompt
        assert "Panel 1:" in prompt
        assert "Panel 2:" in prompt
        assert "sunset" in prompt or "Close-up" in prompt


# ============================================================================
# Test get_recommended_panel_count
# ============================================================================

class TestGetRecommendedPanelCount:
    """Tests for get_recommended_panel_count function."""

    def test_action_scenes(self):
        """Action scenes should recommend 4 panels."""
        assert get_recommended_panel_count("action") == 4

    def test_dialogue_scenes(self):
        """Dialogue scenes should recommend 3 panels."""
        assert get_recommended_panel_count("dialogue") == 3

    def test_emotional_scenes(self):
        """Emotional scenes should recommend 2 panels."""
        assert get_recommended_panel_count("emotional") == 2

    def test_climax_scenes(self):
        """Climax scenes should recommend 1 panel (full page)."""
        assert get_recommended_panel_count("climax") == 1

    def test_unknown_type(self):
        """Unknown types should default to 3 panels."""
        assert get_recommended_panel_count("unknown") == 3
        assert get_recommended_panel_count("random") == 3

    def test_case_insensitive(self):
        """Function should be case insensitive."""
        assert get_recommended_panel_count("ACTION") == 4
        assert get_recommended_panel_count("Dialogue") == 3


# ============================================================================
# Test validate_panel_prompt
# ============================================================================

class TestValidatePanelPrompt:
    """Tests for validate_panel_prompt function."""

    def test_valid_prompt(self):
        """Test validation of a valid prompt."""
        panels = [
            PanelData(1, "Close-up", "Hana", "Test", []),
            PanelData(2, "Wide shot", "Scene", "Test", []),
            PanelData(3, "Medium shot", "Both", "Test", []),
        ]
        prompt = format_multi_panel_prompt(panels, "test style")
        result = validate_panel_prompt(prompt)

        assert result["is_valid"] is True
        assert result["panel_count"] == 3
        assert len(result["issues"]) == 0

    def test_detects_missing_panels(self):
        """Test that missing panel markers are detected."""
        prompt = "A webtoon page with 9:16 aspect ratio. Some description. Thin borders."
        result = validate_panel_prompt(prompt)

        assert result["is_valid"] is False
        assert result["panel_count"] == 0
        assert any("No panel markers" in issue for issue in result["issues"])

    def test_detects_too_many_panels(self):
        """Test that too many panels are detected."""
        prompt = """9:16 aspect ratio. style test. borders.
Panel 1: Test
Panel 2: Test
Panel 3: Test
Panel 4: Test
Panel 5: Test
Panel 6: Test
"""
        result = validate_panel_prompt(prompt)

        assert result["is_valid"] is False
        assert result["panel_count"] == 6
        assert any("Too many panels" in issue for issue in result["issues"])

    def test_detects_missing_aspect_ratio(self):
        """Test that missing aspect ratio is detected."""
        prompt = "Panel 1: Test. Panel 2: Test. style description. thin borders."
        result = validate_panel_prompt(prompt)

        assert any("9:16" in issue for issue in result["issues"])

    def test_detects_missing_border_instruction(self):
        """Test that missing border instruction is detected."""
        prompt = "Panel 1: Test. Panel 2: Test. 9:16 aspect ratio. style test."
        result = validate_panel_prompt(prompt)

        assert any("border" in issue.lower() for issue in result["issues"])


# ============================================================================
# Integration Tests
# ============================================================================

class TestMultiPanelPromptIntegration:
    """Integration tests for the multi-panel prompt system."""

    def test_full_workflow(self):
        """Test complete workflow from panels to validated prompt."""
        # Create panels
        panels = [
            PanelData(
                panel_number=1,
                shot_type="Wide establishing shot",
                subject="Seoul cityscape",
                description="Rainy evening in Gangnam, neon lights reflecting on wet streets",
                characters=[],
                emotional_intensity=4,
                mood_context="mysterious"
            ),
            PanelData(
                panel_number=2,
                shot_type="Medium shot",
                subject="Hana",
                description="Walking alone with umbrella, looking thoughtful",
                characters=["Hana"],
                emotional_intensity=5,
                mood_context="sad"
            ),
            PanelData(
                panel_number=3,
                shot_type="Close-up",
                subject="Hana's face",
                description="A single tear rolling down her cheek",
                characters=["Hana"],
                emotional_intensity=8,
                mood_context="sad"
            ),
        ]

        # Format prompt
        prompt = format_multi_panel_prompt(
            panels=panels,
            style_description="soft romantic manhwa with muted colors and emotional lighting",
            style_keywords="high quality, detailed backgrounds, expressive faces",
            character_references={
                "Hana": "Young Korean woman, long black hair, gentle eyes, wearing a beige coat"
            }
        )

        # Validate
        result = validate_panel_prompt(prompt)

        assert result["is_valid"] is True
        assert result["panel_count"] == 3

        # Check content
        assert "3 distinct horizontal panels" in prompt
        assert "Seoul cityscape" in prompt or "establishing" in prompt.lower()
        assert "tear" in prompt or "Close-up" in prompt
        assert "[sad mood]" in prompt
        assert "CHARACTER REFERENCES" in prompt
        assert "Hana:" in prompt

    def test_mood_variation_across_panels(self):
        """Test that different moods are reflected in the prompt."""
        panels = [
            PanelData(1, "Wide shot", "Scene", "Peaceful morning", [], mood_context="peaceful"),
            PanelData(2, "Medium shot", "Characters", "Argument begins", [], mood_context="conflict"),
            PanelData(3, "Close-up", "Face", "Shock and tears", [], mood_context="sad"),
        ]

        prompt = format_multi_panel_prompt(panels, "dramatic style")

        assert "[peaceful mood]" in prompt
        assert "[conflict mood]" in prompt
        assert "[sad mood]" in prompt
