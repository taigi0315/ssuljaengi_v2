SCENE_IMAGE_TEMPLATE = """

**VISUAL STYLE**
- Vertical Webtoon/Manhwa style.
- Composition must favor verticality (low-angle shots, tall buildings, or standing characters).
- High-definition, optimized for mobile vertical scrolling.

**CRITICAL INSTRUCTION**
Imagine the image is a smartphone screen placed in the middle of a square black room. 
Do not extend any part of the scene into the left or right black pillars. 
Focus all detail and the subject exclusively in the central vertical column.

[Character reference handling section]
{character_description}

**MANDATORY CAMERA SETTINGS - MUST FOLLOW EXACTLY**
[Shot composition section - HIGH PRIORITY]
CAMERA ANGLE/SHOT TYPE: {shot_type}
- You MUST strictly follow this camera angle
- The shot type defines the framing, distance, and perspective
- Examples: Wide Shot = show full environment + small characters, Close-up = face fills frame, Over-the-shoulder = POV from behind one character
COMPOSITION: {composition_notes}
FRAME ALLOCATION: Characters {character_frame_percentage}%, Environment {environment_frame_percentage}%

[Environment context section]
Primary Setting: {environment_focus}
Environmental Details: {environment_details}
Atmospheric Conditions: {atmospheric_conditions}

[Master visual prompt]
{visual_prompt}

[Visual SFX Effects - Apply if specified]
{sfx_description}

[Negative prompt]
{negative_prompt}, square image, 1:1 ratio, horizontal orientation, landscape mode

[Technical parameters - MANDATORY]
- Aspect Ratio: 9:16 VERTICAL (CRITICAL - must be portrait orientation)
- Character Reference Weight: 0.65
- Focus Priority: Environment first, then characters
- Orientation: PORTRAIT / VERTICAL (not landscape)

Generate the image following these instructions precisely. The image MUST be vertical 9:16.
"""


# ============================================================
# USAGE EXAMPLE WITH ACTUAL DATA POPULATED
# ============================================================

SCENE_IMAGE_EXAMPLE = """
[Character reference handling section]
- HANA: Female character (reference image provided)
- JUN: Male character (reference image provided)

[Shot composition section]
Shot Type: Wide establishing shot
Composition Rule: Rule of thirds, characters positioned in lower-left third
Frame Allocation: Characters 35%, Environment 65%

[Environment context section]
Primary Setting: Busy Seoul subway platform during evening rush hour
Environmental Details: Modern subway platform with white ceramic tile walls, fluorescent strip lighting, digital displays
Atmospheric Conditions: Artificial white-blue fluorescent lighting, evening time

[Master visual prompt]
Wide establishing shot, vertical webtoon panel, 9:16 aspect ratio, rule of thirds composition with characters in lower-left third, Modern Seoul subway platform with white ceramic tile walls extending into depth perspective, fluorescent strip lighting creating hard shadows overhead, digital LED arrival displays showing Korean text "2분 후 도착" in orange, advertisement posters for Korean cosmetics and K-pop concerts lining walls, yellow tactile safety line running along platform edge, metal bench with elderly man reading newspaper, visible train tunnel entrance on left with approaching train headlights creating warm yellow glow, stainless steel trash bins and recycling stations, emergency exit signs with green glow, polished floor reflecting overhead lights, depth of field showing platform extending 30+ meters back, crowd of 8-10 commuters in winter coats scattered through midground and background, realistic urban subway environment details, photorealistic environmental textures, cinematic lighting with cool fluorescent dominant and warm train light accents, Hana positioned lower-left frame near platform edge, standing in three-quarter view looking down at phone in hands, natural standing pose with weight on one leg, Jun positioned in midground right of center, mid-stride walking motion with messenger bag over shoulder, turning head slightly back toward Hana, both characters wearing winter casual clothing, natural body language and movement, Romance/Slice-of-life manhwa/webtoon aesthetic, professional digital comic art, cool-toned color grading with warm accents, dramatic depth of field with crisp foreground and detailed background, vertical scrolling optimized, cinematic realism meets Korean webtoon art style

[Negative prompt]
portrait photography, headshot, profile picture, face close-up, cropped body, upper body only, simple background, plain background, empty space, white background, studio lighting, passport photo, character fills entire frame, minimal environment, blurred background, bokeh background only, floating character, no context, symmetrical centered face, instagram selfie style, ID photo, yearbook photo, model photoshoot

[Technical parameters]
- Aspect Ratio: 9:16
- Character Reference Weight: 0.65
- Focus Priority: Environment first, then characters
"""
# ----------------------------------------

# SCEME_IMAGE_TEMPLATE = """
# [SYSTEM INSTRUCTION: Generate a high-fidelity image where characters are visually distinct based on the descriptions below. Cross-reference with provided character images.

# CHARACTER IN SCENE: 
# {character_description}

# GENRE_STYLE: {genre_style}

# SCENE_DESCRIPTION: {scene_description}

# **CRITICAL**
# - ASPECT_RATIO: 9:16
# - VERTICAL SCROLLING WEBTOON AESTHETIC

# """

# # CHARACTER_DESCRIPTIONS = """
# # HANA: Female, long straight jet-black hair with blunt bangs, sharp almond-shaped eyes, wearing a white oversized techwear hoodie. (Shortest character)
# # JUN: Male, messy shoulder-length chocolate brown hair, athletic build, wearing a dark leather jacket and a silver pendant. (Taller than Hana)
# # DAX: Male, buzzed undercut blonde hair, prominent scar over the left eyebrow, wearing a tactical black vest over a grey shirt.
# # """

# CHARACTER_DESCRIPTIONS = ""