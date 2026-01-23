"""
Unit tests for Panel Composer Service (Phase 3.2).

Tests the panel grouping functionality for multi-panel generation.

v2.0.0: Initial implementation
"""

import pytest
from typing import List

from app.models.story import WebtoonPanel
from app.services.panel_composer import (
    PanelComposer,
    Page,
    PageLayoutType,
    group_panels_into_pages,
    calculate_page_statistics,
    should_be_single_panel,
    get_scene_type,
    get_panel_count_for_scene_type,
    SINGLE_PANEL_KEYWORDS,
)


# ============================================================================
# Test Data Helpers
# ============================================================================

def create_test_panel(
    panel_number: int,
    shot_type: str = "Medium shot",
    emotional_intensity: int = 5,
    story_beat: str = "",
    dialogue: List = None,
    active_character_names: List[str] = None
) -> WebtoonPanel:
    """Create a test WebtoonPanel."""
    return WebtoonPanel(
        panel_number=panel_number,
        shot_type=shot_type,
        emotional_intensity=emotional_intensity,
        story_beat=story_beat,
        visual_prompt=f"Test visual prompt for panel {panel_number}",
        dialogue=dialogue or [],
        active_character_names=active_character_names or [],
    )


def create_action_sequence(start_num: int = 1, count: int = 4) -> List[WebtoonPanel]:
    """Create an action sequence of panels."""
    return [
        create_test_panel(
            start_num + i,
            shot_type="Wide shot" if i == 0 else "Medium shot",
            emotional_intensity=6 + i % 3,
            story_beat=f"Action beat {i+1}: fight continues"
        )
        for i in range(count)
    ]


def create_dialogue_sequence(start_num: int = 1, count: int = 3) -> List[WebtoonPanel]:
    """Create a dialogue sequence of panels."""
    return [
        create_test_panel(
            start_num + i,
            shot_type="Medium close-up" if i % 2 == 0 else "Over-shoulder",
            emotional_intensity=4 + i,
            dialogue=[
                {"character": "A", "text": f"Line {i+1}"},
                {"character": "B", "text": f"Response {i+1}"}
            ]
        )
        for i in range(count)
    ]


def create_climax_panel(panel_number: int = 1) -> WebtoonPanel:
    """Create a high-intensity climax panel."""
    return create_test_panel(
        panel_number,
        shot_type="Extreme close-up",
        emotional_intensity=9,
        story_beat="The climax - everything changes"
    )


# ============================================================================
# Test Page Model
# ============================================================================

class TestPageModel:
    """Tests for Page dataclass."""

    def test_basic_creation(self):
        """Test basic Page creation."""
        page = Page(
            page_number=1,
            panel_indices=[0, 1, 2],
            layout_type=PageLayoutType.THREE_PANEL
        )
        assert page.page_number == 1
        assert page.panel_count == 3
        assert page.layout_type == PageLayoutType.THREE_PANEL

    def test_is_single_panel_auto_set(self):
        """Test that is_single_panel is auto-set for single layout."""
        single_page = Page(
            page_number=1,
            panel_indices=[0],
            layout_type=PageLayoutType.SINGLE
        )
        assert single_page.is_single_panel is True

        multi_page = Page(
            page_number=2,
            panel_indices=[1, 2, 3],
            layout_type=PageLayoutType.THREE_PANEL
        )
        assert multi_page.is_single_panel is False

    def test_to_dict(self):
        """Test Page to_dict conversion."""
        page = Page(
            page_number=1,
            panel_indices=[0, 1],
            layout_type=PageLayoutType.TWO_PANEL,
            reasoning="Test reasoning"
        )
        d = page.to_dict()

        assert d["page_number"] == 1
        assert d["panel_count"] == 2
        assert d["layout_type"] == "two_panel"
        assert d["reasoning"] == "Test reasoning"


# ============================================================================
# Test Single Panel Detection
# ============================================================================

class TestSinglePanelDetection:
    """Tests for should_be_single_panel function."""

    def test_high_intensity_triggers_single(self):
        """Panel with intensity >= 9 should be single."""
        panel = create_test_panel(1, emotional_intensity=9)
        is_single, reason = should_be_single_panel(panel)

        assert is_single is True
        assert "intensity" in reason.lower()

    def test_climax_keyword_triggers_single(self):
        """Panel with 'climax' in story beat should be single."""
        panel = create_test_panel(1, story_beat="The climax of the story")
        is_single, reason = should_be_single_panel(panel)

        assert is_single is True
        assert "climax" in reason.lower()

    def test_confession_keyword_triggers_single(self):
        """Panel with 'confession' should be single."""
        panel = create_test_panel(1, story_beat="She makes her confession")
        is_single, reason = should_be_single_panel(panel)

        assert is_single is True
        assert "confession" in reason.lower()

    def test_extreme_closeup_high_intensity_triggers_single(self):
        """Extreme close-up with high intensity should be single."""
        panel = create_test_panel(
            1,
            shot_type="extreme close-up",
            emotional_intensity=7
        )
        is_single, reason = should_be_single_panel(panel)

        assert is_single is True
        assert "close-up" in reason.lower() or "intensity" in reason.lower()

    def test_normal_panel_not_single(self):
        """Normal panel should not be single."""
        panel = create_test_panel(1, emotional_intensity=5)
        is_single, reason = should_be_single_panel(panel)

        assert is_single is False
        assert reason == ""


