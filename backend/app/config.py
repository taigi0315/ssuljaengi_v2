"""
Configuration management for the FastAPI backend.

This module provides a Settings class that loads configuration from environment
variables with sensible defaults. It validates required fields on startup to
ensure the application is properly configured.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables or a .env file.
    Required fields (Reddit API credentials) will cause startup failure if missing.
    """
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host address")
    port: int = Field(default=8000, description="Server port", ge=1, le=65535)
    debug: bool = Field(default=False, description="Debug mode flag")
    
    # CORS Configuration
    frontend_url: str = Field(
        default="http://localhost:3000",
        description="Frontend URL for CORS configuration"
    )
    
    # Reddit API Configuration (Required)
    reddit_client_id: str = Field(
        ...,
        description="Reddit API client ID (required)",
        min_length=1
    )
    reddit_client_secret: str = Field(
        ...,
        description="Reddit API client secret (required)",
        min_length=1
    )
    reddit_user_agent: str = Field(
        default="viral-story-search/1.0",
        description="Reddit API user agent string"
    )
    
    # Cache Configuration
    cache_ttl: int = Field(
        default=300,
        description="Cache time-to-live in seconds",
        ge=0
    )
    cache_max_size: int = Field(
        default=100,
        description="Maximum number of cache entries",
        ge=1
    )
    
    # Google Gemini Configuration
    google_api_key: str = Field(
        ...,
        description="Google API key for Gemini (required)",
        min_length=1
    )
    gemini_model: str = Field(
        default="gemini-2.0-flash-exp",
        description="Gemini model name"
    )
    model_image_gen: str = Field(
        default="gemini-2.5-flash-image",
        description="Gemini model for image generation"
    )
    gemini_temperature: float = Field(
        default=0.7,
        description="Temperature for story generation",
        ge=0.0,
        le=2.0
    )
    gemini_max_tokens: int = Field(
        default=2000,
        description="Maximum tokens for story generation",
        ge=100
    )
    
    # Story Generation Configuration
    story_evaluation_threshold: float = Field(
        default=7.0,
        description="Minimum score to accept story without rewrite",
        ge=0.0,
        le=10.0
    )
    story_max_rewrites: int = Field(
        default=1,
        description="Maximum number of story rewrites",
        ge=0,
        le=3
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator("reddit_client_id", "reddit_client_secret", "google_api_key")
    @classmethod
    def validate_required_fields(cls, v: str, info) -> str:
        """
        Validate that required Reddit API credentials are not placeholder values.
        
        Args:
            v: The field value
            info: Field validation info
            
        Returns:
            The validated field value
            
        Raises:
            ValueError: If the field contains a placeholder value
        """
        if not v or v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        
        # Check for common placeholder values
        placeholder_values = [
            "your_reddit_client_id_here",
            "your_reddit_client_secret_here",
            "your_google_api_key_here",
            "changeme",
            "placeholder"
        ]
        
        if v.lower() in placeholder_values:
            raise ValueError(
                f"{info.field_name} contains a placeholder value. "
                f"Please set a valid Reddit API credential."
            )
        
        return v
    
    @field_validator("frontend_url")
    @classmethod
    def validate_frontend_url(cls, v: str) -> str:
        """
        Validate that the frontend URL is properly formatted.
        
        Args:
            v: The frontend URL
            
        Returns:
            The validated URL (with trailing slash removed)
            
        Raises:
            ValueError: If the URL is invalid
        """
        if not v:
            raise ValueError("frontend_url cannot be empty")
        
        # Remove trailing slash for consistency
        v = v.rstrip("/")
        
        # Basic URL validation
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError(
                "frontend_url must start with http:// or https://"
            )
        
        return v
    
    def get_reddit_auth(self) -> tuple[str, str]:
        """
        Get Reddit API authentication credentials as a tuple.
        
        Returns:
            Tuple of (client_id, client_secret)
        """
        return (self.reddit_client_id, self.reddit_client_secret)
    
    def is_development(self) -> bool:
        """
        Check if the application is running in development mode.
        
        Returns:
            True if debug mode is enabled
        """
        return self.debug


# Global settings instance
# This will be initialized lazily to allow importing the module without
# requiring environment variables to be set (useful for testing)
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    This function lazily initializes the settings on first access.
    It will raise validation errors if required fields are missing.
    
    Returns:
        The global Settings instance
        
    Raises:
        ValidationError: If required configuration is missing or invalid
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# For backward compatibility, provide a settings variable
# Note: This will raise an error if environment variables are not set
try:
    settings = get_settings()
except Exception:
    # Allow import to succeed even if settings are not configured
    # This is useful for testing and development
    settings = None  # type: ignore
