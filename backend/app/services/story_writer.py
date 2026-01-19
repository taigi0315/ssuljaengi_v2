"""
Story Writer node for LangGraph workflow.

This module implements the Writer node that generates initial stories from Reddit posts
using the Gemini LLM through LangChain with mood-based style modifiers.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.llm_config import llm_config
from app.prompt.story_writer import STORY_WRITER_PROMPT
from app.prompt.story_mood import STORY_GENRE_PROMPTS


class RedditPost:
    """Simple data class for Reddit post information."""
    
    def __init__(self, id: str, title: str, content: str, mood: str = "modern_romance"):
        self.id = id
        self.title = title
        self.content = content
        self.mood = mood


class StoryWriter:
    """
    Story Writer node for generating initial stories.
    
    Uses LangChain with Gemini to transform Reddit posts into engaging stories
    with mood-specific style modifiers.
    """
    
    def __init__(self):
        """Initialize the story writer with LLM."""
        self.llm = llm_config.get_model()
    
    def _get_prompt_template(self, mood: str) -> ChatPromptTemplate:
        """
        Get mood-specific prompt template.
        
        Args:
            mood: Story mood/style identifier
            
        Returns:
            ChatPromptTemplate with mood modifier applied
        """
        # Get mood modifier (default to modern_romance if not found)
        mood_modifier = STORY_GENRE_PROMPTS.get(mood, STORY_GENRE_PROMPTS["MODERN_ROMANCE_DRAMA_MANHWA"])
        
        # Replace the {{user_select_genre}} placeholder with the mood modifier
        combined_prompt = STORY_WRITER_PROMPT.replace("{{user_select_genre}}", mood_modifier)
        
        return ChatPromptTemplate.from_template(combined_prompt)
    
    async def write_story(self, reddit_post: RedditPost) -> str:
        """
        Generate initial story from Reddit post with mood-specific styling.
        
        Args:
            reddit_post: Reddit post data to transform into a story
            
        Returns:
            Generated story text
            
        Raises:
            Exception: If story generation fails
        """
        try:
            prompt = self._get_prompt_template(reddit_post.mood)
            chain = prompt | self.llm | StrOutputParser()
            
            story = await chain.ainvoke({
                "title": reddit_post.title,
                "content": reddit_post.content or reddit_post.title
            })
            return story
        except Exception as e:
            raise Exception(f"Story generation failed: {str(e)}")


# Global story writer instance
story_writer = StoryWriter()
