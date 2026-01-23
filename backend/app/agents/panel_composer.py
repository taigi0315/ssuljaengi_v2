# panel_composer.py
"""Panel Composer Agent

Groups panels into pages for multi-panel generation and calculates layout statistics.
"""

from pydantic import BaseModel
from typing import List, Dict, Any

class PanelComposerState(BaseModel):
    panels: List[Dict[str, Any]] | None = None
    page_groupings: List[Dict[str, Any]] | None = None
    page_statistics: Dict[str, Any] | None = None
    # Additional fields can be added as needed

async def run(state: PanelComposerState) -> PanelComposerState:
    """Placeholder implementation – groups panels into pages.

    Uses the existing `panel_composer` service to create page groupings based on
    panel content and emotional intensity.
    """
    if not state.panels:
        return state.model_copy(update={
            "error": "No panels provided",
            "page_groupings": None,
            "page_statistics": None
        })

    from app.services.panel_composer import group_panels_into_pages, calculate_page_statistics
    from app.models.story import WebtoonPanel

    # Convert dict panels to model instances
    panel_objs = [WebtoonPanel(**p) for p in state.panels]

    # Group into pages
    pages = group_panels_into_pages(panel_objs)
    stats = calculate_page_statistics(pages)

    # Serialize page data
    page_data = []
    for page in pages:
        page_data.append({
            "page_number": page.page_number,
            "panel_indices": page.panel_indices,
            "panel_count": page.panel_count,
            "layout_type": page.layout_type.value,
            "is_single_panel": page.is_single_panel,
            "reasoning": page.reasoning,
        })

    return state.model_copy(update={
        "page_groupings": page_data,
        "page_statistics": stats
    })
