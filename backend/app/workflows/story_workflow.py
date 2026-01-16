"""
LangGraph workflow for story generation.

This module implements the complete story generation workflow using LangGraph:
Writer → Evaluator → (conditional) Rewriter → END

The workflow automatically evaluates generated stories and conditionally rewrites
them if they don't meet quality thresholds.
"""

from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END
from app.services.story_writer import story_writer, RedditPost
from app.services.story_evaluator import story_evaluator
from app.services.story_rewriter import story_rewriter
from app.config import get_settings


class StoryWorkflowState(TypedDict):
    """
    State for the story generation workflow.
    
    Attributes:
        reddit_post: Input Reddit post data
        mood: Story mood/style
        draft_story: Initial generated story
        evaluation_score: Score from evaluator
        evaluation_feedback: Feedback from evaluator
        final_story: Final story (after potential rewrite)
        rewrite_count: Number of rewrites performed
        current_step: Current workflow step
        error: Error message if workflow fails
    """
    reddit_post: dict
    mood: str
    draft_story: str
    evaluation_score: float
    evaluation_feedback: str
    final_story: str
    rewrite_count: int
    current_step: str
    error: Optional[str]


async def writer_node(state: StoryWorkflowState) -> StoryWorkflowState:
    """
    Writer node: Generate initial story from Reddit post.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with draft story
    """
    try:
        post_data = state["reddit_post"]
        mood = state.get("mood", "modern_romance")
        
        post = RedditPost(
            id=post_data.get("id", ""),
            title=post_data.get("title", ""),
            content=post_data.get("content", ""),
            mood=mood
        )
        
        story = await story_writer.write_story(post)
        
        return {
            **state,
            "draft_story": story,
            "current_step": "evaluating",
        }
    except Exception as e:
        return {
            **state,
            "error": f"Writer failed: {str(e)}",
            "current_step": "failed"
        }


async def evaluator_node(state: StoryWorkflowState) -> StoryWorkflowState:
    """
    Evaluator node: Evaluate story quality.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with evaluation results
    """
    try:
        # Evaluate the most recent story (final_story if exists, otherwise draft)
        story_to_evaluate = state.get("final_story") or state["draft_story"]
        
        evaluation = await story_evaluator.evaluate_story(story_to_evaluate)
        
        return {
            **state,
            "evaluation_score": evaluation.score,
            "evaluation_feedback": evaluation.feedback,
            "current_step": "evaluated",
        }
    except Exception as e:
        return {
            **state,
            "error": f"Evaluator failed: {str(e)}",
            "current_step": "failed"
        }


async def rewriter_node(state: StoryWorkflowState) -> StoryWorkflowState:
    """
    Rewriter node: Rewrite story based on feedback.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with rewritten story
    """
    try:
        rewritten = await story_rewriter.rewrite_story(
            state["draft_story"],
            state["evaluation_feedback"]
        )
        
        return {
            **state,
            "final_story": rewritten,
            "rewrite_count": state.get("rewrite_count", 0) + 1,
            "current_step": "rewriting",
        }
    except Exception as e:
        return {
            **state,
            "error": f"Rewriter failed: {str(e)}",
            "current_step": "failed"
        }


def should_rewrite(state: StoryWorkflowState) -> Literal["rewrite", "end"]:
    """
    Routing function: Decide if story needs rewriting.
    
    Args:
        state: Current workflow state
        
    Returns:
        "rewrite" if story needs improvement, "end" otherwise
    """
    settings = get_settings()
    score = state.get("evaluation_score", 10.0)
    rewrite_count = state.get("rewrite_count", 0)
    
    # Only rewrite once if score is below threshold
    # After rewrite, always end (no loop back to evaluator)
    if score < settings.story_evaluation_threshold and rewrite_count == 0:
        return "rewrite"
    
    return "end"


def create_story_workflow() -> StateGraph:
    """
    Create the story generation workflow graph.
    
    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(StoryWorkflowState)
    
    # Add nodes
    workflow.add_node("writer", writer_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("rewriter", rewriter_node)
    
    # Add edges
    workflow.set_entry_point("writer")
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
    
    # After rewrite, go directly to END (no loop back)
    workflow.add_edge("rewriter", END)
    
    return workflow.compile()


# Global workflow instance
story_workflow = create_story_workflow()