# ============================================================================
# Test Scene Type Detection
# ============================================================================

class TestSceneTypeDetection:
    """Tests for get_scene_type function."""

    def test_action_scene_detection(self):
        """Detect action scenes."""
        panel = create_test_panel(1, story_beat="They fight in the alley")
        assert get_scene_type(panel) == "action"

    def test_establishing_scene_detection(self):
        """Detect establishing shots."""
        panel = create_test_panel(1, shot_type="Wide establishing shot")
        assert get_scene_type(panel) == "establishing"

    def test_dialogue_scene_detection(self):
        """Detect dialogue-heavy scenes."""
        panel = create_test_panel(
            1,
            dialogue=[
                {"character": "A", "text": "Line 1"},
                {"character": "B", "text": "Line 2"}
            ]
        )
        assert get_scene_type(panel) == "dialogue"

    def test_emotional_scene_detection(self):
        """Detect emotional scenes."""
        panel = create_test_panel(1, story_beat="She starts to cry")
        assert get_scene_type(panel) == "emotional"

    def test_default_is_transition(self):
        """Unknown scenes default to transition."""
        panel = create_test_panel(1, story_beat="Walking down the street")
        assert get_scene_type(panel) == "transition"


class TestPanelCountRecommendation:
    """Tests for get_panel_count_for_scene_type."""

    def test_action_recommends_4(self):
        assert get_panel_count_for_scene_type("action") == 4

    def test_dialogue_recommends_3(self):
        assert get_panel_count_for_scene_type("dialogue") == 3

    def test_emotional_recommends_2(self):
        assert get_panel_count_for_scene_type("emotional") == 2

    def test_establishing_recommends_2(self):
        assert get_panel_count_for_scene_type("establishing") == 2

    def test_unknown_defaults_to_3(self):
        assert get_panel_count_for_scene_type("unknown") == 3


# ============================================================================
# Test Panel Composer Service
# ============================================================================

class TestPanelComposerInit:
    """Tests for PanelComposer initialization."""

    def test_default_init(self):
        """Test default initialization."""
        composer = PanelComposer()
        assert composer._use_llm is False
        assert composer._llm_client is None

    def test_llm_init(self):
        """Test initialization with LLM."""
        mock_client = object()
        composer = PanelComposer(use_llm=True, llm_client=mock_client)
        assert composer._use_llm is True
        assert composer._llm_client is mock_client


class TestPanelComposerGrouping:
    """Tests for panel grouping logic."""

    def test_empty_panels_returns_empty(self):
        """Empty panel list returns empty page list."""
        composer = PanelComposer()
        pages = composer.group_shots_into_pages([])
        assert pages == []

    def test_single_panel_creates_single_page(self):
        """Single panel creates one page."""
        panels = [create_test_panel(1)]
        pages = group_panels_into_pages(panels)

        assert len(pages) == 1
        assert pages[0].panel_count == 1

    def test_high_intensity_gets_own_page(self):
        """High-intensity panel gets its own single page."""
        panels = [
            create_test_panel(1, emotional_intensity=5),
            create_test_panel(2, emotional_intensity=9),  # Should be single
            create_test_panel(3, emotional_intensity=5),
        ]
        pages = group_panels_into_pages(panels)

        # Find the high-intensity panel's page
        high_intensity_page = None
        for page in pages:
            if 1 in page.panel_indices:  # Index 1 is panel 2
                high_intensity_page = page
                break

        assert high_intensity_page is not None
        assert high_intensity_page.is_single_panel is True
        assert high_intensity_page.panel_count == 1

    def test_action_sequence_grouped(self):
        """Action sequence panels are grouped together."""
        panels = create_action_sequence(count=4)
        pages = group_panels_into_pages(panels)

        # Should create 1 page with 4 panels (action default)
        assert len(pages) >= 1
        total_panels = sum(p.panel_count for p in pages)
        assert total_panels == 4

    def test_dialogue_sequence_grouped(self):
        """Dialogue sequence panels are grouped together."""
        panels = create_dialogue_sequence(count=3)
        pages = group_panels_into_pages(panels)

        assert len(pages) >= 1
        total_panels = sum(p.panel_count for p in pages)
        assert total_panels == 3

    def test_all_panels_included(self):
        """All input panels are included in output pages."""
        panels = [create_test_panel(i) for i in range(1, 11)]
        pages = group_panels_into_pages(panels)

        # Collect all panel indices from pages
        all_indices = set()
        for page in pages:
            all_indices.update(page.panel_indices)

        # Should include all 10 panels (indices 0-9)
        assert all_indices == set(range(10))

    def test_mixed_sequence_handling(self):
        """Mixed sequence of different scene types."""
        panels = [
            create_test_panel(1, shot_type="Wide shot"),  # Establishing
            create_test_panel(2, emotional_intensity=5),
            create_test_panel(3, emotional_intensity=9, story_beat="The climax"),  # Single
            create_test_panel(4, story_beat="Running away"),  # Action
            create_test_panel(5, story_beat="Fighting back"),  # Action
        ]
        pages = group_panels_into_pages(panels)

        # Climax panel should be on its own page
        climax_page = None
        for page in pages:
            if 2 in page.panel_indices:  # Index 2 is panel 3 (climax)
                climax_page = page
                break

        assert climax_page is not None
        assert climax_page.is_single_panel is True

    def test_no_more_than_5_panels_per_page(self):
        """No page should have more than 5 panels."""
        panels = [create_test_panel(i) for i in range(1, 15)]
        pages = group_panels_into_pages(panels)

        for page in pages:
            assert page.panel_count <= 5


