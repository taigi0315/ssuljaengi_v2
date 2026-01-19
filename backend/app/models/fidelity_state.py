"""
Data models for the Webtoon Fidelity Validator workflow.

This module defines TypedDict for LangGraph state management and Pydantic models
for structured responses in the fidelity validation workflow.
"""

from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# TypedDict State Schemas (for LangGraph)
# ============================================================================

class PanelData(TypedDict):
    """
    Simplified panel representation for blind reader analysis.
    Contains only what a reader would "see" in a webtoon panel.
    """
    panel_number: int
    visual_description: str
    dialogue: List[dict]  # [{"character": str, "text": str}]
    shot_type: str
    environment: str


class CharacterData(TypedDict):
    """
    Character data visible to the blind reader.
    """
    name: str
    visual_description: str


class CharacterMotivation(TypedDict):
    """
    Structured character motivation from story architect.
    """
    goal: str
    motivation: str
    obstacle: str


class InferredMotivation(TypedDict):
    """
    What the blind reader infers about a character's motivation.
    """
    apparent_goal: str
    confidence: float  # 0-100


class FidelityGap(TypedDict):
    """
    An information gap identified by the evaluator.

    Represents something in the original story that the blind reader
    failed to understand or misinterpreted from the panels.
    """
    category: str  # 'plot', 'motivation', 'emotion', 'relationship', 'conflict'
    original_element: str
    reader_interpretation: str
    severity: str  # 'critical', 'major', 'minor'
    suggested_fix: str


class WebtoonFidelityState(TypedDict):
    """
    Central state schema for the fidelity validation workflow.

    This TypedDict is passed between all nodes in the LangGraph workflow.
    Note: BlindReader node receives a FILTERED version that excludes
    original_story and related ground truth fields.
    """
    # ---- Input ----
    seed: str

    # ---- Node 1 Output: Story Architect (Ground Truth) ----
    # These fields are generated ONCE and never modified
    original_story: str
    story_summary: str
    character_motivations: dict  # {character_name: CharacterMotivation}
    key_conflicts: List[str]
    plot_points: List[str]

    # ---- Node 2 Output: Webtoon Scripter ----
    # These fields are modified on each iteration
    script_panels: List[PanelData]
    characters: List[CharacterData]

    # ---- Node 3 Output: Blind Reader ----
    reconstructed_story: str
    inferred_motivations: dict  # {character_name: InferredMotivation}
    inferred_conflicts: List[str]
    unclear_elements: List[str]
    reader_confidence: float  # 0.0 - 1.0

    # ---- Node 4 Output: Evaluator ----
    fidelity_score: float  # 0.0 - 100.0
    information_gaps: List[FidelityGap]
    critique: Optional[str]

    # ---- Control Flow ----
    iteration: int
    max_iterations: int
    is_validated: bool
    current_step: str
    error: Optional[str]


class BlindReaderInput(TypedDict):
    """
    Filtered state for BlindReader node.

    CRITICAL: This is the ONLY data BlindReader should receive.
    It explicitly excludes original_story and all ground truth fields.
    """
    script_panels: List[PanelData]
    characters: List[CharacterData]


# ============================================================================
# Pydantic Models (for API responses and validation)
# ============================================================================

class FidelityGapModel(BaseModel):
    """
    Pydantic model for information gaps.
    """
    category: str = Field(
        ...,
        description="Gap category: plot, motivation, emotion, relationship, or conflict"
    )
    original_element: str = Field(
        ...,
        description="What was in the original story"
    )
    reader_interpretation: str = Field(
        ...,
        description="What the reader understood (or missed)"
    )
    severity: str = Field(
        ...,
        description="Gap severity: critical, major, or minor"
    )
    suggested_fix: str = Field(
        ...,
        description="How to fix this gap in the panels"
    )


