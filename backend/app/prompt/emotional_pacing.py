# emotional_pacing.py
"""
Emotional Pacing Engine (v2.1.0 E1-T04 & E5-T02)

This module provides automatic shot type and style mode selection
based on dialogue sentiment and story beat analysis.

Key features:
- Sentiment-to-shot-type mapping ("I love you" → macro_eyes)
- Automatic style_mode detection based on scene content
- Emotional pacing rules for visual flow
"""

import re
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum


# ==============================================================================
# Sentiment Categories
# ==============================================================================

class SentimentCategory(str, Enum):
    """Categories of emotional sentiment in dialogue/story beats."""
    ROMANTIC_CONFESSION = "romantic_confession"  # "I love you", confessions
    ROMANTIC_TENSION = "romantic_tension"        # Heart racing, nervous, attracted
    INTIMATE_MOMENT = "intimate_moment"          # Touch, closeness, tenderness
    COMEDIC_REACTION = "comedic_reaction"        # Funny, embarrassed, shocked
    DRAMATIC_REVEAL = "dramatic_reveal"          # Truth revealed, secrets exposed
    EMOTIONAL_PAIN = "emotional_pain"            # Crying, heartbreak, goodbye
    ANGRY_CONFLICT = "angry_conflict"            # Arguments, confrontation
    INTERNAL_STRUGGLE = "internal_struggle"      # Inner conflict, doubt
    ACTION_INTENSE = "action_intense"            # Running, fighting, escaping
    PEACEFUL_CALM = "peaceful_calm"              # Quiet moments, contentment
    MYSTERIOUS_SUSPENSE = "mysterious_suspense"  # Secrets, investigation
    NEUTRAL = "neutral"                          # Default, no strong emotion


# ==============================================================================
# Keyword-Based Sentiment Detection (E1-T04)
# ==============================================================================

SENTIMENT_KEYWORDS = {
    SentimentCategory.ROMANTIC_CONFESSION: [
        "i love you", "i like you", "my feelings", "confession", "confess",
        "be with me", "go out with me", "be my girlfriend", "be my boyfriend",
        "marry me"
    ],
    SentimentCategory.ROMANTIC_TENSION: [
        "heart racing", "heartbeat", "nervous", "blushing", "blush",
        "can't look away", "beautiful", "handsome", "attractive", "stunning",
        "so close", "proximity"
    ],
    SentimentCategory.INTIMATE_MOMENT: [
        "touch", "hand", "embrace", "hug", "kiss", "hold", "caress",
        "whisper", "lean close", "fingers", "skin", "warm", "tender",
        "gentle", "soft touch"
    ],
    SentimentCategory.COMEDIC_REACTION: [
        "haha", "lol", "funny", "ridiculous", "embarrassing", "embarrassed",
        "shocked", "can't believe", "what the", "seriously", "silly",
        "awkward"
    ],
    SentimentCategory.DRAMATIC_REVEAL: [
        "truth is", "actually", "secret", "reveal", "shock", "can't be",
        "all along", "the reason", "i never told you", "find out",
        "reality"
    ],
    SentimentCategory.EMOTIONAL_PAIN: [
        "cry", "tears", "sob", "goodbye", "leave", "over", "end",
        "heartbreak", "hurt", "pain", "sorry", "never again", "lost",
        "alone"
    ],
    SentimentCategory.ANGRY_CONFLICT: [
        "angry", "hate", "shut up", "leave me alone", "fight", "argue",
        "how dare", "you liar", "betrayed", "furious", "rage"
    ],
    SentimentCategory.INTERNAL_STRUGGLE: [
        "don't know", "confused", "should i", "can't decide", "torn",
        "doubt", "maybe", "wondering", "what if", "scared to"
    ],
    SentimentCategory.ACTION_INTENSE: [
        "run", "chase", "escape", "hurry", "quick", "danger", "help",
        "fight", "attack", "dodge", "jump", "catch"
    ],
    SentimentCategory.PEACEFUL_CALM: [
        "peaceful", "calm", "quiet", "relax", "comfortable", "nice day",
        "enjoying", "content", "rest", "serene"
    ],
    SentimentCategory.MYSTERIOUS_SUSPENSE: [
        "strange", "suspicious", "who", "why", "what happened", "hidden",
        "investigate", "clue", "mystery", "secret"
    ],
}


# ==============================================================================
# Sentiment to Shot Type Mapping (E1-T04)
# ==============================================================================

