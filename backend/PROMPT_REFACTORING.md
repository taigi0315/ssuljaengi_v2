# Prompt Refactoring - Summary

## Date: January 15, 2026

## Overview

Refactored all prompts from inline code to centralized prompt files in `backend/app/prompt/` directory. This improves maintainability, makes prompts easier to edit, and separates concerns between prompt engineering and code logic.

## Changes Made

### 1. Prompt Directory Structure

```
backend/app/prompt/
├── story_writer.py      # Base prompt for story generation
├── story_mood.py        # Mood-specific style modifiers
└── story_rewriter.py    # Prompt for story improvement (NEW)
```

### 2. Created Files

#### `backend/app/prompt/story_writer.py`
- Exported `STORY_WRITER_PROMPT` constant
- Contains the master prompt for webtoon story generation
- Focuses on visual-ready narratives for AI image generation
- Includes:
  - Role definition (Viral Webtoon Story Architect)
  - Visual-Ready Rule (15% focus)
  - Universal Structure (Hook → Climb → Peak → Hard Stop)
  - Writing Style guidelines
  - Output format specification

#### `backend/app/prompt/story_mood.py`
- Exported `MOOD_MODIFIERS` dictionary
- Contains 5 mood-specific style modifiers:
  1. **rofan** - Romance Fantasy (European Aristocracy)
  2. **modern_romance** - K-Drama style urban romance
  3. **slice_of_life** - Healing/cozy stories
  4. **revenge** - Revenge & Glow-up (Cider)
  5. **high_teen** - Academy/school drama
- Each modifier includes:
  - Genre rules
  - Setting translation
  - Character translation
  - Visual aesthetic keywords
  - Tone guidelines

#### `backend/app/prompt/story_rewriter.py` (NEW)
- Exported `REWRITER_PROMPT` constant
- Contains prompt for improving stories based on feedback
- Includes:
  - Role definition (Webtoon Story Editor)
  - Improvement rules
  - Visual consistency guidelines
  - Structure preservation instructions

### 3. Updated Services

#### `backend/app/services/story_writer.py`
**Before:**
- Mood modifiers hardcoded in the file
- Simple template string for prompt

**After:**
- Imports `STORY_WRITER_PROMPT` from `app.prompt.story_writer`
- Imports `MOOD_MODIFIERS` from `app.prompt.story_mood`
- `_get_prompt_template()` method now:
  - Combines base prompt with mood modifier
  - Inserts mood modifier after "THE VISUAL-READY RULE"
  - Replaces `{{story_seed}}` placeholder with actual input variables
- Cleaner separation of concerns

#### `backend/app/services/story_rewriter.py`
**Before:**
- Prompt hardcoded as inline template string
- Simple placeholder prompt

**After:**
- Imports `REWRITER_PROMPT` from `app.prompt.story_rewriter`
- Uses centralized prompt constant
- More detailed and structured prompt

### 4. Prompt Assembly Logic

The story writer now assembles prompts dynamically:

```python
def _get_prompt_template(self, mood: str) -> ChatPromptTemplate:
    """Get mood-specific prompt template."""
    mood_modifier = MOOD_MODIFIERS.get(mood, MOOD_MODIFIERS["modern_romance"])
    
    # Combine base prompt with mood modifier
    base_prompt = STORY_WRITER_PROMPT
    
    # Insert mood modifier after THE VISUAL-READY RULE
    insertion_marker = "**THE UNIVERSAL STRUCTURE:**"
    if insertion_marker in base_prompt:
        parts = base_prompt.split(insertion_marker)
        combined_prompt = f"{parts[0]}\n{mood_modifier}\n\n{insertion_marker}{parts[1]}"
    else:
        # Fallback: append mood modifier before output section
        combined_prompt = base_prompt.replace("**OUTPUT:**", f"{mood_modifier}\n\n**OUTPUT:**")
    
    # Replace placeholder with actual input variables
    combined_prompt = combined_prompt.replace(
        "**INPUT:** {{story_seed}}",
        """**INPUT (Reddit Post):**
Title: {title}
Content: {content}"""
    )
    
    return ChatPromptTemplate.from_template(combined_prompt)
```

## Benefits

### 1. Maintainability
- Prompts are now in dedicated files
- Easy to find and edit without touching code
- Version control for prompt changes
- Clear separation between prompt engineering and code logic

### 2. Reusability
- Prompts can be imported by multiple services
- Mood modifiers shared across different components
- Base prompt can be reused with different modifiers

### 3. Testability
- Prompts can be tested independently
- Easy to A/B test different prompt versions
- Can swap prompts without code changes

### 4. Collaboration
- Prompt engineers can edit prompts without Python knowledge
- Clear documentation in each prompt file
- Easy to review prompt changes in PRs

### 5. Flexibility
- Easy to add new moods (just add to `MOOD_MODIFIERS`)
- Can create prompt variations for different use cases
- Dynamic prompt assembly allows for complex combinations

## Prompt Structure

### Base Prompt (story_writer.py)
```
ROLE → VISUAL-READY RULE → [MOOD MODIFIER INSERTED HERE] → UNIVERSAL STRUCTURE → WRITING STYLE → OUTPUT → INPUT
```

### Mood Modifier (story_mood.py)
```
[STYLE MODIFIER: {MOOD_NAME}]
Genre Rule → Setting Translation → Character Translation → Visual Aesthetic → Tone
```

### Rewriter Prompt (story_rewriter.py)
```
ROLE → IMPROVEMENT RULES → VISUAL CONSISTENCY → STRUCTURE → INPUT (story + feedback) → OUTPUT
```

## Usage Example

```python
from app.services.story_writer import story_writer, RedditPost

# Create a post with mood
post = RedditPost(
    id="123",
    title="AITA for leaving my wedding?",
    content="I found out my fiancé was cheating...",
    mood="revenge"  # This will apply the revenge mood modifier
)

# Generate story (prompt is assembled automatically)
story = await story_writer.write_story(post)
```

## Future Enhancements

1. **Prompt Versioning**
   - Add version numbers to prompts
   - Track which version generated each story
   - A/B test different prompt versions

2. **Prompt Templates**
   - Create template system for common patterns
   - Allow dynamic prompt composition
   - Support for custom user prompts

3. **Prompt Analytics**
   - Track which prompts generate best stories
   - Measure evaluation scores by prompt version
   - Optimize prompts based on data

4. **Prompt Library**
   - Create library of reusable prompt components
   - Mix and match components for different effects
   - Community-contributed prompts

5. **Prompt Configuration**
   - Move prompts to configuration files (YAML/JSON)
   - Allow runtime prompt updates
   - Support for environment-specific prompts

## Files Modified

1. `backend/app/services/story_writer.py` - Refactored to use centralized prompts
2. `backend/app/services/story_rewriter.py` - Refactored to use centralized prompts
3. `backend/app/prompt/story_writer.py` - Added docstring and exported constant
4. `backend/app/prompt/story_mood.py` - Added docstring
5. `backend/app/prompt/story_rewriter.py` - Created new file

## Testing Checklist

- [ ] Story generation works with all 5 moods
- [ ] Mood modifiers are correctly inserted into prompts
- [ ] Rewriter uses new centralized prompt
- [ ] Generated stories match expected mood style
- [ ] No regression in story quality
- [ ] Prompts are properly formatted
- [ ] Error handling works correctly

## Notes

- All prompts are now in `backend/app/prompt/` directory
- Services import prompts as constants
- Prompt assembly happens dynamically at runtime
- No changes to API or workflow logic
- Backward compatible with existing code
