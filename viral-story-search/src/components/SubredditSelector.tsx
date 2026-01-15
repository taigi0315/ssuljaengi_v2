'use client';

import React, { useEffect, useState } from 'react';
import { SubredditSelectorProps, SubredditOption } from '@/types';

const DEFAULT_SUBREDDITS: SubredditOption[] = [
  {
    name: 'AmItheAsshole',
    displayName: 'r/AmItheAsshole',
    description: 'Moral judgment stories',
    isPopular: true
  },
  {
    name: 'relationship_advice',
    displayName: 'r/relationship_advice',
    description: 'Relationship guidance and stories',
    isPopular: true
  },
  {
    name: 'tifu',
    displayName: 'r/tifu',
    description: 'Today I F***ed Up stories',
    isPopular: true
  },
  {
    name: 'confession',
    displayName: 'r/confession',
    description: 'Personal confessions',
    isPopular: true
  },
  {
    name: 'pettyrevenge',
    displayName: 'r/pettyrevenge',
    description: 'Small revenge stories',
    isPopular: true
  },
  {
    name: 'maliciouscompliance',
    displayName: 'r/maliciouscompliance',
    description: 'Following rules to the letter',
    isPopular: true
  }
];

export default function SubredditSelector({
  selected,
  onChange,
  availableSubreddits = DEFAULT_SUBREDDITS
}: SubredditSelectorProps) {
  // Load selected subreddits from session storage on mount
  useEffect(() => {
    const savedSelection = sessionStorage.getItem('selectedSubreddits');
    if (savedSelection && selected.length === 0) {
      try {
        const parsed = JSON.parse(savedSelection);
        if (Array.isArray(parsed) && parsed.length > 0) {
          onChange(parsed);
        }
      } catch (error) {
        console.warn('Failed to parse saved subreddit selection:', error);
      }
    }
  }, [onChange, selected.length]);

  // Save selected subreddits to session storage whenever selection changes
  useEffect(() => {
    if (selected.length > 0) {
      sessionStorage.setItem('selectedSubreddits', JSON.stringify(selected));
    } else {
      sessionStorage.removeItem('selectedSubreddits');
    }
  }, [selected]);

  const handleToggle = (subredditName: string) => {
    // Ensure we work with unique values to handle any duplicates in the selected array
    const uniqueSelected = [...new Set(selected)];
    const isSelected = uniqueSelected.includes(subredditName);
    
    if (isSelected) {
      const newSelection = uniqueSelected.filter(name => name !== subredditName);
      onChange(newSelection);
    } else {
      const newSelection = [...uniqueSelected, subredditName];
      onChange(newSelection);
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-semibold text-gray-700">
        📱 Subreddits
      </label>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
        {availableSubreddits.map((subreddit) => {
          const isSelected = selected.includes(subreddit.name);
          
          return (
            <label
              key={subreddit.name}
              className={`
                flex items-center space-x-2 p-3 rounded-lg border-2 cursor-pointer 
                transition-all duration-200 transform hover:scale-102 active:scale-98
                ${
                  isSelected
                    ? 'bg-blue-50 border-blue-400 shadow-sm hover:bg-blue-100'
                    : 'bg-white border-gray-300 hover:bg-gray-50 hover:border-gray-400'
                }
              `}
            >
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => handleToggle(subreddit.name)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded transition-all"
              />
              <div className="flex-1 min-w-0">
                <div className={`text-sm font-semibold ${isSelected ? 'text-blue-700' : 'text-gray-900'}`}>
                  {subreddit.displayName}
                </div>
                <div className="text-xs text-gray-500 truncate">
                  {subreddit.description}
                </div>
              </div>
            </label>
          );
        })}
      </div>
      <div className="flex items-center justify-between text-xs text-gray-500 mt-2">
        <span>
          Selected: <span className="font-semibold text-blue-600">{selected.length}</span> subreddit{selected.length !== 1 ? 's' : ''}
        </span>
        {selected.length === 0 && (
          <span className="text-red-600 font-medium">⚠️ Select at least one</span>
        )}
      </div>
    </div>
  );
}