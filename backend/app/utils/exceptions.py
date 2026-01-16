"""
Custom exception classes for the backend API.

These exceptions provide structured error handling with consistent
error types, messages, and retry information.
"""
from typing import Optional
from app.models import ErrorType


class APIException(Exception):
    """
    Base exception for all API errors.
    
    All custom exceptions should inherit from this class to ensure
    consistent error handling and response formatting.
    """
    
    def __init__(
        self,
        error_type: ErrorType,
        message: str,
        retryable: bool = False,
        retry_after: Optional[int] = None
    ):
        """
        Initialize the exception.
        
        Args:
            error_type: Type of error from ErrorType enum
            message: Human-readable error message
            retryable: Whether the operation can be retried
            retry_after: Seconds to wait before retrying (for rate limits)
        """
        super().__init__(message)
        self.error_type = error_type
        self.message = message
        self.retryable = retryable
        self.retry_after = retry_after


class ValidationException(APIException):
    """
    Raised for validation errors.
    
    Used when request parameters fail validation (invalid format,
    out of range, missing required fields, etc.)
    """
    
    def __init__(self, message: str):
        super().__init__(
            error_type=ErrorType.VALIDATION_ERROR,
            message=message,
            retryable=False
        )


class RateLimitException(APIException):
    """
    Raised when rate limit is exceeded.
    
    Used when too many requests are made to the API or when
    external services (Reddit, OpenAI) return rate limit errors.
    """
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(
            error_type=ErrorType.RATE_LIMIT,
            message=message,
            retryable=True,
            retry_after=retry_after
        )


class TimeoutException(APIException):
    """
    Raised for timeout errors.
    
    Used when requests to external services take too long to complete.
    """
    
    def __init__(self, message: str):
        super().__init__(
            error_type=ErrorType.TIMEOUT_ERROR,
            message=message,
            retryable=True
        )


class ExternalServiceException(APIException):
    """
    Raised for external service failures.
    
    Used when external APIs (Reddit, OpenAI, image generation services)
    return errors or are unavailable.
    """
    
    def __init__(
        self,
        message: str,
        retryable: bool = True,
        retry_after: Optional[int] = None
    ):
        super().__init__(
            error_type=ErrorType.REDDIT_API_ERROR,
            message=message,
            retryable=retryable,
            retry_after=retry_after
        )


class LLMException(APIException):
    """
    Raised for LLM service failures.
    
    Used when Gemini or other LLM services fail, timeout, or are unavailable.
    """
    
    def __init__(
        self,
        message: str,
        retryable: bool = True,
        retry_after: Optional[int] = None
    ):
        super().__init__(
            error_type=ErrorType.NETWORK_ERROR,
            message=f"LLM service error: {message}",
            retryable=retryable,
            retry_after=retry_after
        )


class StoryGenerationException(APIException):
    """
    Raised for story generation failures.
    
    Used when story generation workflow fails for any reason.
    """
    
    def __init__(self, message: str, retryable: bool = False):
        super().__init__(
            error_type=ErrorType.NETWORK_ERROR,
            message=f"Story generation failed: {message}",
            retryable=retryable
        )


class WorkflowException(APIException):
    """
    Raised for workflow execution failures.
    
    Used when LangGraph workflow encounters errors during execution.
    """
    
    def __init__(self, message: str, retryable: bool = False):
        super().__init__(
            error_type=ErrorType.NETWORK_ERROR,
            message=f"Workflow execution failed: {message}",
            retryable=retryable
        )
