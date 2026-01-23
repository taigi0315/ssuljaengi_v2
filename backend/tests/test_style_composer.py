"""
Unit tests for the Style Composer Service.

Tests the style composition functionality that combines BaseStyle and SceneMood.
"""

import pytest
from app.services.style_composer import (
    compose_style,
    compose_style_with_legacy,
    get_style_for_scene,
    get_legacy_style_with_mood,
    resolve_style_key_to_base,
    get_available_styles,
    get_available_moods,
    compose_styles_for_panels,
    compose_unified_style_for_page,
    StyleComposer,
    style_composer,
)
from app.models.style import (
    BaseStyle,
    SceneMood,
    MOOD_PRESETS,
    BASE_STYLES,
    ColorTemperature,
    LightingMood,
    SpecialEffect,
    LineQuality,
    RenderingQuality,
)


# ============================================================================
# compose_style Tests
# ============================================================================

class TestComposeStyle:
    """Test compose_style function."""

    def test_basic_composition(self):
        """Test basic style composition."""
        base = BASE_STYLES["soft_romantic"]
        mood = MOOD_PRESETS["neutral"]

        result = compose_style(base, mood)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Soft Romantic" in result

    def test_composition_without_mood(self):
        """Test composition with None mood uses neutral."""
        base = BASE_STYLES["soft_romantic"]

        result = compose_style(base, None)

        assert isinstance(result, str)
        assert "neutral" in result

    def test_composition_with_romantic_mood(self):
        """Test composition with romantic mood."""
        base = BASE_STYLES["soft_romantic"]
        mood = MOOD_PRESETS["romantic_tension"]

        result = compose_style(base, mood)

        assert "romantic_tension" in result
        assert "sparkle" in result.lower() or "soft" in result.lower()

    def test_composition_with_dramatic_mood(self):
        """Test composition with dramatic mood."""
        base = BASE_STYLES["dramatic_historical"]
        mood = MOOD_PRESETS["serious_conflict"]

        result = compose_style(base, mood)

        assert "Dramatic Historical" in result
        assert "dramatic" in result.lower()


# ============================================================================
# compose_style_with_legacy Tests
# ============================================================================

class TestComposeStyleWithLegacy:
    """Test compose_style_with_legacy function."""

    def test_legacy_style_only(self):
        """Test with legacy style key only."""
        result = compose_style_with_legacy("SOFT_ROMANTIC_WEBTOON")

        assert isinstance(result, str)
        assert "cel-shading" in result.lower() or "webtoon" in result.lower()

    def test_legacy_with_mood(self):
        """Test legacy style with mood modifiers."""
        mood = MOOD_PRESETS["romantic_tension"]
        result = compose_style_with_legacy("SOFT_ROMANTIC_WEBTOON", mood)

        assert "[SCENE MOOD: romantic_tension]" in result
        assert "sparkle" in result.lower()

    def test_invalid_legacy_key(self):
        """Test with invalid legacy key returns empty string."""
        result = compose_style_with_legacy("NONEXISTENT_STYLE")

        assert result == ""

    def test_legacy_with_neutral_mood(self):
        """Test legacy style with neutral mood."""
        mood = MOOD_PRESETS["neutral"]
        result = compose_style_with_legacy("CLEAN_MODERN_WEBTOON", mood)

        assert isinstance(result, str)
        # Neutral mood has minimal modifiers
        assert "SCENE MOOD" in result


# ============================================================================
# get_style_for_scene Tests
# ============================================================================

class TestGetStyleForScene:
    """Test get_style_for_scene function."""

    def test_basic_scene_style(self):
        """Test getting style for a basic scene."""
        result = get_style_for_scene("soft_romantic", 5, "neutral")

        assert isinstance(result, str)
        assert len(result) > 0

    def test_romantic_high_intensity(self):
        """Test romantic scene with high intensity."""
        result = get_style_for_scene("soft_romantic", 9, "romantic")

        assert isinstance(result, str)
        # High romantic intensity should trigger romantic_confession mood
        assert "romantic" in result.lower()

    def test_conflict_scene(self):
        """Test conflict scene style."""
        result = get_style_for_scene("dramatic_historical", 8, "conflict")

        assert isinstance(result, str)
        assert "dramatic" in result.lower()

    def test_invalid_style_name(self):
        """Test with invalid style name returns empty string."""
        result = get_style_for_scene("nonexistent_style", 5, "neutral")

        assert result == ""

    def test_different_contexts(self):
        """Test different scene contexts produce different results."""
        romantic = get_style_for_scene("soft_romantic", 7, "romantic")
        conflict = get_style_for_scene("soft_romantic", 7, "conflict")

        # Should have the same base style but different moods
        assert "Soft Romantic" in romantic
        assert "Soft Romantic" in conflict
        assert romantic != conflict


# ============================================================================
# get_legacy_style_with_mood Tests
# ============================================================================

