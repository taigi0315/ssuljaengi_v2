"""
FastAPI application entry point.

This module creates and configures the FastAPI application with:
- CORS middleware for frontend communication
- Request/response logging
- Exception handlers for custom exceptions
- Health check endpoint
- API routers
"""
import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.config import get_settings
from app.models import ErrorResponse, ErrorType
from app.utils.exceptions import (
    APIException,
    LLMException,
    StoryGenerationException,
    WorkflowException
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the application.
    """
    # Startup
    settings = get_settings()
    logger.info("Starting FastAPI application")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Frontend URL: {settings.frontend_url}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    settings = get_settings()
    
    # Create FastAPI app
    app = FastAPI(
        title="Viral Story Search API",
        version="1.0.0",
        description="Backend API for viral Reddit story search and generation",
        lifespan=lifespan,
    )
    
    # Configure CORS
    setup_cors(app, settings)
    
    # Add middleware
    setup_middleware(app)
    
    # Add exception handlers
    setup_exception_handlers(app)
    
    # Add routes
    setup_routes(app)
    
    return app


def setup_cors(app: FastAPI, settings: Any) -> None:
    """
    Configure CORS middleware for frontend communication.
    
    Args:
        app: FastAPI application instance
        settings: Application settings
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    logger.info(f"CORS configured for origin: {settings.frontend_url}")


def setup_middleware(app: FastAPI) -> None:
    """
    Configure application middleware.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """
        Log all incoming requests and responses.
        
        Logs request method, path, and execution time.
        """
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"Incoming request: {request.method} {request.url.path}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Time: {execution_time:.3f}s"
        )
        
        return response


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Configure exception handlers for the application.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """
        Handle custom API exceptions.
        
        Args:
            request: The incoming request
            exc: The APIException that was raised
            
        Returns:
            JSON response with error details
        """
        logger.error(
            f"API Exception: {exc.error_type} - {exc.message} "
            f"(retryable: {exc.retryable})"
        )
        
        # Determine HTTP status code based on error type
        status_code_map = {
            ErrorType.VALIDATION_ERROR: status.HTTP_400_BAD_REQUEST,
            ErrorType.RATE_LIMIT: status.HTTP_429_TOO_MANY_REQUESTS,
            ErrorType.TIMEOUT_ERROR: status.HTTP_408_REQUEST_TIMEOUT,
            ErrorType.REDDIT_API_ERROR: status.HTTP_502_BAD_GATEWAY,
            ErrorType.NETWORK_ERROR: status.HTTP_503_SERVICE_UNAVAILABLE,
        }
        
        status_code = status_code_map.get(
            exc.error_type,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        error_response = ErrorResponse(
            type=exc.error_type,
            message=exc.message,
            retryable=exc.retryable,
            retry_after=exc.retry_after,
        )
        
        return JSONResponse(
            status_code=status_code,
            content={"error": error_response.model_dump()},
        )
    
    @app.exception_handler(LLMException)
    async def llm_exception_handler(request: Request, exc: LLMException):
        """
        Handle LLM service exceptions.
        
        Args:
            request: The incoming request
            exc: The LLMException that was raised
            
        Returns:
            JSON response with error details
        """
        logger.error(f"LLM Exception: {exc.message}")
        
        error_response = ErrorResponse(
            type=exc.error_type,
            message=exc.message,
            retryable=exc.retryable,
            retry_after=exc.retry_after,
        )
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"error": error_response.model_dump()},
        )
    
    @app.exception_handler(StoryGenerationException)
    async def story_generation_exception_handler(request: Request, exc: StoryGenerationException):
        """
        Handle story generation exceptions.
        
        Args:
            request: The incoming request
            exc: The StoryGenerationException that was raised
            
        Returns:
            JSON response with error details
        """
        logger.error(f"Story Generation Exception: {exc.message}")
        
        error_response = ErrorResponse(
            type=exc.error_type,
            message=exc.message,
            retryable=exc.retryable,
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": error_response.model_dump()},
        )
    
    @app.exception_handler(WorkflowException)
    async def workflow_exception_handler(request: Request, exc: WorkflowException):
        """
        Handle workflow execution exceptions.
        
        Args:
            request: The incoming request
            exc: The WorkflowException that was raised
            
        Returns:
            JSON response with error details
        """
        logger.error(f"Workflow Exception: {exc.message}")
        
        error_response = ErrorResponse(
            type=exc.error_type,
            message=exc.message,
            retryable=exc.retryable,
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": error_response.model_dump()},
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):
        """
        Handle Pydantic validation errors.
        
        Args:
            request: The incoming request
            exc: The validation error
            
        Returns:
            JSON response with validation error details
        """
        logger.error(f"Validation error: {exc.errors()}")
        
        # Format validation errors
        error_messages = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_messages.append(f"{field}: {message}")
        
        error_response = ErrorResponse(
            type=ErrorType.VALIDATION_ERROR,
            message=f"Validation error: {'; '.join(error_messages)}",
            retryable=False,
        )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": error_response.model_dump()},
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request,
        exc: ValidationError
    ):
        """
        Handle Pydantic validation errors (non-request).
        
        Args:
            request: The incoming request
            exc: The validation error
            
        Returns:
            JSON response with validation error details
        """
        logger.error(f"Pydantic validation error: {exc.errors()}")
        
        error_response = ErrorResponse(
            type=ErrorType.VALIDATION_ERROR,
            message=f"Validation error: {str(exc)}",
            retryable=False,
        )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": error_response.model_dump()},
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Handle unexpected exceptions.
        
        Args:
            request: The incoming request
            exc: The exception that was raised
            
        Returns:
            JSON response with generic error message
        """
        logger.error(
            f"Unexpected error: {type(exc).__name__}: {str(exc)}",
            exc_info=True
        )
        
        error_response = ErrorResponse(
            type=ErrorType.NETWORK_ERROR,
            message="An unexpected error occurred. Please try again later.",
            retryable=True,
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": error_response.model_dump()},
        )


def setup_routes(app: FastAPI) -> None:
    """
    Configure application routes.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint.
        
        Returns:
            Status indicating the service is healthy
        """
        return {"status": "healthy"}
    
    # Import and register routers
    from app.routers import search, story
    app.include_router(search.router, tags=["Search"])
    app.include_router(story.router, tags=["Story"])
    
    logger.info("Routes configured")


# Create the application instance
app = create_app()
