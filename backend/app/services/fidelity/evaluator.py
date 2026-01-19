"""
Fidelity Evaluator service for fidelity validation workflow.

Node 4: Compares the original story to the blind reader's reconstruction.
Identifies information gaps and generates actionable feedback for the scripter.
"""

import logging
from typing import Dict, List, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.services.llm_config import llm_config
from app.models.fidelity_state import FidelityGap, FidelityEvaluation, FidelityGapModel
from app.prompt.fidelity import FIDELITY_EVALUATOR_PROMPT


logger = logging.getLogger(__name__)


# ============================================================================
# Output Schema
# ============================================================================

class GapSchema(BaseModel):
    """Schema for an information gap."""
    category: str = Field(description="Gap category")
    original_element: str = Field(description="What was in the original")
    reader_interpretation: str = Field(description="What reader understood")
    severity: str = Field(description="critical, major, or minor")
    suggested_fix: str = Field(description="How to fix this gap")


class EvaluatorOutputSchema(BaseModel):
    """Schema for evaluator output."""
    fidelity_score: float = Field(ge=0, le=100, description="Fidelity score")
    is_valid: bool = Field(description="Whether score meets threshold")
    gaps: List[GapSchema] = Field(default_factory=list, description="Information gaps")
    critique: str = Field(description="Feedback for scripter")


# ============================================================================
# Service Class
# ============================================================================

