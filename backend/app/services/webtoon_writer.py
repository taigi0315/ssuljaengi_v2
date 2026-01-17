"""
Webtoon Writer service for converting stories to webtoon scripts.

This module implements the WebtoonWriter service that converts generated stories
into structured webtoon scripts with characters and panels using Gemini LLM.
"""

import logging
import json
from langchain.prompts import ChatPromptTemplate
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
        if "panels" not in result:
            result["panels"] = []
        
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
            
            # Fill missing visual_prompt - THIS IS THE CRITICAL FIX
            if "visual_prompt" not in panel or not panel.get("visual_prompt", "").strip():
                # Generate a basic visual prompt from available data
                char_descriptions = []
                for char_name in panel.get("active_character_names", []):
                    if char_name in char_lookup:
                        char_descriptions.append(f"{char_lookup[char_name]} ({char_name})")
                
                if char_descriptions:
                    panel["visual_prompt"] = f"{panel['shot_type']} of {', '.join(char_descriptions)}"
                else:
                    panel["visual_prompt"] = f"{panel['shot_type']} scene"
                
                logger.warning(f"Panel {panel.get('panel_number', i+1)} had missing visual_prompt, generated default")
            
            # Ensure dialogue is present (can be None)
            if "dialogue" not in panel:
                panel["dialogue"] = None
        
        # Fill missing character fields
        for char in result.get("characters", []):
            # Ensure name exists
            if "name" not in char:
                char["name"] = "Unknown Character"
            
            # Ensure visual_description exists
            if "visual_description" not in char or not char["visual_description"]:
                char["visual_description"] = "A character in the story"
            
            # Try to infer gender if missing
            if "gender" not in char or not char["gender"]:
                desc_lower = char.get("visual_description", "").lower()
                if "woman" in desc_lower or "female" in desc_lower or "she" in desc_lower:
                    char["gender"] = "female"
                elif "man" in desc_lower or "male" in desc_lower or "he" in desc_lower:
                    char["gender"] = "male"
                else:
                    char["gender"] = "unknown"
                logger.warning(f"Character {char['name']} had missing gender, inferred: {char['gender']}")
            
            # Fill other missing fields with placeholders
            if "face" not in char or not char["face"]:
                char["face"] = "distinctive features"
            if "hair" not in char or not char["hair"]:
                char["hair"] = "styled hair"
            if "body" not in char or not char["body"]:
                char["body"] = "average build"
            if "outfit" not in char or not char["outfit"]:
                char["outfit"] = "casual attire"
            if "mood" not in char or not char["mood"]:
                char["mood"] = "neutral demeanor"
        
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
