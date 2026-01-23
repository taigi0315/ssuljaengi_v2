"""
Enhanced LangGraph workflow for webtoon script generation.

This module implements a modular agent-based workflow with specialized agents:
- Story Analyst: Extracts key information from story
- Scene Planner: Plans scene structure and beats
- Cinematographer: Plans shot types and compositions
- Mood Designer: Assigns per-scene moods
- Visual Prompter: Formats image generation prompts
- SFX Planner: Plans visual effects
- Panel Composer: Groups panels into pages

v2.0.0: Phase 4 Architecture - Modular agent system

Flow:
    START → story_analyst → scene_planner → cinematographer → mood_designer
    → visual_prompter → sfx_planner → panel_composer → evaluator
    → (conditional) target_rewriter → evaluator → END
"""

import logging
from typing import TypedDict, Literal, Optional, List, Dict, Any
from enum import Enum
from langgraph.graph import StateGraph, END

from app.models.story import WebtoonScript, WebtoonPanel, Character
from app.services.webtoon_writer import webtoon_writer
from app.services.webtoon_evaluator import webtoon_evaluator, WebtoonEvaluation
from app.services.webtoon_rewriter import webtoon_rewriter
from app.services.mood_designer import mood_designer, MoodAssignment
from app.services.panel_composer import group_panels_into_pages, Page, calculate_page_statistics
from app.services.style_composer import get_legacy_style_with_mood
from app.prompt.multi_panel import format_panels_from_webtoon_panels
from app.config import get_settings


logger = logging.getLogger(__name__)


# ============================================================================
# Agent Types for Targeted Rewriting (Task 4.3.1)
# ============================================================================

class AgentType(str, Enum):
    """Types of agents in the workflow for targeted rewriting."""
    STORY_ANALYST = "story_analyst"
    SCENE_PLANNER = "scene_planner"
    CINEMATOGRAPHER = "cinematographer"
    MOOD_DESIGNER = "mood_designer"
    VISUAL_PROMPTER = "visual_prompter"
    SFX_PLANNER = "sfx_planner"
    PANEL_COMPOSER = "panel_composer"
    WRITER = "writer"  # Legacy monolithic writer


# Issue to agent mapping for targeted rewriting
ISSUE_AGENT_MAP = {
    # Story/structure issues -> Scene Planner
    "scene_count": AgentType.SCENE_PLANNER,
    "story_structure": AgentType.SCENE_PLANNER,
    "Only": AgentType.SCENE_PLANNER,  # "Only X panels"
    "Too many panels": AgentType.SCENE_PLANNER,

    # Dialogue issues -> Scene Planner (dialogue is part of scene planning)
    "dialogue": AgentType.SCENE_PLANNER,
    "dialogue_coverage": AgentType.SCENE_PLANNER,

    # Shot/composition issues -> Cinematographer
    "shot_variety": AgentType.CINEMATOGRAPHER,
    "Shot variety": AgentType.CINEMATOGRAPHER,
    "close-up": AgentType.CINEMATOGRAPHER,
    "consecutive": AgentType.CINEMATOGRAPHER,

    # Frame/composition issues -> Cinematographer
    "visual_dynamism": AgentType.CINEMATOGRAPHER,
    "frame": AgentType.CINEMATOGRAPHER,
    "Uniform framing": AgentType.CINEMATOGRAPHER,

    # Visual prompt issues -> Visual Prompter
    "visual_prompt": AgentType.VISUAL_PROMPTER,
    "prompt": AgentType.VISUAL_PROMPTER,

    # Character issues -> Story Analyst
    "character": AgentType.STORY_ANALYST,
    "Character": AgentType.STORY_ANALYST,

    # Page grouping issues -> Panel Composer
    "page": AgentType.PANEL_COMPOSER,
    "Page": AgentType.PANEL_COMPOSER,
    "grouping": AgentType.PANEL_COMPOSER,
}


# ============================================================================
# Enhanced Workflow State (Task 4.2.2)
# ============================================================================

