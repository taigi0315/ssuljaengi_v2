"""
COMPLETE WEBTOON CREATION PIPELINE EXAMPLE
===========================================

This demonstrates the full workflow from story → structured JSON → image prompts
"""

# ============================================================

# STEP 1: INPUT STORY

# ============================================================

INPUT_STORY = """
Hana, a 24-year-old college student, has been taking the same subway route for three
years, always lost in her phone. Jun, a 26-year-old photographer, recently moved to
Seoul and finds beauty in everyday moments. One evening during cherry blossom season,
they accidentally bump into each other at the platform. Hana drops her blue messenger
bag, and inside falls out a vintage film camera - the same model Jun uses. Their eyes
meet as Jun helps her pick it up. "You shoot film?" he asks, surprised. Before she can
answer, her train arrives and she rushes off, leaving Jun holding a roll of undeveloped
film that fell from her bag. He decides to develop it, hoping to find her again.
"""

GENRE_STYLE = "Romance/Slice-of-life"

# ============================================================

# STEP 2: WEBTOON WRITER PROMPT GENERATES THIS JSON

# ============================================================

WEBTOON_JSON_OUTPUT = {
"characters": [
{
"name": "Hana",
"reference_tag": "Hana(24, student)",
"gender": "female",
"age": "24",
"appearance_notes": "Long straight black hair with blunt bangs, warm brown eyes, gentle features, petite frame, casual student fashion sense",
"typical_outfit": "Cream oversized knit sweater, blue jeans, white sneakers, blue canvas messenger bag",
"personality_brief": "quiet, observant"
},
{
"name": "Jun",
"reference_tag": "Jun(26, photographer)",
"gender": "male",
"age": "26",
"appearance_notes": "Messy dark brown hair, kind eyes, athletic build, casual artistic style",
"typical_outfit": "Black t-shirt, dark jeans, brown leather jacket, camera bag strap across chest",
"personality_brief": "warm, curious"
}
],

    "scenes": [
        # SCENE 1: Establishing Shot
        {
            "scene_number": 1,
            "shot_type": "Extreme Wide Shot / Establishing Shot",
            "composition_notes": "Symmetrical composition, platform extending into depth, characters tiny in lower third",
            "environment_focus": "Seoul subway platform during cherry blossom season evening",
            "environment_details": "Modern underground subway platform with white ceramic tiles, curved ceiling with embedded LED strip lights creating soft glow, cherry blossom petals scattered on ground blown in from street entrance, digital train arrival display showing '2분 후' in orange LED, vending machines along far wall with soft blue glow, metal benches with elderly passengers, yellow safety line running length of platform, advertisement lightboxes for Korean cosmetics and tech products, visible escalator entrance on right with commuters descending, polished floor reflecting overhead lights",
            "atmospheric_conditions": "Early evening 6:30 PM, cool LED lighting with warm orange accents from displays, pink cherry blossom petals creating magical atmosphere, moderate crowd of commuters in spring jackets, gentle breeze carrying petals through station",
            "active_character_names": ["Hana", "Jun"],
            "character_placement_and_action": "Hana visible as small figure in lower left third standing near platform edge looking at phone, Jun entering frame from right escalator in lower right third carrying camera bag, at least 15 meters apart, both unaware of each other, surrounded by 8-10 other commuters scattered through space",
            "character_frame_percentage": 15,
            "environment_frame_percentage": 85,
            "visual_prompt": "Extreme wide establishing shot, vertical webtoon panel 9:16, symmetrical composition with vanishing point perspective, Seoul subway platform extending deep into frame, white ceramic tile walls and curved ceiling with embedded LED strips creating soft white glow, scattered pink cherry blossom petals on polished floor, digital orange LED display showing Korean text '2분 후', blue-glowing vending machines along far wall, metal benches with elderly passengers reading, yellow tactile safety line running into distance, advertisement lightboxes for cosmetics, visible escalator with descending commuters on right, Hana(24, student) tiny figure lower left near platform edge looking at phone wearing cream sweater, Jun(26, photographer) small figure lower right entering from escalator with camera bag, 8-10 other commuters scattered throughout creating lived-in atmosphere, early evening cool LED lighting with warm orange display accents, gentle breeze effect on petals, photorealistic environmental detail, cinematic depth, manhwa/webtoon aesthetic",
            "negative_prompt": "close-up, portrait, headshot, face focus, character fills frame, simple background, empty space, studio photo, cropped body, minimal environment, blurred background",
            "dialogue": null,
            "story_beat": "Establishing the setting and introducing both characters in their separate worlds"
        },

        # SCENE 2: Hana Close-Up
        {
            "scene_number": 2,
            "shot_type": "Medium Close-Up",
            "composition_notes": "Rule of thirds, Hana positioned right third, negative space left showing platform",
            "environment_focus": "Platform edge with train tunnel visible",
            "environment_details": "Dark train tunnel entrance in background with safety lights along track bed, yellow safety line in foreground, metal platform edge texture, scattered cherry blossom petals on ground near feet, out-of-focus crowd movement in far background, digital display edge visible showing orange glow",
            "atmospheric_conditions": "Cool overhead lighting on face, warm orange glow from nearby display creating rim light on hair, cherry blossom petals floating in shallow depth of field, urban subway ambiance",
            "active_character_names": ["Hana"],
            "character_placement_and_action": "Hana positioned in right third of frame from chest up, holding smartphone in both hands at chest level looking down at screen with focused expression, standing naturally with slight weight shift, cream sweater visible, black hair falling forward slightly, cherry blossom petal caught in hair, platform environment taking up left third and background",
            "character_frame_percentage": 45,
            "environment_frame_percentage": 55,
            "visual_prompt": "Medium close-up shot, vertical 9:16 webtoon panel, rule of thirds with Hana(24, student) positioned right third from chest up, holding smartphone in both hands looking down at screen with focused expression, wearing cream oversized sweater, black hair with bangs falling forward with single cherry blossom petal caught in strands, left third shows dark train tunnel entrance with safety lights along tracks, yellow safety line in foreground, scattered pink petals on platform ground, blurred crowd movement in deep background, orange LED display glow creating warm rim light on hair, cool overhead platform lighting on face, shallow depth of field on floating petals, photorealistic subway textures, manhwa aesthetic, intimate moment in public space",
            "negative_prompt": "headshot only, face-only portrait, cropped at neck, plain background, white background, studio lighting, symmetrical centered face, passport photo, simple backdrop",
            "dialogue": [
                {"character": "Hana", "text": "Where is this train... I'm going to be late."}
            ],
            "story_beat": "Hana absorbed in her routine, unaware of what's about to happen"
        },

        # SCENE 3: Jun Medium Shot
        {
            "scene_number": 3,
            "shot_type": "Medium Full Shot",
            "composition_notes": "Positioned left third, environmental context dominant on right, dynamic walking pose",
            "environment_focus": "Platform with escalator and vending machines",
            "environment_details": "Metal escalator steps visible behind with two commuters descending, blue-lit vending machine displaying drinks on right side, advertisement lightbox showing K-pop poster, tiled wall with directional signage in Korean and English, trash bin with recycling symbols, floor texture showing wear patterns and scattered petals",
            "atmospheric_conditions": "Mixed lighting from cool fluorescent overhead and warm vending machine glow, evening commute atmosphere, sense of movement and transit",
            "active_character_names": ["Jun"],
            "character_placement_and_action": "Jun positioned left third of frame from knees up, mid-stride walking toward camera with camera bag strap across chest, turning head to right observing something off-frame, left hand adjusting camera bag strap, wearing black t-shirt and brown leather jacket partially unzipped, natural walking posture with weight on forward leg, messy dark brown hair catching light",
            "character_frame_percentage": 40,
            "environment_frame_percentage": 60,
            "visual_prompt": "Medium full shot, vertical 9:16 webtoon panel, Jun(26, photographer) positioned left third from knees up mid-stride walking forward, turning head right observing off-frame, adjusting camera bag strap across chest with left hand, wearing black t-shirt and brown leather jacket, messy dark hair catching overhead light, right side shows metal escalator with two descending commuters, blue-glowing vending machine displaying colorful drinks, K-pop advertisement lightbox, Korean-English directional signage on tiled wall, recycling bin, polished floor with wear patterns and scattered pink cherry blossom petals, mixed cool fluorescent and warm vending machine lighting, evening transit atmosphere, sense of movement and discovery, photorealistic urban details, manhwa aesthetic, environmental storytelling",
            "negative_prompt": "close-up portrait, upper body only, cropped legs, simple background, plain backdrop, face focus only, studio photo, headshot, centered subject, empty space",
            "dialogue": null,
            "story_beat": "Jun arriving at platform, his photographer's eye noticing details around him"
        },

        # SCENE 4: The Collision - Wide Dynamic
        {
            "scene_number": 4,
            "shot_type": "Wide Shot",
            "composition_notes": "Dutch angle tilted 15 degrees, characters at intersection in center, environmental chaos around collision point",
            "environment_focus": "Platform collision point with crowd reactions",
            "environment_details": "Platform tiles at Dutch angle showing motion, other commuters stepping back creating circular space around collision, fallen cherry blossom petals suspended in motion blur, blue messenger bag mid-fall with items starting to spill, smartphone tumbling, scattered crowd in background frozen in reaction, metal bench visible at angle, yellow safety line cutting diagonally across frame, train arrival display blurred in background showing urgent orange glow",
            "atmospheric_conditions": "Dramatic moment frozen in time, motion blur on peripheral elements, sharp focus on collision point, cool fluorescent creating hard shadows, sense of sudden chaos in ordered space",
            "active_character_names": ["Hana", "Jun"],
            "character_placement_and_action": "Hana in center-left stumbling backward from collision, arms raising instinctively for balance, expression of surprise, phone falling from hand, blue messenger bag strap slipping from shoulder mid-fall, Jun in center-right reaching forward in apologetic gesture, body language showing sudden stop, both figures sharp while surroundings have motion blur, 3-4 background commuters reacting with turned heads and stepped-back poses",
            "character_frame_percentage": 35,
            "environment_frame_percentage": 65,
            "visual_prompt": "Wide dynamic shot, vertical 9:16 webtoon panel, Dutch angle tilted 15 degrees clockwise, Hana(24, student) center-left stumbling backward with arms raising for balance, surprised expression, cream sweater, phone falling from hand, blue messenger bag strap slipping from shoulder mid-fall, Jun(26, photographer) center-right reaching forward apologetically, leather jacket, both sharp focus while surroundings motion-blurred, platform tiles at angle, 3-4 background commuters stepping back creating circular space around collision, cherry blossom petals suspended mid-air with motion blur, yellow safety line cutting diagonally, metal bench visible at angle, blurred orange train display in background, dramatic collision frozen-moment, cool fluorescent hard shadows, sense of sudden chaos in ordered transit space, cinematic motion, manhwa aesthetic, high detail on action",
            "negative_prompt": "static pose, portrait style, close-up faces, simple background, studio photo, symmetrical composition, no motion, plain setting, character-focused only, minimal environment",
            "dialogue": [
                {"character": "Jun", "text": "Oh! I'm so sorry!"},
                {"character": "Hana", "text": "Ah!"}
            ],
            "story_beat": "The fateful collision that brings them together"
        },

        # SCENE 5: Extreme Close-Up - The Camera
        {
            "scene_number": 5,
            "shot_type": "Extreme Close-Up",
            "composition_notes": "Center focus on camera with hands entering frame edges, shallow depth of field",
            "environment_focus": "Ground level platform showing spilled items",
            "environment_details": "Polished platform floor with reflection of overhead lights, scattered pink cherry blossom petals, strap of blue messenger bag, corner of smartphone screen showing cracked glass catching light, platform tile grout lines, few dropped items from bag",
            "atmospheric_conditions": "Shallow depth of field with only camera and hands in focus, background heavily blurred showing shapes of standing figures, cool overhead light creating glints on metal camera body, intimate moment of connection",
            "active_character_names": ["Hana", "Jun"],
            "character_placement_and_action": "Only hands visible in frame - Jun's hands entering from bottom reaching toward vintage film camera on ground, Hana's hands entering from top also reaching, fingers almost touching, camera positioned center as focal point catching light, rest of bodies out of frame above",
            "character_frame_percentage": 40,
            "environment_frame_percentage": 60,
            "visual_prompt": "Extreme close-up shot, vertical 9:16 webtoon panel, center focus on vintage film camera lying on polished platform floor, Jun's hands entering bottom of frame reaching toward camera, Hana's hands entering top of frame also reaching, fingers nearly touching over camera body, camera catching overhead light on metal surfaces creating glints, scattered pink cherry blossom petals on floor, reflection of fluorescent lights on polished tiles, blue messenger bag strap visible, smartphone corner showing cracked screen, platform tile grout lines in sharp detail, shallow depth of field with background heavily blurred showing legs of standing figures, cool lighting with warm highlights, intimate moment of connection through shared object, photorealistic texture detail, manhwa aesthetic, symbolic composition",
            "negative_prompt": "full body, wide shot, faces visible, multiple objects in focus, busy background, character portraits, plain setting, no depth of field",
            "dialogue": null,
            "story_beat": "The camera becomes the object of connection between them"
        },

        # SCENE 6: Over-the-Shoulder Jun's POV
        {
            "scene_number": 6,
            "shot_type": "Over-the-Shoulder Shot",
            "composition_notes": "Jun's shoulder and back of head in foreground left, Hana's surprised face in midground right third, environmental depth in background",
            "environment_focus": "Platform with approaching train visible",
            "environment_details": "Train headlights growing brighter in tunnel entrance background creating dramatic backlight, platform crowd turning toward approaching train, digital display changing to show 'arriving now' in Korean, yellow safety line prominent in midground, commuters beginning to gather near platform edge, cherry blossom petals swirling in breeze created by approaching train, advertisement panels glowing",
            "atmospheric_conditions": "Dramatic lighting shift as train headlights illuminate scene from behind Hana, creating rim light on her hair, cool platform lights mixing with warm train glow, sense of urgency and time pressure, wind effect from train",
            "active_character_names": ["Hana", "Jun"],
            "character_placement_and_action": "Jun's shoulder and back of head occupying foreground left third out of focus, dark leather jacket and messy hair visible, Hana in midground right third in sharp focus kneeling on ground gathering scattered items into messenger bag, looking up with surprised expression making eye contact, holding vintage camera in one hand, cherry blossom petals blowing around her from train wind, commuters visible in background gathering at platform edge",
            "character_frame_percentage": 45,
            "environment_frame_percentage": 55,
            "visual_prompt": "Over-the-shoulder shot, vertical 9:16 webtoon panel, Jun's shoulder and back of dark messy hair in foreground left third out of focus wearing brown leather jacket, Hana(24, student) in sharp focus midground right third kneeling gathering items into blue messenger bag, looking up making eye contact with surprised expression, holding vintage film camera in one hand, cream sweater, black hair with blowing cherry blossom petals caught in strands, train headlights growing bright in tunnel background creating dramatic rim light around her, yellow safety line prominent in midground, 4-5 commuters gathering at platform edge in background silhouetted by train light, digital display showing Korean 'arriving' text, petals swirling in train-created breeze, dramatic lighting shift from cool fluorescent to warm train glow, sense of urgency and fleeting moment, photorealistic depth, manhwa aesthetic, emotional connection",
            "negative_prompt": "both faces in focus, symmetrical composition, no depth layers, simple background, portrait style, static lighting, plain setting, no atmosphere",
            "dialogue": [
                {"character": "Jun", "text": "You shoot film?"}
            ],
            "story_beat": "Jun notices the camera and makes a connection"
        },

        # SCENE 7: Low Angle - Hana Rising
        {
            "scene_number": 7,
            "shot_type": "Low Angle Shot",
            "composition_notes": "Camera positioned ground level looking up, Hana rising dominating frame with ceiling and crowd in upper background",
            "environment_focus": "Platform from ground perspective with overhead architecture",
            "environment_details": "View from floor level showing polished tiles in extreme foreground, Hana's white sneakers and jean cuffs in immediate foreground, curved subway ceiling with LED strip lights running in parallel lines into distance overhead, hanging directional signs in Korean and English, support pillars visible, crowd of commuters' legs and lower bodies visible in background, train visible past Hana through platform creating bright backlight, architectural lines creating dynamic perspective",
            "atmospheric_conditions": "Dramatic low angle lighting, overhead LEDs creating geometric light patterns, train headlights creating bright backlight halo, sense of movement and rising action, epic feel to mundane moment",
            "active_character_names": ["Hana"],
            "character_placement_and_action": "Hana positioned center rising from kneeling position to standing, camera tilted upward making her appear powerful and decisive, mid-motion of standing up while slinging blue messenger bag over shoulder, holding camera close to chest with both hands, determined expression looking toward train, hair flowing with motion and train breeze, filling vertical frame from ground to upper third",
            "character_frame_percentage": 50,
            "environment_frame_percentage": 50,
            "visual_prompt": "Low angle shot from ground level, vertical 9:16 webtoon panel looking upward, Hana(24, student) center frame rising from kneeling to standing mid-motion, white sneakers and jean cuffs in extreme foreground on polished platform tiles, slinging blue messenger bag over shoulder while holding vintage camera to chest with protective gesture, determined expression looking toward train, cream sweater and black hair flowing with motion and train breeze, curved subway ceiling with parallel LED strip lights running into distance overhead creating geometric patterns, hanging Korean-English directional signs, support pillars visible, crowd of commuters' legs in background, bright train headlights creating backlight halo around her figure, dramatic upward perspective making her appear decisive and powerful, cool LED overhead mixing with warm train glow, sense of rising action and urgency, cinematic drama in transit moment, manhwa aesthetic, dynamic composition",
            "negative_prompt": "eye level shot, portrait, headshot, simple background, static pose, no perspective, plain lighting, studio photo, centered symmetrical, minimal environment",
            "dialogue": null,
            "story_beat": "Hana rushes to catch her train, the moment passing"
        },

        # SCENE 8: Wide Shot - The Departure
        {
            "scene_number": 8,
            "shot_type": "Wide Shot",
            "composition_notes": "Split composition - Jun left foreground, train doors center, Hana visible inside train right, platform depth in background",
            "environment_focus": "Platform with departing train creating visual barrier",
            "environment_details": "Modern subway train car with illuminated interior visible through glass doors, fluorescent interior lighting contrasting with platform, other passengers visible inside train in silhouette, Jun standing on platform tiles with scattered cherry petals around feet, yellow safety line between Jun and train, platform extending into depth behind Jun with dispersing crowd, digital display showing next train time, curved platform ceiling with LED lights, sense of separation and distance despite proximity",
            "atmospheric_conditions": "Transition lighting as train interior brightness contrasts cool platform, cherry blossom petals settling after train wind, quiet moment after action, longing atmosphere, early evening blues and warm train interior yellows creating color separation",
            "active_character_names": ["Hana", "Jun"],
            "character_placement_and_action": "Jun positioned left foreground from full body, standing still watching train with hand raised in incomplete wave holding small film canister that fell from bag, leather jacket and camera bag visible, lonely posture on empty platform, Hana visible through train window right side standing inside holding overhead rail, looking back through glass making eye contact, visible distance and glass barrier between them, 4-5 other passengers in train creating depth",
            "character_frame_percentage": 35,
            "environment_frame_percentage": 65,
            "visual_prompt": "Wide shot, vertical 9:16 webtoon panel, split composition with Jun(26, photographer) left foreground full body standing on platform holding small film canister watching departing train, hand raised in incomplete wave gesture, leather jacket and camera bag, lonely posture surrounded by settling cherry blossom petals, yellow safety line between him and train, modern subway train center occupying middle frame with illuminated interior visible through glass doors, Hana(24, student) visible inside right side through window standing holding overhead rail looking back through glass at Jun, making eye contact across barrier, 4-5 silhouetted passengers in train adding depth, platform extending into background behind Jun with dispersing crowd, curved ceiling with LED lights, digital display showing next train, contrasting lighting between cool blue platform and warm yellow train interior, glass reflection showing both spaces, sense of separation despite proximity, longing atmosphere, cherry petals settling, photorealistic environmental detail, manhwa aesthetic, emotional distance",
            "negative_prompt": "close-up, portrait, simple background, no depth, character-focused only, minimal environment, studio lighting, plain setting, no atmosphere, symmetrical",
            "dialogue": [
                {"character": "Hana", "text": "Wait, that's--"}
            ],
            "story_beat": "Their connection interrupted, but Jun has the film - a reason to meet again"
        }
    ],

    "episode_summary": "Hana and Jun's paths cross for the first time at a Seoul subway platform during cherry blossom season when an accidental collision reveals they both shoot film photography. Before they can talk, Hana rushes to catch her train, unknowingly leaving behind a roll of undeveloped film that Jun finds, setting up their future reunion."

}

