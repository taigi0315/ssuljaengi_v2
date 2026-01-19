"""
Fidelity Validation Prompts

Prompts for the webtoon fidelity validation workflow that ensures
stories are faithfully translated into visual panels.
"""

# ============================================================================
# Node 1: Story Architect - Generates ground truth story from seed
# ============================================================================

STORY_ARCHITECT_PROMPT = """You are a master storyteller creating a detailed narrative.

Based on this seed idea: "{seed}"

Write a complete 1-page story (400-600 words) that includes:

1. **Clear Character Motivations**: For each character, explicitly define:
   - What they want (their goal)
   - Why they want it (their motivation)
   - What's stopping them (their obstacle)

2. **Key Plot Points**: Include 5-7 distinct story beats that drive the narrative

3. **Conflicts**: Include at least one:
   - Internal conflict (character vs self - doubt, fear, moral dilemma)
   - External conflict (character vs character, environment, or circumstances)

4. **Emotional Beats**: Mark clear moments where emotions shift or intensify

5. **Visual Potential**: Write scenes that would translate well to visual panels

IMPORTANT: The story must be clear enough that someone could understand it ONLY from
visual scenes and dialogue - no internal monologue that can't be shown.

Respond with a JSON object in this exact format:
{{
    "story": "<the full narrative text, 400-600 words>",
    "summary": "<a 3-5 sentence summary of the key events>",
    "character_motivations": {{
        "<character_name>": {{
            "goal": "<what they want to achieve>",
            "motivation": "<why they want it - their driving reason>",
            "obstacle": "<what stands in their way>"
        }}
    }},
    "key_conflicts": [
        "<description of conflict 1>",
        "<description of conflict 2>"
    ],
    "plot_points": [
        "<beat 1: setup/introduction>",
        "<beat 2: inciting incident>",
        "<beat 3: rising action>",
        "<beat 4: midpoint>",
        "<beat 5: crisis>",
        "<beat 6: climax>",
        "<beat 7: resolution>"
    ]
}}

Ensure all JSON is valid and properly escaped."""


# ============================================================================
# Node 2: Webtoon Scripter - Converts story to panels
# ============================================================================

SCRIPTER_INITIAL_PROMPT = """You are an expert webtoon scripter who converts stories into visual panels.

STORY TO CONVERT:
{story}

CHARACTER MOTIVATIONS (must be clearly shown in panels):
{character_motivations}

KEY CONFLICTS (must be visually evident):
{key_conflicts}

---

Create a webtoon script with 8-12 panels. Each panel must:

1. **Visual Description** (150+ characters): Describe what the reader SEES.
   - Include facial expressions that SHOW emotions
   - Include body language that SHOWS character state
   - Include environmental details that reinforce mood

2. **Dialogue**: What characters SAY. Use dialogue to:
   - Reveal character motivations
   - Advance the plot
   - Show relationships

3. **Shot Type**: Choose appropriate camera angle
   - Close-up: for emotional moments, reactions
   - Medium: for dialogue, character interactions
   - Wide: for establishing shots, action sequences

CRITICAL RULES:
- SHOW, don't tell. If a character is angry, describe their clenched fists and furrowed brow.
- Every character motivation must be VISUALLY evident through actions or dialogue.
- Every conflict must have at least one panel dedicated to showing it.

Output JSON format:
{{
    "characters": [
        {{
            "name": "<character name>",
            "visual_description": "<detailed appearance for image generation, 100+ chars>"
        }}
    ],
    "panels": [
        {{
            "panel_number": 1,
            "visual_description": "<what the reader sees, 150+ chars>",
            "dialogue": [
                {{"character": "<name>", "text": "<what they say>"}}
            ],
            "shot_type": "<Close-up|Medium Shot|Wide Shot|Bird's Eye|Low Angle>",
            "environment": "<location/setting>"
        }}
    ]
}}"""


SCRIPTER_REVISION_PROMPT = """You are revising webtoon panels based on reader feedback.

A "blind reader" (someone who only saw the panels, not the original story)
tried to understand the story. They MISSED or MISUNDERSTOOD the following:

CRITIQUE (Information Gaps):
{critique}

SPECIFIC GAPS TO ADDRESS:
{specific_gaps}

---

CURRENT PANELS:
{current_panels}

CHARACTER MOTIVATIONS (must be shown):
{character_motivations}

---

REVISION INSTRUCTIONS:
1. Do NOT change the story itself - only improve HOW it's visualized
2. For EACH gap listed above:
   - Add visual cues that SHOW the missing information
   - Add or modify dialogue to TELL the missing context
   - Use environmental details to reinforce meaning
   - Consider adding a dedicated panel if the information is critical

3. Ensure EVERY character motivation is now visually clear
4. Ensure EVERY conflict is explicitly shown

Return the COMPLETE revised panel list (all panels, not just changed ones).

Output JSON format:
{{
    "characters": [
        {{
            "name": "<character name>",
            "visual_description": "<detailed appearance, 100+ chars>"
        }}
    ],
    "panels": [
        {{
            "panel_number": 1,
            "visual_description": "<what the reader sees, 150+ chars>",
            "dialogue": [
                {{"character": "<name>", "text": "<what they say>"}}
            ],
            "shot_type": "<Close-up|Medium Shot|Wide Shot|Bird's Eye|Low Angle>",
            "environment": "<location/setting>"
        }}
    ]
}}"""


