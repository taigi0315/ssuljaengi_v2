"""
Story Evaluator node for LangGraph workflow.

This module implements the Evaluator node that assesses story quality
and provides feedback for potential improvements.
"""

from langchain.prompts import ChatPromptTemplate
from app.services.llm_config import llm_config
from app.models.story import EvaluationResult


class StoryEvaluator:
    """
    Story Evaluator node for assessing story quality.
    
    Uses LangChain with Gemini to evaluate stories and provide structured feedback.
    """
    
    def __init__(self):
        """Initialize the story evaluator with LLM and prompt template."""
        self.llm = llm_config.get_model()
        
        # Placeholder evaluation prompt - can be optimized later
        self.prompt = ChatPromptTemplate.from_template("""
Evaluate this story on a scale of 1-10 based on:
1. Coherence (does it make sense? logical flow?)
2. Engagement (is it interesting? emotionally compelling?)
3. Length (appropriate length? not too short or long?)

Story:
{story}

Provide your evaluation in this EXACT format (one value per line):
Score: [number 1-10]
Coherence: [number 1-10]
Engagement: [number 1-10]
Length Appropriate: [yes or no]
Feedback: [specific suggestions for improvement]
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
            response = await self.llm.ainvoke(
                self.prompt.format(story=story)
            )
            
            # Parse response
            content = response.content
            lines = content.strip().split('\n')
            
            # Extract values with error handling
            score = 7.0  # Default
            coherence = 7.0
            engagement = 7.0
            length_ok = True
            feedback = "Story evaluation completed."
            
            for line in lines:
                line = line.strip()
                if line.startswith("Score:"):
                    try:
                        score = float(line.split(':', 1)[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif line.startswith("Coherence:"):
                    try:
                        coherence = float(line.split(':', 1)[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif line.startswith("Engagement:"):
                    try:
                        engagement = float(line.split(':', 1)[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif line.startswith("Length Appropriate:"):
                    length_str = line.split(':', 1)[1].strip().lower()
                    length_ok = 'yes' in length_str
                elif line.startswith("Feedback:"):
                    feedback = line.split(':', 1)[1].strip()
            
            return EvaluationResult(
                score=score,
                feedback=feedback,
                coherence=coherence,
                engagement=engagement,
                length_appropriate=length_ok
            )
            
        except Exception as e:
            raise Exception(f"Story evaluation failed: {str(e)}")


# Global story evaluator instance
story_evaluator = StoryEvaluator()
