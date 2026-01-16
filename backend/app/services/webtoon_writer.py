"""
Webtoon Writer service for converting stories to webtoon scripts.

This module implements the WebtoonWriter service that converts generated stories
into structured webtoon scripts with characters and panels using Gemini LLM.
"""

import logging
import json
from typing import Dict, Any
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.llm_config import llm_config
from app.prompt.webtoon_writer import WEBTOON_WRITER_PROMPT
from app.models.story import WebtoonScript, Character, WebtoonPanel


logger = logging.getLogger(__name__)


class WebtoonWriter:
    """
    Webtoon Writer service for converting stories to structured scripts.
    
    Uses LangChain with Gemini to transform stories into webtoon scripts
    with character descriptions and panel breakdowns.
    """
    
    def __init__(self):
        """Initialize the webtoon writer with LLM."""
        self.llm = llm_config.get_model()
    
    async def convert_story_to_script(self, story: str) -> WebtoonScript:
        """
        Convert a story into a structured webtoon script.
        
        Args:
            story: The generated story text to convert
            
        Returns:
            WebtoonScript with characters and panels
            
        Raises:
            Exception: If conversion fails
        """
        try:
            logger.info("Converting story to webtoon script")
            
            # Create prompt
            prompt = ChatPromptTemplate.from_template(WEBTOON_WRITER_PROMPT)
            chain = prompt | self.llm | StrOutputParser()
            
            # Generate webtoon script
            response = await chain.ainvoke({
                "web_novel_story": story
            })
            
            logger.info("Webtoon script generated, parsing JSON")
            
            # Parse JSON response
            script_data = self._parse_response(response)
            
            # Convert to WebtoonScript model
            webtoon_script = self._create_webtoon_script(script_data)
            
            logger.info(f"Webtoon script created with {len(webtoon_script.characters)} characters and {len(webtoon_script.panels)} panels")
            
            return webtoon_script
            
        except Exception as e:
            logger.error(f"Webtoon script conversion failed: {str(e)}", exc_info=True)
            raise Exception(f"Webtoon script conversion failed: {str(e)}")
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response to extract JSON.
        
        Args:
            response: Raw LLM response text
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            ValueError: If JSON parsing fails
        """
        try:
            # Try to find JSON in response
            # LLM might wrap JSON in markdown code blocks
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            
            if response.endswith("```"):
                response = response[:-3]
            
            response = response.strip()
            
            # Parse JSON
            data = json.loads(response)
            
            # Validate required fields
            if "characters" not in data or "panels" not in data:
                raise ValueError("Missing required fields: characters or panels")
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            logger.error(f"Response: {response[:500]}")
            raise ValueError(f"Failed to parse JSON response: {str(e)}")
    
    def _create_webtoon_script(self, data: Dict[str, Any]) -> WebtoonScript:
        """
        Create WebtoonScript model from parsed data.
        
        Args:
            data: Parsed JSON dictionary
            
        Returns:
            WebtoonScript model instance
        """
        # Parse characters
        characters = [
            Character(
                name=char["name"],
                visual_description=char["visual_description"]
            )
            for char in data["characters"]
        ]
        
        # Parse panels
        panels = [
            WebtoonPanel(
                panel_number=panel["panel_number"],
                shot_type=panel["shot_type"],
                active_character_names=panel["active_character_names"],
                visual_prompt=panel["visual_prompt"],
                dialogue=panel.get("dialogue")
            )
            for panel in data["panels"]
        ]
        
        return WebtoonScript(
            characters=characters,
            panels=panels
        )


# Global webtoon writer instance
webtoon_writer = WebtoonWriter()
