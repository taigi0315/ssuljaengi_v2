"""
Modular Prompt Architecture (v2.1.0 - E4-T01)

This module implements a modular prompt system that separates monolithic prompts
into composable, focused modules. This approach:

1. Reduces context window overflow by prioritizing critical information
2. Prevents "Attention Loss" in image generation models
3. Enables fine-grained control over prompt composition
4. Keeps prompts under 800 tokens for optimal model performance

Architecture:
- Core Style Module: Technical specs, quality modifiers (LOWEST priority)
- Character Ref Module: Character consistency directives (HIGHEST priority)  
- Scene Action Module: Shot composition, environment, emotions (MEDIUM priority)

The final prompt is assembled in priority order:
CHARACTER_REF (top) → SCENE_ACTION (middle) → CORE_STYLE (bottom)
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class PromptPriority(Enum):
    """Priority levels for prompt modules. Higher = placed earlier in final prompt."""
    CRITICAL = 1    # Character consistency - TOP of prompt
    HIGH = 2        # Scene action/emotion
    MEDIUM = 3      # Environment details
    LOW = 4         # Technical specs/quality


@dataclass
class PromptModule:
    """A single composable prompt module."""
    name: str
    priority: PromptPriority
    content: str
    max_tokens: int = 200  # Target maximum tokens for this module
    
    def __post_init__(self):
        # Rough token estimation (1 token ≈ 4 chars for English)
        self.estimated_tokens = len(self.content) // 4


# =============================================================================
# CORE STYLE MODULE - Technical specifications (LOW priority)
# =============================================================================

CORE_STYLE_TEMPLATE = """[TECHNICAL SPECS]
• Aspect: 9:16 VERTICAL (portrait)
• Quality: 4K, HDR, professional webtoon art
• Style: {art_style}
• NO text/speech bubbles (overlaid separately)"""


def build_core_style_module(art_style: str = "Korean webtoon") -> PromptModule:
    """Build the core style module with technical specifications."""
    content = CORE_STYLE_TEMPLATE.format(art_style=art_style)
    return PromptModule(
        name="core_style",
        priority=PromptPriority.LOW,
        content=content,
        max_tokens=100
    )


# =============================================================================
# CHARACTER REF MODULE - Character consistency (CRITICAL priority)
# =============================================================================

CHARACTER_REF_TEMPLATE = """[CHARACTER CONSISTENCY - CRITICAL]
{character_sheet}

⚠️ MAINTAIN EXACT appearance from reference images.
⚠️ DO NOT change outfits, hair, or features."""


def build_character_ref_module(
    characters: List[Dict[str, Any]],
    include_warning: bool = True
) -> PromptModule:
    """
    Build character reference module for consistency.
    
    This module is placed at the TOP of the prompt to ensure
    maximum attention from the image generation model.
    
    Args:
        characters: List of character dictionaries
        include_warning: Whether to include consistency warnings
    """
    if not characters:
        return PromptModule(
            name="character_ref",
            priority=PromptPriority.CRITICAL,
            content="[No characters defined]",
            max_tokens=50
        )
    
    char_lines = []
    for char in characters:
        name = char.get("name", "Unknown")
        parts = [f"• {name}:"]
        
        # Compact key attributes only
        if char.get("hair"):
            parts.append(f"hair={char['hair']}")
        if char.get("face"):
            parts.append(f"face={char['face']}")
        if char.get("outfit"):
            parts.append(f"outfit={char['outfit']}")
        if char.get("body"):
            parts.append(f"build={char['body']}")
            
        char_lines.append(" ".join(parts))
    
    character_sheet = "\n".join(char_lines)
    
    if include_warning:
        content = CHARACTER_REF_TEMPLATE.format(character_sheet=character_sheet)
    else:
        content = f"[CHARACTERS]\n{character_sheet}"
    
    return PromptModule(
        name="character_ref",
        priority=PromptPriority.CRITICAL,
        content=content,
        max_tokens=200
    )


# =============================================================================
# SCENE ACTION MODULE - Shot composition & emotion (HIGH priority)
# =============================================================================

SCENE_ACTION_TEMPLATE = """[SCENE]
Shot: {shot_type}
Emotion: {emotional_tone}
Action: {action_description}

