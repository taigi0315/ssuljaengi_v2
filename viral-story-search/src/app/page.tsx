'use client';

import { useState, useCallback, useMemo, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { SearchControls, ResultsList, ErrorMessage, GenreSelector, SceneImageGenerator, VideoGenerator, EyeCandyGenerator, WorkflowSelector, ShortsGenerator } from '@/components';
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
  const [manualFullStory, setManualFullStory] = useSessionStorage<string>(
    'gossiptoon_manualFullStory',
    ''
  );

  // Tab state - persistent
  const [activeTab, setActiveTab] = useSessionStorage<'search' | 'generate' | 'script' | 'images' | 'scenes' | 'video' | 'eye_candy' | 'shorts'>(
    SESSION_KEYS.ACTIVE_TAB,
    'search'
  );

  // Eye Candy workflow state
  const [selectedReferenceImage, setSelectedReferenceImage] = useSessionStorage<import('@/types').CharacterImage | null>(
    'gossiptoon_selectedReferenceImage',
    null
  );

  // Workflow state - persistent
  const [workflowMode, setWorkflowMode] = useSessionStorage<'story' | 'eye_candy'>(
    'gossiptoon_workflowMode',
    'story'
  );

  const router = useRouter();

  // Check for stale data on startup - if backend is fresh but frontend has old data
  useEffect(() => {
    const checkAndClearStaleData = async () => {
      // Only run on client
      if (typeof window === 'undefined') return;

      // Check if we have any stored data
      const hasStoredStoryId = sessionStorage.getItem('gossiptoon_generatedStoryId');
      const hasStoredScript = sessionStorage.getItem('gossiptoon_webtoonScript');

      // If we have stored data, verify it exists on the backend
      if (hasStoredStoryId || hasStoredScript) {
        try {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
          const response = await fetch(`${apiUrl}/webtoon/latest`, { method: 'GET' });

          // If backend returns 404 (no data), clear stale frontend cache
          if (response.status === 404 || !response.ok) {
            console.log('Backend data cleared, clearing stale frontend cache...');
            // Clear all gossiptoon session storage keys
            const keysToRemove = Object.keys(sessionStorage).filter(key => key.startsWith('gossiptoon_'));
            keysToRemove.forEach(key => sessionStorage.removeItem(key));
            sessionStorage.removeItem('gossiptoon_manualStoryContent');

            // Reload to get fresh state
            window.location.reload();
          }
        } catch {
          // Backend not available, don't clear (might just be starting up)
        }
      }
    };

    checkAndClearStaleData();
  }, []);

  // Clear all session data for fresh start
  const handleFreshStart = useCallback(() => {
    if (typeof window !== 'undefined') {
      // Clear all gossiptoon session storage keys
      const keysToRemove = Object.keys(sessionStorage).filter(key => key.startsWith('gossiptoon_'));
      keysToRemove.forEach(key => sessionStorage.removeItem(key));

      // Also clear the manual story content
      sessionStorage.removeItem('gossiptoon_manualStoryContent');

      // Reset all local state
      setSelectedPost(null);
      setCustomStorySeed('');
      setSelectedGenre(null);
      setGeneratedStoryId(null);
      setWebtoonScript(null);
      setManualFullStory('');
      setActiveTab('search');
      setPosts([]);
      setSearchCriteria(null);
      setError(null);

      // Clear search cache
      searchCache.clear();
    }
  }, [setSelectedPost, setCustomStorySeed, setSelectedGenre, setGeneratedStoryId, setWebtoonScript, setManualFullStory, setActiveTab]);

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
  const handleTabChange = useCallback((tab: 'search' | 'generate' | 'script' | 'images' | 'scenes' | 'video' | 'eye_candy' | 'shorts') => {
    // Skip validation for Eye Candy mode
    if (workflowMode === 'eye_candy') {
      setActiveTab(tab);
      return;
    }

    // Allow 'generate' tab if: has post/seed, OR has genre (to write manual story)
    if (tab === 'generate' && !selectedGenre) {
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
  }, [selectedGenre, generatedStoryId, webtoonScript, workflowMode]);

  // Handle proceed to shorts from Eye Candy
  const handleProceedToShorts = useCallback((referenceImage: import('@/types').CharacterImage) => {
    setSelectedReferenceImage(referenceImage);
    setActiveTab('shorts');
  }, [setSelectedReferenceImage, setActiveTab]);

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
  // User can proceed if they have a genre selected (they can write full story manually in tab 2)
  const canCreateStory = selectedGenre;

  // Load Test Story Handler
  const handleLoadTestStory = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/webtoon/latest`);
      if (!res.ok) throw new Error('No test data found');

      const script = await res.json();
      console.log('Loaded test script:', script);

      setGeneratedStoryId(script.story_id);
      setWebtoonScript(script);
      setSelectedGenre(script.genre || 'MODERN_ROMANCE_DRAMA_MANHWA');
      setCustomStorySeed('E2E Test Story'); // Dummy to satisfy checks

      setActiveTab('video');
    } catch (e: any) {
      alert('Failed to load test story: ' + e.message);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-4 sm:py-6 relative">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 text-center">
            🔥 Webtoon Shorts Creator
          </h1>
          <p className="text-sm sm:text-base text-gray-600 text-center mt-2">
            Handy tool to create webtoon shorts
          </p>
          {/* Action Buttons */}
          <div className="absolute top-4 right-4 flex gap-2">
            <button
              onClick={handleFreshStart}
              className="text-xs bg-red-50 hover:bg-red-100 text-red-600 px-3 py-1 rounded border border-red-200 transition-colors"
              title="Clear all data and start fresh"
            >
              🔄 Fresh Start
            </button>
            <button
              onClick={handleLoadTestStory}
              className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-600 px-3 py-1 rounded border border-gray-300 transition-colors"
              title="Load latest backend data for testing"
            >
              🧪 Load Test Story
            </button>
          </div>
        </div>
      </header>

      {/* Workflow Selector */}
      <div className="mt-6">
        <WorkflowSelector
          activeWorkflow={workflowMode}
          onChange={(mode: 'story' | 'eye_candy') => {
            setWorkflowMode(mode);
            // Default tab switching logic
            if (mode === 'story') {
              setActiveTab('search');
            } else {
              setActiveTab('eye_candy');
            }
          }}
        />
      </div>

      {/* Tabs */}
      <StoryTabs
        activeTab={activeTab}
        onTabChange={handleTabChange}
        hasSelectedPost={!!(selectedPost || customStorySeed.trim())}
        hasGeneratedStory={!!generatedStoryId}
        hasWebtoonScript={!!webtoonScript}
        activeWorkflow={workflowMode}
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
                {!selectedGenre
                  ? '👆 Select a genre first'
                  : (selectedPost || customStorySeed.trim())
                    ? '✨ Create Story'
                    : '✨ Write Your Story'
                }
              </button>
              {selectedGenre && !(selectedPost || customStorySeed.trim()) && (
                <p className="mt-2 text-sm text-gray-500">
                  You can also select a Reddit post or enter a story seed above
                </p>
              )}
            </div>
          </>
        ) : activeTab === 'generate' ? (
          <>
            {/* Story Building Tab */}
            {selectedGenre && (
              <div className="max-w-7xl mx-auto">
                {/* Manual Full Story Input Option */}
                {!selectedPost && !customStorySeed.trim() && (
                  <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                      ✍️ Write Your Story Manually
                    </h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Enter your complete story below. This will skip AI generation and use your story directly.
                    </p>
                    <textarea
                      value={manualFullStory}
                      onChange={(e) => setManualFullStory(e.target.value)}
                      placeholder="Write your full story here... (This will be used directly without AI rewriting)"
                      className="w-full p-4 text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent resize-none h-64"
                    />
                    {manualFullStory.trim() && (
                      <button
                        onClick={() => {
                          // Create a story object from manual input and proceed
                          const storyId = `manual_${Date.now()}`;
                          setGeneratedStoryId(storyId);
                          // Store the manual story in session for later use
                          sessionStorage.setItem('gossiptoon_manualStoryContent', manualFullStory);
                          setActiveTab('script');
                        }}
                        className="mt-4 w-full px-6 py-4 bg-gradient-to-r from-green-600 to-teal-600 text-white font-bold text-lg rounded-lg hover:shadow-xl hover:scale-105 transition-all"
                      >
                        📝 Use This Story → Proceed to Script
                      </button>
                    )}
                    <div className="mt-4 flex items-center">
                      <div className="flex-1 border-t border-gray-300"></div>
                      <span className="px-4 text-sm text-gray-500">OR go back and select a Reddit post / story seed</span>
                      <div className="flex-1 border-t border-gray-300"></div>
                    </div>
                  </div>
                )}

                {/* Regular Story Builder (shows when post or seed is provided) */}
                {(selectedPost || customStorySeed.trim()) && (
                  <StoryBuilder
                    post={selectedPost}
                    customStorySeed={customStorySeed.trim() || undefined}
                    selectedGenre={selectedGenre}
                    onGenerateImages={handleGenerateImages}
                  />
                )}
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
        ) : activeTab === 'video' ? (
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
        ) : activeTab === 'eye_candy' ? (
          <>
            {/* Eye Candy Tab */}
            <div className="max-w-7xl mx-auto">
              <EyeCandyGenerator onProceedToShorts={handleProceedToShorts} />
            </div>
          </>
        ) : activeTab === 'shorts' ? (
          <>
            {/* Shorts Generator Tab */}
            <div className="max-w-7xl mx-auto">
              <ShortsGenerator referenceImage={selectedReferenceImage || undefined} />
            </div>
          </>
        ) : null}
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
