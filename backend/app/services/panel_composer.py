"""
Panel Composer Service for Webtoon Enhancement.

This module provides functionality to group shots/panels into pages for
multi-panel generation. It analyzes shot sequences and determines optimal
page layouts based on emotional intensity, scene type, and narrative flow.

Key features:
- Rule-based panel grouping (fast, deterministic)
- LLM-based panel grouping (context-aware, nuanced)
- Single vs multi-panel decision logic
- Page layout optimization

v2.0.0: Initial implementation (Phase 3.2)
"""

import json
import logging
import re
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from app.models.story import WebtoonPanel


logger = logging.getLogger(__name__)


# ============================================================================
# Page Layout Types
# ============================================================================

class PageLayoutType(str, Enum):
    """Types of page layouts for multi-panel generation."""
    SINGLE = "single"           # Full-page single panel (key moments)
    TWO_PANEL = "two_panel"     # 2 panels (establishing + reaction)
    THREE_PANEL = "three_panel" # 3 panels (standard progression)
    FOUR_PANEL = "four_panel"   # 4 panels (detailed sequence)
    FIVE_PANEL = "five_panel"   # 5 panels (dense storytelling)


# ============================================================================
# Page Model (Task 3.2.3)
# ============================================================================

@dataclass
class Page:
    """
    Represents a single page in the webtoon containing one or more panels.

    Attributes:
        page_number: Sequential page number (1-indexed)
        panel_indices: Indices of panels from the original list
        panels: List of WebtoonPanel objects on this page
        layout_type: Type of layout (single, two_panel, etc.)
        is_single_panel: Whether this is a full-page single panel
        reasoning: Explanation for this grouping
    """
    page_number: int
    panel_indices: List[int]
    panels: List[WebtoonPanel] = field(default_factory=list)
    layout_type: PageLayoutType = PageLayoutType.THREE_PANEL
    is_single_panel: bool = False
    reasoning: str = ""

    def __post_init__(self):
        """Update is_single_panel based on layout."""
        self.is_single_panel = self.layout_type == PageLayoutType.SINGLE

    @property
    def panel_count(self) -> int:
        """Number of panels on this page."""
        return len(self.panel_indices)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "page_number": self.page_number,
            "panel_indices": self.panel_indices,
            "panel_count": self.panel_count,
            "layout_type": self.layout_type.value,
            "is_single_panel": self.is_single_panel,
            "reasoning": self.reasoning,
        }


# ============================================================================
# Grouping Rules (Task 3.2.5)
# ============================================================================

# Keywords that trigger single-panel pages
SINGLE_PANEL_KEYWORDS = [
    "climax", "reveal", "confession", "death", "kiss",
    "shocking", "devastating", "breakthrough", "transformation",
    "final", "ultimate", "turning point"
]

# Shot types that suggest single-panel treatment at high intensity
SINGLE_PANEL_SHOT_TYPES = [
    "extreme_close_up", "extreme close-up", "extreme close up"
]


def should_be_single_panel(panel: WebtoonPanel) -> Tuple[bool, str]:
    """
    Determine if a panel should be a full-page single panel.

    Args:
        panel: The WebtoonPanel to analyze

    Returns:
        Tuple of (should_be_single, reason)
    """
    intensity = getattr(panel, "emotional_intensity", 5)
    story_beat = getattr(panel, "story_beat", "").lower()
    visual_prompt = getattr(panel, "visual_prompt", "").lower()
    shot_type = getattr(panel, "shot_type", "").lower()

    # High intensity threshold
    if intensity >= 9:
        return True, f"Very high emotional intensity ({intensity})"

    # Check for keyword triggers
    combined_text = f"{story_beat} {visual_prompt}"
    for keyword in SINGLE_PANEL_KEYWORDS:
        if keyword in combined_text:
            return True, f"Key moment detected: '{keyword}'"

    # Extreme close-up with high intensity
    if any(st in shot_type for st in SINGLE_PANEL_SHOT_TYPES) and intensity >= 7:
        return True, f"Extreme close-up with high intensity ({intensity})"

    return False, ""


