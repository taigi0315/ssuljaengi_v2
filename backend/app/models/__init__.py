"""
Pydantic models for the application.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class ErrorType(str, Enum):
    """Enumeration of error types."""
    REDDIT_API_ERROR = "reddit_api_error"
    RATE_LIMIT = "rate_limit"
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"


class ErrorResponse(BaseModel):
    """Standard error response model."""
    type: ErrorType
    message: str
    retryable: bool
    retry_after: Optional[int] = None


# Export models for easy imports
from .search import (
    SearchRequest,
    ViralPost,
    SearchCriteria,
    SearchResponse,
    RedditPost,
)

__all__ = [
    "ErrorType",
    "ErrorResponse",
    "SearchRequest",
    "ViralPost",
    "SearchCriteria",
    "SearchResponse",
    "RedditPost",
]
