"""
Dialogue formatting utilities for image generation prompts.

Provides utilities to convert dialogue into visual/emotional context
for image generation WITHOUT rendering text or speech bubbles.

The key insight: Dialogue can inform character expressions and body language
without being rendered as text in the image.
"""

from typing import List, Dict, Any, Tuple
import re


# Emotion detection keywords and their visual descriptions
EMOTION_VISUAL_MAP = {
    # Anger/Frustration
    "angry": "furious expression, furrowed brows, clenched jaw",
    "mad": "angry expression, narrowed eyes, tense facial muscles",
    "furious": "rage-filled expression, teeth showing, intense glare",
    "what did you": "shocked and confrontational expression, eyes wide with disbelief",
    "how dare": "indignant expression, raised eyebrows, stern gaze",
    "stop": "urgent expression, hand raised defensively",
    "shut up": "frustrated expression, eyes squeezed shut, tense posture",

    # Sadness/Vulnerability
    "sad": "melancholic expression, downcast eyes, slight frown",
    "cry": "tearful expression, glistening eyes, quivering lips",
    "miss you": "longing expression, wistful gaze, soft sadness in eyes",
    "sorry": "apologetic expression, lowered gaze, remorseful look",
    "forgive": "pleading expression, hopeful yet pained eyes",
    "hurt": "pained expression, emotional vulnerability showing",
    "goodbye": "bittersweet expression, mix of sadness and acceptance",
    "leave": "distressed expression, eyes showing pain of separation",

    # Love/Affection
    "love you": "tender expression, soft eyes, gentle smile",
    "i love": "vulnerable loving expression, eyes full of emotion",
    "marry": "overwhelmed with joy, tears of happiness, radiant smile",
    "beautiful": "admiring gaze, soft warm expression",
    "kiss": "intimate expression, eyes half-closed, leaning forward",
    "hold": "seeking comfort expression, reaching out gesture",
    "together": "hopeful expression, warmth in eyes",

    # Surprise/Shock
    "what": "surprised expression, raised eyebrows, mouth slightly open",
    "really": "disbelief expression, eyes wide, leaning back slightly",
    "impossible": "stunned expression, frozen posture, wide eyes",
    "can't believe": "incredulous expression, jaw dropped slightly",
    "oh my": "astonished expression, hand near mouth",
    "no way": "shocked disbelief, stepping back gesture",

    # Fear/Anxiety
    "scared": "fearful expression, trembling, defensive posture",
    "afraid": "anxious expression, worried eyes, tense body",
    "help": "desperate expression, reaching out, panicked eyes",
    "run": "alarmed expression, body tensed for flight",
    "danger": "alert expression, widened eyes, protective stance",

    # Joy/Happiness
    "happy": "joyful expression, bright smile, sparkling eyes",
    "laugh": "amused expression, genuine smile, crinkled eyes",
    "excited": "enthusiastic expression, animated posture, bright eyes",
    "thank": "grateful expression, warm smile, appreciative gaze",
    "amazing": "awestruck expression, eyes wide with wonder",
    "yes": "elated expression, triumphant posture",

    # Confusion/Uncertainty
    "confused": "puzzled expression, tilted head, furrowed brow",
    "don't understand": "bewildered expression, questioning gaze",
    "why": "questioning expression, searching eyes",
    "how": "curious expression, inquisitive tilt of head",

    # Determination/Resolve
    "will": "determined expression, set jaw, focused eyes",
    "promise": "earnest expression, sincere gaze, hand on heart gesture",
    "never": "resolute expression, unwavering gaze",
    "protect": "protective stance, fierce determination in eyes",
    "fight": "combative expression, ready stance, intense focus",

    # Awkwardness/Embarrassment
    "embarrass": "flustered expression, slight blush, avoiding eye contact",
    "awkward": "uncomfortable expression, shifting posture",
    "blush": "embarrassed expression, reddened cheeks, shy smile",
    "nervous": "anxious expression, fidgeting, uncertain gaze",

    # Silence/Contemplation
    "...": "contemplative expression, thoughtful silence, introspective gaze",
    "silence": "pensive expression, quiet intensity, unspoken emotion",
}


def detect_emotion_from_dialogue(text: str) -> Tuple[str, str]:
    """
    Detect the primary emotion from dialogue text.

    Args:
        text: Dialogue text to analyze

    Returns:
        Tuple of (emotion_key, visual_description)
    """
    text_lower = text.lower()

    # Check each emotion keyword
    for keyword, visual_desc in EMOTION_VISUAL_MAP.items():
        if keyword in text_lower:
            return keyword, visual_desc

    # Default to neutral if no emotion detected
    return "neutral", "neutral expression, natural posture"


