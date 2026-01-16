# Prompt Architecture

## Prompt Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Story Generation Request                     │
│                  (Reddit Post + Mood Selection)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Story Writer Service                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  _get_prompt_template(mood)                            │   │
│  │                                                         │   │
│  │  1. Load base prompt from story_writer.py             │   │
│  │  2. Load mood modifier from story_mood.py             │   │
│  │  3. Combine: Base + Mood Modifier                     │   │
│  │  4. Replace placeholders with actual inputs           │   │
│  └────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Assembled Prompt                              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ROLE: Viral Webtoon Story Architect                     │  │
│  │                                                          │  │
│  │ THE VISUAL-READY RULE:                                  │  │
│  │ - Subject Focus (1-2 characters)                        │  │
│  │ - Concrete Actions                                      │  │
│  │ - Visual Consistency                                    │  │
│  │ - Straightforward Structure                             │  │
│  │                                                          │  │
│  │ [STYLE MODIFIER: {SELECTED_MOOD}]                       │  │
│  │ - Genre Rule                                            │  │
│  │ - Setting Translation                                   │  │
│  │ - Character Translation                                 │  │
│  │ - Visual Aesthetic                                      │  │
│  │ - Tone                                                  │  │
│  │                                                          │  │
│  │ THE UNIVERSAL STRUCTURE:                                │  │
│  │ - THE HOOK (0-15s)                                      │  │
│  │ - THE CLIMB (15-50s)                                    │  │
│  │ - THE EMOTIONAL PEAK (50-70s)                           │  │
│  │ - THE HARD STOP                                         │  │
│  │                                                          │  │
│  │ WRITING STYLE:                                          │  │
│  │ - Active Present Tense                                  │  │
│  │ - No Internal Monologue                                 │  │
│  │ - Minimalist Scenes                                     │  │
│  │                                                          │  │
│  │ INPUT:                                                  │  │
│  │ Title: {Reddit Post Title}                              │  │
│  │ Content: {Reddit Post Content}                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Gemini 2.0 Flash                            │
│                   (LLM Processing)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Generated Story (Draft)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Story Evaluator                               │
│                  (Scores 1-10 + Feedback)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
              Score >= 7?        Score < 7?
                    │                 │
                    ▼                 ▼
            ┌──────────────┐  ┌──────────────────┐
            │   END        │  │  Story Rewriter  │
            │ (Return      │  │                  │
            │  Story)      │  │  Uses:           │
            └──────────────┘  │  - Original Story│
                              │  - Feedback      │
                              │  - Rewriter      │
                              │    Prompt        │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ Rewritten Story  │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │  Re-evaluate     │
                              │  (Max 1 rewrite) │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │   Final Story    │
                              └──────────────────┘
```

## Prompt File Organization

```
backend/app/prompt/
│
├── story_writer.py          # Base prompt for story generation
│   └── STORY_WRITER_PROMPT
│       ├── Role Definition
│       ├── Visual-Ready Rule
│       ├── Universal Structure
│       ├── Writing Style
│       └── Input/Output Format
│
├── story_mood.py            # Mood-specific style modifiers
│   └── MOOD_MODIFIERS = {
│       ├── "rofan"          # Romance Fantasy
│       ├── "modern_romance" # K-Drama Style
│       ├── "slice_of_life"  # Healing/Cozy
│       ├── "revenge"        # Revenge & Glow-up
│       └── "high_teen"      # Academy Drama
│       }
│
└── story_rewriter.py        # Prompt for story improvement
    └── REWRITER_PROMPT
        ├── Role Definition
        ├── Improvement Rules
        ├── Visual Consistency
        └── Structure Preservation
```

## Prompt Composition Strategy

### 1. Base Prompt (Foundation)
- Defines the core role and objectives
- Sets visual-ready guidelines
- Establishes universal structure
- Defines writing style

### 2. Mood Modifier (Style Layer)
- Injected between Visual-Ready Rule and Universal Structure
- Transforms genre and setting
- Defines character archetypes
- Sets visual aesthetic and tone

### 3. Input Variables (Context)
- Reddit post title and content
- Dynamically inserted at runtime
- Provides the "seed" for story generation

### 4. Final Assembled Prompt
```
Base Prompt (Part 1: Role + Visual-Ready Rule)
    ↓
