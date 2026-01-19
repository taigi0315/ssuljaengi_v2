"""
Story Evaluator node for LangGraph workflow.

This module implements the Evaluator node that assesses story quality
and provides feedback for potential improvements.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.services.llm_config import llm_config
from app.models.story import EvaluationResult


class StoryEvaluator:
    """
    Story Evaluator node for assessing story quality.
    
    Uses LangChain with Gemini to evaluate stories and provide structured feedback.
    """
    
    def __init__(self):
        """Initialize the story evaluator with LLM and JSON output parser."""
        self.llm = llm_config.get_model()
        self.parser = JsonOutputParser(pydantic_object=EvaluationResult)
        
        # Evaluation prompt
        self.prompt = ChatPromptTemplate.from_template("""
Evaluate this story on a scale of 1-10 based on:
1. Coherence (does it make sense? logical flow?)
2. Engagement (is it interesting? emotionally compelling?)
3. Length (appropriate length? not too short or long?)

Story:
{story}

{format_instructions}

Return ONLY valid JSON, no markdown formatting.
""")
    
    async def evaluate_story(self, story: str) -> EvaluationResult:
        """
        Evaluate story and return score with feedback.
        
        Args:
            story: The story text to evaluate
            
        Returns:
            EvaluationResult with score, feedback, and sub-scores
            
        Raises:
            Exception: If evaluation fails
        """
        try:
            # Use JSON output parser chain
            chain = self.prompt | self.llm | self.parser
            
            result = await chain.ainvoke({
                "story": story,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Convert dict to EvaluationResult model
            evaluation = EvaluationResult(**result)
            
            return evaluation
            
        except Exception as e:
            raise Exception(f"Story evaluation failed: {str(e)}")


# Global story evaluator instance
story_evaluator = StoryEvaluator()
