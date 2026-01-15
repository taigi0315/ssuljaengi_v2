"""
Reddit service for fetching posts from subreddits.

This service handles Reddit API authentication, fetching posts,
transforming responses, and calculating viral scores.
"""
import httpx
import logging
from typing import List, Optional
from app.models.search import RedditPost, ViralPost
from app.utils.viral_score import calculate_viral_score
from app.utils.exceptions import (
    RateLimitException,
    TimeoutException,
    ExternalServiceException,
)
from app.config import Settings
import asyncio
from datetime import datetime


logger = logging.getLogger(__name__)


class RedditService:
    """
    Service for interacting with the Reddit API.
    
    Handles OAuth authentication, fetching posts from subreddits,
    and transforming Reddit API responses to internal models.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the Reddit service.
        
        Args:
            settings: Application settings containing Reddit API credentials
        """
        self.settings = settings
        self.base_url = "https://www.reddit.com"
        self.oauth_url = "https://oauth.reddit.com"
        self.timeout = 30.0  # 30 seconds
        self.access_token: Optional[str] = None
        self.client: Optional[httpx.AsyncClient] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_client()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_client()
        
    async def _initialize_client(self):
        """Initialize the HTTP client and authenticate with Reddit."""
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers={
                "User-Agent": self.settings.reddit_user_agent,
            }
        )
        await self._authenticate()
        
    async def _close_client(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
            
    async def _authenticate(self):
        """
        Authenticate with Reddit API using OAuth.
        
        Uses client credentials flow to obtain an access token.
        
        Raises:
            ExternalServiceException: If authentication fails
        """
        try:
            auth = (self.settings.reddit_client_id, self.settings.reddit_client_secret)
            
            response = await self.client.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=auth,
                data={"grant_type": "client_credentials"},
                headers={
                    "User-Agent": self.settings.reddit_user_agent,
                }
            )
            
            if response.status_code != 200:
                raise ExternalServiceException(
                    f"Reddit authentication failed: {response.status_code}",
                    retryable=False
                )
                
            data = response.json()
            self.access_token = data.get("access_token")
            
            if not self.access_token:
                raise ExternalServiceException(
                    "Reddit authentication failed: No access token received",
                    retryable=False
                )
                
            logger.info("Successfully authenticated with Reddit API")
            
        except httpx.TimeoutException as e:
            raise TimeoutException("Reddit authentication timed out")
        except httpx.HTTPError as e:
            raise ExternalServiceException(
                f"Reddit authentication failed: {str(e)}",
                retryable=True
            )

    
    def _convert_time_range(self, time_range: str) -> str:
        """
        Convert our time range format to Reddit API format.
        
        Args:
            time_range: Time range in our format (1h, 1d, 10d, 100d)
            
        Returns:
            Reddit API time range format (hour, day, week, all)
        """
        time_range_map = {
            "1h": "hour",
            "1d": "day",
            "10d": "week",  # Reddit doesn't have 10 days, use week
            "100d": "all",  # Use all time for 100 days
        }
        return time_range_map.get(time_range, "day")
    
    def _map_reddit_post(self, post_data: dict) -> RedditPost:
        """
        Map Reddit API post data to our RedditPost model.
        
        Args:
            post_data: Raw post data from Reddit API
            
        Returns:
            RedditPost model instance
        """
        return RedditPost(
            id=post_data.get("id", ""),
            title=post_data.get("title", ""),
            subreddit=post_data.get("subreddit", ""),
            permalink=post_data.get("permalink", ""),
            score=post_data.get("score", 0),
            num_comments=post_data.get("num_comments", 0),
            created_utc=int(post_data.get("created_utc", 0)),
            author=post_data.get("author", "[deleted]"),
            is_removed=post_data.get("removed_by_category") is not None,
            is_deleted=(
                post_data.get("author") == "[deleted]" or
                post_data.get("selftext") == "[deleted]"
            ),
        )
    
    def _handle_http_error(self, response: httpx.Response, subreddit: str):
        """
        Handle HTTP errors from Reddit API.
        
        Args:
            response: HTTP response object
            subreddit: Subreddit name for error messages
            
        Raises:
            RateLimitException: For 429 status codes
            ExternalServiceException: For other error status codes
        """
        status = response.status_code
        
        if status == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitException(
                "Too many requests to Reddit API. Please wait before searching again.",
                retry_after=retry_after
            )
        elif status == 403:
            raise ExternalServiceException(
                f"Access forbidden to r/{subreddit}. Subreddit may be private or restricted.",
                retryable=False
            )
        elif status == 404:
            raise ExternalServiceException(
                f"Subreddit r/{subreddit} not found.",
                retryable=False
            )
        elif status in (500, 502, 503, 504):
            raise ExternalServiceException(
                "Reddit service temporarily unavailable. Please try again.",
                retryable=True
            )
        else:
            raise ExternalServiceException(
                f"Reddit API error: {status} {response.reason_phrase}",
                retryable=False
            )
    
    async def fetch_posts(
        self,
        subreddit: str,
        time_range: str,
        limit: int
    ) -> List[RedditPost]:
        """
        Fetch posts from a specific subreddit.
        
        Args:
            subreddit: Subreddit name (without r/ prefix)
            time_range: Time range for posts (1h, 1d, 10d, 100d)
            limit: Maximum number of posts to fetch
            
        Returns:
            List of RedditPost objects
            
        Raises:
            RateLimitException: If rate limit is exceeded
            TimeoutException: If request times out
            ExternalServiceException: For other Reddit API errors
        """
        if not self.client or not self.access_token:
            raise ExternalServiceException(
                "Reddit service not initialized. Use async context manager.",
                retryable=False
            )
        
        try:
            # Convert time range to Reddit format
            reddit_time_range = self._convert_time_range(time_range)
            
            # Build URL for Reddit OAuth API
            url = f"{self.oauth_url}/r/{subreddit}/top"
            params = {
                "t": reddit_time_range,
                "limit": limit,
            }
            
            # Make request with OAuth token
            response = await self.client.get(
                url,
                params=params,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "User-Agent": self.settings.reddit_user_agent,
                }
            )
            
            # Handle errors
            if response.status_code != 200:
                self._handle_http_error(response, subreddit)
            
            # Parse response
            data = response.json()
            
            # Extract posts from Reddit API response
            if not data.get("data") or not data["data"].get("children"):
                logger.warning(f"No posts found in r/{subreddit}")
                return []
            
            # Map Reddit posts to our model
            posts = []
            for child in data["data"]["children"]:
                try:
                    post = self._map_reddit_post(child["data"])
                    posts.append(post)
                except Exception as e:
                    logger.warning(f"Failed to map post: {e}")
                    continue
            
            logger.info(f"Fetched {len(posts)} posts from r/{subreddit}")
            return posts
            
        except httpx.TimeoutException:
            raise TimeoutException(f"Request to r/{subreddit} timed out")
        except httpx.NetworkError as e:
            raise ExternalServiceException(
                f"Network error while fetching r/{subreddit}: {str(e)}",
                retryable=True
            )
        except (RateLimitException, TimeoutException, ExternalServiceException):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching r/{subreddit}: {e}")
            raise ExternalServiceException(
                f"Failed to fetch posts from r/{subreddit}: {str(e)}",
                retryable=True
            )

    
    def _to_viral_post(self, post: RedditPost) -> ViralPost:
        """
        Convert a RedditPost to a ViralPost with viral score.
        
        Args:
            post: RedditPost object
            
        Returns:
            ViralPost object with calculated viral score
        """
        viral_score = calculate_viral_score(post)
        
        return ViralPost(
            id=post.id,
            title=post.title,
            subreddit=post.subreddit,
            url=f"https://www.reddit.com{post.permalink}",
            upvotes=post.score,
            comments=post.num_comments,
            viral_score=viral_score,
            created_at=datetime.fromtimestamp(post.created_utc),
            author=post.author,
        )
    
    async def fetch_multiple_subreddits(
        self,
        subreddits: List[str],
        time_range: str,
        post_count: int
    ) -> List[ViralPost]:
        """
        Fetch posts from multiple subreddits in parallel.
        
        This method fetches posts from all subreddits concurrently,
        handles individual failures gracefully, combines results,
        sorts by viral score, and limits to the requested count.
        
        Args:
            subreddits: List of subreddit names (without r/ prefix)
            time_range: Time range for posts (1h, 1d, 10d, 100d)
            post_count: Maximum number of posts to return
            
        Returns:
            List of ViralPost objects sorted by viral score (highest first)
            
        Raises:
            ExternalServiceException: If all subreddits fail to fetch
        """
        if not subreddits:
            return []
        
        # Calculate how many posts to fetch per subreddit
        # Fetch more than needed to ensure we have enough after filtering
        posts_per_subreddit = max(post_count, 25)
        
        # Create tasks for fetching from each subreddit
        tasks = []
        for subreddit in subreddits:
            task = self._fetch_subreddit_safe(
                subreddit,
                time_range,
                posts_per_subreddit
            )
            tasks.append(task)
        
        # Fetch from all subreddits in parallel
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # Combine all posts from successful fetches
        all_posts: List[RedditPost] = []
        successful_subreddits = 0
        
        for subreddit, posts in zip(subreddits, results):
            if isinstance(posts, list):
                all_posts.extend(posts)
                successful_subreddits += 1
                logger.info(f"Successfully fetched {len(posts)} posts from r/{subreddit}")
            else:
                logger.warning(f"Failed to fetch from r/{subreddit}")
        
        # If all subreddits failed, raise an exception
        if successful_subreddits == 0:
            raise ExternalServiceException(
                "Failed to fetch posts from all subreddits",
                retryable=True
            )
        
        # Convert to ViralPost and calculate viral scores
        viral_posts = [self._to_viral_post(post) for post in all_posts]
        
        # Sort by viral score (highest first)
        viral_posts.sort(key=lambda p: p.viral_score, reverse=True)
        
        # Limit to requested count
        viral_posts = viral_posts[:post_count]
        
        logger.info(
            f"Returning {len(viral_posts)} posts from {successful_subreddits} "
            f"subreddit(s) out of {len(subreddits)} requested"
        )
        
        return viral_posts
    
    async def _fetch_subreddit_safe(
        self,
        subreddit: str,
        time_range: str,
        limit: int
    ) -> List[RedditPost]:
        """
        Safely fetch posts from a subreddit, catching and logging errors.
        
        This method wraps fetch_posts to handle errors gracefully,
        allowing other subreddits to succeed even if one fails.
        
        Args:
            subreddit: Subreddit name
            time_range: Time range for posts
            limit: Maximum number of posts to fetch
            
        Returns:
            List of RedditPost objects, or empty list if fetch fails
        """
        try:
            return await self.fetch_posts(subreddit, time_range, limit)
        except Exception as e:
            logger.error(f"Error fetching r/{subreddit}: {e}")
            return []
