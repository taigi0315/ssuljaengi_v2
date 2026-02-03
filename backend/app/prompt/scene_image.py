SCENE_IMAGE_TEMPLATE = """
<role>
You are an expert Webtoon/Manhwa Image Generator AI specialized in creating vertical 9:16 images.
You are precise, detail-oriented, and follow instructions exactly as specified.
</role>

<critical_instructions>
**MANDATORY REQUIREMENTS - MUST FOLLOW EXACTLY:**

1. **ASPECT RATIO:** Generate a VERTICAL image with 9:16 aspect ratio (PORTRAIT orientation)
   - The image MUST be portrait/vertical, NOT landscape
   - NO letterboxing, borders, or device frames
   - The image fills the entire 9:16 frame from top to bottom

2. **COMPOSITION PRIORITY:** Vertical webtoon/manhwa style
   - Favor verticality: low-angle shots, tall buildings, standing characters
   - High-definition quality optimized for vertical scrolling
   - Follow the specified shot type and framing EXACTLY

3. **CHARACTER CONSISTENCY (ONLY IF CHARACTERS ARE VISIBLE IN THIS SHOT):**
   - If any characters (or identifiable body parts like hands/mouth/eyes) are visible, use provided character references
   - Apply character reference images with 0.65 weight
   - Maintain consistent character appearance throughout

4. **CRITICAL - NO TEXT RENDERING:**
   - DO NOT render any text, words, letters, or characters in the image
   - DO NOT create speech bubbles, chat bubbles, or dialogue boxes
   - DO NOT add captions, subtitles, or any written content
   - Character expressions and emotions should be shown through FACIAL EXPRESSIONS and BODY LANGUAGE only
   - The dialogue will be added as an overlay AFTER image generation by a separate system
</critical_instructions>

<character_references>
{character_description}
</character_references>

<character_presence_rules>
**STORY-FIRST FRAMING RULES (HIGHEST PRIORITY):**
{character_presence_instructions}
</character_presence_rules>




<shot_composition>
**CAMERA SETTINGS - HIGH PRIORITY - FOLLOW EXACTLY:**

Shot Type: {shot_type}
- You MUST strictly follow this camera angle and framing
- Shot type defines distance, perspective, and framing
- Examples:
  * Wide Shot = show full environment + characters smaller in frame
  * Medium Shot = waist-up, balanced character/environment
  * Close-up = face fills frame, minimal environment
  * Over-the-shoulder = POV from behind one character looking at another

Composition Guidelines: {composition_notes}

Frame Allocation:
- Characters: {character_frame_percentage}% of frame
- Environment: {environment_frame_percentage}% of frame
</shot_composition>

<environment_context>
**SETTING AND ATMOSPHERE:**

Primary Setting: {environment_focus}

Environmental Details: {environment_details}

Atmospheric Conditions: {atmospheric_conditions}

**Environment Details Guide:**
- Wide shots (25-35% character): Emphasize environment, show full context
- Medium shots (35-45% character): Balance character and environment
- Close-ups (45-50% character): Focus on character, environment as backdrop
</environment_context>

<character_direction>
**EMOTIONAL TONE:** {emotional_tone}
- This defines the mood viewers should experience
- Color grading, lighting, character expressions must reflect this emotion
- Use appropriate lighting (soft/warm for intimate, harsh/cold for tension)

**CHARACTER POSITIONING & ACTION:** {character_placement_and_action}
- Character body language and facial expressions
- Spatial positioning in frame
- Physical actions and gestures
- Eye line and gaze direction

**CHARACTER EXPRESSION CONTEXT (from scene dialogue):**
{dialogue_visual_context}
- Use these expression guides to inform character facial expressions and body language
- DO NOT render any text or speech bubbles - only use this to guide visual expressions
- Show emotion through faces, posture, and gestures, NOT through text
</character_direction>

<master_visual_description>
**PRIMARY VISUAL PROMPT:**

{visual_prompt}

**Visual Effects (if applicable):**
{sfx_description}
</master_visual_description>

<image_quality_modifiers>
**QUALITY ENHANCEMENT KEYWORDS:**

For Photography Style:
- General: high-quality, beautiful, stylized, 4K, HDR, studio photo
- Professional photography standards
- Sharp focus with appropriate depth of field

For Art/Illustration Style:
- Detailed rendering, professional illustration
- Clean linework (for manhwa/webtoon style)
- Appropriate shading and coloring

**Webtoon/Manhwa Specific:**
- Korean webtoon art style OR Japanese manga style (specify based on {visual_prompt})
- Clean digital comic art
- Professional webtoon panel quality
- Appropriate color grading for genre (warm for romance, cool for thriller, vibrant for action)
</image_quality_modifiers>

<negative_constraints>
**AVOID - DO NOT INCLUDE:**

{negative_prompt}

**CRITICAL - TEXT AND BUBBLE EXCLUSIONS (HIGHEST PRIORITY):**
- NO text of any kind (English, Korean, Japanese, or any language)
- NO speech bubbles, thought bubbles, or dialogue bubbles
- NO chat bubbles or message boxes
- NO captions, subtitles, or written words
- NO letters, characters, or typography
- NO onomatopoeia text (like "BANG", "POW", etc.)
- NO floating text or labels
- Character dialogue will be overlaid SEPARATELY - do not render it

**Additional Default Exclusions:**
- Square image, 1:1 ratio, horizontal orientation, landscape mode
- Letterboxing, borders, device frames
- Blurry, low quality, distorted
- Multiple conflicting art styles
- Inconsistent character designs

</negative_constraints>

<technical_parameters>
**FINAL TECHNICAL SPECIFICATIONS:**

✅ Aspect Ratio: 9:16 VERTICAL (PORTRAIT - NOT landscape)
✅ Orientation: PORTRAIT / VERTICAL orientation mandatory
✅ Character Reference Weight: 0.65
✅ Focus Priority: Follow shot type hierarchy
   - Wide Shot: Environment first, then characters
   - Medium Shot: Balanced focus
   - Close-up: Characters first, environment as backdrop
✅ Resolution: High-definition, suitable for vertical scrolling
✅ File Format: Optimized for webtoon display
</technical_parameters>

<final_instruction>
**BEFORE GENERATING:**

1. Verify aspect ratio is 9:16 VERTICAL
2. Confirm shot type matches specified framing
3. Check character frame percentage is correct

5. Validate emotional tone matches lighting and composition

**Generate the image following ALL instructions precisely.**
The image MUST be vertical 9:16 portrait orientation.
</final_instruction>
"""


