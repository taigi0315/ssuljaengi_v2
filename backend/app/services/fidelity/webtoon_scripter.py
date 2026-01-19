"""
Webtoon Scripter service for fidelity validation workflow.

Node 2: Converts story to webtoon panels. On subsequent iterations,
uses critique from the evaluator to improve panel clarity without
changing the underlying story.
"""

import json
import logging
from typing import Dict, List, Any, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.services.llm_config import llm_config
from app.models.fidelity_state import PanelData, CharacterData
from app.prompt.fidelity import SCRIPTER_INITIAL_PROMPT, SCRIPTER_REVISION_PROMPT


logger = logging.getLogger(__name__)


# ============================================================================
# Output Schema
# ============================================================================

class DialogueSchema(BaseModel):
    """Schema for dialogue line."""
    character: str = Field(description="Character speaking")
    text: str = Field(description="What they say")


class PanelSchema(BaseModel):
    """Schema for a single panel."""
    panel_number: int = Field(description="Sequential panel number")
    visual_description: str = Field(description="What the reader sees")
    dialogue: List[DialogueSchema] = Field(default_factory=list)
    shot_type: str = Field(default="Medium Shot")
    environment: str = Field(default="")


class CharacterSchema(BaseModel):
    """Schema for character definition."""
    name: str = Field(description="Character name")
    visual_description: str = Field(description="Visual appearance")


class ScripterOutputSchema(BaseModel):
    """Schema for scripter output."""
    characters: List[CharacterSchema] = Field(description="Character definitions")
    panels: List[PanelSchema] = Field(description="Panel sequence")


# ============================================================================
# Service Class
# ============================================================================

