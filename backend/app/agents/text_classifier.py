# text_classifier.py
"""
Text Type Classifier Agent (v2.1.0 E2-T01)

Classifies dialogue/text in webtoon panels into types:
- DIALOGUE: Standard speech bubbles (round)
- MONOLOGUE: Internal thoughts (square box)
- SFX: Atmospheric/sound effects (artistic floating text)
- NARRATION: Story narration (narrator box)

This agent runs after scene planning to classify all text
before rendering, ensuring appropriate visual treatment.
"""

import logging
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.models.story import TextType, DialogueLine, SFX_KEYWORDS, MONOLOGUE_PATTERNS

logger = logging.getLogger(__name__)


class TextClassifierState(BaseModel):
    """State for the Text Classifier agent."""
    panels: List[Dict[str, Any]] | None = None
    classified_panels: List[Dict[str, Any]] | None = None
    classification_stats: Dict[str, int] | None = None
    error: str | None = None


def classify_text(text: str, character: str = "") -> TextType:
    """
    Classify a single text string into its type.
    
    Classification priority (highest to lowest):
    1. SFX - Check for sound/atmosphere keywords first
    2. Monologue - Thought patterns (*, (), [])
    3. Narration - Narrator character
    4. Dialogue - Default
    
    Args:
        text: The text to classify
        character: Optional character name for context
        
    Returns:
        TextType enum value
    """
    import re
    
    text_stripped = text.strip()
    text_lower = text_stripped.lower()
    
    # PRIORITY 1: Check for SFX first (before monologue patterns)
    # This ensures *Silence*, *Thump* etc. are classified as SFX, not monologue
    if text_stripped.startswith("*") and text_stripped.endswith("*"):
        inner_text = text_stripped[1:-1].lower().strip()
        # Check if inner text matches SFX keywords
        if any(kw in inner_text for kw in SFX_KEYWORDS):
            return TextType.SFX
        # Also check if the entire inner text IS an SFX keyword
        if inner_text in SFX_KEYWORDS:
            return TextType.SFX
    
    # Standalone SFX (just the keyword without asterisks)
    if text_lower in SFX_KEYWORDS:
        return TextType.SFX
    
    # PRIORITY 2: Check for monologue patterns (*, (), [], etc.)
    # Only after SFX check, so *I'm thinking...* is monologue but *Silence* is SFX
    for pattern in MONOLOGUE_PATTERNS:
        if re.match(pattern, text_stripped):
            return TextType.MONOLOGUE
    
    # PRIORITY 3: Check for narration by character name
    if character.lower() in ["narrator", "나레이터", "system", "narration"]:
        return TextType.NARRATION
    
    # Also check content-based narration (no character, narrative text)
    if not character or character.strip() == "":
        narration_indicators = ["the next day", "meanwhile", "later that", "hours passed", "time went by", "once upon"]
        if any(ind in text_lower for ind in narration_indicators):
            return TextType.NARRATION
    
    # PRIORITY 4: Default to dialogue
    return TextType.DIALOGUE


def classify_panel_dialogue(dialogue_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Classify all dialogue entries in a panel.
    
    Args:
        dialogue_list: List of dialogue dicts [{'character': '...', 'text': '...'}]
        
    Returns:
        Enhanced dialogue list with text_type added
    """
    if not dialogue_list:
        return []
    
    classified = []
    for i, entry in enumerate(dialogue_list):
        character = entry.get("character", "")
        text = entry.get("text", "")
        
        # Classify
        text_type = classify_text(text, character)
        
        # Create enhanced entry
        classified_entry = {
            **entry,
            "text_type": text_type.value,
            "order": entry.get("order", i + 1)
        }
        classified.append(classified_entry)
    
    return classified


async def run(state: TextClassifierState) -> TextClassifierState:
    """
    Text Classifier Agent: Classifies all dialogue/text in panels.
    
    v2.1.0 E2-T01: Ensures proper visual treatment for:
    - Regular dialogue → Round speech bubbles
    - Internal monologue → Square thought boxes
    - SFX/Atmosphere → Artistic floating text
    - Narration → Narrator boxes
    
    Args:
        state: Input state with panels
        
    Returns:
        Updated state with classified_panels and stats
    """
    if not state.panels:
        return state.model_copy(update={
            "error": "No panels provided",
            "classified_panels": None,
            "classification_stats": None
        })
    
    # Statistics tracking
    stats = {
        "dialogue": 0,
        "monologue": 0,
        "sfx": 0,
        "narration": 0,
        "total_entries": 0
    }
    
    classified_panels = []
    
    for panel in state.panels:
        dialogue_list = panel.get("dialogue", [])
        
        if dialogue_list:
            # Classify all dialogue in this panel
            classified_dialogue = classify_panel_dialogue(dialogue_list)
            
            # Update stats
            for entry in classified_dialogue:
                text_type = entry.get("text_type", "dialogue")
                stats[text_type] = stats.get(text_type, 0) + 1
                stats["total_entries"] += 1
            
            # Update panel with classified dialogue
            classified_panel = {
                **panel,
                "dialogue": classified_dialogue
            }
        else:
            classified_panel = panel
        
        classified_panels.append(classified_panel)
    
    logger.info(
        f"Text Classifier: Processed {len(classified_panels)} panels. "
        f"Stats: {stats['dialogue']} dialogue, {stats['monologue']} monologue, "
        f"{stats['sfx']} SFX, {stats['narration']} narration"
    )
    
    return state.model_copy(update={
        "classified_panels": classified_panels,
        "classification_stats": stats
    })


# Convenience function for use in workflow
def classify_dialogue_in_script(panels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convenience function to classify dialogue in a list of panels.
    
    Can be used directly without the async agent pattern.
    
    Args:
        panels: List of panel dicts
        
    Returns:
        Panels with classified dialogue
    """
    classified = []
    for panel in panels:
        dialogue_list = panel.get("dialogue", [])
        if dialogue_list:
            classified_dialogue = classify_panel_dialogue(dialogue_list)
            classified.append({**panel, "dialogue": classified_dialogue})
        else:
            classified.append(panel)
    return classified
