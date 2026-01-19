"""
Blind Reader service for fidelity validation workflow.

Node 3: Reconstructs the story from panels ONLY.

CRITICAL SECURITY NOTE:
This service must NEVER receive or access the original_story.
State isolation is enforced at both the service level and the graph level.
The filter_state_for_blind_reader() function ensures only safe data is passed.
"""

import json
import logging
from typing import Dict, List, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.services.llm_config import llm_config
from app.models.fidelity_state import (
    BlindReaderInput,
    BlindReaderOutput,
    PanelData,
    CharacterData,
    WebtoonFidelityState
)
from app.prompt.fidelity import BLIND_READER_PROMPT


logger = logging.getLogger(__name__)


# ============================================================================
# Output Schema
# ============================================================================

class InferredMotivationSchema(BaseModel):
    """Schema for inferred character motivation."""
    apparent_goal: str = Field(description="What the character appears to want")
    confidence: float = Field(ge=0, le=100, description="Confidence in this inference")


class BlindReaderSchema(BaseModel):
    """Schema for Blind Reader output."""
    reconstructed_story: str = Field(description="Reader's interpretation of the story")
    inferred_motivations: Dict[str, InferredMotivationSchema] = Field(
        default_factory=dict,
        description="Inferred character motivations"
    )
    inferred_conflicts: List[str] = Field(
        default_factory=list,
        description="Conflicts identified from panels"
    )
    unclear_elements: List[str] = Field(
        default_factory=list,
        description="Elements that were confusing"
    )
    overall_confidence: float = Field(
        ge=0, le=100,
        description="Overall confidence in interpretation"
    )


# ============================================================================
# State Filtering (CRITICAL SECURITY)
# ============================================================================

def filter_state_for_blind_reader(state: WebtoonFidelityState) -> BlindReaderInput:
    """
    Filter state to extract ONLY what BlindReader should see.

    CRITICAL: This function ensures the BlindReader cannot access:
    - original_story
    - story_summary
    - character_motivations
    - key_conflicts
    - plot_points

    Args:
        state: Full workflow state

    Returns:
        Filtered state containing only panels and characters

    Raises:
        ValueError: If required fields are missing
    """
    # Validate required fields exist
    if "script_panels" not in state:
        raise ValueError("State missing 'script_panels' field")
    if "characters" not in state:
        raise ValueError("State missing 'characters' field")

    # Return ONLY safe fields
    return {
        "script_panels": state["script_panels"],
        "characters": state["characters"]
    }


def validate_no_leak(filtered_input: BlindReaderInput) -> bool:
    """
    Validate that filtered input contains no ground truth data.

    This is a secondary check to ensure state isolation.

    Args:
        filtered_input: The filtered input to validate

    Returns:
        True if input is safe, raises exception otherwise

    Raises:
        ValueError: If ground truth data is detected
    """
    # Check keys - should ONLY have these two
    allowed_keys = {"script_panels", "characters"}
    actual_keys = set(filtered_input.keys())

    forbidden_keys = actual_keys - allowed_keys
    if forbidden_keys:
        raise ValueError(
            f"SECURITY VIOLATION: BlindReader input contains forbidden keys: {forbidden_keys}"
        )

    # Convert to string and check for suspicious patterns
    input_str = json.dumps(filtered_input)

    # These patterns should NOT appear in blind reader input
    # (they indicate ground truth data leaking)
    suspicious_patterns = [
        '"original_story"',
        '"story_summary"',
        '"character_motivations"',
        '"key_conflicts"',
        '"plot_points"'
    ]

    for pattern in suspicious_patterns:
        if pattern in input_str:
            raise ValueError(
                f"SECURITY VIOLATION: BlindReader input contains suspicious pattern: {pattern}"
            )

    return True


# ============================================================================
# Service Class
# ============================================================================

