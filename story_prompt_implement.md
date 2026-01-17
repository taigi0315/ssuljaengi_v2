# Webtoon Generation System - Implementation Guide

## Overview

This system generates webtoon panels from Reddit posts through a 3-stage pipeline:

1. **Story Generation** → Beat-based narrative (10-16 visual moments)
2. **Webtoon Writer** → Structured JSON with panel specifications
3. **Scene Image Generation** → Final image prompts for each panel

---

## Changes Required

### 🔴 **CRITICAL CHANGES**

#### 1. Story Generation Prompt (REPLACED)

**File**: `story_writer_prompt.py` or similar

**Problem**: Current prompt generates flowing web novel prose (1000-2000 words). This makes it nearly impossible for the Webtoon Writer to extract distinct visual panels.

**Solution**: Replace with the **beat-based story prompt** that outputs 10-16 paragraph "beats" where each paragraph = one potential visual panel.

**Key Differences**:

```python
# OLD (web novel style) ❌
"Hana walked through the subway, lost in thought about her day.
The cherry blossoms reminded her of when she first moved to Seoul..."

# NEW (beat-based) ✅
Paragraph 1: "The subway platform buzzes with evening commuters.
Hana stands near the yellow safety line, thumbs scrolling through
her phone. Cherry blossom petals drift across the floor."

Paragraph 2: "Across the platform, Jun descends the escalator,
camera bag slung over his shoulder. He pauses, noticing the falling
petals."
```

**Technical**: The prompt enforces:

- Present tense, active voice
- One paragraph = one visual moment
- Specific locations for every beat
- 10-16 total beats
- Minimal dialogue (0-2 lines per beat)
- Visual actions, not internal monologue

---

#### 2. Webtoon Writer Prompt (ENHANCED)

**File**: `webtoon_writer_prompt.py` or similar

**Problem**: Current prompt doesn't enforce environmental storytelling, frame composition, or shot diversity. Results in character-dominated panels.

**Solution**: Enhanced prompt with strict compositional rules and environmental priority.

**New Fields Required in Output JSON**:

```python
# Character object - UPDATED
{
    "name": str,
    "reference_tag": str,  # NEW - minimal tag like "Hana(24, student)"
    "gender": str,
    "age": str,
    "appearance_notes": str,  # NEW - detailed notes for reference only
    "typical_outfit": str,
    "personality_brief": str  # NEW - 1-2 words
}

# Scene object - UPDATED
{
    "scene_number": int,
    "shot_type": str,  # From defined list
    "composition_notes": str,  # NEW - e.g. "rule of thirds, character left"
    "environment_focus": str,  # NEW - primary setting
    "environment_details": str,  # NEW - specific props/architecture
    "atmospheric_conditions": str,  # NEW - lighting/weather/mood
    "character_frame_percentage": int,  # NEW - e.g. 35
    "environment_frame_percentage": int,  # NEW - e.g. 65
    "active_character_names": list[str],
    "character_placement_and_action": str,  # NEW - where + what doing
    "visual_prompt": str,  # ENHANCED - 200-300 words
    "negative_prompt": str,  # NEW - anti-portrait keywords
    "dialogue": list[dict] | None,  # Format: [{"character": "name", "text": "..."}]
    "story_beat": str  # NEW - one sentence narrative description
}
```

**Key Enforcement Rules**:

- Characters must occupy 25-45% max of frame
- Environment must occupy 55-75% of frame
- Shot diversity mandate: 30% wide, 30% medium, 20% dynamic angles, 15% close-ups, 5% creative
- Every visual_prompt must include:
  - Shot type integration
  - Composition rule
  - Environmental description (more words than character description)
  - Atmospheric details
  - Character placement and action

---

#### 3. Scene Image Template (REPLACED)

**File**: `scene_image_template.py` or similar

**Problem**: Current template is too minimal (just character description + scene description). Gives no compositional guidance, so AI defaults to portrait mode.

**Solution**: Enhanced template that uses all the new JSON fields to construct detailed prompts.

**New Structure**:

```python
SCENE_IMAGE_TEMPLATE = """
[Character reference handling section]
{character_description}  # Minimal, since refs handle appearance

[Shot composition section]
Shot Type: {shot_type}
Composition Rule: {composition_notes}
Frame Allocation: Characters {character_frame_percentage}%,
                  Environment {environment_frame_percentage}%

[Environment context section]
Primary Setting: {environment_focus}
Environmental Details: {environment_details}
Atmospheric Conditions: {atmospheric_conditions}

[Master visual prompt]
{visual_prompt}  # Complete 200-300 word prompt from JSON

[Negative prompt]
{negative_prompt}  # Anti-portrait keywords

[Technical parameters]
- Aspect Ratio: 9:16
- Character Reference Weight: 0.65  # IMPORTANT: Not 1.0!
- Focus Priority: Environment first, then characters
"""
```

