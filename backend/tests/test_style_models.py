"""
Unit tests for the modular style system models.

Tests the BaseStyle, SceneMood, MOOD_PRESETS, and style composition functionality.
"""

import pytest
from app.models.style import (
    # Enums
    ColorTemperature,
    SaturationLevel,
    LightingMood,
    DetailLevel,
    ExpressionStyle,
    SpecialEffect,
    RenderingQuality,
    LineQuality,
    # Models
    BaseStyle,
    SceneMood,
    ComposedStyle,
    # Presets
    MOOD_PRESETS,
    BASE_STYLES,
    # Functions
    get_mood_preset,
    get_mood_for_intensity,
    list_mood_presets,
    get_base_style,
    list_base_styles,
)


# ============================================================================
# Enum Tests
# ============================================================================

class TestEnums:
    """Test style-related enums."""

    def test_color_temperature_values(self):
        """Test color temperature enum values."""
        assert ColorTemperature.COOL.value == "cool"
        assert ColorTemperature.WARM.value == "warm"
        assert ColorTemperature.NEUTRAL.value == "neutral"
        assert ColorTemperature.VERY_WARM.value == "very_warm"
        assert ColorTemperature.VERY_COOL.value == "very_cool"

    def test_saturation_level_values(self):
        """Test saturation level enum values."""
        assert SaturationLevel.DESATURATED.value == "desaturated"
        assert SaturationLevel.NORMAL.value == "normal"
        assert SaturationLevel.VIVID.value == "vivid"

    def test_lighting_mood_values(self):
        """Test lighting mood enum values."""
        assert LightingMood.BRIGHT.value == "bright"
        assert LightingMood.DRAMATIC.value == "dramatic"
        assert LightingMood.ETHEREAL.value == "ethereal"
        assert LightingMood.GOLDEN_HOUR.value == "golden_hour"

    def test_special_effect_values(self):
        """Test special effect enum values."""
        assert SpecialEffect.SPARKLES.value == "sparkles"
        assert SpecialEffect.BLOOM.value == "bloom"
        assert SpecialEffect.VIGNETTE.value == "vignette"
        assert SpecialEffect.RAIN.value == "rain"

    def test_expression_style_values(self):
        """Test expression style enum values."""
        assert ExpressionStyle.SUBTLE.value == "subtle"
        assert ExpressionStyle.EXAGGERATED.value == "exaggerated"


# ============================================================================
# BaseStyle Tests
# ============================================================================

class TestBaseStyle:
    """Test BaseStyle model."""

    def test_basic_creation(self):
        """Test basic BaseStyle creation."""
        style = BaseStyle(
            name="Test Style",
            medium_description="clean digital art",
            color_palette_base="warm pastels"
        )
        assert style.name == "Test Style"
        assert style.medium_description == "clean digital art"
        assert style.line_quality == LineQuality.MEDIUM  # default
        assert style.rendering_quality == RenderingQuality.HIGH  # default

    def test_full_creation(self):
        """Test BaseStyle with all fields."""
        style = BaseStyle(
            name="Custom Style",
            medium_description="painterly digital illustration",
            color_palette_base="rich jewel tones",
            line_quality=LineQuality.THICK,
            rendering_quality=RenderingQuality.ULTRA,
            style_keywords=["dramatic", "fantasy"],
            legacy_style_key="CUSTOM_STYLE"
        )
        assert style.name == "Custom Style"
        assert style.line_quality == LineQuality.THICK
        assert style.rendering_quality == RenderingQuality.ULTRA
        assert "dramatic" in style.style_keywords
        assert style.legacy_style_key == "CUSTOM_STYLE"

    def test_name_validation(self):
        """Test name field validation."""
        with pytest.raises(ValueError):
            BaseStyle(
                name="",  # Empty name should fail
                medium_description="test",
                color_palette_base="test"
            )


# ============================================================================
# SceneMood Tests
# ============================================================================

