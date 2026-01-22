"""
Unit tests for SFX models.

Tests the SFX data models for impact text, motion effects, screen effects,
emotional effects, and SFX bundles.
"""

import pytest
from app.models.sfx import (
    # Enums
    ImpactTextStyle,
    ImpactTextSize,
    ImpactTextAnimation,
    MotionEffectType,
    MotionDirection,
    EffectIntensity,
    ScreenEffectType,
    EmotionalEffectType,
    EmotionalEffectPosition,
    EmotionalEffectAnimation,
    SFXTiming,
    # Models
    ImpactText,
    MotionEffect,
    ScreenEffect,
    EmotionalEffect,
    SFXBundle,
    # Utilities
    SFX_TRIGGERS,
    get_suggested_sfx,
)


class TestEnums:
    """Test SFX enums."""

    def test_impact_text_styles(self):
        """Test impact text style enum values."""
        assert ImpactTextStyle.BOLD.value == "bold"
        assert ImpactTextStyle.EXPLOSIVE.value == "explosive"
        assert ImpactTextStyle.SHAKY.value == "shaky"

    def test_impact_text_sizes(self):
        """Test impact text size enum values."""
        assert ImpactTextSize.SMALL.value == "small"
        assert ImpactTextSize.MASSIVE.value == "massive"

    def test_motion_effect_types(self):
        """Test motion effect type enum values."""
        assert MotionEffectType.SPEED_LINES.value == "speed_lines"
        assert MotionEffectType.IMPACT_BURST.value == "impact_burst"
        assert MotionEffectType.ZOOM_LINES.value == "zoom_lines"

    def test_screen_effect_types(self):
        """Test screen effect type enum values."""
        assert ScreenEffectType.FLASH.value == "flash"
        assert ScreenEffectType.SHAKE.value == "shake"
        assert ScreenEffectType.VIGNETTE.value == "vignette"

    def test_emotional_effect_types(self):
        """Test emotional effect type enum values."""
        assert EmotionalEffectType.SPARKLES.value == "sparkles"
        assert EmotionalEffectType.HEARTS.value == "hearts"
        assert EmotionalEffectType.DARK_AURA.value == "dark_aura"
        assert EmotionalEffectType.SWEAT_DROP.value == "sweat_drop"

    def test_sfx_timing(self):
        """Test SFX timing enum values."""
        assert SFXTiming.ON_ENTER.value == "on_enter"
        assert SFXTiming.WITH_DIALOGUE.value == "with_dialogue"
        assert SFXTiming.CONTINUOUS.value == "continuous"


class TestImpactText:
    """Test ImpactText model."""

    def test_basic_creation(self):
        """Test basic impact text creation."""
        impact = ImpactText(text="CRASH!")
        assert impact.text == "CRASH!"
        assert impact.style == ImpactTextStyle.BOLD  # default
        assert impact.size == ImpactTextSize.MEDIUM  # default

    def test_full_creation(self):
        """Test impact text with all fields."""
        impact = ImpactText(
            text="POW!",
            style=ImpactTextStyle.EXPLOSIVE,
            position=(0.8, 0.2),
            size=ImpactTextSize.LARGE,
            color="#FF0000",
            outline_color="#000000",
            rotation=-15,
            animation=ImpactTextAnimation.POP,
            timing=SFXTiming.ON_ENTER,
            duration_ms=600
        )
        assert impact.text == "POW!"
        assert impact.style == ImpactTextStyle.EXPLOSIVE
        assert impact.position == (0.8, 0.2)
        assert impact.size == ImpactTextSize.LARGE
        assert impact.color == "#FF0000"
        assert impact.rotation == -15

    def test_position_tuple(self):
        """Test position is properly handled as tuple."""
        impact = ImpactText(text="!", position=(0.5, 0.5))
        assert impact.position[0] == 0.5
        assert impact.position[1] == 0.5

    def test_text_validation(self):
        """Test text field validation."""
        # Min length
        with pytest.raises(ValueError):
            ImpactText(text="")

    def test_rotation_bounds(self):
        """Test rotation is within bounds."""
        impact = ImpactText(text="!", rotation=45)
        assert impact.rotation == 45

        impact = ImpactText(text="!", rotation=-45)
        assert impact.rotation == -45

    def test_duration_bounds(self):
        """Test duration is within bounds."""
        impact = ImpactText(text="!", duration_ms=100)
        assert impact.duration_ms == 100

        impact = ImpactText(text="!", duration_ms=3000)
        assert impact.duration_ms == 3000


