# Plugin Definition: Story Narrative (The World Builder)

## 1. Mission Statement

The **Story Narrative Plugin** is responsible for the "Script" and the "Physics" of the world. Its goal is to generate scene descriptions, dialogue, and plot progression that adhere to a specific **Narrative Context**.

**Crucial Rule:** This plugin **NEVER** describes how the image is rendered (e.g., colors, lighting, brushstrokes). It only describes **WHAT** exists physically in the scene and **HOW** characters speak.

## 2. Key Responsibilities

- **Era Enforcement:** Strictly filters physical objects to match the timeline (e.g., No smartphones in 1800s; No horses in a Space Station unless specified).
- **Dialogue Dialect:** Controls the speech patterns (e.g., Formal archaic, Modern slang, Technical jargon).
- **Scene Assets:** Lists the tangible props and background elements required for the plot.

2. Detailed Component Breakdown
   To build a robust Narrative Plugin, your prompt must cover four distinct "Logic Gates":

The Chrono-Lock (Time/Tech Constraints):

Why: To prevent "anachronisms" (e.g., a samurai wearing a digital watch).

Mechanism: A strict "Negative Constraint" list.

The Sociolinguistic Layer (Dialogue):

Why: Characters sound fake if they all speak in "Standard GPT English."

Mechanism: A specific "Dialect Profile" for the genre.

The Prop Database (Asset Generation):

Why: When generating images later, we need concrete nouns.

Mechanism: A pre-defined list of acceptable items for the setting.

The Trope Engine (Plot Structure):

Why: Readers read genres for specific feelings. A thriller must have high stakes.

Mechanism: Defined plot beats that the story generator must hit.
