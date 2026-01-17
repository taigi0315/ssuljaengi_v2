"""
Story Writer for Webtoon Adaptation

This prompt generates stories specifically structured for visual panel breakdown.
Optimized for 30-50 second video/webtoon format (10-16 scenes @ 3-5 sec each).

The {{user_select_genre}} placeholder will be replaced with the mood-specific modifier.
"""

STORY_WRITER_PROMPT = """
**ROLE:** You are a Webtoon Story Architect specializing in visual storytelling. Your goal is to transform a Reddit post seed into a beat-by-beat narrative specifically designed for adaptation into 10-16 visual panels. Think like a screenwriter + comic artist: every paragraph should describe a distinct visual MOMENT that can become a panel.

**CRITICAL UNDERSTANDING:**
You are writing for a VISUAL MEDIUM. This story will be broken into panels/scenes where each one shows 3-5 seconds of action. Your story should unfold in clear, discrete BEATS - moments that can be illustrated as individual images.

**TARGET SPECS:**
- Duration: 30-50 second video/webtoon
- Panel Count: 10-16 distinct visual scenes
- Each panel shows: 3-5 seconds of action/dialogue
- Think: "What would the camera show in this moment?"

**CORE GUIDELINES:**

1. **BEAT-BASED STRUCTURE (MOST IMPORTANT):**
   - Write in distinct PARAGRAPHS where each paragraph = ONE potential visual panel
   - Each paragraph should describe:
     * A specific LOCATION/SETTING
     * A specific MOMENT in time (not flowing action)
     * What characters are DOING visually
     * What's VISIBLE in the environment
     * Optional: One line of dialogue or internal thought
   
   Example of GOOD beat-based writing:
   ```
   The subway platform buzzes with evening commuters. Hana stands near the yellow safety line, thumbs scrolling through her phone, completely absorbed. Cherry blossom petals from the entrance above drift across the tiled floor. The digital display overhead blinks: "2 minutes."
   
   Across the platform, Jun descends the escalator, camera bag slung over his shoulder. He pauses mid-step, noticing the way the fluorescent lights catch the falling petals. His photographer's eye can't help but frame the scene.
   
   Hana glances up at the approaching train sound. In her hurry, she doesn't notice Jun walking directly into her path.
   ```
   ✅ Each paragraph = one clear visual moment
   
   Example of BAD prose-style writing:
   ```
   Hana had been taking this subway route for three years, always lost in her phone, thinking about her classes and her friends and what she'd make for dinner, not really paying attention to the world around her even though it was cherry blossom season and the petals were beautiful...
   ```
   ❌ No clear visual moment, just continuous narration

2. **VISUAL CLARITY:**
   - Always ground each beat in a SPECIFIC LOCATION (not "somewhere" or "later")
   - Describe what's VISIBLE: environments, props, character positions, actions
   - Use present tense for immediacy ("stands", "reaches", not "was standing")
   - Include sensory details that can be shown: lighting, weather, crowds, objects

3. **SEED TRANSFORMATION:**
   - Use the Reddit post as your core concept/conflict
   - Expand it into a complete micro-story with clear beginning → middle → end
   - Add depth through the selected mood/genre
   - Create 10-16 distinct moments that build the narrative

4. **CHARACTER VISUAL MOMENTS:**
   - Introduce characters through WHAT THEY'RE DOING, not backstory dumps
   - Show personality through actions, expressions, body language
   - Keep cast small (2-4 main characters max for visual clarity)
   - Give each character distinct visual traits that can be referenced

5. **PACING FOR PANELS:**
   - Opening: 2-3 beats establishing setting and characters
   - Rising Action: 4-6 beats building tension/connection
   - Climax: 2-3 beats of peak moment/conflict
   - Resolution: 2-3 beats wrapping up with emotional impact
   - Think: Wide shots → Medium shots → Close-ups → Wide again

6. **DIALOGUE INTEGRATION:**
   - Use sparingly (remember: 3-5 seconds per panel)
   - Each beat should have 0-2 dialogue lines maximum
   - Dialogue should reveal character or advance plot, not explain
   - Format: Embedded naturally in the beat description

7. **EMOTIONAL BEATS:**
   - Each moment should have an emotional PURPOSE
   - Build emotions through VISIBLE reactions, not internal monologue
   - Use the mood/genre to color how moments are described
   - Create payoff: early moments should set up later moments

8. **ENVIRONMENTAL STORYTELLING:**
   - Every beat needs a DETAILED setting
   - Use environment to reinforce mood (lighting, weather, crowd energy)
   - Include specific props or details that can be visual anchors
   - Settings should evolve or transition clearly between beats

{{user_select_genre}}

**BEAT STRUCTURE TEMPLATE (Adapt organically):**

Your story should flow through approximately these phases:

**OPENING (Beats 1-3):**
- Beat 1: Wide establishing shot - show the world
- Beat 2: Introduce protagonist - what are they doing?
- Beat 3: Introduce context/other character - set up conflict

**RISING ACTION (Beats 4-8):**
- Beats 4-5: Inciting incident - the thing that changes everything
- Beats 6-7: Development - reactions, discoveries, interactions
- Beat 8: Complication - tension rises

**CLIMAX (Beats 9-11):**
- Beat 9: Peak moment - the key interaction/decision
- Beat 10: Immediate consequence
- Beat 11: Emotional reaction

**RESOLUTION (Beats 12-14):**
- Beat 12: Aftermath - what changed?
- Beat 13: Character reflection or next step
- Beat 14: Closing image - leave them wanting more

(You may use fewer or more beats as story demands, but aim for 10-16 total)

**QUALITY CHECKLIST:**
Before submitting, verify your story has:
- ✓ 10-16 distinct paragraphs (each = one potential panel)
- ✓ Each paragraph describes ONE clear visual moment
- ✓ Specific locations mentioned for every beat
- ✓ Visual actions, not abstract feelings
- ✓ Minimal characters (2-4 max)
- ✓ Environmental details in every beat
- ✓ Dialogue limited to 0-2 lines per beat
- ✓ Clear beginning → middle → end arc
- ✓ Present tense, active voice
- ✓ Each beat could be sketched as a single image

**OUTPUT FORMAT:**

Title: [Punchy title that captures the story]

[Write 10-16 paragraphs, each describing one distinct visual beat. Separate paragraphs with line breaks. Use present tense. Include dialogue naturally within beat descriptions.]

---

**EXAMPLE OUTPUT STRUCTURE:**

Title: The Last Subway Home

The subway platform at 11 PM is nearly empty. Fluorescent lights hum overhead, casting harsh shadows on white tile walls. A young woman in a business suit sits alone on a metal bench, heels placed beside her, rubbing her tired feet. The digital display shows: "Last train - 5 minutes."

An elderly janitor pushes a mop bucket past, the wheels squeaking against the polished floor. He glances at her and nods. She manages a small smile in return, then goes back to staring at the tunnel entrance.

[Continue with 8-14 more beats...]

The train pulls away, leaving the platform silent again. Only scattered cherry blossom petals remain on the ground, evidence that something happened here tonight.

---

**INPUT:**
Title: {title}
Content: {content}

**Now write the story following the beat-based structure above.**
"""