class TestMotionEffect:
    """Test MotionEffect model."""

    def test_basic_creation(self):
        """Test basic motion effect creation."""
        motion = MotionEffect(type=MotionEffectType.SPEED_LINES)
        assert motion.type == MotionEffectType.SPEED_LINES
        assert motion.direction == MotionDirection.CENTER  # default
        assert motion.intensity == EffectIntensity.MEDIUM  # default

    def test_full_creation(self):
        """Test motion effect with all fields."""
        motion = MotionEffect(
            type=MotionEffectType.IMPACT_BURST,
            direction=MotionDirection.RADIAL,
            intensity=EffectIntensity.INTENSE,
            duration_ms=500,
            timing=SFXTiming.ON_ENTER,
            color="#FFFFFF",
            opacity=0.9
        )
        assert motion.type == MotionEffectType.IMPACT_BURST
        assert motion.direction == MotionDirection.RADIAL
        assert motion.intensity == EffectIntensity.INTENSE
        assert motion.opacity == 0.9

    def test_opacity_bounds(self):
        """Test opacity is within 0-1."""
        motion = MotionEffect(type=MotionEffectType.BLUR, opacity=0.0)
        assert motion.opacity == 0.0

        motion = MotionEffect(type=MotionEffectType.BLUR, opacity=1.0)
        assert motion.opacity == 1.0


class TestScreenEffect:
    """Test ScreenEffect model."""

    def test_basic_creation(self):
        """Test basic screen effect creation."""
        screen = ScreenEffect(type=ScreenEffectType.FLASH)
        assert screen.type == ScreenEffectType.FLASH
        assert screen.intensity == EffectIntensity.MEDIUM  # default

    def test_full_creation(self):
        """Test screen effect with all fields."""
        screen = ScreenEffect(
            type=ScreenEffectType.COLOR_SHIFT,
            intensity=EffectIntensity.SUBTLE,
            duration_ms=300,
            timing=SFXTiming.CONTINUOUS,
            color="#FF6666"
        )
        assert screen.type == ScreenEffectType.COLOR_SHIFT
        assert screen.color == "#FF6666"

    def test_shake_effect(self):
        """Test shake effect specifically."""
        shake = ScreenEffect(
            type=ScreenEffectType.SHAKE,
            intensity=EffectIntensity.INTENSE,
            duration_ms=200
        )
        assert shake.type == ScreenEffectType.SHAKE
        assert shake.duration_ms == 200


class TestEmotionalEffect:
    """Test EmotionalEffect model."""

    def test_basic_creation(self):
        """Test basic emotional effect creation."""
        effect = EmotionalEffect(type=EmotionalEffectType.SPARKLES)
        assert effect.type == EmotionalEffectType.SPARKLES
        assert effect.position == EmotionalEffectPosition.AROUND_CHARACTER  # default
        assert effect.animation == EmotionalEffectAnimation.FLOAT  # default

    def test_full_creation(self):
        """Test emotional effect with all fields."""
        effect = EmotionalEffect(
            type=EmotionalEffectType.DARK_AURA,
            position=EmotionalEffectPosition.BACKGROUND,
            animation=EmotionalEffectAnimation.PULSE,
            intensity=EffectIntensity.INTENSE,
            timing=SFXTiming.CONTINUOUS,
            duration_ms=2000,
            color="#440044"
        )
        assert effect.type == EmotionalEffectType.DARK_AURA
        assert effect.position == EmotionalEffectPosition.BACKGROUND
        assert effect.animation == EmotionalEffectAnimation.PULSE

    def test_face_position(self):
        """Test face-positioned effect (like blush)."""
        blush = EmotionalEffect(
            type=EmotionalEffectType.BLUSH,
            position=EmotionalEffectPosition.FACE
        )
        assert blush.position == EmotionalEffectPosition.FACE


