"""
Pydantic models for search functionality.
"""
from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime


class SearchRequest(BaseModel):
    """Request model for Reddit search."""
    time_range: Literal["1h", "1d", "10d", "100d"]
    subreddits: List[str] = Field(min_length=1, max_length=10)
    post_count: int = Field(ge=1, le=100, default=20)


class ViralPost(BaseModel):
    """Public representation of a viral Reddit post."""
    id: str
    title: str
    subreddit: str
    url: str
    upvotes: int
    comments: int
    viral_score: float
    created_at: datetime
    author: str


class SearchCriteria(BaseModel):
    """Search criteria used for a search request."""
    time_range: Literal["1h", "1d", "10d", "100d"]
    subreddits: List[str]
    post_count: int


class SearchResponse(BaseModel):
    """Response model for Reddit search."""
    posts: List[ViralPost]
    total_found: int
    search_criteria: SearchCriteria
    execution_time: float


class RedditPost(BaseModel):
    """Internal Reddit post representation."""
    id: str
    title: str
    subreddit: str
    permalink: str
    score: int
    num_comments: int
    created_utc: int
    author: str
    is_removed: bool = False
    is_deleted: bool = False