---

## Pydantic Models Update

### Before:

```python
class Character(BaseModel):
    name: str
    gender: str
    age: str
    face: str
    hair: str
    body: str
    outfit: str
    mood: str
```

### After:

```python
class Character(BaseModel):
    name: str
    reference_tag: str  # NEW - e.g. "Hana(24, student)"
    gender: str
    age: str
    appearance_notes: str  # NEW - replaces face/hair/body combined
    typical_outfit: str
    personality_brief: str  # NEW - e.g. "quiet, observant"
```

### Before:

```python
class Scene(BaseModel):
    scene_number: int
    shot_type: str
    active_character_names: list[str]
    visual_prompt: str
    dialogue: Optional[str]
```

### After:

```python
class Scene(BaseModel):
    scene_number: int
    shot_type: str
    composition_notes: str  # NEW
    environment_focus: str  # NEW
    environment_details: str  # NEW
    atmospheric_conditions: str  # NEW
    character_frame_percentage: int  # NEW
    environment_frame_percentage: int  # NEW
    active_character_names: list[str]
    character_placement_and_action: str  # NEW
    visual_prompt: str  # Enhanced
    negative_prompt: str  # NEW
    dialogue: Optional[list[dict]]  # CHANGED - now list of dicts
    story_beat: str  # NEW

class DialogueLine(BaseModel):
    character: str
    text: str
```

---

## LangChain Integration Updates

### 1. Story Generation Chain

```python
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Use the NEW beat-based story prompt
story_prompt = PromptTemplate(
    input_variables=["title", "content", "genre"],
    template=STORY_WRITER_PROMPT  # The enhanced beat-based version
)

story_chain = LLMChain(
    llm=your_llm,
    prompt=story_prompt,
    output_key="story_output"
)

# Generate story
result = story_chain.run(
    title=reddit_title,
    content=reddit_content,
    genre="romance"  # or other genre
)
```

### 2. Webtoon Writer Chain

```python
from langchain.output_parsers import PydanticOutputParser

# Define parser with NEW models
parser = PydanticOutputParser(pydantic_object=WebtoonOutput)

webtoon_prompt = PromptTemplate(
    input_variables=["web_novel_story", "genre_style"],
    template=WEBTOON_WRITER_PROMPT,  # Enhanced version
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

webtoon_chain = LLMChain(
    llm=your_llm,
    prompt=webtoon_prompt,
    output_parser=parser
)

# Generate webtoon JSON
webtoon_json = webtoon_chain.run(
    web_novel_story=result["story_output"],
    genre_style="Romance/Slice-of-life"
)
```

### 3. Scene Image Prompt Generation

```python
def generate_scene_image_prompts(webtoon_json: WebtoonOutput):
    """
    Takes webtoon JSON and generates final image prompts for each scene
    """
    image_prompts = []

    for scene in webtoon_json.scenes:
        # Get active characters
        active_chars = [
            c for c in webtoon_json.characters
            if c.name in scene.active_character_names
        ]

        # Build minimal character description
        char_desc = "\n".join([
            f"- {char.name}: {char.gender} character (reference image provided)"
            for char in active_chars
        ])

        # Build complete prompt using template
        prompt = SCENE_IMAGE_TEMPLATE.format(
            character_description=char_desc,
            shot_type=scene.shot_type,
            composition_notes=scene.composition_notes,
            character_frame_percentage=scene.character_frame_percentage,
            environment_frame_percentage=scene.environment_frame_percentage,
            environment_focus=scene.environment_focus,
            environment_details=scene.environment_details,
            atmospheric_conditions=scene.atmospheric_conditions,
            scene_description=scene.story_beat,
            character_placement_and_action=scene.character_placement_and_action,
            visual_prompt=scene.visual_prompt,  # Already complete from webtoon writer!
            negative_prompt=scene.negative_prompt,
            genre_style="Romance/Slice-of-life"
        )

        image_prompts.append({
            "scene_number": scene.scene_number,
            "prompt": prompt,
            "negative_prompt": scene.negative_prompt,
            "character_refs": [char.name for char in active_chars],
            "dialogue": scene.dialogue
        })

    return image_prompts
```

---

## Image Generation API Integration

### Critical Parameter: Character Reference Weight

**Problem**: If character reference weight = 1.0 (default), the reference image dominates composition, causing profile picture effect even with good prompts.