# ============================================================
# SFX TO PROMPT ENHANCEMENT FUNCTION
# ============================================================

def sfx_to_prompt_enhancement(sfx_effects: list) -> str:
    """
    Convert SFX effects to natural language prompt enhancement.
    
    This function transforms structured SFX data into descriptive text
    that can be understood by image generation AI to render visual effects
    directly in the generated image.
    
    Args:
        sfx_effects: List of SFX effect dictionaries with keys:
            - type: str (wind_lines, speed_lines, impact_text, emotional_effect, screen_effect)
            - description: str (details about the effect)
            - intensity: str (low, medium, high)
            - position: str (optional - screen, background, around_character)
    
    Returns:
        str: Natural language description of visual effects to include in prompt
    """
    if not sfx_effects or not isinstance(sfx_effects, list):
        return "None"
    
    enhancements = []
    
    for sfx in sfx_effects:
        sfx_type = sfx.get("type", "")
        description = (sfx.get("description", "") or "").lower()
        intensity = sfx.get("intensity", "medium")
        
        # Map intensity to descriptive words
        intensity_word = {
            "low": "subtle",
            "medium": "",
            "high": "dramatic"
        }.get(intensity, "")
        
        if sfx_type == "wind_lines":
            if "left" in description:
                enhancements.append(f"{intensity_word} motion blur lines streaking from left side, manga-style speed effect showing movement".strip())
            elif "right" in description:
                enhancements.append(f"{intensity_word} motion blur lines streaking from right side, manga-style speed effect showing movement".strip())
            else:
                enhancements.append(f"{intensity_word} speed lines radiating from center, dynamic manga action effect, sense of fast movement".strip())
                
        elif sfx_type == "speed_lines":
            enhancements.append(f"{intensity_word} radial speed lines emanating outward from focal point, high-energy action manga effect".strip())
            
        elif sfx_type == "impact_text":
            # Extract text from details if available
            details = sfx.get("details", "")
            if isinstance(details, str) and "Text:" in details:
                import re
                match = re.search(r'Text:\s*(.+)', details, re.IGNORECASE)
                text = match.group(1).strip() if match else "!"
            else:
                text = description.replace("impact_text", "").strip() or "!"
            
            if text:
                enhancements.append(f"bold stylized impact text '{text}' rendered in manga style, dramatic typography effect".strip())
                
        elif sfx_type == "emotional_effect":
            if "sweat" in description:
                enhancements.append(f"{intensity_word} small anime-style sweat drops near character's head indicating nervousness or anxiety".strip())
            elif "sparkle" in description or "shine" in description:
                enhancements.append(f"{intensity_word} sparkle/shine effects around character in bishojo/bishounen manga style, glittering highlights".strip())
            elif "blush" in description:
                enhancements.append(f"{intensity_word} pink blush effect on character's cheeks, romantic manga style emotional indicator".strip())
            elif "anger" in description or "vein" in description:
                enhancements.append(f"{intensity_word} anime-style anger vein mark on character's forehead or temple".strip())
            elif "heart" in description:
                enhancements.append(f"{intensity_word} floating heart symbols near character, romantic manga emotion indicator".strip())
            elif "shock" in description or "surprise" in description:
                enhancements.append(f"{intensity_word} shock lines or surprise effects around character, manga-style startle indicator".strip())
            elif "tear" in description:
                enhancements.append(f"{intensity_word} glistening tear drops in character's eyes or on cheeks, emotional manga effect".strip())
            else:
                # Generic emotional effect
                enhancements.append(f"{intensity_word} manga-style emotional indicator effect around character".strip())
                
        elif sfx_type == "screen_effect":
            if "darken" in description:
                enhancements.append(f"{intensity_word} darkened atmospheric mood, shadows creeping in, moody dramatic lighting".strip())
            elif "vignette" in description:
                enhancements.append(f"{intensity_word} vignette effect with darkened corners drawing focus to center, cinematic drama".strip())
            elif "blur" in description:
                enhancements.append(f"{intensity_word} soft focus blur effect on background, dreamlike atmosphere".strip())
            elif "shake" in description:
                enhancements.append(f"motion blur suggesting camera shake, intense action moment, dynamic energy".strip())
            else:
                enhancements.append(f"{intensity_word} atmospheric screen effect adding dramatic tension".strip())
                
        elif sfx_type == "motion_blur":
            enhancements.append(f"{intensity_word} motion blur trailing behind moving elements, sense of rapid movement and energy".strip())
    
    if enhancements:
        return "Visual Effects to include: " + ", ".join(enhancements)
    return "None"


