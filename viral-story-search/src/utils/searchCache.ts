/**
 * Client-side search result cache
 * Implements LRU cache with TTL for search results
 */

import { SearchResponse, SearchCriteria } from '@/types';

interface CachedResult {
  data: SearchResponse;
  timestamp: number;
  ttl: number;
}

export class SearchCache {
  private cache = new Map<string, CachedResult>();
  private readonly maxCacheSize: number;
  private readonly defaultTTL: number;

  constructor(maxCacheSize: number = 50, defaultTTL: number = 300000) {
    this.maxCacheSize = maxCacheSize;
    this.defaultTTL = defaultTTL; // 5 minutes default
  }

  /**
   * Generate cache key from search criteria
   */
  private getCacheKey(criteria: SearchCriteria): string {
    return JSON.stringify({
      timeRange: criteria.timeRange,
      subreddits: [...criteria.subreddits].sort(), // Sort for consistent keys
      postCount: criteria.postCount,
    });
  }

  /**
   * Check if cached result is expired
   */
  private isExpired(cached: CachedResult): boolean {
    return Date.now() - cached.timestamp > cached.ttl;
  }

  /**
   * Evict oldest entry from cache
   */
  private evictOldest(): void {
    const oldestKey = this.cache.keys().next().value;
    if (oldestKey) {
      this.cache.delete(oldestKey);
    }
  }

  /**
   * Set cache entry
   */
  set(criteria: SearchCriteria, data: SearchResponse, ttl?: number): void {
    // Implement LRU by removing oldest entries if cache is full
    if (this.cache.size >= this.maxCacheSize) {
      this.evictOldest();
    }

    const key = this.getCacheKey(criteria);
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTTL,
    });
  }

  /**
   * Get cache entry
   */
  get(criteria: SearchCriteria): SearchResponse | null {
    const key = this.getCacheKey(criteria);
    const cached = this.cache.get(key);

    if (!cached) {
      return null;
    }

    if (this.isExpired(cached)) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Invalidate cache entries matching criteria
   */
  invalidate(criteria?: Partial<SearchCriteria>): void {
    if (!criteria) {
      this.clear();
      return;
    }

    // Invalidate entries matching partial criteria
    const keysToDelete: string[] = [];
    
    this.cache.forEach((_, key) => {
      try {
        const parsedKey = JSON.parse(key);
        let shouldInvalidate = false;

        if (criteria.timeRange && parsedKey.timeRange === criteria.timeRange) {
          shouldInvalidate = true;
        }

        if (criteria.subreddits && criteria.subreddits.length > 0) {
          const hasMatchingSubreddit = criteria.subreddits.some(sub =>
            parsedKey.subreddits.includes(sub)
          );
          if (hasMatchingSubreddit) {
            shouldInvalidate = true;
          }
        }

        if (shouldInvalidate) {
          keysToDelete.push(key);
        }
      } catch (error) {
        // Invalid key format, delete it
        keysToDelete.push(key);
      }
    });

    keysToDelete.forEach(key => this.cache.delete(key));
  }

  /**
   * Get cache statistics
   */
  getStats(): { size: number; maxSize: number; hitRate?: number } {
    return {
      size: this.cache.size,
      maxSize: this.maxCacheSize,
    };
  }
}

// Export singleton instance
export const searchCache = new SearchCache();