# ============================================================================
# Test Statistics
# ============================================================================

class TestPageStatistics:
    """Tests for calculate_page_statistics function."""

    def test_empty_pages_statistics(self):
        """Statistics for empty page list."""
        stats = calculate_page_statistics([])

        assert stats["total_pages"] == 0
        assert stats["total_panels"] == 0
        assert stats["average_panels_per_page"] == 0

    def test_basic_statistics(self):
        """Basic statistics calculation."""
        pages = [
            Page(1, [0, 1, 2], layout_type=PageLayoutType.THREE_PANEL),
            Page(2, [3], layout_type=PageLayoutType.SINGLE),
            Page(3, [4, 5], layout_type=PageLayoutType.TWO_PANEL),
        ]
        stats = calculate_page_statistics(pages)

        assert stats["total_pages"] == 3
        assert stats["total_panels"] == 6
        assert stats["single_panel_pages"] == 1
        assert stats["multi_panel_pages"] == 2
        assert stats["average_panels_per_page"] == 2.0

    def test_layout_distribution(self):
        """Statistics include layout distribution."""
        pages = [
            Page(1, [0, 1, 2], layout_type=PageLayoutType.THREE_PANEL),
            Page(2, [3, 4, 5], layout_type=PageLayoutType.THREE_PANEL),
            Page(3, [6], layout_type=PageLayoutType.SINGLE),
        ]
        stats = calculate_page_statistics(pages)

        assert stats["layout_distribution"]["three_panel"] == 2
        assert stats["layout_distribution"]["single"] == 1


# ============================================================================
# Integration Tests
# ============================================================================

class TestPanelComposerIntegration:
    """Integration tests for panel composer."""

    def test_typical_webtoon_sequence(self):
        """Test a typical webtoon panel sequence."""
        # Create a typical story flow
        panels = [
            # Establishing
            create_test_panel(1, shot_type="Wide shot", story_beat="Seoul cityscape at night"),
            # Dialogue exchange
            create_test_panel(2, dialogue=[{"character": "A", "text": "Hi"}]),
            create_test_panel(3, dialogue=[{"character": "B", "text": "Hello"}]),
            create_test_panel(4, dialogue=[{"character": "A", "text": "What's wrong?"}]),
            # Emotional climax
            create_test_panel(5, emotional_intensity=9, story_beat="She reveals the truth"),
            # Resolution
            create_test_panel(6, story_beat="They embrace"),
            create_test_panel(7, shot_type="Wide shot", story_beat="Walking into the sunset"),
        ]

        pages = group_panels_into_pages(panels)
        stats = calculate_page_statistics(pages)

        # Basic validation
        assert stats["total_panels"] == 7
        assert stats["single_panel_pages"] >= 1  # At least the climax
        assert all(p.panel_count <= 5 for p in pages)

        # Climax should be single
        for page in pages:
            if 4 in page.panel_indices:  # Panel 5 (index 4)
                assert page.is_single_panel

    def test_page_numbers_are_sequential(self):
        """Page numbers should be sequential starting from 1."""
        panels = [create_test_panel(i) for i in range(1, 8)]
        pages = group_panels_into_pages(panels)

        for i, page in enumerate(pages, start=1):
            assert page.page_number == i

    def test_panels_array_populated(self):
        """Each page should have its panels array populated."""
        panels = [create_test_panel(i) for i in range(1, 5)]
        pages = group_panels_into_pages(panels)

        for page in pages:
            assert len(page.panels) == len(page.panel_indices)
            for panel in page.panels:
                assert isinstance(panel, WebtoonPanel)
