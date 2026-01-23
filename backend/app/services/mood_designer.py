"""
Mood Designer Service for Webtoon Enhancement.

This module provides functionality to automatically analyze webtoon panels
and assign appropriate visual mood settings (SceneMood) based on:
- Emotional intensity
- Scene context (dialogue, visual description, story beat)
- Shot type
- Narrative flow

It supports two modes:
1. Rule-based: Fast, deterministic mood assignment using keyword detection
2. LLM-based: More nuanced, context-aware mood assignment

v2.0.0: Initial implementation
"""

import json
import logging
import re
from typing import List, Optional, Dict, Any, Tuple

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
    get_mood_preset,
    get_mood_for_intensity,
)
from app.prompt.mood_designer import (
    MOOD_DESIGNER_SYSTEM_PROMPT,
    MOOD_DESIGNER_USER_PROMPT,
    PANEL_CONTEXT_FORMAT,
    EMOTION_CONTEXT_KEYWORDS,
    INTENSITY_KEYWORDS,
)


logger = logging.getLogger(__name__)


# ============================================================================
# Mood Assignment Result
# ============================================================================

class MoodAssignment:
    """
    Result of mood assignment for a single panel.

    Contains the assigned SceneMood plus metadata about the assignment.
    """

    def __init__(
        self,
        panel_number: int,
        mood: SceneMood,
        detected_context: str = "neutral",
        confidence: float = 1.0,
        reasoning: str = ""
    ):
        """
        Initialize mood assignment.

        Args:
            panel_number: Panel number this assignment is for
            mood: The assigned SceneMood
            detected_context: Detected emotional context
            confidence: Confidence in the assignment (0-1)
            reasoning: Explanation of why this mood was chosen
        """
        self.panel_number = panel_number
        self.mood = mood
        self.detected_context = detected_context
        self.confidence = confidence
        self.reasoning = reasoning

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "panel_number": self.panel_number,
            "mood_name": self.mood.name,
            "detected_context": self.detected_context,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "mood_settings": {
                "color_temperature": self.mood.color_temperature.value,
                "saturation": self.mood.saturation.value,
                "lighting_mood": self.mood.lighting_mood.value,
                "intensity": self.mood.intensity,
                "special_effects": [e.value for e in self.mood.special_effects],
            }
        }


# ============================================================================
# Context Detection Functions
# ============================================================================

def detect_context_from_text(text: str) -> Tuple[str, float]:
    """
    Detect emotional context from text using keyword matching.

    Args:
        text: Combined text from dialogue, visual description, story beat

    Returns:
        Tuple of (context_name, confidence_score)
    """
    if not text:
        return ("neutral", 0.5)

    text_lower = text.lower()

    # Count keyword matches for each context
    context_scores: Dict[str, int] = {}

    for context, keywords in EMOTION_CONTEXT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            context_scores[context] = score

    if not context_scores:
        return ("neutral", 0.5)

    # Find best matching context
    best_context = max(context_scores, key=context_scores.get)
    best_score = context_scores[best_context]

    # Calculate confidence based on number of matches
    # More matches = higher confidence
    confidence = min(0.95, 0.5 + (best_score * 0.1))

    return (best_context, confidence)


def detect_intensity_modifier(text: str) -> int:
    """
    Detect intensity modifier from text.

    Args:
        text: Text to analyze

    Returns:
        Intensity modifier (-2 to +2)
    """
    if not text:
        return 0

    text_lower = text.lower()
    modifier = 0

    # Check for high intensity keywords
    for keyword in INTENSITY_KEYWORDS["high"]:
        if keyword in text_lower:
            modifier += 1
            break

    # Check for low intensity keywords
    for keyword in INTENSITY_KEYWORDS["low"]:
        if keyword in text_lower:
            modifier -= 1
            break

    return max(-2, min(2, modifier))


def get_shot_type_mood_bias(shot_type: str) -> Dict[str, Any]:
    """
    Get mood parameter biases based on shot type.

    Different shot types tend to work better with certain moods.

    Args:
        shot_type: The shot type string

    Returns:
        Dictionary of mood parameter suggestions
    """
    shot_lower = shot_type.lower() if shot_type else ""

    if "close" in shot_lower or "detail" in shot_lower:
        # Close-ups are good for emotional intensity
        return {
            "detail_level": DetailLevel.FOCUS_CHARACTER,
            "expression_style": ExpressionStyle.DRAMATIC,
            "intensity_boost": 1
        }

    elif "wide" in shot_lower or "establishing" in shot_lower:
        # Wide shots are good for atmosphere
        return {
            "detail_level": DetailLevel.HIGH,
            "expression_style": ExpressionStyle.NORMAL,
            "intensity_boost": -1
        }

    elif "medium" in shot_lower:
        # Medium shots are versatile
        return {
            "detail_level": DetailLevel.STANDARD,
            "expression_style": ExpressionStyle.NORMAL,
            "intensity_boost": 0
        }

    else:
        return {
            "detail_level": DetailLevel.STANDARD,
            "expression_style": ExpressionStyle.NORMAL,
            "intensity_boost": 0
        }


