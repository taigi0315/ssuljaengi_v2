"""
Story Rewriter node for LangGraph workflow.

This module implements the Rewriter node that improves stories based on
evaluator feedback.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.llm_config import llm_config
from app.prompt.story_rewriter import REWRITER_PROMPT


class StoryRewriter:
    """
    Story Rewriter node for improving stories.
    
    Uses LangChain with Gemini to rewrite stories based on evaluator feedback.
    """
    
    def __init__(self):
        """Initialize the story rewriter with LLM and prompt template."""
        self.llm = llm_config.get_model()
        self.prompt = ChatPromptTemplate.from_template(REWRITER_PROMPT)
        
        # Create LangChain chain
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    async def rewrite_story(self, story: str, feedback: str) -> str:
        """
        Rewrite story based on evaluator feedback.
        
        Args:
            story: The original story text
            feedback: Feedback from the evaluator
            
        Returns:
            Rewritten story text
            
        Raises:
            Exception: If rewriting fails
        """
        try:
            rewritten = await self.chain.ainvoke({
                "story": story,
                "feedback": feedback
            })
            return rewritten
        except Exception as e:
            raise Exception(f"Story rewriting failed: {str(e)}")


# Global story rewriter instance
story_rewriter = StoryRewriter()