# ============================================================

# STEP 3: GENERATE ACTUAL IMAGE PROMPTS FOR EACH SCENE

# ============================================================

def generate_image_prompt_for_scene(scene_data, characters_data):
"""
Takes one scene from the JSON and creates the final image generation prompt
using the enhanced SCENE_IMAGE_TEMPLATE structure
"""

    # Get active characters for this scene
    active_chars = [c for c in characters_data if c["name"] in scene_data["active_character_names"]]

    # Build minimal character description (since references handle appearance)
    char_description = "\n".join([
        f"- {char['name']}: {char['gender']} character (reference image provided - appearance locked)"
        for char in active_chars
    ])

    # Build the complete prompt following the enhanced template
    image_prompt = f"""

You are generating a single webtoon panel for an AI image generator. Character consistency is maintained through reference images - your job is to create CINEMATIC COMPOSITION with rich environments.

---

**CHARACTER REFERENCE HANDLING:**
{char_description}

**IMPORTANT:** Character appearance (face, hair, body) is locked via reference images. Do NOT over-describe their physical features. Focus on PLACEMENT, POSE, and ACTION.

---

**SHOT COMPOSITION:**
Shot Type: {scene_data['shot_type']}
Composition Rule: {scene_data['composition_notes']}
Frame Allocation: Characters occupy {scene_data['character_frame_percentage']}% of frame, environment occupies {scene_data['environment_frame_percentage']}%

---

**ENVIRONMENT CONTEXT:**
Primary Setting: {scene_data['environment_focus']}
Environmental Details: {scene_data['environment_details']}
Atmospheric Conditions: {scene_data['atmospheric_conditions']}

---

**SCENE ACTION:**
{scene_data.get('story_beat', 'N/A')}

---

**GENRE STYLE:** Romance/Slice-of-life

---

**MASTER VISUAL PROMPT:**

{scene_data['visual_prompt']}

---

**NEGATIVE PROMPT (CRITICAL - ALWAYS INCLUDE):**
{scene_data['negative_prompt']}

---

**TECHNICAL PARAMETERS:**

- Aspect Ratio: 9:16 (vertical)
- Image Quality: Maximum detail, 4K equivalent
- Focus Priority: Environment first, then characters in context
- Depth of Field: Multi-layer (foreground, midground, background all detailed)
- Character Reference Weight: 0.65 (face consistency maintained, but composition not dominated)

---

**CHARACTER REFERENCES TO LOAD:**
{', '.join([char['name'] for char in active_chars])}

---

Generate the image following these instructions precisely.
"""

    return image_prompt

# ============================================================

# EXAMPLE: GENERATE PROMPTS FOR ALL SCENES

# ============================================================

print("=" _ 80)
print("WEBTOON IMAGE GENERATION PROMPTS")
print("=" _ 80)
print()

for scene in WEBTOON_JSON_OUTPUT["scenes"]:
prompt = generate_image_prompt_for_scene(scene, WEBTOON_JSON_OUTPUT["characters"])

    print(f"\n{'=' * 80}")
    print(f"SCENE {scene['scene_number']}: {scene['story_beat']}")
    print(f"{'=' * 80}\n")
    print(prompt)
    print("\n" + "-" * 80)

    # In actual implementation, you'd send this to your image generator:
    # image = your_image_generator.generate(
    #     prompt=prompt,
    #     character_refs={
    #         "Hana": hana_reference_image,
    #         "Jun": jun_reference_image
    #     },
    #     reference_weight=0.65,
    #     aspect_ratio="9:16"
    # )
