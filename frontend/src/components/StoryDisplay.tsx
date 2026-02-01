import React from 'react';
import { StoryDisplayProps } from '@/types';

const StoryDisplay: React.FC<StoryDisplayProps> = ({ story }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 sm:p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <span>📖</span>
        <span>Your Story</span>
      </h2>
      
      <div className="space-y-6">
        {/* Story Content */}
        <div className="prose prose-lg max-w-none">
          {story.content.split('\n\n').map((paragraph, index) => (
            <p key={index} className="text-gray-800 leading-relaxed mb-4">
              {paragraph}
            </p>
          ))}
        </div>

        {/* Story Metadata */}
        <div className="border-t pt-6 mt-8">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Story Details</h3>
          <div className="flex flex-wrap gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <span className="font-semibold">Quality Score:</span>
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded font-bold">
                {story.evaluationScore.toFixed(1)}/10
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold">Rewrites:</span>
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
                {story.rewriteCount}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold">Word Count:</span>
              <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded">
                {story.content.split(/\s+/).length}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold">Created:</span>
              <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded">
                {new Date(story.createdAt).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StoryDisplay;
