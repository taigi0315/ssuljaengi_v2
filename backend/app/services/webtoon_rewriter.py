"""
Webtoon Script Rewriter service.

This module implements LLM-based rewriting of webtoon scripts based on
evaluation feedback. It takes an existing script and feedback, then
generates an improved version that addresses the identified issues.
"""

import logging
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.services.llm_config import llm_config
from app.models.story import WebtoonScript
from app.services.webtoon_writer import WebtoonWriter


logger = logging.getLogger(__name__)


WEBTOON_REWRITER_PROMPT = """
**ROLE:** You are a Webtoon Script Editor. Your task is to IMPROVE an existing webtoon script based on specific feedback.

**ORIGINAL SCRIPT:**
```json
{original_script}
```

**ISSUES TO FIX:**
{feedback}

**ORIGINAL STORY (for reference):**
{original_story}

---

**YOUR TASK:**

Rewrite the webtoon script to address ALL the issues listed above while maintaining:
1. The same characters (but you can add missing character definitions)
2. The same overall story arc
3. The same genre style and tone

**SPECIFIC FIXES TO MAKE:**

1. **If "ADD MORE SCENES" is mentioned:**
   - Create NEW scenes that expand the story (8-12 total)
   - Add development scenes between existing ones
   - Ensure proper 3-act structure: Setup (25%), Development (50%), Resolution (25%)

2. **If "ADD DIALOGUE" is mentioned:**
   - Add 2-5 lines of dialogue to silent scenes
   - Dialogue should reveal character personality
   - Use dialogue to advance the story, not just fill space

3. **If "EXPAND visual_prompt" is mentioned:**
   - Rewrite short prompts to be 150-250 characters
   - Follow the formula: shot_type, vertical 9:16, composition, environment (40%), 
     character placement (30%), lighting/atmosphere (20%), style (10%)

4. **If "CHARACTER" issues are mentioned:**
   - Add missing character definitions to the characters array
   - Ensure all active_character_names match defined characters

**OUTPUT FORMAT:**

Return a complete, valid JSON object with this structure:
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
  "panels": [...]       // Include ALL panels, both original and rewritten
}}

**CRITICAL:**
- Return ONLY valid JSON, no markdown formatting
- Include ALL required fields for each panel
- visual_prompt must be complete (150+ characters)
- dialogue must be an array of objects with "character", "text", "order" fields
- panel_number must be sequential starting from 1

{format_instructions}
"""


class WebtoonRewriter:
    """
    Rewriter for webtoon scripts.
    
    Uses LLM to improve scripts based on evaluator feedback.
    """
    
    def __init__(self):
        """Initialize the rewriter with LLM and parser."""
        self.llm = llm_config.get_model()
        self.parser = JsonOutputParser(pydantic_object=WebtoonScript)
        self.webtoon_writer = WebtoonWriter()  # For post-processing
    
    async def rewrite_script(
        self, 
        original_script: WebtoonScript, 
        feedback: str,
        original_story: str
    ) -> WebtoonScript:
        """
        Rewrite a webtoon script based on feedback.
        
        Args:
            original_script: The original WebtoonScript to improve
            feedback: Detailed feedback from evaluator
            original_story: The original story text for context
            
        Returns:
            Improved WebtoonScript
            
        Raises:
            Exception: If rewriting fails
        """
        try:
            logger.info(
                f"Rewriting webtoon script. Original panels: {len(original_script.panels)}. "
                f"Feedback: {feedback[:100]}..."
            )
            
            # Convert original script to JSON for the prompt
            original_script_json = json.dumps(
                {
                    "characters": [c.model_dump() for c in original_script.characters],
                    "panels": [p.model_dump() for p in original_script.panels]
                },
                indent=2
            )
            
            # Create prompt
            prompt = ChatPromptTemplate.from_template(
                WEBTOON_REWRITER_PROMPT + "\n\nReturn ONLY valid JSON, no markdown formatting."
            )
            
            # Build chain
            chain = prompt | self.llm | self.parser
            
            # Generate rewritten script
            result = await chain.ainvoke({
                "original_script": original_script_json,
                "feedback": feedback,
                "original_story": original_story,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Fill in any missing fields using the existing logic from WebtoonWriter
            result = self.webtoon_writer._fill_missing_fields_in_dict(result)
            
            # Convert to WebtoonScript
            rewritten_script = WebtoonScript(**result)
            
            logger.info(
                f"Rewritten script has {len(rewritten_script.panels)} panels, "
                f"{len(rewritten_script.characters)} characters"
            )
            
            return rewritten_script
            
        except Exception as e:
            logger.error(f"Webtoon script rewrite failed: {str(e)}", exc_info=True)
            raise Exception(f"Webtoon script rewrite failed: {str(e)}")


# Global rewriter instance
webtoon_rewriter = WebtoonRewriter()
