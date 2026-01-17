'use client';

import { useState } from 'react';

interface ScenePromptEditorProps {
  prompt: string;
  originalPrompt: string;
  onPromptChange: (prompt: string) => void;
  isLocked: boolean;
  onLockToggle: () => void;
}

export default function ScenePromptEditor({
  prompt,
  originalPrompt,
  onPromptChange,
  isLocked,
  onLockToggle,
}: ScenePromptEditorProps) {
  const hasChanges = prompt !== originalPrompt;
  
  const handleReset = () => {
    onPromptChange(originalPrompt);
  };
  
  const handleCopy = () => {
    navigator.clipboard.writeText(prompt);
  };

  return (
    <div className="bg-gray-100 rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-700">Scene Description</h3>
        
        {/* Toolbar */}
        <div className="flex items-center gap-2">
          {hasChanges && (
            <span className="text-xs text-orange-600 font-medium">Modified</span>
          )}
          
          <button
            onClick={handleCopy}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded transition-colors"
            title="Copy prompt"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </button>
          
          <button
            onClick={handleReset}
            disabled={!hasChanges}
            className={`p-2 rounded transition-colors ${
              hasChanges
                ? 'text-gray-500 hover:text-gray-700 hover:bg-gray-200'
                : 'text-gray-300 cursor-not-allowed'
            }`}
            title="Reset to original"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          
          <button
            onClick={onLockToggle}
            className={`p-2 rounded transition-colors ${
              isLocked
                ? 'text-red-500 hover:text-red-700 hover:bg-red-100'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200'
            }`}
            title={isLocked ? 'Unlock prompt' : 'Lock prompt'}
          >
            {isLocked ? (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 2a5 5 0 00-5 5v2a2 2 0 00-2 2v5a2 2 0 002 2h10a2 2 0 002-2v-5a2 2 0 00-2-2H7V7a3 3 0 015.905-.75 1 1 0 001.937-.5A5.002 5.002 0 0010 2z" />
              </svg>
            )}
          </button>
        </div>
      </div>
      
      <textarea
        value={prompt}
        onChange={(e) => onPromptChange(e.target.value)}
        disabled={isLocked}
        className={`
          w-full h-32 p-3 text-sm border rounded-lg resize-none
          ${isLocked
            ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
            : 'bg-white text-gray-900 border-gray-300 focus:ring-2 focus:ring-purple-600 focus:border-transparent'
          }
        `}
        placeholder="Enter scene description for image generation..."
      />
    </div>
  );
}