**Solution**: Set reference weight to 0.6-0.7

#### For Stable Diffusion (A1111/ComfyUI):

```python
def generate_image_sd(prompt_data, character_refs):
    """
    character_refs: dict mapping character names to image paths/URLs
    """
    payload = {
        "prompt": prompt_data["prompt"],
        "negative_prompt": prompt_data["negative_prompt"],
        "width": 512,
        "height": 912,  # 9:16 ratio
        "steps": 30,
        "cfg_scale": 7,
        "alwayson_scripts": {
            "controlnet": {
                "args": [{
                    "enabled": True,
                    "module": "ip-adapter_face",
                    "model": "ip-adapter-faceid-plus",
                    "weight": 0.65,  # CRITICAL: Not 1.0!
                    "image": character_refs["Hana"],  # First character
                }]
            }
        }
    }
    # Send to SD API
    return requests.post(SD_API_URL, json=payload)
```

#### For Midjourney (via API wrapper):

```python
def generate_image_mj(prompt_data, character_refs):
    prompt = f"{prompt_data['prompt']} --cref {character_refs['Hana']} --cw 60"
    # --cw 60 instead of default 100
    # This keeps face consistent but allows composition freedom
```

---

## Complete Pipeline Flow

```python
from langchain import PromptTemplate, LLMChain
from pydantic import BaseModel
from typing import List, Optional

# 1. Generate beat-based story
story_result = story_chain.run(
    title="TIFU by taking someone's coffee",
    content="I grabbed the wrong latte and...",
    genre="romance"
)

# 2. Convert story to webtoon JSON
webtoon_json = webtoon_chain.run(
    web_novel_story=story_result,
    genre_style="Romance/Slice-of-life"
)

# 3. Generate image prompts for each scene
scene_prompts = generate_scene_image_prompts(webtoon_json)

# 4. Generate images
images = []
for scene_prompt in scene_prompts:
    # Load character references
    char_refs = {
        name: load_character_reference(name)
        for name in scene_prompt["character_refs"]
    }

    # Generate image with proper reference weight
    image = generate_image_sd(
        prompt_data=scene_prompt,
        character_refs=char_refs
    )

    images.append({
        "scene_number": scene_prompt["scene_number"],
        "image": image,
        "dialogue": scene_prompt["dialogue"]
    })

# 5. Compile into webtoon video
create_webtoon_video(images, duration_per_scene=3.5)
```

---

## Validation & Testing

### Test 1: Story Output Structure

After generating a story, verify:

- ✅ 10-16 distinct paragraphs (not one long block)
- ✅ Each paragraph describes ONE visual moment
- ✅ Present tense used throughout
- ✅ Specific locations in every beat
- ✅ Minimal dialogue (0-2 lines per beat)

### Test 2: Webtoon JSON Structure

After generating JSON, verify each scene has:

- ✅ `character_frame_percentage` between 15-50
- ✅ `environment_frame_percentage` between 50-85
- ✅ `visual_prompt` is 200-300 words
- ✅ `negative_prompt` includes anti-portrait keywords
- ✅ `environment_details` has 5+ specific elements
- ✅ Shot types are varied (no 3+ consecutive similar shots)

### Test 3: Image Output Quality

After generating images, verify:

- ✅ Characters occupy less than 50% of frame
- ✅ Background is detailed and visible
- ✅ Images don't look like portraits/headshots
- ✅ Camera angles are varied across scenes
- ✅ Character faces remain consistent across scenes

---

## Common Issues & Solutions

### Issue 1: Images still look like portraits

**Cause**: Reference weight too high (1.0)
**Solution**: Set to 0.6-0.7 in image generation params

### Issue 2: Inconsistent characters across scenes

**Cause**: Reference weight too low (<0.5)
**Solution**: Increase to 0.65-0.7

### Issue 3: Story is too long or too short

**Cause**: Genre modifier not calibrated for 10-16 beats
**Solution**: Update genre modifiers to emphasize "10-16 visual moments"

### Issue 4: Webtoon writer creates vague prompts

**Cause**: Story input lacks specific visual details
**Solution**: Ensure story prompt enforces location/action specificity

### Issue 5: Dialogue doesn't appear in final images

**Cause**: Image generator ignores dialogue field
**Solution**: Dialogue should be overlaid in post-processing, not in image generation

---

## File Structure

