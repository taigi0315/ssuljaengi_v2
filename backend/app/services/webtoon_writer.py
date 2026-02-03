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
                
                # Ensure dialogue is valid (keep as list of dicts, or None)
                if "dialogue" in panel and isinstance(panel["dialogue"], list):
                    # Sanitize dialogue list items if needed
                    valid_dialogue = []
                    for entry in panel["dialogue"]:
                        if isinstance(entry, dict) and "character" in entry and "text" in entry:
                            valid_dialogue.append(entry)
                    panel["dialogue"] = valid_dialogue if valid_dialogue else None
                elif "dialogue" not in panel:
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
        
        # Extract basic character names from story (simple approach)
        story_words = story.split()
        potential_names = [word.strip('.,!?":') for word in story_words if word[0].isupper() and len(word) > 2]
        
        # Create basic characters
        characters = []
        unique_names = list(set(potential_names[:2]))  # Take first 2 unique names
        
        if not unique_names:
            unique_names = ["Character A", "Character B"]
        
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
        
        # Group sentences into scenes (max 3 panels per scene)
        scene_number = 1
        panel_number = 1
        
        for i in range(0, len(story_sentences[:25]), 3):  # Process in groups of 3
            scene_sentences = story_sentences[i:i+3]
            scene_panels = []
            
            for j, sentence in enumerate(scene_sentences):
                panel = WebtoonPanel(
                    panel_number=panel_number,
                    shot_type="Medium Shot" if j % 2 == 0 else "Wide Shot",
                    visual_prompt=f"A scene showing: {sentence[:100]}. Characters in a modern setting with good lighting and clear composition.",
                    active_character_names=[characters[j % len(characters)].name] if characters else [],
                    dialogue=[],
                    negative_prompt="low quality, blurry, dark",
                    composition_notes="Standard composition with clear focus",
                    environment_focus="modern setting",
                    environment_details="Clean, well-lit environment",
                    atmospheric_conditions="Natural lighting",
                    story_beat=f"Story moment {panel_number}",
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
                is_hero_shot=(scene_number == 1),  # Make first scene the hero shot
                hero_video_prompt="Gentle camera movement showing the story beginning" if scene_number == 1 else None
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
                    dialogue=[],
                    negative_prompt="low quality, blurry, dark",
                    composition_notes="Standard wide shot composition",
                    environment_focus="story setting",
                    environment_details="General background environment",
                    atmospheric_conditions="Natural lighting",
                    story_beat=f"Transition {panel_number}",
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
