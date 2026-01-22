"""
Cinematographer service for planning shot sequences.

This module implements the Cinematographer agent that analyzes story scenes
and plans an optimal shot sequence with visual variety and emotional alignment.
"""

import logging
import json
from typing import List, Optional
from collections import Counter
from langchain_core.output_parsers import JsonOutputParser
from app.services.llm_config import llm_config
from app.prompt.cinematographer import get_cinematographer_prompt
from app.models.story import (
    Shot,
    ShotPlan,
    ShotType,
    CameraAngle,
    WebtoonScript,
    WebtoonPanel,
    Character
)


logger = logging.getLogger(__name__)


class CinematographerService:
    """
    Cinematographer service for planning shot sequences.

    Analyzes story scenes and generates a ShotPlan with optimal
    shot types, angles, and emotional alignment.
    """

    def __init__(self):
        """Initialize the cinematographer with LLM."""
        self.llm = llm_config.get_model()

    async def plan_shots(
        self,
        script: WebtoonScript,
        genre: str,
        target_shot_count: Optional[int] = None
    ) -> ShotPlan:
        """
        Plan the shot sequence for a webtoon script.

        Args:
            script: WebtoonScript with panels and characters
            genre: Story genre for style guidance
            target_shot_count: Target number of shots (default: 2x panel count)

        Returns:
            ShotPlan with ordered shots and variety score
        """
        # Default target: ~2 shots per panel for variety
        if target_shot_count is None:
            target_shot_count = max(15, len(script.panels) * 2)

        # Format scenes for the prompt
        scenes_text = self._format_scenes(script.panels)
        characters_text = self._format_characters(script.characters)

        # Get the prompt
        prompt = get_cinematographer_prompt(
            scenes=scenes_text,
            characters=characters_text,
            genre=genre,
            target_shot_count=target_shot_count
        )

        try:
            # Call LLM
            response = await self.llm.ainvoke(prompt)

            # Parse response
            response_text = response.content if hasattr(response, 'content') else str(response)

            # Extract JSON from response
            shot_plan_dict = self._parse_json_response(response_text)

            # Convert to ShotPlan
            shot_plan = self._dict_to_shot_plan(shot_plan_dict)

            # Validate and fix variety rules
            shot_plan = self._enforce_variety_rules(shot_plan)

            # Calculate variety score
            shot_plan.calculate_variety_score()

            logger.info(
                f"Cinematographer planned {len(shot_plan.shots)} shots "
                f"with variety score {shot_plan.variety_score:.2f}"
            )

            return shot_plan

        except Exception as e:
            logger.error(f"Error in cinematographer: {e}")
            # Return a basic shot plan as fallback
            return self._generate_fallback_shot_plan(script, target_shot_count)

    def _format_scenes(self, panels: List[WebtoonPanel]) -> str:
        """Format panels as scene descriptions for the prompt."""
        scenes = []
        for p in panels:
            scene_text = f"Scene {p.panel_number}:\n"
            scene_text += f"  Story beat: {p.story_beat or 'Not specified'}\n"
            scene_text += f"  Characters: {', '.join(p.active_character_names) if p.active_character_names else 'None'}\n"
            scene_text += f"  Environment: {p.environment_focus or 'Not specified'}\n"
            scene_text += f"  Current shot type: {p.shot_type}\n"
            if p.dialogue:
                dialogue_preview = p.dialogue[0].get('text', '')[:50] if p.dialogue else ''
                scene_text += f"  Dialogue preview: \"{dialogue_preview}...\"\n"
            scenes.append(scene_text)
        return "\n".join(scenes)

    def _format_characters(self, characters: List[Character]) -> str:
        """Format characters for the prompt."""
        chars = []
        for c in characters:
            char_text = f"- {c.name}: {c.gender}, {c.age}"
            if c.mood:
                char_text += f", {c.mood}"
            chars.append(char_text)
        return "\n".join(chars) if chars else "No characters defined"

    def _parse_json_response(self, response_text: str) -> dict:
        """Extract and parse JSON from LLM response."""
        # Try to find JSON in the response
        text = response_text.strip()

        # Remove markdown code blocks if present
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
            # Try to extract just the object
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            raise

    def _dict_to_shot_plan(self, data: dict) -> ShotPlan:
        """Convert parsed dict to ShotPlan model."""
        shots = []

        for shot_dict in data.get("shots", []):
            try:
                # Map string values to enums
                shot_type_str = shot_dict.get("shot_type", "medium")
                angle_str = shot_dict.get("angle", "eye_level")

                # Handle enum conversion
                try:
                    shot_type = ShotType(shot_type_str)
                except ValueError:
                    shot_type = ShotType.MEDIUM

                try:
                    angle = CameraAngle(angle_str)
                except ValueError:
                    angle = CameraAngle.EYE_LEVEL

                shot = Shot(
                    shot_id=shot_dict.get("shot_id", f"shot_{len(shots)+1}"),
                    shot_type=shot_type,
                    subject=shot_dict.get("subject", "scene"),
                    subject_characters=shot_dict.get("subject_characters", []),
                    frame_percentage=shot_dict.get("frame_percentage", 50),
                    angle=angle,
                    emotional_purpose=shot_dict.get("emotional_purpose", ""),
                    emotional_intensity=shot_dict.get("emotional_intensity", 5),
                    belongs_to_scene=shot_dict.get("belongs_to_scene", 1),
                    story_beat=shot_dict.get("story_beat", "")
                )
                shots.append(shot)
            except Exception as e:
                logger.warning(f"Failed to parse shot: {e}")
                continue

        return ShotPlan(
            shots=shots,
            total_scenes=data.get("total_scenes", max(s.belongs_to_scene for s in shots) if shots else 1)
        )

    def _enforce_variety_rules(self, shot_plan: ShotPlan) -> ShotPlan:
        """
        Enforce shot variety rules and fix violations.

        Rules:
        1. No more than 2 consecutive shots of the same type
        2. Emotional peaks (intensity 7+) need close-ups
        3. Ensure at least some variety exists
        """
        if not shot_plan.shots:
            return shot_plan

        shots = shot_plan.shots.copy()
        modified = False

        # Rule 1: No more than 2 consecutive same types
        for i in range(2, len(shots)):
            if (shots[i].shot_type == shots[i-1].shot_type == shots[i-2].shot_type):
                # Change the current shot to something different
                current_type = shots[i].shot_type
                alternative = self._get_alternative_shot_type(current_type, shots[i].emotional_intensity)
                shots[i] = Shot(
                    **{**shots[i].model_dump(), "shot_type": alternative}
                )
                modified = True
                logger.debug(f"Fixed consecutive shot types at index {i}")

        # Rule 2: Emotional peaks need close-ups
        for i, shot in enumerate(shots):
            if shot.emotional_intensity >= 7:
                if shot.shot_type not in [ShotType.CLOSE_UP, ShotType.EXTREME_CLOSE_UP, ShotType.DETAIL]:
                    shots[i] = Shot(
                        **{**shot.model_dump(), "shot_type": ShotType.CLOSE_UP}
                    )
                    modified = True
                    logger.debug(f"Changed shot {i} to close_up for emotional intensity {shot.emotional_intensity}")

        if modified:
            shot_plan.shots = shots

        return shot_plan

    def _get_alternative_shot_type(self, current: ShotType, intensity: int) -> ShotType:
        """Get an alternative shot type based on intensity."""
        if intensity >= 7:
            return ShotType.CLOSE_UP
        elif intensity >= 5:
            alternatives = [ShotType.MEDIUM, ShotType.MEDIUM_CLOSE_UP, ShotType.OVER_SHOULDER]
        else:
            alternatives = [ShotType.WIDE, ShotType.MEDIUM_WIDE, ShotType.MEDIUM]

        # Return first alternative that's different from current
        for alt in alternatives:
            if alt != current:
                return alt
        return ShotType.MEDIUM

    def _generate_fallback_shot_plan(self, script: WebtoonScript, target_count: int) -> ShotPlan:
        """Generate a basic shot plan as fallback if LLM fails."""
        shots = []
        shot_types_cycle = [
            ShotType.WIDE,
            ShotType.MEDIUM,
            ShotType.CLOSE_UP,
            ShotType.MEDIUM,
            ShotType.DETAIL
        ]

        shot_num = 0
        for panel in script.panels:
            # Generate 2-3 shots per panel
            shots_for_panel = min(3, max(2, target_count // len(script.panels)))

            for i in range(shots_for_panel):
                shot_type = shot_types_cycle[shot_num % len(shot_types_cycle)]
                frame_min, frame_max = ShotType.get_frame_percentage_range(shot_type)

                shot = Shot(
                    shot_id=f"scene_{panel.panel_number}_shot_{i+1}",
                    shot_type=shot_type,
                    subject=f"scene_{panel.panel_number}_moment_{i+1}",
                    subject_characters=panel.active_character_names or [],
                    frame_percentage=(frame_min + frame_max) // 2,
                    angle=CameraAngle.EYE_LEVEL,
                    emotional_purpose="capture_moment",
                    emotional_intensity=panel.emotional_intensity if hasattr(panel, 'emotional_intensity') else 5,
                    belongs_to_scene=panel.panel_number,
                    story_beat=panel.story_beat or ""
                )
                shots.append(shot)
                shot_num += 1

        plan = ShotPlan(
            shots=shots,
            total_scenes=len(script.panels)
        )
        plan.calculate_variety_score()

        return plan

    def score_variety(self, shot_plan: ShotPlan) -> dict:
        """
        Calculate detailed variety metrics for a shot plan.

        Returns:
            Dict with variety score and breakdown
        """
        if not shot_plan.shots:
            return {
                "overall_score": 0.0,
                "type_distribution": {},
                "consecutive_violations": 0,
                "close_up_ratio": 0.0,
                "detail_shot_ratio": 0.0,
                "issues": ["No shots in plan"]
            }

        shots = shot_plan.shots
        total = len(shots)

        # Type distribution
        type_counts = Counter(s.shot_type for s in shots)
        type_distribution = {st.value: count for st, count in type_counts.items()}

        # Check consecutive violations
        consecutive_violations = 0
        for i in range(2, len(shots)):
            if shots[i].shot_type == shots[i-1].shot_type == shots[i-2].shot_type:
                consecutive_violations += 1

        # Calculate ratios
        close_up_count = sum(
            1 for s in shots
            if s.shot_type in [ShotType.CLOSE_UP, ShotType.EXTREME_CLOSE_UP]
        )
        detail_count = sum(1 for s in shots if s.shot_type == ShotType.DETAIL)

        close_up_ratio = close_up_count / total
        detail_ratio = detail_count / total

        # Calculate overall score
        issues = []

        # Penalize for same type dominance
        max_type_ratio = max(type_counts.values()) / total
        if max_type_ratio > 0.5:
            issues.append(f"Too many {max(type_counts, key=type_counts.get).value} shots ({max_type_ratio*100:.0f}%)")

        # Penalize for consecutive violations
        if consecutive_violations > 0:
            issues.append(f"{consecutive_violations} consecutive same-type violations")

        # Check for missing close-ups
        if close_up_ratio < 0.15:
            issues.append(f"Low close-up ratio ({close_up_ratio*100:.0f}%). Add more close-ups for emotional moments.")

        # Check for missing detail shots
        if detail_ratio < 0.05 and total >= 10:
            issues.append("Consider adding detail shots for visual interest")

        # Calculate score (0-1)
        base_score = 1.0 - max(0, (max_type_ratio - 0.3) * 1.5)
        penalty = consecutive_violations * 0.1
        bonus = (0.1 if close_up_ratio >= 0.15 else 0) + (0.05 if detail_ratio >= 0.05 else 0)

        overall_score = max(0.0, min(1.0, base_score - penalty + bonus))

        return {
            "overall_score": round(overall_score, 3),
            "type_distribution": type_distribution,
            "consecutive_violations": consecutive_violations,
            "close_up_ratio": round(close_up_ratio, 3),
            "detail_shot_ratio": round(detail_ratio, 3),
            "issues": issues
        }


# Global service instance
cinematographer_service = CinematographerService()
