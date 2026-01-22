"""
SFX Planner Service for Webtoon Enhancement.

This module provides functionality to automatically suggest and plan visual
effects (SFX) for webtoon panels based on their emotional content and actions.

It supports two modes:
1. Rule-based: Uses SFX_TRIGGERS mapping for fast, deterministic suggestions
2. LLM-based: Uses an LLM for more nuanced, context-aware suggestions

v2.0.0: Initial implementation
"""

import json
import logging
import re
from typing import List, Optional, Dict, Any

from app.models.sfx import (
    ImpactText,
    ImpactTextStyle,
    ImpactTextSize,
    MotionEffect,
    MotionEffectType,
    MotionDirection,
    ScreenEffect,
    ScreenEffectType,
    EmotionalEffect,
    EmotionalEffectType,
    EmotionalEffectPosition,
    EffectIntensity,
    SFXBundle,
    SFXTiming,
    SFX_TRIGGERS,
    get_suggested_sfx,
)
from app.models.story import WebtoonPanel
from app.prompt.sfx_planner import (
    SFX_PLANNER_SYSTEM_PROMPT,
    SFX_PLANNER_USER_PROMPT,
    PANEL_CONTEXT_FORMAT,
)


logger = logging.getLogger(__name__)


# ============================================================================
# Extended Trigger Mappings (1.6.3)
# ============================================================================

# Keywords that trigger specific emotions/actions
EMOTION_KEYWORDS = {
    "anger": ["angry", "furious", "rage", "mad", "frustrated", "irritated", "annoyed"],
    "love": ["love", "adore", "crush", "attracted", "romantic", "affection"],
    "fear": ["scared", "afraid", "terrified", "frightened", "nervous", "anxious", "worried"],
    "sad": ["sad", "crying", "tears", "depressed", "heartbroken", "grief", "sorrow"],
    "happy": ["happy", "joy", "excited", "thrilled", "elated", "delighted"],
    "surprise": ["surprised", "shocked", "startled", "amazed", "astonished"],
    "shock": ["shock", "disbelief", "horrified", "traumatized"],
    "romantic": ["blush", "heart", "romantic", "intimate", "tender"],
    "comedy": ["funny", "laugh", "awkward", "embarrassed", "silly"],
    "nervous": ["nervous", "sweating", "anxious", "tense", "uneasy"],
}

ACTION_KEYWORDS = {
    "impact": ["hit", "punch", "kick", "slam", "crash", "strike", "smash", "bang"],
    "run": ["run", "running", "sprint", "dash", "chase", "flee"],
    "fall": ["fall", "falling", "trip", "stumble", "collapse"],
    "realization": ["realize", "understand", "discover", "epiphany", "revelation"],
    "dramatic_entrance": ["enter", "appear", "arrive", "dramatic", "entrance"],
}

# Intensity to effect intensity mapping
INTENSITY_MAP = {
    (1, 3): EffectIntensity.SUBTLE,
    (4, 6): EffectIntensity.MEDIUM,
    (7, 10): EffectIntensity.INTENSE,
}


def _map_intensity(emotional_intensity: int) -> EffectIntensity:
    """Map 1-10 emotional intensity to effect intensity."""
    for (low, high), intensity in INTENSITY_MAP.items():
        if low <= emotional_intensity <= high:
            return intensity
    return EffectIntensity.MEDIUM


def _detect_emotion_from_text(text: str) -> Optional[str]:
    """Detect emotion keyword from dialogue/description text."""
    text_lower = text.lower()
    
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return emotion
    
    return None


def _detect_action_from_text(text: str) -> Optional[str]:
    """Detect action keyword from dialogue/description text."""
    text_lower = text.lower()
    
    for action, keywords in ACTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return action
    
    return None


# ============================================================================
# SFX Planner Class (1.6.2, 1.6.4)
# ============================================================================