def get_scene_type(panel: WebtoonPanel) -> str:
    """
    Detect the scene type for grouping purposes.

    Args:
        panel: The WebtoonPanel to analyze

    Returns:
        Scene type: "action", "dialogue", "emotional", "establishing", "transition"
    """
    story_beat = getattr(panel, "story_beat", "").lower()
    visual_prompt = getattr(panel, "visual_prompt", "").lower()
    shot_type = getattr(panel, "shot_type", "").lower()
    dialogue = getattr(panel, "dialogue", [])

    combined = f"{story_beat} {visual_prompt}"

    # Action indicators
    action_keywords = ["fight", "chase", "run", "attack", "dodge", "jump", "crash", "explosion"]
    if any(kw in combined for kw in action_keywords):
        return "action"

    # Establishing indicators
    if "wide" in shot_type or "establishing" in combined:
        return "establishing"

    # Dialogue heavy
    if dialogue and len(dialogue) >= 2:
        return "dialogue"

    # Emotional indicators
    emotional_keywords = ["cry", "tear", "sob", "laugh", "smile", "hug", "embrace"]
    if any(kw in combined for kw in emotional_keywords):
        return "emotional"

    # Default to transition
    return "transition"


def get_panel_count_for_scene_type(scene_type: str) -> int:
    """
    Get recommended panel count for a scene type.

    Args:
        scene_type: Type of scene

    Returns:
        Recommended number of panels per page
    """
    recommendations = {
        "action": 4,
        "dialogue": 2,
        "emotional": 2,
        "establishing": 1,
        "transition": 2,
    }
    return recommendations.get(scene_type, 3)


# ============================================================================
# Panel Composer Service (Task 3.2.2)
# ============================================================================

