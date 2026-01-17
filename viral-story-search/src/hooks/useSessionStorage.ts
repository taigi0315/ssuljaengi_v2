'use client';

import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for persisting state to sessionStorage.
 * Automatically saves state changes and restores on mount.
 */
export function useSessionStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void, () => void] {
  // Initialize state
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }
    try {
      const item = window.sessionStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading sessionStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Update sessionStorage when state changes
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    try {
      if (storedValue === null || storedValue === undefined) {
        window.sessionStorage.removeItem(key);
      } else {
        window.sessionStorage.setItem(key, JSON.stringify(storedValue));
      }
    } catch (error) {
      console.warn(`Error saving to sessionStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  // Setter function that matches useState API
  const setValue = useCallback((value: T | ((prev: T) => T)) => {
    setStoredValue((prev) => {
      const nextValue = value instanceof Function ? value(prev) : value;
      return nextValue;
    });
  }, []);

  // Clear function to remove from storage
  const clearValue = useCallback(() => {
    setStoredValue(initialValue);
    if (typeof window !== 'undefined') {
      window.sessionStorage.removeItem(key);
    }
  }, [key, initialValue]);

  return [storedValue, setValue, clearValue];
}

/**
 * Session storage keys for the app
 */
export const SESSION_KEYS = {
  SELECTED_POST: 'gossiptoon_selectedPost',
  CUSTOM_STORY_SEED: 'gossiptoon_customStorySeed',
  SELECTED_GENRE: 'gossiptoon_selectedGenre',
  GENERATED_STORY_ID: 'gossiptoon_generatedStoryId',
  WEBTOON_SCRIPT: 'gossiptoon_webtoonScript',
  CHARACTER_IMAGES: 'gossiptoon_characterImages',
  SCENE_IMAGES: 'gossiptoon_sceneImages',
  ACTIVE_TAB: 'gossiptoon_activeTab',
} as const;
