import logging
import json
from langchain_core.output_parsers import JsonOutputParser
from app.services.llm_config import llm_config
from app.prompt.shorts_script import SHORTS_SCRIPT_PROMPT
from app.models.shorts import ShortsScript

logger = logging.getLogger(__name__)

class ShortsGenerator:
    def __init__(self):
        self.llm = llm_config.get_model()
        self.parser = JsonOutputParser(pydantic_object=ShortsScript)
    
    async def generate_script(self, topic: str = "random") -> ShortsScript:
        """
        Generate a shorts script based on the topic.
        If topic is empty or 'random', the LLM will pick a topic.
        """
        try:
            logger.info(f"Generating shorts script for topic: {topic}")
            
            # Use the defined prompt template
            # The prompt already contains strict JSON schema instructions
            chain = SHORTS_SCRIPT_PROMPT | self.llm | self.parser
            
            result = await chain.ainvoke({"topic": topic})
            
            # Validate with Pydantic
            script = ShortsScript(**result)
            
            return script
            
        except Exception as e:
            logger.error(f"Shorts script generation failed: {str(e)}", exc_info=True)
            raise Exception(f"Shorts script generation failed: {str(e)}")

# Global instance
shorts_generator = ShortsGenerator()
