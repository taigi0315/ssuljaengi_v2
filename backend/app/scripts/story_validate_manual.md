# Webtoon Generation Debugging Guide

## Your Current Issues

Based on your output, you have:

- ❌ Only 4 scenes (need 8-12)
- ❌ Only 1 dialogue (panel 1 only)
- ❌ Scene 4 has broken `visual_prompt`: "Medium Shot of A teenage boy with messy black hair..." (this is just character description, not a scene)
- ❌ Story doesn't progress - it's all setup, no development or resolution

---

## Root Cause Analysis

### Issue 1: Story Generation is Still Prose-Style

**What you probably have:**

```
Story output = Long flowing narrative (1000-2000 words)

Example:
"Ji-hoon stood on the bridge at dusk, thinking about how he wished he could
go back in time. He remembered high school in 2010, the bustling hallways
where he used to watch Soojin from afar. She would laugh with her friends
near the notice board, her hair illuminated by sunlight..."
```

**What you need:**

```
Story output = 8-16 paragraph beats

Example:
Paragraph 1: "The Han River bridge at dusk. Ji-hoon stands alone, clutching
a photograph."

Paragraph 2: "High school hallway, 2010. Teenage Ji-hoon navigates the crowd,
looking overwhelmed."

Paragraph 3: "Soojin laughs with friends near the notice board. Ji-hoon watches
from afar."
```

**How to check:**

```python
from story_validator import validate_story_for_webtoon

story_text = your_llm_story_output
results = validate_story_for_webtoon(story_text)

# Should show:
# ✅ 8-16 paragraphs
# ✅ Each paragraph = one moment
# ✅ Present tense
# ✅ Specific locations
```

---

### Issue 2: Webtoon Writer Receiving Poor Input

When the webtoon writer receives prose-style story, it:

1. Struggles to find distinct visual moments → creates only 4 vague scenes
2. Can't extract dialogue → most scenes are silent
3. Generates incomplete prompts → Scene 4 breakdown shows this

**The fix:**

- Use the **revised story prompt** (beat-based)
- Validate story output BEFORE sending to webtoon writer

---

## Expected Output Comparison

### ❌ WHAT YOU'RE GETTING (BAD)

```json
{
  "scenes": [
    {
      "panel_number": 1,
      "dialogue": [{"character": "Ji-hoon", "text": "If only I could go back..."}]
    },
    {
      "panel_number": 2,
      "dialogue": null  // ❌ No dialogue
    },
    {
      "panel_number": 3,
      "dialogue": null  // ❌ No dialogue
    },
    {
      "panel_number": 4,
      "visual_prompt": "Medium Shot of A teenage boy..."  // ❌ BROKEN!
      "dialogue": null
    }
  ]
}
```

**Problems:**

- Only 4 scenes
- 3 of 4 scenes have no dialogue
- Scene 4 is completely broken
- No story progression (all setup, no payoff)

---

### ✅ WHAT YOU SHOULD GET (GOOD)