# ============================================================================
# Node 3: Blind Reader - Reconstructs story from panels only
# ============================================================================

BLIND_READER_PROMPT = """You are a reader who has NEVER seen the original story.
You can ONLY see the webtoon panels below. Analyze them and reconstruct what you understand.

===== WEBTOON PANELS =====
{panels_json}

===== CHARACTERS DEFINED =====
{characters_json}

===== YOUR TASK =====
Based ONLY on what you can see and read in these panels, answer:

1. **Story Reconstruction**: What is the plot? Write a narrative summary of what happened.
   Be as detailed as possible, including character actions and dialogue.

2. **Character Analysis**: For each character you can identify:
   - What do they seem to want? (their apparent goal)
   - How confident are you in this interpretation? (0-100)

3. **Conflict Identification**: What conflicts or tensions exist in this story?
   List any you can identify from the visuals and dialogue.

4. **Unclear Elements**: What was confusing, ambiguous, or unclear?
   List anything you couldn't understand from the panels alone.

5. **Overall Confidence**: How confident are you in your overall interpretation? (0-100%)
   - 80-100%: Very clear, I understand the story well
   - 50-79%: Somewhat clear, but some things are ambiguous
   - 0-49%: Confusing, I'm guessing at many things

IMPORTANT: Be honest about what you DON'T understand. If something is unclear,
say so. Your job is to identify gaps, not to make perfect guesses.

Output JSON:
{{
    "reconstructed_story": "<your interpretation of the story, 100-300 words>",
    "inferred_motivations": {{
        "<character_name>": {{
            "apparent_goal": "<what you think they want>",
            "confidence": <0-100>
        }}
    }},
    "inferred_conflicts": [
        "<conflict 1 description>",
        "<conflict 2 description>"
    ],
    "unclear_elements": [
        "<element 1 that was confusing>",
        "<element 2 that was confusing>"
    ],
    "overall_confidence": <0-100>
}}"""


# ============================================================================
# Node 4: Fidelity Evaluator - Compares original to reconstruction
# ============================================================================

FIDELITY_EVALUATOR_PROMPT = """You are a fidelity evaluator comparing an ORIGINAL story to a READER'S reconstruction.

The reader ONLY saw webtoon panels - they never read the original story.
Your job is to identify what information was LOST or MISUNDERSTOOD in translation.

===== ORIGINAL STORY =====
{original_story}

===== ORIGINAL SUMMARY =====
{story_summary}

===== ORIGINAL CHARACTER MOTIVATIONS =====
{character_motivations}

===== ORIGINAL KEY CONFLICTS =====
{key_conflicts}

===== ORIGINAL PLOT POINTS =====
{plot_points}

===== READER'S RECONSTRUCTION =====
{reconstructed_story}

===== READER'S INFERRED MOTIVATIONS =====
{inferred_motivations}

===== READER'S INFERRED CONFLICTS =====
{inferred_conflicts}

===== READER'S UNCLEAR ELEMENTS =====
{unclear_elements}

===== READER'S CONFIDENCE =====
{reader_confidence}%

---

EVALUATION TASK:

1. **Compare** the original story to the reconstruction
2. **Identify Gaps** - things the reader missed or misunderstood:
   - Plot gaps: Key events the reader missed
   - Motivation gaps: Character goals the reader didn't understand
   - Emotion gaps: Emotional beats that weren't conveyed
   - Relationship gaps: Character relationships that were unclear
   - Conflict gaps: Tensions that weren't apparent

3. **Score Fidelity** (0-100):
   - 90-100: Reader understood almost everything correctly
   - 70-89: Reader got the main story, missed some details
   - 50-69: Reader got partial understanding, significant gaps
   - 30-49: Reader was confused about major elements
   - 0-29: Reader completely misunderstood the story

4. **Generate Critique** for the scripter:
   - Be SPECIFIC about what needs to change
   - Suggest HOW to fix each gap (visual cues, dialogue, etc.)

Output JSON:
{{
    "fidelity_score": <0-100>,
    "is_valid": <true if score >= 80>,
    "gaps": [
        {{
            "category": "<plot|motivation|emotion|relationship|conflict>",
            "original_element": "<what was in the original>",
            "reader_interpretation": "<what the reader understood, or 'NOT DETECTED'>",
            "severity": "<critical|major|minor>",
            "suggested_fix": "<specific suggestion for scripter>"
        }}
    ],
    "critique": "<structured feedback for scripter, 100-300 words>"
}}

IMPORTANT:
- Be thorough - identify ALL significant gaps
- Be constructive - every gap should have a suggested fix
- Critical gaps = story doesn't make sense without this
- Major gaps = important information missing
- Minor gaps = small details that enhance but aren't essential"""