class EnhancedWebtoonState(TypedDict):
    """
    State for the enhanced webtoon generation workflow.

    Contains outputs from each agent stage for full traceability.
    """
    # Input
    story: str
    story_genre: str
    image_style: str

    # Story Analyst output
    story_analysis: Optional[Dict[str, Any]]

    # Scene Planner output
    scene_plan: Optional[Dict[str, Any]]

    # Generated script (from writer or scene_planner)
    webtoon_script: Optional[dict]
    characters: Optional[List[dict]]
    panels: Optional[List[dict]]

    # Cinematographer output
    shot_plan: Optional[Dict[str, Any]]

    # Mood Designer output
    mood_assignments: Optional[List[dict]]

    # Visual Prompter output
    enhanced_prompts: Optional[List[str]]

    # SFX Planner output
    sfx_plan: Optional[Dict[str, Any]]

    # Panel Composer output
    page_groupings: Optional[List[dict]]
    page_statistics: Optional[Dict[str, Any]]

    # Evaluation
    evaluation_score: float
    evaluation_feedback: str
    evaluation_issues: List[str]
    score_breakdown: Optional[Dict[str, float]]

    # Rewrite tracking (Task 4.3.3)
    rewrite_count: int
    rewrite_history: List[Dict[str, Any]]  # Track which agent was rewritten
    target_agent: Optional[str]  # Which agent to rewrite

    # Workflow state
    current_step: str
    error: Optional[str]


# ============================================================================
# Agent Node Functions (Task 4.2.3)
# ============================================================================

