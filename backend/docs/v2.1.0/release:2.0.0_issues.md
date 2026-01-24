1. Cinematic Storyboarding & Panel Flow
   The Issue: The system is limited to a basic 3-panel layout that feels "flat." It lacks the emotional close-ups (macro shots) and dynamic pacing essential for the Romance genre.

Action Items:

Dynamic Layout Logic: Move beyond the fixed 3-panel grid. Implement logic that allows for "Focus Panels" (e.g., a hand touch or a facial expression) versus "Action Panels."

Compositional Weight: Allow the agent to assign "importance" to a panel. A "High Importance" panel should take up 60-70% of the image real estate, while "Secondary" panels act as supporting beats.

Emotional Pacing: Define a library of shot types (Extreme Close-Up, Medium Shot, Wide Shot) that the agent must choose from based on the dialogue's sentiment.

2. On-Image Environmental Text (SFX)
   The Issue: Non-dialogue text (e.g., "Silence," "Thump," "Nervousness") is being treated like standard dialogue, which ruins the immersion.

Action Items:

Categorization Agent: Create a classification step for text. Is it Dialogue (Chat Bubble), Internal Monologue (Square Box), or Atmospheric SFX (Free-floating)?

Stylized Typography: For SFX/Atmospheric text, bypass the chat bubble rendering. Use distinct, artistic fonts that blend into the background to enhance the mood rather than cluttering the scene.

3. Character & Outfit Consistency (The "Regression")
   The Issue: Despite using a multi-agent architecture and high-end models, characters are losing their visual identity (e.g., switching from a suit to shorts) between scenes.

Action Items:

Global "Style Sheet" Reference: Ensure the "Outfit Description" isn't just a prompt fragment but a fixed variable passed to every agent.

Temporal Memory Check: Implement a "Verification Agent" that compares the output of Scene N with Scene N-1 to ensure clothing and hair remain consistent.

Context Pruning: If the prompt is too long (see Section 4), the model might be "forgetting" the outfit because it's buried in the middle of the text.

4. Prompt Optimization (Length vs. Clarity)
   The Issue: Using AI (Claude) to write prompts has resulted in "Extraordinarily Long" instructions. This may be causing "Prompt Drift" or "Attention Loss" in the image generator.

Action Items:

Modular Prompting: Instead of one massive prompt, break it into:

Core Style (The "Look")

Character Ref (The "Who")

Scene Action (The "What")

Weight Testing: Research "Negative Constraints" vs. "Over-Description." Sometimes, describing a suit too much causes the model to hallucinate details (like shorts) to fill the "token space."

5. Style Switching at the Panel Level
   The Issue: You want the ability to switch from "High Detail/Beautiful" (Serious Romance) to "Chibi/Simplified" (Comedy) within the same page or even the same image.

Action Items:

Style Tagging per Panel: Assign a style_mode (e.g., romantic_detail or comedy_chibi) to each panel description within the multi-note structure.

Hybrid Rendering: Test if the model can handle multiple styles in one prompt via "Region-based prompting" or if it’s better to generate panels separately and stitch them together to maintain the distinct art styles.
