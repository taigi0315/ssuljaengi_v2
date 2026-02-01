# Multi-Panel Generation Guide

This guide explains how to use the multi-panel webtoon generation system in Gossiptoon V2.

## Overview

The multi-panel system allows generating multiple webtoon panels in a single image, creating cohesive vertical webtoon pages with consistent character appearance and style.

## Architecture

### Core Module: `app/prompt/multi_panel.py`

This is the **primary module** for multi-panel functionality. It provides:

- **Structured prompt templates** for 2-5 panel pages
- **Panel data models** for type-safe panel definitions
- **Character reference handling** for consistent appearance
- **Style integration** with mood and visual systems

### Service Layer: `app/services/multi_panel_generator.py`

The service layer handles:

- **API integration** with Gemini image generation
- **Prompt formatting** using the core module
- **Image caching** and file management
- **Error handling** and retry logic

## Key Components

### 1. Panel Data Structure

```python
@dataclass
class PanelData:
    panel_number: int           # Panel position (1-5)
    shot_type: str             # "Close-up", "Medium shot", etc.
    subject: str               # Main subject/character
    description: str           # Scene description
    characters: List[str]      # Character names
    emotional_intensity: int   # 1-10 scale
    mood_context: str         # "romantic", "tense", etc.
```

### 2. Prompt Templates

#### Basic Multi-Panel Template
```python
MULTI_PANEL_TEMPLATE = """A vertical webtoon-style comic page with a 9:16 aspect ratio,
featuring {panel_count} distinct horizontal panels stacked vertically.
The art style is {style_description}.

{panel_descriptions}

CRITICAL - NO TEXT OR SPEECH BUBBLES:
- DO NOT render any text, words, letters, or characters
- Show character emotions through FACIAL EXPRESSIONS and BODY LANGUAGE only
- The dialogue will be added as an overlay AFTER image generation
"""
```

#### Character Reference Template
```python
MULTI_PANEL_WITH_REFERENCES_TEMPLATE = """A vertical webtoon-style comic page...
CHARACTER REFERENCES (maintain exact appearance in all panels):
{character_references}

{panel_descriptions}
"""
```

## Usage Examples

### 1. Basic Multi-Panel Generation

```python
from app.prompt.multi_panel import format_multi_panel_prompt, PanelData

# Define panels
panels = [
    PanelData(
        panel_number=1,
        shot_type="Wide shot",
        subject="Min-ji and Ji-hoon",
        description="Two students walking through school hallway",
        characters=["Min-ji", "Ji-hoon"],
        emotional_intensity=3,
        mood_context="casual"
    ),
    PanelData(
        panel_number=2,
        shot_type="Close-up",
        subject="Min-ji",
        description="Min-ji looking surprised and blushing",
        characters=["Min-ji"],
        emotional_intensity=7,
        mood_context="romantic_tension"
    )
]

# Generate prompt
prompt = format_multi_panel_prompt(
    panels=panels,
    style_description="Soft romantic manhwa style with warm lighting",
    style_keywords="High resolution, clean line art, professional webtoon quality"
)
```

### 2. Using WebtoonPanel Objects

```python
from app.prompt.multi_panel import format_panels_from_webtoon_panels

# Convert WebtoonPanel objects to multi-panel prompt
prompt = format_panels_from_webtoon_panels(
    webtoon_panels=webtoon_script.panels[:3],  # First 3 panels
    style_description="Modern Korean romance webtoon style",
    character_references={
        "Min-ji": "Young woman with long black hair, school uniform",
        "Ji-hoon": "Tall young man with brown hair, casual clothes"
    }
)
```

### 3. Service Layer Usage

```python
from app.services.multi_panel_generator import multi_panel_generator

# Generate multi-panel image
image_url = await multi_panel_generator.generate_multi_panel_page(
    panels=webtoon_panels,
    style_description="Bright youthful webtoon style",
    style_modifiers="Vibrant colors, dynamic composition",
    character_images={"Min-ji": "path/to/reference.jpg"}
)
```

## API Integration

### REST Endpoint

The multi-panel system is integrated into the webtoon API:

```http
POST /api/v1/webtoon/{workflow_id}/multi-panel
Content-Type: application/json

{
  "page_number": 1,
  "panel_indices": [0, 1, 2],
  "style_description": "Soft romantic manhwa style",
  "character_references": {
    "Min-ji": "Young woman with long black hair"
  }
}
```

### Response Format