[ENVIRONMENT]
{environment_brief}"""


def build_scene_action_module(
    shot_type: str,
    emotional_tone: str,
    action_description: str,
    environment_brief: str
) -> PromptModule:
    """
    Build scene action module with shot and emotion context.
    
    Kept concise to prevent prompt drift while maintaining
    essential visual direction.
    """
    content = SCENE_ACTION_TEMPLATE.format(
        shot_type=shot_type,
        emotional_tone=emotional_tone,
        action_description=action_description,
        environment_brief=environment_brief
    )
    
    return PromptModule(
        name="scene_action",
        priority=PromptPriority.HIGH,
        content=content,
        max_tokens=200
    )


# =============================================================================
# VISUAL DESCRIPTION MODULE - Main visual prompt (HIGH priority)
# =============================================================================

def build_visual_description_module(visual_prompt: str) -> PromptModule:
    """Build the main visual description module."""
    # Truncate if too long (>300 tokens ≈ 1200 chars)
    max_chars = 3000  # Increased to prevent environment loss
    if len(visual_prompt) > max_chars:
        visual_prompt = visual_prompt[:max_chars] + "..."
    
    content = f"[VISUAL]\n{visual_prompt}"
    
    return PromptModule(
        name="visual_description",
        priority=PromptPriority.HIGH,
        content=content,
        max_tokens=500  # Increased from 300
    )


# =============================================================================
# STYLE & MOOD MODULE - From visual_prompter (MEDIUM priority)
# =============================================================================

def build_style_mood_module(style_keywords: str) -> PromptModule:
    """Build style and mood enhancement module."""
    if not style_keywords:
        return PromptModule(
            name="style_mood",
            priority=PromptPriority.MEDIUM,
            content="",
            max_tokens=0
        )
        
    content = f"[STYLE & MOOD]\n{style_keywords}"
    
    return PromptModule(
        name="style_mood",
        priority=PromptPriority.MEDIUM,
        content=content,
        max_tokens=150
    )


# =============================================================================
# NEGATIVE PROMPT MODULE - Quality control (v2.1.0 E4-T03)
# =============================================================================

STANDARD_NEGATIVE_PROMPT = (
    "speech bubble, word, logo, watermark, signature, "
    "error, jpeg artifacts, username, artist name, greyscale, monochrome"
)

def build_negative_prompt_module(
    custom_negative: str = "",
    use_standard: bool = True
) -> PromptModule:
    """
    Build negative prompt module.
    
    Used to exclude unwanted elements. Negative prompts are technically
    handled separately by most APIs, but for prompt engineering structure
    we include it here as a module that can be extracted.
    """
    parts = []
    if use_standard:
        parts.append(STANDARD_NEGATIVE_PROMPT)
    if custom_negative:
        parts.append(custom_negative)
        
    content = ", ".join(parts)
    
    return PromptModule(
        name="negative_prompt",
        priority=PromptPriority.LOW,
        content=f"[NEGATIVE]\n{content}",
        max_tokens=100
    )

def get_clean_negative_prompt(
    prompt_str: str, 
    remove_standard: bool = False
) -> str:
    """
    Extract clean negative prompt string (without [NEGATIVE] tag).
    Useful when API requires negative prompt as separate parameter.
    """
    if "[NEGATIVE]" in prompt_str:
        # If it was composed into the main string (not recommended for API use but good for debug)
        start = prompt_str.find("[NEGATIVE]") + 11
        return prompt_str[start:].strip()
    
    # Otherwise return standard
    return STANDARD_NEGATIVE_PROMPT if not remove_standard else ""


# =============================================================================
# PROMPT COMPOSER - Assembles modules into final prompt
# =============================================================================

class ModularPromptComposer:
    """
    Composes multiple prompt modules into a single optimized prompt.
    
    Features:
    - Priority-based ordering (CRITICAL first)
    - Token budget management
    - Automatic truncation warnings
    """
    
    def __init__(self, max_total_tokens: int = 800):
        self.max_total_tokens = max_total_tokens
        self.modules: List[PromptModule] = []
    
    def add_module(self, module: PromptModule) -> "ModularPromptComposer":
        """Add a module to the composer."""
        self.modules.append(module)
        return self
    
    def add_modules(self, modules: List[PromptModule]) -> "ModularPromptComposer":
        """Add multiple modules."""
        self.modules.extend(modules)
        return self
    
    def compose(self, separator: str = "\n\n") -> str:
        """
        Compose all modules into a final prompt string.
        
        Modules are sorted by priority (CRITICAL first, LOW last).
        
        Returns:
            Composed prompt string
        """
        # Sort by priority (lower enum value = higher priority)
        sorted_modules = sorted(self.modules, key=lambda m: m.priority.value)
        
        # Estimate total tokens
        total_estimated = sum(m.estimated_tokens for m in sorted_modules)
        
        if total_estimated > self.max_total_tokens:
            # Log warning (in production, use proper logging)
            import logging
            logging.warning(
                f"Prompt exceeds token budget: ~{total_estimated} > {self.max_total_tokens}. "
                "Consider reducing module content."
            )
        
        # Compose
        parts = [m.content for m in sorted_modules]
        return separator.join(parts)
    
    def get_token_breakdown(self) -> Dict[str, int]:
        """Get estimated token count per module."""
        return {m.name: m.estimated_tokens for m in self.modules}
    
    def get_total_estimated_tokens(self) -> int:
        """Get total estimated tokens."""
        return sum(m.estimated_tokens for m in self.modules)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def compose_scene_prompt(
    characters: List[Dict[str, Any]],
    visual_prompt: str,
    shot_type: str = "medium_shot",
    emotional_tone: str = "neutral",
    action_description: str = "",
    environment_brief: str = "",
    style_keywords: str = "",
    art_style: str = "Korean webtoon"
) -> str:
    """
    Convenience function to compose a complete scene prompt.
    
    This is the recommended entry point for generating scene prompts
    with the modular architecture.
    
    Args:
        characters: Character definitions for consistency
        visual_prompt: Main visual description
        shot_type: Camera shot type
        emotional_tone: Emotional mood of the scene
        action_description: What's happening in the scene
        environment_brief: Brief environment description
        style_keywords: Additional style/mood keywords
        art_style: Art style specification
        
    Returns:
        Composed prompt string optimized for image generation
    """
    composer = ModularPromptComposer(max_total_tokens=800)
    
    # Add modules in any order - they'll be sorted by priority
    composer.add_module(build_character_ref_module(characters))
    composer.add_module(build_visual_description_module(visual_prompt))
    
    if action_description or environment_brief:
        composer.add_module(build_scene_action_module(
            shot_type=shot_type,
            emotional_tone=emotional_tone,
            action_description=action_description,
            environment_brief=environment_brief
        ))
    
    if style_keywords:
        composer.add_module(build_style_mood_module(style_keywords))
    
    composer.add_module(build_core_style_module(art_style))
    
    return composer.compose()


def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 chars for English)."""
    return len(text) // 4
