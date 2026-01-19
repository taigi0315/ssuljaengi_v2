"""
Webtoon Writer service for converting stories to webtoon scripts.

This module implements the WebtoonWriter service that converts generated stories
into structured webtoon scripts with characters and panels using Gemini LLM.
"""

import logging
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.services.llm_config import llm_config
from app.prompt.webtoon_writer import WEBTOON_WRITER_PROMPT
from app.models.story import WebtoonScript
from app.prompt.image_mood import CHARACTER_GENRE_MODIFIERS


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
    
    
    def _fill_missing_fields_in_dict(self, result: dict) -> dict:
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
        
        if "panels" not in result:
            result["panels"] = []
            
        # Critical Fallback: If panels is still empty, create a default start panel
        if not result["panels"]:
            logger.warning("LLM returned empty panels list. Generating fallback panel to prevent crash.")
            result["panels"] = [{
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
            }]
        
        # Create character lookup for visual descriptions
        char_lookup = {}
        for char in result.get("characters", []):
            if "name" in char and "visual_description" in char:
                char_lookup[char["name"]] = char["visual_description"]
        
        # Fill missing panel fields
        for i, panel in enumerate(result.get("panels", [])):
            # Ensure panel_number exists
            if "panel_number" not in panel:
                panel["panel_number"] = i + 1
            
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
                panel["negative_prompt"] = "worst quality, low quality, bad anatomy, text, watermark, close-up portrait, headshot, face-only, zoomed face, cropped body, simple background, plain background, empty space, floating character, studio photo, profile picture, character fills frame, minimal environment, blurred background"
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
                
                logger.warning(f"Panel {panel.get('panel_number', i+1)} had missing or too short visual_prompt, generated rich fallback")
            
            # Ensure dialogue is valid (keep as list of dicts, or None)
            if "dialogue" in panel and isinstance(panel["dialogue"], list):
                # Sanitize dialogue list items if needed
                valid_dialogue = []
                for entry in panel["dialogue"]:
                    if isinstance(entry, dict) and "character" in entry and "text" in entry:
                         valid_dialogue.append(entry)
                panel["dialogue"] = valid_dialogue if valid_dialogue else None
            elif "dialogue" in panel and not isinstance(panel["dialogue"], list) and panel["dialogue"] is not None:
                # If it's a string somehow (shouldn't be with strict prompt), convert to list
                 pass # Or handle if strict fallback needed
            
            if "dialogue" not in panel:
                panel["dialogue"] = None
        
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
            
            # Fill other missing fields with placeholders (New Schema)
            if "age" not in char or not char["age"]:
                char["age"] = "adult"
            if "reference_tag" not in char:
                char["reference_tag"] = f"{char['name']}({char['gender']})"
            
            # New fields defaults
            if "face" not in char:
                char["face"] = ""
            if "hair" not in char:
                char["hair"] = ""
            if "body" not in char:
                char["body"] = ""
            if "outfit" not in char:
                char["outfit"] = char.get("typical_outfit", "Casual attire")
            if "mood" not in char:
                char["mood"] = char.get("personality_brief", "Neutral")
                
            # Legacy fields for compat
            if "appearance_notes" not in char or not char["appearance_notes"]:
                char["appearance_notes"] = "Distinctive features"
            if "typical_outfit" not in char or not char["typical_outfit"]:
                char["typical_outfit"] = char.get("outfit", "Casual attire")
            if "personality_brief" not in char or not char["personality_brief"]:
                char["personality_brief"] = char.get("mood", "Neutral")
            
            # Build visual_description programmatically from all fields
            # This replaces the LLM-generated visual_description
            char["visual_description"] = self._build_visual_description(char)
            logger.info(f"Built visual_description for {char['name']}: {char['visual_description'][:100]}...")
        
        return result
    
    async def convert_story_to_script(self, story: str, genre: str = "MODERN_ROMANCE_DRAMA_MANHWA") -> WebtoonScript:
        """
        Convert a story into a structured webtoon script.
        
        Args:
            story: The generated story text to convert
            genre: The genre key for styling (default: MODERN_ROMANCE_DRAMA_MANHWA)
            
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
            
            # Get genre style prompt
            genre_style = CHARACTER_GENRE_MODIFIERS.get(genre, CHARACTER_GENRE_MODIFIERS["MODERN_ROMANCE_DRAMA_MANHWA"])
            
            # Generate webtoon script
            result = await chain.ainvoke({
                "web_novel_story": story,
                "genre_style": genre_style,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # CRITICAL: Fill missing fields in raw dict BEFORE Pydantic validation
            # This prevents validation errors when LLM returns incomplete data
            result = self._fill_missing_fields_in_dict(result)
            
            # Convert dict to WebtoonScript model (now with all fields filled)
            webtoon_script = WebtoonScript(**result)
            
            logger.info(f"Webtoon script created with {len(webtoon_script.characters)} characters and {len(webtoon_script.panels)} panels")
            
            return webtoon_script
            
        except Exception as e:
            logger.error(f"Webtoon script conversion failed: {str(e)}", exc_info=True)
            raise Exception(f"Webtoon script conversion failed: {str(e)}")


# Global webtoon writer instance
webtoon_writer = WebtoonWriter()