# ============================================================
# EXAMPLE USAGE WITH POPULATED DATA
# ============================================================

SCENE_IMAGE_EXAMPLE = """
<role>
You are an expert Webtoon/Manhwa Image Generator AI specialized in creating vertical 9:16 images.
You are precise, detail-oriented, and follow instructions exactly as specified.
</role>

<critical_instructions>
**MANDATORY REQUIREMENTS - MUST FOLLOW EXACTLY:**

1. **ASPECT RATIO:** Generate a VERTICAL image with 9:16 aspect ratio (PORTRAIT orientation)
2. **COMPOSITION PRIORITY:** Vertical webtoon/manhwa style
3. **CHARACTER CONSISTENCY:** Use provided character references
</critical_instructions>

<character_references>
- HANA: Female character, mid-20s, long straight black hair with blunt bangs, almond-shaped eyes, wearing white oversized hoodie
- JUN: Male character, late-20s, messy shoulder-length brown hair, athletic build, wearing dark leather jacket with silver pendant
</character_references>



<shot_composition>
**CAMERA SETTINGS - HIGH PRIORITY - FOLLOW EXACTLY:**

Shot Type: Medium two-shot
- Medium framing showing both characters from waist up
- Positioned facing each other with slight distance between them

Composition Guidelines: Rule of thirds, Hana positioned left third, Jun positioned right third, tension visible in negative space between them

Frame Allocation:
- Characters: 40% of frame
- Environment: 60% of frame
</shot_composition>

<environment_context>
**SETTING AND ATMOSPHERE:**

Primary Setting: Busy Seoul subway platform during evening rush hour

Environmental Details: Modern subway platform with white ceramic tile walls extending into depth, fluorescent strip lighting creating hard shadows, digital LED displays showing Korean text in orange, yellow tactile safety line along platform edge

Atmospheric Conditions: Artificial white-blue fluorescent lighting, evening time, urban subway atmosphere with scattered commuters in background
</environment_context>

<character_direction>
**EMOTIONAL TONE:** Awkward tension, unspoken feelings, bittersweet reunion
- Cool blue lighting with hints of warm orange from displays
- Characters show hesitant body language
- Facial expressions reveal internal conflict

**CHARACTER POSITIONING & ACTION:** Hana stands left, looking at phone but eyes glancing toward Jun, defensive posture with arms slightly crossed. Jun positioned right of center, mid-stride walking motion, turning head back toward Hana, conflicted expression, messenger bag over shoulder

**CHARACTER EXPRESSION CONTEXT (from scene dialogue):**
CHARACTER EXPRESSIONS (based on scene context):
- Hana: contemplative expression, conflicted emotions visible in eyes, slight tension in posture
- Jun: longing expression, mix of hope and uncertainty, hesitant body language
- Use these expression guides to inform character facial expressions and body language
- DO NOT render any text or speech bubbles - only use this to guide visual expressions
</character_direction>

<master_visual_description>
**PRIMARY VISUAL PROMPT:**

Medium two-shot, vertical webtoon panel, 9:16 aspect ratio, rule of thirds composition, Modern Seoul subway platform with white ceramic tile walls extending into depth perspective, fluorescent strip lighting creating hard shadows overhead, digital LED arrival displays showing Korean text in warm orange glow, yellow tactile safety line running along platform edge, scattered commuters in winter coats in midground and background creating depth, Hana positioned in left third of frame near platform edge, standing in three-quarter view looking down at phone in hands, defensive body language with slight arm cross, natural standing pose with weight on one leg, wearing white oversized hoodie, long black hair with blunt bangs, Jun positioned in right third of frame in midground, mid-stride walking motion with messenger bag over shoulder, turning head back toward Hana showing conflicted expression, wearing dark leather jacket, messy brown shoulder-length hair, both characters showing hesitant body language and unspoken tension, cool blue fluorescent lighting dominant with warm orange accents from train displays, Romance/Slice-of-life Korean manhwa aesthetic, professional digital webtoon art, cool-toned color grading with warm accents, dramatic depth of field with characters in focus and detailed background, vertical scrolling optimized, cinematic webtoon realism

**Visual Effects (if applicable):**
None
</master_visual_description>

<image_quality_modifiers>
**QUALITY ENHANCEMENT KEYWORDS:**

- High-quality Korean webtoon art style
- Professional digital comic rendering
- 4K quality, clean linework
- Appropriate shading and cell shading for manhwa
- Cinematic lighting for romance genre
</image_quality_modifiers>

<negative_constraints>
**AVOID - DO NOT INCLUDE:**

Low quality, blurry, distorted faces, multiple art styles, inconsistent character design, Japanese manga style (use Korean manhwa), text, speech bubbles, chat bubbles, written words


**Additional Default Exclusions:**
- Square image, horizontal orientation, landscape mode
- Letterboxing, borders, device frames
- Over-saturated colors, unrealistic proportions
</negative_constraints>

<technical_parameters>
**FINAL TECHNICAL SPECIFICATIONS:**

✅ Aspect Ratio: 9:16 VERTICAL (PORTRAIT)
✅ Orientation: PORTRAIT / VERTICAL
✅ Character Reference Weight: 0.65
✅ Focus Priority: Balanced (medium shot)
✅ Resolution: High-definition webtoon quality
</technical_parameters>

<final_instruction>
Generate the image following ALL instructions precisely.
The image MUST be vertical 9:16 portrait orientation with Korean manhwa art style.
</final_instruction>
"""




