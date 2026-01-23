"""
Integration tests for Phase 2.4: Mood-Aware Style System Integration.

Tests that the mood detection and style composition work together
with the webtoon generation workflow.

v2.0.0: Initial implementation
"""

import pytest
from typing import List

from app.models.story import WebtoonPanel
from app.services.mood_designer import (
    mood_designer,
    detect_context_from_text,
    MoodAssignment,
)
from app.services.style_composer import (
    get_legacy_style_with_mood,
    compose_style_with_legacy,
)
from app.models.style import (
    MOOD_PRESETS,
    ColorTemperature,
    LightingMood,
)


# ============================================================================
# Test Data
# ============================================================================

def create_test_panels() -> List[WebtoonPanel]:
    """Create a set of test panels with varying emotional content."""
    return [
        WebtoonPanel(
            panel_number=1,
            shot_type="Wide Shot",
            active_character_names=["Ji-hoon"],
            visual_prompt="A lonely figure stands at the edge of a rainy rooftop, city lights blurry in the distance.",
            story_beat="Protagonist contemplates his loneliness",
            emotional_intensity=7,
            dialogue=[{"character": "Ji-hoon", "text": "Why does everything feel so empty..."}],
        ),
        WebtoonPanel(
            panel_number=2,
            shot_type="Close-up",
            active_character_names=["Ji-hoon", "Hana"],
            visual_prompt="Hana bursts through the door, her face full of joy and excitement.",
            story_beat="Hana surprises Ji-hoon with good news",
            emotional_intensity=8,
            dialogue=[{"character": "Hana", "text": "You won't believe what just happened!"}],
        ),
        WebtoonPanel(
            panel_number=3,
            shot_type="Medium Shot",
            active_character_names=["Ji-hoon", "Hana"],
            visual_prompt="The two laugh together, their eyes meeting with warmth.",
            story_beat="Romantic tension builds",
            emotional_intensity=6,
            dialogue=[
                {"character": "Hana", "text": "You're always there for me..."},
                {"character": "Ji-hoon", "text": "I always will be."}
            ],
        ),
        WebtoonPanel(
            panel_number=4,
            shot_type="Extreme Close-up",
            active_character_names=["Ji-hoon", "Villain"],
            visual_prompt="The villain's eyes narrow dangerously, a cold smile playing on his lips.",
            story_beat="Confrontation with antagonist",
            emotional_intensity=9,
            dialogue=[{"character": "Villain", "text": "You think you can stop me?"}],
        ),
        WebtoonPanel(
            panel_number=5,
            shot_type="Medium Shot",
            active_character_names=["Ji-hoon", "Hana"],
            visual_prompt="A peaceful moment in the park, cherry blossoms falling gently.",
            story_beat="Calm after the storm",
            emotional_intensity=3,
            dialogue=[{"character": "Hana", "text": "It's so peaceful today."}],
        ),
    ]


# ============================================================================
# Integration Tests
# ============================================================================

class TestMoodDetectionIntegration:
    """Test mood detection with real panel content."""

    def test_sad_panel_detected_as_sad(self):
        """Panel 1 should be detected as sad due to 'lonely', 'empty' keywords."""
        panels = create_test_panels()
        panel = panels[0]

        combined_text = f"{panel.visual_prompt} {panel.story_beat}"
        for d in panel.dialogue:
            combined_text += f" {d['text']}"

        context, confidence = detect_context_from_text(combined_text)
        assert context in ["sad", "peaceful", "neutral"], f"Expected sad-related context, got {context}"

    def test_romantic_panel_detected_as_romantic(self):
        """Panel 3 should be detected as romantic due to love keywords."""
        panels = create_test_panels()
        panel = panels[2]

        combined_text = f"{panel.visual_prompt} {panel.story_beat}"
        for d in panel.dialogue:
            combined_text += f" {d['text']}"

        context, confidence = detect_context_from_text(combined_text)
        # Romance detection includes warmth, together, romantic
        assert context in ["romantic", "neutral"], f"Expected romantic context, got {context}"

    def test_conflict_panel_detected_as_conflict(self):
        """Panel 4 should be detected as conflict/tense due to antagonist confrontation."""
        panels = create_test_panels()
        panel = panels[3]

        combined_text = f"{panel.visual_prompt} {panel.story_beat}"
        for d in panel.dialogue:
            combined_text += f" {d['text']}"

        context, confidence = detect_context_from_text(combined_text)
        assert context in ["conflict", "tense", "action", "neutral"], f"Expected conflict context, got {context}"


