"""
Story Architect service for fidelity validation workflow.

Node 1: Generates the "Ground Truth" story from a seed input.
This story becomes the reference against which the blind reader's
reconstruction is compared.
"""

from typing import Dict, List, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.services.llm_config import llm_config
from app.models.fidelity_state import StoryArchitectOutput
from app.prompt.fidelity import STORY_ARCHITECT_PROMPT


# ============================================================================
# Output Schema for Parsing
# ============================================================================

class CharacterMotivationSchema(BaseModel):
    """Schema for character motivation in LLM output."""
    goal: str = Field(description="What the character wants to achieve")
    motivation: str = Field(description="Why they want it")
    obstacle: str = Field(description="What stands in their way")


class StoryArchitectSchema(BaseModel):
    """Schema for Story Architect LLM output."""
    story: str = Field(description="The full narrative text")
    summary: str = Field(description="3-5 sentence summary")
    character_motivations: Dict[str, CharacterMotivationSchema] = Field(
        description="Character motivations keyed by name"
    )
    key_conflicts: List[str] = Field(description="Main conflicts")
    plot_points: List[str] = Field(description="Key plot beats")


# ============================================================================
# Service Class
# ============================================================================

class StoryArchitect:
    """
    Story Architect service (Node 1).

    Generates the ground truth story from a seed input. The story includes
    explicit character motivations, conflicts, and plot points that will
    be used as the reference for fidelity validation.
    """

    def __init__(self):
        """Initialize with LLM configuration."""
        self.llm = llm_config.get_model()
        self.prompt = ChatPromptTemplate.from_template(STORY_ARCHITECT_PROMPT)
        self.parser = JsonOutputParser(pydantic_object=StoryArchitectSchema)

    async def generate_story(self, seed: str) -> Dict[str, Any]:
        """
        Generate a complete story with structured metadata from a seed.

        Args:
            seed: The initial concept or idea for the story

        Returns:
            Dictionary containing:
                - story: Full narrative text
                - summary: Brief summary
                - character_motivations: Dict of character goals/motivations
                - key_conflicts: List of conflicts
                - plot_points: List of plot beats

        Raises:
            Exception: If story generation fails
        """
        try:
            chain = self.prompt | self.llm | self.parser

            result = await chain.ainvoke({"seed": seed})

            # Validate and fill any missing fields
            result = self._validate_and_fill(result, seed)

            return result

        except Exception as e:
            raise Exception(f"Story generation failed: {str(e)}")

    def _validate_and_fill(self, result: Dict[str, Any], seed: str) -> Dict[str, Any]:
        """
        Validate LLM output and fill any missing fields with defaults.

        Args:
            result: Raw LLM output
            seed: Original seed for fallback

        Returns:
            Validated and complete result dict
        """
        # Ensure story exists
        if not result.get("story"):
            raise ValueError("LLM did not generate a story")

        # Ensure summary exists
        if not result.get("summary"):
            # Generate a simple summary from first few sentences
            story = result["story"]
            sentences = story.split(".")[:3]
            result["summary"] = ".".join(sentences) + "."

        # Ensure character_motivations exists
        if not result.get("character_motivations"):
            result["character_motivations"] = {
                "Protagonist": {
                    "goal": "Achieve their objective",
                    "motivation": "Personal drive",
                    "obstacle": "External forces"
                }
            }

        # Validate character_motivations structure
        for char_name, motivation in result["character_motivations"].items():
            if not isinstance(motivation, dict):
                result["character_motivations"][char_name] = {
                    "goal": str(motivation),
                    "motivation": "Unknown",
                    "obstacle": "Unknown"
                }
            else:
                # Ensure all required fields exist
                motivation.setdefault("goal", "Unknown goal")
                motivation.setdefault("motivation", "Unknown motivation")
                motivation.setdefault("obstacle", "Unknown obstacle")

        # Ensure key_conflicts exists
        if not result.get("key_conflicts"):
            result["key_conflicts"] = ["Primary conflict in the story"]

        # Ensure plot_points exists
        if not result.get("plot_points"):
            result["plot_points"] = [
                "Introduction",
                "Rising action",
                "Climax",
                "Resolution"
            ]

        return result

    def to_output_model(self, result: Dict[str, Any]) -> StoryArchitectOutput:
        """
        Convert raw result to Pydantic model.

        Args:
            result: Validated result dict

        Returns:
            StoryArchitectOutput model
        """
        return StoryArchitectOutput(
            story=result["story"],
            summary=result["summary"],
            character_motivations=result["character_motivations"],
            key_conflicts=result["key_conflicts"],
            plot_points=result["plot_points"]
        )


# Global instance
story_architect = StoryArchitect()