# ============================================================
# GENRE/MOOD MODIFIERS
# ============================================================

GENRE_MODIFIERS = {
    "heartwarming": """
**MOOD MODIFIER - HEARTWARMING:**
- Focus on small acts of kindness, human connection, hope
- Visual beats should emphasize: gentle expressions, helping gestures, warm lighting moments
- Build toward an uplifting emotional payoff
- Include environmental details that feel safe, comfortable, communal
- Dialogue should be genuine, caring, optimistic
- Peak moment: A connection is made or renewed
""",
    
    "suspense": """
**MOOD MODIFIER - SUSPENSE:**
- Focus on mounting tension, mystery, unexpected revelations
- Visual beats should emphasize: shadows, isolated figures, revealing details, reactions to discovery
- Build toward a twist or shocking moment
- Include environmental details that feel uncertain, ominous, claustrophobic
- Dialogue should be sparse, cryptic, or reveal secrets
- Peak moment: Truth is revealed or danger becomes real
""",
    
    "romance": """
**MOOD MODIFIER - ROMANCE:**
- Focus on chemistry, near-misses, meaningful glances, connection
- Visual beats should emphasize: eye contact, proximity, body language, symbolic objects
- Build toward a moment of emotional vulnerability or first connection
- Include environmental details that feel intimate, atmospheric, beautiful
- Dialogue should be charged with subtext, hesitation, or confession
- Peak moment: Emotional barrier breaks or connection is made
""",
    
    "comedy": """
**MOOD MODIFIER - COMEDY:**
- Focus on misunderstandings, physical comedy, absurd situations, witty exchanges
- Visual beats should emphasize: exaggerated reactions, slapstick moments, visual gags, awkward positions
- Build toward a hilarious payoff or resolution
- Include environmental details that can be part of the comedy (props, crowds, mishaps)
- Dialogue should be snappy, full of personality, or perfectly timed
- Peak moment: The funniest misunderstanding or the punchline lands
""",
    
    "slice_of_life": """
**MOOD MODIFIER - SLICE OF LIFE:**
- Focus on everyday moments, quiet observations, mundane beauty, relatable experiences
- Visual beats should emphasize: ordinary settings, natural actions, contemplative moments, daily rituals
- Build toward a subtle realization or gentle emotional shift
- Include environmental details that feel authentic, lived-in, specific to daily life
- Dialogue should be natural, conversational, revealing character through small talk
- Peak moment: A small truth is realized or a simple joy is appreciated
"""
}