class TestSceneMood:
    """Test SceneMood model."""

    def test_default_creation(self):
        """Test SceneMood with defaults."""
        mood = SceneMood()
        assert mood.name == "neutral"
        assert mood.color_temperature == ColorTemperature.NEUTRAL
        assert mood.saturation == SaturationLevel.NORMAL
        assert mood.lighting_mood == LightingMood.SOFT
        assert mood.intensity == 5

    def test_custom_creation(self):
        """Test SceneMood with custom values."""
        mood = SceneMood(
            name="custom_romantic",
            color_temperature=ColorTemperature.WARM,
            saturation=SaturationLevel.HIGH,
            lighting_mood=LightingMood.GOLDEN_HOUR,
            detail_level=DetailLevel.FOCUS_CHARACTER,
            expression_style=ExpressionStyle.DRAMATIC,
            special_effects=[SpecialEffect.SPARKLES, SpecialEffect.BLOOM],
            intensity=9,
            accent_color="#FF69B4"
        )
        assert mood.name == "custom_romantic"
        assert mood.color_temperature == ColorTemperature.WARM
        assert mood.intensity == 9
        assert SpecialEffect.SPARKLES in mood.special_effects

    def test_intensity_bounds(self):
        """Test intensity is within 1-10."""
        mood = SceneMood(intensity=1)
        assert mood.intensity == 1

        mood = SceneMood(intensity=10)
        assert mood.intensity == 10

        with pytest.raises(ValueError):
            SceneMood(intensity=0)

        with pytest.raises(ValueError):
            SceneMood(intensity=11)

    def test_to_prompt_modifiers_neutral(self):
        """Test prompt generation for neutral mood."""
        mood = SceneMood()
        modifiers = mood.to_prompt_modifiers()
        assert "balanced color temperature" in modifiers
        assert "soft diffused lighting" in modifiers

    def test_to_prompt_modifiers_warm(self):
        """Test prompt generation for warm mood."""
        mood = SceneMood(
            color_temperature=ColorTemperature.WARM,
            lighting_mood=LightingMood.GOLDEN_HOUR
        )
        modifiers = mood.to_prompt_modifiers()
        assert "warm" in modifiers.lower() or "golden" in modifiers.lower()

    def test_to_prompt_modifiers_with_effects(self):
        """Test prompt generation with special effects."""
        mood = SceneMood(
            special_effects=[SpecialEffect.SPARKLES, SpecialEffect.BLOOM]
        )
        modifiers = mood.to_prompt_modifiers()
        assert "sparkle" in modifiers.lower()
        assert "bloom" in modifiers.lower()

    def test_to_prompt_modifiers_high_intensity(self):
        """Test prompt generation for high intensity."""
        mood = SceneMood(intensity=9)
        modifiers = mood.to_prompt_modifiers()
        assert "heightened" in modifiers.lower()

    def test_to_prompt_modifiers_low_intensity(self):
        """Test prompt generation for low intensity."""
        mood = SceneMood(intensity=2)
        modifiers = mood.to_prompt_modifiers()
        assert "calm" in modifiers.lower() or "subdued" in modifiers.lower()


# ============================================================================
# MOOD_PRESETS Tests
# ============================================================================

class TestMoodPresets:
    """Test mood presets dictionary."""

    def test_presets_exist(self):
        """Test that presets dictionary has entries."""
        assert len(MOOD_PRESETS) > 0
        assert "neutral" in MOOD_PRESETS
        assert "comedy" in MOOD_PRESETS
        assert "romantic_tension" in MOOD_PRESETS
        assert "serious_conflict" in MOOD_PRESETS

    def test_neutral_preset(self):
        """Test neutral preset configuration."""
        neutral = MOOD_PRESETS["neutral"]
        assert neutral.color_temperature == ColorTemperature.NEUTRAL
        assert neutral.intensity == 5

    def test_comedy_preset(self):
        """Test comedy preset configuration."""
        comedy = MOOD_PRESETS["comedy"]
        assert comedy.saturation == SaturationLevel.HIGH
        assert comedy.lighting_mood == LightingMood.BRIGHT
        assert comedy.expression_style == ExpressionStyle.EXAGGERATED

    def test_romantic_tension_preset(self):
        """Test romantic tension preset configuration."""
        romantic = MOOD_PRESETS["romantic_tension"]
        assert romantic.color_temperature == ColorTemperature.WARM
        assert romantic.lighting_mood == LightingMood.SOFT
        assert SpecialEffect.SPARKLES in romantic.special_effects

    def test_sad_emotional_preset(self):
        """Test sad emotional preset configuration."""
        sad = MOOD_PRESETS["sad_emotional"]
        assert sad.color_temperature == ColorTemperature.COOL
        assert sad.saturation == SaturationLevel.DESATURATED
        assert sad.lighting_mood == LightingMood.MOODY

    def test_flashback_preset(self):
        """Test flashback preset configuration."""
        flashback = MOOD_PRESETS["flashback"]
        assert flashback.saturation == SaturationLevel.DESATURATED
        assert SpecialEffect.SOFT_FOCUS in flashback.special_effects
        assert SpecialEffect.GRAIN in flashback.special_effects

    def test_climax_preset(self):
        """Test climax preset configuration."""
        climax = MOOD_PRESETS["climax"]
        assert climax.saturation == SaturationLevel.VIVID
        assert climax.lighting_mood == LightingMood.DRAMATIC
        assert climax.intensity == 10

    def test_all_presets_are_scene_mood(self):
        """Test all presets are SceneMood instances."""
        for name, preset in MOOD_PRESETS.items():
            assert isinstance(preset, SceneMood), f"{name} is not a SceneMood"