class FidelityEvaluation(BaseModel):
    """
    Result of fidelity evaluation comparing original to reconstruction.
    """
    fidelity_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Fidelity score from 0-100"
    )
    is_valid: bool = Field(
        ...,
        description="Whether the score meets the validation threshold"
    )
    gaps: List[FidelityGapModel] = Field(
        default_factory=list,
        description="List of identified information gaps"
    )
    critique: str = Field(
        default="",
        description="Actionable feedback for the scripter"
    )
    iteration: int = Field(
        ...,
        ge=1,
        description="Which iteration this evaluation is from"
    )
    converged: bool = Field(
        default=False,
        description="Whether score improved from previous iteration"
    )


class ValidationHistoryEntry(BaseModel):
    """
    Record of a single validation iteration.
    """
    iteration: int = Field(..., description="Iteration number")
    fidelity_score: float = Field(..., description="Score for this iteration")
    gap_count: int = Field(..., description="Number of gaps identified")
    information_gaps: List[FidelityGapModel] = Field(
        default_factory=list,
        description="Gaps found in this iteration"
    )
    critique: str = Field(default="", description="Feedback given")
    reader_confidence: float = Field(..., description="Blind reader's confidence")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When this iteration completed"
    )


class StoryArchitectOutput(BaseModel):
    """
    Output from the Story Architect node.
    """
    story: str = Field(..., description="The full narrative text")
    summary: str = Field(..., description="3-5 sentence summary")
    character_motivations: dict = Field(
        ...,
        description="Character name to motivation mapping"
    )
    key_conflicts: List[str] = Field(..., description="Main conflicts in the story")
    plot_points: List[str] = Field(..., description="Key plot beats")


class BlindReaderOutput(BaseModel):
    """
    Output from the Blind Reader node.
    """
    reconstructed_story: str = Field(
        ...,
        description="Reader's interpretation of the story"
    )
    inferred_motivations: dict = Field(
        ...,
        description="What reader thinks each character wants"
    )
    inferred_conflicts: List[str] = Field(
        default_factory=list,
        description="Conflicts the reader identified"
    )
    unclear_elements: List[str] = Field(
        default_factory=list,
        description="Things that were confusing or unclear"
    )
    overall_confidence: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Reader's confidence in their interpretation (0-100)"
    )


class FidelityValidationRequest(BaseModel):
    """
    API request model for starting a fidelity validation workflow.
    """
    seed: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Seed text to generate story from"
    )
    max_iterations: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum validation iterations"
    )
    fidelity_threshold: float = Field(
        default=80.0,
        ge=0.0,
        le=100.0,
        description="Score threshold for validation to pass"
    )


class FidelityValidationResponse(BaseModel):
    """
    API response model for fidelity validation workflow result.
    """
    workflow_id: str = Field(..., description="Unique workflow identifier")
    status: str = Field(
        ...,
        description="Final status: validated, max_iterations_reached, or error"
    )
    final_score: Optional[float] = Field(
        default=None,
        description="Final fidelity score achieved"
    )
    iterations_used: int = Field(..., description="Number of iterations executed")
    original_story: str = Field(..., description="The generated ground truth story")
    script_panels: Optional[List[dict]] = Field(
        default=None,
        description="Final validated panels ready for image generation"
    )
    characters: Optional[List[dict]] = Field(
        default=None,
        description="Character definitions"
    )
    validation_history: List[ValidationHistoryEntry] = Field(
        default_factory=list,
        description="History of all validation iterations"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if workflow failed"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When the workflow completed"
    )


class FidelityWorkflowStatus(BaseModel):
    """
    Model for tracking fidelity workflow execution status.
    """
    workflow_id: str = Field(..., description="Unique workflow ID")
    status: str = Field(..., description="Current status")
    current_step: str = Field(..., description="Current node being executed")
    iteration: int = Field(..., description="Current iteration number")
    progress: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Progress percentage"
    )
    latest_score: Optional[float] = Field(
        default=None,
        description="Most recent fidelity score"
    )
    error: Optional[str] = Field(default=None, description="Error if failed")
