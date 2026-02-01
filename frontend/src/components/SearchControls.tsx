'use client';

import React, { useState, useEffect } from 'react';
import { SearchControlsProps, SearchCriteria } from '@/types';
import { validateSearchCriteria, validatePostCount } from '@/utils/validation';
import { searchCache } from '@/utils/searchCache';
import TimeRangeSelector from './TimeRangeSelector';
import SubredditSelector from './SubredditSelector';
import PostCountInput from './PostCountInput';

const DEFAULT_TIME_RANGE = '1d';
const DEFAULT_POST_COUNT = 20;

const DEFAULT_SUBREDDITS = [
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

interface ValidationErrors {
  subreddits?: string;
  postCount?: string;
  timeRange?: string;
}

export default function SearchControls({ onSearch, isLoading }: SearchControlsProps) {
  const [timeRange, setTimeRange] = useState<string>(DEFAULT_TIME_RANGE);
  const [selectedSubreddits, setSelectedSubreddits] = useState<string[]>([]);
  const [postCount, setPostCount] = useState<number>(DEFAULT_POST_COUNT);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [hasAttemptedSearch, setHasAttemptedSearch] = useState(false);

  // Validate all fields and update error state
  const validateAllFields = (): boolean => {
    const errors: ValidationErrors = {};

    // Validate subreddits
    if (selectedSubreddits.length === 0) {
      errors.subreddits = 'Please select at least one subreddit';
    }

    // Validate post count
    const postCountError = validatePostCount(postCount);
    if (postCountError) {
      errors.postCount = postCountError;
    }

    // Validate time range
    const validTimeRanges = ['1h', '1d', '10d', '100d'];
    if (!validTimeRanges.includes(timeRange)) {
      errors.timeRange = 'Invalid time range selected';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Validate on field changes if user has attempted search
  useEffect(() => {
    if (hasAttemptedSearch) {
      validateAllFields();
    }
  }, [timeRange, selectedSubreddits, postCount, hasAttemptedSearch]);

  // Handle search button click
  const handleSearch = () => {
    setHasAttemptedSearch(true);

    if (!validateAllFields()) {
      return;
    }

    const criteria: SearchCriteria = {
      timeRange: timeRange as '1h' | '1d' | '10d' | '100d',
      subreddits: selectedSubreddits,
      postCount,
    };

    onSearch(criteria);
  };

  // Handle time range change
  const handleTimeRangeChange = (newRange: string) => {
    setTimeRange(newRange);
    // Invalidate cache entries for the old time range
    searchCache.invalidate({ timeRange: timeRange as '1h' | '1d' | '10d' | '100d' });
    // Clear time range error when changed
    if (validationErrors.timeRange) {
      setValidationErrors(prev => ({ ...prev, timeRange: undefined }));
    }
  };

  // Handle subreddit selection change
  const handleSubredditChange = (subreddits: string[]) => {
    setSelectedSubreddits(subreddits);
    // Clear subreddit error when subreddits are selected
    if (subreddits.length > 0 && validationErrors.subreddits) {
      setValidationErrors(prev => ({ ...prev, subreddits: undefined }));
    }
  };

  // Handle post count change
  const handlePostCountChange = (count: number) => {
    setPostCount(count);
    // Clear post count error when valid count is entered
    const error = validatePostCount(count);
    if (!error && validationErrors.postCount) {
      setValidationErrors(prev => ({ ...prev, postCount: undefined }));
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-4 sm:p-6 bg-white rounded-lg shadow-lg border border-gray-200 transition-shadow hover:shadow-xl">
      <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4 sm:mb-6">
        Search Settings
      </h2>

      <div className="space-y-4 sm:space-y-6">
        {/* Time Range Selector */}
        <div className={validationErrors.timeRange ? 'ring-2 ring-red-300 rounded-lg p-2 transition-all' : ''}>
          <TimeRangeSelector
            selected={timeRange}
            onChange={handleTimeRangeChange}
          />
          {validationErrors.timeRange && (
            <div className="mt-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-2 animate-pulse">
              {validationErrors.timeRange}
            </div>
          )}
        </div>

        {/* Subreddit Selector */}
        <div className={validationErrors.subreddits ? 'ring-2 ring-red-300 rounded-lg p-2 transition-all' : ''}>
          <SubredditSelector
            selected={selectedSubreddits}
            onChange={handleSubredditChange}
            availableSubreddits={DEFAULT_SUBREDDITS}
          />
          {validationErrors.subreddits && (
            <div className="mt-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-2 animate-pulse">
              {validationErrors.subreddits}
            </div>
          )}
        </div>

        {/* Post Count Input */}
        <div className={validationErrors.postCount ? 'ring-2 ring-red-300 rounded-lg p-2 transition-all' : ''}>
          <PostCountInput
            value={postCount}
            onChange={handlePostCountChange}
            error={validationErrors.postCount}
          />
        </div>

        {/* Global Validation Error Display */}
        {hasAttemptedSearch && Object.keys(validationErrors).length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3 animate-pulse">
            <p className="text-sm font-semibold text-red-800 mb-1">
              ⚠️ Please fix the following errors:
            </p>
            <ul className="list-disc list-inside text-sm text-red-600 space-y-1">
              {validationErrors.subreddits && <li>{validationErrors.subreddits}</li>}
              {validationErrors.postCount && <li>{validationErrors.postCount}</li>}
              {validationErrors.timeRange && <li>{validationErrors.timeRange}</li>}
            </ul>
          </div>
        )}

        {/* Search Button */}
        <div className="flex justify-center pt-2 sm:pt-4">
          <button
            onClick={handleSearch}
            disabled={isLoading || selectedSubreddits.length === 0}
            className={`
              w-full sm:w-auto px-6 sm:px-8 py-3 rounded-lg font-semibold text-white text-base sm:text-lg
              transition-all duration-200 transform shadow-md
              ${
                isLoading || selectedSubreddits.length === 0
                  ? 'bg-gray-400 cursor-not-allowed opacity-75'
                  : 'bg-blue-600 hover:bg-blue-700 hover:scale-105 hover:shadow-lg active:scale-95 focus:ring-4 focus:ring-blue-300'
              }
            `}
            aria-label={isLoading ? 'Searching...' : 'Search Viral Stories'}
          >
            {isLoading ? (
              <span className="flex items-center justify-center space-x-2">
                <svg
                  className="animate-spin h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                <span>Searching...</span>
              </span>
            ) : (
              <span className="flex items-center justify-center space-x-2">
                <span>🔍</span>
                <span>Search Viral Stories</span>
              </span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