```json
{
  "characters": [
    {
      "name": "Ji-hoon",
      "reference_tag": "Ji-hoon(20s, melancholic)",
      "appearance_notes": "Disheveled black hair, tired eyes, lean build"
    },
    {
      "name": "Ji-hoon-teen",
      "reference_tag": "Ji-hoon-teen(17, awkward)",
      "appearance_notes": "Messy black hair, shy eyes, lanky"
    },
    {
      "name": "Soojin",
      "reference_tag": "Soojin(20s, gentle)",
      "appearance_notes": "Long dark hair, warm eyes, freckles"
    }
  ],
  "scenes": [
    {
      "panel_number": 1,
      "shot_type": "Extreme Wide Shot / Establishing Shot",
      "visual_prompt": "Extreme wide shot, vertical 9:16 panel, Han River bridge at dusk with illuminated structure stretching across frame, Seoul skyline with glowing buildings in distance, orange and purple sky reflecting on water below, scattered traffic lights on bridge, faint mist rising from river, Ji-hoon(20s, melancholic) standing small in center of bridge clutching photograph, looking out at cityscape, dramatic dusk lighting, calm melancholic atmosphere, romance/drama manhwa style, cinematic depth",
      "dialogue": [
        {
          "character": "Ji-hoon",
          "text": "If only I could go back...",
          "order": 1
        }
      ],
      "character_frame_percentage": 20,
      "environment_frame_percentage": 80
    },
    {
      "panel_number": 2,
      "shot_type": "Wide Shot",
      "visual_prompt": "Wide shot, vertical 9:16 panel, bustling high school hallway in 2010 with rows of green metal lockers, notice boards covered in colorful flyers, fluorescent ceiling lights, vinyl floor tiles, groups of students in uniforms walking and talking, windows showing sunny day outside, Ji-hoon-teen(17, awkward) navigating crowded hallway positioned left third bumping into other students, looking overwhelmed with hunched shoulders, bright daylight through windows, energetic noisy atmosphere, nostalgia filter, slice-of-life manhwa style",
      "dialogue": null,
      "character_frame_percentage": 30,
      "environment_frame_percentage": 70
    },
    {
      "panel_number": 3,
      "shot_type": "Medium Shot",
      "visual_prompt": "Medium shot, vertical 9:16 panel, high school hallway corner near notice board covered in club posters and announcements, green lockers with stickers, sunlight streaming through large windows creating light pools on floor, dust motes visible in sunbeam, Soojin(17, cheerful) positioned center-right laughing with three friends in school uniforms, hair catching sunlight with golden glow, Ji-hoon-teen(17, awkward) in background left watching from distance behind other students, hesitant posture, warm afternoon lighting, youthful bright atmosphere, romance manhwa style",
      "dialogue": null,
      "character_frame_percentage": 40,
      "environment_frame_percentage": 60
    },
    {
      "panel_number": 4,
      "shot_type": "Medium Shot",
      "visual_prompt": "Medium shot, vertical 9:16 panel, school cafeteria with rows of tables and orange plastic chairs, students eating and chatting in background, vending machines against far wall, large windows showing schoolyard, food trays and drink cups on tables, Ji-hoon-teen(17, awkward) sitting alone at corner table positioned left third hunched over sketchbook drawing, Min(17, energetic) sitting beside him leaning in with encouraging expression, fluorescent lighting mixing with window daylight, busy lunch atmosphere, slice-of-life manhwa style",
      "dialogue": [
        {
          "character": "Min",
          "text": "Just go talk to her already!",
          "order": 1
        },
        {
          "character": "Ji-hoon-teen",
          "text": "I... I can't.",
          "order": 2
        }
      ],
      "character_frame_percentage": 40,
      "environment_frame_percentage": 60
    },
    {
      "panel_number": 5,
      "shot_type": "Medium Close-Up",
      "visual_prompt": "Medium close-up, vertical 9:16 panel, cafeteria table surface with sketchbook, pencils, and food tray visible, other students blurred in background, Soojin(17, cheerful) standing at table positioned right third holding folded paper crane with gentle smile, Ji-hoon-teen(17, awkward) visible from shoulders up left third looking up with surprised wide-eyed expression from his sketchbook, soft afternoon light from nearby window, intimate moment in crowded space, romance manhwa style, shallow depth of field",
      "dialogue": [
        {
          "character": "Soojin",
          "text": "You dropped this.",
          "order": 1
        },
        {
          "character": "Ji-hoon-teen",
          "text": "I... I didn't—",
          "order": 2
        },
        {
          "character": "Soojin",
          "text": "I know. I made it for you.",
          "order": 3
        }
      ],
      "character_frame_percentage": 45,
      "environment_frame_percentage": 55
    },
    {
      "panel_number": 6,
      "shot_type": "Two-Shot",
      "visual_prompt": "Two-shot medium composition, vertical 9:16 panel, cafeteria table between them with paper crane in foreground, Ji-hoon-teen(17, awkward) left side of frame blushing taking crane with trembling hands, Soojin(17, cheerful) right side sitting down across from him with warm encouraging smile, cafeteria background with other students eating and talking, afternoon sunlight creating warm atmosphere, orange and yellow color palette, romantic tension, manhwa style with soft glow",
      "dialogue": [
        {
          "character": "Ji-hoon-teen",
          "text": "Why?",
          "order": 1
        },
        {
          "character": "Soojin",
          "text": "You're always alone. Thought you could use a friend.",
          "order": 2
        }
      ],
      "character_frame_percentage": 45,
      "environment_frame_percentage": 55
    },
    {
      "panel_number": 7,
      "shot_type": "Medium Shot",
      "visual_prompt": "Medium shot, vertical 9:16 panel, same cafeteria table now with fewer students in background, half-empty cafeteria suggesting time passing, Ji-hoon-teen(17, awkward) showing sketchbook pages to Soojin(17, cheerful) both leaning over table, her eyes wide with amazement, his nervous excited expression, papers and pencils scattered on table, warm late afternoon golden light through windows, intimate conversation atmosphere, slice-of-life manhwa style",
      "dialogue": [
        {
          "character": "Soojin",
          "text": "These are amazing! You should show people.",
          "order": 1
        },
        {
          "character": "Ji-hoon-teen",
          "text": "I'm not good enough...",
          "order": 2
        },
        {
          "character": "Soojin",
          "text": "Yes, you are.",
          "order": 3
        }
      ],
      "character_frame_percentage": 40,
      "environment_frame_percentage": 60
    },
    {
      "panel_number": 8,
      "shot_type": "Wide Shot",
      "visual_prompt": "Wide shot, vertical 9:16 panel, school rooftop at sunset with metal fence, air conditioning units, distant Seoul cityscape, orange and pink sky, Ji-hoon-teen(17, awkward) and Soojin(17, cheerful) standing by fence positioned in lower third of frame looking out at city view together, gentle breeze moving their hair and uniforms, golden hour lighting creating long shadows, peaceful hopeful atmosphere, romance manhwa style, cinematic composition",
      "dialogue": [
        {
          "character": "Ji-hoon-teen",
          "text": "Thanks for today.",
          "order": 1
        },
        {
          "character": "Soojin",
          "text": "Let's do this again tomorrow?",
          "order": 2
        }
      ],
      "character_frame_percentage": 30,
      "environment_frame_percentage": 70
    },
    {
      "panel_number": 9,
      "shot_type": "Close-Up",
      "visual_prompt": "Close-up, vertical 9:16 panel, Ji-hoon(20s, melancholic) hands in foreground holding old photograph showing younger him and Soojin on rooftop, bridge railing visible in midground, blurred city lights in background, dusk lighting with cool blue tones, photograph in warm nostalgic sepia, emotional contrast between past and present, drama manhwa style",
      "dialogue": [
        {
          "character": "Ji-hoon",
          "text": "If only I'd kept that promise...",
          "order": 1
        }
      ],
      "character_frame_percentage": 50,
      "environment_frame_percentage": 50
    },
    {
      "panel_number": 10,
      "shot_type": "Medium Close-Up",
      "visual_prompt": "Medium close-up, vertical 9:16 panel, Ji-hoon(20s, melancholic) from chest up positioned center-right on bridge, looking down at glowing phone screen in hands showing message notification, city lights bokeh in background, cool evening blue lighting on face with warm phone screen glow creating contrast, surprised hopeful expression dawning on face, romantic atmosphere, drama manhwa style, emotional turning point",
      "dialogue": null,
      "character_frame_percentage": 45,
      "environment_frame_percentage": 55
    },
    {
      "panel_number": 11,
      "shot_type": "Extreme Close-Up",
      "visual_prompt": "Extreme close-up, vertical 9:16 panel, phone screen in sharp focus showing text message 'Same bridge, same time tomorrow? - Soojin', Ji-hoon(20s, melancholic) blurred face visible in background with widening eyes showing shock and hope, blue phone screen light illuminating his features, dark evening background, intimate moment of realization, romance drama manhwa style",
      "dialogue": null,
      "character_frame_percentage": 40,
      "environment_frame_percentage": 60
    },
    {
      "panel_number": 12,
      "shot_type": "Wide Shot",
      "visual_prompt": "Wide shot, vertical 9:16 panel, Han River bridge at night with city lights twinkling in background, same composition as opening but now with hopeful atmosphere, Ji-hoon(20s, melancholic but hopeful) positioned center looking up from phone toward city with slight smile beginning to form, clutching photograph and phone, night sky with stars appearing, bridge lights glowing warm yellow, sense of new beginning and hope, romance drama manhwa style, circular narrative closure",
      "dialogue": [
        {
          "character": "Ji-hoon",
          "text": "Maybe... it's not too late.",
          "order": 1
        }
      ],
      "character_frame_percentage": 25,
      "environment_frame_percentage": 75
    }
  ],
  "episode_summary": "Ji-hoon stands on a bridge reflecting on his high school past, when he was too shy to fully connect with Soojin despite their budding friendship. Just as regret overwhelms him, he receives an unexpected message from Soojin, offering a second chance at the connection he thought he'd lost."
}
```