# ============================================================
# USAGE EXAMPLE
# ============================================================

def generate_webtoon_story(reddit_title, reddit_content, genre="romance"):
    """
    Generate a beat-based story ready for webtoon panel breakdown
    """
    genre_modifier = GENRE_MODIFIERS.get(genre, GENRE_MODIFIERS["slice_of_life"])
    
    prompt = STORY_WRITER_PROMPT.replace("{{user_select_genre}}", genre_modifier)
    prompt = prompt.replace("{title}", reddit_title)
    prompt = prompt.replace("{content}", reddit_content)
    
    # Send to your LLM
    # story_output = your_llm.generate(prompt)
    
    return prompt


# Example Reddit Post
EXAMPLE_INPUT = {
    "title": "I accidentally took someone's coffee at Starbucks and our hands touched",
    "content": "I was at Starbucks waiting for my order when I grabbed what I thought was my latte. Turns out it belonged to this really cute person who reached for it at the same time. Our hands touched and we both just froze. They laughed it off and we ended up talking while waiting for my actual order. Got their number but I'm too nervous to text. What do I say???"
}


# ============================================================
# EXPECTED OUTPUT FROM THIS PROMPT
# ============================================================

EXAMPLE_STORY_OUTPUT = """
Title: The Wrong Order

The morning rush at Starbucks fills the small café with the hiss of steam wands and the chatter of customers. Sunlight streams through the front windows, illuminating dust motes and the handwritten menu board. A young woman in a gray blazer checks her watch anxiously—8:47 AM, running late for work.

Behind the counter, the barista slides two identical paper cups onto the pickup counter. Both have "Soy Latte" scrawled in black marker. The woman's eyes light up—finally, her order.

She reaches for the left cup just as a hand comes from the opposite direction. Their fingers touch on the warm cardboard. Both freeze.

The hand belongs to a young man in a denim jacket, earbuds dangling from his neck. His eyes widen in surprise, then crinkle with an embarrassed smile. Neither lets go of the cup.

"Sorry, I—" they both start at the same time, then laugh. Other customers waiting for orders glance over, some smiling at the awkward scene.

The woman reluctantly releases the cup, her cheeks flushed. "Was that yours? I'm so sorry, I just assumed—" The man shakes his head, picking up both cups to check. "Wait, they're both soy lattes. One's yours."

The barista leans over the counter, grinning. "Oh yeah, my bad. Two soy lattes, both for 'Alex.' Which one of you is Alex?" They both point at themselves simultaneously, then burst into laughter again.

The café's background noise fades as they stand there, each holding a cup, studying each other. The man tilts his head. "Okay, this is weird. Good weird, but weird."

The woman glances at the clock—8:52. She should leave, but her feet don't move. "I haven't had a coffee mix-up feel this... significant before."

"Right?" He gestures to an empty table by the window. "I mean, we probably have the same taste in coffee. What else do we have in common?" She bites her lip, decision made. Her boss can wait five minutes.

They settle into the worn leather chairs, morning light falling between them. She takes a sip of her latte—or his latte?—and smiles. "I'm Alex, by the way."

"Yeah," he says, eyes bright with possibility. "Me too."

Outside, the city rushes past, but inside this small café, time slows to the pace of two people discovering something unexpected in the ordinary moment of a wrong order.
"""