# ============================================================================
# Mood Designer Service Class
# ============================================================================

class MoodDesigner:
    """
    Service for automatically assigning visual moods to webtoon panels.

    Analyzes panel content and determines appropriate SceneMood settings
    to enhance the emotional impact of each scene.
    """

    def __init__(self, use_llm: bool = False, llm_client=None):
        """
        Initialize the Mood Designer.

        Args:
            use_llm: Whether to use LLM for mood assignment
            llm_client: Optional LLM client for LLM-based assignment
        """
        self._use_llm = use_llm
        self._llm_client = llm_client

    def assign_moods(
        self,
        panels: List[WebtoonPanel],
        story_context: str = ""
    ) -> List[MoodAssignment]:
        """
        Assign moods to a list of webtoon panels.

        This is the main entry point for mood assignment.

        Args:
            panels: List of WebtoonPanel objects to analyze
            story_context: Optional overall story context for better analysis

        Returns:
            List of MoodAssignment objects, one per panel
        """
        if self._use_llm and self._llm_client:
            return self._assign_moods_with_llm(panels, story_context)
        else:
            return self._assign_moods_rule_based(panels)

    def _assign_moods_rule_based(
        self,
        panels: List[WebtoonPanel]
    ) -> List[MoodAssignment]:
        """
        Assign moods using rule-based approach.

        Fast and deterministic, suitable for most use cases.
        """
        assignments = []
        previous_context = "neutral"

        for panel in panels:
            assignment = self._analyze_panel(panel, previous_context)
            assignments.append(assignment)
            previous_context = assignment.detected_context

        # Post-process for smooth transitions
        self._smooth_transitions(assignments)

        return assignments

    def _analyze_panel(
        self,
        panel: WebtoonPanel,
        previous_context: str = "neutral"
    ) -> MoodAssignment:
        """
        Analyze a single panel and assign mood.

        Args:
            panel: WebtoonPanel to analyze
            previous_context: Context from previous panel for continuity

        Returns:
            MoodAssignment for this panel
        """
        # Combine text sources for analysis
        dialogue_text = ""
        if panel.dialogue:
            for d in panel.dialogue:
                if isinstance(d, dict):
                    dialogue_text += " " + d.get("text", "")
                else:
                    dialogue_text += " " + str(d)

        combined_text = " ".join(filter(None, [
            panel.visual_prompt or "",
            dialogue_text,
            getattr(panel, "story_beat", "") or "",
        ]))

        # Detect context
        detected_context, confidence = detect_context_from_text(combined_text)

        # Get base emotional intensity
        base_intensity = getattr(panel, "emotional_intensity", 5)

        # Apply intensity modifier from text
        intensity_modifier = detect_intensity_modifier(combined_text)
        adjusted_intensity = max(1, min(10, base_intensity + intensity_modifier))

        # Get shot type mood bias
        shot_bias = get_shot_type_mood_bias(panel.shot_type or "")
        adjusted_intensity += shot_bias.get("intensity_boost", 0)
        adjusted_intensity = max(1, min(10, adjusted_intensity))

        # Get base mood from preset
        base_mood = get_mood_for_intensity(adjusted_intensity, detected_context)

        # Create customized mood based on analysis
        customized_mood = self._customize_mood(
            base_mood,
            adjusted_intensity,
            shot_bias,
            detected_context
        )

        # Generate reasoning
        reasoning = self._generate_reasoning(
            detected_context,
            adjusted_intensity,
            panel.shot_type or "unknown"
        )

        return MoodAssignment(
            panel_number=panel.panel_number,
            mood=customized_mood,
            detected_context=detected_context,
            confidence=confidence,
            reasoning=reasoning
        )

    def _customize_mood(
        self,
        base_mood: SceneMood,
        intensity: int,
        shot_bias: Dict[str, Any],
        context: str
    ) -> SceneMood:
        """
        Customize a mood based on additional analysis.

        Args:
            base_mood: Starting mood preset
            intensity: Adjusted emotional intensity
            shot_bias: Shot type mood biases
            context: Detected context

        Returns:
            Customized SceneMood
        """
        # Start with base mood values
        color_temp = base_mood.color_temperature
        saturation = base_mood.saturation
        lighting = base_mood.lighting_mood
        detail_level = shot_bias.get("detail_level", base_mood.detail_level)
        expression = shot_bias.get("expression_style", base_mood.expression_style)
        effects = list(base_mood.special_effects)

        # Adjust based on context if needed
        if context == "romantic" and intensity >= 7:
            if SpecialEffect.SPARKLES not in effects:
                effects.append(SpecialEffect.SPARKLES)

        elif context == "sad" and intensity >= 6:
            if SpecialEffect.VIGNETTE not in effects:
                effects.append(SpecialEffect.VIGNETTE)

        elif context == "flashback":
            if SpecialEffect.GRAIN not in effects:
                effects.append(SpecialEffect.GRAIN)
            if SpecialEffect.SOFT_FOCUS not in effects:
                effects.append(SpecialEffect.SOFT_FOCUS)

        # Limit effects to prevent overload
        effects = effects[:3]

        return SceneMood(
            name=f"{context}_{intensity}",
            color_temperature=color_temp,
            saturation=saturation,
            lighting_mood=lighting,
            detail_level=detail_level,
            expression_style=expression,
            special_effects=effects,
            intensity=intensity,
            accent_color=base_mood.accent_color
        )

    def _generate_reasoning(
        self,
        context: str,
        intensity: int,
        shot_type: str
    ) -> str:
        """Generate human-readable reasoning for mood assignment."""
        context_desc = {
            "neutral": "balanced, everyday scene",
            "romantic": "romantic or intimate moment",
            "conflict": "tense confrontation or argument",
            "sad": "emotional or melancholic scene",
            "comedy": "light-hearted or humorous moment",
            "action": "dynamic action sequence",
            "mystery": "mysterious or suspenseful scene",
            "peaceful": "calm and serene atmosphere",
            "tense": "anxious or suspenseful buildup",
            "flashback": "memory or past event",
        }

        intensity_desc = "moderate"
        if intensity >= 8:
            intensity_desc = "high"
        elif intensity <= 3:
            intensity_desc = "low"

        desc = context_desc.get(context, "general scene")

        return f"{intensity_desc.capitalize()} intensity {desc}. Shot type: {shot_type}."

    def _smooth_transitions(self, assignments: List[MoodAssignment]):
        """
        Post-process assignments for smoother mood transitions.

        Prevents jarring jumps between very different moods.
        """
        if len(assignments) < 2:
            return

        for i in range(1, len(assignments)):
            prev = assignments[i - 1]
            curr = assignments[i]

            # Check for jarring intensity jumps
            intensity_diff = abs(curr.mood.intensity - prev.mood.intensity)

            if intensity_diff > 4:
                # Smooth the transition
                avg_intensity = (curr.mood.intensity + prev.mood.intensity) // 2

                # Adjust current mood intensity slightly toward previous
                new_intensity = curr.mood.intensity
                if curr.mood.intensity > prev.mood.intensity:
                    new_intensity = min(10, prev.mood.intensity + 3)
                else:
                    new_intensity = max(1, prev.mood.intensity - 3)

                # Update the mood
                curr.mood = SceneMood(
                    name=curr.mood.name,
                    color_temperature=curr.mood.color_temperature,
                    saturation=curr.mood.saturation,
                    lighting_mood=curr.mood.lighting_mood,
                    detail_level=curr.mood.detail_level,
                    expression_style=curr.mood.expression_style,
                    special_effects=curr.mood.special_effects,
                    intensity=new_intensity,
                    accent_color=curr.mood.accent_color
                )

                curr.reasoning += f" (smoothed from {curr.mood.intensity} for transition)"

    def _assign_moods_with_llm(
        self,
        panels: List[WebtoonPanel],
        story_context: str = ""
    ) -> List[MoodAssignment]:
        """
        Assign moods using LLM for more nuanced analysis.
        """
        if not self._llm_client:
            logger.warning("LLM client not configured, falling back to rule-based")
            return self._assign_moods_rule_based(panels)

        # Format panels for LLM
        panels_json = []
        for panel in panels:
            dialogue_text = ""
            if panel.dialogue:
                dialogue_text = " ".join(
                    d.get("text", "") if isinstance(d, dict) else str(d)
                    for d in panel.dialogue
                )

            characters = ", ".join(panel.active_character_names) if panel.active_character_names else "none"

            panel_data = {
                "panel_number": panel.panel_number,
                "shot_type": panel.shot_type or "unknown",
                "visual_description": panel.visual_prompt or "",
                "dialogue": dialogue_text,
                "story_beat": getattr(panel, "story_beat", "") or "",
                "characters": characters,
            }
            panels_json.append(PANEL_CONTEXT_FORMAT.format(**panel_data))

        # Call LLM
        user_prompt = MOOD_DESIGNER_USER_PROMPT.format(
            story_context=story_context or "No additional context provided.",
            panels_json="\n".join(panels_json)
        )

        try:
            response = self._llm_client.generate(
                system_prompt=MOOD_DESIGNER_SYSTEM_PROMPT,
                user_prompt=user_prompt
            )

            # Parse response
            assignments = self._parse_llm_response(response, panels)
            return assignments

        except Exception as e:
            logger.error(f"LLM mood assignment failed: {e}, falling back to rule-based")
            return self._assign_moods_rule_based(panels)

    def _parse_llm_response(
        self,
        response: str,
        panels: List[WebtoonPanel]
    ) -> List[MoodAssignment]:
        """Parse LLM response into MoodAssignment objects."""
        assignments = []

        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                mood_data = json.loads(json_match.group())

                for item in mood_data:
                    panel_num = item.get("panel_number", 1)
                    mood_preset = item.get("mood_preset", "neutral")
                    adjustments = item.get("adjustments", {})
                    reasoning = item.get("reasoning", "")
                    detected = item.get("detected_emotion", "neutral")

                    # Get base preset
                    base_mood = get_mood_preset(mood_preset)

                    # Apply adjustments
                    mood = self._apply_llm_adjustments(base_mood, adjustments)

                    assignments.append(MoodAssignment(
                        panel_number=panel_num,
                        mood=mood,
                        detected_context=detected,
                        confidence=0.8,
                        reasoning=reasoning
                    ))

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response: {e}")

        # Fill in missing panels with rule-based assignments
        assigned_panels = {a.panel_number for a in assignments}
        for panel in panels:
            if panel.panel_number not in assigned_panels:
                assignment = self._analyze_panel(panel)
                assignments.append(assignment)

        # Sort by panel number
        assignments.sort(key=lambda a: a.panel_number)

        return assignments

    def _apply_llm_adjustments(
        self,
        base_mood: SceneMood,
        adjustments: Dict[str, Any]
    ) -> SceneMood:
        """Apply LLM-suggested adjustments to a mood."""
        # Parse adjustments
        try:
            color_temp = ColorTemperature(adjustments.get(
                "color_temperature",
                base_mood.color_temperature.value
            ))
        except ValueError:
            color_temp = base_mood.color_temperature

        try:
            saturation = SaturationLevel(adjustments.get(
                "saturation",
                base_mood.saturation.value
            ))
        except ValueError:
            saturation = base_mood.saturation

        try:
            lighting = LightingMood(adjustments.get(
                "lighting_mood",
                base_mood.lighting_mood.value
            ))
        except ValueError:
            lighting = base_mood.lighting_mood

        # Parse effects
        effects = []
        for effect_name in adjustments.get("special_effects", []):
            try:
                effects.append(SpecialEffect(effect_name))
            except ValueError:
                pass

        if not effects:
            effects = list(base_mood.special_effects)

        intensity = adjustments.get("intensity", base_mood.intensity)

        return SceneMood(
            name=base_mood.name,
            color_temperature=color_temp,
            saturation=saturation,
            lighting_mood=lighting,
            detail_level=base_mood.detail_level,
            expression_style=base_mood.expression_style,
            special_effects=effects[:3],
            intensity=max(1, min(10, intensity)),
            accent_color=base_mood.accent_color
        )