SENTIMENT_TO_SHOT_TYPE = {
    SentimentCategory.ROMANTIC_CONFESSION: [
        "macro_eyes", "extreme_close_up", "close_up", "two_shot"
    ],
    SentimentCategory.ROMANTIC_TENSION: [
        "close_up", "macro_hands", "detail", "medium_close_up"
    ],
    SentimentCategory.INTIMATE_MOMENT: [
        "macro_hands", "macro_lips", "close_up", "silhouette"
    ],
    SentimentCategory.COMEDIC_REACTION: [
        "medium", "medium_close_up", "close_up"  # with comedy_chibi style
    ],
    SentimentCategory.DRAMATIC_REVEAL: [
        "extreme_close_up", "macro_eyes", "close_up", "dutch_angle"
    ],
    SentimentCategory.EMOTIONAL_PAIN: [
        "close_up", "silhouette", "extreme_wide", "macro_eyes"
    ],
    SentimentCategory.ANGRY_CONFLICT: [
        "close_up", "medium", "over_shoulder", "split_screen"
    ],
    SentimentCategory.INTERNAL_STRUGGLE: [
        "close_up", "medium_close_up"  # with dutch angle
    ],
    SentimentCategory.ACTION_INTENSE: [
        "wide", "medium_wide", "full_body"  # with action_dynamic style
    ],
    SentimentCategory.PEACEFUL_CALM: [
        "wide", "medium", "two_shot"
    ],
    SentimentCategory.MYSTERIOUS_SUSPENSE: [
        "detail", "close_up", "silhouette", "extreme_wide"
    ],
    SentimentCategory.NEUTRAL: [
        "medium", "medium_close_up", "medium_wide"
    ],
}


# ==============================================================================
# Sentiment to Style Mode Mapping (E5-T02)
# ==============================================================================

SENTIMENT_TO_STYLE_MODE = {
    SentimentCategory.ROMANTIC_CONFESSION: "romantic_detail",
    SentimentCategory.ROMANTIC_TENSION: "romantic_detail",
    SentimentCategory.INTIMATE_MOMENT: "romantic_detail",
    SentimentCategory.COMEDIC_REACTION: "comedy_chibi",
    SentimentCategory.DRAMATIC_REVEAL: "romantic_detail",
    SentimentCategory.EMOTIONAL_PAIN: "romantic_detail",
    SentimentCategory.ANGRY_CONFLICT: None,  # default style
    SentimentCategory.INTERNAL_STRUGGLE: "romantic_detail",
    SentimentCategory.ACTION_INTENSE: "action_dynamic",
    SentimentCategory.PEACEFUL_CALM: None,
    SentimentCategory.MYSTERIOUS_SUSPENSE: None,
    SentimentCategory.NEUTRAL: None,
}


# ==============================================================================
# Core Functions
# ==============================================================================

def detect_sentiment(
    dialogue_text: str = "",
    story_beat: str = "",
    visual_prompt: str = ""
) -> Tuple[SentimentCategory, float]:
    """
    Detect the primary sentiment category from text content.
    
    v2.1.0 E1-T04: Analyzes dialogue and story beats for emotional content.
    
    Args:
        dialogue_text: Combined dialogue from the panel
        story_beat: Story beat description
        visual_prompt: Visual prompt text
        
    Returns:
        Tuple of (SentimentCategory, confidence score 0.0-1.0)
    """
    combined_text = f"{dialogue_text} {story_beat} {visual_prompt}".lower()
    
    if not combined_text.strip():
        return SentimentCategory.NEUTRAL, 0.0
    
    # Score each sentiment category
    scores = {}
    for sentiment, keywords in SENTIMENT_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in combined_text:
                # Longer keywords get higher weight
                weight = 1 + (len(keyword.split()) - 1) * 0.5
                score += weight
        scores[sentiment] = score
    
    # Find the top sentiment
    if not scores:
        return SentimentCategory.NEUTRAL, 0.0
    
    max_sentiment = max(scores, key=scores.get)
    max_score = scores[max_sentiment]
    
    if max_score == 0:
        return SentimentCategory.NEUTRAL, 0.0
    
    # Normalize confidence (cap at 1.0)
    confidence = min(1.0, max_score / 5.0)
    
    return max_sentiment, confidence


def get_recommended_shot_types(sentiment: SentimentCategory) -> List[str]:
    """
    Get recommended shot types for a given sentiment.
    
    v2.1.0 E1-T04: Maps emotional sentiment to appropriate shot types.
    
    Args:
        sentiment: Detected sentiment category
        
    Returns:
        List of recommended shot type strings
    """
    return SENTIMENT_TO_SHOT_TYPE.get(sentiment, ["medium"])


def get_recommended_style_mode(
    sentiment: SentimentCategory,
    emotional_intensity: int = 5
) -> Optional[str]:
    """
    Get recommended style_mode for a given sentiment.
    
    v2.1.0 E5-T02: Auto-detects appropriate style mode.
    
    Args:
        sentiment: Detected sentiment category
        emotional_intensity: Intensity level (1-10)
        
    Returns:
        Style mode string or None for default
    """
    # Only apply non-default styles for moderate+ intensity
    if emotional_intensity < 4:
        return None
    
    return SENTIMENT_TO_STYLE_MODE.get(sentiment)