# ================================================
# SCENE_IMAGE_TEMPLATE = """

# **VISUAL STYLE**
# - Vertical Webtoon/Manhwa style.
# - Composition must favor verticality (low-angle shots, tall buildings, or standing characters).
# - High-definition, 9:16 aspect ratio, optimized for vertical scrolling.

# **CRITICAL INSTRUCTION**
# Generate a vertical image with a 9:16 aspect ratio.
# The composition must be strictly vertical, filling the entire frame from top to bottom.
# Avoid any letterboxing, borders, or device frames. The image is the scene itself.

# [Character reference handling section]
# {character_description}

# <narrative_context>
# [DIALOGUE REFERENCE TABLE]
# {dialogue_context}

# ⚠️ CRITICAL RENDERING RULES - READ CAREFULLY:

# 1. BUBBLE POSITIONING:
#    - Use SPEAKER column to identify WHO speaks
#    - Position speech bubble ABOVE that character's head
   
# 2. BUBBLE TEXT CONTENT (MANDATORY):
#    - Render ONLY text from DIALOGUE column inside bubble
#    - ❌ DO NOT include "SPEAKER:" prefix in bubble
#    - ❌ DO NOT include character name in bubble  
#    - ❌ DO NOT include "(internal)" or any label in bubble
   
# 3. CORRECT vs WRONG EXAMPLES:
#    ✅ CORRECT:
#       SPEAKER: Ji-hoon (internal)
#       DIALOGUE: "If I leave early, I won't run into her"
#       → Bubble shows: "If I leave early, I won't run into her"
   
