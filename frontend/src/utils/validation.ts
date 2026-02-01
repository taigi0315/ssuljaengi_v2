import { SearchCriteria, SearchRequest } from '@/types';
import { SEARCH_CONFIG, ERROR_MESSAGES } from '@/lib/constants';

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

/**
 * Validate search criteria
 */
export function validateSearchCriteria(
  criteria: SearchCriteria
): ValidationResult {
  const errors: string[] = [];

  // Validate subreddits
  if (!criteria.subreddits || criteria.subreddits.length === 0) {
    errors.push(ERROR_MESSAGES.NO_SUBREDDITS_SELECTED);
  }

  // Validate post count
  if (
    criteria.postCount < 1 ||
    criteria.postCount > SEARCH_CONFIG.maxPostCount
  ) {
    errors.push(ERROR_MESSAGES.INVALID_POST_COUNT);
  }

  // Validate time range
  const validTimeRanges = ['1h', '1d', '10d', '100d'];
  if (!validTimeRanges.includes(criteria.timeRange)) {
    errors.push('Invalid time range selected');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validate post count input
 */
export function validatePostCount(count: number): string | null {
  if (isNaN(count) || count < 1) {
    return 'Post count must be at least 1';
  }

  if (count > SEARCH_CONFIG.maxPostCount) {
    return `Post count cannot exceed ${SEARCH_CONFIG.maxPostCount}`;
  }

  return null;
}

/**
 * Validate search request from API
 */
export function validateSearchRequest(request: SearchRequest): string | null {
  // Check if request body exists
  if (!request) {
    return 'Request body is required';
  }

  // Validate subreddits
  if (!request.subreddits || !Array.isArray(request.subreddits) || request.subreddits.length === 0) {
    return ERROR_MESSAGES.NO_SUBREDDITS_SELECTED;
  }

  // Validate each subreddit name
  for (const subreddit of request.subreddits) {
    if (typeof subreddit !== 'string' || subreddit.trim().length === 0) {
      return 'All subreddit names must be non-empty strings';
    }
  }

  // Validate post count
  if (typeof request.postCount !== 'number' || isNaN(request.postCount)) {
    return 'Post count must be a valid number';
  }

  if (request.postCount < 1 || request.postCount > SEARCH_CONFIG.maxPostCount) {
    return ERROR_MESSAGES.INVALID_POST_COUNT;
  }

  // Validate time range
  const validTimeRanges = ['1h', '1d', '10d', '100d'];
  if (!request.timeRange || !validTimeRanges.includes(request.timeRange)) {
    return 'Invalid time range. Must be one of: 1h, 1d, 10d, 100d';
  }

  return null; // No validation errors
}
