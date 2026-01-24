
import asyncio
import logging
from app.utils.llm_logger import llm_logger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_logger():
    logger.info("--- Testing LLM Logger ---")
    
    # 1. Simulate Story Log
    await llm_logger.log_request(
        service_name="test_story",
        model_name="gemini-test",
        prompt="Write a story about a cat",
        output="Once upon a time there was a cat...",
        metadata={"id": "test_1"}
    )
    
    # 2. Simulate Image Log
    await llm_logger.log_request(
        service_name="test_image",
        model_name="imagen-test",
        prompt="A photo of a cat",
        output="<Base64>",
        metadata={"style": "realistic"}
    )
    
    logger.info("Logs written. Checking file...")
    
    # Check file exists and has content
    import os
    if os.path.exists(llm_logger.log_file):
        with open(llm_logger.log_file, 'r') as f:
            lines = f.readlines()
            logger.info(f"Log file found with {len(lines)} lines.")
            print("Last log entry:", lines[-1])
    else:
        logger.error("Log file NOT found!")

if __name__ == "__main__":
    asyncio.run(test_logger())