def analyze_panel_for_pacing(
    dialogue_list: List[Dict[str, Any]] = None,
    story_beat: str = "",
    visual_prompt: str = "",
    emotional_intensity: int = 5
) -> Dict[str, Any]:
    """
    Analyze a panel and return pacing recommendations.
    
    v2.1.0 E1-T04 & E5-T02: Combined analysis for shot and style selection.
    
    Args:
        dialogue_list: List of dialogue dicts
        story_beat: Story beat text
        visual_prompt: Visual prompt text
        emotional_intensity: Predefined intensity (1-10)
        
    Returns:
        Dict with sentiment, shot_types, style_mode, and pacing_notes
    """
    # Combine dialogue text
    dialogue_text = ""
    if dialogue_list:
        dialogue_text = " ".join(d.get("text", "") for d in dialogue_list)
    
    # Detect sentiment
    sentiment, confidence = detect_sentiment(dialogue_text, story_beat, visual_prompt)
    
    # Get recommendations
    shot_types = get_recommended_shot_types(sentiment)
    style_mode = get_recommended_style_mode(sentiment, emotional_intensity)
    
    # Generate pacing notes
    pacing_notes = _generate_pacing_notes(sentiment, emotional_intensity, confidence)
    
    return {
        "sentiment": sentiment.value,
        "confidence": round(confidence, 2),
        "recommended_shot_types": shot_types,
        "recommended_style_mode": style_mode,
        "emotional_intensity": emotional_intensity,
        "pacing_notes": pacing_notes,
    }


def _generate_pacing_notes(
    sentiment: SentimentCategory,
    intensity: int,
    confidence: float
) -> str:
    """Generate human-readable pacing notes."""
    notes = []
    
    if sentiment == SentimentCategory.ROMANTIC_CONFESSION and intensity >= 7:
        notes.append("CRITICAL: Use macro_eyes or extreme_close_up for confession.")
    elif sentiment == SentimentCategory.INTIMATE_MOMENT:
        notes.append("Consider macro_hands for physical contact moments.")
    elif sentiment == SentimentCategory.COMEDIC_REACTION:
        notes.append("Consider comedy_chibi style for humor impact.")
    elif sentiment == SentimentCategory.DRAMATIC_REVEAL and intensity >= 8:
        notes.append("Use extreme_close_up with dutch_angle for dramatic effect.")
    elif sentiment == SentimentCategory.EMOTIONAL_PAIN:
        notes.append("Silhouette or extreme_wide can emphasize isolation.")
    
    if confidence < 0.3:
        notes.append("Low confidence - consider manual review.")
    
    return " ".join(notes) if notes else "Standard pacing applies."


# ==============================================================================
# Batch Processing for Workflow Integration
# ==============================================================================

def analyze_panels_batch(panels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze multiple panels and return enhanced data with pacing info.
    
    v2.1.0: Designed for workflow integration.
    
    Args:
        panels: List of panel dicts
        
    Returns:
        Panels with added pacing_analysis field
    """
    analyzed = []
    
    for panel in panels:
        dialogue_list = panel.get("dialogue", [])
        story_beat = panel.get("story_beat", "")
        visual_prompt = panel.get("visual_prompt", "")
        intensity = panel.get("emotional_intensity", 5)
        
        pacing_analysis = analyze_panel_for_pacing(
            dialogue_list=dialogue_list,
            story_beat=story_beat,
            visual_prompt=visual_prompt,
            emotional_intensity=intensity
        )
        
        # Add analysis to panel
        enhanced_panel = {
            **panel,
            "pacing_analysis": pacing_analysis
        }
        
        # Auto-populate style_mode if not set
        if not panel.get("style_mode") and pacing_analysis["recommended_style_mode"]:
            enhanced_panel["style_mode"] = pacing_analysis["recommended_style_mode"]
        
        analyzed.append(enhanced_panel)
    
    return analyzed


# ==============================================================================
# Specific Detection Functions
# ==============================================================================

def is_confession_moment(text: str) -> bool:
    """Check if text contains a confession/love declaration."""
    text_lower = text.lower()
    confession_patterns = [
        r"i love you",
        r"i'?m in love with",
        r"i like you",
        r"my feelings for you",
        r"be my (girlfriend|boyfriend)",
        r"go out with me",
    ]
    return any(re.search(p, text_lower) for p in confession_patterns)


def is_kiss_scene(text: str) -> bool:
    """Check if text describes a kiss scene."""
    text_lower = text.lower()
    kiss_patterns = [
        r"\bkiss\b",
        r"lips (touch|meet|press)",
        r"kissed",
    ]
    return any(re.search(p, text_lower) for p in kiss_patterns)


def is_hand_contact(text: str) -> bool:
    """Check if text describes hand contact."""
    text_lower = text.lower()
    hand_patterns = [
        r"hold.{0,10}hand",
        r"hand.{0,10}touch",
        r"fingers.{0,10}(intertwine|touch|brush)",
        r"grab.{0,10}hand",
    ]
    return any(re.search(p, text_lower) for p in hand_patterns)


def get_mandatory_shot_for_moment(story_beat: str, dialogue_text: str) -> Optional[str]:
    """
    Get mandatory shot type for critical emotional moments.
    
    v2.1.0 E1-T04: Enforces shot type for key moments.
    
    Returns shot type string or None if no mandatory shot.
    """
    combined = f"{story_beat} {dialogue_text}"
    
    if is_confession_moment(combined):
        return "macro_eyes"  # MANDATORY for confession
    
    if is_kiss_scene(combined):
        return "macro_lips"  # MANDATORY for kiss
    
    if is_hand_contact(combined):
        return "macro_hands"  # MANDATORY for hand contact
    
    return None
