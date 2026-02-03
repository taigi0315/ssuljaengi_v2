"""
Webtoon Writer service for converting stories to webtoon scripts.

This module implements the WebtoonWriter service that converts generated stories
into structured webtoon scripts with characters and panels using Gemini LLM.
"""

import logging
import json
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.services.llm_config import llm_config
from app.prompt.webtoon_writer import WEBTOON_WRITER_PROMPT
from app.models.story import WebtoonScript
from app.prompt.image_style import VISUAL_STYLE_PROMPTS


logger = logging.getLogger(__name__)


class WebtoonWriter:
    """
    Webtoon Writer service for converting stories to structured scripts.
    
    Uses LangChain with Gemini to transform stories into webtoon scripts
    with character descriptions and panel breakdowns.
    """
    
    def __init__(self):
        """Initialize the webtoon writer with LLM and JSON output parser."""
        self.llm = llm_config.get_model()
        self.parser = JsonOutputParser(pydantic_object=WebtoonScript)
    
    def _build_visual_description(self, char: dict) -> str:
        """
        Programmatically build visual_description from character attributes.
        
        Args:
            char: Character dict with specific fields
            
        Returns:
            Complete visual description string
        """
        parts = []
        
        # Build description using new schema fields first
        if char.get("gender"):
            parts.append(char["gender"])
        if char.get("age"):
            parts.append(f"{char['age']} years old")
            
        # New atomic fields
        if char.get("face"):
            parts.append(f"Face: {char['face']}")
        if char.get("hair"):
            parts.append(f"Hair: {char['hair']}")
        if char.get("body"):
            parts.append(f"Body: {char['body']}")
        if char.get("outfit"):
            parts.append(f"Wearing {char['outfit']}")
        elif char.get("typical_outfit"): # Fallback
            parts.append(f"Wearing {char['typical_outfit']}")
            
        if char.get("mood"):
             parts.append(f"Vibe: {char['mood']}")
        elif char.get("personality_brief"): # Fallback
             parts.append(f"Vibe: {char['personality_brief']}")
        
        # Fallback to legacy appearance_notes if atomic fields are missing
        if not char.get("face") and not char.get("hair") and char.get("appearance_notes"):
             parts.append(char["appearance_notes"])
        
        return ", ".join(parts) if parts else "A character in the story"

    def _normalize_dialogue(self, dialogue: object) -> list[dict] | None:
        """
        Normalize dialogue into the canonical list-of-dicts format.

        Accepts:
        - list[dict] with at least {"character","text"}
        - list[str] like ["Name: ...", "..."]
        - str with newline-separated lines like "Name: ...\\nName2: ..."
        """
        if dialogue is None:
            return None

        def to_entry(text: str, character: str | None, order: int) -> dict:
            return {
                "character": character or "Unknown",
                "text": (text or "").strip(),
                "order": order,
            }

        entries: list[dict] = []

        # list[dict]
        if isinstance(dialogue, list) and dialogue and all(isinstance(x, dict) for x in dialogue):
            order = 1
            for d in dialogue:
                character = d.get("character") if isinstance(d.get("character"), str) else None
                text = d.get("text") if isinstance(d.get("text"), str) else ""
                text = text.strip()
                if not text:
                    continue
                entries.append({
                    "character": character or "Unknown",
                    "text": text,
                    "order": int(d.get("order", order)) if str(d.get("order", "")).isdigit() else order,
                })
                order += 1
            return entries or None

        # list[str]
        if isinstance(dialogue, list) and all(isinstance(x, str) for x in dialogue):
            order = 1
            for line in dialogue:
                line = line.strip()
                if not line:
                    continue
                if ":" in line:
                    speaker, text = line.split(":", 1)
                    speaker = speaker.strip() or None
                    text = text.strip()
                else:
                    speaker, text = None, line
                if not text:
                    continue
                entries.append(to_entry(text=text, character=speaker, order=order))
                order += 1
            return entries or None

        # str
        if isinstance(dialogue, str):
            lines = [ln.strip() for ln in dialogue.splitlines() if ln.strip()]
            if not lines:
                return None
            return self._normalize_dialogue(lines)

        return None

    def _extract_character_names_from_story(self, story: str) -> list[str]:
        """
        Best-effort character name extraction from story text.

        Prioritizes romanized Korean-style hyphenated names like "Ji-hoon", "Min-ji".
        Falls back to capitalized tokens while filtering common non-name headings.
        """
        if not story:
            return []

        stopwords = {
            "episode", "chapter", "prologue", "epilogue", "title",
            "midnight", "encounters", "laundry", "room", "five", "days", "day",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "part", "scene", "act",
        }

        # 1) Hyphenated names: allow second segment lowercase (Min-ji) or titlecase (Min-Ji)
        hyphenated = []
        for m in re.finditer(r"\b([A-Z][a-z]{1,20})-([a-z]{1,20}|[A-Z][a-z]{1,20})\b", story):
            full = m.group(0)
            if full.lower() in stopwords:
                continue
            hyphenated.append(full)

        # De-duplicate while preserving order
        seen = set()
        ordered = []
        for name in hyphenated:
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            # Normalize first letter uppercase (handles "min-ji")
            ordered.append(name[0].upper() + name[1:])

        if ordered:
            return ordered[:6]

        # 2) Capitalized tokens fallback (preserve order, filter stopwords)
        tokens = []
        for m in re.finditer(r"\b[A-Z][a-z]{2,}\b", story):
            t = m.group(0)
            if t.lower() in stopwords:
                continue
            tokens.append(t)

        seen.clear()
        ordered2 = []
        for t in tokens:
            key = t.lower()
            if key in seen:
                continue
            seen.add(key)
            ordered2.append(t)

        return ordered2[:6]

    def _extract_dialogue_pairs_from_story(self, story: str) -> list[tuple[str | None, str]]:
        """
        Extract dialogue as (speaker, text) pairs from story.

        Supports:
        - `Name: "..."` / `Name: ...`
        - Quoted lines `"..."` or `“...”` (speaker unknown)
        """
        if not story:
            return []

        pairs: list[tuple[str | None, str]] = []

        # 1) Name: line
        for line in story.splitlines():
            line = line.strip()
            if not line:
                continue
            m = re.match(r"^([A-Za-z][A-Za-z\\- ]{1,40})\\s*:\\s*(.+)$", line)
            if m:
                speaker = m.group(1).strip()
                text = m.group(2).strip().strip("\"“”")
                if text:
                    pairs.append((speaker, text))

        # 2) Quoted lines (speaker unknown)
        quote_pattern = re.compile(r'“([^”]+)”|"([^"]+)"')
        for a, b in quote_pattern.findall(story):
            q = (a or b or "").strip()
            if q:
                pairs.append((None, q))

        # De-dupe while preserving order
        seen = set()
        out: list[tuple[str | None, str]] = []
        for speaker, text in pairs:
            key = (speaker or "", text)
            if key in seen:
                continue
            seen.add(key)
            out.append((speaker, text))
        return out

    def _story_contains_name(self, story: str, name: str) -> bool:
        if not story or not name:
            return False
        return name.lower() in story.lower()

    def _maybe_fix_character_names_from_story(self, result: dict, original_story: str | None) -> dict:
        """
        If the model/fallback produced obvious non-character names (e.g., 'Episode', 'Midnight')
        and the original story contains better names, replace characters (and active_character_names)
        with extracted names.
        """
        if not original_story or not original_story.strip():
            return result

        extracted = self._extract_character_names_from_story(original_story)
        if len(extracted) < 1:
            return result

        characters = result.get("characters") or []
        if not isinstance(characters, list) or not characters:
            return result

        stopwords = {
            "episode", "chapter", "prologue", "epilogue", "title",
            "midnight", "encounters", "laundry", "room", "five", "days", "day",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "part", "scene", "act",
        }

        # If at least one existing character name (that isn't a heading/stopword) appears in the story, don't override.
        if any(
            self._story_contains_name(original_story, c.get("name", ""))
            and str(c.get("name", "")).strip().lower() not in stopwords
            for c in characters
            if isinstance(c, dict)
        ):
            return result

        # Replace only up to existing character count
        mapping: dict[str, str] = {}
        for i, c in enumerate(characters):
            if not isinstance(c, dict):
                continue
            new_name = extracted[i] if i < len(extracted) else None
            old_name = c.get("name")
            if isinstance(old_name, str) and new_name and old_name != new_name:
                mapping[old_name] = new_name
                c["name"] = new_name
                c["reference_tag"] = new_name.upper().replace(" ", "_")

        # Update active_character_names in panels/scenes if present
        for scene in (result.get("scenes") or []):
            if not isinstance(scene, dict):
                continue
            for panel in (scene.get("panels") or []):
                if not isinstance(panel, dict):
                    continue
                names = panel.get("active_character_names")
                if not isinstance(names, list):
                    continue
                panel["active_character_names"] = [mapping.get(n, n) for n in names if isinstance(n, str)]

                dialogue = panel.get("dialogue")
                if isinstance(dialogue, list):
                    for d in dialogue:
                        if isinstance(d, dict) and isinstance(d.get("character"), str):
                            d["character"] = mapping.get(d["character"], d["character"])

        return result

    def _backfill_dialogue_from_story(self, result: dict, original_story: str | None) -> dict:
        """
        If dialogue coverage is too low, populate missing panel dialogue from the original story
        using extracted dialogue lines (no additional model calls).
        """
        if not original_story or not original_story.strip():
            return result

        pairs = self._extract_dialogue_pairs_from_story(original_story)
        if not pairs:
            return result

        # Flatten panels in order
        panels: list[dict] = []
        for scene in (result.get("scenes") or []):
            if not isinstance(scene, dict):
                continue
            for panel in (scene.get("panels") or []):
                if isinstance(panel, dict):
                    panels.append(panel)

        if not panels:
            return result

        # Compute current coverage
        def has_dialogue(p: dict) -> bool:
            d = p.get("dialogue")
            return isinstance(d, list) and len(d) > 0

        with_dialogue = sum(1 for p in panels if has_dialogue(p))
        if with_dialogue / max(1, len(panels)) >= 0.6:
            return result

        # Create queue of (speaker,text)
        queue = pairs.copy()

        # Known characters (for normalization)
        known = []
        for c in (result.get("characters") or []):
            if isinstance(c, dict) and isinstance(c.get("name"), str):
                known.append(c["name"])

        def normalize_speaker(speaker: str | None, fallback: str | None) -> str:
            if speaker:
                # exact match
                for k in known:
                    if speaker.lower() == k.lower():
                        return k
                # substring match (handles small variations)
                for k in known:
                    if speaker.lower() in k.lower() or k.lower() in speaker.lower():
                        return k
                return speaker
            return fallback or (known[0] if known else "Unknown")

        for p in panels:
            if has_dialogue(p):
                continue
            active = p.get("active_character_names")
            if not isinstance(active, list) or not active:
                continue
            speaker_fallback = next((a for a in active if isinstance(a, str)), None)
            if not queue:
                break
            speaker, text = queue.pop(0)
            speaker_norm = normalize_speaker(speaker, speaker_fallback)
            p["dialogue"] = [{"character": speaker_norm, "text": text[:220], "order": 1}]

        return result
    
    
    def _fill_missing_fields_in_dict(
        self,
        result: dict,
        original_story: str | None = None,
        story_genre: str | None = None,
        image_style: str | None = None,
    ) -> dict:
        """
        Fill in missing fields in the raw dict BEFORE Pydantic validation.
        
        This is critical because Pydantic validates during __init__, so we must
        ensure all required fields exist in the dict before creating the model.
        
        Args:
            result: Raw dict from LLM with potential missing fields
            
        Returns:
            Dict with all fields filled and ready for Pydantic validation
        """
        # Ensure top-level keys exist
        if "characters" not in result:
            result["characters"] = []
        # Handle potential key mismatch (LLM might return 'scenes' instead of 'panels')
        if "panels" not in result and "scenes" in result:
            result["panels"] = result.pop("scenes")
            # Renaming scene_number to panel_number inside panels if needed
            for p in result["panels"]:
                if "scene_number" in p and "panel_number" not in p:
                    p["panel_number"] = p.pop("scene_number")
        
        # Handle both old (panels) and new (scenes) structure
        if "scenes" not in result and "panels" in result:
            # Convert old flat panel structure to new scene structure
            panels = result.get("panels", [])
            scenes = []
            
            # Group panels into scenes (max 3 panels per scene)
            current_scene_panels = []
            scene_number = 1
            
            for panel in panels:
                current_scene_panels.append(panel)
                
                # Create a new scene when we have 3 panels or reach the end
                if len(current_scene_panels) >= 3 or panel == panels[-1]:
                    scene = {
                        "scene_number": scene_number,
                        "scene_type": "story",
                        "scene_title": f"Scene {scene_number}",
                        "panels": current_scene_panels,
                        "is_hero_shot": False,
                        "hero_video_prompt": None
                    }
                    scenes.append(scene)
                    current_scene_panels = []
                    scene_number += 1
            
            result["scenes"] = scenes
            # Remove old panels key
            if "panels" in result:
                del result["panels"]
        
        # Ensure scenes exist
        if "scenes" not in result:
            result["scenes"] = []

        # If the model produced obviously wrong names and the story has better ones, fix now.
        result = self._maybe_fix_character_names_from_story(result, original_story)
            
        # Critical Fallback: If scenes is still empty, generate a robust fallback (NOT a single panel)
        if not result["scenes"]:
            if original_story and original_story.strip():
                logger.warning(
                    "LLM returned empty scenes list. Generating robust fallback script from the original story "
                    "(prevents 1-panel outputs)."
                )
                fallback = self._create_fallback_script(
                    original_story,
                    story_genre or "MODERN_ROMANCE_DRAMA",
                    image_style or "SOFT_ROMANTIC_WEBTOON",
                )
                return fallback.model_dump()

            logger.warning("LLM returned empty scenes list and no original story provided. Generating minimal fallback scene.")
            result["scenes"] = [{
                "scene_number": 1,
                "scene_type": "story",
                "scene_title": "Opening Scene",
                "panels": [{
                    "panel_number": 1,
                    "shot_type": "Wide Shot",
                    "visual_prompt": "An establishing shot of the setting.",
                    "composition_notes": "Standard wide shot",
                    "environment_focus": "Story setting",
                    "environment_details": "General background",
                    "atmospheric_conditions": "Neutral lighting",
                    "active_character_names": [],
                    "character_placement_and_action": "None",
                    "character_frame_percentage": 0,
                    "environment_frame_percentage": 100,
                    "story_beat": "Introduction",
                    "negative_prompt": "low quality, text, watermark",
                    "dialogue": None
                }],
                "is_hero_shot": False,
                "hero_video_prompt": None
            }]
        
        # Create character lookup for visual descriptions
        char_lookup = {}
        for char in result.get("characters", []):
            if "name" in char and "visual_description" in char:
                char_lookup[char["name"]] = char["visual_description"]
        
        # Fill missing fields for each scene and its panels
        for scene_idx, scene in enumerate(result.get("scenes", [])):
            # Ensure scene fields exist
            if "scene_number" not in scene:
                scene["scene_number"] = scene_idx + 1
            if "scene_type" not in scene:
                scene["scene_type"] = "story"
            if "scene_title" not in scene:
                scene["scene_title"] = f"Scene {scene['scene_number']}"
            if "panels" not in scene:
                scene["panels"] = []
            if "is_hero_shot" not in scene:
                scene["is_hero_shot"] = False
            if "hero_video_prompt" not in scene:
                scene["hero_video_prompt"] = None
            
            # Fill missing panel fields within each scene
            for panel_idx, panel in enumerate(scene.get("panels", [])):
                # Ensure panel_number exists (will be set properly later)
                if "panel_number" not in panel:
                    panel["panel_number"] = panel_idx + 1
                
                # Ensure shot_type exists
                if "shot_type" not in panel or not panel["shot_type"]:
                    panel["shot_type"] = "Medium Shot"
                
                # Ensure active_character_names exists
                if "active_character_names" not in panel:
                    panel["active_character_names"] = []
                
                # Fill missing cinematic fields first so we can use them for visual_prompt fallback
                if "composition_notes" not in panel:
                    panel["composition_notes"] = f"{panel['shot_type']} composition"
                if "environment_focus" not in panel:
                    panel["environment_focus"] = "Scene background"
                if "environment_details" not in panel:
                    panel["environment_details"] = "Detailed background environment"
                if "atmospheric_conditions" not in panel:
                    panel["atmospheric_conditions"] = "Standard lighting"
                if "story_beat" not in panel:
                    panel["story_beat"] = "Scene action"
                if "negative_prompt" not in panel:
                    panel["negative_prompt"] = (
                        "worst quality, low quality, blurry, bad anatomy, malformed hands, extra fingers, extra limbs, "
                        "distorted face, duplicated face, "
                        "text, speech bubbles, thought bubbles, dialogue bubbles, captions, subtitles, "
                        "watermark, logo, UI, "
                        "device frame, border, "
                        "photorealistic studio portrait, passport photo, profile picture, "
                        "plain empty background"
                    )
                if "character_frame_percentage" not in panel:
                    panel["character_frame_percentage"] = 40
                if "environment_frame_percentage" not in panel:
                    panel["environment_frame_percentage"] = 60
                
                if "character_placement_and_action" not in panel:
                    # Try to build a better default action
                    char_names = panel.get("active_character_names", [])
                    if char_names:
                        panel["character_placement_and_action"] = f"{', '.join(char_names)} in the scene"
                    else:
                        panel["character_placement_and_action"] = "No characters present"
                
                # Fill missing visual_prompt - RICH FALLBACK
                if "visual_prompt" not in panel or not panel.get("visual_prompt", "").strip() or len(panel.get("visual_prompt", "")) < 20: 
                    # Check for "less than 20 chars" to catch broken "Medium Shot" type prompts
                    
                    # Generate a rich visual prompt from available data
                    parts = []
                    parts.append(f"{panel['shot_type']}, vertical 9:16 webtoon panel")
                    parts.append(panel['composition_notes'])
                    parts.append(panel['environment_details'])
                    
                    # Add characters with descriptions if not properly in placement_and_action
                    if "character_placement_and_action" in panel and len(panel["character_placement_and_action"]) > 20:
                        parts.append(panel["character_placement_and_action"])
                    else:
                        # Fallback character descriptions
                        char_descriptions = []
                        for char_name in panel.get("active_character_names", []):
                            if char_name in char_lookup:
                                char_descriptions.append(f"{char_lookup[char_name]} ({char_name})")
                        if char_descriptions:
                            parts.append(f"Characters: {', '.join(char_descriptions)}")

                    parts.append(panel['atmospheric_conditions'])
                    parts.append("manhwa style, cinematic depth, high quality")
                    
                    panel["visual_prompt"] = ", ".join(parts)
                    
                    logger.warning(f"Panel {panel.get('panel_number', panel_idx+1)} had missing or too short visual_prompt, generated rich fallback")
                
                # Normalize dialogue into list-of-dicts (or None)
                if "dialogue" in panel:
                    panel["dialogue"] = self._normalize_dialogue(panel.get("dialogue"))
                else:
                    panel["dialogue"] = None

        # If dialogue coverage is still very low, backfill from the original story (no model calls)
        result = self._backfill_dialogue_from_story(result, original_story)
        
        # Fill missing character fields
        for char in result.get("characters", []):
            # Ensure name exists
            if "name" not in char:
                char["name"] = "Unknown Character"
            
            # Try to infer gender if missing
            if "gender" not in char or not char["gender"]:
                # Try to infer from other fields
                all_text = f"{char.get('appearance_notes', '')} {char.get('personality_brief', '')}".lower()
                if "woman" in all_text or "female" in all_text or "she" in all_text:
                    char["gender"] = "female"
                elif "man" in all_text or "male" in all_text or "he" in all_text:
                    char["gender"] = "male"
                else:
                    char["gender"] = "unknown"
                logger.warning(f"Character {char['name']} had missing gender, inferred: {char['gender']}")
            
            # Fill other missing character fields with placeholders
            if "reference_tag" not in char:
                char["reference_tag"] = char["name"].upper().replace(" ", "_")
            if "age" not in char:
                char["age"] = "20"
            if "face" not in char:
                char["face"] = "Friendly features, expressive eyes"
            if "hair" not in char:
                char["hair"] = "Medium length, natural color"
            if "body" not in char:
                char["body"] = "Average build"
            if "outfit" not in char:
                char["outfit"] = "Casual modern clothing"
            if "mood" not in char:
                char["mood"] = "neutral"
            
            # Build visual_description if missing
            if "visual_description" not in char or not char["visual_description"]:
                desc_parts = [
                    f"{char['gender']}, {char['age']} years old",
                    f"Face: {char['face']}",
                    f"Hair: {char['hair']}",
                    f"Body: {char['body']}",
                    f"Outfit: {char['outfit']}",
                    f"Mood: {char['mood']}"
                ]
                char["visual_description"] = ", ".join(desc_parts)
                logger.info(f"Built visual_description for {char['name']}: {char['visual_description'][:100]}...")
        
        return result
    
    def _create_fallback_script(self, story: str, story_genre: str, image_style: str) -> WebtoonScript:
        """
        Create a minimal fallback script when content is blocked by safety filters.
        
        Args:
            story: The original story
            story_genre: The story genre
            image_style: The image style
            
        Returns:
            A minimal WebtoonScript
        """
        from app.models.story import WebtoonScript, Character, WebtoonPanel, WebtoonScene
        
        # Extract character names (prefer hyphenated names like Ji-hoon, Min-ji)
        extracted_names = self._extract_character_names_from_story(story)

        # Create basic characters
        characters = []
        unique_names = extracted_names[:2]

        if len(unique_names) < 2:
            unique_names = (unique_names + ["Character A", "Character B"])[:2]
        
        for i, name in enumerate(unique_names):
            character = Character(
                name=name,
                reference_tag=name.upper().replace(" ", "_"),
                gender="female" if i % 2 == 0 else "male",
                age="20",
                face="Friendly features, expressive eyes",
                hair="Medium length, natural color",
                body="Average build",
                outfit="Casual modern clothing",
                mood="neutral",
                visual_description=f"{name} is a young person with friendly features and casual style."
            )
            characters.append(character)
        
        # Create scenes with panels (aim for at least 20 panels total)
        scenes = []
        story_sentences = [s.strip() for s in story.replace('.', '.|').replace('!', '!|').replace('?', '?|').split('|') if s.strip()]

        # Extract quoted dialogue (best-effort) to populate panels
        quote_pattern = re.compile(r'“([^”]+)”|\"([^\"]+)\"')
        quote_queue = []
        for a, b in quote_pattern.findall(story):
            q = (a or b or "").strip()
            if q:
                quote_queue.append(q)

        high_intensity_keywords = [
            "kiss", "confess", "confession", "i love you", "breakup", "goodbye",
            "reveal", "truth", "caught", "betray", "betrayal", "scream", "cry", "tears",
            "gun", "knife", "blood", "death", "accident", "collapse"
        ]
        medium_intensity_keywords = [
            "argue", "fight", "panic", "shock", "surprise", "hug", "embrace", "touch",
            "slap", "run", "chase", "threat", "secret"
        ]

        def estimate_intensity(text: str) -> int:
            t = text.lower()
            intensity = 4
            if any(k in t for k in high_intensity_keywords):
                intensity = 9
            elif any(k in t for k in medium_intensity_keywords):
                intensity = 7
            if "!" in text:
                intensity = min(10, intensity + 1)
            if "?" in text:
                intensity = min(10, max(intensity, 6))
            return max(1, min(10, intensity))

        def pick_speaker(sentence: str, default_idx: int) -> str:
            for c in characters:
                if c.name.lower() in sentence.lower():
                    return c.name
            return characters[default_idx % len(characters)].name

        def synthesize_dialogue(intensity: int) -> str:
            if intensity >= 9:
                return "Tell me the truth."
            if intensity >= 8:
                return "Don't leave."
            if intensity >= 7:
                return "What are you doing here?"
            if intensity >= 6:
                return "Are you okay?"
            if intensity >= 5:
                return "We need to talk."
            return "Hey."

        def make_dialogue(sentence: str, default_idx: int, intensity: int, has_characters: bool) -> list[dict] | None:
            if not has_characters:
                return None

            # Common web novel dialogue pattern: "Name: ..."
            m = re.match(r'^\s*([A-Z][\w ]{1,30})\s*:\s*(.+)\s*$', sentence)
            if m:
                speaker = m.group(1).strip()
                text = m.group(2).strip()
                if text:
                    return [{"character": speaker, "text": text[:200], "order": 1}]

            # ONLY treat "Name - ..." as dialogue when dash has spaces around it
            m = re.match(r'^\s*([A-Z][\w ]{1,30})\s+[—–-]\s+(.+)\s*$', sentence)
            if m:
                speaker = m.group(1).strip()
                text = m.group(2).strip()
                if text:
                    return [{"character": speaker, "text": text[:200], "order": 1}]

            # Prefer global quote queue (keeps dialogue coverage high)
            if quote_queue:
                speaker = pick_speaker(sentence, default_idx)
                q = quote_queue.pop(0)
                return [{"character": speaker, "text": q[:220], "order": 1}]

            # As a last resort, synthesize a short spoken line (better than empty UI)
            speaker = pick_speaker(sentence, default_idx)
            return [{"character": speaker, "text": synthesize_dialogue(intensity), "order": 1}]
        
        # Group sentences into scenes (max 3 panels per scene)
        scene_number = 1
        panel_number = 1
        hero_candidate: tuple[int, int] | None = None  # (scene_index, panel_index)
        hero_score = -1
        
        for i in range(0, len(story_sentences[:25]), 3):  # Process in groups of 3
            scene_sentences = story_sentences[i:i+3]
            scene_panels = []
            
            for j, sentence in enumerate(scene_sentences):
                intensity = estimate_intensity(sentence)
                if intensity > hero_score:
                    hero_score = intensity
                    hero_candidate = (len(scenes), len(scene_panels))

                shot_type = "Wide Shot" if (j == 0 and scene_number == 1) else ("Close-Up" if intensity >= 8 else ("Medium Shot" if j % 2 == 0 else "Wide Shot"))

                panel = WebtoonPanel(
                    panel_number=panel_number,
                    shot_type=shot_type,
                    visual_prompt=f"A scene showing: {sentence[:100]}. Characters in a modern setting with good lighting and clear composition.",
                    active_character_names=[characters[j % len(characters)].name] if characters else [],
                    dialogue=make_dialogue(
                        sentence,
                        default_idx=j,
                        intensity=intensity,
                        has_characters=bool(characters),
                    ),
                    negative_prompt="low quality, blurry, dark",
                    composition_notes="Standard composition with clear focus",
                    environment_focus="modern setting",
                    environment_details="Clean, well-lit environment",
                    atmospheric_conditions="Natural lighting",
                    story_beat=sentence[:200],
                    emotional_intensity=intensity,
                    character_placement_and_action="Character positioned naturally in scene",
                    character_frame_percentage=40,
                    environment_frame_percentage=60,
                    style_variation=None
                )
                scene_panels.append(panel)
                panel_number += 1
            
            scene = WebtoonScene(
                scene_number=scene_number,
                scene_type="story" if scene_number % 3 == 1 else "bridge",
                scene_title=f"Scene {scene_number}",
                panels=scene_panels,
                is_hero_shot=False,
                hero_video_prompt=None
            )
            scenes.append(scene)
            scene_number += 1
        
        # Ensure we have at least 7 scenes (to get 20+ panels)
        while len(scenes) < 7:
            scene_panels = []
            for j in range(3):  # 3 panels per scene
                panel = WebtoonPanel(
                    panel_number=panel_number,
                    shot_type="Wide Shot",
                    visual_prompt=f"A transitional scene showing the story environment. Panel {panel_number} of the narrative sequence.",
                    active_character_names=[],
                    dialogue=None,
                    negative_prompt="low quality, blurry, dark",
                    composition_notes="Standard wide shot composition",
                    environment_focus="story setting",
                    environment_details="General background environment",
                    atmospheric_conditions="Natural lighting",
                    story_beat=f"Transition moment {panel_number}",
                    emotional_intensity=3,
                    character_placement_and_action="Environmental focus",
                    character_frame_percentage=20,
                    environment_frame_percentage=80,
                    style_variation=None
                )
                scene_panels.append(panel)
                panel_number += 1
            
            scene = WebtoonScene(
                scene_number=scene_number,
                scene_type="bridge",
                scene_title=f"Transition Scene {scene_number}",
                panels=scene_panels,
                is_hero_shot=False,
                hero_video_prompt=None
            )
            scenes.append(scene)
            scene_number += 1

        # Mark hero shot as the most intense panel (fallback heuristic)
        if hero_candidate:
            s_idx, p_idx = hero_candidate
            if 0 <= s_idx < len(scenes) and 0 <= p_idx < len(scenes[s_idx].panels):
                scenes[s_idx].is_hero_shot = True
                scenes[s_idx].hero_video_prompt = (
                    "Slow vertical push-in emphasizing the most dramatic moment; "
                    "subtle parallax on foreground/background; hold on the key expression/detail."
                )
        
        total_panels = sum(len(scene.panels) for scene in scenes)
        logger.info(f"Created fallback script with {len(characters)} characters, {len(scenes)} scenes, and {total_panels} panels")
        
        return WebtoonScript(characters=characters, scenes=scenes)
    
    async def convert_story_to_script(self, story: str, story_genre: str, image_style: str = "SOFT_ROMANTIC_WEBTOON") -> WebtoonScript:
        """
        Convert a story into a structured webtoon script.
        
        Args:
            story: The generated story text to convert
            story_genre: The genre style of the story (e.g. MODERN_ROMANCE_DRAMA)
            image_style: The visual style key for styling (default: SOFT_ROMANTIC_WEBTOON)
            
        Returns:
            WebtoonScript with characters and panels
            
        Raises:
            Exception: If conversion fails
        """
        try:
            logger.info("Converting story to webtoon script")
            
            # Create prompt with format instructions
            prompt = ChatPromptTemplate.from_template(
                WEBTOON_WRITER_PROMPT + "\n\n{format_instructions}\n\nReturn ONLY valid JSON, no markdown formatting."
            )
            
            # Use JSON output parser chain
            chain = prompt | self.llm | self.parser
            # Generate webtoon script
            result = await chain.ainvoke({
                "web_novel_story": story,
                "story_genre": story_genre,
                "image_style": image_style,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Handle edge case where LLM returns a list instead of a dict
            if isinstance(result, list):
                logger.warning(f"LLM returned a list of type {type(result)}. Attempting to extract dictionary.")
                if result and isinstance(result[0], dict):
                    result = result[0]
                else:
                    logger.warning("List was empty or didn't contain dict. Using empty dict to force fallback.")
                    result = {}
            
            # CRITICAL: Fill missing fields in raw dict BEFORE Pydantic validation
            # This prevents validation errors when LLM returns incomplete data
            result = self._fill_missing_fields_in_dict(
                result,
                original_story=story,
                story_genre=story_genre,
                image_style=image_style,
            )
            
            # Convert dict to WebtoonScript model (now with all fields filled)
            webtoon_script = WebtoonScript(**result)
            
            logger.info(f"Webtoon script created with {len(webtoon_script.characters)} characters and {len(webtoon_script.panels)} panels")
            
            return webtoon_script
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if this is a content blocking issue
            if "prohibited_content" in error_msg or "blocked" in error_msg or "safety" in error_msg:
                logger.warning(f"Content was blocked by safety filters. Creating minimal fallback script. Error: {str(e)}")
                
                # Create a minimal fallback script
                fallback_script = self._create_fallback_script(story, story_genre, image_style)
                return fallback_script
            
            logger.error(f"Webtoon script conversion failed: {str(e)}", exc_info=True)
            raise Exception(f"Webtoon script conversion failed: {str(e)}")


# Global webtoon writer instance
webtoon_writer = WebtoonWriter()