class TestSFXBundle:
    """Test SFXBundle model."""

    def test_empty_bundle(self):
        """Test empty bundle creation."""
        bundle = SFXBundle(panel_number=1)
        assert bundle.panel_number == 1
        assert bundle.total_effects == 0
        assert bundle.has_effects is False
        assert bundle.get_all_effects() == []

    def test_bundle_with_effects(self):
        """Test bundle with multiple effects."""
        impact = ImpactText(text="BOOM!")
        motion = MotionEffect(type=MotionEffectType.IMPACT_BURST)
        screen = ScreenEffect(type=ScreenEffectType.SHAKE)
        emotional = EmotionalEffect(type=EmotionalEffectType.SHOCK_LINES)

        bundle = SFXBundle(
            panel_number=5,
            impact_texts=[impact],
            motion_effects=[motion],
            screen_effects=[screen],
            emotional_effects=[emotional]
        )

        assert bundle.total_effects == 4
        assert bundle.has_effects is True
        assert len(bundle.get_all_effects()) == 4

    def test_bundle_multiple_same_type(self):
        """Test bundle with multiple effects of same type."""
        impacts = [
            ImpactText(text="CRASH!"),
            ImpactText(text="BANG!"),
            ImpactText(text="POW!")
        ]
        bundle = SFXBundle(panel_number=1, impact_texts=impacts)

        assert bundle.total_effects == 3
        assert len(bundle.impact_texts) == 3

    def test_get_all_effects_order(self):
        """Test that get_all_effects returns effects in expected order."""
        impact = ImpactText(text="!")
        motion = MotionEffect(type=MotionEffectType.BLUR)
        screen = ScreenEffect(type=ScreenEffectType.FLASH)
        emotional = EmotionalEffect(type=EmotionalEffectType.GLOW)

        bundle = SFXBundle(
            panel_number=1,
            impact_texts=[impact],
            motion_effects=[motion],
            screen_effects=[screen],
            emotional_effects=[emotional]
        )

        all_effects = bundle.get_all_effects()
        assert all_effects[0] == impact
        assert all_effects[1] == motion
        assert all_effects[2] == screen
        assert all_effects[3] == emotional


class TestSFXTriggers:
    """Test SFX trigger mapping."""

    def test_triggers_exist(self):
        """Test that triggers dictionary exists and has entries."""
        assert len(SFX_TRIGGERS) > 0
        assert "anger" in SFX_TRIGGERS
        assert "love" in SFX_TRIGGERS
        assert "impact" in SFX_TRIGGERS

    def test_anger_triggers(self):
        """Test anger has appropriate suggestions."""
        anger = SFX_TRIGGERS["anger"]
        assert len(anger) > 0
        # Should have dark_aura or speed_lines for anger
        effect_types = [e.get("effect") for e in anger]
        assert "dark_aura" in effect_types or "speed_lines" in effect_types

    def test_love_triggers(self):
        """Test love has appropriate suggestions."""
        love = SFX_TRIGGERS["love"]
        assert len(love) > 0
        effect_types = [e.get("effect") for e in love]
        assert "sparkles" in effect_types or "hearts" in effect_types

    def test_impact_triggers(self):
        """Test impact has appropriate suggestions."""
        impact = SFX_TRIGGERS["impact"]
        assert len(impact) > 0
        # Should have impact text
        has_impact_text = any(e.get("type") == "impact_text" for e in impact)
        assert has_impact_text


class TestGetSuggestedSfx:
    """Test get_suggested_sfx function."""

    def test_known_emotion(self):
        """Test getting suggestions for known emotion."""
        suggestions = get_suggested_sfx("anger")
        assert len(suggestions) > 0

    def test_unknown_emotion(self):
        """Test getting suggestions for unknown emotion."""
        suggestions = get_suggested_sfx("nonexistent_emotion")
        assert suggestions == []

    def test_case_insensitive(self):
        """Test that lookup is case insensitive."""
        lower = get_suggested_sfx("anger")
        upper = get_suggested_sfx("ANGER")
        mixed = get_suggested_sfx("Anger")

        assert lower == upper == mixed

    def test_action_suggestions(self):
        """Test getting suggestions for actions."""
        punch = get_suggested_sfx("punch")
        assert len(punch) > 0

        run = get_suggested_sfx("run")
        assert len(run) > 0
