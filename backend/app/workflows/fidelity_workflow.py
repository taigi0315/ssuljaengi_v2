"""
LangGraph workflow for webtoon fidelity validation.

This workflow validates that a story is faithfully translated to webtoon panels
using a "Blind Reader" approach:

1. Story Architect: Generate ground truth story from seed
2. Webtoon Scripter: Convert story to panels
3. Blind Reader: Reconstruct story from panels ONLY (no access to original)
4. Evaluator: Compare original to reconstruction, identify gaps
5. Loop: If gaps found, revise panels and re-validate (max 3 iterations)

CRITICAL: The Blind Reader must NEVER access the original story. This is
enforced through state filtering in the blind_reader_node function.
"""

import logging
import uuid
from typing import Literal, Optional, List
from datetime import datetime

from langgraph.graph import StateGraph, END

from app.models.fidelity_state import (
    WebtoonFidelityState,
    BlindReaderInput,
    ValidationHistoryEntry,
    FidelityValidationResponse,
    FidelityGapModel
)
from app.services.fidelity.story_architect import story_architect
from app.services.fidelity.webtoon_scripter import webtoon_scripter
from app.services.fidelity.blind_reader import (
    blind_reader,
    filter_state_for_blind_reader,
    validate_no_leak
)
from app.services.fidelity.evaluator import fidelity_evaluator
from app.config import get_settings


logger = logging.getLogger(__name__)


# ============================================================================
# Node Functions
# ============================================================================

async def story_architect_node(state: WebtoonFidelityState) -> dict:
    """
    Node 1: Story Architect - Generate ground truth story.

    This node runs ONCE at the start of the workflow.
    It creates the "original story" that all subsequent validation
    is measured against.

    Args:
        state: Current workflow state

    Returns:
        Updated state with original story and metadata
    """
    try:
        seed = state["seed"]
        logger.info(f"Story Architect: Generating story from seed ({len(seed)} chars)")

        result = await story_architect.generate_story(seed)

        logger.info(
            f"Story Architect complete: {len(result['story'])} chars, "
            f"{len(result.get('character_motivations', {}))} characters"
        )

        return {
            "original_story": result["story"],
            "story_summary": result["summary"],
            "character_motivations": result["character_motivations"],
            "key_conflicts": result["key_conflicts"],
            "plot_points": result.get("plot_points", []),
            "current_step": "story_architect_complete",
        }

    except Exception as e:
        logger.error(f"Story Architect failed: {str(e)}", exc_info=True)
        return {
            "error": f"Story Architect failed: {str(e)}",
            "current_step": "failed"
        }


async def webtoon_scripter_node(state: WebtoonFidelityState) -> dict:
    """
    Node 2: Webtoon Scripter - Convert story to panels.

    On first run: Creates panels from original story.
    On subsequent runs: Revises panels based on evaluator critique.

    Args:
        state: Current workflow state

    Returns:
        Updated state with panels and characters
    """
    try:
        iteration = state.get("iteration", 1)
        critique = state.get("critique")

        if critique and iteration > 1:
            # Revision mode
            logger.info(f"Webtoon Scripter: Revising panels (iteration {iteration})")

            result = await webtoon_scripter.revise_panels(
                current_panels=state.get("script_panels", []),
                current_characters=state.get("characters", []),
                critique=critique,
                information_gaps=state.get("information_gaps", []),
                character_motivations=state.get("character_motivations", {})
            )
        else:
            # Initial conversion
            logger.info("Webtoon Scripter: Converting story to panels")

            result = await webtoon_scripter.convert_to_panels(
                story=state["original_story"],
                character_motivations=state.get("character_motivations", {}),
                key_conflicts=state.get("key_conflicts", [])
            )

        panels, characters = webtoon_scripter.to_state_format(result)

        logger.info(
            f"Webtoon Scripter complete: {len(panels)} panels, "
            f"{len(characters)} characters"
        )

        return {
            "script_panels": panels,
            "characters": characters,
            "current_step": "webtoon_scripter_complete",
        }

    except Exception as e:
        logger.error(f"Webtoon Scripter failed: {str(e)}", exc_info=True)
        return {
            "error": f"Webtoon Scripter failed: {str(e)}",
            "current_step": "failed"
        }