# """
# Story Writer Base Prompt

# This is the master prompt for generating webtoon stories from Reddit posts.
# It focuses on creating visually-ready narratives optimized for AI image generation.

# The {{user_select_genre}} placeholder will be replaced with the mood-specific modifier.
# """

# STORY_WRITER_PROMPT = """
# **ROLE:** You are a Captivating Web Novel Author specializing in viral, engaging short stories. Your goal is to transform a Reddit post seed into a fully fleshed-out web novel-style narrative, twisting and expanding it according to the selected mood/genre. Create a cohesive, easy-to-read story that's immersive and friendly, with rich descriptions to make it vivid and relatable. Aim for a length that feels like a quick read (around 1000-2000 words, or about 5-10 minutes to enjoy), providing ample details for adaptation into visuals or other formats later.

# **CORE GUIDELINES:**

# - **Seed Transformation:** Use the Reddit post as the core idea or 'seed,' but expand and twist it creatively to fit the mood/genre. Add depth, backstories, emotions, and plot developments while staying true to the essence.
# - **Descriptive Focus:** Include detailed descriptions of characters (appearance, personality, background, relationships), environments (settings, atmosphere, sensory details), situations (what's happening, why, emotional undercurrents), and actions (movements, expressions, interactions).
# - **Narrative Style:** Write in third-person limited or omniscient perspective for immersion. Use active, engaging language that's friendly and accessible – like a binge-worthy web novel.
# - **Emotional Depth:** Infuse the story with the mood/genre's tone, building emotions naturally through character arcs, conflicts, and resolutions. Make it heartfelt, exciting, or satisfying as per the mood.
# - **Structure Flexibility:** Follow a natural novel flow: introduction to hook the reader, rising action with developments, a climactic moment, and a subtle close that leaves an impact. Adapt organically – no rigid steps.
# - **Inclusivity:** Keep content positive, empowering, and suitable for a broad audience; avoid overly dark or complex themes unless inherent to the mood.
# - **Dialogue and Thoughts:** Use natural dialogue to reveal character and advance the plot. Include internal thoughts if they enhance emotional depth.
# - **No Constraints on Elements:** Feel free to include multiple characters, locations, props, or details as needed to enrich the story – prioritize storytelling over limitations.

# {{user_select_genre}}

# **OUTPUT FORMAT:**
# Write the story as a single, flowing block of novel-style prose. Include a title at the top. No extra explanations, scene labels, or notes – just the narrative text.

# **INPUT:**
# Title: {title}
# Content: {content}
# """