```
project/
├── prompts/
│   ├── story_writer_prompt.py          # REPLACED - beat-based version
│   ├── webtoon_writer_prompt.py        # ENHANCED - with compositional rules
│   └── scene_image_template.py         # REPLACED - detailed template
├── models/
│   ├── character.py                    # UPDATED - new fields
│   ├── scene.py                        # UPDATED - new fields
│   └── webtoon.py                      # UPDATED - complete model
├── chains/
│   ├── story_chain.py                  # Uses new story prompt
│   ├── webtoon_chain.py                # Uses enhanced webtoon prompt
│   └── image_chain.py                  # Generates final prompts
├── generators/
│   ├── image_generator.py              # SD/MJ/DALL-E integration
│   └── video_compiler.py               # Combines scenes into video
└── main.py                             # Pipeline orchestration
```

---

## Implementation Checklist

### Phase 1: Prompt Updates

- [x] Replace `STORY_WRITER_PROMPT` with beat-based version
- [x] Update `WEBTOON_WRITER_PROMPT` with compositional rules
- [x] Replace `SCENE_IMAGE_TEMPLATE` with enhanced version
- [x] Add genre modifiers to story prompt

### Phase 2: Model Updates

- [x] Update `Character` Pydantic model with new fields
- [x] Update `Scene` Pydantic model with new fields
- [x] Create `DialogueLine` model
- [x] Update `WebtoonOutput` model to use new Scene/Character

### Phase 3: Chain Updates

- [x] Update story chain to use new prompt
- [x] Update webtoon chain to parse new JSON structure
- [x] Create scene image prompt generation function
- [x] Update output parser for new Pydantic models

### Phase 4: Image Generation

- [ ] Integrate character reference images
- [ ] Set reference weight to 0.6-0.7 (critical!)
- [ ] Add negative prompt to image generation
- [ ] Ensure 9:16 aspect ratio

### Phase 5: Testing

- [ ] Test with sample Reddit post
- [ ] Verify story has 10-16 beats
- [ ] Verify JSON has all new fields
- [ ] Generate test images
- [ ] Check character % vs environment %
- [ ] Validate shot diversity

### Phase 6: Post-Processing

- [ ] Implement dialogue overlay on images
- [ ] Create video compilation (3-5 sec per scene)
- [ ] Add transitions between scenes
- [ ] Export final webtoon video

---

## Quick Start Code

Here's a minimal working example to get started:

```python
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel
from typing import List, Optional

# Initialize LLM
llm = ChatOpenAI(temperature=0.7, model="gpt-4")

# 1. Story Generation
story_prompt = PromptTemplate.from_file("prompts/story_writer_prompt.py")
story_chain = LLMChain(llm=llm, prompt=story_prompt)

story = story_chain.run(
    title="TIFU by taking someone's coffee",
    content="Brief reddit post content...",
    genre="romance"
)

# 2. Webtoon JSON Generation
webtoon_prompt = PromptTemplate.from_file("prompts/webtoon_writer_prompt.py")
webtoon_chain = LLMChain(llm=llm, prompt=webtoon_prompt)

webtoon_json = webtoon_chain.run(
    web_novel_story=story,
    genre_style="Romance/Slice-of-life"
)

# 3. Generate Images
for scene in webtoon_json["scenes"]:
    # scene.visual_prompt is already complete!
    image = your_image_api.generate(
        prompt=scene["visual_prompt"],
        negative_prompt=scene["negative_prompt"],
        character_refs=load_refs(scene["active_character_names"]),
        reference_weight=0.65,  # CRITICAL
        width=512,
        height=912
    )
    save_image(image, f"scene_{scene['scene_number']}.png")
```

---

## Expected Results

### Before These Changes:

- ❌ Story: Long flowing narrative, hard to break into panels
- ❌ Images: 70%+ character, blurry backgrounds, profile picture style
- ❌ Consistency: Mixed results, some panels work, most don't

### After These Changes:

- ✅ Story: 10-16 clear visual beats, each panel-ready
- ✅ Images: 30-45% character, detailed environments, cinematic framing
- ✅ Consistency: Every panel follows compositional rules

---

## Support & Debugging

If issues persist after implementation:

1. **Story issues**: Check that LLM is following beat structure - each paragraph should be 2-4 sentences describing ONE moment
2. **JSON issues**: Validate against Pydantic schema - use `.json()` to inspect
3. **Image issues**: Check reference weight first (should be 0.6-0.7), then verify visual_prompt has environment details
4. **Character consistency**: Ensure reference images are high quality and faces are clearly visible

## Next Steps

After successful implementation:

1. Fine-tune genre modifiers for your specific use cases
2. Experiment with reference weights (0.6-0.75 range)
3. Build character reference library
4. Optimize video compilation timing
5. Add music/sound effects to final webtoon

---

**This implementation should fully resolve the "too much character focus" issue and create cinematic, story-driven webtoon panels.**