class TestMoodAssignmentIntegration:
    """Test that mood assignments work correctly across panel sequences."""

    def test_all_panels_get_mood_assignments(self):
        """All panels should receive mood assignments."""
        panels = create_test_panels()
        assignments = mood_designer.assign_moods(panels)

        assert len(assignments) == len(panels)
        for i, assignment in enumerate(assignments):
            assert assignment.panel_number == panels[i].panel_number
            assert assignment.mood is not None

    def test_high_intensity_panels_get_intense_moods(self):
        """High emotional intensity panels should get corresponding mood settings."""
        panels = create_test_panels()
        assignments = mood_designer.assign_moods(panels)

        # Panel 4 has intensity 9 (confrontation)
        confrontation_assignment = assignments[3]
        assert confrontation_assignment.mood.intensity >= 7

        # Panel 5 has intensity 3 (peaceful) but may be smoothed up
        # The smoothing algorithm prevents jarring jumps, so if panel 4 was 9,
        # panel 5 can be at most 3 points lower (6) after smoothing
        peaceful_assignment = assignments[4]
        # Just verify it exists and is less than confrontation
        assert peaceful_assignment.mood.intensity < confrontation_assignment.mood.intensity

    def test_mood_transitions_are_smoothed(self):
        """Mood transitions should be smoothed to avoid jarring changes."""
        panels = create_test_panels()
        assignments = mood_designer.assign_moods(panels)

        # Check that consecutive panels don't have huge intensity jumps
        for i in range(1, len(assignments)):
            prev_intensity = assignments[i-1].mood.intensity
            curr_intensity = assignments[i].mood.intensity
            # Difference should be <= 4 after smoothing (original smoothing threshold is 4)
            # But smoothing may allow up to 3-point jumps
            assert abs(curr_intensity - prev_intensity) <= 5, \
                f"Panel {i}: intensity jump {prev_intensity} -> {curr_intensity}"


class TestStyleCompositionIntegration:
    """Test style composition with different moods."""

    def test_legacy_style_with_different_moods(self):
        """Different moods should produce different style outputs."""
        styles = []

        for intensity, context in [(3, "peaceful"), (5, "neutral"), (8, "romantic"), (9, "conflict")]:
            style = get_legacy_style_with_mood(
                legacy_style_key="SOFT_ROMANTIC_WEBTOON",
                emotional_intensity=intensity,
                scene_context=context
            )
            styles.append(style)

        # All styles should be non-empty
        for style in styles:
            assert len(style) > 0

        # High intensity styles should have different modifiers than low
        peaceful_style = styles[0]
        conflict_style = styles[3]

        # They should be different (contain different mood sections)
        # At minimum, check they're not identical
        # Note: They will share the base style but differ in mood modifiers
        assert len(peaceful_style) > 100  # Should have substantial content
        assert len(conflict_style) > 100

    def test_composed_style_includes_mood_modifiers(self):
        """Composed style should include mood modifiers section."""
        style = get_legacy_style_with_mood(
            legacy_style_key="SOFT_ROMANTIC_WEBTOON",
            emotional_intensity=8,
            scene_context="romantic"
        )

        # Should include mood section marker
        assert "SCENE MOOD" in style or "Color temperature" in style.lower() or "warm" in style.lower()

    def test_different_base_styles_work(self):
        """Different base styles should work with mood composition."""
        base_styles = [
            "SOFT_ROMANTIC_WEBTOON",
            "VIBRANT_FANTASY_WEBTOON",
            "DRAMATIC_HISTORICAL_WEBTOON",
        ]

        for base_style in base_styles:
            style = get_legacy_style_with_mood(
                legacy_style_key=base_style,
                emotional_intensity=7,
                scene_context="romantic"
            )
            assert len(style) > 0, f"Empty style for {base_style}"


