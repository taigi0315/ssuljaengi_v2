"""
Webtoon Script Evaluator service.

This module implements programmatic evaluation of webtoon scripts against
quality criteria: scene count, dialogue coverage, visual prompt completeness,
story structure, shot variety, and visual dynamism.

v2.0.0 Updates:
- Added shot_variety scoring (penalizes >50% same shot type)
- Added visual_dynamism scoring (checks frame percentage variance)
- Updated evaluation weights to include new metrics
- Added detailed feedback for variety issues
"""

import logging
import statistics
from collections import Counter
from pydantic import BaseModel
from typing import List, Dict, Tuple, Optional
from app.models.story import WebtoonScript, ShotType
from app.config import get_settings
from app.config.enhanced_panel_config import get_enhanced_panel_config
from app.services.panel_composer import group_panels_into_pages, calculate_page_statistics, Page


logger = logging.getLogger(__name__)


# Evaluation weights (v2.0.0)
# Rebalanced to include shot variety and visual dynamism
# v2.0.0 Phase 3.4: Added page_grouping for multi-panel support
EVALUATION_WEIGHTS = {
    "scene_count": 0.15,           # Reduced for multi-panel (15-25 panels target)
    "dialogue_coverage": 0.20,     # Dialogue is key for webtoons
    "visual_prompt": 0.15,         # Prompt quality matters
    "character_consistency": 0.10, # Basic requirement
    "story_structure": 0.05,       # Basic structure check
    "shot_variety": 0.20,          # Critical for visual interest
    "visual_dynamism": 0.10,       # Prevents static compositions
    "page_grouping": 0.05,         # NEW v2.0.0: Multi-panel page efficiency
}

# Panel count targets for enhanced panel generation system
# Updated for 20-50 panel range with ideal 25-40
PANEL_COUNT_TARGET = {
    "min": 20,   # Minimum panels for a complete story (enhanced)
    "ideal_min": 25,  # Ideal range start (enhanced)
    "ideal_max": 40,  # Ideal range end (enhanced)
    "max": 50,   # Maximum before it's too long (enhanced)
}

# Page count targets (panels grouped into multi-panel pages)
PAGE_COUNT_TARGET = {
    "min": 4,    # Minimum pages
    "ideal_min": 5,   # Ideal range start
    "ideal_max": 8,   # Ideal range end
    "max": 10,   # Maximum pages
}


class WebtoonEvaluation(BaseModel):
    """Result of webtoon script evaluation."""
    score: float  # 0-10 scale
    is_valid: bool
    issues: List[str]
    feedback: str  # Detailed feedback for rewriter
    score_breakdown: Optional[Dict[str, float]] = None  # v2.0.0: detailed scores


