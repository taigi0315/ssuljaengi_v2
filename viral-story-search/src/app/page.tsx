'use client';

import { useState, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { SearchControls, ResultsList, ErrorMessage, GenreSelector } from '@/components';
import StoryTabs from '@/components/StoryTabs';
import StoryBuilder from '@/components/StoryBuilder';
import CharacterImageGenerator from '@/components/CharacterImageGenerator';
import { SearchCriteria, ViralPost, ErrorState, StoryGenre } from '@/types';
import { searchCache } from '@/utils/searchCache';
import { debounce } from '@/utils/debounce';
import { searchPosts } from '@/lib/apiClient';

export default function Home() {
  // Global state management for search data
  const [posts, setPosts] = useState<ViralPost[]>([]);
  const [searchCriteria, setSearchCriteria] = useState<SearchCriteria | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ErrorState | string | null>(null);
  
  // Selection state for story generation
  const [selectedPost, setSelectedPost] = useState<ViralPost | null>(null);
  const [customStorySeed, setCustomStorySeed] = useState<string>('');
  const [selectedGenre, setSelectedGenre] = useState<StoryGenre | null>(null);
  const [generatedStoryId, setGeneratedStoryId] = useState<string | null>(null);
  
  // Tab state
  const [activeTab, setActiveTab] = useState<'search' | 'generate' | 'images'>('search');
  
  const router = useRouter();

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

  // Handle post selection
  const handlePostSelect = useCallback((post: ViralPost) => {
    setSelectedPost(post);
    setCustomStorySeed(''); // Clear custom seed when selecting a post
  }, []);

  // Handle create story navigation
  const handleCreateStory = useCallback(() => {
    if ((selectedPost || customStorySeed.trim()) && selectedGenre) {
      // Store selected data in sessionStorage for persistence
      if (selectedPost) {
        sessionStorage.setItem('selectedPost', JSON.stringify(selectedPost));
      }
      sessionStorage.setItem('selectedGenre', selectedGenre);
      if (customStorySeed.trim()) {
        sessionStorage.setItem('customStorySeed', customStorySeed);
      }
      // Switch to story building tab
      setActiveTab('generate');
    }
  }, [selectedPost, customStorySeed, selectedGenre]);

  // Handle tab change
  const handleTabChange = useCallback((tab: 'search' | 'generate' | 'images') => {
    if (tab === 'generate' && !(selectedPost || customStorySeed.trim()) && !selectedGenre) {
      // Don't allow switching to generate tab without source and genre
      return;
    }
    if (tab === 'images' && !generatedStoryId) {
      // Don't allow switching to images tab without a generated story
      return;
    }
    setActiveTab(tab);
  }, [selectedPost, customStorySeed, selectedGenre, generatedStoryId]);

  // Handle generate images
  const handleGenerateImages = useCallback((storyId: string) => {
    setGeneratedStoryId(storyId);
    setActiveTab('images');
  }, []);

  // Check if can proceed to create story
  const canCreateStory = (selectedPost || customStorySeed.trim()) && selectedGenre;

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

      {/* Tabs */}
      <StoryTabs
        activeTab={activeTab}
        onTabChange={handleTabChange}
        hasSelectedPost={!!(selectedPost || customStorySeed.trim())}
        hasGeneratedStory={!!generatedStoryId}
      />

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 sm:py-8 md:py-12">
        {activeTab === 'search' ? (
          <>
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
                selectedPost={selectedPost}
                onPostSelect={handlePostSelect}
                onCreateStory={handleCreateStory}
              />
            )}

            {/* OR Divider */}
            <div className="mt-8 max-w-4xl mx-auto">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-gradient-to-br from-gray-50 via-blue-50 to-gray-100 text-gray-500 font-medium">
                    OR type your own story seed
                  </span>
                </div>
              </div>
            </div>

            {/* Custom Story Seed Input */}
            <div className="mt-6 max-w-4xl mx-auto">
              <div className="bg-white rounded-lg shadow-lg p-6">
                <label className="block text-lg font-bold text-gray-900 mb-3">
                  ✍️ Write Your Own Story Seed
                </label>
                <textarea
                  value={customStorySeed}
                  onChange={(e) => {
                    setCustomStorySeed(e.target.value);
                    if (e.target.value.trim()) {
                      setSelectedPost(null); // Clear selected post when typing custom seed
                    }
                  }}
                  placeholder="Enter your story idea, concept, or seed here... (e.g., 'A corporate executive discovers that her rival is actually her long-lost childhood friend')"
                  className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent resize-none text-gray-900"
                />
              </div>
            </div>

            {/* Genre Selection */}
            <div className="mt-8 max-w-6xl mx-auto">
              <div className="bg-white rounded-lg shadow-lg p-6">
                <GenreSelector
                  selectedGenre={selectedGenre}
                  onGenreSelect={setSelectedGenre}
                />
              </div>
            </div>

            {/* Create Story Button */}
            <div className="mt-8 max-w-4xl mx-auto text-center">
              <button
                onClick={handleCreateStory}
                disabled={!canCreateStory}
                className={`
                  px-10 py-4 rounded-lg font-bold text-lg transition-all
                  ${canCreateStory
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:shadow-xl hover:scale-105'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }
                `}
              >
                {!selectedGenre && !(selectedPost || customStorySeed.trim())
                  ? '👆 Select a post/seed AND genre first'
                  : !selectedGenre
                    ? '👆 Select a genre first'
                    : !(selectedPost || customStorySeed.trim())
                      ? '👆 Select a post or enter a story seed first'
                      : '✨ Create Story'
                }
              </button>
            </div>
          </>
        ) : activeTab === 'generate' ? (
          <>
            {/* Story Building Tab */}
            {selectedGenre && (
              <div className="max-w-7xl mx-auto">
                <StoryBuilder 
                  post={selectedPost}
                  customStorySeed={customStorySeed.trim() || undefined}
                  selectedGenre={selectedGenre}
                  onGenerateImages={handleGenerateImages}
                />
              </div>
            )}
          </>
        ) : (
          <>
            {/* Character Images Tab */}
            {generatedStoryId && (
              <div className="max-w-7xl mx-auto">
                <CharacterImageGenerator storyId={generatedStoryId} />
              </div>
            )}
          </>
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
