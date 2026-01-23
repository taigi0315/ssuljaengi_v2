"""
Unit tests for the Mood Designer Service.

Tests the automatic mood assignment functionality for webtoon panels.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.services.mood_designer import (
    MoodDesigner,
    MoodAssignment,
    detect_context_from_text,
    detect_intensity_modifier,
    get_shot_type_mood_bias,
    create_mood_designer,
    assign_moods_to_panels,
    get_mood_for_panel,
    mood_designer,
)
from app.models.story import WebtoonPanel
from app.models.style import (
    SceneMood,
    MOOD_PRESETS,
    ColorTemperature,
    SaturationLevel,
    LightingMood,
    DetailLevel,
    ExpressionStyle,
    SpecialEffect,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def neutral_panel():
    """Panel with neutral content."""
    return WebtoonPanel(
        panel_number=1,
        shot_type="Medium Shot",
        active_character_names=["Ji-hoon"],
        visual_prompt="Ji-hoon walking down a street, normal afternoon",
        dialogue=[{"character": "Ji-hoon", "text": "I should head home."}],
    )


@pytest.fixture
def romantic_panel():
    """Panel with romantic content."""
    return WebtoonPanel(
        panel_number=2,
        shot_type="Close-up",
        active_character_names=["Ji-hoon", "Min-ji"],
        visual_prompt="Ji-hoon and Min-ji gazing into each other's eyes, their faces close, blushing",
        dialogue=[{"character": "Ji-hoon", "text": "I love you."}],
        emotional_intensity=9,
    )


@pytest.fixture
def sad_panel():
    """Panel with sad content."""
    return WebtoonPanel(
        panel_number=3,
        shot_type="Medium Shot",
        active_character_names=["Min-ji"],
        visual_prompt="Min-ji sitting alone, tears streaming down her face",
        dialogue=[{"character": "Min-ji", "text": "I miss him so much..."}],
        emotional_intensity=8,
    )


@pytest.fixture
def action_panel():
    """Panel with action content."""
    return WebtoonPanel(
        panel_number=4,
        shot_type="Wide Shot",
        active_character_names=["Ji-hoon"],
        visual_prompt="Ji-hoon running fast through the rain, chasing after the car",
        dialogue=[],
        emotional_intensity=7,
    )


@pytest.fixture
def comedy_panel():
    """Panel with comedy content."""
    return WebtoonPanel(
        panel_number=5,
        shot_type="Medium Shot",
        active_character_names=["Ji-hoon"],
        visual_prompt="Ji-hoon with a funny surprised expression, embarrassed",
        dialogue=[{"character": "Ji-hoon", "text": "Wait, that was a joke?!"}],
        emotional_intensity=5,
    )


@pytest.fixture
def conflict_panel():
    """Panel with conflict content."""
    return WebtoonPanel(
        panel_number=6,
        shot_type="Close-up",
        active_character_names=["Ji-hoon", "rival"],
        visual_prompt="Ji-hoon and his rival confronting each other, tension in the air",
        dialogue=[{"character": "Ji-hoon", "text": "How dare you challenge me!"}],
        emotional_intensity=8,
    )


@pytest.fixture
def flashback_panel():
    """Panel with flashback content."""
    return WebtoonPanel(
        panel_number=7,
        shot_type="Wide Shot",
        active_character_names=["young Ji-hoon"],
        visual_prompt="A memory from the past, young Ji-hoon as a child",
        dialogue=[{"character": "narrator", "text": "I remember when I was younger..."}],
        emotional_intensity=4,
    )


@pytest.fixture
def multiple_panels(neutral_panel, romantic_panel, sad_panel):
    """Multiple panels for testing."""
    return [neutral_panel, romantic_panel, sad_panel]


# ============================================================================
# Context Detection Tests
# ============================================================================

class TestContextDetection:
    """Test context detection functions."""

    def test_detect_romantic_context(self):
        """Test detection of romantic context."""
        text = "She looked at him with love in her eyes, her heart racing"
        context, confidence = detect_context_from_text(text)
        assert context == "romantic"
        assert confidence > 0.5

    def test_detect_conflict_context(self):
        """Test detection of conflict context."""
        text = "They argued fiercely, shouting at each other in anger"
        context, confidence = detect_context_from_text(text)
        assert context == "conflict"
        assert confidence > 0.5

    def test_detect_sad_context(self):
        """Test detection of sad context."""
        text = "Tears fell as she grieved over her loss, feeling so lonely"
        context, confidence = detect_context_from_text(text)
        assert context == "sad"
        assert confidence > 0.5

    def test_detect_comedy_context(self):
        """Test detection of comedy context."""
        text = "He made a funny face, causing everyone to laugh at the joke"
        context, confidence = detect_context_from_text(text)
        assert context == "comedy"
        assert confidence > 0.5

    def test_detect_action_context(self):
        """Test detection of action context."""
        text = "He ran fast, dodging attacks and jumping over obstacles"
        context, confidence = detect_context_from_text(text)
        assert context == "action"
        assert confidence > 0.5

    def test_detect_mystery_context(self):
        """Test detection of mystery context."""
        text = "Something strange was hidden in the shadows, a secret waiting"
        context, confidence = detect_context_from_text(text)
        assert context == "mystery"
        assert confidence > 0.5

    def test_detect_neutral_for_empty(self):
        """Test empty text returns neutral."""
        context, confidence = detect_context_from_text("")
        assert context == "neutral"
        assert confidence == 0.5

    def test_detect_neutral_for_no_keywords(self):
        """Test text without keywords returns neutral."""
        context, confidence = detect_context_from_text("The sky was blue")
        assert context == "neutral"


class TestIntensityModifier:
    """Test intensity modifier detection."""

    def test_high_intensity_keywords(self):
        """Test high intensity keywords."""
        text = "He was extremely passionate about it"
        modifier = detect_intensity_modifier(text)
        assert modifier > 0

    def test_low_intensity_keywords(self):
        """Test low intensity keywords."""
        text = "She felt slightly nervous"
        modifier = detect_intensity_modifier(text)
        assert modifier < 0

    def test_no_modifier_for_neutral(self):
        """Test neutral text has no modifier."""
        text = "He walked to the store"
        modifier = detect_intensity_modifier(text)
        assert modifier == 0

    def test_empty_text(self):
        """Test empty text returns 0."""
        modifier = detect_intensity_modifier("")
        assert modifier == 0


class TestShotTypeBias:
    """Test shot type mood bias."""

    def test_close_up_bias(self):
        """Test close-up shot bias."""
        bias = get_shot_type_mood_bias("Close-up")
        assert bias["detail_level"] == DetailLevel.FOCUS_CHARACTER
        assert bias["expression_style"] == ExpressionStyle.DRAMATIC
        assert bias["intensity_boost"] > 0

    def test_wide_shot_bias(self):
        """Test wide shot bias."""
        bias = get_shot_type_mood_bias("Wide Shot")
        assert bias["detail_level"] == DetailLevel.HIGH
        assert bias["intensity_boost"] < 0

    def test_medium_shot_bias(self):
        """Test medium shot bias."""
        bias = get_shot_type_mood_bias("Medium Shot")
        assert bias["detail_level"] == DetailLevel.STANDARD
        assert bias["intensity_boost"] == 0

    def test_unknown_shot_type(self):
        """Test unknown shot type returns defaults."""
        bias = get_shot_type_mood_bias("Unknown")
        assert bias["detail_level"] == DetailLevel.STANDARD
        assert bias["intensity_boost"] == 0


# ============================================================================
# MoodAssignment Tests
# ============================================================================

class TestMoodAssignment:
    """Test MoodAssignment class."""

    def test_basic_creation(self):
        """Test basic MoodAssignment creation."""
        mood = MOOD_PRESETS["neutral"]
        assignment = MoodAssignment(
            panel_number=1,
            mood=mood,
            detected_context="neutral",
            confidence=0.8,
            reasoning="Test reasoning"
        )
        assert assignment.panel_number == 1
        assert assignment.mood == mood
        assert assignment.detected_context == "neutral"
        assert assignment.confidence == 0.8

    def test_to_dict(self):
        """Test MoodAssignment to_dict conversion."""
        mood = MOOD_PRESETS["romantic_tension"]
        assignment = MoodAssignment(
            panel_number=2,
            mood=mood,
            detected_context="romantic",
            confidence=0.9,
            reasoning="Romantic moment"
        )

        result = assignment.to_dict()

        assert result["panel_number"] == 2
        assert result["mood_name"] == "romantic_tension"
        assert result["detected_context"] == "romantic"
        assert result["confidence"] == 0.9
        assert "mood_settings" in result


# ============================================================================
# MoodDesigner Tests
# ============================================================================

class TestMoodDesignerInit:
    """Test MoodDesigner initialization."""

    def test_default_init(self):
        """Test default initialization."""
        designer = MoodDesigner()
        assert designer._use_llm is False
        assert designer._llm_client is None

    def test_init_with_llm(self):
        """Test initialization with LLM."""
        mock_client = MagicMock()
        designer = MoodDesigner(use_llm=True, llm_client=mock_client)
        assert designer._use_llm is True
        assert designer._llm_client == mock_client

    def test_factory_function(self):
        """Test factory function."""
        designer = create_mood_designer()
        assert isinstance(designer, MoodDesigner)

    def test_global_instance(self):
        """Test global instance exists."""
        assert mood_designer is not None
        assert isinstance(mood_designer, MoodDesigner)


class TestMoodDesignerAssignment:
    """Test MoodDesigner mood assignment."""

    def test_assign_single_panel(self, neutral_panel):
        """Test assigning mood to single panel."""
        designer = MoodDesigner()
        assignments = designer.assign_moods([neutral_panel])

        assert len(assignments) == 1
        assert assignments[0].panel_number == 1
        assert isinstance(assignments[0].mood, SceneMood)

    def test_assign_multiple_panels(self, multiple_panels):
        """Test assigning moods to multiple panels."""
        designer = MoodDesigner()
        assignments = designer.assign_moods(multiple_panels)

        assert len(assignments) == 3
        for i, assignment in enumerate(assignments):
            assert assignment.panel_number == multiple_panels[i].panel_number

    def test_romantic_panel_gets_romantic_mood(self, romantic_panel):
        """Test romantic panel gets appropriate mood."""
        designer = MoodDesigner()
        assignments = designer.assign_moods([romantic_panel])

        assert assignments[0].detected_context == "romantic"
        # High intensity romantic should have sparkles
        assert assignments[0].mood.intensity >= 7

    def test_sad_panel_gets_sad_mood(self, sad_panel):
        """Test sad panel gets appropriate mood."""
        designer = MoodDesigner()
        assignments = designer.assign_moods([sad_panel])

        assert assignments[0].detected_context == "sad"
        # Sad mood should have cooler temperature or vignette
        mood = assignments[0].mood
        assert (
            mood.color_temperature in [ColorTemperature.COOL, ColorTemperature.VERY_COOL] or
            SpecialEffect.VIGNETTE in mood.special_effects
        )

    def test_action_panel_gets_action_mood(self, action_panel):
        """Test action panel gets appropriate mood."""
        designer = MoodDesigner()
        assignments = designer.assign_moods([action_panel])

        assert assignments[0].detected_context == "action"

    def test_comedy_panel_gets_comedy_mood(self, comedy_panel):
        """Test comedy panel gets appropriate mood."""
        designer = MoodDesigner()
        assignments = designer.assign_moods([comedy_panel])

        assert assignments[0].detected_context == "comedy"

    def test_conflict_panel_gets_conflict_mood(self, conflict_panel):
        """Test conflict panel gets appropriate mood."""
        designer = MoodDesigner()
        assignments = designer.assign_moods([conflict_panel])

        assert assignments[0].detected_context == "conflict"
        # Conflict should have dramatic lighting
        assert assignments[0].mood.lighting_mood in [LightingMood.DRAMATIC, LightingMood.HARSH]

    def test_flashback_panel_gets_flashback_mood(self, flashback_panel):
        """Test flashback panel gets appropriate mood."""
        designer = MoodDesigner()
        assignments = designer.assign_moods([flashback_panel])

        assert assignments[0].detected_context == "flashback"
        # Flashback should have grain or soft focus
        effects = assignments[0].mood.special_effects
        assert (
            SpecialEffect.GRAIN in effects or
            SpecialEffect.SOFT_FOCUS in effects
        )


class TestMoodDesignerTransitions:
    """Test mood transition smoothing."""

    def test_smooth_intensity_jump(self):
        """Test that large intensity jumps are smoothed."""
        designer = MoodDesigner()

        # Create panels with big intensity difference
        panels = [
            WebtoonPanel(
                panel_number=1,
                shot_type="Medium Shot",
                visual_prompt="Calm scene",
                emotional_intensity=2,
            ),
            WebtoonPanel(
                panel_number=2,
                shot_type="Close-up",
                visual_prompt="Extremely passionate confession, overwhelming love",
                emotional_intensity=10,
            ),
        ]

        assignments = designer.assign_moods(panels)

        # The transition should be somewhat smoothed
        intensity_diff = abs(assignments[1].mood.intensity - assignments[0].mood.intensity)
        # Should be smoothed to at most 5 (not jumping from 2 to 10)
        assert intensity_diff <= 6


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_assign_moods_to_panels(self, multiple_panels):
        """Test assign_moods_to_panels function."""
        assignments = assign_moods_to_panels(multiple_panels)

        assert len(assignments) == 3
        assert all(isinstance(a, MoodAssignment) for a in assignments)

    def test_get_mood_for_panel(self, romantic_panel):
        """Test get_mood_for_panel function."""
        mood = get_mood_for_panel(romantic_panel)

        assert isinstance(mood, SceneMood)


# ============================================================================
# Integration Tests
# ============================================================================

class TestMoodDesignerIntegration:
    """Integration tests for mood designer."""

    def test_full_workflow(self):
        """Test complete mood assignment workflow."""
        panels = [
            WebtoonPanel(
                panel_number=1,
                shot_type="Wide Shot",
                visual_prompt="Establishing shot of the city",
                emotional_intensity=3,
            ),
            WebtoonPanel(
                panel_number=2,
                shot_type="Medium Shot",
                visual_prompt="Ji-hoon walking, looking worried",
                dialogue=[{"character": "Ji-hoon", "text": "I'm nervous about meeting her"}],
                emotional_intensity=5,
            ),
            WebtoonPanel(
                panel_number=3,
                shot_type="Close-up",
                visual_prompt="Min-ji smiling, her eyes sparkling with love",
                dialogue=[{"character": "Min-ji", "text": "I've been waiting for you"}],
                emotional_intensity=7,
            ),
            WebtoonPanel(
                panel_number=4,
                shot_type="Close-up",
                visual_prompt="Their faces close, intimate moment, blushing",
                dialogue=[],
                emotional_intensity=9,
            ),
        ]

        designer = MoodDesigner()
        assignments = designer.assign_moods(panels)

        assert len(assignments) == 4

        # Verify progression
        # First panel should be lower intensity
        assert assignments[0].mood.intensity <= 5

        # Last panels should be higher intensity (romantic)
        assert assignments[3].mood.intensity >= 7
        assert assignments[3].detected_context == "romantic"

    def test_all_panel_types_get_moods(
        self,
        neutral_panel,
        romantic_panel,
        sad_panel,
        action_panel,
        comedy_panel,
        conflict_panel,
        flashback_panel
    ):
        """Test all panel types get appropriate moods."""
        all_panels = [
            neutral_panel,
            romantic_panel,
            sad_panel,
            action_panel,
            comedy_panel,
            conflict_panel,
            flashback_panel,
        ]

        designer = MoodDesigner()
        assignments = designer.assign_moods(all_panels)

        assert len(assignments) == 7

        # Each should have a valid mood
        for assignment in assignments:
            assert isinstance(assignment.mood, SceneMood)
            assert 1 <= assignment.mood.intensity <= 10
            assert len(assignment.reasoning) > 0

    def test_mood_has_prompt_modifiers(self, romantic_panel):
        """Test that assigned mood can generate prompt modifiers."""
        designer = MoodDesigner()
        assignments = designer.assign_moods([romantic_panel])

        mood = assignments[0].mood
        modifiers = mood.to_prompt_modifiers()

        assert isinstance(modifiers, str)
        assert len(modifiers) > 0


class TestMoodDesignerEdgeCases:
    """Test edge cases."""

    def test_empty_panel_list(self):
        """Test with empty panel list."""
        designer = MoodDesigner()
        assignments = designer.assign_moods([])

        assert len(assignments) == 0

    def test_panel_without_dialogue(self):
        """Test panel without dialogue."""
        panel = WebtoonPanel(
            panel_number=1,
            shot_type="Wide Shot",
            visual_prompt="Silent scene, beautiful sunset",
            dialogue=[],
        )

        designer = MoodDesigner()
        assignments = designer.assign_moods([panel])

        assert len(assignments) == 1
        assert isinstance(assignments[0].mood, SceneMood)

    def test_panel_without_visual_prompt(self):
        """Test panel without visual prompt."""
        panel = WebtoonPanel(
            panel_number=1,
            shot_type="Medium Shot",
            dialogue=[{"character": "test", "text": "Hello world"}],
        )

        designer = MoodDesigner()
        assignments = designer.assign_moods([panel])

        assert len(assignments) == 1

    def test_panel_with_high_intensity(self):
        """Test panel with maximum intensity."""
        panel = WebtoonPanel(
            panel_number=1,
            shot_type="Close-up",
            visual_prompt="Climactic moment, extremely intense",
            emotional_intensity=10,
        )

        designer = MoodDesigner()
        assignments = designer.assign_moods([panel])

        assert assignments[0].mood.intensity >= 8

    def test_panel_with_low_intensity(self):
        """Test panel with minimum intensity."""
        panel = WebtoonPanel(
            panel_number=1,
            shot_type="Wide Shot",
            visual_prompt="Calm, peaceful morning",
            emotional_intensity=1,
        )

        designer = MoodDesigner()
        assignments = designer.assign_moods([panel])

        assert assignments[0].mood.intensity <= 4
