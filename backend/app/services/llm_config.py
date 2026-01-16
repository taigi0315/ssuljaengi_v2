"""
LLM Configuration for Gemini model.

This module provides configuration and initialization for the Google Gemini model
used in story generation. It handles API authentication and model parameter setup.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import get_settings


class LLMConfig:
    """
    Configuration manager for Gemini LLM.
    
    Handles initialization and configuration of the Google Gemini model
    with appropriate parameters for story generation.
    """
    
    def __init__(self):
        """Initialize LLM configuration from settings."""
        settings = get_settings()
        self.model_name = settings.gemini_model
        self.api_key = settings.google_api_key
        self.temperature = settings.gemini_temperature
        self.max_tokens = settings.gemini_max_tokens
    
    def get_model(self) -> ChatGoogleGenerativeAI:
        """
        Get configured Gemini model instance.
        
        Returns:
            Configured ChatGoogleGenerativeAI instance ready for use
            
        Raises:
            ValueError: If API key is not configured
        """
        if not self.api_key:
            raise ValueError(
                "Google API key not configured. "
                "Please set GOOGLE_API_KEY in your .env file."
            )
        
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )


# Global LLM config instance
llm_config = LLMConfig()
