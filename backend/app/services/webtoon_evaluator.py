"""
Webtoon Script Evaluator service.

This module implements programmatic evaluation of webtoon scripts against
quality criteria: scene count, dialogue coverage, visual prompt completeness,
and story structure.
"""

import logging
from pydantic import BaseModel
from typing import List
from app.models.story import WebtoonScript
from app.config import get_settings


logger = logging.getLogger(__name__)


class WebtoonEvaluation(BaseModel):
    """Result of webtoon script evaluation."""
    score: float  # 0-10 scale
    is_valid: bool
    issues: List[str]
    feedback: str  # Detailed feedback for rewriter


class WebtoonEvaluator:
    """
    Evaluator for webtoon scripts.
    
    Uses programmatic checks (not LLM) to validate scripts against
    quality criteria. This is faster and more deterministic than LLM-based evaluation.
    """
    
    def evaluate_script(self, script: WebtoonScript) -> WebtoonEvaluation:
        """
        Evaluate a webtoon script against quality criteria.
        
        Args:
            script: WebtoonScript to evaluate
            
        Returns:
            WebtoonEvaluation with score, validity, issues, and feedback
        """
        settings = get_settings()
        issues = []
        feedback_parts = []
        
        # Initialize scores (each out of 10)
        scores = {
            "scene_count": 0.0,
            "dialogue_coverage": 0.0,
            "visual_prompt": 0.0,
            "character_consistency": 0.0,
            "story_structure": 0.0,
        }
        
        panels = script.panels
        characters = script.characters
        
        # ===== 1. Scene Count Evaluation (Weight: 30%) =====
        num_panels = len(panels)
        min_scenes = settings.webtoon_min_scenes
        max_scenes = 12
        
        if num_panels < min_scenes:
            scores["scene_count"] = max(0, (num_panels / min_scenes) * 10)
            issues.append(f"Only {num_panels} scenes. Need {min_scenes}-{max_scenes}.")
            feedback_parts.append(
                f"ADD {min_scenes - num_panels} MORE SCENES. "
                f"Current: {num_panels}, Required: {min_scenes}-{max_scenes}. "
                "Add development and resolution scenes."
            )
        elif num_panels > max_scenes:
            scores["scene_count"] = max(0, 10 - ((num_panels - max_scenes) * 2))
            issues.append(f"Too many scenes: {num_panels}. Max is {max_scenes}.")
            feedback_parts.append(f"REDUCE scenes to {max_scenes}. Combine similar beats.")
        else:
            scores["scene_count"] = 10.0
        
        # ===== 2. Dialogue Coverage Evaluation (Weight: 25%) =====
        panels_with_dialogue = sum(
            1 for p in panels 
            if p.dialogue and len(p.dialogue) > 0
        )
        dialogue_ratio = panels_with_dialogue / num_panels if num_panels > 0 else 0
        required_coverage = settings.webtoon_dialogue_coverage
        
        if dialogue_ratio < required_coverage:
            scores["dialogue_coverage"] = (dialogue_ratio / required_coverage) * 10
            issues.append(
                f"Only {panels_with_dialogue}/{num_panels} scenes have dialogue "
                f"({dialogue_ratio*100:.0f}%). Need {required_coverage*100:.0f}%+."
            )
            # Identify which panels need dialogue
            silent_panels = [p.panel_number for p in panels if not p.dialogue or len(p.dialogue) == 0]
            feedback_parts.append(
                f"ADD DIALOGUE to panels: {silent_panels[:5]}. "
                "Every scene should have character interaction."
            )
        else:
            scores["dialogue_coverage"] = 10.0
        
        # ===== 3. Visual Prompt Completeness (Weight: 20%) =====
        min_prompt_length = 150
        short_prompts = []
        
        for p in panels:
            prompt_len = len(p.visual_prompt) if p.visual_prompt else 0
            if prompt_len < min_prompt_length:
                short_prompts.append((p.panel_number, prompt_len))
        
        if short_prompts:
            good_prompt_ratio = (num_panels - len(short_prompts)) / num_panels if num_panels > 0 else 0
            scores["visual_prompt"] = good_prompt_ratio * 10
            issues.append(
                f"{len(short_prompts)} panels have incomplete visual prompts."
            )
            feedback_parts.append(
                f"EXPAND visual_prompt for panels {[p[0] for p in short_prompts[:3]]}. "
                f"Each prompt should be 150-250 characters with: "
                "shot_type, composition, environment details, character placement, "
                "lighting, atmosphere, style."
            )
        else:
            scores["visual_prompt"] = 10.0
        
        # ===== 4. Character Consistency (Weight: 15%) =====
        # Check if characters mentioned in panels exist in character list
        character_names = {c.name for c in characters}
        unknown_characters = set()
        
        for p in panels:
            for char_name in (p.active_character_names or []):
                if char_name not in character_names:
                    unknown_characters.add(char_name)
        
        if unknown_characters:
            consistency_score = max(0, 10 - len(unknown_characters) * 2)
            scores["character_consistency"] = consistency_score
            issues.append(
                f"Characters in scenes not defined: {list(unknown_characters)[:3]}"
            )
            feedback_parts.append(
                f"ADD character definitions for: {list(unknown_characters)}. "
                "Or use existing character names consistently."
            )
        else:
            scores["character_consistency"] = 10.0
        
        # ===== 5. Story Structure (Weight: 10%) =====
        # Check for proper 3-act structure:
        # Act 1 (Setup): ~25% of scenes
        # Act 2 (Development): ~50% of scenes
        # Act 3 (Resolution): ~25% of scenes
        
        if num_panels >= 8:
            # Check for variety in shot types
            shot_types = [p.shot_type for p in panels if p.shot_type]
            unique_shots = set(shot_types)
            
            if len(unique_shots) < 3:
                scores["story_structure"] = 5.0
                issues.append("Limited shot variety. Use more diverse shot types.")
                feedback_parts.append(
                    "ADD SHOT VARIETY: Mix Wide Shots, Medium Shots, Close-Ups, "
                    "and Extreme Close-Ups throughout the story."
                )
            else:
                scores["story_structure"] = 10.0
        else:
            scores["story_structure"] = (num_panels / 8) * 10
        
        # ===== Calculate Final Score =====
        # Weights: scene_count=30%, dialogue=25%, prompt=20%, character=15%, structure=10%
        final_score = (
            scores["scene_count"] * 0.30 +
            scores["dialogue_coverage"] * 0.25 +
            scores["visual_prompt"] * 0.20 +
            scores["character_consistency"] * 0.15 +
            scores["story_structure"] * 0.10
        )
        
        is_valid = final_score >= settings.webtoon_evaluation_threshold
        
        # Build feedback string for rewriter
        feedback = ""
        if feedback_parts:
            feedback = "ISSUES TO FIX:\n" + "\n".join(f"- {fb}" for fb in feedback_parts)
        else:
            feedback = "Script meets all quality criteria."
        
        logger.info(
            f"Webtoon evaluation: score={final_score:.2f}, valid={is_valid}, "
            f"panels={num_panels}, dialogue_ratio={dialogue_ratio:.2f}"
        )
        
        return WebtoonEvaluation(
            score=round(final_score, 2),
            is_valid=is_valid,
            issues=issues,
            feedback=feedback
        )


# Global evaluator instance
webtoon_evaluator = WebtoonEvaluator()
