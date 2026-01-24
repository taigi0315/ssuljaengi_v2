import logging
import json
import os
import aiofiles
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class LLMLogger:
    """
    Centralized logger for LLM inputs and outputs.
    Writes logs to a JSONL file for easy parsing and analysis.
    """
    
    def __init__(self, log_dir: str = "logs", filename: str = "llm_history.jsonl"):
        # adjustments for absolute path relative to backend root if needed, 
        # but defaulting to relative for now or using absolute if provided.
        # Assuming backend root is where main.py runs, usually backend/
        
        # Resolve path relative to this file's parent (app/utils -> app -> backend)
        base_dir = Path(__file__).parent.parent.parent
        self.log_dir = base_dir / log_dir
        self.log_file = self.log_dir / filename
        
        # Ensure log directory exists
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"LLM Logger initialized. Logging to: {self.log_file}")
        except Exception as e:
            logger.error(f"Failed to create log directory {self.log_dir}: {e}")

    async def log_request(
        self, 
        service_name: str, 
        model_name: str, 
        prompt: Any, 
        output: Any, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log an LLM request/response pair asynchronously.
        
        Args:
            service_name: Name of the service (e.g., 'story_writer', 'image_gen')
            model_name: Name of the model used (e.g., 'gemini-1.5-flash')
            prompt: The input prompt sent to the LLM (string or complex object)
            output: The output received from the LLM
            metadata: Additional context (e.g., request_id, parameters)
        """
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "service": service_name,
                "model": model_name,
                "metadata": metadata or {},
                "input": prompt,
                "output": output
            }
            
            # Use aiofiles for non-blocking I/O
            async with aiofiles.open(self.log_file, mode='a', encoding='utf-8') as f:
                await f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                
        except Exception as e:
            # Fallback to standard logging if file write fails, don't crash the app
            logger.error(f"Failed to log LLM request: {e}")

# Global instance
llm_logger = LLMLogger()