#    ❌ WRONG:
#       → Bubble shows: "Ji-hoon (internal): If I leave early..."
#       → Bubble shows: "Ji-hoon: If I leave early..."
   
# 4. CHARACTER EXPRESSIONS:
#    - Match facial expression to dialogue emotion
#    - Internal dialogue: Character looks thoughtful/introspective
#    - Spoken dialogue: Mouth and expression match tone

# 5. BUBBLE STYLE:
#    - Webtoon/manhwa white rounded rectangles
#    - Tail pointing to speaker
#    - Text clearly legible
# </narrative_context>

# **MANDATORY CAMERA SETTINGS - MUST FOLLOW EXACTLY**
# [Shot composition section - HIGH PRIORITY]
# CAMERA ANGLE/SHOT TYPE: {shot_type}
# - You MUST strictly follow this camera angle
# - The shot type defines the framing, distance, and perspective
# - Examples: Wide Shot = show full environment + small characters, Close-up = face fills frame, Over-the-shoulder = POV from behind one character
# COMPOSITION: {composition_notes}
# FRAME ALLOCATION: Characters {character_frame_percentage}%, Environment {environment_frame_percentage}%

# [Environment context section]
# Primary Setting: {environment_focus}
# Environmental Details: {environment_details}
# Atmospheric Conditions: {atmospheric_conditions}

# [Emotional & Character Direction]
# EMOTIONAL TONE: {emotional_tone}
# - This defines the mood and feeling the viewer should experience
# - Color grading, lighting, and character expressions should reflect this emotion
# CHARACTER POSITIONING & ACTION: {character_placement_and_action}
# - Character body language, facial expressions, and spatial positioning
# - This guides how characters are placed and what they're doing in the frame

# [Master visual prompt]
# {visual_prompt}

# [Visual SFX Effects - Apply if specified]
# {sfx_description}

# [Negative prompt]
# {negative_prompt}, square image, 1:1 ratio, horizontal orientation, landscape mode