async def blind_reader_node(state: WebtoonFidelityState) -> dict:
    """
    Node 3: Blind Reader - Reconstruct story from panels only.

    CRITICAL SECURITY: This node filters the state to ensure the
    Blind Reader cannot access the original story.

    Args:
        state: Current workflow state (will be filtered)

    Returns:
        Updated state with reconstructed story and inferences
    """
    try:
        logger.info("Blind Reader: Filtering state for isolation")

        # SECURITY: Filter state to remove ground truth data
        filtered_state: BlindReaderInput = filter_state_for_blind_reader(state)

        # SECURITY: Validate no ground truth data leaked
        validate_no_leak(filtered_state)

        logger.info(
            f"Blind Reader: Reconstructing from {len(filtered_state['script_panels'])} panels"
        )

        # Run blind reader with filtered input
        result = await blind_reader.reconstruct_from_filtered_state(filtered_state)

        logger.info(
            f"Blind Reader complete: confidence={result['overall_confidence']}%, "
            f"unclear elements={len(result.get('unclear_elements', []))}"
        )

        return {
            "reconstructed_story": result["reconstructed_story"],
            "inferred_motivations": result["inferred_motivations"],
            "inferred_conflicts": result["inferred_conflicts"],
            "unclear_elements": result.get("unclear_elements", []),
            "reader_confidence": result["overall_confidence"] / 100.0,
            "current_step": "blind_reader_complete",
        }

    except Exception as e:
        logger.error(f"Blind Reader failed: {str(e)}", exc_info=True)
        return {
            "error": f"Blind Reader failed: {str(e)}",
            "current_step": "failed"
        }


async def evaluator_node(state: WebtoonFidelityState) -> dict:
    """
    Node 4: Evaluator - Compare original to reconstruction.

    Identifies information gaps and decides if validation passes.

    Args:
        state: Current workflow state

    Returns:
        Updated state with evaluation results
    """
    try:
        iteration = state.get("iteration", 1)
        previous_score = state.get("fidelity_score", 0.0) if iteration > 1 else None

        logger.info(f"Evaluator: Comparing stories (iteration {iteration})")

        result = await fidelity_evaluator.evaluate(
            original_story=state["original_story"],
            story_summary=state.get("story_summary", ""),
            character_motivations=state.get("character_motivations", {}),
            key_conflicts=state.get("key_conflicts", []),
            plot_points=state.get("plot_points", []),
            reconstructed_story=state["reconstructed_story"],
            inferred_motivations=state.get("inferred_motivations", {}),
            inferred_conflicts=state.get("inferred_conflicts", []),
            unclear_elements=state.get("unclear_elements", []),
            reader_confidence=state.get("reader_confidence", 0.5) * 100
        )

        # Check for convergence
        converged = False
        if previous_score is not None and result["fidelity_score"] > previous_score:
            converged = True

        logger.info(
            f"Evaluator complete: score={result['fidelity_score']:.1f}%, "
            f"valid={result['is_valid']}, gaps={len(result['gaps'])}, "
            f"converged={converged}"
        )

        return {
            "fidelity_score": result["fidelity_score"],
            "information_gaps": result["gaps"],
            "critique": result["critique"],
            "is_validated": result["is_valid"],
            "iteration": iteration + 1,  # Increment for next loop
            "current_step": "evaluator_complete",
        }

    except Exception as e:
        logger.error(f"Evaluator failed: {str(e)}", exc_info=True)
        return {
            "error": f"Evaluator failed: {str(e)}",
            "current_step": "failed"
        }


# ============================================================================
# Routing Logic
# ============================================================================

def should_continue(state: WebtoonFidelityState) -> Literal["webtoon_scripter", "end"]:
    """
    Routing function: Decide if we should continue the validation loop.

    Returns "end" if:
    - Validation passed (is_validated = True)
    - Max iterations reached
    - An error occurred

    Returns "webtoon_scripter" if:
    - Validation failed and we have iterations remaining

    Args:
        state: Current workflow state

    Returns:
        "webtoon_scripter" to continue loop, "end" to finish
    """
    # Check for errors
    error = state.get("error")
    if error:
        logger.warning(f"Workflow has error, ending: {error}")
        return "end"

    # Check if validated
    is_validated = state.get("is_validated", False)
    if is_validated:
        logger.info("Validation PASSED - story faithfully translated to panels")
        return "end"

    # Check iteration limit
    iteration = state.get("iteration", 1)
    max_iterations = state.get("max_iterations", 3)

    if iteration > max_iterations:
        logger.warning(
            f"Max iterations ({max_iterations}) reached without validation. "
            f"Final score: {state.get('fidelity_score', 0):.1f}%"
        )
        return "end"

    # Continue loop
    logger.info(
        f"Validation FAILED (score: {state.get('fidelity_score', 0):.1f}%). "
        f"Starting iteration {iteration}/{max_iterations}"
    )
    return "webtoon_scripter"


# ============================================================================
# Workflow Graph
# ============================================================================

