"""
Cache utility for search results with TTL and LRU eviction.
"""
import asyncio
from typing import Any, Optional
from cachetools import TTLCache


class SearchCache:
    """
    Thread-safe in-memory cache with TTL and LRU eviction.
    
    Uses cachetools.TTLCache for automatic expiration and LRU eviction policy.
    All operations are protected by an asyncio.Lock for thread safety.
    """
    
    def __init__(self, maxsize: int = 100, ttl: int = 300):
        """
        Initialize the cache.
        
        Args:
            maxsize: Maximum number of entries (default: 100)
            ttl: Time-to-live in seconds (default: 300 = 5 minutes)
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        async with self.lock:
            return self.cache.get(key)
    
    async def set(self, key: str, value: Any) -> None:
        """
        Store a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        async with self.lock:
            self.cache[key] = value
    
    async def clear(self) -> None:
        """Clear all entries from the cache."""
        async with self.lock:
            self.cache.clear()
    
    async def size(self) -> int:
        """
        Get the current number of entries in the cache.
        
        Returns:
            Number of cached entries
        """
        async with self.lock:
            return len(self.cache)
