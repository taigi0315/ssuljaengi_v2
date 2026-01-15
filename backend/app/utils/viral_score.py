"""
Viral score calculation for Reddit posts.

Ported from TypeScript implementation in viral-story-search/src/utils/viralScore.ts
"""
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.search import RedditPost


def calculate_viral_score(post: "RedditPost") -> float:
    """
    Calculate viral score for a Reddit post.
    
    Formula: (upvotes + comments * 2) / (hours_since_posted + 1)
    
    The score represents engagement velocity - how much engagement
    a post is getting relative to its age. Newer posts with high
    engagement get higher scores.
    
    Args:
        post: RedditPost object with score, num_comments, and created_utc
        
    Returns:
        Viral score rounded to 2 decimal places
    """
    upvotes = max(0, post.score)
    comments = post.num_comments
    
    # Calculate hours since posted
    current_time = time.time()
    hours_since_posted = (current_time - post.created_utc) / 3600
    
    # Base engagement score (comments weighted 2x)
    engagement_score = upvotes + (comments * 2)
    
    # Time decay factor (newer posts get higher scores)
    time_decay = max(1, hours_since_posted + 1)
    
    # Viral score with time weighting
    viral_score = engagement_score / time_decay
    
    return round(viral_score, 2)


def is_eligible_post(
    post: "RedditPost",
    min_upvotes: int = 10,
    min_comments: int = 5
) -> bool:
    """
    Check if a post meets the minimum criteria for inclusion.
    
    Args:
        post: RedditPost object to check
        min_upvotes: Minimum upvotes required (default: 10)
        min_comments: Minimum comments required (default: 5)
        
    Returns:
        True if post meets all criteria, False otherwise
    """
    # Early returns for faster rejection
    if post.is_removed or post.is_deleted:
        return False
    if post.score < min_upvotes:
        return False
    if post.num_comments < min_comments:
        return False
    if len(post.title) <= 10:
        return False
    
    return True