class WebtoonEvaluator:
    """
    Evaluator for webtoon scripts.

    Uses programmatic checks (not LLM) to validate scripts against
    quality criteria. This is faster and more deterministic than LLM-based evaluation.

    v2.0.0: Added shot variety and visual dynamism scoring.
    """

    # Standard shot type mappings for variety checking
    SHOT_TYPE_CATEGORIES = {
        # Close shots
        "extreme close-up": "close",
        "extreme close up": "close",
        "close-up": "close",
        "close up": "close",
        "closeup": "close",
        "extreme_close_up": "close",
        "close_up": "close",
        # Medium shots
        "medium close-up": "medium",
        "medium close up": "medium",
        "medium shot": "medium",
        "medium": "medium",
        "medium_close_up": "medium",
        "medium_wide": "medium",
        # Wide shots
        "wide shot": "wide",
        "wide": "wide",
        "extreme wide": "wide",
        "extreme_wide": "wide",
        "establishing shot": "wide",
        "establishing": "wide",
        # Special shots
        "detail": "detail",
        "detail shot": "detail",
        "over shoulder": "other",
        "over_shoulder": "other",
        "pov": "other",
        "bird's eye": "other",
        "birds_eye": "other",
        "worm's eye": "other",
        "worms_eye": "other",
        "dutch angle": "other",
        "dutch_angle": "other",
        "low angle": "other",
        "low_angle": "other",
        "high angle": "other",
        "high_angle": "other",
    }

    def _normalize_shot_type(self, shot_type: str) -> str:
        """Normalize shot type string to category."""
        if not shot_type:
            return "unknown"
        normalized = shot_type.lower().strip()
        return self.SHOT_TYPE_CATEGORIES.get(normalized, "other")

    def score_shot_variety(
        self,
        script: WebtoonScript
    ) -> Tuple[float, List[str], List[str]]:
        """
        Score the variety of shot types in the script.

        Criteria:
        - Penalize if >50% of shots are the same category
        - Bonus for having close-ups (emotional moments)
        - Bonus for having detail shots (visual interest)
        - Penalize for consecutive same-type shots

        Args:
            script: WebtoonScript to evaluate

        Returns:
            Tuple of (score 0-10, issues list, feedback list)
        """
        panels = script.panels
        if not panels:
            return 0.0, ["No panels to evaluate"], ["Add panels to the script"]

        issues = []
        feedback = []

        # Normalize all shot types
        shot_categories = [
            self._normalize_shot_type(p.shot_type)
            for p in panels
        ]
        total = len(shot_categories)

        # Count category distribution
        category_counts = Counter(shot_categories)

        # Check for dominance (>50% same category)
        most_common_category, most_common_count = category_counts.most_common(1)[0]
        dominance_ratio = most_common_count / total

        base_score = 10.0

        if dominance_ratio > 0.5:
            # Penalize for lack of variety
            penalty = (dominance_ratio - 0.5) * 10  # Max 5 point penalty
            base_score -= penalty
            issues.append(
                f"Shot variety low: {most_common_count}/{total} ({dominance_ratio*100:.0f}%) "
                f"are {most_common_category} shots"
            )
            feedback.append(
                f"ADD SHOT VARIETY: Too many {most_common_category} shots. "
                f"Mix in more {'close-ups and detail shots' if most_common_category == 'wide' else 'wide and establishing shots'}."
            )

        # Check for close-ups (important for emotions)
        close_count = category_counts.get("close", 0)
        close_ratio = close_count / total

        if close_ratio < 0.15 and total >= 5:
            base_score -= 1.0
            issues.append(f"Low close-up ratio ({close_ratio*100:.0f}%)")
            feedback.append(
                "ADD CLOSE-UPS: Include close-up shots for emotional moments, "
                "reactions, and key dialogue."
            )
        elif close_ratio >= 0.20:
            base_score += 0.5  # Bonus for good close-up usage

        # Check for detail shots (visual interest)
        detail_count = category_counts.get("detail", 0)
        detail_ratio = detail_count / total

        if detail_ratio < 0.05 and total >= 8:
            # Soft penalty for missing detail shots
            issues.append("No detail shots for visual interest")
            feedback.append(
                "CONSIDER DETAIL SHOTS: Add shots of hands, objects, or symbolic "
                "elements to add visual interest and break up medium shots."
            )
        elif detail_ratio >= 0.10:
            base_score += 0.5  # Bonus for detail shots

        # Check for consecutive same-type shots
        consecutive_violations = 0
        for i in range(2, len(shot_categories)):
            if (shot_categories[i] == shot_categories[i-1] == shot_categories[i-2]
                and shot_categories[i] != "unknown"):
                consecutive_violations += 1

        if consecutive_violations > 0:
            base_score -= min(2.0, consecutive_violations * 0.5)
            issues.append(f"{consecutive_violations} consecutive same-type shot violations")
            feedback.append(
                "VARY CONSECUTIVE SHOTS: Avoid 3+ consecutive shots of the same type. "
                "Alternate between shot types for visual rhythm."
            )

        # Check for minimum variety (at least 3 categories used)
        unique_categories = len([c for c in category_counts if c != "unknown"])
        if unique_categories < 3 and total >= 6:
            base_score -= 1.0
            issues.append(f"Only {unique_categories} shot categories used")
            feedback.append(
                "INCREASE SHOT DIVERSITY: Use at least 3 different shot types "
                "(close, medium, wide, or detail)."
            )

        final_score = max(0.0, min(10.0, base_score))
        return final_score, issues, feedback

    def score_visual_dynamism(
        self,
        script: WebtoonScript
    ) -> Tuple[float, List[str], List[str]]:
        """
        Score the visual dynamism based on frame percentages and composition.

        Criteria:
        - Check variance in character_frame_percentage
        - Penalize if all shots have similar framing
        - Bonus for range of frame percentages (mix of close and wide)

        Args:
            script: WebtoonScript to evaluate

        Returns:
            Tuple of (score 0-10, issues list, feedback list)
        """
        panels = script.panels
        if not panels:
            return 0.0, ["No panels to evaluate"], ["Add panels to the script"]

        issues = []
        feedback = []

        # Get frame percentages
        frame_percentages = [
            p.character_frame_percentage
            for p in panels
            if hasattr(p, 'character_frame_percentage') and p.character_frame_percentage is not None
        ]

        if len(frame_percentages) < 3:
            # Not enough data, give neutral score
            return 5.0, [], []

        base_score = 10.0

        # Calculate variance
        try:
            variance = statistics.variance(frame_percentages)
            mean_pct = statistics.mean(frame_percentages)
            min_pct = min(frame_percentages)
            max_pct = max(frame_percentages)
            range_pct = max_pct - min_pct
        except statistics.StatisticsError:
            return 5.0, [], []

        # Check variance (ideal: 200-600 for good mix)
        if variance < 100:
            # Too uniform - all shots similar framing
            base_score -= 3.0
            issues.append(
                f"Uniform framing: variance={variance:.0f}, "
                f"all shots around {mean_pct:.0f}% frame"
            )
            feedback.append(
                "VARY FRAME COMPOSITION: All shots have similar framing. "
                "Mix close-ups (70-90% frame) with wide shots (10-30% frame) "
                "for visual dynamism."
            )
        elif variance > 800:
            # Possibly too chaotic, mild penalty
            base_score -= 0.5
            issues.append(f"Highly variable framing (variance={variance:.0f})")

        # Check range (ideal: at least 40% range)
        if range_pct < 30:
            base_score -= 2.0
            issues.append(f"Narrow frame range: {min_pct}%-{max_pct}%")
            feedback.append(
                f"EXPAND FRAME RANGE: Current range is {min_pct}%-{max_pct}%. "
                "Include both tight close-ups (80%+) and wide shots (20% or less)."
            )
        elif range_pct >= 50:
            base_score += 1.0  # Bonus for good range

        # Check for extreme values (should have some)
        has_close = any(p >= 70 for p in frame_percentages)
        has_wide = any(p <= 30 for p in frame_percentages)

        if not has_close:
            base_score -= 1.0
            issues.append("No close framing (70%+ character in frame)")
            feedback.append(
                "ADD CLOSE FRAMING: Include shots where characters fill 70%+ "
                "of the frame for emotional impact."
            )

        if not has_wide:
            base_score -= 1.0
            issues.append("No wide framing (30% or less character in frame)")
            feedback.append(
                "ADD WIDE FRAMING: Include establishing or context shots where "
                "characters are 30% or less of the frame."
            )

        final_score = max(0.0, min(10.0, base_score))
        return final_score, issues, feedback

    def score_page_grouping(
        self,
        script: WebtoonScript
    ) -> Tuple[float, List[str], List[str]]:
        """
        Score how well panels group into multi-panel pages.

        v2.0.0 Phase 3.4: Added for multi-panel system evaluation.

        Criteria:
        - Check if page count is in ideal range (5-8)
        - Check ratio of single vs multi-panel pages
        - Bonus for having key moments as single panels
        - Bonus for efficient grouping (3-4 panels per multi-panel page average)

        Args:
            script: WebtoonScript to evaluate

        Returns:
            Tuple of (score 0-10, issues list, feedback list)
        """
        panels = script.panels
        if not panels or len(panels) < 2:
            return 5.0, [], []  # Neutral score for very short scripts

        issues = []
        feedback = []

        # Group panels into pages
        pages = group_panels_into_pages(panels)
        stats = calculate_page_statistics(pages)

        base_score = 10.0

        # Check page count
        total_pages = stats["total_pages"]
        min_pages = PAGE_COUNT_TARGET["min"]
        max_pages = PAGE_COUNT_TARGET["max"]
        ideal_min = PAGE_COUNT_TARGET["ideal_min"]
        ideal_max = PAGE_COUNT_TARGET["ideal_max"]

        if total_pages < min_pages:
            base_score -= 3.0
            issues.append(f"Only {total_pages} pages. Need at least {min_pages}.")
            feedback.append(
                f"ADD MORE CONTENT: Script groups into only {total_pages} pages. "
                f"Target is {ideal_min}-{ideal_max} pages for good pacing."
            )
        elif total_pages > max_pages:
            base_score -= 2.0
            issues.append(f"Too many pages: {total_pages}. Ideal max is {ideal_max}.")
            feedback.append(
                f"CONDENSE CONTENT: Script groups into {total_pages} pages. "
                f"Consider combining some panels for {ideal_max} pages max."
            )
        elif ideal_min <= total_pages <= ideal_max:
            base_score += 1.0  # Bonus for ideal range

        # Check single vs multi-panel ratio
        single_pages = stats["single_panel_pages"]
        multi_pages = stats["multi_panel_pages"]

        if total_pages > 0:
            single_ratio = single_pages / total_pages

            # Too many single panels = inefficient
            if single_ratio > 0.5:
                base_score -= 2.0
                issues.append(f"Too many single-panel pages ({single_pages}/{total_pages})")
                feedback.append(
                    "IMPROVE GROUPING: Too many single-panel pages. "
                    "Only key emotional moments should be single panels. "
                    "Group action/dialogue into 3-4 panel pages."
                )
            elif single_ratio < 0.1 and len(panels) > 8:
                # No single panels but script is long enough to have key moments
                issues.append("No single-panel pages for key moments")
                feedback.append(
                    "ADD KEY MOMENTS: Consider making emotional peaks into "
                    "single full-page panels for impact."
                )

        # Check average panels per multi-panel page
        if multi_pages > 0:
            multi_panel_total = stats["total_panels"] - single_pages
            avg_per_page = multi_panel_total / multi_pages

            if avg_per_page < 2.5:
                base_score -= 1.0
                issues.append(f"Low panel density per page ({avg_per_page:.1f})")
            elif avg_per_page > 4.5:
                base_score -= 0.5
                issues.append(f"High panel density ({avg_per_page:.1f} per page)")
            elif 3.0 <= avg_per_page <= 4.0:
                base_score += 0.5  # Bonus for ideal density

        # Calculate API efficiency (panels / pages)
        if total_pages > 0:
            efficiency = len(panels) / total_pages
            if efficiency < 2.0:
                feedback.append(
                    f"API EFFICIENCY: {len(panels)} panels / {total_pages} pages = "
                    f"{efficiency:.1f} panels/page. Target 3-4 for cost efficiency."
                )

        final_score = max(0.0, min(10.0, base_score))
        return final_score, issues, feedback

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
            "shot_variety": 0.0,      # v2.0.0
            "visual_dynamism": 0.0,   # v2.0.0
            "page_grouping": 0.0,     # v2.0.0 Phase 3.4
        }

        panels = script.panels
        characters = script.characters

        # ===== 1. Scene/Panel Count Evaluation (Weight: 15%) =====
        # Enhanced panel generation system: Updated targets for 20-50 panel range
        enhanced_config = get_enhanced_panel_config()
        num_panels = len(panels)
        min_panels = enhanced_config.panel_count_min
        max_panels = enhanced_config.panel_count_max
        ideal_min = enhanced_config.panel_count_ideal_min
        ideal_max = enhanced_config.panel_count_ideal_max

        if num_panels < min_panels:
            # Be more strict about insufficient panels - force rewrite
            scores["scene_count"] = max(0, (num_panels / min_panels) * 6)  # Max 6 points for insufficient panels
            issues.append(f"Only {num_panels} panels. Need {min_panels}-{max_panels}.")
            feedback_parts.append(
                f"ADD {min_panels - num_panels} MORE PANELS. "
                f"Current: {num_panels}, Required: {ideal_min}-{ideal_max}. "
                "Enhanced panel generation needs sufficient content for rich storytelling."
            )
        elif num_panels > max_panels:
            scores["scene_count"] = max(0, 10 - ((num_panels - max_panels) * 0.5))
            issues.append(f"Too many panels: {num_panels}. Ideal is {ideal_max}.")
            feedback_parts.append(f"REDUCE panels to {ideal_max}. Combine similar beats.")
        elif ideal_min <= num_panels <= ideal_max:
            scores["scene_count"] = 10.0  # Perfect range
        else:
            # Between min and ideal_min, or ideal_max and max
            scores["scene_count"] = 8.0  # Acceptable but not ideal
        
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
        
        # ===== 5. Story Structure (Weight: 5%) =====
        # Basic structure check - do we have enough scenes for a story?
        if num_panels >= 8:
            scores["story_structure"] = 10.0
        else:
            scores["story_structure"] = (num_panels / 8) * 10
            if num_panels < 6:
                issues.append(f"Story may be too short: only {num_panels} panels")
                feedback_parts.append(
                    "ADD MORE PANELS: A good webtoon needs 8-12 panels "
                    "for proper story development."
                )

        # ===== 6. Shot Variety (Weight: 20%) - v2.0.0 =====
        variety_score, variety_issues, variety_feedback = self.score_shot_variety(script)
        scores["shot_variety"] = variety_score
        issues.extend(variety_issues)
        feedback_parts.extend(variety_feedback)

        # ===== 7. Visual Dynamism (Weight: 10%) - v2.0.0 =====
        dynamism_score, dynamism_issues, dynamism_feedback = self.score_visual_dynamism(script)
        scores["visual_dynamism"] = dynamism_score
        issues.extend(dynamism_issues)
        feedback_parts.extend(dynamism_feedback)

        # ===== 8. Page Grouping (Weight: 5%) - v2.0.0 Phase 3.4 =====
        page_score, page_issues, page_feedback = self.score_page_grouping(script)
        scores["page_grouping"] = page_score
        issues.extend(page_issues)
        feedback_parts.extend(page_feedback)

        # ===== Calculate Final Score =====
        # v2.0.0 weights from EVALUATION_WEIGHTS constant
        final_score = sum(
            scores[metric] * weight
            for metric, weight in EVALUATION_WEIGHTS.items()
        )
        
        is_valid = final_score >= settings.webtoon_evaluation_threshold

        # Build feedback string for rewriter
        feedback = ""
        if feedback_parts:
            feedback = "ISSUES TO FIX:\n" + "\n".join(f"- {fb}" for fb in feedback_parts)
        else:
            feedback = "Script meets all quality criteria."

        # Round scores for output
        score_breakdown = {k: round(v, 2) for k, v in scores.items()}

        logger.info(
            f"Webtoon evaluation: score={final_score:.2f}, valid={is_valid}, "
            f"panels={num_panels}, dialogue_ratio={dialogue_ratio:.2f}, "
            f"shot_variety={scores['shot_variety']:.2f}, dynamism={scores['visual_dynamism']:.2f}"
        )

        return WebtoonEvaluation(
            score=round(final_score, 2),
            is_valid=is_valid,
            issues=issues,
            feedback=feedback,
            score_breakdown=score_breakdown
        )


# Global evaluator instance
webtoon_evaluator = WebtoonEvaluator()
