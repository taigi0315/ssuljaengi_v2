"""Integration tests for Enhanced Webtoon Workflow

Tests the complete LangGraph workflow with all agents working together.
"""

import pytest
from app.workflows.enhanced_webtoon_workflow import (
    enhanced_webtoon_workflow,
    EnhancedWebtoonState,
)


class TestEnhancedWebtoonWorkflow:
    """Test the complete enhanced webtoon workflow."""

    @pytest.mark.asyncio
    async def test_full_workflow_execution(self):
        """Test complete workflow execution from story to final script."""
        # Prepare initial state
        initial_state: EnhancedWebtoonState = {
            "story": """
            Min-ji is a brilliant AI researcher who has just created a revolutionary 
            language model. One day, she meets Ji-hoo, a talented writer struggling 
            with writer's block. Their collaboration leads to an unexpected romance 
            as they discover they complement each other perfectly.
            """,
            "story_genre": "MODERN_ROMANCE_DRAMA",
            "image_style": "SOFT_ROMANTIC_WEBTOON",
            
            # Initialize empty fields
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
            
            # Evaluation fields
            "evaluation_score": 0.0,
            "evaluation_feedback": "",
            "evaluation_issues": [],
            "score_breakdown": None,
            
            # Rewrite tracking
            "rewrite_count": 0,
            "rewrite_history": [],
            "target_agent": None,
            
            # Workflow state
            "current_step": "start",
            "error": None,
        }

        # Execute workflow
        result = await enhanced_webtoon_workflow.ainvoke(initial_state)

        # Verify final state
        assert result is not None
        assert result.get("error") is None, f"Workflow failed: {result.get('error')}"
        
        # Verify story analysis was performed
        assert result.get("story_analysis") is not None
        assert result["story_analysis"]["analyzed"] is True
        
        # Verify scene planning
        assert result.get("scene_plan") is not None
        assert result["scene_plan"]["planned"] is True
        assert result["scene_plan"]["total_panels"] > 0
        
        # Verify script generation
        assert result.get("webtoon_script") is not None
        assert result.get("characters") is not None
        assert result.get("panels") is not None
        assert len(result["panels"]) > 0
        
        # Verify cinematographer analysis
        assert result.get("shot_plan") is not None
        assert result["shot_plan"]["analyzed"] is True
        assert result["shot_plan"]["total_shots"] == len(result["panels"])
        
        # Verify mood assignment
        assert result.get("mood_assignments") is not None
        assert len(result["mood_assignments"]) == len(result["panels"])
        
        # Verify visual prompts enhanced
        assert result.get("enhanced_prompts") is not None
        assert len(result["enhanced_prompts"]) == len(result["panels"])
        
        # Verify SFX planning
        assert result.get("sfx_plan") is not None
        assert result["sfx_plan"]["planned"] is True
        
        # Verify panel composition
        assert result.get("page_groupings") is not None
        assert len(result["page_groupings"]) > 0
        assert result.get("page_statistics") is not None
        
        # Verify evaluation
        assert result.get("evaluation_score") > 0
        assert result.get("evaluation_feedback") is not None
        
        print(f"\n✅ Workflow completed successfully!")
        print(f"   - Total panels: {len(result['panels'])}")
        print(f"   - Total pages: {len(result['page_groupings'])}")
        print(f"   - Evaluation score: {result['evaluation_score']:.2f}")
        print(f"   - Rewrite count: {result['rewrite_count']}")


    @pytest.mark.asyncio
    async def test_workflow_with_rewrite(self):
        """Test workflow with low evaluation score triggering rewrite."""
        # This test uses a minimal story that may trigger rewrites
        initial_state: EnhancedWebtoonState = {
            "story": "Two people meet. They talk. The end.",
            "story_genre": "MODERN_ROMANCE_DRAMA",
            "image_style": "SOFT_ROMANTIC_WEBTOON",
            
            # Initialize empty fields
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
            
            # Evaluation fields
            "evaluation_score": 0.0,
            "evaluation_feedback": "",
            "evaluation_issues": [],
            "score_breakdown": None,
            
            # Rewrite tracking
            "rewrite_count": 0,
            "rewrite_history": [],
            "target_agent": None,
            
            # Workflow state
            "current_step": "start",
            "error": None,
        }

        # Execute workflow
        result = await enhanced_webtoon_workflow.ainvoke(initial_state)

        # Verify execution completed (may or may not trigger rewrite)
        assert result is not None
        assert result.get("error") is None
        
        # Check if rewrite was triggered
        if result["rewrite_count"] > 0:
            print(f"\n✅ Workflow triggered {result['rewrite_count']} rewrite(s)")
            print(f"   - Target agent(s): {[h['target_agent'] for h in result['rewrite_history']]}")
            print(f"   - Final score: {result['evaluation_score']:.2f}")
            
            # Verify rewrite history
            assert result.get("rewrite_history") is not None
            assert len(result["rewrite_history"]) == result["rewrite_count"]
        else:
            print(f"\n✅ Workflow completed without rewrites")
            print(f"   - Score: {result['evaluation_score']:.2f}")


    @pytest.mark.asyncio
    async def test_workflow_error_handling(self):
        """Test workflow behavior with invalid input."""
        # Test with empty story
        initial_state: EnhancedWebtoonState = {
            "story": "",
            "story_genre": "MODERN_ROMANCE_DRAMA",
            "image_style": "SOFT_ROMANTIC_WEBTOON",
            
            # Initialize empty fields
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
            
            # Evaluation fields
            "evaluation_score": 0.0,
            "evaluation_feedback": "",
            "evaluation_issues": [],
            "score_breakdown": None,
            
            # Rewrite tracking
            "rewrite_count": 0,
            "rewrite_history": [],
            "target_agent": None,
            
            # Workflow state
            "current_step": "start",
            "error": None,
        }

        # Execute workflow - should handle gracefully
        result = await enhanced_webtoon_workflow.ainvoke(initial_state)

        # Workflow should complete but may have error or low quality
        assert result is not None
        print(f"\n✅ Workflow handled edge case")
        print(f"   - Error: {result.get('error')}")
        print(f"   - Score: {result.get('evaluation_score', 0):.2f}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
