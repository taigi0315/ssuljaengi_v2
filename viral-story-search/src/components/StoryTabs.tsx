'use client';

interface StoryTabsProps {
  activeTab: 'search' | 'generate' | 'script' | 'images' | 'scenes' | 'video' | 'eye_candy' | 'shorts';
  onTabChange: (tab: 'search' | 'generate' | 'script' | 'images' | 'scenes' | 'video' | 'eye_candy' | 'shorts') => void;
  hasSelectedPost: boolean;
  hasGeneratedStory: boolean;
  hasWebtoonScript?: boolean;
  activeWorkflow: 'story' | 'eye_candy';
}

export default function StoryTabs({
  activeTab,
  onTabChange,
  hasSelectedPost,
  hasGeneratedStory,
  hasWebtoonScript = false,
  activeWorkflow,
}: StoryTabsProps) {
  return (
    <div className="bg-white border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex gap-2 overflow-x-auto justify-center">
          {activeWorkflow === 'story' ? (
            <>
              {/* Tab 1: Story Finding */}
              <button
                onClick={() => onTabChange('search')}
                className={`
                  px-4 sm:px-6 py-4 font-semibold text-sm sm:text-base transition-all relative whitespace-nowrap
                  ${activeTab === 'search'
                    ? 'text-purple-600 border-b-2 border-purple-600'
                    : 'text-gray-600 hover:text-gray-900'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">🔍</span>
                  <span>Story Finding</span>
                </div>
              </button>

              {/* Tab 2: Story Building */}
              <button
                onClick={() => onTabChange('generate')}
                disabled={!hasSelectedPost}
                className={`
                  px-4 sm:px-6 py-4 font-semibold text-sm sm:text-base transition-all relative whitespace-nowrap
                  ${activeTab === 'generate'
                    ? 'text-purple-600 border-b-2 border-purple-600'
                    : hasSelectedPost
                      ? 'text-gray-600 hover:text-gray-900'
                      : 'text-gray-400 cursor-not-allowed'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">✨</span>
                  <span>Story Building</span>
                </div>
              </button>

              {/* Tab 3: Script Preview (NEW) */}
              <button
                onClick={() => onTabChange('script')}
                disabled={!hasGeneratedStory}
                className={`
                  px-4 sm:px-6 py-4 font-semibold text-sm sm:text-base transition-all relative whitespace-nowrap
                  ${activeTab === 'script'
                    ? 'text-purple-600 border-b-2 border-purple-600'
                    : hasGeneratedStory
                      ? 'text-gray-600 hover:text-gray-900'
                      : 'text-gray-400 cursor-not-allowed'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">📖</span>
                  <span>Webtoon Script</span>
                </div>
              </button>

              {/* Tab 4: Character Images */}
              <button
                onClick={() => onTabChange('images')}
                disabled={!hasWebtoonScript}
                className={`
                  px-4 sm:px-6 py-4 font-semibold text-sm sm:text-base transition-all relative whitespace-nowrap
                  ${activeTab === 'images'
                    ? 'text-purple-600 border-b-2 border-purple-600'
                    : hasWebtoonScript
                      ? 'text-gray-600 hover:text-gray-900'
                      : 'text-gray-400 cursor-not-allowed'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">🎨</span>
                  <span>Characters</span>
                </div>
              </button>

              {/* Tab 5: Scene Images */}
              <button
                onClick={() => onTabChange('scenes')}
                disabled={!hasWebtoonScript}
                className={`
                  px-4 sm:px-6 py-4 font-semibold text-sm sm:text-base transition-all relative whitespace-nowrap
                  ${activeTab === 'scenes'
                    ? 'text-purple-600 border-b-2 border-purple-600'
                    : hasWebtoonScript
                      ? 'text-gray-600 hover:text-gray-900'
                      : 'text-gray-400 cursor-not-allowed'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">🖼️</span>
                  <span>Scene Images</span>
                </div>
              </button>

              {/* Tab 6: Final Video */}
              <button
                onClick={() => onTabChange('video')}
                disabled={!hasWebtoonScript}
                className={`
                  px-4 sm:px-6 py-4 font-semibold text-sm sm:text-base transition-all relative whitespace-nowrap
                  ${activeTab === 'video'
                    ? 'text-purple-600 border-b-2 border-purple-600'
                    : hasWebtoonScript
                      ? 'text-gray-600 hover:text-gray-900'
                      : 'text-gray-400 cursor-not-allowed'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">🎬</span>
                  <span>Final Video</span>
                </div>
              </button>
            </>
          ) : (
            <>
              {/* Eye Candy Pipeline Tabs */}
              <button
                onClick={() => onTabChange('eye_candy')}
                className={`
                  px-4 sm:px-6 py-4 font-semibold text-sm sm:text-base transition-all relative whitespace-nowrap
                  ${activeTab === 'eye_candy'
                    ? 'text-pink-600 border-b-2 border-pink-600'
                    : 'text-gray-600 hover:text-pink-600'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">🍬</span>
                  <span>Create Characters</span>
                </div>
              </button>
              <button
                onClick={() => onTabChange('shorts')}
                className={`
                  px-4 sm:px-6 py-4 font-semibold text-sm sm:text-base transition-all relative whitespace-nowrap
                  ${activeTab === 'shorts'
                    ? 'text-pink-600 border-b-2 border-pink-600'
                    : 'text-gray-600 hover:text-pink-600'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">🎬</span>
                  <span>Shorts Generator</span>
                </div>
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

