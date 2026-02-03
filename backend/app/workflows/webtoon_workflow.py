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
from app.services.sfx_planner import plan_sfx_for_panels
from app.models.sfx import SFXBundle
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
    story_genre: str
    image_style: str
    webtoon_script: Optional[dict]  # Serialized WebtoonScript
    evaluation_score: float
    evaluation_feedback: str
    evaluation_issues: list
    best_webtoon_script: Optional[dict]  # Best attempt across rewrites
    best_evaluation_score: float
    best_evaluation_feedback: str
    best_evaluation_issues: list
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
        story_genre = state.get("story_genre", "MODERN_ROMANCE_DRAMA")
        image_style = state.get("image_style", "SOFT_ROMANTIC_WEBTOON")
        
        logger.info(f"Generating webtoon script for story ({len(story)} chars) with style {image_style}")
        
        script = await webtoon_writer.convert_story_to_script(story, story_genre, image_style)
        
        # Serialize to dict for state (TypedDict doesn't support Pydantic models directly)
        script_dict = {
            "characters": [c.model_dump() for c in script.characters],
            "scenes": [s.model_dump() for s in script.scenes],
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
        
        updated_state: WebtoonWorkflowState = {
            **state,
            "evaluation_score": evaluation.score,
            "evaluation_feedback": evaluation.feedback,
            "evaluation_issues": evaluation.issues,
            "current_step": "evaluated",
        }
        
        # Keep the best-scoring script so later rewrites can't regress panel count/quality
        prev_best_score = state.get("best_evaluation_score", float("-inf"))
        if (updated_state["evaluation_score"] >= prev_best_score) or (not state.get("best_webtoon_script")):
            updated_state["best_webtoon_script"] = script_dict
            updated_state["best_evaluation_score"] = updated_state["evaluation_score"]
            updated_state["best_evaluation_feedback"] = updated_state["evaluation_feedback"]
            updated_state["best_evaluation_issues"] = updated_state["evaluation_issues"]
            logger.info(f"New best script selected: score={updated_state['best_evaluation_score']}")
        
        return updated_state
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
            "scenes": [s.model_dump() for s in rewritten_script.scenes],
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
        # Instead of failing, continue with original script and mark rewrite as failed
        logger.warning("Continuing workflow with original script due to rewriter failure")
        return {
            **state,
            "rewrite_count": state.get("rewrite_count", 0) + 1,
            "current_step": "rewrite_failed_continuing",
            "rewriter_error": str(e)
        }

async def sfx_enhancer_node(state: WebtoonWorkflowState) -> WebtoonWorkflowState:
    """
    SFX Enhancer node: Add SFX plans to panels.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with SFX-enriched script
    """
    try:
        # Prefer best attempt across rewrites (prevents last rewrite regression)
        script_dict = state.get("best_webtoon_script") or state.get("webtoon_script")
        if not script_dict:
            return {
                **state,
                "error": "No script to enhance with SFX",
                "current_step": "failed"
            }
        
        # Reconstruct WebtoonScript from dict
        script = WebtoonScript(**script_dict)
        
        logger.info(f"Planning SFX for {len(script.panels)} panels")
        
        # Generate SFX plans
        sfx_bundles = plan_sfx_for_panels(script.panels)
        
        # Apply SFX to panels
        for i, panel in enumerate(script.panels):
            # Find matching bundle (should be 1-to-1 matching by index/panel_number)
            bundle = next((b for b in sfx_bundles if b.panel_number == panel.panel_number), None)
            
            if bundle and bundle.has_effects:
                # Convert bundle effects to simple dict list for generic compatibility
                effects = []
                
                # Impact Texts
                for it in bundle.impact_texts:
                    effects.append({
                        "type": "impact_text",
                        "description": it.text,  # Use text as description for prompt
                        "intensity": "high" if it.size in ["large", "massive"] else "medium",
                        "position": "overlay",
                        "details": f"Style: {it.style.value}, Text: {it.text}"
                    })
                
                # Motion Effects
                for me in bundle.motion_effects:
                    effects.append({
                        "type": me.type.value,
                        "description": f"{me.type.value} moving {me.direction.value}",
                        "intensity": me.intensity.value,
                        "position": "background"
                    })
                
                # Screen Effects
                for se in bundle.screen_effects:
                    effects.append({
                        "type": "screen_effect",
                        "description": f"{se.type.value} effect",
                        "intensity": se.intensity.value,
                        "position": "screen"
                    })
                
                # Emotional Effects
                for ee in bundle.emotional_effects:
                    effects.append({
                        "type": "emotional_effect",
                        "description": f"{ee.type.value}",
                        "intensity": ee.intensity.value,
                        "position": ee.position.value
                    })
                
                panel.sfx_effects = effects
                
                # APPEND SFX TO VISUAL PROMPT FOR VISIBILITY
                # This ensures the user sees it in the text interactions and the image generator definitely gets it.
                sfx_summary = "; ".join([f"{e['type']}: {e['description']}" for e in effects])
                if sfx_summary:
                    panel.visual_prompt += f"\n[SFX: {sfx_summary}]"

                logger.info(f"Added {len(effects)} SFX to panel {panel.panel_number}")
        
        # Serialize back to dict
        script_dict = {
            "characters": [c.model_dump() for c in script.characters],
            "scenes": [s.model_dump() for s in script.scenes],
            "script_id": getattr(script, 'script_id', None),
        }
        
        return {
            **state,
            "webtoon_script": script_dict,
            "current_step": "sfx_planned",
        }
    except Exception as e:
        logger.error(f"SFX node failed: {str(e)}", exc_info=True)
        # Don't fail the whole workflow just for SFX
        logger.warning("Continuing without SFX due to error")
        return {
            **state,
            "current_step": "sfx_failed" # Mark as failed but keep script
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
    current_step = state.get("current_step", "")
    
    # If there was an error, don't try to rewrite
    if error:
        logger.warning(f"Workflow has error, ending: {error}")
        return "end"
    
    # If rewriter failed but we're continuing, don't try to rewrite again
    if current_step == "rewrite_failed_continuing":
        logger.warning("Rewriter failed, continuing to SFX with original script")
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
    workflow.add_node("sfx_enhancer", sfx_enhancer_node)
    
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
            "end": "sfx_enhancer"
        }
    )
    
    # After SFX, go to END
    workflow.add_edge("sfx_enhancer", END)
    
    # After rewrite, go back to evaluator (creates the loop)
    workflow.add_edge("rewriter", "evaluator")
    
    return workflow.compile()