async def story_analyst_node(state: EnhancedWebtoonState) -> EnhancedWebtoonState:
    """
    Story Analyst: Extract key information from the input story.

    Analyzes story to identify:
    - Main characters and their traits
    - Key plot points
    - Emotional beats
    - Setting/environment details

    Note: Currently delegates to the monolithic writer for initial generation.
    Future: Separate LLM call for analysis only.
    """
    logger.info("Story Analyst: Analyzing story...")

    try:
        story = state["story"]

        # For now, we use a simple analysis structure
        # Future: LLM-based story analysis
        analysis = {
            "story_length": len(story),
            "estimated_scenes": max(8, min(20, len(story) // 500)),
            "genre": state.get("story_genre", "MODERN_ROMANCE_DRAMA"),
            "analyzed": True
        }

        logger.info(f"Story analysis complete: {analysis['estimated_scenes']} estimated scenes")

        return {
            **state,
            "story_analysis": analysis,
            "current_step": "story_analyzed"
        }

    except Exception as e:
        logger.error(f"Story Analyst failed: {e}")
        return {
            **state,
            "error": f"Story Analyst failed: {e}",
            "current_step": "failed"
        }


async def scene_planner_node(state: EnhancedWebtoonState) -> EnhancedWebtoonState:
    """
    Scene Planner: Generate scene structure and beats.

    Currently uses the monolithic writer, which handles scene planning internally.
    Outputs the initial WebtoonScript with panels.
    """
    logger.info("Scene Planner: Planning scenes...")

    try:
        story = state["story"]
        story_genre = state.get("story_genre", "MODERN_ROMANCE_DRAMA")
        image_style = state.get("image_style", "SOFT_ROMANTIC_WEBTOON")

        # Use the existing webtoon writer for scene generation
        script = await webtoon_writer.convert_story_to_script(story, story_genre, image_style)

        # Serialize to dict
        characters = [c.model_dump() for c in script.characters]
        panels = [p.model_dump() for p in script.panels]

        scene_plan = {
            "total_panels": len(panels),
            "character_count": len(characters),
            "planned": True
        }

        logger.info(f"Scene planning complete: {len(panels)} panels, {len(characters)} characters")

        return {
            **state,
            "webtoon_script": {
                "characters": characters,
                "panels": panels
            },
            "characters": characters,
            "panels": panels,
            "scene_plan": scene_plan,
            "current_step": "scenes_planned"
        }

    except Exception as e:
        logger.error(f"Scene Planner failed: {e}", exc_info=True)
        return {
            **state,
            "error": f"Scene Planner failed: {e}",
            "current_step": "failed"
        }


async def cinematographer_node(state: EnhancedWebtoonState) -> EnhancedWebtoonState:
    """
    Cinematographer: Analyze and optimize shot compositions.

    Reviews panels and suggests shot improvements for:
    - Shot variety
    - Frame composition
    - Visual dynamism

    Note: Shot types are already in panels from scene_planner.
    This node validates and logs shot distribution.
    """
    logger.info("Cinematographer: Analyzing shots...")

    try:
        panels = state.get("panels", [])
        if not panels:
            return {
                **state,
                "error": "No panels for cinematographer",
                "current_step": "failed"
            }

        # Analyze shot distribution
        shot_types = [p.get("shot_type", "Medium shot") for p in panels]
        shot_counts = {}
        for st in shot_types:
            normalized = st.lower().strip()
            shot_counts[normalized] = shot_counts.get(normalized, 0) + 1

        # Calculate variety metrics
        unique_shots = len(shot_counts)
        most_common = max(shot_counts.values()) if shot_counts else 0
        variety_ratio = unique_shots / len(panels) if panels else 0

        shot_plan = {
            "total_shots": len(panels),
            "unique_shot_types": unique_shots,
            "shot_distribution": shot_counts,
            "variety_ratio": round(variety_ratio, 2),
            "most_common_count": most_common,
            "analyzed": True
        }

        logger.info(f"Cinematography analysis: {unique_shots} unique shots, variety={variety_ratio:.2f}")

        return {
            **state,
            "shot_plan": shot_plan,
            "current_step": "shots_analyzed"
        }

    except Exception as e:
        logger.error(f"Cinematographer failed: {e}")
        return {
            **state,
            "error": f"Cinematographer failed: {e}",
            "current_step": "failed"
        }


async def mood_designer_node(state: EnhancedWebtoonState) -> EnhancedWebtoonState:
    """
    Mood Designer: Assign per-scene moods based on emotional content.

    Uses the mood_designer service to analyze panels and assign moods.
    """
    logger.info("Mood Designer: Assigning moods...")

    try:
        panels_data = state.get("panels", [])
        if not panels_data:
            return {
                **state,
                "error": "No panels for mood designer",
                "current_step": "failed"
            }

        # Convert to WebtoonPanel objects
        panels = [WebtoonPanel(**p) for p in panels_data]

        # Assign moods using the mood designer service
        assignments = mood_designer.assign_moods(panels)

        # Serialize assignments
        mood_data = [
            {
                "panel_number": a.panel_number,
                "mood_name": a.mood.name,
                "intensity": a.mood.intensity,
                "detected_context": a.detected_context,
                "color_temperature": a.mood.color_temperature.value,
                "lighting_mood": a.mood.lighting_mood.value,
                "reasoning": a.reasoning
            }
            for a in assignments
        ]

        logger.info(f"Mood assignment complete for {len(assignments)} panels")

        return {
            **state,
            "mood_assignments": mood_data,
            "current_step": "moods_assigned"
        }

    except Exception as e:
        logger.error(f"Mood Designer failed: {e}")
        return {
            **state,
            "error": f"Mood Designer failed: {e}",
            "current_step": "failed"
        }


async def visual_prompter_node(state: EnhancedWebtoonState) -> EnhancedWebtoonState:
    """
    Visual Prompter: Enhance visual prompts with mood and style information.

    Combines base style with mood modifiers for each panel.
    """
    logger.info("Visual Prompter: Enhancing prompts...")

    try:
        panels = state.get("panels", [])
        mood_assignments = state.get("mood_assignments", [])
        image_style = state.get("image_style", "SOFT_ROMANTIC_WEBTOON")

        if not panels:
            return {
                **state,
                "error": "No panels for visual prompter",
                "current_step": "failed"
            }

        # Create mood lookup
        mood_lookup = {m["panel_number"]: m for m in mood_assignments}

        enhanced_prompts = []
        for panel in panels:
            panel_num = panel.get("panel_number")
            base_prompt = panel.get("visual_prompt", "")
            mood_data = mood_lookup.get(panel_num, {})

            # Get composed style with mood
            intensity = mood_data.get("intensity", 5)
            context = mood_data.get("detected_context", "neutral")

            composed_style = get_legacy_style_with_mood(
                legacy_style_key=image_style,
                emotional_intensity=intensity,
                scene_context=context
            )

            # Combine base prompt with style
            enhanced = f"{base_prompt}\n\n[STYLE & MOOD]\n{composed_style}"
            enhanced_prompts.append(enhanced)

        logger.info(f"Enhanced {len(enhanced_prompts)} visual prompts")

        return {
            **state,
            "enhanced_prompts": enhanced_prompts,
            "current_step": "prompts_enhanced"
        }

    except Exception as e:
        logger.error(f"Visual Prompter failed: {e}")
        return {
            **state,
            "error": f"Visual Prompter failed: {e}",
            "current_step": "failed"
        }


async def sfx_planner_node(state: EnhancedWebtoonState) -> EnhancedWebtoonState:
    """
    SFX Planner: Plan visual effects for panels.

    Reviews panels and their SFX effects (already in panel data).
    Logs SFX distribution for the script.
    """
    logger.info("SFX Planner: Planning effects...")

    try:
        panels = state.get("panels", [])

        # Analyze existing SFX in panels
        panels_with_sfx = 0
        sfx_types = {}

        for panel in panels:
            effects = panel.get("sfx_effects", [])
            if effects:
                panels_with_sfx += 1
                for effect in effects:
                    etype = effect.get("type", "unknown")
                    sfx_types[etype] = sfx_types.get(etype, 0) + 1

        sfx_plan = {
            "panels_with_sfx": panels_with_sfx,
            "total_panels": len(panels),
            "sfx_coverage": round(panels_with_sfx / len(panels), 2) if panels else 0,
            "sfx_distribution": sfx_types,
            "planned": True
        }

        logger.info(f"SFX planning: {panels_with_sfx}/{len(panels)} panels have effects")

        return {
            **state,
            "sfx_plan": sfx_plan,
            "current_step": "sfx_planned"
        }

    except Exception as e:
        logger.error(f"SFX Planner failed: {e}")
        return {
            **state,
            "error": f"SFX Planner failed: {e}",
            "current_step": "failed"
        }


async def panel_composer_node(state: EnhancedWebtoonState) -> EnhancedWebtoonState:
    """
    Panel Composer: Group panels into pages for multi-panel generation.

    Uses the panel_composer service to create page groupings.
    """
    logger.info("Panel Composer: Grouping panels into pages...")

    try:
        panels_data = state.get("panels", [])
        if not panels_data:
            return {
                **state,
                "error": "No panels for panel composer",
                "current_step": "failed"
            }

        # Convert to WebtoonPanel objects
        panels = [WebtoonPanel(**p) for p in panels_data]

        # Group into pages
        pages = group_panels_into_pages(panels)
        stats = calculate_page_statistics(pages)

        # Serialize page data
        page_data = [
            {
                "page_number": page.page_number,
                "panel_indices": page.panel_indices,
                "panel_count": page.panel_count,
                "layout_type": page.layout_type.value,
                "is_single_panel": page.is_single_panel,
                "reasoning": page.reasoning
            }
            for page in pages
        ]

        logger.info(f"Panel composition: {len(pages)} pages from {len(panels)} panels")

        return {
            **state,
            "page_groupings": page_data,
            "page_statistics": stats,
            "current_step": "panels_composed"
        }

    except Exception as e:
        logger.error(f"Panel Composer failed: {e}")
        return {
            **state,
            "error": f"Panel Composer failed: {e}",
            "current_step": "failed"
        }


async def evaluator_node(state: EnhancedWebtoonState) -> EnhancedWebtoonState:
    """
    Evaluator: Evaluate the complete webtoon script.

    Uses the webtoon_evaluator service and identifies which agent
    should be targeted for rewriting if issues are found.
    """
    logger.info("Evaluator: Evaluating script...")

    try:
        script_dict = state.get("webtoon_script")
        if not script_dict:
            return {
                **state,
                "error": "No script to evaluate",
                "current_step": "failed"
            }

        # Reconstruct WebtoonScript
        script = WebtoonScript(**script_dict)

        # Evaluate
        evaluation = webtoon_evaluator.evaluate_script(script)

        # Identify target agent for rewriting (Task 4.3.1)
        target_agent = identify_rewrite_target(evaluation.issues)

        logger.info(
            f"Evaluation: score={evaluation.score}, valid={evaluation.is_valid}, "
            f"issues={len(evaluation.issues)}, target_agent={target_agent}"
        )

        return {
            **state,
            "evaluation_score": evaluation.score,
            "evaluation_feedback": evaluation.feedback,
            "evaluation_issues": evaluation.issues,
            "score_breakdown": evaluation.score_breakdown,
            "target_agent": target_agent,
            "current_step": "evaluated"
        }

    except Exception as e:
        logger.error(f"Evaluator failed: {e}")
        return {
            **state,
            "error": f"Evaluator failed: {e}",
            "current_step": "failed"
        }


async def rewriter_node(state: EnhancedWebtoonState) -> EnhancedWebtoonState:
    """
    Rewriter: Rewrite the script based on evaluation feedback.

    Uses the existing webtoon_rewriter service.
    Tracks which agent triggered the rewrite.
    """
    logger.info("Rewriter: Rewriting script...")

    try:
        script_dict = state.get("webtoon_script")
        feedback = state.get("evaluation_feedback", "")
        story = state.get("story", "")
        target_agent = state.get("target_agent", AgentType.WRITER.value)

        if not script_dict:
            return {
                **state,
                "error": "No script to rewrite",
                "current_step": "failed"
            }

        original_script = WebtoonScript(**script_dict)

        # Track rewrite history
        rewrite_history = state.get("rewrite_history", [])
        rewrite_history.append({
            "attempt": state.get("rewrite_count", 0) + 1,
            "target_agent": target_agent,
            "issues": state.get("evaluation_issues", [])[:3],
            "score_before": state.get("evaluation_score", 0)
        })

        logger.info(f"Rewriting (attempt {len(rewrite_history)}) targeting: {target_agent}")

        # Rewrite
        rewritten_script = await webtoon_rewriter.rewrite_script(
            original_script,
            feedback,
            story
        )

        # Serialize
        new_script_dict = {
            "characters": [c.model_dump() for c in rewritten_script.characters],
            "panels": [p.model_dump() for p in rewritten_script.panels]
        }

        return {
            **state,
            "webtoon_script": new_script_dict,
            "characters": new_script_dict["characters"],
            "panels": new_script_dict["panels"],
            "rewrite_count": state.get("rewrite_count", 0) + 1,
            "rewrite_history": rewrite_history,
            "current_step": "rewritten"
        }

    except Exception as e:
        logger.error(f"Rewriter failed: {e}")
        return {
            **state,
            "error": f"Rewriter failed: {e}",
            "current_step": "failed"
        }


# ============================================================================
# Routing Functions (Task 4.2.5)
# ============================================================================

def identify_rewrite_target(issues: List[str]) -> str:
    """
    Identify which agent should be targeted for rewriting based on issues.

    Task 4.3.1: Maps evaluation issues to responsible agents.

    Args:
        issues: List of issue strings from evaluator

    Returns:
        Agent type string to target for rewriting
    """
    if not issues:
        return AgentType.WRITER.value

    # Score each agent by how many issues match
    agent_scores = {}

    for issue in issues:
        issue_lower = issue.lower()
        for keyword, agent in ISSUE_AGENT_MAP.items():
            if keyword.lower() in issue_lower:
                agent_scores[agent] = agent_scores.get(agent, 0) + 1

    if agent_scores:
        # Return agent with most matching issues
        top_agent = max(agent_scores, key=agent_scores.get)
        return top_agent.value

    # Default to writer if no match
    return AgentType.WRITER.value


def should_rewrite(state: EnhancedWebtoonState) -> Literal["rewrite", "continue_pipeline", "end"]:
    """
    Routing function: Decide if script needs rewriting.

    Task 4.2.5: Conditional routing based on evaluation.

    Returns:
        - "rewrite": Score below threshold, rewrite needed
        - "continue_pipeline": After rewrite, continue to remaining agents
        - "end": Score acceptable or max rewrites reached
    """
    settings = get_settings()
    score = state.get("evaluation_score", 10.0)
    rewrite_count = state.get("rewrite_count", 0)
    error = state.get("error")
    current_step = state.get("current_step", "")

    # If there was an error, end
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


# ============================================================================
# Workflow Graph Definition (Task 4.2.4)
# ============================================================================

def create_enhanced_webtoon_workflow() -> StateGraph:
    """
    Create the enhanced webtoon generation workflow graph.

    Flow:
        START → story_analyst → scene_planner → cinematographer
        → mood_designer → visual_prompter → sfx_planner
        → panel_composer → evaluator → (conditional)
            if score < threshold and rewrites < max:
                → rewriter → cinematographer → ... (re-run pipeline)
            else:
                → END

    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(EnhancedWebtoonState)

    # Add all agent nodes
    workflow.add_node("story_analyst", story_analyst_node)
    workflow.add_node("scene_planner", scene_planner_node)
    workflow.add_node("cinematographer", cinematographer_node)
    workflow.add_node("mood_designer", mood_designer_node)
    workflow.add_node("visual_prompter", visual_prompter_node)
    workflow.add_node("sfx_planner", sfx_planner_node)
    workflow.add_node("panel_composer", panel_composer_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("rewriter", rewriter_node)

    # Set entry point
    workflow.set_entry_point("story_analyst")

    # Define sequential flow through agents
    workflow.add_edge("story_analyst", "scene_planner")
    workflow.add_edge("scene_planner", "cinematographer")
    workflow.add_edge("cinematographer", "mood_designer")
    workflow.add_edge("mood_designer", "visual_prompter")
    workflow.add_edge("visual_prompter", "sfx_planner")
    workflow.add_edge("sfx_planner", "panel_composer")
    workflow.add_edge("panel_composer", "evaluator")

    # Conditional edge after evaluation
    workflow.add_conditional_edges(
        "evaluator",
        should_rewrite,
        {
            "rewrite": "rewriter",
            "end": END
        }
    )

    # After rewrite, go back through the pipeline (starting at cinematographer)
    # This re-runs analysis on the rewritten script
    workflow.add_edge("rewriter", "cinematographer")

    return workflow.compile()


# ============================================================================
# Global Workflow Instance
# ============================================================================

enhanced_webtoon_workflow = create_enhanced_webtoon_workflow()


# ============================================================================
# Main Entry Point
# ============================================================================

async def run_enhanced_webtoon_workflow(
    story: str,
    story_genre: str = "MODERN_ROMANCE_DRAMA",
    image_style: str = "SOFT_ROMANTIC_WEBTOON"
) -> Dict[str, Any]:
    """
    Run the enhanced webtoon generation workflow.

    Args:
        story: The story text to convert
        story_genre: Genre style for narrative content
        image_style: Visual style for the webtoon

    Returns:
        Dictionary containing:
        - webtoon_script: Generated WebtoonScript as dict
        - mood_assignments: Mood data for each panel
        - page_groupings: Page layout information
        - evaluation_score: Final quality score
        - rewrite_history: History of any rewrites

    Raises:
        Exception: If workflow fails
    """
    initial_state: EnhancedWebtoonState = {
        "story": story,
        "story_genre": story_genre,
        "image_style": image_style,
        "story_analysis": None,
        "scene_plan": None,
        "webtoon_script": None,
        "characters": None,
        "panels": None,
        "shot_plan": None,
        "mood_assignments": None,
        "enhanced_prompts": None,
        "sfx_plan": None,
        "page_groupings": None,
        "page_statistics": None,
        "evaluation_score": 0.0,
        "evaluation_feedback": "",
        "evaluation_issues": [],
        "score_breakdown": None,
        "rewrite_count": 0,
        "rewrite_history": [],
        "target_agent": None,
        "current_step": "starting",
        "error": None,
    }

    logger.info(f"Starting enhanced webtoon workflow for story ({len(story)} chars)")

    # Run the workflow
    final_state = await enhanced_webtoon_workflow.ainvoke(initial_state)

    # Check for errors
    if final_state.get("error"):
        raise Exception(final_state["error"])

    # Extract the final script
    script_dict = final_state.get("webtoon_script")
    if not script_dict:
        raise Exception("Workflow completed but no script was generated")

    logger.info(
        f"Enhanced workflow complete. Final score: {final_state.get('evaluation_score')}, "
        f"rewrites: {final_state.get('rewrite_count')}, "
        f"pages: {len(final_state.get('page_groupings', []))}"
    )

    return {
        "webtoon_script": script_dict,
        "characters": final_state.get("characters", []),
        "panels": final_state.get("panels", []),
        "mood_assignments": final_state.get("mood_assignments", []),
        "page_groupings": final_state.get("page_groupings", []),
        "page_statistics": final_state.get("page_statistics", {}),
        "enhanced_prompts": final_state.get("enhanced_prompts", []),
        "evaluation_score": final_state.get("evaluation_score", 0),
        "evaluation_feedback": final_state.get("evaluation_feedback", ""),
        "rewrite_count": final_state.get("rewrite_count", 0),
        "rewrite_history": final_state.get("rewrite_history", []),
    }