**Why this works:**

- ✅ 12 scenes (perfect for 36-60 second video)
- ✅ 7 scenes have dialogue (58% dialogue-driven)
- ✅ Clear 3-act structure:
  - Act 1 (1-3): Setup - bridge, flashback to school
  - Act 2 (4-8): Development - meeting Soojin, connection forms
  - Act 3 (9-12): Resolution - regret, surprise message, hope
- ✅ All visual_prompts are complete 150-250 word descriptions
- ✅ Multiple dialogues per scene showing conversations
- ✅ Shot variety (wide, medium, close-up, extreme close-up, two-shot)
- ✅ Emotional progression from melancholy → hope

---

## Action Items for You

### 1. Validate Your Story Output

Run your story through the validator:

```python
from story_validator import validate_story_for_webtoon, print_validation_report

# Get your story output
story = your_story_chain.run(...)

# Validate
results = validate_story_for_webtoon(story)
print_validation_report(results)

# Should see:
# ✅ 8-16 paragraphs
# ✅ Beat-based structure
# ✅ 60%+ paragraphs with dialogue
```

**If validation fails:**

- Your story prompt is still the old prose-style version
- Replace with the new beat-based story prompt

### 2. Update Webtoon Writer Prompt

Replace with the new fixed version that:

- **Forces 8-12 scenes minimum**
- **Enforces dialogue in 60%+ of scenes**
- **Validates complete visual_prompts (not broken "Medium Shot of..." garbage)**
- **Supports multiple dialogue lines per scene** (your great idea!)