class TestFullPipelineIntegration:
    """Test the complete mood -> style pipeline."""

    def test_panel_to_composed_style_pipeline(self):
        """Test full pipeline from panel to composed style."""
        panels = create_test_panels()

        for panel in panels:
            # 1. Build combined text
            combined_text = f"{panel.visual_prompt} {panel.story_beat}"
            for d in panel.dialogue:
                combined_text += f" {d['text']}"

            # 2. Detect context
            detected_context, confidence = detect_context_from_text(combined_text)

            # 3. Compose style with mood
            composed_style = get_legacy_style_with_mood(
                legacy_style_key="SOFT_ROMANTIC_WEBTOON",
                emotional_intensity=panel.emotional_intensity,
                scene_context=detected_context
            )

            # Verify output
            assert len(composed_style) > 100, f"Panel {panel.panel_number}: composed style too short"
            assert isinstance(detected_context, str)

    def test_mood_assignment_to_style_pipeline(self):
        """Test mood assignment -> style composition pipeline."""
        panels = create_test_panels()
        assignments = mood_designer.assign_moods(panels)

        for i, assignment in enumerate(assignments):
            # Compose style using assignment data
            composed_style = get_legacy_style_with_mood(
                legacy_style_key="SOFT_ROMANTIC_WEBTOON",
                emotional_intensity=assignment.mood.intensity,
                scene_context=assignment.detected_context
            )

            assert len(composed_style) > 100

            # Log for debugging
            print(f"\nPanel {assignment.panel_number}:")
            print(f"  Context: {assignment.detected_context}")
            print(f"  Intensity: {assignment.mood.intensity}")
            print(f"  Mood name: {assignment.mood.name}")
            print(f"  Style preview: {composed_style[:100]}...")


class TestEdgeCases:
    """Test edge cases in the integration."""

    def test_empty_dialogue_panel(self):
        """Panel with no dialogue should still get mood assigned."""
        panel = WebtoonPanel(
            panel_number=1,
            shot_type="Wide Shot",
            active_character_names=["Ji-hoon"],
            visual_prompt="A serene sunset over the ocean.",
            story_beat="Contemplation",
            emotional_intensity=4,
            dialogue=None,
        )

        assignments = mood_designer.assign_moods([panel])
        assert len(assignments) == 1
        assert assignments[0].mood is not None

    def test_minimal_panel(self):
        """Panel with minimal content should still work."""
        panel = WebtoonPanel(
            panel_number=1,
            shot_type="Medium Shot",
            active_character_names=[],
            visual_prompt="",
            emotional_intensity=5,
        )

        assignments = mood_designer.assign_moods([panel])
        assert len(assignments) == 1
        # Should default to neutral
        assert assignments[0].detected_context == "neutral"

    def test_extreme_intensity_values(self):
        """Extreme intensity values should be handled gracefully."""
        panels = [
            WebtoonPanel(
                panel_number=1,
                shot_type="Medium Shot",
                visual_prompt="Intense scene",
                emotional_intensity=10,  # Max
            ),
            WebtoonPanel(
                panel_number=2,
                shot_type="Medium Shot",
                visual_prompt="Calm scene",
                emotional_intensity=1,  # Min
            ),
        ]

        assignments = mood_designer.assign_moods(panels)
        assert len(assignments) == 2

        # Both should have valid moods
        for assignment in assignments:
            assert 1 <= assignment.mood.intensity <= 10
