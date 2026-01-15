'use client';

import { useState, useCallback, useMemo } from 'react';
import { SearchControls, ResultsList, ErrorMessage } from '@/components';
import { SearchCriteria, ViralPost, ErrorState } from '@/types';
import { searchCache } from '@/utils/searchCache';
import { debounce } from '@/utils/debounce';
import { searchPosts } from '@/lib/apiClient';

export default function Home() {
  // Global state management for search data
  const [posts, setPosts] = useState<ViralPost[]>([]);
  const [searchCriteria, setSearchCriteria] = useState<SearchCriteria | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ErrorState | string | null>(null);

  // Handle search execution with caching
  const performSearch = useCallback(async (criteria: SearchCriteria) => {
    setIsLoading(true);
    setError(null);
    setSearchCriteria(criteria);

    // Check client-side cache first
    const cachedResult = searchCache.get(criteria);
    if (cachedResult) {
      setPosts(cachedResult.posts || []);
      setError(null);
      setIsLoading(false);
      return;
    }

    try {
      const data = await searchPosts({
        timeRange: criteria.timeRange,
        subreddits: criteria.subreddits,
        postCount: criteria.postCount,
      });

      // Handle successful response
      setPosts(data.posts || []);
      setError(null);
      
      // Cache the successful result
      searchCache.set(criteria, data);
    } catch (err) {
      console.error('Search error:', err);
      if (err instanceof Error) {
        // Check if it's a backend unavailable error
        if (err.message.includes('fetch') || err.message.includes('Failed to fetch')) {
          setError('Backend unavailable. Please ensure the Python backend is running on port 8000.');
        } else {
          setError(err.message);
        }
      } else {
        setError('Connection error. Please check your internet connection and try again.');
      }
      setPosts([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Debounced search handler (300ms delay)
  const debouncedSearch = useMemo(
    () => debounce(performSearch, 300),
    [performSearch]
  );

  // Handle search execution
  const handleSearch = useCallback((criteria: SearchCriteria) => {
    // Use immediate execution for button clicks
    performSearch(criteria);
  }, [performSearch]);

  // Handle retry for recoverable errors
  const handleRetry = () => {
    if (searchCriteria) {
      handleSearch(searchCriteria);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-4 sm:py-6">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 text-center">
            🔥 Viral Story Search
          </h1>
          <p className="text-sm sm:text-base text-gray-600 text-center mt-2">
            Discover the most engaging Reddit stories
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 sm:py-8 md:py-12">
        {/* Search Controls */}
        <SearchControls onSearch={handleSearch} isLoading={isLoading} />

        {/* Error Display */}
        {error && (
          <div className="mt-6 max-w-4xl mx-auto">
            <ErrorMessage error={error} onRetry={handleRetry} />
          </div>
        )}

        {/* Results Display */}
        {(searchCriteria || isLoading) && !error && (
          <ResultsList
            posts={posts}
            searchCriteria={searchCriteria || { timeRange: '1d', subreddits: [], postCount: 20 }}
            isLoading={isLoading}
            error={null}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="container mx-auto px-4 py-6 text-center text-sm text-gray-600">
          <p>Powered by Reddit API • Built with Next.js & TailwindCSS</p>
        </div>
      </footer>
    </div>
  );
}