class FidelityEvaluator:
    """
    Fidelity Evaluator service (Node 4).

    Compares the original story to the blind reader's reconstruction,
    identifies information gaps, and generates actionable feedback.
    """

    def __init__(self, validation_threshold: float = 80.0):
        """
        Initialize with LLM configuration.

        Args:
            validation_threshold: Score needed to pass validation (default 80.0)
        """
        self.llm = llm_config.get_model()
        self.prompt = ChatPromptTemplate.from_template(FIDELITY_EVALUATOR_PROMPT)
        self.parser = JsonOutputParser(pydantic_object=EvaluatorOutputSchema)
        self.validation_threshold = validation_threshold

    async def evaluate(
        self,
        original_story: str,
        story_summary: str,
        character_motivations: Dict[str, Dict[str, str]],
        key_conflicts: List[str],
        plot_points: List[str],
        reconstructed_story: str,
        inferred_motivations: Dict[str, Dict[str, Any]],
        inferred_conflicts: List[str],
        unclear_elements: List[str],
        reader_confidence: float
    ) -> Dict[str, Any]:
        """
        Evaluate fidelity by comparing original to reconstruction.

        Args:
            original_story: The ground truth story text
            story_summary: Summary of key events
            character_motivations: Original character motivations
            key_conflicts: Original conflicts
            plot_points: Key plot beats
            reconstructed_story: Reader's interpretation
            inferred_motivations: What reader thinks characters want
            inferred_conflicts: Conflicts reader identified
            unclear_elements: Things reader found confusing
            reader_confidence: Reader's confidence score (0-100)

        Returns:
            Dictionary containing:
                - fidelity_score: 0-100 score
                - is_valid: Whether score meets threshold
                - gaps: List of information gaps
                - critique: Actionable feedback

        Raises:
            Exception: If evaluation fails
        """
        try:
            # Format inputs for prompt
            motivations_text = self._format_motivations(character_motivations)
            conflicts_text = "\n".join(f"- {c}" for c in key_conflicts)
            plot_text = "\n".join(f"{i+1}. {p}" for i, p in enumerate(plot_points))
            inferred_motivations_text = self._format_inferred_motivations(inferred_motivations)
            inferred_conflicts_text = "\n".join(f"- {c}" for c in inferred_conflicts) or "None identified"
            unclear_text = "\n".join(f"- {e}" for e in unclear_elements) or "None reported"

            chain = self.prompt | self.llm | self.parser

            result = await chain.ainvoke({
                "original_story": original_story,
                "story_summary": story_summary,
                "character_motivations": motivations_text,
                "key_conflicts": conflicts_text,
                "plot_points": plot_text,
                "reconstructed_story": reconstructed_story,
                "inferred_motivations": inferred_motivations_text,
                "inferred_conflicts": inferred_conflicts_text,
                "unclear_elements": unclear_text,
                "reader_confidence": reader_confidence
            })

            # Validate and fill missing fields
            result = self._validate_and_fill(result)

            # Apply threshold
            result["is_valid"] = result["fidelity_score"] >= self.validation_threshold

            return result

        except Exception as e:
            logger.error(f"Fidelity evaluation failed: {str(e)}")
            raise Exception(f"Fidelity evaluation failed: {str(e)}")

    def _format_motivations(self, motivations: Dict[str, Dict[str, str]]) -> str:
        """Format original character motivations."""
        lines = []
        for name, data in motivations.items():
            goal = data.get("goal", "Unknown")
            motivation = data.get("motivation", "Unknown")
            obstacle = data.get("obstacle", "Unknown")
            lines.append(f"- {name}:")
            lines.append(f"  Goal: {goal}")
            lines.append(f"  Why: {motivation}")
            lines.append(f"  Obstacle: {obstacle}")
        return "\n".join(lines) if lines else "No character motivations defined."

    def _format_inferred_motivations(self, motivations: Dict[str, Dict[str, Any]]) -> str:
        """Format reader's inferred motivations."""
        lines = []
        for name, data in motivations.items():
            goal = data.get("apparent_goal", "Unknown")
            confidence = data.get("confidence", 0)
            lines.append(f"- {name}: {goal} (confidence: {confidence}%)")
        return "\n".join(lines) if lines else "No motivations inferred."

    def _validate_and_fill(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and fill missing fields in the result.

        Args:
            result: Raw LLM output

        Returns:
            Validated result with all required fields
        """
        # Ensure fidelity_score exists and is valid
        if "fidelity_score" not in result:
            result["fidelity_score"] = 50.0
        else:
            try:
                result["fidelity_score"] = float(result["fidelity_score"])
                result["fidelity_score"] = max(0, min(100, result["fidelity_score"]))
            except (ValueError, TypeError):
                result["fidelity_score"] = 50.0

        # Ensure is_valid exists
        if "is_valid" not in result:
            result["is_valid"] = result["fidelity_score"] >= self.validation_threshold

        # Ensure gaps exists and is valid
        if "gaps" not in result:
            result["gaps"] = []

        # Validate gap structure
        valid_gaps = []
        valid_categories = {"plot", "motivation", "emotion", "relationship", "conflict"}
        valid_severities = {"critical", "major", "minor"}

        for gap in result.get("gaps", []):
            if not isinstance(gap, dict):
                continue

            # Ensure required fields
            gap.setdefault("category", "plot")
            gap.setdefault("original_element", "Unknown element")
            gap.setdefault("reader_interpretation", "NOT DETECTED")
            gap.setdefault("severity", "major")
            gap.setdefault("suggested_fix", "Clarify this element in the panels")

            # Validate category
            if gap["category"] not in valid_categories:
                gap["category"] = "plot"

            # Validate severity
            if gap["severity"] not in valid_severities:
                gap["severity"] = "major"

            valid_gaps.append(gap)

        result["gaps"] = valid_gaps

        # Ensure critique exists
        if not result.get("critique"):
            if valid_gaps:
                result["critique"] = self._generate_critique_from_gaps(valid_gaps)
            else:
                result["critique"] = "The panels effectively convey the story. No significant gaps identified."

        return result

    def _generate_critique_from_gaps(self, gaps: List[Dict]) -> str:
        """
        Generate critique text from gaps if LLM didn't provide one.

        Args:
            gaps: List of information gaps

        Returns:
            Formatted critique text
        """
        lines = ["REVISION NEEDED - The following gaps were identified:\n"]

        # Group by severity
        critical = [g for g in gaps if g["severity"] == "critical"]
        major = [g for g in gaps if g["severity"] == "major"]
        minor = [g for g in gaps if g["severity"] == "minor"]

        if critical:
            lines.append("CRITICAL ISSUES (must fix):")
            for g in critical:
                lines.append(f"  - [{g['category']}] {g['original_element']}")
                lines.append(f"    Fix: {g['suggested_fix']}")

        if major:
            lines.append("\nMAJOR ISSUES (should fix):")
            for g in major:
                lines.append(f"  - [{g['category']}] {g['original_element']}")
                lines.append(f"    Fix: {g['suggested_fix']}")

        if minor:
            lines.append("\nMINOR ISSUES (nice to fix):")
            for g in minor:
                lines.append(f"  - [{g['category']}] {g['original_element']}")

        return "\n".join(lines)

    def to_evaluation_model(
        self,
        result: Dict[str, Any],
        iteration: int,
        previous_score: float = None
    ) -> FidelityEvaluation:
        """
        Convert result to FidelityEvaluation model.

        Args:
            result: Validated result dict
            iteration: Current iteration number
            previous_score: Score from previous iteration (for convergence check)

        Returns:
            FidelityEvaluation model
        """
        # Check convergence
        converged = False
        if previous_score is not None:
            converged = result["fidelity_score"] > previous_score

        # Convert gaps to models
        gap_models = []
        for gap in result["gaps"]:
            gap_models.append(FidelityGapModel(
                category=gap["category"],
                original_element=gap["original_element"],
                reader_interpretation=gap["reader_interpretation"],
                severity=gap["severity"],
                suggested_fix=gap["suggested_fix"]
            ))

        return FidelityEvaluation(
            fidelity_score=result["fidelity_score"],
            is_valid=result["is_valid"],
            gaps=gap_models,
            critique=result["critique"],
            iteration=iteration,
            converged=converged
        )


# Global instance
fidelity_evaluator = FidelityEvaluator()