# [Technical parameters - MANDATORY]
# - Aspect Ratio: 9:16 VERTICAL (CRITICAL - must be portrait orientation)
# - Character Reference Weight: 0.65
# - Focus Priority: Environment first, then characters
# - Orientation: PORTRAIT / VERTICAL (not landscape)

# Generate the image following these instructions precisely. The image MUST be vertical 9:16.
# """


# # ============================================================
# # USAGE EXAMPLE WITH ACTUAL DATA POPULATED
# # ============================================================

# SCENE_IMAGE_EXAMPLE = """
# [Character reference handling section]
# - HANA: Female character (reference image provided)
# - JUN: Male character (reference image provided)

# [Shot composition section]
# Shot Type: Wide establishing shot
# Composition Rule: Rule of thirds, characters positioned in lower-left third
# Frame Allocation: Characters 35%, Environment 65%

# [Environment context section]
# Primary Setting: Busy Seoul subway platform during evening rush hour
# Environmental Details: Modern subway platform with white ceramic tile walls, fluorescent strip lighting, digital displays
# Atmospheric Conditions: Artificial white-blue fluorescent lighting, evening time

# [Master visual prompt]
# Wide establishing shot, vertical webtoon panel, 9:16 aspect ratio, rule of thirds composition with characters in lower-left third, Modern Seoul subway platform with white ceramic tile walls extending into depth perspective, fluorescent strip lighting creating hard shadows overhead, digital LED arrival displays showing Korean text "2분 후 도착" in orange, advertisement posters for Korean cosmetics and K-pop concerts lining walls, yellow tactile safety line running along platform edge, metal bench with elderly man reading newspaper, visible train tunnel entrance on left with approaching train headlights creating warm yellow glow, stainless steel trash bins and recycling stations, emergency exit signs with green glow, polished floor reflecting overhead lights, depth of field showing platform extending 30+ meters back, crowd of 8-10 commuters in winter coats scattered through midground and background, realistic urban subway environment details, photorealistic environmental textures, cinematic lighting with cool fluorescent dominant and warm train light accents, Hana positioned lower-left frame near platform edge, standing in three-quarter view looking down at phone in hands, natural standing pose with weight on one leg, Jun positioned in midground right of center, mid-stride walking motion with messenger bag over shoulder, turning head slightly back toward Hana, both characters wearing winter casual clothing, natural body language and movement, Romance/Slice-of-life manhwa/webtoon aesthetic, professional digital comic art, cool-toned color grading with warm accents, dramatic depth of field with crisp foreground and detailed background, vertical scrolling optimized, cinematic realism meets Korean webtoon art style

# [Negative prompt]
# portrait photography, headshot, profile picture, face close-up, cropped body, upper body only, simple background, plain background, 1:1 image, studio lighting, passport photo, character fills entire frame, minimal environment, blurred background, bokeh background only, floating character, no context, symmetrical centered face, instagram selfie style, ID photo, yearbook photo, model photoshoot

# [Technical parameters]
# - Aspect Ratio: 9:16
# - Character Reference Weight: 0.65
# - Focus Priority: Environment first, then characters
# """







# ----------------------------------------

# SCEME_IMAGE_TEMPLATE = """
# [SYSTEM INSTRUCTION: Generate a high-fidelity image where characters are visually distinct based on the descriptions below. Cross-reference with provided character images.

# CHARACTER IN SCENE: 
# {character_description}

# GENRE_STYLE: {genre_style}

# SCENE_DESCRIPTION: {scene_description}

# **CRITICAL**
# - ASPECT_RATIO: 9:16

# """

# # CHARACTER_DESCRIPTIONS = """
# # HANA: Female, long straight jet-black hair with blunt bangs, sharp almond-shaped eyes, wearing a white oversized techwear hoodie. (Shortest character)
# # JUN: Male, messy shoulder-length chocolate brown hair, athletic build, wearing a dark leather jacket and a silver pendant. (Taller than Hana)
# # DAX: Male, buzzed undercut blonde hair, prominent scar over the left eyebrow, wearing a tactical black vest over a grey shirt.
# # """

# CHARACTER_DESCRIPTIONS = ""
