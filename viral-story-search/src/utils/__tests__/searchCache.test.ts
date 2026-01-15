import { SearchCache } from '../searchCache';
import { SearchCriteria, SearchResponse } from '@/types';

describe('SearchCache', () => {
  let cache: SearchCache;

  beforeEach(() => {
    cache = new SearchCache(3, 1000); // Max 3 entries, 1 second TTL
  });

  describe('Basic cache operations', () => {
    it('should store and retrieve cached results', () => {
      const criteria: SearchCriteria = {
        timeRange: '1d',
        subreddits: ['AmItheAsshole'],
        postCount: 20,
      };

      const response: SearchResponse = {
        posts: [],
        totalFound: 0,
        searchCriteria: criteria,
        executionTime: 100,
      };

      cache.set(criteria, response);
      const retrieved = cache.get(criteria);

      expect(retrieved).toEqual(response);
    });

    it('should return null for non-existent cache entries', () => {
      const criteria: SearchCriteria = {
        timeRange: '1d',
        subreddits: ['AmItheAsshole'],
        postCount: 20,
      };

      const retrieved = cache.get(criteria);
      expect(retrieved).toBeNull();
    });

    it('should generate consistent cache keys for same criteria', () => {
      const criteria1: SearchCriteria = {
        timeRange: '1d',
        subreddits: ['AmItheAsshole', 'tifu'],
        postCount: 20,
      };

      const criteria2: SearchCriteria = {
        timeRange: '1d',
        subreddits: ['tifu', 'AmItheAsshole'], // Different order
        postCount: 20,
      };

      const response: SearchResponse = {
        posts: [],
        totalFound: 0,
        searchCriteria: criteria1,
        executionTime: 100,
      };

      cache.set(criteria1, response);
      const retrieved = cache.get(criteria2);

      expect(retrieved).toEqual(response); // Should find it despite different order
    });
  });

  describe('Cache expiration', () => {
    it('should expire cached entries after TTL', async () => {
      const criteria: SearchCriteria = {
        timeRange: '1d',
        subreddits: ['AmItheAsshole'],
        postCount: 20,
      };

      const response: SearchResponse = {
        posts: [],
        totalFound: 0,
        searchCriteria: criteria,
        executionTime: 100,
      };

      cache.set(criteria, response, 100); // 100ms TTL

      // Should be available immediately
      expect(cache.get(criteria)).toEqual(response);

      // Wait for expiration
      await new Promise(resolve => setTimeout(resolve, 150));

      // Should be expired
      expect(cache.get(criteria)).toBeNull();
    });
  });

  describe('LRU eviction', () => {
    it('should evict oldest entry when cache is full', () => {
      const criteria1: SearchCriteria = {
        timeRange: '1d',
        subreddits: ['AmItheAsshole'],
        postCount: 20,
      };

      const criteria2: SearchCriteria = {
        timeRange: '1d',
        subreddits: ['tifu'],
        postCount: 20,
      };

      const criteria3: SearchCriteria = {
        timeRange: '1d',
        subreddits: ['confession'],
        postCount: 20,
      };

      const criteria4: SearchCriteria = {
        timeRange: '1d',
        subreddits: ['pettyrevenge'],
        postCount: 20,
      };

      const response: SearchResponse = {
        posts: [],
        totalFound: 0,
        searchCriteria: criteria1,
        executionTime: 100,
      };

      // Fill cache to max capacity (3 entries)
      cache.set(criteria1, response);
      cache.set(criteria2, response);
      cache.set(criteria3, response);

      // All should be retrievable
      expect(cache.get(criteria1)).not.toBeNull();
      expect(cache.get(criteria2)).not.toBeNull();
      expect(cache.get(criteria3)).not.toBeNull();

      // Add 4th entry, should evict oldest (criteria1)
      cache.set(criteria4, response);

      expect(cache.get(criteria1)).toBeNull(); // Evicted
      expect(cache.get(criteria2)).not.toBeNull();
      expect(cache.get(criteria3)).not.toBeNull();
      expect(cache.get(criteria4)).not.toBeNull();
    });
  });

  describe('Cache invalidation', () => {
    it('should clear all entries', () => {
      const criteria1: SearchCriteria = {
        timeRange: '1d',
        subreddits: ['AmItheAsshole'],
        postCount: 20,
      };

      const criteria2: SearchCriteria = {
        timeRange: '1d',
        subreddits: ['tifu'],
        postCount: 20,
      };

      const response: SearchResponse = {
        posts: [],
        totalFound: 0,
        searchCriteria: criteria1,
        executionTime: 100,
      };

      cache.set(criteria1, response);
      cache.set(criteria2, response);

      cache.clear();

      expect(cache.get(criteria1)).toBeNull();
      expect(cache.get(criteria2)).toBeNull();
    });

    it('should invalidate entries matching time range', () => {
      const criteria1: SearchCriteria = {
        timeRange: '1d',
        subreddits: ['AmItheAsshole'],
        postCount: 20,
      };

      const criteria2: SearchCriteria = {
        timeRange: '10d',
        subreddits: ['tifu'],
        postCount: 20,
      };

      const response: SearchResponse = {
        posts: [],
        totalFound: 0,
        searchCriteria: criteria1,
        executionTime: 100,
      };

      cache.set(criteria1, response);
      cache.set(criteria2, response);

      // Invalidate all 1d entries
      cache.invalidate({ timeRange: '1d' });

      expect(cache.get(criteria1)).toBeNull();
      expect(cache.get(criteria2)).not.toBeNull();
    });

    it('should invalidate entries matching subreddits', () => {
      const criteria1: SearchCriteria = {
        timeRange: '1d',
        subreddits: ['AmItheAsshole', 'tifu'],
        postCount: 20,
      };

      const criteria2: SearchCriteria = {
        timeRange: '1d',
        subreddits: ['confession'],
        postCount: 20,
      };

      const response: SearchResponse = {
        posts: [],
        totalFound: 0,
        searchCriteria: criteria1,
        executionTime: 100,
      };

      cache.set(criteria1, response);
      cache.set(criteria2, response);

      // Invalidate entries containing 'tifu'
      cache.invalidate({ subreddits: ['tifu'] });

      expect(cache.get(criteria1)).toBeNull();
      expect(cache.get(criteria2)).not.toBeNull();
    });
  });

  describe('Cache statistics', () => {
    it('should return cache statistics', () => {
      const criteria: SearchCriteria = {
        timeRange: '1d',
        subreddits: ['AmItheAsshole'],
        postCount: 20,
      };

      const response: SearchResponse = {
        posts: [],
        totalFound: 0,
        searchCriteria: criteria,
        executionTime: 100,
      };

      const stats1 = cache.getStats();
      expect(stats1.size).toBe(0);
      expect(stats1.maxSize).toBe(3);

      cache.set(criteria, response);

      const stats2 = cache.getStats();
      expect(stats2.size).toBe(1);
      expect(stats2.maxSize).toBe(3);
    });
  });
});