def format_dialogue_as_visual_context(
    dialogue_list: List[Dict[str, Any]],
    max_lines: int = 4
) -> str:
    """
    Convert dialogue into visual/emotional context for image generation.

    This function analyzes dialogue to extract emotional content and converts
    it into visual descriptions that guide character expressions and body
    language WITHOUT rendering any text or speech bubbles in the image.

    Args:
        dialogue_list: List of dialogue dicts with 'character' and 'text' keys
        max_lines: Maximum dialogue lines to analyze (default 4)

    Returns:
        Visual context description for character expressions

    Example:
        Input: [{"character": "Mina", "text": "What did you say?!"}]
        Output: "Mina: shocked and confrontational expression, eyes wide with disbelief"
    """
    if not dialogue_list:
        return ""

    # Sort by order if available
    sorted_dialogue = sorted(
        dialogue_list,
        key=lambda d: d.get("order", 0)
    )

    visual_contexts = []

    for d in sorted_dialogue[:max_lines]:
        if isinstance(d, dict):
            speaker = d.get("character", "Character")
            text = d.get("text", "")

            # Skip if internal monologue marker (shouldn't show externally)
            if "(internal)" in speaker.lower() or "(thinking)" in speaker.lower():
                # For internal thoughts, show contemplative expression
                clean_speaker = speaker.replace("(internal)", "").replace("(thinking)", "").strip()
                visual_contexts.append(
                    f"{clean_speaker}: introspective expression, deep in thought, subtle emotion showing through eyes"
                )
                continue

            if text.strip():
                # Detect emotion and get visual description
                _, visual_desc = detect_emotion_from_dialogue(text)
                visual_contexts.append(f"{speaker}: {visual_desc}")

    if not visual_contexts:
        return ""

    # Format as character expression guide
    result = "CHARACTER EXPRESSIONS (based on scene context):\n"
    result += "\n".join(f"- {ctx}" for ctx in visual_contexts)

    return result


def get_dominant_scene_emotion(dialogue_list: List[Dict[str, Any]]) -> str:
    """
    Determine the dominant emotional tone of a scene from its dialogue.

    Args:
        dialogue_list: List of dialogue dicts

    Returns:
        Dominant emotion descriptor for the scene
    """
    if not dialogue_list:
        return "neutral atmosphere"

    emotion_scores = {
        "romantic": 0,
        "tense": 0,
        "joyful": 0,
        "sad": 0,
        "dramatic": 0,
    }

    romantic_words = ["love", "kiss", "heart", "beautiful", "marry", "together", "hold"]
    tense_words = ["what", "how dare", "stop", "angry", "mad", "fight", "never"]
    joyful_words = ["happy", "laugh", "excited", "amazing", "yes", "thank"]
    sad_words = ["sad", "cry", "sorry", "miss", "goodbye", "hurt", "leave"]
    dramatic_words = ["impossible", "can't believe", "reveal", "truth", "secret", "promise"]

    for d in dialogue_list:
        if isinstance(d, dict):
            text = d.get("text", "").lower()

            for word in romantic_words:
                if word in text:
                    emotion_scores["romantic"] += 1
            for word in tense_words:
                if word in text:
                    emotion_scores["tense"] += 1
            for word in joyful_words:
                if word in text:
                    emotion_scores["joyful"] += 1
            for word in sad_words:
                if word in text:
                    emotion_scores["sad"] += 1
            for word in dramatic_words:
                if word in text:
                    emotion_scores["dramatic"] += 1

    # Find dominant emotion
    max_emotion = max(emotion_scores, key=emotion_scores.get)
    max_score = emotion_scores[max_emotion]

    if max_score == 0:
        return "neutral conversational atmosphere"

    emotion_atmosphere = {
        "romantic": "intimate romantic atmosphere, soft emotional tension",
        "tense": "confrontational atmosphere, emotional tension visible",
        "joyful": "lighthearted cheerful atmosphere, warm energy",
        "sad": "melancholic atmosphere, emotional weight in the air",
        "dramatic": "dramatic atmosphere, pivotal moment energy",
    }

    return emotion_atmosphere.get(max_emotion, "neutral atmosphere")


# Legacy function - kept for backwards compatibility but marked as deprecated
def format_dialogue_for_image_prompt(
    dialogue_list: List[Dict[str, Any]],
    max_lines: int = 6
) -> str:
    """
    DEPRECATED: This function was used to format dialogue for rendering in images.

    Use format_dialogue_as_visual_context() instead, which converts dialogue
    into visual/emotional descriptions WITHOUT rendering text bubbles.

    This function is kept for backwards compatibility but should not be used
    for new code.
    """
    # Return empty to prevent any dialogue from being rendered
    return ""