+ Mood Modifier (Genre-specific transformation)
    ↓
+ Base Prompt (Part 2: Structure + Style)
    ↓
+ Input Variables (Reddit post data)
    ↓
= Complete Prompt sent to LLM
```

## Mood Modifier Injection Point

```python
# Original Base Prompt Structure:
"""
ROLE
VISUAL-READY RULE
                        ← MOOD MODIFIER INSERTED HERE
UNIVERSAL STRUCTURE
WRITING STYLE
OUTPUT
INPUT
"""

# After Injection:
"""
ROLE
VISUAL-READY RULE

[STYLE MODIFIER: REVENGE & GLOW-UP]
Genre Rule: Maximize contrast...
Setting Translation: ...
Character Translation: ...
Visual Aesthetic: ...
Tone: ...

UNIVERSAL STRUCTURE
WRITING STYLE
OUTPUT
INPUT
"""
```

## Prompt Variables

### Story Writer Prompt Variables
- `{title}` - Reddit post title
- `{content}` - Reddit post content

### Story Rewriter Prompt Variables
- `{story}` - Original story text
- `{feedback}` - Evaluator feedback

## Prompt Design Principles

### 1. Modularity
- Each prompt component is independent
- Can be mixed and matched
- Easy to add new moods or styles

### 2. Clarity
- Clear section headers (marked with **)
- Numbered lists for rules
- Concrete examples

### 3. Consistency
- All prompts follow similar structure
- Common terminology across prompts
- Predictable format for LLM

### 4. Specificity
- Concrete instructions (not abstract)
- Visual-first language
- Actionable guidelines

### 5. Flexibility
- Supports multiple moods
- Adaptable to different inputs
- Extensible for future features

## Example: Prompt Assembly for "Revenge" Mood

```python
# Input
post = RedditPost(
    title="AITA for exposing my ex at their wedding?",
    content="They cheated on me and I showed up with receipts...",
    mood="revenge"
)

# Step 1: Load base prompt
base = STORY_WRITER_PROMPT

# Step 2: Load mood modifier
mood_mod = MOOD_MODIFIERS["revenge"]

# Step 3: Combine
combined = f"""
{base_part1}

{mood_mod}

{base_part2}
"""

# Step 4: Insert variables
final = combined.format(
    title=post.title,
    content=post.content
)

# Result: Complete prompt ready for LLM
```

## Prompt Optimization Tips

### For Story Writer Prompt:
1. Keep instructions concrete and visual
2. Use examples when possible
3. Emphasize "show don't tell"
4. Focus on AI-drawable actions
5. Maintain consistent character traits

### For Mood Modifiers:
1. Clear transformation rules
2. Specific visual keywords
3. Tone-appropriate language
4. Genre-consistent examples
5. Avoid conflicting instructions

### For Rewriter Prompt:
1. Preserve original intent
2. Address specific feedback
3. Maintain visual consistency
4. Keep structure intact
5. Improve without overwriting

## Testing Prompts

### Unit Testing
```python
# Test prompt assembly
def test_prompt_assembly():
    prompt = story_writer._get_prompt_template("revenge")
    assert "REVENGE & GLOW-UP" in prompt
    assert "{title}" in prompt
    assert "{content}" in prompt
```

### Integration Testing
```python
# Test with actual LLM
async def test_story_generation():
    post = RedditPost(...)
    story = await story_writer.write_story(post)
    assert len(story) > 100
    assert "revenge" theme in story
```

### Quality Testing
- Manual review of generated stories
- Evaluation scores tracking
- User feedback collection
- A/B testing different prompt versions

## Maintenance Guidelines

### When to Update Prompts:
1. Story quality issues
2. Evaluation scores consistently low
3. User feedback indicates problems
4. New mood/style requirements
5. LLM model updates

### How to Update Prompts:
1. Edit prompt file in `backend/app/prompt/`
2. Test with sample inputs
3. Compare before/after results
4. Deploy and monitor metrics
5. Rollback if quality degrades

### Version Control:
- Track prompt changes in git
- Document reasons for changes
- Keep old versions for comparison
- Tag releases with prompt versions