def create_fidelity_workflow() -> StateGraph:
    """
    Create the fidelity validation workflow graph.

    Flow:
        story_architect → webtoon_scripter → blind_reader → evaluator
                               ↑                              |
                               └───── (if not validated) ─────┘

    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(WebtoonFidelityState)

    # Add nodes
    workflow.add_node("story_architect", story_architect_node)
    workflow.add_node("webtoon_scripter", webtoon_scripter_node)
    workflow.add_node("blind_reader", blind_reader_node)
    workflow.add_node("evaluator", evaluator_node)

    # Set entry point
    workflow.set_entry_point("story_architect")

    # Linear edges
    workflow.add_edge("story_architect", "webtoon_scripter")
    workflow.add_edge("webtoon_scripter", "blind_reader")
    workflow.add_edge("blind_reader", "evaluator")

    # Conditional edge: continue loop or end
    workflow.add_conditional_edges(
        "evaluator",
        should_continue,
        {
            "webtoon_scripter": "webtoon_scripter",
            "end": END
        }
    )

    return workflow.compile()


# Global workflow instance
fidelity_workflow = create_fidelity_workflow()


# ============================================================================
# Workflow Runner
# ============================================================================

async def run_fidelity_workflow(
    seed: str,
    max_iterations: int = 3,
    fidelity_threshold: float = 80.0
) -> FidelityValidationResponse:
    """
    Run the complete fidelity validation workflow.

    Args:
        seed: Initial concept to generate story from
        max_iterations: Maximum validation iterations (default 3)
        fidelity_threshold: Score needed to pass (default 80.0)

    Returns:
        FidelityValidationResponse with results

    Raises:
        Exception: If workflow fails critically
    """
    workflow_id = str(uuid.uuid4())

    # Update evaluator threshold
    fidelity_evaluator.validation_threshold = fidelity_threshold

    initial_state: WebtoonFidelityState = {
        # Input
        "seed": seed,
        # Story Architect outputs (will be filled)
        "original_story": "",
        "story_summary": "",
        "character_motivations": {},
        "key_conflicts": [],
        "plot_points": [],
        # Scripter outputs (will be filled)
        "script_panels": [],
        "characters": [],
        # Blind Reader outputs (will be filled)
        "reconstructed_story": "",
        "inferred_motivations": {},
        "inferred_conflicts": [],
        "unclear_elements": [],
        "reader_confidence": 0.0,
        # Evaluator outputs (will be filled)
        "fidelity_score": 0.0,
        "information_gaps": [],
        "critique": None,
        # Control
        "iteration": 1,
        "max_iterations": max_iterations,
        "is_validated": False,
        "current_step": "starting",
        "error": None,
    }

    logger.info(
        f"Starting fidelity workflow {workflow_id} with seed ({len(seed)} chars), "
        f"max_iterations={max_iterations}, threshold={fidelity_threshold}"
    )

    # Track validation history
    validation_history: List[ValidationHistoryEntry] = []

    # Run the workflow
    final_state = await fidelity_workflow.ainvoke(initial_state)

    # Build validation history from final state
    # Note: In a more complex implementation, we'd track this during execution
    if final_state.get("fidelity_score", 0) > 0:
        gap_models = []
        for gap in final_state.get("information_gaps", []):
            if isinstance(gap, dict):
                gap_models.append(FidelityGapModel(
                    category=gap.get("category", "unknown"),
                    original_element=gap.get("original_element", ""),
                    reader_interpretation=gap.get("reader_interpretation", ""),
                    severity=gap.get("severity", "major"),
                    suggested_fix=gap.get("suggested_fix", "")
                ))

        validation_history.append(ValidationHistoryEntry(
            iteration=final_state.get("iteration", 1) - 1,
            fidelity_score=final_state.get("fidelity_score", 0),
            gap_count=len(gap_models),
            information_gaps=gap_models,
            critique=final_state.get("critique", ""),
            reader_confidence=final_state.get("reader_confidence", 0) * 100,
            timestamp=datetime.now()
        ))

    # Determine final status
    if final_state.get("error"):
        status = "error"
    elif final_state.get("is_validated"):
        status = "validated"
    else:
        status = "max_iterations_reached"

    logger.info(
        f"Fidelity workflow {workflow_id} complete. "
        f"Status: {status}, Final score: {final_state.get('fidelity_score', 0):.1f}%, "
        f"Iterations: {final_state.get('iteration', 1) - 1}"
    )

    return FidelityValidationResponse(
        workflow_id=workflow_id,
        status=status,
        final_score=final_state.get("fidelity_score"),
        iterations_used=final_state.get("iteration", 1) - 1,
        original_story=final_state.get("original_story", ""),
        script_panels=final_state.get("script_panels"),
        characters=final_state.get("characters"),
        validation_history=validation_history,
        error=final_state.get("error"),
        created_at=datetime.now()
    )
