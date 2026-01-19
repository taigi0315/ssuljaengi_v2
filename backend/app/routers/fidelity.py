"""
Fidelity validation API endpoints.

This module provides REST API endpoints for the webtoon fidelity validator:
- POST /fidelity/validate: Start fidelity validation workflow
- GET /fidelity/status/{workflow_id}: Check workflow status
- GET /fidelity/{workflow_id}: Retrieve validation results
"""

import logging
import uuid
import asyncio
import time
import os
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.models.fidelity_state import (
    FidelityValidationRequest,
    FidelityValidationResponse,
    FidelityWorkflowStatus
)
from app.workflows.fidelity_workflow import run_fidelity_workflow
from app.config import get_settings
from app.utils.persistence import JsonStore


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fidelity", tags=["Fidelity Validation"])

# Initialize persistent storage
settings = get_settings()
fidelity_workflows: JsonStore[dict] = JsonStore(
    os.path.join(settings.data_dir, "fidelity_workflows.json")
)
fidelity_results: JsonStore[dict] = JsonStore(
    os.path.join(settings.data_dir, "fidelity_results.json")
)


@router.post("/validate")
async def validate_webtoon_fidelity(request: FidelityValidationRequest) -> dict:
    """
    Start fidelity validation workflow.

    This endpoint initiates the complete fidelity validation process:
    1. Generates a story from the provided seed
    2. Converts it to webtoon panels
    3. Has a "blind reader" reconstruct the story from panels
    4. Compares reconstruction to original
    5. Iterates until validated or max iterations reached

    Args:
        request: Validation request with seed and optional settings

    Returns:
        Dictionary with workflow_id and status
    """
    workflow_id = str(uuid.uuid4())

    logger.info(f"Starting fidelity validation workflow: {workflow_id}")
    logger.info(f"Seed: {request.seed[:100]}...")
    logger.info(f"Max iterations: {request.max_iterations}")
    logger.info(f"Threshold: {request.fidelity_threshold}")

    # Initialize workflow status
    fidelity_workflows[workflow_id] = {
        "status": "started",
        "current_step": "initializing",
        "iteration": 0,
        "progress": 0.0,
        "latest_score": None,
        "start_time": time.time(),
        "error": None
    }
    await fidelity_workflows.save()

    # Start workflow in background
    asyncio.create_task(
        run_fidelity_workflow_async(
            workflow_id,
            request.seed,
            request.max_iterations,
            request.fidelity_threshold
        )
    )

    return {
        "workflow_id": workflow_id,
        "status": "started",
        "message": "Fidelity validation started"
    }


async def run_fidelity_workflow_async(
    workflow_id: str,
    seed: str,
    max_iterations: int,
    fidelity_threshold: float
):
    """
    Execute fidelity validation workflow in background.

    Args:
        workflow_id: Unique workflow identifier
        seed: Story seed text
        max_iterations: Maximum validation iterations
        fidelity_threshold: Score needed to pass
    """
    try:
        # Update status to in_progress
        fidelity_workflows[workflow_id].update({
            "status": "in_progress",
            "current_step": "story_architect",
            "progress": 0.1
        })
        await fidelity_workflows.save()

        # Run the workflow
        result = await run_fidelity_workflow(
            seed=seed,
            max_iterations=max_iterations,
            fidelity_threshold=fidelity_threshold
        )

        # Store the result
        fidelity_results[workflow_id] = result.model_dump()
        await fidelity_results.save()

        # Update final status
        fidelity_workflows[workflow_id].update({
            "status": "completed" if result.status != "error" else "failed",
            "current_step": "complete",
            "progress": 1.0,
            "latest_score": result.final_score,
            "iterations_used": result.iterations_used,
            "is_validated": result.status == "validated",
            "end_time": time.time()
        })
        await fidelity_workflows.save()

        logger.info(
            f"Fidelity workflow {workflow_id} completed. "
            f"Status: {result.status}, Score: {result.final_score}"
        )

    except Exception as e:
        logger.error(f"Fidelity workflow {workflow_id} failed: {str(e)}", exc_info=True)

        fidelity_workflows[workflow_id].update({
            "status": "failed",
            "current_step": "error",
            "error": str(e),
            "end_time": time.time()
        })
        await fidelity_workflows.save()


@router.get("/status/{workflow_id}")
async def get_fidelity_status(workflow_id: str) -> FidelityWorkflowStatus:
    """
    Get fidelity validation workflow status.

    Args:
        workflow_id: Unique workflow identifier

    Returns:
        Current workflow status

    Raises:
        HTTPException: If workflow not found
    """
    if workflow_id not in fidelity_workflows:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow {workflow_id} not found"
        )

    workflow_data = fidelity_workflows[workflow_id]

    # Calculate progress based on step
    progress_map = {
        "initializing": 0.0,
        "story_architect": 0.15,
        "webtoon_scripter": 0.35,
        "blind_reader": 0.55,
        "evaluator": 0.75,
        "complete": 1.0,
        "error": 1.0
    }
    progress = progress_map.get(workflow_data.get("current_step", ""), 0.5)

    return FidelityWorkflowStatus(
        workflow_id=workflow_id,
        status=workflow_data.get("status", "unknown"),
        current_step=workflow_data.get("current_step", "unknown"),
        iteration=workflow_data.get("iteration", 0),
        progress=progress,
        latest_score=workflow_data.get("latest_score"),
        error=workflow_data.get("error")
    )


@router.get("/{workflow_id}")
async def get_fidelity_result(workflow_id: str) -> FidelityValidationResponse:
    """
    Get fidelity validation result.

    Args:
        workflow_id: Unique workflow identifier

    Returns:
        Complete validation results

    Raises:
        HTTPException: If workflow not found or not completed
    """
    # Check if workflow exists
    if workflow_id not in fidelity_workflows:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow {workflow_id} not found"
        )

    # Check if workflow is completed
    workflow_data = fidelity_workflows[workflow_id]
    if workflow_data.get("status") not in ["completed", "failed"]:
        raise HTTPException(
            status_code=202,
            detail=f"Workflow {workflow_id} is still in progress"
        )

    # Get result
    if workflow_id not in fidelity_results:
        raise HTTPException(
            status_code=404,
            detail=f"Results for workflow {workflow_id} not found"
        )

    result_data = fidelity_results[workflow_id]

    return FidelityValidationResponse(**result_data)


@router.post("/validate/sync")
async def validate_webtoon_fidelity_sync(
    request: FidelityValidationRequest
) -> FidelityValidationResponse:
    """
    Run fidelity validation synchronously (blocking).

    This endpoint runs the complete workflow and returns the result.
    Use for testing or when you need immediate results.

    WARNING: This can take 30-120 seconds depending on iterations.

    Args:
        request: Validation request with seed and optional settings

    Returns:
        Complete validation results
    """
    logger.info(f"Starting synchronous fidelity validation")
    logger.info(f"Seed: {request.seed[:100]}...")

    result = await run_fidelity_workflow(
        seed=request.seed,
        max_iterations=request.max_iterations,
        fidelity_threshold=request.fidelity_threshold
    )

    return result
