# visual_prompter.py
"""Visual Prompter Agent

Enhances visual prompts with mood, style, and CHARACTER REFERENCE information
for image generation. This ensures character consistency across all panels.

v2.1.0 Updates:
- E3-T01: Added global character style sheet
- E3-T03: Character refs placed at TOP of every prompt
- E4-T01: Integrated modular prompt architecture with token management
"""

import logging
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class VisualPrompterState(BaseModel):
    panels: List[Dict[str, Any]] | None = None
    mood_assignments: List[Dict[str, Any]] | None = None
    image_style: str = "SOFT_ROMANTIC_WEBTOON"
    # v2.1.0: Global character style sheet for consistency
    characters: List[Dict[str, Any]] | None = None
    enhanced_prompts: List[str] | None = None
    # v2.1.0 E4-T01: Token statistics for monitoring
    prompt_token_stats: Dict[str, Any] | None = None
    # Additional fields can be added as needed


# Token budget configuration (E4-T01)
MAX_PROMPT_TOKENS = 800
TOKEN_WARNING_THRESHOLD = 700


def _estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 chars for English)."""
    return len(text) // 4


def _format_character_style_sheet(characters: List[Dict[str, Any]]) -> str:
    """
    Format character definitions into a concise style sheet.
    
    v2.1.0 E3-T01/E3-T03: This creates a consistent character reference block 
    that is placed at the TOP of every prompt to ensure maximum attention weight.
    
    Optimized for token efficiency while maintaining key visual attributes.
    
    Args:
        characters: List of character dictionaries with visual attributes
        
    Returns:
        Formatted character style sheet string
    """
    if not characters:
        return ""
    
    lines = ["[CHARACTER CONSISTENCY - CRITICAL]"]
    
    for char in characters:
        name = char.get("name", "Unknown")
        
        # Build compact but complete character line (token-efficient)
        attrs = []
        if char.get("hair"):
            attrs.append(f"hair={char['hair']}")
        if char.get("face"):
            attrs.append(f"face={char['face']}")
        if char.get("outfit"):
            attrs.append(f"outfit={char['outfit']}")
        if char.get("body"):
            attrs.append(f"build={char['body']}")
        
        if attrs:
            char_line = f"• {name}: {' '.join(attrs)}"
        else:
            # Fallback to visual_description if no structured attrs
            visual_desc = char.get("visual_description", "")
            if visual_desc:
                # Truncate long descriptions
                if len(visual_desc) > 100:
                    visual_desc = visual_desc[:100] + "..."
                char_line = f"• {name}: {visual_desc}"
            else:
                char_line = f"• {name}: (no visual attributes defined)"
        
        lines.append(char_line)
    
    lines.append("⚠️ MAINTAIN EXACT appearance. DO NOT change outfits.")
    
    return "\n".join(lines)


def _build_core_style_block(art_style: str = "Korean webtoon") -> str:
    """
    Build core style/technical block (placed at BOTTOM - lowest priority).
    
    v2.1.0 E4-T01: Kept minimal to save tokens for higher priority content.
    """
    return f"""[TECHNICAL]
