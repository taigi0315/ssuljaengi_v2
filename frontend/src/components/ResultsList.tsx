import React from 'react';
import { ResultsListProps } from '@/types';
import ResultItem from './ResultItem';
import LoadingSpinner from './LoadingSpinner';

const ResultsList: React.FC<ResultsListProps> = ({
  posts,
  searchCriteria,
  isLoading,
  error,
  selectedPost = null,
  onPostSelect,
  onCreateStory,
}) => {
  // Loading state
  if (isLoading) {
    return (
      <div className="w-full max-w-4xl mx-auto mt-6 sm:mt-8 p-4 sm:p-6">
        <div className="bg-white rounded-lg shadow-lg p-8 sm:p-12">
          <LoadingSpinner 
            size="lg" 
            message="Searching for viral stories..." 
            submessage="This may take a few moments"
          />
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="w-full max-w-4xl mx-auto mt-6 sm:mt-8 p-4 sm:p-6">
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6 shadow-sm">
          <p className="text-red-800 text-center">{error}</p>
        </div>
      </div>
    );
  }

  // Empty results
  if (posts.length === 0) {
    return (
      <div className="w-full max-w-4xl mx-auto mt-6 sm:mt-8 p-4 sm:p-6">
        <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-8 sm:p-12 text-center shadow-sm">
          <div className="text-6xl mb-4">🔍</div>
          <p className="text-gray-700 text-lg sm:text-xl font-semibold mb-2">No viral posts found</p>
          <p className="text-gray-500 text-sm sm:text-base">
            Try adjusting your search criteria or selecting different subreddits
          </p>
        </div>
      </div>
    );
  }

  // Display search criteria
  const timeRangeLabels: Record<string, string> = {
    '1h': '1 hour',
    '1d': '1 day',
    '10d': '10 days',
    '100d': '100 days',
  };

  return (
    <div className="w-full max-w-4xl mx-auto mt-6 sm:mt-8 p-4 sm:p-6 animate-fadeIn">
      {/* Search criteria display */}
      <div className="mb-6 p-4 sm:p-5 bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-lg shadow-sm animate-slideInFromTop">
        <h3 className="text-sm sm:text-base font-bold text-blue-900 mb-3 flex items-center">
          <span className="mr-2">📋</span>
          Search Criteria
        </h3>
        <div className="text-sm text-blue-800 space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-semibold">Time Range:</span>
            <span className="px-2 py-1 bg-blue-100 rounded-md transition-all hover:bg-blue-200">
              {timeRangeLabels[searchCriteria.timeRange] || searchCriteria.timeRange}
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-semibold">Subreddits:</span>
            <div className="flex flex-wrap gap-1">
              {searchCriteria.subreddits.map(sub => (
                <span key={sub} className="px-2 py-1 bg-blue-100 rounded-md text-xs sm:text-sm transition-all hover:bg-blue-200">
                  r/{sub}
                </span>
              ))}
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-semibold">Post Count:</span>
            <span className="px-2 py-1 bg-blue-100 rounded-md transition-all hover:bg-blue-200">
              {searchCriteria.postCount}
            </span>
          </div>
        </div>
      </div>

      {/* Results header */}
      <div className="mb-4 sm:mb-6 flex items-center justify-between animate-slideInFromTop" style={{ animationDelay: '0.1s' }}>
        <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 flex items-center">
          <span className="mr-2">🔥</span>
          Viral Stories
        </h2>
        <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-semibold animate-scaleIn">
          {posts.length} {posts.length === 1 ? 'result' : 'results'}
        </span>
      </div>

      {/* Results list */}
      <div className="space-y-3 sm:space-y-4">
        {posts.map((post, index) => (
          <div 
            key={post.id} 
            className="animate-fadeIn"
            style={{ animationDelay: `${index * 0.05}s` }}
          >
            <ResultItem 
              post={post} 
              isSelected={selectedPost?.id === post.id}
              onSelect={onPostSelect}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResultsList;
