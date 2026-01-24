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
        panel_weights: v2.1.0 E1-T02 - Percentage weight for each panel
        composition: v2.1.0 E1-T02 - Detailed composition analysis
    """
    page_number: int
    panel_indices: List[int]
    panels: List[WebtoonPanel] = field(default_factory=list)
    layout_type: PageLayoutType = PageLayoutType.THREE_PANEL
    is_single_panel: bool = False
    reasoning: str = ""
    # v2.1.0 E1-T02: Panel importance weights (percentage of page per panel)
    panel_weights: Dict[int, float] = field(default_factory=dict)
    # v2.1.0 E1-T02: Detailed composition analysis
    composition: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Update is_single_panel based on layout."""
        self.is_single_panel = self.layout_type == PageLayoutType.SINGLE

    @property
    def panel_count(self) -> int:
        """Number of panels on this page."""
        return len(self.panel_indices)
    
    def get_panel_weight(self, panel_index: int) -> float:
        """
        Get the weight (% of page) for a specific panel.
        
        v2.1.0 E1-T02: Returns the compositional weight for sizing.
        
        Args:
            panel_index: Index within this page's panels (0-indexed)
            
        Returns:
            Percentage weight (0-100). Default 100/panel_count if not set.
        """
        if self.panel_weights and panel_index in self.panel_weights:
            return self.panel_weights[panel_index]
        # Default to equal distribution
        return 100.0 / self.panel_count if self.panel_count > 0 else 100.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "page_number": self.page_number,
            "panel_indices": self.panel_indices,
            "panel_count": self.panel_count,
            "layout_type": self.layout_type.value,
            "is_single_panel": self.is_single_panel,
            "reasoning": self.reasoning,
            # v2.1.0 E1-T02
            "panel_weights": self.panel_weights,
            "composition": self.composition,
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

    v2.1.0 E1-T01: Extended to support 1-5 panel range dynamically.
    
    Args:
        scene_type: Type of scene

    Returns:
        Recommended number of panels per page (1-5)
    """
    recommendations = {
        "action": 4,       # Fast pacing, more panels
        "dialogue": 3,     # Standard conversation flow
        "emotional": 2,    # Give space for emotional beats
        "establishing": 2, # Wide shots need room
        "transition": 3,   # Standard pacing
        "dense": 5,        # v2.1.0: Dense storytelling sequences
        "climax": 1,       # v2.1.0: Single panel for key moments
    }
    return recommendations.get(scene_type, 3)


# ============================================================================
# Panel Importance Weighting System (v2.1.0 E1-T02)
# ============================================================================

class PanelImportance(str, Enum):
    """
    Panel importance levels for compositional weighting.
    
    v2.1.0 E1-T02: Defines how much visual space a panel should occupy
    relative to other panels on the same page.
    """
    HERO = "hero"           # 60-70% of page - key emotional/story moments
    PRIMARY = "primary"     # 40-50% of page - main action/dialogue
    SECONDARY = "secondary" # 25-35% of page - supporting context
    TERTIARY = "tertiary"   # 15-20% of page - transitions/reactions


# Importance weight mapping (percentage of page)
IMPORTANCE_WEIGHTS = {
    PanelImportance.HERO: (60, 70),      # Hero panels dominate the page
    PanelImportance.PRIMARY: (40, 50),   # Primary panels are substantial
    PanelImportance.SECONDARY: (25, 35), # Secondary panels support
    PanelImportance.TERTIARY: (15, 20),  # Tertiary panels are compact
}


def calculate_panel_importance(panel: WebtoonPanel) -> PanelImportance:
    """
    Calculate the importance level of a panel based on content analysis.
    
    v2.1.0 E1-T02: Determines how much visual weight a panel should have.
    
    Args:
        panel: The WebtoonPanel to analyze
        
    Returns:
        PanelImportance level
    """
    intensity = getattr(panel, "emotional_intensity", 5)
    story_beat = getattr(panel, "story_beat", "").lower()
    visual_prompt = getattr(panel, "visual_prompt", "").lower()
    shot_type = getattr(panel, "shot_type", "").lower()
    dialogue = getattr(panel, "dialogue", [])
    
    combined = f"{story_beat} {visual_prompt}"
    
    # HERO: Key emotional/story moments (intensity 8-10)
    hero_keywords = ["climax", "confession", "reveal", "kiss", "death", "breakthrough"]
    if intensity >= 9 or any(kw in combined for kw in hero_keywords):
        return PanelImportance.HERO
    
    # HERO: Extreme close-ups at high intensity
    if "extreme" in shot_type and intensity >= 7:
        return PanelImportance.HERO
    
    # PRIMARY: Important scenes with dialogue or mid-high intensity
    if intensity >= 7 or (dialogue and len(dialogue) >= 2):
        return PanelImportance.PRIMARY
    
    # PRIMARY: Close-up shots typically carry emotional weight
    if "close" in shot_type and intensity >= 5:
        return PanelImportance.PRIMARY
    
    # TERTIARY: Low intensity transitions and wide establishing shots
    transition_keywords = ["meanwhile", "later", "walks", "approaches", "enters"]
    if intensity <= 3 or any(kw in combined for kw in transition_keywords):
        return PanelImportance.TERTIARY
    
    # SECONDARY: Everything else
    return PanelImportance.SECONDARY


def get_recommended_layout_for_importance_mix(
    importance_levels: List[PanelImportance]
) -> Tuple[PageLayoutType, Dict[int, float]]:
    """
    Get recommended layout and size distribution for a mix of panel importances.
    
    v2.1.0 E1-T02: Dynamically calculates panel sizes based on importance.
    
    Args:
        importance_levels: List of importance levels for panels on the page
        
    Returns:
        Tuple of (layout_type, size_distribution dict mapping panel index to % of page)
    """
    count = len(importance_levels)
    
    # Determine layout type
    layout_map = {
        1: PageLayoutType.SINGLE,
        2: PageLayoutType.TWO_PANEL,
        3: PageLayoutType.THREE_PANEL,
        4: PageLayoutType.FOUR_PANEL,
        5: PageLayoutType.FIVE_PANEL,
    }
    layout_type = layout_map.get(count, PageLayoutType.FIVE_PANEL)
    
    # If single panel, it gets 100%
    if count == 1:
        return layout_type, {0: 100.0}
    
    # Calculate weights based on importance
    raw_weights = []
    for imp in importance_levels:
        min_pct, max_pct = IMPORTANCE_WEIGHTS[imp]
        avg = (min_pct + max_pct) / 2
        raw_weights.append(avg)
    
    # Normalize to 100%
    total = sum(raw_weights)
    size_distribution = {
        i: round((w / total) * 100, 1)
        for i, w in enumerate(raw_weights)
    }
    
    return layout_type, size_distribution


def analyze_page_composition(panels: List[WebtoonPanel]) -> Dict[str, Any]:
    """
    Analyze a page's composition based on panel importance.
    
    v2.1.0 E1-T02: Provides detailed composition analysis for rendering.
    
    Args:
        panels: List of WebtoonPanel objects on the page
        
    Returns:
        Composition analysis with layout recommendations
    """
    if not panels:
        return {"error": "No panels provided"}
    
    importance_levels = [calculate_panel_importance(p) for p in panels]
    layout_type, size_distribution = get_recommended_layout_for_importance_mix(importance_levels)
    
    # Count importance distribution
    importance_counts = {}
    for imp in importance_levels:
        importance_counts[imp.value] = importance_counts.get(imp.value, 0) + 1
    
    return {
        "panel_count": len(panels),
        "layout_type": layout_type.value,
        "importance_distribution": importance_counts,
        "panel_details": [
            {
                "index": i,
                "importance": importance_levels[i].value,
                "weight_percentage": size_distribution[i],
            }
            for i in range(len(panels))
        ],
        "has_hero_panel": PanelImportance.HERO in importance_levels,
        "composition_notes": _generate_composition_notes(importance_levels, layout_type),
    }


def _generate_composition_notes(
    importance_levels: List[PanelImportance],
    layout_type: PageLayoutType
) -> str:
    """Generate human-readable composition notes."""
    count = len(importance_levels)
    hero_count = importance_levels.count(PanelImportance.HERO)
    primary_count = importance_levels.count(PanelImportance.PRIMARY)
    
    if hero_count > 0:
        return f"Hero-focused layout with {count} panels. Primary focus on panel(s) with highest emotional weight."
    elif primary_count >= count // 2:
        return f"Balanced {layout_type.value} layout. Multiple important moments require careful visual hierarchy."
    else:
        return f"Supporting sequence with {count} panels. Quick pacing for transitional content."


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

        for i, panel in enumerate(panels):
            # Check if this panel should be single
            is_single, reason = should_be_single_panel(panel)

            if is_single:
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
        """
        Create a Page object with the appropriate layout type.
        
        v2.1.0 E1-T02: Now includes panel importance weights and composition analysis.
        """
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
        
        # v2.1.0 E1-T02: Calculate panel importance and weights
        composition = analyze_page_composition(page_panels)
        
        # Extract weights from composition (map local index to weight)
        panel_weights = {}
        if "panel_details" in composition:
            for detail in composition["panel_details"]:
                panel_weights[detail["index"]] = detail["weight_percentage"]

        return Page(
            page_number=page_number,
            panel_indices=panel_indices,
            panels=page_panels,
            layout_type=layout_type,
            reasoning=reasoning,
            panel_weights=panel_weights,
            composition=composition
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