class BlindReader:
    """
    Blind Reader service (Node 3).

    Reconstructs the story from panels only, without access to the original story.
    This service is critical for fidelity validation - it simulates a real reader
    who only sees the visual panels.

    SECURITY: This service must NEVER receive original_story data.
    Use filter_state_for_blind_reader() before calling this service.
    """

    def __init__(self):
        """Initialize with LLM configuration."""
        self.llm = llm_config.get_model()
        self.prompt = ChatPromptTemplate.from_template(BLIND_READER_PROMPT)
        self.parser = JsonOutputParser(pydantic_object=BlindReaderSchema)

    async def reconstruct_story(
        self,
        panels: List[PanelData],
        characters: List[CharacterData]
    ) -> Dict[str, Any]:
        """
        Reconstruct the story from panels only.

        IMPORTANT: This method accepts ONLY panels and characters.
        It does NOT accept any original story data.

        Args:
            panels: List of panel data (visual descriptions and dialogue)
            characters: List of character definitions

        Returns:
            Dictionary containing:
                - reconstructed_story: Reader's interpretation
                - inferred_motivations: What reader thinks characters want
                - inferred_conflicts: Conflicts identified
                - unclear_elements: Things that were confusing
                - overall_confidence: Confidence score (0-100)

        Raises:
            Exception: If reconstruction fails
        """
        try:
            # Format panels for prompt
            panels_json = json.dumps(panels, indent=2)
            characters_json = json.dumps(characters, indent=2)

            chain = self.prompt | self.llm | self.parser

            result = await chain.ainvoke({
                "panels_json": panels_json,
                "characters_json": characters_json
            })

            # Validate and fill missing fields
            result = self._validate_and_fill(result, characters)

            return result

        except Exception as e:
            logger.error(f"Story reconstruction failed: {str(e)}")
            raise Exception(f"Story reconstruction failed: {str(e)}")

    async def reconstruct_from_filtered_state(
        self,
        filtered_state: BlindReaderInput
    ) -> Dict[str, Any]:
        """
        Reconstruct story from pre-filtered state.

        This is the preferred method when called from the workflow,
        as it accepts the already-filtered state.

        Args:
            filtered_state: State filtered by filter_state_for_blind_reader()

        Returns:
            Reconstruction result

        Raises:
            ValueError: If state validation fails
            Exception: If reconstruction fails
        """
        # Validate the filtered state has no leaks
        validate_no_leak(filtered_state)

        return await self.reconstruct_story(
            panels=filtered_state["script_panels"],
            characters=filtered_state["characters"]
        )

    def _validate_and_fill(
        self,
        result: Dict[str, Any],
        characters: List[CharacterData]
    ) -> Dict[str, Any]:
        """
        Validate and fill missing fields in the result.

        Args:
            result: Raw LLM output
            characters: Character list for reference

        Returns:
            Validated result with all required fields
        """
        # Ensure reconstructed_story exists
        if not result.get("reconstructed_story"):
            result["reconstructed_story"] = "Unable to reconstruct story from panels."

        # Ensure inferred_motivations exists
        if not result.get("inferred_motivations"):
            result["inferred_motivations"] = {}

        # Validate motivation structure
        for char_name, motivation in result.get("inferred_motivations", {}).items():
            if not isinstance(motivation, dict):
                result["inferred_motivations"][char_name] = {
                    "apparent_goal": str(motivation),
                    "confidence": 50
                }
            else:
                motivation.setdefault("apparent_goal", "Unknown")
                motivation.setdefault("confidence", 50)
                # Ensure confidence is a number
                try:
                    motivation["confidence"] = float(motivation["confidence"])
                except (ValueError, TypeError):
                    motivation["confidence"] = 50

        # Ensure inferred_conflicts exists
        if not result.get("inferred_conflicts"):
            result["inferred_conflicts"] = []

        # Ensure unclear_elements exists
        if not result.get("unclear_elements"):
            result["unclear_elements"] = []

        # Ensure overall_confidence exists and is valid
        if "overall_confidence" not in result:
            result["overall_confidence"] = 50
        else:
            try:
                result["overall_confidence"] = float(result["overall_confidence"])
                # Clamp to valid range
                result["overall_confidence"] = max(0, min(100, result["overall_confidence"]))
            except (ValueError, TypeError):
                result["overall_confidence"] = 50

        return result

    def to_output_model(self, result: Dict[str, Any]) -> BlindReaderOutput:
        """
        Convert result to Pydantic model.

        Args:
            result: Validated result dict

        Returns:
            BlindReaderOutput model
        """
        return BlindReaderOutput(
            reconstructed_story=result["reconstructed_story"],
            inferred_motivations=result["inferred_motivations"],
            inferred_conflicts=result["inferred_conflicts"],
            unclear_elements=result["unclear_elements"],
            overall_confidence=result["overall_confidence"]
        )


# Global instance
blind_reader = BlindReader()