### 3. Test with Simple Input

Try this minimal test:

**Reddit Input:**

```
Title: Coffee Shop Mistake
Content: I accidentally took someone's coffee and our hands touched.
We laughed and ended up talking. Got their number but too nervous to text.
```

**Expected Output:**

- 8-12 scenes
- Opening: Coffee shop establishing
- Development: Hand touch, awkward conversation, number exchange
- Resolution: Contemplating whether to text, hopeful ending
- 6+ scenes should have dialogue

### 4. Check Visual Prompt Completeness

Every scene's `visual_prompt` should be 150-250 words and follow the formula:

```
{shot_type}, vertical 9:16, {composition}, {5+ environment elements},
{character placement + action}, {lighting/atmosphere}, {style}
```

**If you see:**

```json
"visual_prompt": "Medium Shot of characters talking"
```

That's BROKEN. Should be:

```json
"visual_prompt": "Medium shot, vertical 9:16 panel, cozy coffee shop interior with exposed brick walls, hanging Edison lights, wooden counter with espresso machine, potted plants on windowsill, afternoon sunlight through large windows, Person A(20s) sitting at small table left third looking down at coffee cup with nervous expression, Person B(20s) standing right approaching with gentle smile holding phone, warm amber interior lighting, intimate atmosphere, romance manhwa style, shallow depth of field"
```

---

## Quick Fix Checklist

- [ ] Validate story output is beat-based (8-16 paragraphs)
- [ ] Update webtoon writer prompt to force 8-12 scenes
- [ ] Ensure dialogue appears in 60%+ of scenes
- [ ] Verify visual_prompts are complete (not broken)
- [ ] Test with simple Reddit post
- [ ] Check output has clear beginning → middle → end

---

## Expected Timeline

With the fixed prompts:

- **Story generation:** 8-16 beat paragraphs with dialogue
- **Webtoon conversion:** 8-12 complete scenes with full prompts
- **Image generation:** Each scene becomes one image with sequential dialogue
- **Final video:** 30-50 seconds (3-5 sec per scene × 10 scenes average)

---

## Still Having Issues?

Share:

1. Your **actual story output** (first 3-4 paragraphs)
2. Your **webtoon JSON** (first 2 scenes)
3. Any **error messages**

I can diagnose exactly where the pipeline is breaking!
