"""
Story generation API endpoints.

This module provides REST API endpoints for story generation, including:
- POST /story/generate: Start story generation workflow
- GET /story/status/{workflow_id}: Check workflow status
- GET /story/{story_id}: Retrieve generated story
"""

import logging
import uuid
import asyncio
import time
from typing import Dict
from fastapi import APIRouter, HTTPException

from app.models.story import (
    StoryRequest,
    StoryResponse,
    WorkflowStatus,
    Story
)
from app.workflows.story_workflow import story_workflow


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/story", tags=["Story"])

# In-memory storage (use Redis in production)
workflows: Dict[str, dict] = {}
stories: Dict[str, dict] = {}


@router.post("/generate")
async def generate_story(request: StoryRequest) -> dict:
    """
    Start story generation workflow.
    
    Args:
        request: Story generation request with Reddit post data and mood
        
    Returns:
        Dictionary with workflow_id and status
    """
    workflow_id = str(uuid.uuid4())
    
    logger.info(f"Starting story generation workflow: {workflow_id}")
    logger.info(f"Post: {request.post_title}")
    logger.info(f"Mood: {request.mood}")
    
    # Initialize workflow status
    workflows[workflow_id] = {
        "status": "started",
        "current_step": "initializing",
        "progress": 0.0,
        "start_time": time.time()
    }
    
    # Start workflow in background
    asyncio.create_task(run_workflow(workflow_id, request))
    
    return {
        "workflow_id": workflow_id,
        "status": "started",
        "message": "Story generation started"
    }


async def run_workflow(workflow_id: str, request: StoryRequest):
    """
    Execute story generation workflow in background.
    
    Args:
        workflow_id: Unique workflow identifier
        request: Story generation request
    """
    try:
        # Update status to in_progress
        workflows[workflow_id].update({
            "status": "in_progress",
            "current_step": "writing",
            "progress": 0.1
        })
        
        logger.info(f"Workflow {workflow_id}: Starting writer node")
        
        # Run workflow
        result = await story_workflow.ainvoke({
            "reddit_post": {
                "id": request.post_id,
                "title": request.post_title,
                "content": request.post_content
            },
            "mood": request.mood,
            "rewrite_count": 0,
            "current_step": "writing",
            "draft_story": "",
            "evaluation_score": 0.0,
            "evaluation_feedback": "",
            "final_story": "",
            "error": None
        })
        
        logger.info(f"Workflow {workflow_id}: Completed")
        logger.info(f"Evaluation score: {result.get('evaluation_score', 0)}")
        logger.info(f"Rewrite count: {result.get('rewrite_count', 0)}")
        
        # Check for errors
        if result.get("error"):
            workflows[workflow_id].update({
                "status": "failed",
                "error": result["error"],
                "progress": 0.0
            })
            logger.error(f"Workflow {workflow_id} failed: {result['error']}")
            return
        
        # Store result
        story_id = str(uuid.uuid4())
        end_time = time.time()
        start_time = workflows[workflow_id]["start_time"]
        generation_time = end_time - start_time
        
        stories[story_id] = {
            "id": story_id,
            "content": result.get("final_story") or result["draft_story"],
            "evaluation_score": result.get("evaluation_score", 0.0),
            "rewrite_count": result.get("rewrite_count", 0),
            "workflow_id": workflow_id,
            "generation_time": generation_time,
            "metadata": {
                "post_id": request.post_id,
                "post_title": request.post_title
            }
        }
        
        # Update workflow status
        workflows[workflow_id].update({
            "status": "completed",
            "current_step": "done",
            "progress": 1.0,
            "story_id": story_id
        })
        
        logger.info(f"Workflow {workflow_id}: Story saved with ID {story_id}")
        
    except Exception as e:
        logger.error(f"Workflow {workflow_id} failed with exception: {str(e)}", exc_info=True)
        workflows[workflow_id].update({
            "status": "failed",
            "error": str(e),
            "progress": 0.0
        })


@router.get("/status/{workflow_id}")
async def get_workflow_status(workflow_id: str) -> WorkflowStatus:
    """
    Get workflow status.
    
    Args:
        workflow_id: Unique workflow identifier
        
    Returns:
        WorkflowStatus with current status and progress
        
    Raises:
        HTTPException: If workflow not found
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow_data = workflows[workflow_id]
    
    return WorkflowStatus(
        workflow_id=workflow_id,
        status=workflow_data["status"],
        current_step=workflow_data.get("current_step", ""),
        progress=workflow_data.get("progress", 0.0),
        story_id=workflow_data.get("story_id"),
        error=workflow_data.get("error")
    )


@router.get("/{story_id}")
async def get_story(story_id: str) -> StoryResponse:
    """
    Get generated story.
    
    Args:
        story_id: Unique story identifier
        
    Returns:
        StoryResponse with story and metadata
        
    Raises:
        HTTPException: If story not found
    """
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")
    
    story_data = stories[story_id]
    
    story = Story(
        id=story_data["id"],
        content=story_data["content"],
        evaluation_score=story_data["evaluation_score"],
        rewrite_count=story_data["rewrite_count"],
        metadata=story_data.get("metadata")
    )
    
    return StoryResponse(
        story=story,
        generation_time=story_data.get("generation_time", 0.0),
        workflow_info={
            "evaluation_score": story_data["evaluation_score"],
            "rewrite_count": story_data["rewrite_count"]
        }
    )
