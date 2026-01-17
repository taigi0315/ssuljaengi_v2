"""
LangGraph workflow for webtoon script generation with evaluation loop.

This module implements the complete webtoon generation workflow using LangGraph:
Writer → Evaluator → (conditional) Rewriter → Evaluator → END

The workflow automatically evaluates generated scripts and conditionally rewrites
them if they don't meet quality thresholds. Maximum 2 rewrites.
"""

import logging
from typing import TypedDict, Literal, Optional, Any
from langgraph.graph import StateGraph, END
from app.services.webtoon_writer import webtoon_writer
from app.services.webtoon_evaluator import webtoon_evaluator, WebtoonEvaluation
from app.services.webtoon_rewriter import webtoon_rewriter
from app.models.story import WebtoonScript
from app.config import get_settings


logger = logging.getLogger(__name__)


class WebtoonWorkflowState(TypedDict):
    """
    State for the webtoon generation workflow.
    
    Attributes:
        story: Input story text to convert
        genre: Genre style for the webtoon
        webtoon_script: Generated WebtoonScript (or None if not yet generated)
        evaluation_score: Score from evaluator (0-10)
        evaluation_feedback: Feedback from evaluator for rewriter
        evaluation_issues: List of specific issues found
        rewrite_count: Number of rewrites performed
        current_step: Current workflow step name
        error: Error message if workflow fails
    """
    story: str
    genre: str
    webtoon_script: Optional[dict]  # Serialized WebtoonScript
    evaluation_score: float
    evaluation_feedback: str
    evaluation_issues: list
    rewrite_count: int
    current_step: str
    error: Optional[str]


async def webtoon_writer_node(state: WebtoonWorkflowState) -> WebtoonWorkflowState:
    """
    Writer node: Generate initial webtoon script from story.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with generated webtoon script
    """
    try:
        story = state["story"]
        genre = state.get("genre", "MODERN_ROMANCE_DRAMA_MANHWA")
        
        logger.info(f"Generating webtoon script for story ({len(story)} chars) with genre {genre}")
        
        script = await webtoon_writer.convert_story_to_script(story, genre)
        
        # Serialize to dict for state (TypedDict doesn't support Pydantic models directly)
        script_dict = {
            "characters": [c.model_dump() for c in script.characters],
            "panels": [p.model_dump() for p in script.panels],
            "script_id": getattr(script, 'script_id', None),
        }
        
        logger.info(f"Generated script with {len(script.panels)} panels")
        
        return {
            **state,
            "webtoon_script": script_dict,
            "current_step": "evaluating",
        }
    except Exception as e:
        logger.error(f"Writer node failed: {str(e)}", exc_info=True)
        return {
            **state,
            "error": f"Writer failed: {str(e)}",
            "current_step": "failed"
        }


async def webtoon_evaluator_node(state: WebtoonWorkflowState) -> WebtoonWorkflowState:
    """
    Evaluator node: Evaluate webtoon script quality.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with evaluation results
    """
    try:
        script_dict = state.get("webtoon_script")
        if not script_dict:
            return {
                **state,
                "error": "No script to evaluate",
                "current_step": "failed"
            }
        
        # Reconstruct WebtoonScript from dict
        script = WebtoonScript(**script_dict)
        
        logger.info(f"Evaluating script with {len(script.panels)} panels")
        
        evaluation = webtoon_evaluator.evaluate_script(script)
        
        logger.info(
            f"Evaluation complete: score={evaluation.score}, "
            f"valid={evaluation.is_valid}, issues={len(evaluation.issues)}"
        )
        
        return {
            **state,
            "evaluation_score": evaluation.score,
            "evaluation_feedback": evaluation.feedback,
            "evaluation_issues": evaluation.issues,
            "current_step": "evaluated",
        }
    except Exception as e:
        logger.error(f"Evaluator node failed: {str(e)}", exc_info=True)
        return {
            **state,
            "error": f"Evaluator failed: {str(e)}",
            "current_step": "failed"
        }


