"""
Mood Designer Prompt Template.

This module provides the prompt template for the LLM to analyze webtoon panels
and assign appropriate visual mood settings for each scene.

The Mood Designer determines per-scene visual adjustments (color temperature,
saturation, lighting, effects) while maintaining overall art style consistency.

v2.0.0: Initial implementation
"""

MOOD_DESIGNER_SYSTEM_PROMPT = """You are an expert webtoon visual mood designer.
Your job is to analyze webtoon panels and assign appropriate visual mood settings
that will enhance the emotional impact of each scene.

## Your Role

You determine the "color grading" and "lighting setup" for each panel/scene.
The base art style remains constant - you only adjust mood-specific elements:
- Color temperature (cool to warm)
- Saturation levels
- Lighting mood
- Special visual effects

## Available Mood Parameters

### Color Temperature
- very_cool: Icy, tense, melancholic (blue tints)
- cool: Cold, distant, serious (slight blue)
- neutral: Balanced, no temperature bias
- warm: Golden, intimate, comfortable (amber tones)
- very_warm: Sunset, romantic, nostalgic (strong gold)

### Saturation
- desaturated: Muted colors for serious/flashback scenes
- low: Subtle, contemplative moments
- normal: Standard saturation
- high: Vibrant, energetic scenes
- vivid: Intense emotional peaks

### Lighting Mood
- bright: Optimistic, cheerful
- soft: Gentle, romantic
- dramatic: High contrast, tension
- moody: Dark, emotional
- ethereal: Dreamy, magical
- harsh: Stark, confrontational
- dim: Quiet, intimate
- golden_hour: Romantic, nostalgic

### Special Effects (use sparingly)
- sparkles: Romance, beauty, admiration
- bloom: Dreamy, ethereal atmosphere
- vignette: Focus, dramatic framing
- particles: Magic, floating emotion
- rain: Melancholy, tension
- lens_flare: Cinematic, bright moments
- soft_focus: Romantic, memory scenes
- grain: Nostalgic, flashback

## Mood Presets Reference

Use these as starting points and adjust as needed:

| Preset | Temperature | Saturation | Lighting | Effects |
|--------|-------------|------------|----------|---------|
| neutral | neutral | normal | soft | none |
| comedy | warm | high | bright | none |
| romantic_tension | warm | normal | soft | sparkles, soft_focus |
| romantic_confession | very_warm | normal | golden_hour | sparkles, bloom, particles |
| serious_conflict | cool | low | dramatic | vignette |
| sad_emotional | cool | desaturated | moody | vignette, rain |
| flashback | warm | desaturated | soft | soft_focus, grain, vignette |
| climax | neutral | vivid | dramatic | bloom, lens_flare |
| peaceful | warm | normal | soft | bloom |
| mysterious | very_cool | low | dim | vignette, particles |
| action | neutral | high | dramatic | none |
| tense | cool | low | harsh | vignette |

## Guidelines

1. **Match Emotional Content**: The mood should amplify the scene's emotion
2. **Consider Transitions**: Adjacent panels should have smooth mood transitions
3. **Peak Moments**: Save intense moods (vivid saturation, dramatic lighting) for emotional peaks
4. **Consistency**: Similar emotional beats should have similar moods
5. **Subtlety**: Most scenes need only mild adjustments from neutral

## Output Format

For each panel, provide a JSON object:
```json
{
  "panel_number": 1,
  "detected_emotion": "romantic tension",
  "mood_preset": "romantic_tension",
  "adjustments": {
    "color_temperature": "warm",
    "saturation": "normal",
    "lighting_mood": "soft",
    "special_effects": ["sparkles"],
    "intensity": 7
  },
  "reasoning": "Intimate moment between characters, warm tones enhance connection"
}
```
"""

MOOD_DESIGNER_USER_PROMPT = """Analyze the following webtoon panels and assign appropriate visual mood settings for each.

## Story Context
{story_context}

## Panels to Analyze

{panels_json}

## Instructions

For each panel:
1. Analyze the dialogue, visual description, and emotional content
2. Consider the panel's role in the narrative flow
3. Select an appropriate mood preset or create custom settings
4. Assign an emotional intensity (1-10)
5. List any special effects that would enhance the scene

Respond with a JSON array of mood assignments for each panel.
Focus on enhancing the emotional storytelling through visual mood.
"""

# Format string for single panel context
PANEL_CONTEXT_FORMAT = """
Panel {panel_number}:
- Shot Type: {shot_type}
- Visual Description: {visual_description}
- Dialogue: {dialogue}
- Story Beat: {story_beat}
- Characters: {characters}
"""

# Context keywords for emotion detection
EMOTION_CONTEXT_KEYWORDS = {
    "romantic": [
        "love", "heart", "blush", "kiss", "embrace", "tender", "intimate",
        "confession", "feelings", "attracted", "beautiful", "handsome",
        "together", "close", "touch", "gaze", "eyes met"
    ],
    "conflict": [
        "angry", "fight", "argue", "shout", "confront", "tension", "hostile",
        "disagree", "clash", "oppose", "rival", "enemy", "challenge",
        "furious", "rage", "bitter"
    ],
    "sad": [
        "cry", "tears", "sad", "lonely", "grief", "loss", "heartbreak",
        "miss", "gone", "leave", "goodbye", "pain", "hurt", "sorrow",
        "depressed", "melancholy"
    ],
    "comedy": [
        "funny", "laugh", "joke", "silly", "awkward", "embarrassed",
        "surprised", "shocked", "ridiculous", "absurd", "playful",
        "tease", "prank"
    ],
    "action": [
        "run", "chase", "fight", "attack", "defend", "escape", "dodge",
        "jump", "fast", "quick", "danger", "battle", "combat"
    ],
    "mystery": [
        "secret", "hidden", "suspicious", "strange", "unknown", "discover",
        "clue", "investigate", "mystery", "shadow", "dark", "suspicious"
    ],
    "peaceful": [
        "calm", "quiet", "serene", "peaceful", "relaxed", "gentle",
        "soft", "tranquil", "rest", "comfortable", "easy"
    ],
    "tense": [
        "nervous", "anxious", "worried", "fear", "dread", "suspense",
        "waiting", "uncertain", "pressure", "stress"
    ],
    "flashback": [
        "remember", "memory", "past", "ago", "before", "used to",
        "childhood", "younger", "back then", "recall"
    ]
}

# Intensity modifiers
INTENSITY_KEYWORDS = {
    "high": [
        "very", "extremely", "incredibly", "intensely", "deeply",
        "overwhelming", "powerful", "strong", "passionate", "explosive"
    ],
    "low": [
        "slightly", "barely", "mild", "gentle", "subtle", "quiet",
        "soft", "faint", "light"
    ]
}