# ============================================================================
# Mood Utility Functions Tests
# ============================================================================

class TestMoodUtilityFunctions:
    """Test mood utility functions."""

    def test_get_mood_preset_exists(self):
        """Test getting existing preset."""
        mood = get_mood_preset("comedy")
        assert mood.name == "comedy"

    def test_get_mood_preset_not_found(self):
        """Test getting non-existent preset returns neutral."""
        mood = get_mood_preset("nonexistent")
        assert mood.name == "neutral"

    def test_get_mood_preset_case_insensitive(self):
        """Test preset lookup is case insensitive."""
        mood = get_mood_preset("COMEDY")
        assert mood.name == "comedy"

        mood = get_mood_preset("Romantic_Tension")
        assert mood.name == "romantic_tension"

    def test_list_mood_presets(self):
        """Test listing all mood presets."""
        presets = list_mood_presets()
        assert "neutral" in presets
        assert "comedy" in presets
        assert len(presets) >= 10

    def test_get_mood_for_intensity_romantic(self):
        """Test mood selection for romantic context."""
        mood = get_mood_for_intensity(8, "romantic")
        assert mood.name == "romantic_confession"

        mood = get_mood_for_intensity(5, "romantic")
        assert mood.name == "romantic_tension"

    def test_get_mood_for_intensity_conflict(self):
        """Test mood selection for conflict context."""
        mood = get_mood_for_intensity(8, "conflict")
        assert mood.name == "serious_conflict"

        mood = get_mood_for_intensity(5, "conflict")
        assert mood.name == "tense"

    def test_get_mood_for_intensity_sad(self):
        """Test mood selection for sad context."""
        mood = get_mood_for_intensity(7, "sad")
        assert mood.name == "sad_emotional"

    def test_get_mood_for_intensity_default(self):
        """Test mood selection with neutral context."""
        mood = get_mood_for_intensity(9, "neutral")
        assert mood.name == "climax"

        mood = get_mood_for_intensity(2, "neutral")
        assert mood.name == "peaceful"


# ============================================================================
# BASE_STYLES Tests
# ============================================================================

class TestBaseStyles:
    """Test base styles dictionary."""

    def test_base_styles_exist(self):
        """Test base styles dictionary has entries."""
        assert len(BASE_STYLES) > 0
        assert "soft_romantic" in BASE_STYLES
        assert "vibrant_fantasy" in BASE_STYLES
        assert "clean_modern" in BASE_STYLES

    def test_soft_romantic_style(self):
        """Test soft romantic base style."""
        style = BASE_STYLES["soft_romantic"]
        assert style.name == "Soft Romantic"
        assert "cel-shading" in style.medium_description.lower()
        assert style.legacy_style_key == "SOFT_ROMANTIC_WEBTOON"

    def test_emotive_luxury_style(self):
        """Test emotive luxury base style."""
        style = BASE_STYLES["emotive_luxury"]
        assert style.rendering_quality == RenderingQuality.ULTRA
        assert "luxury" in style.style_keywords

    def test_all_base_styles_have_legacy_key(self):
        """Test all base styles have legacy key for backward compatibility."""
        for name, style in BASE_STYLES.items():
            assert style.legacy_style_key is not None, f"{name} missing legacy_style_key"

    def test_get_base_style(self):
        """Test get_base_style function."""
        style = get_base_style("soft_romantic")
        assert style is not None
        assert style.name == "Soft Romantic"

    def test_get_base_style_normalized(self):
        """Test get_base_style with various name formats."""
        # Underscore
        style = get_base_style("soft_romantic")
        assert style is not None

        # Space
        style = get_base_style("soft romantic")
        assert style is not None

        # Hyphen
        style = get_base_style("soft-romantic")
        assert style is not None

        # Mixed case
        style = get_base_style("SOFT_ROMANTIC")
        assert style is not None

    def test_get_base_style_not_found(self):
        """Test get_base_style returns None for unknown style."""
        style = get_base_style("nonexistent_style")
        assert style is None

    def test_list_base_styles(self):
        """Test listing all base styles."""
        styles = list_base_styles()
        assert "soft_romantic" in styles
        assert "clean_modern" in styles
        assert len(styles) >= 5