class WebtoonScripter:
    """
    Webtoon Scripter service (Node 2).

    Converts stories into webtoon panels. Handles both initial conversion
    and revision based on evaluator feedback.
    """

    def __init__(self):
        """Initialize with LLM configuration."""
        self.llm = llm_config.get_model()
        self.initial_prompt = ChatPromptTemplate.from_template(SCRIPTER_INITIAL_PROMPT)
        self.revision_prompt = ChatPromptTemplate.from_template(SCRIPTER_REVISION_PROMPT)
        self.parser = JsonOutputParser(pydantic_object=ScripterOutputSchema)

    async def convert_to_panels(
        self,
        story: str,
        character_motivations: Dict[str, Dict[str, str]],
        key_conflicts: List[str]
    ) -> Dict[str, Any]:
        """
        Convert a story to webtoon panels (initial conversion).

        Args:
            story: The full narrative text
            character_motivations: Dict mapping character names to their motivations
            key_conflicts: List of conflicts that must be shown

        Returns:
            Dictionary with 'characters' and 'panels' lists

        Raises:
            Exception: If conversion fails
        """
        try:
            # Format character motivations for prompt
            motivations_text = self._format_motivations(character_motivations)
            conflicts_text = "\n".join(f"- {c}" for c in key_conflicts)

            chain = self.initial_prompt | self.llm | self.parser

            result = await chain.ainvoke({
                "story": story,
                "character_motivations": motivations_text,
                "key_conflicts": conflicts_text
            })

            # Validate and fill missing fields
            result = self._validate_and_fill(result)

            return result

        except Exception as e:
            logger.error(f"Panel conversion failed: {str(e)}")
            raise Exception(f"Panel conversion failed: {str(e)}")

    async def revise_panels(
        self,
        current_panels: List[Dict],
        current_characters: List[Dict],
        critique: str,
        information_gaps: List[Dict],
        character_motivations: Dict[str, Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Revise panels based on evaluator feedback.

        Args:
            current_panels: Current panel list
            current_characters: Current character definitions
            critique: Overall critique from evaluator
            information_gaps: Specific gaps identified
            character_motivations: Original character motivations

        Returns:
            Revised dictionary with 'characters' and 'panels'

        Raises:
            Exception: If revision fails
        """
        try:
            # Format current panels as JSON for the prompt
            current_script = {
                "characters": current_characters,
                "panels": current_panels
            }
            panels_json = json.dumps(current_script, indent=2)

            # Format gaps for prompt
            specific_gaps = self._format_gaps(information_gaps)
            motivations_text = self._format_motivations(character_motivations)

            chain = self.revision_prompt | self.llm | self.parser

            result = await chain.ainvoke({
                "current_panels": panels_json,
                "critique": critique,
                "specific_gaps": specific_gaps,
                "character_motivations": motivations_text
            })

            # Validate and fill missing fields
            result = self._validate_and_fill(result)

            return result

        except Exception as e:
            logger.error(f"Panel revision failed: {str(e)}")
            raise Exception(f"Panel revision failed: {str(e)}")

    def _format_motivations(self, motivations: Dict[str, Dict[str, str]]) -> str:
        """Format character motivations for prompt."""
        lines = []
        for name, data in motivations.items():
            goal = data.get("goal", "Unknown")
            motivation = data.get("motivation", "Unknown")
            obstacle = data.get("obstacle", "Unknown")
            lines.append(f"- {name}:")
            lines.append(f"  Goal: {goal}")
            lines.append(f"  Motivation: {motivation}")
            lines.append(f"  Obstacle: {obstacle}")
        return "\n".join(lines) if lines else "No specific motivations defined."

    def _format_gaps(self, gaps: List[Dict]) -> str:
        """Format information gaps for prompt."""
        if not gaps:
            return "No specific gaps identified."

        lines = []
        for i, gap in enumerate(gaps, 1):
            severity = gap.get("severity", "unknown")
            category = gap.get("category", "unknown")
            original = gap.get("original_element", "Unknown element")
            reader = gap.get("reader_interpretation", "Not understood")
            fix = gap.get("suggested_fix", "Clarify this element")

            lines.append(f"\n{i}. [{severity.upper()}] {category.title()} Gap:")
            lines.append(f"   Original: {original}")
            lines.append(f"   Reader saw: {reader}")
            lines.append(f"   Fix: {fix}")

        return "\n".join(lines)

    def _validate_and_fill(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and fill missing fields in the result.

        Args:
            result: Raw LLM output

        Returns:
            Validated result with all required fields
        """
        # Ensure characters list exists
        if "characters" not in result:
            result["characters"] = []

        # Ensure panels list exists
        if "panels" not in result:
            result["panels"] = []

        # Fill character fields
        for char in result["characters"]:
            if "name" not in char:
                char["name"] = "Unknown Character"
            if "visual_description" not in char or not char["visual_description"]:
                char["visual_description"] = f"A character named {char['name']}"

        # Fill panel fields
        for i, panel in enumerate(result["panels"]):
            if "panel_number" not in panel:
                panel["panel_number"] = i + 1
            if "visual_description" not in panel or not panel["visual_description"]:
                panel["visual_description"] = "A scene in the story"
            if "dialogue" not in panel:
                panel["dialogue"] = []
            if "shot_type" not in panel:
                panel["shot_type"] = "Medium Shot"
            if "environment" not in panel:
                panel["environment"] = "Story location"

            # Ensure dialogue is a list
            if not isinstance(panel["dialogue"], list):
                panel["dialogue"] = []

            # Validate dialogue entries
            valid_dialogue = []
            for d in panel["dialogue"]:
                if isinstance(d, dict) and "character" in d and "text" in d:
                    valid_dialogue.append(d)
            panel["dialogue"] = valid_dialogue

        # Ensure at least one panel exists
        if not result["panels"]:
            logger.warning("No panels generated, creating fallback")
            result["panels"] = [{
                "panel_number": 1,
                "visual_description": "An establishing shot of the story setting",
                "dialogue": [],
                "shot_type": "Wide Shot",
                "environment": "Story location"
            }]

        return result

    def to_state_format(
        self,
        result: Dict[str, Any]
    ) -> tuple[List[PanelData], List[CharacterData]]:
        """
        Convert result to state format (TypedDict compatible).

        Args:
            result: Validated result dict

        Returns:
            Tuple of (panels, characters) in state format
        """
        panels: List[PanelData] = []
        for p in result["panels"]:
            panels.append({
                "panel_number": p["panel_number"],
                "visual_description": p["visual_description"],
                "dialogue": p["dialogue"],
                "shot_type": p["shot_type"],
                "environment": p.get("environment", "")
            })

        characters: List[CharacterData] = []
        for c in result["characters"]:
            characters.append({
                "name": c["name"],
                "visual_description": c["visual_description"]
            })

        return panels, characters


# Global instance
webtoon_scripter = WebtoonScripter()
