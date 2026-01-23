# Webtoon Enhancement Proposal

## Document Purpose
This document captures the discussion and proposed solutions for transforming the current webtoon generation system from "functional but plain" to "dynamic and human-drawn feeling."

---

## Part 1: Current State Problems

### Problem 1: Scene Count Limitation Creates Plain Output

**Current State:**
- System generates 8-12 scenes (enforced by prompts + evaluator)
- Each scene = 1 image = 1 visual moment
- Video duration: 60-120 seconds
- Result: ~5-10 seconds per scene

**Why It's a Problem:**
- Dialogue often progresses faster than visuals
- One visual can't represent multiple story beats in a dialogue exchange
- Forces "establishing shot" style - showing WHERE characters are rather than WHAT they're feeling
- Real webtoons show progression: reaction → close-up → wide shot within one story beat

**Root Cause:**
The "1 scene = 1 image" model doesn't match webtoon visual grammar.

---

### Problem 2: Multi-Panel Generation Was Unreliable

**Previous Attempt:**
- Generate 2-3 panels within a single image
- AI had to draw panel borders + multiple compositions + maintain consistency
- Results were inconsistent (sometimes worked, sometimes failed)

**Why It Failed:**
- Too many competing objectives in one generation call
- Panel border drawing is finicky
- Character consistency across panels in one image is hard
- Layout decisions embedded in generation (can't adjust after)

---

### Problem 3: Imagery Is Too Static/Plain

**Current State:**
- Most images are "characters in location" shots
- Missing: close-ups, detail shots (hands, lips, eyes), reaction shots, atmospheric shots
- Images explain WHERE characters are, not WHAT they're feeling

**Evidence from Code:**
- `shot_type` field exists but no evaluator enforcement
- `character_frame_percentage` underutilized (likely always 40-60%)
- No explicit "emotional beat" or "intensity" field to drive shot selection

**What Real Webtoons Have:**
- Extreme close-ups for emotional moments (eyes filling the panel)
- Detail shots (clenched fist, trembling lip, hand reaching)
- Reaction panels (character's face responding)
- Atmosphere panels (rain on window, empty coffee cup)
- Dynamic angles (low angle for power, high angle for vulnerability)

---

### Problem 4: Image Style Is Monolithic

**Current State:**
- User selects ONE image style (e.g., "SOFT_ROMANTIC_WEBTOON")
- Style passed as single template to all image generations
- Same aesthetic throughout entire webtoon

**What Real Webtoons Do:**
- Comedy moments → simpler/chibi style, exaggerated expressions
- Serious moments → detailed rendering, dramatic lighting
- Romantic moments → soft focus, warm colors, blush effects
- Flashbacks → desaturated, different color palette
- Dreams → ethereal, surreal elements

**Code Finding:**
The writer prompt mentions style override authority, but:
- It's buried in a massive prompt
- No structured output for style modifiers
- No per-scene mood/style fields in the data model

---

### Problem 5: SFX System Is Defined But Unused

**Current State:**
- `sfx_effects: Optional[List[dict]]` exists in WebtoonPanel model
- Video generation doesn't render SFX
- Output feels like "slideshow of images" not "webtoon video"

**What's Missing:**
- Impact text ("CRASH!", "THUMP!", "SLAM!", "WHOOSH!")
- Motion lines / speed effects
- Screen effects (flash, shake, blur)
- Emotional effects (sparkles, dark aura, flowers)

---

### Problem 6: Evaluator Optimizes for Safety, Not Quality

**Current Weights:**
| Metric | Weight | Issue |
|--------|--------|-------|
| Scene count | 30% | Quantity over quality |
| Dialogue coverage | 25% | Encourages text, not visuals |
| Visual prompt length | 20% | Length ≠ interesting |
| Character consistency | 15% | Good |
| Story structure | 10% | Vague |

**Missing Evaluations:**
- Shot type variety (no enforcement)
- Emotional beat coverage
- Visual dynamism
- Frame percentage distribution

---

### Problem 7: Writer Agent Is Overloaded

**Current Webtoon Writer Responsibilities:**
1. Understand story narrative
2. Break into scenes
3. Decide shot types
4. Write visual prompts
5. Write dialogue
6. Plan style variations
7. Add SFX
8. Ensure character consistency
9. Maintain story structure

**Result:**
LLM can't optimize all simultaneously → defaults to "safe" choices.

---

## Part 2: Proposed Solutions

### Solution 1: Direct Multi-Panel Generation with Structured Prompts

**Concept:**
Generate multi-panel webtoon pages directly using well-structured prompts. Gemini handles this reliably when prompts follow a clear panel-by-panel format.

**Why This Works (vs previous attempts):**
Previous attempts failed because prompts were vague about layout. With structured prompts specifying each panel explicitly, Gemini generates consistent multi-panel images.

**Prompt Structure Template:**
```
A vertical webtoon-style comic page with a 9:16 aspect ratio,
featuring [N] distinct horizontal panels stacked vertically.
The art style is [STYLE_DESCRIPTION].

Panel 1: [shot_type] of [subject] [action/emotion]. [details]
Panel 2: [shot_type] of [subject] [action/emotion]. [details]
Panel 3: [shot_type] of [subject] [action/emotion]. [details]
...

[STYLE_KEYWORDS]. Thin panel borders.
```

**Example (from testing):**
```
A vertical webtoon-style comic page with a 9:16 aspect ratio,
featuring 5 distinct horizontal panels stacked vertically.
The art style is vibrant digital 2D illustration (manhwa style).

Panel 1: A close-up of a female fantasy protagonist with blue eyes
         and dark hair looking determined.
Panel 2: A wide establishing shot of a floating castle city at sunrise.
Panel 3: The hero jumping off a cliff toward a giant griffin.
Panel 4: The hero riding the griffin through the clouds.
Panel 5: A small fairy guide pointing at a map while the hero looks on.

High resolution, clean line art.
```

**Benefits:**
- **Cost effective**: 1 API call generates 3-5 panels (vs 3-5 separate calls)
- **Better consistency**: Same generation = same style/colors across panels
- **No post-processing**: No crop/compose step needed
- **Natural webtoon feel**: AI understands panel flow and visual rhythm

**Panel Layout Options:**
```
3-Panel Page:    [==========]     - Standard story progression
                 [==========]
                 [==========]

4-Panel Page:    [==========]     - Detailed sequence
                 [==========]
                 [==========]
                 [==========]

5-Panel Page:    [==========]     - Dense storytelling
                 [==========]
                 [==========]
                 [==========]
                 [==========]

Mixed Heights:   [==========]     - Emphasis variation
                 [====]
                 [==========]
                 [====]
```

**Implementation Approach:**
1. Cinematographer plans shot sequence with shot types
2. Panel Composer groups shots into pages (3-5 panels per page)
3. Visual Prompter formats into structured multi-panel prompt
4. Single API call generates entire page
5. Output: Complete webtoon pages ready for video

**When to Use Single vs Multi-Panel:**
| Situation | Approach |
|-----------|----------|
| Key emotional moment | Single full-page panel |
| Action sequence | 4-5 panel page |
| Dialogue exchange | 3-4 panel page |
| Establishing + reaction | 2-3 panel page |
| Climax/reveal | Single panel for impact |

---

### Solution 2: Cinematographer Agent for Shot Planning

**Concept:**
Dedicated agent that plans shot sequence BEFORE visual prompts are written.

**Input:**
- Story beats from scene planner
- Emotional intensity per beat
- Genre conventions

**Output:**
```python
class ShotPlan:
    scene_number: int
    shots: List[Shot]

class Shot:
    shot_type: str          # "extreme_close_up", "detail", "wide", etc.
    subject: str            # "character_a_eyes", "hands", "both_characters"
    frame_percentage: int   # How much of frame subject fills
    angle: str              # "eye_level", "low", "high", "dutch"
    movement: str           # "static", "zoom_in", "pan_left"
    emotional_purpose: str  # "show_tension", "reveal_reaction", "establish_mood"
```

**Shot Type Library:**
| Type | Frame % | Use Case |
|------|---------|----------|
| Extreme Wide | 5-15% | Establishing, isolation, scale |
| Wide | 15-30% | Context, multiple characters |
| Medium | 30-50% | Standard dialogue, interaction |
| Medium Close-up | 50-70% | Emotional dialogue, focus |
| Close-up | 70-85% | Key emotions, reactions |
| Extreme Close-up | 85-100% | Intense emotion, detail emphasis |
| Detail Shot | varies | Hands, objects, symbolic elements |
| Over-shoulder | 40-60% | Conversation, POV hint |
| POV | 100% | Character perspective |

**Variety Rules:**
- No more than 2 consecutive shots of same type
- Each scene must have at least 2 different shot types
- Emotional peaks require close-up or extreme close-up
- Scene transitions should use establishing/wide shots

---

### Solution 3: Modular Style System

**Concept:**
Factor "image style" into composable components that can vary per scene.

**Base Style (constant throughout):**
```python
class BaseStyle:
    name: str                    # "SOFT_ROMANTIC_WEBTOON"
    medium: str                  # Cel-shading approach
    color_palette_base: str      # Core colors
    line_quality: str            # Clean, sketchy, bold, etc.
    rendering_quality: str       # High detail baseline
```

**Per-Scene Modifiers:**
```python
class SceneMood:
    color_temperature: str       # "warm", "neutral", "cool"
    saturation: str              # "vibrant", "normal", "muted", "desaturated"
    lighting_mood: str           # "soft", "dramatic", "harsh", "dreamy"
    detail_level: str            # "simplified", "standard", "detailed"
    expression_style: str        # "subtle", "normal", "expressive", "exaggerated"
    special_effect: Optional[str] # "chibi", "sparkles", "dark_aura", "flowers", "speed_lines"
```

**Mood Presets (auto-assigned based on emotional beat):**
```python
MOOD_PRESETS = {
    "comedy": {
        "detail_level": "simplified",
        "expression_style": "exaggerated",
        "special_effect": "chibi"
    },
    "romantic_tension": {
        "color_temperature": "warm",
        "lighting_mood": "soft",
        "special_effect": "sparkles"
    },
    "serious_conflict": {
        "saturation": "muted",
        "lighting_mood": "dramatic",
        "detail_level": "detailed"
    },
    "sad_emotional": {
        "color_temperature": "cool",
        "saturation": "desaturated",
        "lighting_mood": "soft"
    },
    "flashback": {
        "saturation": "desaturated",
        "special_effect": "vignette",
        "detail_level": "simplified"
    },
    "climax": {
        "lighting_mood": "dramatic",
        "detail_level": "detailed",
        "expression_style": "expressive"
    }
}
```

**Flow:**
1. Mood Designer agent analyzes each scene's emotional content
2. Assigns mood preset (can be overridden)
3. Scene modifiers combined with base style
4. Final style instruction passed to image generation

---

### Solution 4: SFX Rendering System

**Concept:**
Use existing `sfx_effects` field, render as video overlays.

**SFX Categories:**

**1. Impact Text (Onomatopoeia) - English**
```python
class ImpactText:
    text: str                # "CRASH!", "THUMP!", "SLAM!", "WHOOSH!", "GASP!"
    style: str               # "bold", "shaky", "explosive", "soft"
    position: tuple          # (x_pct, y_pct)
    size: str                # "small", "medium", "large", "massive"
    color: str               # Hex or preset
    rotation: int            # Degrees
    animation: str           # "pop", "shake", "grow", "none"
```

**2. Motion Effects**
```python
class MotionEffect:
    type: str                # "speed_lines", "blur", "impact_burst", "zoom_lines"
    direction: str           # "left", "right", "center", "radial"
    intensity: str           # "subtle", "medium", "intense"
    duration_ms: int         # How long effect shows
```

**3. Screen Effects**
```python
class ScreenEffect:
    type: str                # "flash", "shake", "vignette", "color_shift"
    intensity: str
    duration_ms: int
```

**4. Emotional Effects**
```python
class EmotionalEffect:
    type: str                # "sparkles", "flowers", "dark_aura", "sweat_drop", "heart"
    position: str            # "around_character", "background", "corner"
    animation: str           # "float", "burst", "pulse"
```

**Video Integration:**
- SFX rendered as transparent overlays
- Composited during video generation
- Timed to appear with specific dialogue or panel transitions

**SFX Mapping (auto-suggestions by emotion/action):**
```python
SFX_TRIGGERS = {
    "surprise": ["!", "pop_effect"],
    "anger": ["speed_lines", "dark_aura"],
    "love": ["sparkles", "hearts", "flowers"],
    "fear": ["sweat_drop", "shake"],
    "impact": ["impact_burst", "CRASH/THUD text"],
    "realization": ["flash", "zoom_lines"],
    "comedy": ["sweat_drop", "chibi_expression"]
}
```

---

### Solution 5: Enhanced Evaluation System

**New Evaluation Metrics:**

```python
EVALUATION_WEIGHTS = {
    "story_coverage": 0.20,        # Does it cover the narrative?
    "shot_variety": 0.20,          # Distribution of shot types
    "emotional_alignment": 0.15,   # Mood matches content
    "visual_dynamism": 0.15,       # Not all static medium shots
    "dialogue_integration": 0.15,  # Dialogue matches visuals
    "character_consistency": 0.10, # Characters recognizable
    "sfx_appropriateness": 0.05,   # SFX used effectively
}
```

**Shot Variety Scoring:**
```python
def score_shot_variety(shots: List[Shot]) -> float:
    shot_types = [s.shot_type for s in shots]

    # Penalize if >50% are same type
    most_common_ratio = max(Counter(shot_types).values()) / len(shots)
    variety_score = 1.0 - (most_common_ratio - 0.3) if most_common_ratio > 0.3 else 1.0

    # Bonus for having close-ups and detail shots
    has_closeup = any(s in shot_types for s in ["close_up", "extreme_close_up"])
    has_detail = "detail" in shot_types

    return variety_score * (1.1 if has_closeup else 1.0) * (1.1 if has_detail else 1.0)
```

**Visual Dynamism Scoring:**
```python
def score_dynamism(shots: List[Shot]) -> float:
    # Check frame percentage distribution
    frame_pcts = [s.frame_percentage for s in shots]
    variance = statistics.variance(frame_pcts)

    # Higher variance = more dynamic (mix of close and wide)
    # Ideal variance around 400-600 (range of 20-80% coverage)
    if variance < 100:
        return 0.5  # Too uniform
    elif variance > 800:
        return 0.8  # Maybe too chaotic
    else:
        return 1.0  # Good variety
```

---

### ~~Solution 6: Video Enhancement - Ken Burns Effect~~ (REJECTED)

**Why Not:**
- Dialogue text is displayed over images during video playback
- Camera movement (zoom/pan) while reading text causes viewer dizziness
- Short SFX bursts work better than continuous movement
- Static image + dynamic SFX overlay = better experience than moving image + static text

**Alternative:** Focus on SFX system (Solution 4) for visual dynamism instead.

---

## Part 3: Proposed Architecture

### Option A: Multi-Agent Pipeline (Recommended)

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT: Story                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STORY ANALYST AGENT                           │
│  - Extract key narrative beats                                   │
│  - Identify emotional peaks                                      │
│  - Map character arcs                                            │
│  - Output: StoryAnalysis (beats, emotions, characters)           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SCENE PLANNER AGENT                           │
│  - Divide story into scenes                                      │
│  - Assign story beats to scenes                                  │
│  - Determine scene count (flexible, based on content)            │
│  - Output: ScenePlan (scenes with beats and dialogue)            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CINEMATOGRAPHER AGENT                          │
│  - Plan shot sequence for each scene                             │
│  - Assign shot types (close-up, wide, detail, etc.)              │
│  - Determine frame percentages and angles                        │
│  - Ensure variety rules are met                                  │
│  - Output: ShotPlan (shots with types, subjects, purposes)       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MOOD DESIGNER AGENT                           │
│  - Analyze emotional content of each shot                        │
│  - Assign mood modifiers (color temp, lighting, detail level)    │
│  - Select special effects per shot                               │
│  - Output: MoodPlan (per-shot style modifiers)                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   VISUAL PROMPTER AGENT                          │
│  - Format shots into structured multi-panel prompts              │
│  - "Panel 1: ... Panel 2: ... Panel 3: ..." format               │
│  - Incorporate shot type, mood, character details                │
│  - Output: PagePrompts (multi-panel generation prompts)          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SFX PLANNER AGENT                              │
│  - Identify moments needing SFX                                  │
│  - Assign impact text, motion effects, emotional effects         │
│  - Output: SFXPlan (per-shot effects)                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PANEL COMPOSER AGENT                           │
│  - Group shots into pages (3-5 panels per page)                  │
│  - Decide: multi-panel page vs single full-page panel            │
│  - Key moments get dedicated single panels                       │
│  - Output: PageLayouts (which shots go on which page)            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EVALUATOR AGENT                             │
│  - Score using new metrics                                       │
│  - Check shot variety, emotional alignment, dynamism             │
│  - Output: EvaluationResult (score + specific feedback)          │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │   Score < Threshold?  │
                    └───────────┬───────────┘
                         │ Yes          │ No
                         ▼              ▼
              ┌──────────────────┐   ┌──────────────────┐
              │  REWRITER AGENT  │   │  Continue to     │
              │  (targeted fix)  │   │  Image Gen       │
              └────────┬─────────┘   └──────────────────┘
                       │
                       └──────► Back to relevant agent
                                (based on feedback)

                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    IMAGE GENERATION                              │
│  - Generate multi-panel pages using structured prompts           │
│  - 1 API call = 3-5 panels per page                              │
│  - Mix of multi-panel pages + single full-page panels            │
│  - Use visual prompts + style modifiers                          │
│  - Character reference integration                               │
│  - Output: 5-8 page images (containing 15-25 total panels)       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VIDEO GENERATION                              │
│  - Sequence panels with timing                                   │
│  - Add dialogue bubbles                                          │
│  - Render SFX overlays                                           │
│  - Output: Final video (60-180 seconds, YouTube Shorts format)   │
└─────────────────────────────────────────────────────────────────┘
```

### LangGraph Implementation Sketch

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List

class WebtoonState(TypedDict):
    # Input
    story: str
    genre: str
    base_style: str

    # Stage outputs
    story_analysis: Optional[dict]
    scene_plan: Optional[dict]
    shot_plan: Optional[dict]
    mood_plan: Optional[dict]
    visual_prompts: Optional[dict]
    sfx_plan: Optional[dict]
    panel_layouts: Optional[dict]

    # Evaluation
    evaluation_score: float
    evaluation_feedback: str
    rewrite_target: Optional[str]  # Which agent to rerun
    rewrite_count: int

    # Final outputs
    generated_images: Optional[List[str]]
    composed_panels: Optional[List[str]]
    final_video: Optional[str]

# Build graph
workflow = StateGraph(WebtoonState)

# Add nodes
workflow.add_node("story_analyst", story_analyst_node)
workflow.add_node("scene_planner", scene_planner_node)
workflow.add_node("cinematographer", cinematographer_node)
workflow.add_node("mood_designer", mood_designer_node)
workflow.add_node("visual_prompter", visual_prompter_node)
workflow.add_node("sfx_planner", sfx_planner_node)
workflow.add_node("panel_composer", panel_composer_node)
workflow.add_node("evaluator", evaluator_node)
workflow.add_node("rewriter", rewriter_node)
workflow.add_node("image_generator", image_generator_node)
workflow.add_node("panel_compositor", panel_compositor_node)
workflow.add_node("video_generator", video_generator_node)

# Define edges
workflow.set_entry_point("story_analyst")
workflow.add_edge("story_analyst", "scene_planner")
workflow.add_edge("scene_planner", "cinematographer")
workflow.add_edge("cinematographer", "mood_designer")
workflow.add_edge("mood_designer", "visual_prompter")
workflow.add_edge("visual_prompter", "sfx_planner")
workflow.add_edge("sfx_planner", "panel_composer")
workflow.add_edge("panel_composer", "evaluator")

# Conditional routing from evaluator
workflow.add_conditional_edges(
    "evaluator",
    route_after_evaluation,
    {
        "rewrite": "rewriter",
        "generate": "image_generator"
    }
)

# Rewriter routes back to appropriate agent
workflow.add_conditional_edges(
    "rewriter",
    route_rewrite_target,
    {
        "scene_planner": "scene_planner",
        "cinematographer": "cinematographer",
        "mood_designer": "mood_designer",
        "visual_prompter": "visual_prompter",
        "sfx_planner": "sfx_planner",
        "panel_composer": "panel_composer"
    }
)

# Final generation pipeline
workflow.add_edge("image_generator", "panel_compositor")
workflow.add_edge("panel_compositor", "video_generator")
workflow.add_edge("video_generator", END)
```

---

### Option B: Enhanced Single Agent (Simpler Alternative)

If multi-agent feels too complex, enhance the current writer with structured multi-stage output:

```python
class EnhancedWebtoonScript:
    # Stage 1: Analysis
    story_beats: List[StoryBeat]
    emotional_peaks: List[int]  # Beat indices

    # Stage 2: Scene Plan
    scenes: List[Scene]

    # Stage 3: Shot Plan (per scene)
    # Embedded in Scene object

    # Stage 4: Visual Details
    panels: List[WebtoonPanel]  # With all details

    # Stage 5: Mood & SFX
    # Embedded in Panel object
```

**Pros:** Simpler, one LLM call (or chained calls)
**Cons:** Still overloaded, harder to debug individual stages

---

## Part 4: Implementation Priorities

### Phase 1: Foundation (High Impact, Medium Effort)
1. **Add Cinematographer logic** - Shot type planning and variety enforcement
2. **Enhance evaluator** - Add shot variety and dynamism metrics
3. **SFX rendering** - Implement video overlay system (replaces Ken Burns for dynamism)

### Phase 2: Visual Enhancement (High Impact, Medium Effort)
4. **Modular style system** - Factor out style into components
5. **Mood Designer logic** - Per-scene style modifiers
6. **Panel prompt enhancement** - Update image gen prompts to include panel layouts

### Phase 3: Panel System (High Impact, Medium Effort)
7. **Structured prompt templates** - Panel-by-panel prompt format for multi-panel generation
8. **Panel Composer logic** - Group shots into pages (3-5 panels each), decide layout
9. **Increase visual density** - More panels per webtoon (15-25 panels across 5-8 pages)

### Phase 4: Architecture (Medium Impact, High Effort)
10. **Multi-agent refactor** - Split into specialized agents
11. **Targeted rewriting** - Route feedback to specific agents (max 3 iterations)

---

## Part 4.1: Development Task List

### Legend
- [ ] Not started
- [~] In progress
- [x] Complete

---

### Phase 1: Foundation

#### 1.1 Data Model Updates
- [ ] Add `Shot` model to `models/story.py`
  ```python
  class Shot:
      shot_id: str
      shot_type: str  # "extreme_close_up", "close_up", "medium", "wide", "detail"
      subject: str
      frame_percentage: int
      angle: str
      emotional_purpose: str
      belongs_to_scene: int
  ```
- [ ] Add `ShotPlan` model to `models/story.py`
- [ ] Add `emotional_intensity` field to existing panel model (1-10 scale)
- [ ] Add `shot_type` enum with enforced values

#### 1.2 Cinematographer Service
- [ ] Create `services/cinematographer.py`
- [ ] Implement `plan_shots(scenes: List[Scene]) -> ShotPlan`
- [ ] Define shot type distribution rules:
  - No more than 2 consecutive same shot types
  - Emotional peaks require close-up or extreme close-up
  - Each scene must have 2+ different shot types
- [ ] Create cinematographer prompt template in `prompt/cinematographer.py`
- [ ] Add variety scoring function

#### 1.3 Enhanced Evaluator
- [ ] Update `services/webtoon_evaluator.py`
- [ ] Add `score_shot_variety()` function
- [ ] Add `score_visual_dynamism()` function
- [ ] Update weights:
  ```python
  EVALUATION_WEIGHTS = {
      "story_coverage": 0.20,
      "shot_variety": 0.20,
      "emotional_alignment": 0.15,
      "visual_dynamism": 0.15,
      "dialogue_integration": 0.15,
      "character_consistency": 0.10,
      "sfx_appropriateness": 0.05,
  }
  ```
- [ ] Add feedback for shot variety issues

#### 1.4 SFX System - Models
- [ ] Create `models/sfx.py`
- [ ] Define `ImpactText` model
- [ ] Define `MotionEffect` model
- [ ] Define `ScreenEffect` model
- [ ] Define `EmotionalEffect` model
- [ ] Define `SFXEffect` union type

#### 1.5 SFX System - Rendering
- [ ] Create `services/sfx_renderer.py`
- [ ] Implement impact text rendering (PIL)
- [ ] Add SFX font config to `config.py` (configurable path)
- [ ] Implement screen flash effect
- [ ] Implement screen shake effect
- [ ] Update `services/video_service.py` to call SFX renderer
- [ ] Add SFX timing logic (on_enter, with_dialogue, on_exit)

#### 1.6 SFX System - Planning
- [ ] Create `services/sfx_planner.py`
- [ ] Implement emotion-to-SFX mapping
- [ ] Create SFX planner prompt template
- [ ] Integrate with panel generation flow

---

### Phase 2: Visual Enhancement

#### 2.1 Modular Style System - Models
- [ ] Create `models/style.py`
- [ ] Define `BaseStyle` model
- [ ] Define `SceneMood` model with fields:
  - color_temperature
  - saturation
  - lighting_mood
  - detail_level
  - expression_style
  - special_effect
- [ ] Define `MOOD_PRESETS` dictionary

#### 2.2 Modular Style System - Refactor
- [ ] Update `prompt/image_style.py` to use modular structure
- [ ] Refactor existing styles into BaseStyle + default mood
- [ ] Create style composition function: `compose_style(base, mood) -> str`

#### 2.3 Mood Designer Service
- [ ] Create `services/mood_designer.py`
- [ ] Implement `assign_moods(shots: List[Shot]) -> List[SceneMood]`
- [ ] Create mood designer prompt template
- [ ] Add mood preset auto-selection based on emotional_intensity

#### 2.4 Integration
- [ ] Update webtoon workflow to include mood assignment step
- [ ] Pass mood modifiers to image generation
- [ ] Update image generation prompt to incorporate mood

---

### Phase 3: Panel System

#### 3.1 Multi-Panel Prompt Template
- [ ] Create `prompt/multi_panel.py`
- [ ] Define structured prompt template:
  ```
  A vertical webtoon-style comic page with 9:16 aspect ratio,
  featuring {panel_count} distinct horizontal panels stacked vertically.
  Art style: {style_description}

  Panel 1: {shot_description}
  Panel 2: {shot_description}
  ...

  {style_keywords}. Thin panel borders.
  ```
- [ ] Create function `format_multi_panel_prompt(shots, style, mood)`

#### 3.2 Panel Composer Service
- [ ] Create `services/panel_composer.py`
- [ ] Implement `group_shots_into_pages(shots: List[Shot]) -> List[Page]`
- [ ] Define rules:
  - Key emotional moments → single full-page panel
  - Action sequences → 4-5 panels per page
  - Dialogue exchanges → 3-4 panels per page
  - Standard progression → 3 panels per page
- [ ] Create panel composer prompt template

#### 3.3 Image Generation Update
- [ ] Update `routers/webtoon.py` image generation endpoint
- [ ] Add support for multi-panel generation
- [ ] Update to use structured prompt format
- [ ] Handle mix of single + multi-panel pages

#### 3.4 Workflow Integration
- [ ] Update scene count targets (15-25 panels total)
- [ ] Update evaluator for new panel counts
- [ ] Add page count validation (5-8 pages)

---

### Phase 4: Architecture

#### 4.1 Agent Separation
- [ ] Extract Story Analyst from webtoon writer
- [ ] Extract Scene Planner from webtoon writer
- [ ] Create dedicated Cinematographer node
- [ ] Create dedicated Mood Designer node
- [ ] Create dedicated Visual Prompter node
- [ ] Create dedicated SFX Planner node
- [ ] Create dedicated Panel Composer node

#### 4.2 LangGraph Workflow
- [ ] Create `workflows/enhanced_webtoon_workflow.py`
- [ ] Define `WebtoonState` with all stage outputs
- [ ] Implement node functions for each agent
- [ ] Define edge routing
- [ ] Implement targeted rewrite routing

#### 4.3 Evaluation & Rewrite Loop
- [ ] Update evaluator to identify which agent caused issues
- [ ] Implement `route_rewrite_target()` function
- [ ] Add rewrite count tracking per agent
- [ ] Set max 3 total rewrites

---

### Testing Checkpoints

#### After Phase 1
- [ ] Generate webtoon with cinematographer
- [ ] Verify shot variety in output
- [ ] Test SFX rendering in video
- [ ] Compare visual quality before/after

#### After Phase 2
- [ ] Test mood variation across scenes
- [ ] Verify style shifts align with emotional beats
- [ ] Compare with monolithic style output

#### After Phase 3
- [ ] Test multi-panel generation reliability
- [ ] Verify panel count targets (15-25)
- [ ] Measure API cost reduction
- [ ] Test mix of single + multi-panel pages

#### After Phase 4
- [ ] End-to-end test full pipeline
- [ ] Verify targeted rewriting works
- [ ] Performance/latency testing
- [ ] Compare output quality vs current system

---

## Part 5: Data Model Updates

### New/Modified Models

```python
# New: Story Analysis
class StoryBeat:
    beat_number: int
    description: str
    characters_involved: List[str]
    emotional_intensity: int  # 1-10
    beat_type: str  # "setup", "conflict", "climax", "resolution", "transition"

class StoryAnalysis:
    beats: List[StoryBeat]
    emotional_arc: List[int]  # Intensity per beat
    key_moments: List[int]  # Beat indices for emphasis

# New: Shot Planning
class Shot:
    shot_id: str
    shot_type: str
    subject: str
    frame_percentage: int
    angle: str
    movement: str
    emotional_purpose: str
    belongs_to_scene: int

class ShotPlan:
    shots: List[Shot]
    variety_score: float

# New: Mood/Style
class SceneMood:
    color_temperature: str
    saturation: str
    lighting_mood: str
    detail_level: str
    expression_style: str
    special_effect: Optional[str]

# Enhanced: Panel
class EnhancedPanel:
    panel_id: str
    shots: List[str]  # Shot IDs included in this panel
    layout_type: str  # "single", "vertical_2", "horizontal_2", "l_shape_3", "grid_3"
    dialogue: List[dict]
    sfx_effects: List[SFXEffect]
    mood: SceneMood

# New: SFX
class SFXEffect:
    type: str  # "impact_text", "motion", "screen", "emotional"
    config: dict  # Type-specific configuration
    timing: str  # "on_enter", "with_dialogue", "on_exit"
```

---

## Part 6: Success Metrics

### Before vs After Targets

| Metric | Current | Target |
|--------|---------|--------|
| Total panels per webtoon | 8-12 | 15-25 |
| Pages (images) generated | 8-12 | 5-8 multi-panel pages |
| API calls for images | 8-12 | 5-8 (cost savings!) |
| Shot type variety | 2-3 types | 5+ types |
| Close-ups per webtoon | 0-2 | 5-8 |
| Detail shots per webtoon | 0-1 | 3-5 |
| Style variations | 0 | 2-4 mood shifts |
| SFX per webtoon | 0 | 5-10 |
| Single full-page panels | 100% | 20-30% (for key moments) |
| "Plain shot" ratio | ~80% | <30% |

### Quality Indicators
- Viewer can identify emotional beats from visuals alone
- Mix of establishing, medium, and close-up shots visible
- Style shifts align with mood changes
- SFX enhance impact moments
- Video feels dynamic, not slideshow

---

## Part 7: Decisions Made

These questions were discussed and resolved:

| Question | Decision | Rationale |
|----------|----------|-----------|
| **Panel generation approach** | Direct multi-panel generation | Gemini handles multi-panel reliably with structured prompts. 1 API call = 3-5 panels. Most cost-effective. No crop/compose needed. |
| **Character consistency** | Current system works | Occasionally changes clothing color, resolved by regenerating specific images. Acceptable. |
| **Generation order** | Dev: 1-by-1 / Prod: batch | During development, generate sequentially to inspect. In production, batch generate → review → regen failures. |
| **SFX text language** | English | "CRASH!", "THUMP!", "SLAM!" etc. Consistent with international webtoon style. |
| **Video duration** | 60-180 seconds | Keep current 60-120s target, allow extension up to 3 minutes (YouTube Shorts max). |
| **Evaluation iterations** | Max 3 rewrites | Balance between quality improvement and processing time/cost. |

### Additional Decisions

| Question | Decision | Notes |
|----------|----------|-------|
| **Panel border style** | Thin borders | Clean, modern webtoon aesthetic |
| **SFX font** | Same as dialogue font (configurable) | Store as separate font file path in config so it can be swapped later without code changes |
| **Dialogue placement** | Manual in UI | User positions dialogue bubbles by hand in the UI. System does NOT need to auto-position dialogue. |

---

## Conclusion

The current system works but produces "safe" output because:
1. Scene count is fixed and low
2. Shot variety isn't enforced
3. Style is monolithic
4. SFX aren't rendered
5. Writer agent is overloaded

The proposed enhancements address each issue:
1. More moments, composed into panels → richer visual storytelling
2. Cinematographer + shot variety metrics → dynamic framing
3. Modular style + mood designer → emotional visual shifts
4. SFX rendering → dynamic video feel (note: Ken Burns rejected due to dialogue readability)
5. Multi-agent pipeline → focused, optimizable components

**Key Decisions:**
- Panel approach: Direct multi-panel generation with structured prompts (1 call = 3-5 panels)
- Panel borders: Thin
- SFX language: English
- SFX font: Configurable (separate font file, easy to swap later)
- Dialogue placement: Manual in UI (no auto-positioning needed)
- Video duration: 60-180 seconds (YouTube Shorts compatible)
- Max evaluation rewrites: 3
- Generation workflow: batch → review → regen failures

Implementation can be phased, starting with highest-impact items (cinematographer logic, shot variety evaluation, SFX rendering) before tackling architectural changes.

---

*Document created: January 2026*
*Based on discussion between developer and Claude*
