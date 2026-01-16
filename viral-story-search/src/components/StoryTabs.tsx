'use client';

interface StoryTabsProps {
  activeTab: 'search' | 'generate' | 'images';
  onTabChange: (tab: 'search' | 'generate' | 'images') => void;
  hasSelectedPost: boolean;
  hasGeneratedStory: boolean;
}

export default function StoryTabs({ activeTab, onTabChange, hasSelectedPost, hasGeneratedStory }: StoryTabsProps) {
  return (
    <div className="bg-white border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex gap-2">
          {/* Tab 1: Story Finding */}
          <button
            onClick={() => onTabChange('search')}
            className={`
              px-6 py-4 font-semibold text-sm sm:text-base transition-all relative
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
              px-6 py-4 font-semibold text-sm sm:text-base transition-all relative
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
              {!hasSelectedPost && (
                <span className="text-xs bg-gray-200 px-2 py-1 rounded">Select a post first</span>
              )}
            </div>
          </button>

          {/* Tab 3: Character Images */}
          <button
            onClick={() => onTabChange('images')}
            disabled={!hasGeneratedStory}
            className={`
              px-6 py-4 font-semibold text-sm sm:text-base transition-all relative
              ${activeTab === 'images'
                ? 'text-purple-600 border-b-2 border-purple-600'
                : hasGeneratedStory
                  ? 'text-gray-600 hover:text-gray-900'
                  : 'text-gray-400 cursor-not-allowed'
              }
            `}
          >
            <div className="flex items-center gap-2">
              <span className="text-lg">🎨</span>
              <span>Character Images</span>
              {!hasGeneratedStory && (
                <span className="text-xs bg-gray-200 px-2 py-1 rounded">Generate story first</span>
              )}
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}