class SFXPlanner:
    """
    Plans and suggests visual effects for webtoon panels.
    
    This planner analyzes panel content and suggests appropriate SFX
    to enhance the visual storytelling.
    """
    
    def __init__(self, use_llm: bool = False, llm_client=None):
        """
        Initialize the SFX planner.
        
        Args:
            use_llm: Whether to use LLM for suggestions (vs rule-based)
            llm_client: Optional LLM client for LLM-based planning
        """
        self._use_llm = use_llm
        self._llm_client = llm_client
    
    def plan_sfx(
        self,
        panels: List[WebtoonPanel]
    ) -> List[SFXBundle]:
        """
        Plan SFX for a list of webtoon panels.
        
        This is the main entry point for SFX planning. It analyzes each
        panel and returns a list of SFXBundle objects with suggested effects.
        
        Args:
            panels: List of WebtoonPanel objects to analyze
            
        Returns:
            List of SFXBundle objects, one per panel
        """
        if self._use_llm and self._llm_client:
            return self._plan_sfx_with_llm(panels)
        else:
            return self._plan_sfx_rule_based(panels)
    
    def _plan_sfx_rule_based(
        self,
        panels: List[WebtoonPanel]
    ) -> List[SFXBundle]:
        """
        Plan SFX using rule-based trigger mapping.
        
        This is fast and deterministic, suitable for most use cases.
        """
        bundles = []
        
        for panel in panels:
            bundle = self._analyze_panel(panel)
            bundles.append(bundle)
        
        return bundles
    
    def _analyze_panel(self, panel: WebtoonPanel) -> SFXBundle:
        """
        Analyze a single panel and generate SFX suggestions.
        
        Args:
            panel: WebtoonPanel to analyze
            
        Returns:
            SFXBundle with suggested effects
        """
        bundle = SFXBundle(panel_number=panel.panel_number)
        
        # Combine text sources for analysis
        dialogue_texts = []
        if panel.dialogue:
            for d in panel.dialogue:
                if isinstance(d, dict):
                    dialogue_texts.append(d.get('text', ''))
                else:
                    dialogue_texts.append(str(d))
        
        combined_text = " ".join([
            panel.visual_prompt or "",
            " ".join(dialogue_texts),
        ])
        
        # Get emotional intensity
        intensity = getattr(panel, 'emotional_intensity', 5)
        effect_intensity = _map_intensity(intensity)
        
        # Detect emotion from text
        detected_emotion = _detect_emotion_from_text(combined_text)
        
        # Detect action from visual prompt
        detected_action = _detect_action_from_text(panel.visual_prompt or "")
        
        # Apply effects based on detected emotion
        if detected_emotion:
            self._apply_emotion_effects(bundle, detected_emotion, effect_intensity)
        
        # Apply effects based on detected action
        if detected_action:
            self._apply_action_effects(bundle, detected_action, effect_intensity)
        
        # High intensity panels get additional screen effects
        if intensity >= 8:
            self._apply_high_intensity_effects(bundle, effect_intensity)
        
        # Limit effects to prevent overload
        self._limit_effects(bundle, max_per_category=2)
        
        return bundle
    
    def _apply_emotion_effects(
        self,
        bundle: SFXBundle,
        emotion: str,
        intensity: EffectIntensity
    ):
        """Apply effects based on detected emotion."""
        suggestions = get_suggested_sfx(emotion)
        
        for suggestion in suggestions:
            sfx_type = suggestion.get("type")
            
            if sfx_type == "emotional":
                effect_name = suggestion.get("effect")
                try:
                    effect_type = EmotionalEffectType(effect_name)
                    effect = EmotionalEffect(
                        type=effect_type,
                        intensity=intensity,
                        position=EmotionalEffectPosition.AROUND_CHARACTER
                    )
                    bundle.emotional_effects.append(effect)
                except ValueError:
                    pass
            
            elif sfx_type == "screen":
                effect_name = suggestion.get("effect")
                try:
                    effect_type = ScreenEffectType(effect_name)
                    effect = ScreenEffect(
                        type=effect_type,
                        intensity=intensity
                    )
                    bundle.screen_effects.append(effect)
                except ValueError:
                    pass
            
            elif sfx_type == "impact_text":
                text = suggestion.get("text", "!")
                style_name = suggestion.get("style", "bold")
                try:
                    style = ImpactTextStyle(style_name)
                except ValueError:
                    style = ImpactTextStyle.BOLD
                
                impact = ImpactText(
                    text=text,
                    style=style,
                    position=(0.8, 0.3),
                    size=ImpactTextSize.MEDIUM if intensity == EffectIntensity.MEDIUM else ImpactTextSize.LARGE
                )
                bundle.impact_texts.append(impact)
    
    def _apply_action_effects(
        self,
        bundle: SFXBundle,
        action: str,
        intensity: EffectIntensity
    ):
        """Apply effects based on detected action."""
        suggestions = get_suggested_sfx(action)
        
        for suggestion in suggestions:
            sfx_type = suggestion.get("type")
            
            if sfx_type == "motion":
                effect_name = suggestion.get("effect")
                direction_name = suggestion.get("direction", "center")
                try:
                    effect_type = MotionEffectType(effect_name)
                    direction = MotionDirection(direction_name)
                    effect = MotionEffect(
                        type=effect_type,
                        direction=direction,
                        intensity=intensity
                    )
                    bundle.motion_effects.append(effect)
                except ValueError:
                    pass
            
            elif sfx_type == "screen":
                effect_name = suggestion.get("effect")
                try:
                    effect_type = ScreenEffectType(effect_name)
                    effect = ScreenEffect(
                        type=effect_type,
                        intensity=intensity
                    )
                    bundle.screen_effects.append(effect)
                except ValueError:
                    pass
            
            elif sfx_type == "impact_text":
                text = suggestion.get("text", "!")
                style_name = suggestion.get("style", "bold")
                try:
                    style = ImpactTextStyle(style_name)
                except ValueError:
                    style = ImpactTextStyle.BOLD
                
                size = ImpactTextSize.LARGE if intensity == EffectIntensity.INTENSE else ImpactTextSize.MEDIUM
                
                impact = ImpactText(
                    text=text,
                    style=style,
                    position=(0.7, 0.3),
                    size=size
                )
                bundle.impact_texts.append(impact)
    
    def _apply_high_intensity_effects(
        self,
        bundle: SFXBundle,
        intensity: EffectIntensity
    ):
        """Apply additional effects for high-intensity panels."""
        # Add vignette for focus
        if not any(e.type == ScreenEffectType.VIGNETTE for e in bundle.screen_effects):
            bundle.screen_effects.append(
                ScreenEffect(type=ScreenEffectType.VIGNETTE, intensity=EffectIntensity.SUBTLE)
            )
    
    def _limit_effects(self, bundle: SFXBundle, max_per_category: int = 2):
        """Limit effects per category to prevent visual overload."""
        bundle.impact_texts = bundle.impact_texts[:max_per_category]
        bundle.motion_effects = bundle.motion_effects[:max_per_category]
        bundle.screen_effects = bundle.screen_effects[:max_per_category]
        bundle.emotional_effects = bundle.emotional_effects[:max_per_category]
    
    def _plan_sfx_with_llm(
        self,
        panels: List[WebtoonPanel]
    ) -> List[SFXBundle]:
        """
        Plan SFX using LLM for more nuanced suggestions.
        
        This requires an LLM client to be configured.
        """
        if not self._llm_client:
            logger.warning("LLM client not configured, falling back to rule-based")
            return self._plan_sfx_rule_based(panels)
        
        # Format panels for LLM
        panels_json = []
        for panel in panels:
            dialogue_text = ""
            if panel.dialogue:
                dialogue_text = " ".join(
                    d.get('text', '') if isinstance(d, dict) else str(d)
                    for d in panel.dialogue
                )
            panel_data = {
                "panel_number": panel.panel_number,
                "visual_description": panel.visual_prompt or "",
                "dialogue": dialogue_text,
                "emotion": getattr(panel, 'emotion', 'neutral'),
                "intensity": getattr(panel, 'emotional_intensity', 5),
                "action": getattr(panel, 'action', 'none'),
            }
            panels_json.append(PANEL_CONTEXT_FORMAT.format(**panel_data))
        
        # Call LLM
        user_prompt = SFX_PLANNER_USER_PROMPT.format(
            panels_json="\n".join(panels_json)
        )
        
        try:
            response = self._llm_client.generate(
                system_prompt=SFX_PLANNER_SYSTEM_PROMPT,
                user_prompt=user_prompt
            )
            
            # Parse response
            bundles = self._parse_llm_response(response, panels)
            return bundles
            
        except Exception as e:
            logger.error(f"LLM SFX planning failed: {e}, falling back to rule-based")
            return self._plan_sfx_rule_based(panels)
    
    def _parse_llm_response(
        self,
        response: str,
        panels: List[WebtoonPanel]
    ) -> List[SFXBundle]:
        """Parse LLM response into SFXBundle objects."""
        bundles = []
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                suggestions = json.loads(json_match.group())
                
                for suggestion in suggestions:
                    panel_num = suggestion.get("panel_number", 1)
                    bundle = self._convert_suggestion_to_bundle(suggestion, panel_num)
                    bundles.append(bundle)
        
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response: {e}")
        
        # Fill in missing panels with empty bundles
        panel_numbers = {b.panel_number for b in bundles}
        for panel in panels:
            if panel.panel_number not in panel_numbers:
                bundles.append(SFXBundle(panel_number=panel.panel_number))
        
        # Sort by panel number
        bundles.sort(key=lambda b: b.panel_number)
        
        return bundles
    
    def _convert_suggestion_to_bundle(
        self,
        suggestion: Dict[str, Any],
        panel_number: int
    ) -> SFXBundle:
        """Convert LLM suggestion dict to SFXBundle."""
        bundle = SFXBundle(panel_number=panel_number)
        
        effects = suggestion.get("suggested_effects", {})
        
        # Parse impact texts
        for it in effects.get("impact_texts", []):
            try:
                bundle.impact_texts.append(ImpactText(
                    text=it.get("text", "!"),
                    style=ImpactTextStyle(it.get("style", "bold")),
                    position=tuple(it.get("position", [0.5, 0.3])),
                    size=ImpactTextSize(it.get("size", "medium"))
                ))
            except (ValueError, TypeError):
                pass
        
        # Parse motion effects
        for me in effects.get("motion_effects", []):
            try:
                bundle.motion_effects.append(MotionEffect(
                    type=MotionEffectType(me.get("type", "speed_lines")),
                    direction=MotionDirection(me.get("direction", "center")),
                    intensity=EffectIntensity(me.get("intensity", "medium"))
                ))
            except (ValueError, TypeError):
                pass
        
        # Parse screen effects
        for se in effects.get("screen_effects", []):
            try:
                bundle.screen_effects.append(ScreenEffect(
                    type=ScreenEffectType(se.get("type", "flash")),
                    intensity=EffectIntensity(se.get("intensity", "medium"))
                ))
            except (ValueError, TypeError):
                pass
        
        # Parse emotional effects
        for ee in effects.get("emotional_effects", []):
            try:
                bundle.emotional_effects.append(EmotionalEffect(
                    type=EmotionalEffectType(ee.get("type", "sparkles")),
                    position=EmotionalEffectPosition(ee.get("position", "around_character"))
                ))
            except (ValueError, TypeError):
                pass
        
        return bundle


# ============================================================================
# Convenience Functions
# ============================================================================

def create_sfx_planner(use_llm: bool = False, llm_client=None) -> SFXPlanner:
    """
    Factory function to create an SFX planner.
    
    Args:
        use_llm: Whether to use LLM-based planning
        llm_client: Optional LLM client instance
        
    Returns:
        SFXPlanner instance
    """
    return SFXPlanner(use_llm=use_llm, llm_client=llm_client)


def plan_sfx_for_panels(panels: List[WebtoonPanel]) -> List[SFXBundle]:
    """
    Convenience function to plan SFX for panels using rule-based approach.
    
    Args:
        panels: List of WebtoonPanel objects
        
    Returns:
        List of SFXBundle objects
    """
    planner = SFXPlanner()
    return planner.plan_sfx(panels)
