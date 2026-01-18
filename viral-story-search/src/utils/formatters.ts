/**
 * Shared formatting utilities for the application.
 *
 * This module consolidates duplicate formatting functions that were previously
 * scattered across multiple components.
 */

import { StoryGenre } from '@/types';

/**
 * Format a genre enum value for display.
 * Converts MODERN_ROMANCE_DRAMA_MANHWA -> "MODERN ROMANCE DRAMA"
 *
 * @param genre - The StoryGenre enum value
 * @returns Formatted genre string for display
 */
export function formatGenreName(genre: StoryGenre): string {
  return genre.replace(/_/g, ' ').replace(/MANHWA/g, '').trim();
}

/**
 * Format a number for compact display.
 * Converts large numbers to shortened format (1000 -> 1.0k)
 *
 * @param num - The number to format
 * @returns Formatted number string
 */
export function formatNumber(num: number): string {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k';
  }
  return num.toString();
}

/**
 * Format a date as relative time (e.g., "5m ago", "2h ago", "3d ago")
 *
 * @param date - The date to format
 * @returns Relative time string
 */
export function formatRelativeTime(date: Date): string {
  const now = new Date();
  const postDate = new Date(date);
  const diffMs = now.getTime() - postDate.getTime();
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMinutes < 60) {
    return `${diffMinutes}m ago`;
  } else if (diffHours < 24) {
    return `${diffHours}h ago`;
  } else if (diffDays < 30) {
    return `${diffDays}d ago`;
  } else {
    const diffMonths = Math.floor(diffDays / 30);
    return `${diffMonths}mo ago`;
  }
}
