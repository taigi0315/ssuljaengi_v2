// Application-wide constants shared across utils and components.

export const SEARCH_CONFIG = {
  defaultTimeRange: '1d',
  defaultPostCount: 10,
  maxPostCount: 100,
  minUpvotes: 100,
  minComments: 10,
  cacheTimeout: 300_000, // 5 minutes in ms
} as const;

export const ERROR_MESSAGES = {
  NO_SUBREDDITS_SELECTED: 'Please select at least one subreddit.',
  INVALID_POST_COUNT: `Post count must be between 1 and ${SEARCH_CONFIG.maxPostCount}.`,
  RATE_LIMIT_EXCEEDED: 'Reddit rate limit reached. Please wait a moment and try again.',
  REDDIT_API_UNAVAILABLE: 'Reddit API is currently unavailable. Please try again later.',
  NETWORK_ERROR: 'Network error. Please check your connection and try again.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
} as const;
