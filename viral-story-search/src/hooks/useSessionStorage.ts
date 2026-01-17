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
  // Initialize state with initialValue to match server-side rendering
  const [storedValue, setStoredValue] = useState<T>(initialValue);

  // Hydrate from storage after mount (client-side only)
  useEffect(() => {
    if (typeof window === 'undefined') return;

    try {
      const item = window.sessionStorage.getItem(key);
      if (item) {
        setStoredValue(JSON.parse(item));
      }
    } catch (error) {
      console.warn(`Error reading sessionStorage key "${key}":`, error);
    }
  }, [key]);

  // Setter function that updates both state and storage
  const setValue = useCallback((value: T | ((prev: T) => T)) => {
    setStoredValue((prev) => {
      const nextValue = value instanceof Function ? value(prev) : value;
      
      if (typeof window !== 'undefined') {
        try {
          if (nextValue === null || nextValue === undefined) {
            window.sessionStorage.removeItem(key);
          } else {
            window.sessionStorage.setItem(key, JSON.stringify(nextValue));
          }
        } catch (error) {
          console.warn(`Error saving to sessionStorage key "${key}":`, error);
        }
      }
      
      return nextValue;
    });
  }, [key]);

  // Clear function to remove from storage
  const clearValue = useCallback(() => {
    setStoredValue(initialValue);
    if (typeof window !== 'undefined') {
      try {
        window.sessionStorage.removeItem(key);
      } catch (error) {
        console.warn(`Error clearing sessionStorage key "${key}":`, error);
      }
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