```json
{
  "image_url": "/cache/images/multi_panel_3p_abc123.jpg",
  "panel_count": 3,
  "generation_time_ms": 2500,
  "style_applied": "Soft romantic manhwa style",
  "cache_hit": false
}
```

## Configuration Options

### Panel Count Recommendations

```python
def get_recommended_panel_count(panel_type: str) -> int:
    recommendations = {
        "dialogue_heavy": 2,      # Focus on conversation
        "action_sequence": 4,     # Show movement progression
        "emotional_moment": 3,    # Build emotional impact
        "scene_transition": 5,    # Smooth location changes
        "character_introduction": 2  # Focus on character details
    }
    return recommendations.get(panel_type, 3)
```

### Style Integration

The system integrates with the mood and style systems:

```python
# Mood-based style modifiers
mood_styles = {
    "romantic_tension": "Soft lighting, warm colors, intimate framing",
    "dramatic_conflict": "High contrast, dynamic angles, intense expressions",
    "peaceful_moment": "Gentle lighting, pastel colors, serene composition"
}
```

## Best Practices

### 1. Panel Composition

- **Vary shot types**: Mix wide shots, medium shots, and close-ups
- **Emotional progression**: Build intensity through panel sequence
- **Visual flow**: Guide reader's eye from panel to panel
- **Character consistency**: Maintain appearance across panels

### 2. Prompt Engineering

- **Specific descriptions**: Detailed scene and character descriptions
- **Emotional context**: Include mood and emotional intensity
- **Style consistency**: Use consistent style keywords
- **Character references**: Provide reference descriptions for consistency

### 3. Performance Optimization

- **Batch generation**: Generate multiple pages in sequence
- **Cache utilization**: Reuse similar panel combinations
- **Resource management**: Monitor memory usage for large batches
- **Error handling**: Implement retry logic for failed generations

## Troubleshooting

### Common Issues

#### Inconsistent Character Appearance
**Problem**: Characters look different across panels
**Solution**: 
- Use character reference descriptions
- Include specific physical details in prompts
- Maintain consistent style keywords

#### Poor Panel Separation
**Problem**: Panels blend together without clear borders
**Solution**:
- Ensure "thin black panel borders" in prompt
- Verify 9:16 aspect ratio specification
- Check panel count matches description

#### Low Image Quality
**Problem**: Generated images are blurry or low resolution
**Solution**:
- Include "High resolution, clean line art" in style keywords
- Verify Gemini model settings
- Check image generation parameters

### Debug Commands

```python
# Validate panel prompt
from app.prompt.multi_panel import validate_panel_prompt

validation_result = validate_panel_prompt(prompt)
if not validation_result["is_valid"]:
    print(f"Issues found: {validation_result['issues']}")

# Test panel data
panel = PanelData(...)
prompt_line = panel.to_prompt_line(include_mood=True)
print(f"Generated line: {prompt_line}")
```

### Logging

Enable detailed logging for debugging:

```python
import logging
logging.getLogger("app.services.multi_panel_generator").setLevel(logging.DEBUG)
```

## Advanced Features

### 1. Dynamic Panel Layouts

```python
# Adaptive panel count based on content
def determine_optimal_panels(webtoon_panels: List[WebtoonPanel]) -> int:
    dialogue_heavy = sum(1 for p in webtoon_panels if len(p.dialogue) > 50)
    action_heavy = sum(1 for p in webtoon_panels if "action" in p.shot_type.lower())
    
    if dialogue_heavy > action_heavy:
        return min(3, len(webtoon_panels))  # Fewer panels for dialogue
    else:
        return min(4, len(webtoon_panels))  # More panels for action
```

### 2. Style Inheritance

```python
# Inherit style from previous panels
def inherit_style_context(previous_panels: List[PanelData], new_panel: PanelData):
    # Maintain mood consistency
    if previous_panels:
        dominant_mood = max(set(p.mood_context for p in previous_panels), 
                          key=lambda x: sum(1 for p in previous_panels if p.mood_context == x))
        new_panel.mood_context = dominant_mood
```

### 3. Quality Validation

```python
# Validate generated panels
def validate_panel_quality(image_path: str, expected_panels: int) -> Dict[str, Any]:
    # Use computer vision to detect panel boundaries
    # Verify panel count matches expectation
    # Check image quality metrics
    pass
```

## Related Documentation

- [Workflow Architecture](WORKFLOW_ARCHITECTURE.md)
- [Image Generation Guide](IMAGE_GENERATION.md)
- [Style System Documentation](STYLE_SYSTEM.md)
- [API Reference](../README.md#api-endpoints)