class PanelComposer:
    """
    Service for grouping panels into pages for multi-panel generation.

    Supports both rule-based (fast, deterministic) and LLM-based
    (context-aware, nuanced) approaches.
    """

    def __init__(self, use_llm: bool = False, llm_client=None):
        """
        Initialize the Panel Composer.

        Args:
            use_llm: Whether to use LLM for grouping decisions
            llm_client: Optional LLM client instance
        """
        self._use_llm = use_llm
        self._llm_client = llm_client

    def group_shots_into_pages(
        self,
        panels: List[WebtoonPanel],
        target_pages: Optional[int] = None
    ) -> List[Page]:
        """
        Group panels into pages for multi-panel generation.

        This is the main entry point for panel grouping.

        Args:
            panels: List of WebtoonPanel objects to group
            target_pages: Optional target number of pages (guides grouping)

        Returns:
            List of Page objects, each containing grouped panels
        """
        if not panels:
            return []

        if self._use_llm and self._llm_client:
            return self._group_with_llm(panels, target_pages)
        else:
            return self._group_rule_based(panels, target_pages)

    def _group_rule_based(
        self,
        panels: List[WebtoonPanel],
        target_pages: Optional[int] = None
    ) -> List[Page]:
        """
        Group panels using rule-based approach.

        Fast and deterministic, suitable for most use cases.
        """
        pages: List[Page] = []
        current_page_panels: List[int] = []
        current_scene_type = None
        page_number = 1
        
        # Guarantee at least 1-2 full-page single panels (climax/hero moment)
        # Even if emotional_intensity isn't populated, pick the best available candidate.
        hero_panel_index = 0
        hero_intensity = -1
        for idx, p in enumerate(panels):
            intensity = getattr(p, "emotional_intensity", 5)
            if intensity > hero_intensity:
                hero_intensity = intensity
                hero_panel_index = idx

        single_panel_budget = max(1, len(panels) // 12)  # ~2 for 24+ panels
        extra_single_budget = max(0, single_panel_budget - 1)  # hero doesn't consume budget
        extra_single_used = 0

        for i, panel in enumerate(panels):
            # Check if this panel should be single
            if i == hero_panel_index:
                is_single, reason = True, f"Hero moment (peak emotional intensity {hero_intensity})"
            else:
                is_single, reason = should_be_single_panel(panel)
                # Promote a small number of high-intensity panels to single-page even if < 9
                if not is_single and extra_single_used < extra_single_budget:
                    intensity = getattr(panel, "emotional_intensity", 5)
                    if intensity >= 8:
                        is_single, reason = True, f"High emotional intensity ({intensity})"

            if is_single:
                if i != hero_panel_index and reason.startswith("High emotional intensity"):
                    extra_single_used += 1
                # First, close out any pending page
                if current_page_panels:
                    pages.append(self._create_page(
                        page_number=page_number,
                        panel_indices=current_page_panels,
                        panels=panels,
                        reasoning=f"Grouped {len(current_page_panels)} {current_scene_type or 'mixed'} panels"
                    ))
                    page_number += 1
                    current_page_panels = []

                # Create single-panel page
                pages.append(Page(
                    page_number=page_number,
                    panel_indices=[i],
                    panels=[panel],
                    layout_type=PageLayoutType.SINGLE,
                    is_single_panel=True,
                    reasoning=reason
                ))
                page_number += 1
                current_scene_type = None
                continue

            # Get scene type for grouping
            scene_type = get_scene_type(panel)
            recommended_count = get_panel_count_for_scene_type(scene_type)

            # Start new page if scene type changes significantly or page is full
            should_start_new_page = (
                len(current_page_panels) >= recommended_count or
                (current_scene_type and current_scene_type != scene_type and len(current_page_panels) >= 2)
            )

            if should_start_new_page and current_page_panels:
                pages.append(self._create_page(
                    page_number=page_number,
                    panel_indices=current_page_panels,
                    panels=panels,
                    reasoning=f"{current_scene_type or 'mixed'} sequence"
                ))
                page_number += 1
                current_page_panels = []
                current_scene_type = None

            # Add panel to current page
            current_page_panels.append(i)
            current_scene_type = scene_type

        # Don't forget the last page
        if current_page_panels:
            pages.append(self._create_page(
                page_number=page_number,
                panel_indices=current_page_panels,
                panels=panels,
                reasoning=f"Final {current_scene_type or 'mixed'} sequence"
            ))

        return pages

    def _create_page(
        self,
        page_number: int,
        panel_indices: List[int],
        panels: List[WebtoonPanel],
        reasoning: str = ""
    ) -> Page:
        """Create a Page object with the appropriate layout type."""
        count = len(panel_indices)
        layout_map = {
            1: PageLayoutType.SINGLE,
            2: PageLayoutType.TWO_PANEL,
            3: PageLayoutType.THREE_PANEL,
            4: PageLayoutType.FOUR_PANEL,
            5: PageLayoutType.FIVE_PANEL,
        }
        layout_type = layout_map.get(count, PageLayoutType.FIVE_PANEL)

        page_panels = [panels[i] for i in panel_indices]

        return Page(
            page_number=page_number,
            panel_indices=panel_indices,
            panels=page_panels,
            layout_type=layout_type,
            reasoning=reasoning
        )

    def _group_with_llm(
        self,
        panels: List[WebtoonPanel],
        target_pages: Optional[int] = None
    ) -> List[Page]:
        """
        Group panels using LLM for context-aware decisions.
        """
        from app.prompt.panel_composer import (
            PANEL_COMPOSER_SYSTEM_PROMPT,
            PANEL_COMPOSER_USER_PROMPT
        )

        if not self._llm_client:
            logger.warning("LLM client not configured, falling back to rule-based")
            return self._group_rule_based(panels, target_pages)

        # Format panels for LLM
        shots_data = []
        for i, panel in enumerate(panels):
            shot_data = {
                "index": i,
                "shot_type": getattr(panel, "shot_type", "Medium shot"),
                "emotional_intensity": getattr(panel, "emotional_intensity", 5),
                "story_beat": getattr(panel, "story_beat", ""),
                "has_dialogue": bool(getattr(panel, "dialogue", [])),
                "characters": getattr(panel, "active_character_names", []),
            }
            shots_data.append(shot_data)

        # Calculate target pages if not provided
        if target_pages is None:
            target_pages = max(3, len(panels) // 3)

        user_prompt = PANEL_COMPOSER_USER_PROMPT.format(
            shots_json=json.dumps(shots_data, indent=2),
            total_shots=len(panels),
            target_pages=target_pages
        )

        try:
            response = self._llm_client.generate(
                system_prompt=PANEL_COMPOSER_SYSTEM_PROMPT,
                user_prompt=user_prompt
            )

            pages = self._parse_llm_response(response, panels)
            return pages

        except Exception as e:
            logger.error(f"LLM grouping failed: {e}, falling back to rule-based")
            return self._group_rule_based(panels, target_pages)

    def _parse_llm_response(
        self,
        response: str,
        panels: List[WebtoonPanel]
    ) -> List[Page]:
        """Parse LLM response into Page objects."""
        pages = []

        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                page_data = json.loads(json_match.group())

                for item in page_data:
                    page_num = item.get("page_number", len(pages) + 1)
                    indices = item.get("panel_indices", [])
                    layout_str = item.get("layout_type", "three_panel")
                    reasoning = item.get("reasoning", "")

                    # Convert layout string to enum
                    try:
                        layout_type = PageLayoutType(layout_str)
                    except ValueError:
                        layout_type = PageLayoutType.THREE_PANEL

                    # Get panels for this page
                    page_panels = [panels[i] for i in indices if i < len(panels)]

                    pages.append(Page(
                        page_number=page_num,
                        panel_indices=indices,
                        panels=page_panels,
                        layout_type=layout_type,
                        reasoning=reasoning
                    ))

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response: {e}")

        # If parsing failed or incomplete, fill with rule-based
        if not pages:
            return self._group_rule_based(panels, None)

        # Verify all panels are included
        included = set()
        for page in pages:
            included.update(page.panel_indices)

        missing = set(range(len(panels))) - included
        if missing:
            logger.warning(f"LLM missed panels {missing}, adding to last page")
            for idx in sorted(missing):
                pages[-1].panel_indices.append(idx)
                pages[-1].panels.append(panels[idx])

        return pages


# ============================================================================
# Convenience Functions
# ============================================================================

def group_panels_into_pages(
    panels: List[WebtoonPanel],
    target_pages: Optional[int] = None
) -> List[Page]:
    """
    Convenience function to group panels using rule-based approach.

    Args:
        panels: List of WebtoonPanel objects
        target_pages: Optional target number of pages

    Returns:
        List of Page objects
    """
    composer = PanelComposer()
    return composer.group_shots_into_pages(panels, target_pages)


def calculate_page_statistics(pages: List[Page]) -> Dict[str, Any]:
    """
    Calculate statistics about page groupings.

    Args:
        pages: List of Page objects

    Returns:
        Dictionary with statistics
    """
    if not pages:
        return {
            "total_pages": 0,
            "total_panels": 0,
            "single_panel_pages": 0,
            "multi_panel_pages": 0,
            "average_panels_per_page": 0,
            "layout_distribution": {}
        }

    total_panels = sum(page.panel_count for page in pages)
    single_pages = sum(1 for page in pages if page.is_single_panel)

    layout_dist = {}
    for page in pages:
        layout = page.layout_type.value
        layout_dist[layout] = layout_dist.get(layout, 0) + 1

    return {
        "total_pages": len(pages),
        "total_panels": total_panels,
        "single_panel_pages": single_pages,
        "multi_panel_pages": len(pages) - single_pages,
        "average_panels_per_page": round(total_panels / len(pages), 2),
        "layout_distribution": layout_dist
    }


# ============================================================================
# Global Instance
# ============================================================================

# Default panel composer instance
panel_composer = PanelComposer()
