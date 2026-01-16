import React from 'react';
import { RedditPostDisplayProps } from '@/types';

const RedditPostDisplay: React.FC<RedditPostDisplayProps> = ({ post }) => {
  const formatNumber = (num: number): string => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 sticky top-6">
      <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
        <span>📝</span>
        <span>Original Post</span>
      </h2>
      
      <div className="space-y-4">
        {/* Post Title */}
        <div>
          <h3 className="font-bold text-gray-900 mb-3 leading-snug">{post.title}</h3>
          
          {/* Post Metadata */}
          <div className="flex flex-wrap gap-2 text-sm">
            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded font-semibold">
              r/{post.subreddit}
            </span>
            <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded font-bold">
              ⚡ {post.viralScore.toFixed(1)}
            </span>
            <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded">
              ↑ {formatNumber(post.upvotes)}
            </span>
            <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded">
              💬 {formatNumber(post.comments)}
            </span>
          </div>
        </div>

        {/* Author */}
        <div className="text-sm text-gray-600 border-t pt-4">
          <p className="flex items-center gap-2">
            <span>👤</span>
            <span className="font-semibold">u/{post.author}</span>
          </p>
        </div>

        {/* View on Reddit Link */}
        <div className="border-t pt-4">
          <a
            href={post.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-semibold text-sm transition-colors"
          >
            <span>View on Reddit</span>
            <span>→</span>
          </a>
        </div>
      </div>
    </div>
  );
};

export default RedditPostDisplay;
