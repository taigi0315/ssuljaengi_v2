'use client';

import { useState, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { SearchControls, ResultsList, ErrorMessage, GenreSelector, SceneImageGenerator, VideoGenerator } from '@/components';
import StoryTabs from '@/components/StoryTabs';
import StoryBuilder from '@/components/StoryBuilder';
import CharacterImageGenerator from '@/components/CharacterImageGenerator';
import ScriptPreview from '@/components/ScriptPreview';
import { SearchCriteria, ViralPost, ErrorState, StoryGenre, WebtoonScript } from '@/types';
import { searchCache } from '@/utils/searchCache';
import { debounce } from '@/utils/debounce';
import { searchPosts } from '@/lib/apiClient';
import { useSessionStorage, SESSION_KEYS } from '@/hooks/useSessionStorage';

export default function Home() {
  // Global state management for search data
  // Global state management for search data
  const [posts, setPosts] = useState<ViralPost[]>([]);
  const [searchCriteria, setSearchCriteria] = useState<SearchCriteria | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ErrorState | string | null>(null);
  
  // Selection state for story generation - Persistent
  const [selectedPost, setSelectedPost] = useSessionStorage<ViralPost | null>(
    SESSION_KEYS.SELECTED_POST, 
    null
  );
  const [customStorySeed, setCustomStorySeed] = useSessionStorage<string>(
    SESSION_KEYS.CUSTOM_STORY_SEED, 
    ''
  );
  const [selectedGenre, setSelectedGenre] = useSessionStorage<StoryGenre | null>(
    SESSION_KEYS.SELECTED_GENRE, 
    null
  );
  const [generatedStoryId, setGeneratedStoryId] = useSessionStorage<string | null>(
    SESSION_KEYS.GENERATED_STORY_ID, 
    null
  );
  const [webtoonScript, setWebtoonScript] = useSessionStorage<WebtoonScript | null>(
    SESSION_KEYS.WEBTOON_SCRIPT, 
    null
  );
  
  // Tab state - persistent
  const [activeTab, setActiveTab] = useSessionStorage<'search' | 'generate' | 'script' | 'images' | 'scenes' | 'video'>(
    SESSION_KEYS.ACTIVE_TAB, 
    'search'
  );
  
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
      // Use useSessionStorage hook logic, no need for manual setItem here
      // Just switching tab triggers re-render and saving happens automatically in useEffect if values changed
      // But values are already set via setters (setSelectedPost etc) which trigger save.
      
      // Explicitly clear generated story if we are starting a NEW story
      // (This logic might need refinement if we want to "resume" creation?)
      // For now, assuming "Create Story" button implies "Start Fresh" or "Continue with selection"
      
      // If we want to force clear previous results when clicking Create Story:
      // But we are using persistent state... 
      // Actually, if I select a new post, `generatedStoryId` might still be the OLD one unless I clear it.
      // So I shoud clear derived state.
      setGeneratedStoryId(null);
      setWebtoonScript(null);
      
      // Switch to story building tab
      setActiveTab('generate');
    }
  }, [selectedPost, customStorySeed, selectedGenre, setGeneratedStoryId, setWebtoonScript, setActiveTab]);

  // Handle tab change
  const handleTabChange = useCallback((tab: 'search' | 'generate' | 'script' | 'images' | 'scenes' | 'video') => {
    if (tab === 'generate' && !(selectedPost || customStorySeed.trim()) && !selectedGenre) {
      return;
    }
    if (tab === 'script' && !generatedStoryId) {
      return;
    }
    if (tab === 'images' && !webtoonScript) {
      return;
    }
    if (tab === 'scenes' && !webtoonScript) {
      return;
    }
    if (tab === 'video' && !webtoonScript) {
      return;
    }
    setActiveTab(tab);
  }, [selectedPost, customStorySeed, selectedGenre, generatedStoryId, webtoonScript]);

  // Handle story generation complete - go to script tab
  const handleGenerateImages = useCallback((storyId: string) => {
    setGeneratedStoryId(storyId);
    setActiveTab('script');
  }, []);

  // Handle webtoon script generated (called from ScriptPreview)
  const handleScriptGenerated = useCallback((script: WebtoonScript) => {
    setWebtoonScript(script);
  }, [setWebtoonScript]);

  // Handle script update (from Character/Scene generators)
  const handleScriptUpdate = useCallback((script: WebtoonScript) => {
    setWebtoonScript(script);
  }, [setWebtoonScript]);

  // Handle proceed to characters (called from ScriptPreview)
  const handleProceedToCharacters = useCallback(() => {
    setActiveTab('images');
  }, [setActiveTab]);

  // Handle proceed to scenes (called from CharacterImageGenerator)
  const handleProceedToScenes = useCallback(() => {
    setActiveTab('scenes');
  }, [setActiveTab]);

  // Handle proceed to video (called from SceneImageGenerator)
  const handleProceedToVideo = useCallback(() => {
    setActiveTab('video');
  }, [setActiveTab]);

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
        hasWebtoonScript={!!webtoonScript}
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
                searchCriteria={searchCriteria!}
                isLoading={isLoading}
                error={null}
                selectedPost={selectedPost}
                onPostSelect={handlePostSelect}
              />
            )}

            {/* Custom Story Seed Input */}
            <div className="mt-8 max-w-4xl mx-auto">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-gradient-to-br from-gray-50 via-blue-50 to-gray-100 text-gray-500">
                    OR type your own story seed
                  </span>
                </div>
              </div>
              
              <div className="mt-6">
                <textarea
                  value={customStorySeed}
                  onChange={(e) => {
                    setCustomStorySeed(e.target.value);
                    if (e.target.value.trim()) {
                      setSelectedPost(null); // Clear selected post when typing custom seed
                    }
                  }}
                  placeholder="Enter your story idea here... (e.g., 'A young woman discovers she can read minds after a lightning strike')"
                  className="w-full p-4 text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent resize-none h-32"
                />
              </div>
            </div>

            {/* Genre Selector */}
            <div className="mt-8 max-w-4xl mx-auto">
              <GenreSelector
                selectedGenre={selectedGenre}
                onGenreSelect={setSelectedGenre}
              />
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
        ) : activeTab === 'script' ? (
          <>
            {/* Script Preview Tab */}
            {generatedStoryId && selectedGenre && (
              <div className="max-w-7xl mx-auto">
                <ScriptPreview
                  storyId={generatedStoryId}
                  genre={selectedGenre}
                  webtoonScript={webtoonScript}
                  onScriptGenerated={handleScriptGenerated}
                  onProceedToCharacters={handleProceedToCharacters}
                />
              </div>
            )}
          </>
        ) : activeTab === 'images' ? (
          <>
            {/* Character Images Tab */}
            {webtoonScript && (
              <div className="max-w-7xl mx-auto">
                <CharacterImageGenerator 
                  storyId={generatedStoryId!}
                  webtoonScript={webtoonScript}
                  onUpdateScript={handleScriptUpdate}
                  onProceedToScenes={handleProceedToScenes}
                />
              </div>
            )}
          </>
        ) : activeTab === 'scenes' ? (
          <>
            {/* Scene Images Tab */}
            {webtoonScript && (
              <div className="max-w-7xl mx-auto">
                <SceneImageGenerator 
                  webtoonScript={webtoonScript} 
                  onUpdateScript={handleScriptUpdate}
                  onProceedToVideo={handleProceedToVideo}
                />
              </div>
            )}
          </>
        ) : (
          <>
            {/* Video Generator Tab */}
            {webtoonScript && selectedGenre && (
              <div className="max-w-7xl mx-auto">
                <VideoGenerator 
                  webtoonScript={webtoonScript}
                  genre={selectedGenre}
                />
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