# ============================================================================
# ComposedStyle Tests
# ============================================================================

class TestComposedStyle:
    """Test ComposedStyle model."""

    def test_basic_creation(self):
        """Test basic ComposedStyle creation."""
        composed = ComposedStyle(
            base_style=BASE_STYLES["soft_romantic"],
            scene_mood=MOOD_PRESETS["neutral"]
        )
        assert composed.base_style.name == "Soft Romantic"
        assert composed.scene_mood.name == "neutral"

    def test_to_prompt(self):
        """Test ComposedStyle prompt generation."""
        composed = ComposedStyle(
            base_style=BASE_STYLES["soft_romantic"],
            scene_mood=MOOD_PRESETS["romantic_tension"]
        )
        prompt = composed.to_prompt()

        assert "Soft Romantic" in prompt
        assert "romantic_tension" in prompt
        assert "cel-shading" in prompt.lower() or "gradient" in prompt.lower()

    def test_to_prompt_includes_mood_modifiers(self):
        """Test ComposedStyle prompt includes mood modifiers."""
        composed = ComposedStyle(
            base_style=BASE_STYLES["clean_modern"],
            scene_mood=SceneMood(
                name="test_mood",
                color_temperature=ColorTemperature.WARM,
                special_effects=[SpecialEffect.SPARKLES]
            )
        )
        prompt = composed.to_prompt()

        assert "warm" in prompt.lower() or "golden" in prompt.lower()
        assert "sparkle" in prompt.lower()

    def test_default_mood(self):
        """Test ComposedStyle uses neutral mood by default."""
        composed = ComposedStyle(
            base_style=BASE_STYLES["soft_romantic"]
        )
        assert composed.scene_mood.name == "neutral"


# ============================================================================
# Integration Tests
# ============================================================================

class TestStyleSystemIntegration:
    """Integration tests for the style system."""

    def test_full_style_composition_workflow(self):
        """Test complete workflow of style composition."""
        # 1. Get base style
        base = get_base_style("soft_romantic")
        assert base is not None

        # 2. Get mood for scene
        mood = get_mood_for_intensity(8, "romantic")
        assert mood.name == "romantic_confession"

        # 3. Compose
        composed = ComposedStyle(base_style=base, scene_mood=mood)

        # 4. Generate prompt
        prompt = composed.to_prompt()
        assert len(prompt) > 50
        assert "Soft Romantic" in prompt

    def test_multiple_scenes_different_moods(self):
        """Test same base style with different scene moods."""
        base = BASE_STYLES["clean_modern"]

        # Scene 1: Comedy
        comedy_composed = ComposedStyle(
            base_style=base,
            scene_mood=MOOD_PRESETS["comedy"]
        )
        comedy_prompt = comedy_composed.to_prompt()

        # Scene 2: Serious
        serious_composed = ComposedStyle(
            base_style=base,
            scene_mood=MOOD_PRESETS["serious_conflict"]
        )
        serious_prompt = serious_composed.to_prompt()

        # Both should have same base style info
        assert "Clean Modern" in comedy_prompt
        assert "Clean Modern" in serious_prompt

        # But different mood modifiers
        assert "bright" in comedy_prompt.lower() or "exaggerated" in comedy_prompt.lower()
        assert "dramatic" in serious_prompt.lower()

    def test_mood_prompt_modifiers_all_presets(self):
        """Test all presets generate valid prompt modifiers."""
        for name, mood in MOOD_PRESETS.items():
            modifiers = mood.to_prompt_modifiers()
            assert isinstance(modifiers, str), f"{name} didn't return string"
            # Most moods should generate some modifiers
            if name != "neutral":
                assert len(modifiers) > 0, f"{name} generated empty modifiers"