# ============================================================================
# Convenience Functions
# ============================================================================

def create_mood_designer(use_llm: bool = False, llm_client=None) -> MoodDesigner:
    """
    Factory function to create a Mood Designer.

    Args:
        use_llm: Whether to use LLM-based assignment
        llm_client: Optional LLM client instance

    Returns:
        MoodDesigner instance
    """
    return MoodDesigner(use_llm=use_llm, llm_client=llm_client)


def assign_moods_to_panels(panels: List[WebtoonPanel]) -> List[MoodAssignment]:
    """
    Convenience function to assign moods using rule-based approach.

    Args:
        panels: List of WebtoonPanel objects

    Returns:
        List of MoodAssignment objects
    """
    designer = MoodDesigner()
    return designer.assign_moods(panels)


def get_mood_for_panel(panel: WebtoonPanel) -> SceneMood:
    """
    Get the appropriate mood for a single panel.

    Args:
        panel: WebtoonPanel to analyze

    Returns:
        SceneMood for this panel
    """
    designer = MoodDesigner()
    assignments = designer.assign_moods([panel])
    return assignments[0].mood if assignments else MOOD_PRESETS["neutral"]


# ============================================================================
# Global Instance
# ============================================================================

# Default mood designer instance
mood_designer = MoodDesigner()