# Global workflow instance
webtoon_workflow = create_webtoon_workflow()


async def run_webtoon_workflow(story: str, story_genre: str = "MODERN_ROMANCE_DRAMA", image_style: str = "SOFT_ROMANTIC_WEBTOON") -> WebtoonScript:
    """
    Run the complete webtoon generation workflow.
    
    Args:
        story: The story text to convert
        image_style: Visual style for the webtoon
        
    Returns:
        Generated WebtoonScript
        
    Raises:
        Exception: If workflow fails
    """
    initial_state: WebtoonWorkflowState = {
        "story": story,
        "story_genre": story_genre,
        "image_style": image_style,
        "webtoon_script": None,
        "evaluation_score": 0.0,
        "evaluation_feedback": "",
        "evaluation_issues": [],
        "best_webtoon_script": None,
        "best_evaluation_score": float("-inf"),
        "best_evaluation_feedback": "",
        "best_evaluation_issues": [],
        "rewrite_count": 0,
        "current_step": "starting",
        "error": None,
    }
    
    logger.info(f"Starting webtoon workflow for story ({len(story)} chars)")
    
    # Run the workflow
    final_state = await webtoon_workflow.ainvoke(initial_state)
    
    # Check for critical errors (but allow rewriter failures)
    error = final_state.get("error")
    current_step = final_state.get("current_step", "")
    
    if error and current_step != "rewrite_failed_continuing":
        raise Exception(error)
    
    # Extract the best script (not necessarily the last attempt)
    script_dict = final_state.get("best_webtoon_script") or final_state.get("webtoon_script")
    if not script_dict:
        raise Exception("Workflow completed but no script was generated")
    
    # Reconstruct WebtoonScript
    script = WebtoonScript(**script_dict)
    
    # Log any rewriter errors as warnings
    rewriter_error = final_state.get("rewriter_error")
    if rewriter_error:
        logger.warning(f"Workflow completed with rewriter error: {rewriter_error}")
    
    logger.info(
        f"Webtoon workflow complete. Final score: {final_state.get('evaluation_score')}, "
        f"best score: {final_state.get('best_evaluation_score')}, "
        f"rewrites: {final_state.get('rewrite_count')}, panels: {len(script.panels)}"
    )
    
    return script
