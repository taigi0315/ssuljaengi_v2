"""
Search API router for Reddit post search functionality.

This module provides the POST /search endpoint that:
- Accepts search parameters (subreddits, time range, post count)
- Checks cache for existing results
- Fetches posts from Reddit via RedditService
- Calculates execution time
- Caches and returns results
- Handles errors with appropriate status codes
"""
import logging
import time
import hashlib
import json
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.models import (
    SearchRequest,
    SearchResponse,
    SearchCriteria,
    ErrorResponse,
    ErrorType,
)
from app.services.reddit import RedditService
from app.utils.cache import SearchCache
from app.utils.exceptions import APIException
from app.config import get_settings, Settings


logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize cache (singleton)
_cache: SearchCache = None


def get_cache() -> SearchCache:
    """
    Get or create the global cache instance.
    
    Returns:
        SearchCache instance
    """
    global _cache
    if _cache is None:
        settings = get_settings()
        _cache = SearchCache(
            maxsize=settings.cache_max_size,
            ttl=settings.cache_ttl
        )
        logger.info(
            f"Cache initialized: maxsize={settings.cache_max_size}, "
            f"ttl={settings.cache_ttl}s"
        )
    return _cache


def generate_cache_key(request: SearchRequest) -> str:
    """
    Generate a cache key from a search request.
    
    Creates a deterministic hash based on the search parameters
    to enable efficient cache lookups.
    
    Args:
        request: SearchRequest object
        
    Returns:
        Cache key string (hex digest of SHA256 hash)
    """
    # Sort subreddits for consistent hashing
    sorted_subreddits = sorted(request.subreddits)
    
    # Create a dictionary with sorted keys for consistent JSON serialization
    cache_data = {
        "subreddits": sorted_subreddits,
        "time_range": request.time_range,
        "post_count": request.post_count,
    }
    
    # Convert to JSON string with sorted keys
    cache_string = json.dumps(cache_data, sort_keys=True)
    
    # Generate SHA256 hash
    cache_key = hashlib.sha256(cache_string.encode()).hexdigest()
    
    logger.debug(f"Generated cache key: {cache_key} for request: {cache_string}")
    
    return cache_key


@router.post("/search", response_model=SearchResponse)
async def search_posts(
    request: SearchRequest,
    settings: Settings = Depends(get_settings)
) -> SearchResponse:
    """
    Search for viral Reddit posts across multiple subreddits.
    
    This endpoint:
    1. Validates the search request
    2. Checks the cache for existing results
    3. If not cached, fetches posts from Reddit API
    4. Calculates viral scores and sorts by score
    5. Caches the results
    6. Returns the search response
    
    Args:
        request: SearchRequest with subreddits, time_range, and post_count
        settings: Application settings (injected)
        
    Returns:
        SearchResponse with posts, total_found, search_criteria, and execution_time
        
    Raises:
        HTTPException: For validation errors, rate limits, timeouts, etc.
    """
    start_time = time.time()
    
    logger.info(
        f"Search request received: subreddits={request.subreddits}, "
        f"time_range={request.time_range}, post_count={request.post_count}"
    )
    
    # Generate cache key
    cache_key = generate_cache_key(request)
    cache = get_cache()
    
    # Check cache first
    cached_response = await cache.get(cache_key)
    if cached_response is not None:
        logger.info(f"Cache hit for key: {cache_key}")
        # Update execution time to reflect cache retrieval
        cached_response.execution_time = time.time() - start_time
        return cached_response
    
    logger.info(f"Cache miss for key: {cache_key}")
    
    # Fetch posts from Reddit
    try:
        async with RedditService(settings) as reddit_service:
            viral_posts = await reddit_service.fetch_multiple_subreddits(
                subreddits=request.subreddits,
                time_range=request.time_range,
                post_count=request.post_count
            )
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Build search criteria
        search_criteria = SearchCriteria(
            time_range=request.time_range,
            subreddits=request.subreddits,
            post_count=request.post_count,
        )
        
        # Build response
        response = SearchResponse(
            posts=viral_posts,
            total_found=len(viral_posts),
            search_criteria=search_criteria,
            execution_time=execution_time,
        )
        
        # Cache the response
        await cache.set(cache_key, response)
        logger.info(
            f"Search completed successfully: {len(viral_posts)} posts found "
            f"in {execution_time:.3f}s"
        )
        
        return response
        
    except APIException as e:
        # APIException is already handled by the global exception handler
        # Just re-raise it
        logger.error(f"API exception during search: {e.error_type} - {e.message}")
        raise
    
    except Exception as e:
        # Unexpected error - log and re-raise
        logger.error(f"Unexpected error during search: {type(e).__name__}: {str(e)}")
        raise

