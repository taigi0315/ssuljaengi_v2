"""
Enhanced Webtoon Script Rewriter service.

This module implements LLM-based rewriting of webtoon scripts based on
evaluation feedback with enhanced panel generation support. It takes an 
existing script and feedback, then generates an improved version that 
addresses identified issues while supporting:

- 20-50 panel range handling
- Three-act panel redistribution  
- Enhanced scene expansion capabilities
- Intelligent panel addition strategies

Enhanced for the expanded panel generation system.
"""

import logging
import json
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.services.llm_config import llm_config
from app.models.story import WebtoonScript
from app.services.webtoon_writer import WebtoonWriter


logger = logging.getLogger(__name__)


WEBTOON_REWRITER_PROMPT = """
**ROLE:** You are an Expert Webtoon Script Editor. Your task is to improve an existing webtoon script based on specific feedback.

**ORIGINAL SCRIPT:**
```json
{original_script}
```

**ISSUES TO FIX:**
{feedback}

**ORIGINAL STORY (for reference):**
{original_story}

**YOUR TASK:**
Rewrite the webtoon script to address ALL the issues listed above while maintaining:
1. The same characters (but you can add missing character definitions)
2. The same overall story arc and genre style
3. Proper panel count (aim for 20-40 panels for quality storytelling)

**KEY IMPROVEMENTS TO MAKE:**

1. **If "ADD MORE PANELS" is mentioned:**
   - Expand scenes into multi-panel sequences (2-6 panels per scene)
   - Add emotional reaction panels between dialogue
   - Break complex actions into step-by-step panels
   - Target 25-35 panels total for optimal pacing

2. **If "IMPROVE DIALOGUE" is mentioned:**
   - Add 2-5 lines of SPOKEN dialogue to silent scenes
   - Dialogue should reveal character personality and advance story
   - NO internal monologue or narration - only spoken words

3. **If "EXPAND visual_prompt" is mentioned:**
   - Rewrite short prompts to be 150-250 characters
   - Include: shot type, character placement, environment, lighting, atmosphere

4. **If "CHARACTER" issues are mentioned:**
   - Add missing character definitions to the characters array
   - Ensure all active_character_names match defined characters

**OUTPUT FORMAT:**
Return a complete, valid JSON object with this structure:
```json
{{
  "characters": [
    {{
      "name": "string",
      "reference_tag": "string", 
      "gender": "string",
      "age": "string",
      "face": "string",
      "hair": "string",
      "body": "string",
      "outfit": "string",
      "mood": "string",
      "visual_description": "string"
    }}
  ],
  "panels": [
    {{
      "panel_number": 1,
      "scene_type": "bridge",
      "shot_type": "string",
      "visual_prompt": "string (150+ characters)",
      "active_character_names": ["string"],
      "dialogue": [
        {{
          "character": "string",
          "text": "string (SPOKEN words only)",
          "order": 1
        }}
      ],
      "negative_prompt": "string",
      "composition_notes": "string",
      "environment_focus": "string",
      "environment_details": "string",
      "atmospheric_conditions": "string",
      "story_beat": "string",
      "character_placement_and_action": "string",
      "character_frame_percentage": 50,
      "environment_frame_percentage": 50,
      "style_variation": null
    }}
  ]
}}
```

**CRITICAL REQUIREMENTS:**
- Return ONLY valid JSON, no markdown formatting or extra text
- Include ALL required fields for each panel
- visual_prompt must be complete (150+ characters)
- dialogue must be SPOKEN words only (no internal monologue)
- panel_number must be sequential starting from 1
- Total panels should be 20-40 for optimal quality
- Ensure proper character consistency

{format_instructions}
"""