async def webtoon_rewriter_node(state: WebtoonWorkflowState) -> WebtoonWorkflowState:
    """
    Rewriter node: Rewrite webtoon script based on feedback.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with rewritten script
    """
    try:
        script_dict = state.get("webtoon_script")
        feedback = state.get("evaluation_feedback", "")
        story = state.get("story", "")
        
        if not script_dict:
            return {
                **state,
                "error": "No script to rewrite",
                "current_step": "failed"
            }
        
        # Reconstruct WebtoonScript from dict
        original_script = WebtoonScript(**script_dict)
        
        logger.info(
            f"Rewriting script (attempt {state.get('rewrite_count', 0) + 1}). "
            f"Feedback: {feedback[:100]}..."
        )
        
        rewritten_script = await webtoon_rewriter.rewrite_script(
            original_script,
            feedback,
            story
        )
        
        # Serialize back to dict
        script_dict = {
            "characters": [c.model_dump() for c in rewritten_script.characters],
            "panels": [p.model_dump() for p in rewritten_script.panels],
            "script_id": getattr(rewritten_script, 'script_id', None),
        }
        
        logger.info(f"Rewritten script has {len(rewritten_script.panels)} panels")
        
        return {
            **state,
            "webtoon_script": script_dict,
            "rewrite_count": state.get("rewrite_count", 0) + 1,
            "current_step": "rewritten",
        }
    except Exception as e:
        logger.error(f"Rewriter node failed: {str(e)}", exc_info=True)
        return {
            **state,
            "error": f"Rewriter failed: {str(e)}",
            "current_step": "failed"
        }


def should_rewrite(state: WebtoonWorkflowState) -> Literal["rewrite", "end"]:
    """
    Routing function: Decide if script needs rewriting.
    
    Args:
        state: Current workflow state
        
    Returns:
        "rewrite" if script needs improvement, "end" otherwise
    """
    settings = get_settings()
    score = state.get("evaluation_score", 10.0)
    rewrite_count = state.get("rewrite_count", 0)
    error = state.get("error")
    
    # If there was an error, don't try to rewrite
    if error:
        logger.warning(f"Workflow has error, ending: {error}")
        return "end"
    
    # Check if score is below threshold and we haven't exceeded max rewrites
    max_rewrites = settings.webtoon_max_rewrites
    threshold = settings.webtoon_evaluation_threshold
    
    if score < threshold and rewrite_count < max_rewrites:
        logger.info(
            f"Score {score} < threshold {threshold}, "
            f"rewrite {rewrite_count + 1}/{max_rewrites}"
        )
        return "rewrite"
    
    if score < threshold:
        logger.warning(
            f"Score {score} still below threshold after {rewrite_count} rewrites. "
            "Accepting best effort."
        )
    else:
        logger.info(f"Score {score} >= threshold {threshold}. Script approved.")
    
    return "end"


def create_webtoon_workflow() -> StateGraph:
    """
    Create the webtoon generation workflow graph.
    
    Flow:
        START → writer → evaluator → (conditional)
            if score < threshold and rewrites < 2:
                → rewriter → evaluator → ...
            else:
                → END
    
    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(WebtoonWorkflowState)
    
    # Add nodes
    workflow.add_node("writer", webtoon_writer_node)
    workflow.add_node("evaluator", webtoon_evaluator_node)
    workflow.add_node("rewriter", webtoon_rewriter_node)
    
    # Set entry point
    workflow.set_entry_point("writer")
    
    # Add edges
    workflow.add_edge("writer", "evaluator")
    
    # Conditional edge: rewrite or end based on evaluation
    workflow.add_conditional_edges(
        "evaluator",
        should_rewrite,
        {
            "rewrite": "rewriter",
            "end": END
        }
    )
    
    # After rewrite, go back to evaluator (creates the loop)
    workflow.add_edge("rewriter", "evaluator")
    
    return workflow.compile()


# Global workflow instance
webtoon_workflow = create_webtoon_workflow()


async def run_webtoon_workflow(story: str, genre: str = "MODERN_ROMANCE_DRAMA_MANHWA") -> WebtoonScript:
    """
    Run the complete webtoon generation workflow.
    
    Args:
        story: The story text to convert
        genre: Genre style for the webtoon
        
    Returns:
        Generated WebtoonScript
        
    Raises:
        Exception: If workflow fails
    """
    initial_state: WebtoonWorkflowState = {
        "story": story,
        "genre": genre,
        "webtoon_script": None,
        "evaluation_score": 0.0,
        "evaluation_feedback": "",
        "evaluation_issues": [],
        "rewrite_count": 0,
        "current_step": "starting",
        "error": None,
    }
    
    logger.info(f"Starting webtoon workflow for story ({len(story)} chars)")
    
    # Run the workflow
    final_state = await webtoon_workflow.ainvoke(initial_state)
    
    # Check for errors
    if final_state.get("error"):
        raise Exception(final_state["error"])
    
    # Extract the final script
    script_dict = final_state.get("webtoon_script")
    if not script_dict:
        raise Exception("Workflow completed but no script was generated")
    
    # Reconstruct WebtoonScript
    script = WebtoonScript(**script_dict)
    
    logger.info(
        f"Webtoon workflow complete. Final score: {final_state.get('evaluation_score')}, "
        f"rewrites: {final_state.get('rewrite_count')}, panels: {len(script.panels)}"
    )
    
    return script