• Aspect: 9:16 VERTICAL
• Style: {art_style}, 4K quality
• NO text/speech bubbles"""


async def run(state: VisualPrompterState) -> VisualPrompterState:
    """
    Visual Prompter: Enhances prompts using MODULAR ARCHITECTURE.

    v2.1.0 Enhancements:
    - E3-T01: Character style sheet at TOP of every prompt
    - E3-T03: Priority-based composition (Characters > Scene > Style)
    - E4-T01: Token budget management with warnings
    
    Prompt Structure (by priority):
    1. [CHARACTER CONSISTENCY] - CRITICAL priority (top)
    2. [VISUAL] - Main scene description (high)
    3. [STYLE & MOOD] - Style keywords (medium)
    4. [TECHNICAL] - Tech specs (lowest priority, bottom)
    """
    if not state.panels:
        return state.model_copy(update={
            "error": "No panels provided", 
            "enhanced_prompts": None
        })

    from app.services.style_composer import get_legacy_style_with_mood

    mood_assignments = state.mood_assignments or []
    characters = state.characters or []
    
    # Create mood lookup by panel_number
    mood_lookup = {m["panel_number"]: m for m in mood_assignments}
    
    # v2.1.0 E3-T01: Create global character style sheet (TOP priority)
    character_block = _format_character_style_sheet(characters)
    
    # v2.1.0 E4-T01: Core style block (BOTTOM priority)
    core_style_block = _build_core_style_block(state.image_style)

    enhanced_prompts = []
    token_stats = {
        "total_prompts": 0,
        "avg_tokens": 0,
        "max_tokens": 0,
        "min_tokens": float("inf"),
        "over_budget_count": 0,
        "per_panel": []
    }
    
    total_tokens = 0

    for panel in state.panels:
        panel_num = panel.get("panel_number")
        base_prompt = panel.get("visual_prompt", "")
        mood_data = mood_lookup.get(panel_num, {})

        # Get composed style with mood
        intensity = mood_data.get("intensity", 5)
        context = mood_data.get("detected_context", "neutral")

        style_keywords = get_legacy_style_with_mood(
            legacy_style_key=state.image_style,
            emotional_intensity=intensity,
            scene_context=context
        )

        # v2.1.0 E4-T01: MODULAR PROMPT COMPOSITION BY PRIORITY
        # Order: Character (critical) -> Visual (high) -> Style (medium) -> Tech (low)
        prompt_parts = []
        
        # 1. CHARACTER BLOCK - SKIPPED (Handled by Template Wrapper)
        # v2.1.0 Fix: Pruning redundant character block to avoid double-instruction
        # if character_block:
        #     prompt_parts.append(character_block)
        
        # 2. VISUAL DESCRIPTION - HIGH priority
        # Truncate if too long to stay within token budget
        visual_block = f"[VISUAL]\n{base_prompt}"
        if _estimate_tokens(visual_block) > 500: # Increased budget since we pruned other blocks
            # Truncate to ~2000 chars
            visual_block = f"[VISUAL]\n{base_prompt[:2000]}..."
        prompt_parts.append(visual_block)
        
        # 3. STYLE & MOOD - MEDIUM priority
        style_block = f"[STYLE & MOOD]\n{style_keywords}"
        prompt_parts.append(style_block)
        
        # 4. TECHNICAL - SKIPPED (Handled by Template Wrapper)
        # prompt_parts.append(core_style_block)
        
        # Compose final prompt
        enhanced = "\n\n".join(prompt_parts)
        enhanced_prompts.append(enhanced)
        
        # v2.1.0 E4-T01: Track token statistics
        prompt_tokens = _estimate_tokens(enhanced)
        total_tokens += prompt_tokens
        
        token_stats["per_panel"].append({
            "panel": panel_num,
            "tokens": prompt_tokens,
            "over_budget": prompt_tokens > MAX_PROMPT_TOKENS
        })
        
        if prompt_tokens > MAX_PROMPT_TOKENS:
            token_stats["over_budget_count"] += 1
            logger.warning(
                f"Panel {panel_num} prompt exceeds token budget: "
                f"~{prompt_tokens} > {MAX_PROMPT_TOKENS}"
            )
        elif prompt_tokens > TOKEN_WARNING_THRESHOLD:
            logger.info(
                f"Panel {panel_num} prompt approaching limit: ~{prompt_tokens} tokens"
            )
        
        token_stats["max_tokens"] = max(token_stats["max_tokens"], prompt_tokens)
        token_stats["min_tokens"] = min(token_stats["min_tokens"], prompt_tokens)

    # Finalize stats
    num_prompts = len(enhanced_prompts)
    token_stats["total_prompts"] = num_prompts
    token_stats["avg_tokens"] = total_tokens // num_prompts if num_prompts > 0 else 0
    if token_stats["min_tokens"] == float("inf"):
        token_stats["min_tokens"] = 0
    
    logger.info(
        f"Visual Prompter: Generated {num_prompts} prompts. "
        f"Avg tokens: ~{token_stats['avg_tokens']}, "
        f"Over budget: {token_stats['over_budget_count']}"
    )

    return state.model_copy(update={
        "enhanced_prompts": enhanced_prompts,
        "prompt_token_stats": token_stats
    })