class WebtoonRewriter:
    """
    Enhanced Webtoon Script Rewriter for expanded panel support.
    
    Uses LLM to improve scripts based on evaluator feedback with support for:
    - 20-50 panel range handling
    - Three-act panel redistribution
    - Enhanced scene expansion capabilities
    - Intelligent panel addition strategies
    """
    
    def __init__(self):
        """Initialize the enhanced rewriter with LLM and parser."""
        self.llm = llm_config.get_model()
        self.parser = JsonOutputParser(pydantic_object=WebtoonScript)
        self.webtoon_writer = WebtoonWriter()  # For post-processing
    
    def _analyze_panel_distribution(self, script: WebtoonScript) -> dict:
        """
        Analyze current panel distribution across three acts.
        
        Args:
            script: WebtoonScript to analyze
            
        Returns:
            Dictionary with distribution analysis
        """
        total_panels = len(script.panels)
        if total_panels == 0:
            return {"total": 0, "act1": 0, "act2": 0, "act3": 0, "needs_redistribution": True}
        
        # Estimate current act distribution (simple thirds for now)
        act1_end = total_panels // 3
        act2_end = (total_panels * 2) // 3
        
        act1_panels = act1_end
        act2_panels = act2_end - act1_end
        act3_panels = total_panels - act2_end
        
        # Calculate ratios
        act1_ratio = act1_panels / total_panels
        act2_ratio = act2_panels / total_panels
        act3_ratio = act3_panels / total_panels
        
        # Check if redistribution is needed (target: 25%/50%/25%)
        needs_redistribution = (
            abs(act1_ratio - 0.25) > 0.1 or
            abs(act2_ratio - 0.50) > 0.1 or
            abs(act3_ratio - 0.25) > 0.1
        )
        
        return {
            "total": total_panels,
            "act1": act1_panels,
            "act2": act2_panels,
            "act3": act3_panels,
            "act1_ratio": act1_ratio,
            "act2_ratio": act2_ratio,
            "act3_ratio": act3_ratio,
            "needs_redistribution": needs_redistribution
        }
    
    def _calculate_target_panel_count(self, current_count: int, feedback: str) -> int:
        """
        Calculate target panel count based on current count and feedback.
        
        Args:
            current_count: Current number of panels
            feedback: Evaluator feedback
            
        Returns:
            Target panel count (20-50 range)
        """
        # Import here to avoid circular imports
        from app.config.enhanced_panel_config import get_enhanced_panel_config
        config = get_enhanced_panel_config()
        
        # If feedback mentions specific panel needs
        if "ADD" in feedback and "PANELS" in feedback:
            # Extract number if mentioned in feedback
            import re
            numbers = re.findall(r'ADD (\d+) MORE PANELS', feedback)
            if numbers:
                target = current_count + int(numbers[0])
                return min(max(target, config.panel_count_min), config.panel_count_max)
        
        # If current count is below minimum, target ideal minimum
        if current_count < config.panel_count_min:
            return config.panel_count_ideal_min
        
        # If current count is above maximum, target ideal maximum
        if current_count > config.panel_count_max:
            return config.panel_count_ideal_max
        
        # If in acceptable range but not ideal, move toward ideal
        if current_count < config.panel_count_ideal_min:
            return config.panel_count_ideal_min
        elif current_count > config.panel_count_ideal_max:
            return config.panel_count_ideal_max
        
        # Already in ideal range
        return current_count
    
    def _generate_panel_expansion_guidance(self, 
                                         current_count: int, 
                                         target_count: int,
                                         distribution: dict) -> str:
        """
        Generate specific guidance for panel expansion.
        
        Args:
            current_count: Current panel count
            target_count: Target panel count
            distribution: Current panel distribution analysis
            
        Returns:
            Detailed expansion guidance string
        """
        panels_to_add = target_count - current_count
        if panels_to_add <= 0:
            return ""
        
        # Calculate how many panels to add to each act for proper distribution
        target_act1 = max(1, round(target_count * 0.25))
        target_act2 = max(1, round(target_count * 0.50))
        target_act3 = max(1, target_count - target_act1 - target_act2)
        
        act1_to_add = max(0, target_act1 - distribution["act1"])
        act2_to_add = max(0, target_act2 - distribution["act2"])
        act3_to_add = max(0, target_act3 - distribution["act3"])
        
        guidance_parts = [
            f"EXPAND TO {target_count} PANELS (add {panels_to_add} panels):",
            f"- Act 1 (Setup): Add {act1_to_add} panels for character/world introduction",
            f"- Act 2 (Development): Add {act2_to_add} panels for conflict/tension building",
            f"- Act 3 (Resolution): Add {act3_to_add} panels for climax/resolution sequences"
        ]
        
        # Add specific expansion strategies
        if act1_to_add > 0:
            guidance_parts.append("  * Act 1 strategies: Character introduction panels, world-building, setup moments")
        if act2_to_add > 0:
            guidance_parts.append("  * Act 2 strategies: Conflict escalation, emotional development, tension sequences")
        if act3_to_add > 0:
            guidance_parts.append("  * Act 3 strategies: Climax build-up, resolution panels, conclusion moments")
        
        return "\n".join(guidance_parts)
    
    def _enhance_feedback_with_panel_guidance(self, 
                                            original_feedback: str, 
                                            script: WebtoonScript) -> str:
        """
        Enhance evaluator feedback with specific panel expansion guidance.
        
        Args:
            original_feedback: Original evaluator feedback
            script: Current WebtoonScript
            
        Returns:
            Enhanced feedback with panel expansion guidance
        """
        distribution = self._analyze_panel_distribution(script)
        current_count = distribution["total"]
        target_count = self._calculate_target_panel_count(current_count, original_feedback)
        
        enhanced_parts = [original_feedback]
        
        # Add panel count guidance if needed
        if current_count < 20:
            expansion_guidance = self._generate_panel_expansion_guidance(
                current_count, target_count, distribution
            )
            enhanced_parts.append(f"\nENHANCED PANEL GENERATION REQUIREMENTS:\n{expansion_guidance}")
        
        # Add three-act distribution guidance if needed
        if distribution["needs_redistribution"]:
            enhanced_parts.append(
                f"\nTHREE-ACT REDISTRIBUTION NEEDED:\n"
                f"Current: Act 1 ({distribution['act1_ratio']:.1%}), "
                f"Act 2 ({distribution['act2_ratio']:.1%}), "
                f"Act 3 ({distribution['act3_ratio']:.1%})\n"
                f"Target: Act 1 (25%), Act 2 (50%), Act 3 (25%)"
            )
        
        # Add scene expansion guidance
        if "EXPAND" in original_feedback or current_count < 25:
            enhanced_parts.append(
                "\nSCENE EXPANSION STRATEGIES:\n"
                "- Convert key emotional moments into 3-5 panel sequences\n"
                "- Break complex actions into step-by-step panels\n"
                "- Add reaction panels between dialogue exchanges\n"
                "- Include environmental panels for setting changes\n"
                "- Use 1-8 panels per scene based on narrative complexity"
            )
        
        return "\n".join(enhanced_parts)
    
    async def rewrite_script(
        self, 
        original_script: WebtoonScript, 
        feedback: str,
        original_story: str
    ) -> WebtoonScript:
        """
        Rewrite a webtoon script based on feedback with enhanced panel support.
        
        Args:
            original_script: The original WebtoonScript to improve
            feedback: Detailed feedback from evaluator
            original_story: The original story text for context
            
        Returns:
            Improved WebtoonScript with enhanced panel generation
            
        Raises:
            Exception: If rewriting fails
        """
        try:
            # Enhance feedback with panel expansion guidance
            enhanced_feedback = self._enhance_feedback_with_panel_guidance(
                feedback, original_script
            )
            
            logger.info(
                f"Enhanced rewriting webtoon script. Original panels: {len(original_script.panels)}. "
                f"Enhanced feedback length: {len(enhanced_feedback)} chars"
            )
            
            # Convert original script to JSON for the prompt
            original_script_json = json.dumps(
                {
                    "characters": [c.model_dump() for c in original_script.characters],
                    "panels": [p.model_dump() for p in original_script.panels]
                },
                indent=2
            )
            
            # Create enhanced prompt
            prompt = ChatPromptTemplate.from_template(
                WEBTOON_REWRITER_PROMPT + "\n\nReturn ONLY valid JSON, no markdown formatting."
            )
            
            # Build chain
            chain = prompt | self.llm | self.parser
            
            # Generate rewritten script with enhanced guidance
            result = await chain.ainvoke({
                "original_script": original_script_json,
                "feedback": enhanced_feedback,
                "original_story": original_story,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Fill in any missing fields using the existing logic from WebtoonWriter
            # If the LLM returns empty scenes/panels, regenerate a robust fallback from the original story.
            result = self.webtoon_writer._fill_missing_fields_in_dict(
                result,
                original_story=original_story,
            )
            
            # Convert to WebtoonScript
            rewritten_script = WebtoonScript(**result)
            
            # Validate enhanced panel requirements
            panel_count = len(rewritten_script.panels)
            from app.config.enhanced_panel_config import get_enhanced_panel_config
            config = get_enhanced_panel_config()
            
            if not config.validate_panel_count(panel_count):
                logger.warning(
                    f"Rewritten script panel count ({panel_count}) outside enhanced range "
                    f"({config.panel_count_min}-{config.panel_count_max})"
                )
            
            logger.info(
                f"Enhanced rewritten script: {panel_count} panels, "
                f"{len(rewritten_script.characters)} characters. "
                f"Target range: {config.panel_count_min}-{config.panel_count_max}"
            )
            
            return rewritten_script
            
        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"Enhanced webtoon script rewrite failed: {str(e)}", exc_info=True)
            
            # Check if this is a content blocking issue
            if "prohibited_content" in error_msg or "blocked" in error_msg or "safety" in error_msg:
                logger.warning("Rewrite blocked by safety filters, returning original script")
            else:
                logger.warning("Rewrite failed due to technical error, returning original script")
            
            # If rewriting fails, return the original script with a warning
            # This prevents the entire workflow from failing
            logger.warning("Returning original script due to rewrite failure")
            return original_script
    
    def analyze_script_for_enhancement(self, script: WebtoonScript) -> dict:
        """
        Analyze a script to identify enhancement opportunities.
        
        Args:
            script: WebtoonScript to analyze
            
        Returns:
            Dictionary with enhancement analysis
        """
        distribution = self._analyze_panel_distribution(script)
        current_count = distribution["total"]
        
        from app.config.enhanced_panel_config import get_enhanced_panel_config
        config = get_enhanced_panel_config()
        
        analysis = {
            "current_panel_count": current_count,
            "target_panel_count": self._calculate_target_panel_count(current_count, ""),
            "panel_distribution": distribution,
            "enhancement_needed": current_count < config.panel_count_min,
            "redistribution_needed": distribution["needs_redistribution"],
            "recommendations": []
        }
        
        # Generate recommendations
        if current_count < config.panel_count_min:
            analysis["recommendations"].append(
                f"Increase panel count from {current_count} to at least {config.panel_count_min}"
            )
        
        if distribution["needs_redistribution"]:
            analysis["recommendations"].append("Rebalance panels across three-act structure")
        
        if current_count < config.panel_count_ideal_min:
            analysis["recommendations"].append(
                f"Target {config.panel_count_ideal_min}-{config.panel_count_ideal_max} panels for optimal quality"
            )
        
        return analysis


# Global rewriter instance
webtoon_rewriter = WebtoonRewriter()
