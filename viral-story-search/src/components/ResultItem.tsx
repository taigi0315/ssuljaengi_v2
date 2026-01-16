import React from 'react';
import { ResultItemProps } from '@/types';

const ResultItem: React.FC<ResultItemProps> = ({ post, isSelected = false, onSelect }) => {
  // Format post age
  const formatPostAge = (createdAt: Date): string => {
    const now = new Date();
    const postDate = new Date(createdAt);
    const diffMs = now.getTime() - postDate.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) {
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      return `${diffMinutes}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 30) {
      return `${diffDays}d ago`;
    } else {
      const diffMonths = Math.floor(diffDays / 30);
      return `${diffMonths}mo ago`;
    }
  };

  // Format numbers with commas
  const formatNumber = (num: number): string => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  };

  // Handle click - either select or navigate to Reddit
  const handleClick = (e: React.MouseEvent) => {
    if (onSelect) {
      // If onSelect is provided, use selection mode
      e.preventDefault();
      onSelect(post);
    }
    // Otherwise, let the default link behavior happen
  };

  const containerClasses = `
    bg-white border-2 rounded-lg p-4 sm:p-5 transition-all duration-200 transform
    ${isSelected 
      ? 'border-blue-500 shadow-lg ring-2 ring-blue-200 bg-blue-50' 
      : 'border-gray-200 hover:shadow-lg hover:border-blue-300 hover:-translate-y-1'
    }
    ${onSelect ? 'cursor-pointer' : ''}
  `.trim();

  return (
    <div 
      className={containerClasses}
      onClick={onSelect ? handleClick : undefined}
    >
      {/* Post title */}
      {onSelect ? (
        // Selection mode - no external link
        <div className="mb-3">
          <h3 className="text-base sm:text-lg font-bold text-gray-900 leading-snug">
            {post.title}
          </h3>
          {isSelected && (
            <span className="text-xs text-blue-600 font-medium mt-1 inline-block">
              ✓ Selected for story generation
            </span>
          )}
        </div>
      ) : (
        // Normal mode - external link
        <a
          href={post.url}
          target="_blank"
          rel="noopener noreferrer"
          className="block mb-3 group"
        >
          <h3 className="text-base sm:text-lg font-bold text-gray-900 group-hover:text-blue-600 transition-colors duration-150 leading-snug">
            {post.title}
          </h3>
          <span className="text-xs text-blue-500 group-hover:text-blue-700 opacity-0 group-hover:opacity-100 transition-opacity">
            Click to view on Reddit →
          </span>
        </a>
      )}

      {/* Post metadata */}
      <div className="flex flex-wrap items-center gap-3 sm:gap-4 text-xs sm:text-sm text-gray-600">
        {/* Subreddit */}
        <div className="flex items-center font-semibold">
          <span className="text-blue-600 hover:text-blue-700 transition-colors">
            r/{post.subreddit}
          </span>
        </div>

        {/* Viral Score */}
        <div className="flex items-center px-2 py-1 bg-purple-100 rounded-md">
          <span className="font-bold text-purple-700">
            ⚡ {post.viralScore.toFixed(1)}
          </span>
        </div>

        {/* Upvotes */}
        <div className="flex items-center space-x-1 px-2 py-1 bg-orange-50 rounded-md">
          <span className="text-orange-500 font-bold">↑</span>
          <span className="font-medium">{formatNumber(post.upvotes)}</span>
        </div>

        {/* Comments */}
        <div className="flex items-center space-x-1 px-2 py-1 bg-gray-100 rounded-md">
          <span className="text-gray-600">💬</span>
          <span className="font-medium">{formatNumber(post.comments)}</span>
        </div>

        {/* Post age */}
        <div className="flex items-center text-gray-500">
          <span>🕐 {formatPostAge(post.createdAt)}</span>
        </div>

        {/* Author */}
        <div className="flex items-center text-gray-500 hidden sm:flex">
          <span>👤 u/{post.author}</span>
        </div>
      </div>

      {/* Author on mobile */}
      <div className="mt-2 text-xs text-gray-500 sm:hidden">
        👤 u/{post.author}
      </div>
    </div>
  );
};

export default ResultItem;