class TestGetLegacyStyleWithMood:
    """Test get_legacy_style_with_mood function."""

    def test_basic_legacy_with_mood(self):
        """Test legacy style with mood based on intensity."""
        result = get_legacy_style_with_mood("SOFT_ROMANTIC_WEBTOON", 5, "neutral")

        assert isinstance(result, str)
        assert len(result) > 0

    def test_high_intensity_romantic(self):
        """Test high intensity romantic scene."""
        result = get_legacy_style_with_mood("SOFT_ROMANTIC_WEBTOON", 9, "romantic")

        assert "SCENE MOOD" in result
        # High romantic intensity should include effects
        assert "sparkle" in result.lower() or "bloom" in result.lower()


# ============================================================================
# resolve_style_key_to_base Tests
# ============================================================================

class TestResolveStyleKeyToBase:
    """Test resolve_style_key_to_base function."""

    def test_resolve_known_key(self):
        """Test resolving known legacy key."""
        base = resolve_style_key_to_base("SOFT_ROMANTIC_WEBTOON")

        assert base is not None
        assert base.name == "Soft Romantic"

    def test_resolve_another_key(self):
        """Test resolving another legacy key."""
        base = resolve_style_key_to_base("CLEAN_MODERN_WEBTOON")

        assert base is not None
        assert base.name == "Clean Modern"

    def test_resolve_unknown_key(self):
        """Test resolving unknown key returns None."""
        base = resolve_style_key_to_base("NONEXISTENT_STYLE")

        assert base is None


# ============================================================================
# get_available_styles Tests
# ============================================================================

class TestGetAvailableStyles:
    """Test get_available_styles function."""

    def test_returns_list(self):
        """Test function returns a list."""
        styles = get_available_styles()

        assert isinstance(styles, list)
        assert len(styles) > 0

    def test_tuple_structure(self):
        """Test each item is a proper tuple."""
        styles = get_available_styles()

        for style in styles:
            assert len(style) == 3
            name, display_name, legacy_key = style
            assert isinstance(name, str)
            assert isinstance(display_name, str)
            assert isinstance(legacy_key, str)

    def test_contains_known_styles(self):
        """Test list contains known styles."""
        styles = get_available_styles()
        names = [s[0] for s in styles]

        assert "soft_romantic" in names
        assert "clean_modern" in names


# ============================================================================
# get_available_moods Tests
# ============================================================================

class TestGetAvailableMoods:
    """Test get_available_moods function."""

    def test_returns_list(self):
        """Test function returns a list."""
        moods = get_available_moods()

        assert isinstance(moods, list)
        assert len(moods) > 0

    def test_tuple_structure(self):
        """Test each item is a proper tuple."""
        moods = get_available_moods()

        for mood in moods:
            assert len(mood) == 3
            name, description, intensity = mood
            assert isinstance(name, str)
            assert isinstance(description, str)
            assert isinstance(intensity, int)

    def test_contains_known_moods(self):
        """Test list contains known moods."""
        moods = get_available_moods()
        names = [m[0] for m in moods]

        assert "neutral" in names
        assert "comedy" in names
        assert "romantic_tension" in names


# ============================================================================
# compose_styles_for_panels Tests
# ============================================================================

class TestComposeStylesForPanels:
    """Test compose_styles_for_panels function."""

    def test_basic_panels_composition(self):
        """Test composing styles for multiple panels."""
        panels_data = [
            {"emotional_intensity": 5, "scene_context": "neutral"},
            {"emotional_intensity": 8, "scene_context": "romantic"},
            {"emotional_intensity": 7, "scene_context": "conflict"},
        ]

        results = compose_styles_for_panels("soft_romantic", panels_data)

        assert len(results) == 3
        assert all(isinstance(r, str) for r in results)
        assert all(len(r) > 0 for r in results)

    def test_different_moods_per_panel(self):
        """Test that different panels get different moods."""
        panels_data = [
            {"emotional_intensity": 3, "scene_context": "neutral"},
            {"emotional_intensity": 9, "scene_context": "romantic"},
        ]

        results = compose_styles_for_panels("soft_romantic", panels_data)

        # Should be different due to different intensities/contexts
        assert results[0] != results[1]

    def test_invalid_style_returns_empty(self):
        """Test invalid style returns empty strings."""
        panels_data = [
            {"emotional_intensity": 5, "scene_context": "neutral"},
        ]

        results = compose_styles_for_panels("nonexistent", panels_data)

        assert len(results) == 1
        assert results[0] == ""


# ============================================================================
# compose_unified_style_for_page Tests
# ============================================================================

