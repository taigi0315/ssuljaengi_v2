"""
Multi‑panel generation prompt utilities.

Provides a structured prompt template that can be fed to Gemini (or other LLM) to generate
N distinct webtoon panels in one image. The template enforces:
- 9:16 vertical aspect ratio
- Explicit panel count
- Per‑panel shot type, subject, action/emotion, and optional style modifiers
- Consistent overall art style

The generated prompt can be passed directly to the LLM via the existing Gemini client.
"""

from typing import List, Dict

# ---------------------------------------------------------------------------
# Prompt template (raw string) – keep placeholders for easy formatting
# ---------------------------------------------------------------------------
MULTI_PANEL_PROMPT_TEMPLATE = """
A vertical webtoon-style comic page with a 9:16 aspect ratio,
featuring {panel_count} distinct horizontal panels stacked vertically.
The overall art style is {style_description}.

CRITICAL INSTRUCTION - NO TEXT OR SPEECH BUBBLES:
- DO NOT render any text, words, letters, or characters in any language
- DO NOT create speech bubbles, thought bubbles, dialogue boxes, or chat bubbles
- DO NOT add captions, subtitles, onomatopoeia, or any written content
- Show character emotions through FACIAL EXPRESSIONS and BODY LANGUAGE only
- The dialogue/text will be added as an overlay AFTER image generation

{panel_descriptions}

{style_modifiers}
Thin panel borders. High resolution, clean line art.
NO TEXT. NO SPEECH BUBBLES. NO DIALOGUE BOXES. EXPRESSIONS ONLY.

"""


def build_panel_description(panel_index: int, spec: Dict[str, str]) -> str:
    """Return a single panel description line.

    Args:
        panel_index: 1‑based index of the panel.
        spec: Dictionary with keys ``shot_type``, ``subject``, ``action`` and optional ``details``.
    Returns:
        Formatted description string for the prompt.
    """
    shot = spec.get("shot_type", "wide")
    subject = spec.get("subject", "character")
    action = spec.get("action", "")
    details = spec.get("details", "")
    parts = [f"Panel {panel_index}: {shot} of {subject}"]
    if action:
        parts.append(action)
    if details:
        parts.append(details)
    return " ".join(parts) + "\n"


def build_multi_panel_prompt(
    panel_count: int,
    style_description: str,
    panels: List[Dict[str, str]],
    style_modifiers: List[str] | None = None,
) -> str:
    """Construct the full multi‑panel generation prompt.

    Parameters
    ----------
    panel_count: Number of panels to generate (must match length of ``panels``).
    style_description: Human readable description of the overall art style.
    panels: List of dictionaries, each describing a panel. Required keys are
        ``shot_type``, ``subject`` and optionally ``action`` and ``details``.
    style_modifiers: Optional list of style keywords (e.g. "vibrant", "soft",
        "high contrast"). These are appended as a single line at the end of the prompt.
    """
    if panel_count != len(panels):
        raise ValueError("panel_count must equal len(panels)")

    panel_desc_lines = []
    for i, spec in enumerate(panels, start=1):
        panel_desc_lines.append(build_panel_description(i, spec))
    panel_descriptions = "".join(panel_desc_lines).strip()

    if style_modifiers:
        style_mod_line = "Style modifiers: " + ", ".join(style_modifiers)
    else:
        style_mod_line = ""

    prompt = MULTI_PANEL_PROMPT_TEMPLATE.format(
        panel_count=panel_count,
        style_description=style_description,
        panel_descriptions=panel_descriptions,
        style_modifiers=style_mod_line,
    )
    return prompt.strip()

# ---------------------------------------------------------------------------
# Example usage (kept as docstring, not executed on import)
# ---------------------------------------------------------------------------
"""
example_prompt = build_multi_panel_prompt(
    panel_count=5,
    style_description="vibrant digital 2D illustration (manhwa style)",
    panels=[
        {"shot_type": "close‑up", "subject": "female fantasy protagonist", "action": "looking determined", "details": "blue eyes, dark hair"},
        {"shot_type": "wide", "subject": "floating castle city", "action": "at sunrise"},
        {"shot_type": "action", "subject": "hero", "action": "jumping off a cliff toward a giant griffin"},
        {"shot_type": "action", "subject": "hero riding the griffin", "details": "through the clouds"},
        {"shot_type": "close‑up", "subject": "small fairy guide", "action": "pointing at a map while the hero looks on"},
    ],
    style_modifiers=["vibrant", "high contrast", "soft lighting"],
)
print(example_prompt)
"""
