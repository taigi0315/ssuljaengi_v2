import { SearchConfig, TimeRangeOption, SubredditOption } from '@/types';

export const SEARCH_CONFIG: SearchConfig = {
  defaultTimeRange: '1d',
  defaultPostCount: 20,
  maxPostCount: 100,
  minUpvotes: 10,
  minComments: 5,
  cacheTimeout: 300000, // 5 minutes in milliseconds
};

export const TIME_RANGE_OPTIONS: TimeRangeOption[] = [
  {
    value: '1h',
    label: '1 Hour',
    description: 'Posts from the last hour',
  },
  {
    value: '1d',
    label: '1 Day',
    description: 'Posts from the last day',
  },
  {
    value: '10d',
    label: '10 Days',
    description: 'Posts from the last 10 days',
  },
  {
    value: '100d',
    label: '100 Days',
    description: 'Posts from the last 100 days',
  },
];

export const AVAILABLE_SUBREDDITS: SubredditOption[] = [
  {
    name: 'AmItheAsshole',
    displayName: 'r/AmItheAsshole',
    description: 'Moral judgment stories',
    isPopular: true,
  },
  {
    name: 'relationship_advice',
    displayName: 'r/relationship_advice',
    description: 'Relationship guidance and stories',
    isPopular: true,
  },
  {
    name: 'tifu',
    displayName: 'r/tifu',
    description: 'Today I F***ed Up stories',
    isPopular: true,
  },
  {
    name: 'confession',
    displayName: 'r/confession',
    description: 'Personal confessions',
    isPopular: true,
  },
  {
    name: 'pettyrevenge',
    displayName: 'r/pettyrevenge',
    description: 'Small-scale revenge stories',
    isPopular: true,
  },
  {
    name: 'maliciouscompliance',
    displayName: 'r/maliciouscompliance',
    description: 'Following rules to the letter',
    isPopular: true,
  },
];

export const ERROR_MESSAGES = {
  REDDIT_API_UNAVAILABLE: 'Reddit service temporarily unavailable',
  RATE_LIMIT_EXCEEDED: 'Too many requests, please wait',
  NETWORK_ERROR: 'Connection error, please check your internet',
  VALIDATION_ERROR: 'Invalid search parameters',
  TIMEOUT_ERROR: 'Request timed out, please try again',
  NO_SUBREDDITS_SELECTED: 'Please select at least one subreddit',
  INVALID_POST_COUNT: 'Post count must be between 1 and 100',
} as const;