class TestComposeUnifiedStyleForPage:
    """Test compose_unified_style_for_page function."""

    def test_basic_unified_style(self):
        """Test composing unified style for a page."""
        panels_data = [
            {"emotional_intensity": 5, "scene_context": "neutral"},
            {"emotional_intensity": 7, "scene_context": "neutral"},
            {"emotional_intensity": 6, "scene_context": "neutral"},
        ]

        base_prompt, mood_modifiers = compose_unified_style_for_page("soft_romantic", panels_data)

        assert isinstance(base_prompt, str)
        assert isinstance(mood_modifiers, str)
        assert len(base_prompt) > 0

    def test_uses_max_intensity(self):
        """Test that unified style uses maximum intensity."""
        panels_data = [
            {"emotional_intensity": 3, "scene_context": "neutral"},
            {"emotional_intensity": 9, "scene_context": "romantic"},
            {"emotional_intensity": 4, "scene_context": "neutral"},
        ]

        base_prompt, mood_modifiers = compose_unified_style_for_page("soft_romantic", panels_data)

        # Max intensity 9 + romantic should trigger intense mood effects
        assert "heightened" in mood_modifiers.lower() or "sparkle" in mood_modifiers.lower()

    def test_invalid_style_returns_empty(self):
        """Test invalid style returns empty tuple."""
        panels_data = [{"emotional_intensity": 5, "scene_context": "neutral"}]

        base_prompt, mood_modifiers = compose_unified_style_for_page("nonexistent", panels_data)

        assert base_prompt == ""
        assert mood_modifiers == ""


# ============================================================================
# StyleComposer Class Tests
# ============================================================================

class TestStyleComposerClass:
    """Test StyleComposer class."""

    def test_default_instance(self):
        """Test default global instance exists."""
        assert style_composer is not None
        assert isinstance(style_composer, StyleComposer)

    def test_custom_default_style(self):
        """Test creating composer with custom default style."""
        composer = StyleComposer(default_base_style="clean_modern")

        result = composer.compose()
        assert "Clean Modern" in result

    def test_compose_with_explicit_style(self):
        """Test compose with explicit style name."""
        composer = StyleComposer()

        result = composer.compose(base_style_name="dramatic_historical")
        assert "Dramatic Historical" in result

    def test_compose_with_mood_name(self):
        """Test compose with explicit mood name."""
        composer = StyleComposer()

        result = composer.compose(
            base_style_name="soft_romantic",
            scene_mood_name="romantic_tension"
        )
        assert "Soft Romantic" in result

    def test_compose_for_panels(self):
        """Test compose_for_panels method."""
        composer = StyleComposer()

        panels_data = [
            {"emotional_intensity": 5, "scene_context": "neutral"},
            {"emotional_intensity": 8, "scene_context": "romantic"},
        ]

        results = composer.compose_for_panels(panels_data)

        assert len(results) == 2
        assert all(len(r) > 0 for r in results)


# ============================================================================
# Integration Tests
# ============================================================================

class TestStyleComposerIntegration:
    """Integration tests for style composition."""

    def test_full_workflow_single_panel(self):
        """Test complete workflow for single panel."""
        # 1. Get style for a romantic peak moment
        style = get_style_for_scene(
            base_style_name="soft_romantic",
            emotional_intensity=9,
            scene_context="romantic"
        )

        assert len(style) > 100  # Should be substantial
        assert "romantic" in style.lower()

    def test_full_workflow_multi_panel(self):
        """Test complete workflow for multi-panel page."""
        panels = [
            {"emotional_intensity": 4, "scene_context": "neutral"},
            {"emotional_intensity": 6, "scene_context": "romantic"},
            {"emotional_intensity": 8, "scene_context": "romantic"},
            {"emotional_intensity": 5, "scene_context": "neutral"},
        ]

        # Option 1: Individual styles per panel
        individual_styles = compose_styles_for_panels("soft_romantic", panels)
        assert len(individual_styles) == 4

        # Option 2: Unified style for page
        base, mood = compose_unified_style_for_page("soft_romantic", panels)
        assert len(base) > 0
        assert len(mood) > 0

    def test_backward_compatibility(self):
        """Test backward compatibility with legacy styles."""
        # Using legacy key directly
        legacy_result = compose_style_with_legacy("SOFT_ROMANTIC_WEBTOON")

        # Using new system
        new_result = compose_style(BASE_STYLES["soft_romantic"], None)

        # Both should be valid strings
        assert len(legacy_result) > 0
        assert len(new_result) > 0

    def test_all_base_styles_compose(self):
        """Test all base styles can be composed."""
        for name, base_style in BASE_STYLES.items():
            result = compose_style(base_style, MOOD_PRESETS["neutral"])
            assert len(result) > 0, f"Failed to compose {name}"

    def test_all_moods_compose(self):
        """Test all moods can be composed with a base style."""
        base = BASE_STYLES["soft_romantic"]

        for name, mood in MOOD_PRESETS.items():
            result = compose_style(base, mood)
            assert len(result) > 0, f"Failed to compose with mood {name}"
