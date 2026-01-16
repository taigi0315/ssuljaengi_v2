'use client';

import { StoryMood, StoryMoodOption } from '@/types';

interface MoodSelectorProps {
  selectedMood: StoryMood | null;
  onMoodSelect: (mood: StoryMood) => void;
}

const MOOD_OPTIONS: StoryMoodOption[] = [
  {
    id: 'rofan',
    name: 'RoFan (Romance Fantasy)',
    emoji: '👑',
    description: 'Duke/Duchess/Princess stories with European aristocracy vibes',
  },
  {
    id: 'modern_romance',
    name: 'Modern Romance (K-Drama)',
    emoji: '💕',
    description: 'High-end, glossy urban romance with heart-fluttering moments',
  },
  {
    id: 'slice_of_life',
    name: 'Slice of Life / Healing',
    emoji: '🌿',
    description: 'Cozy, warm, and comforting stories with gentle pacing',
  },
  {
    id: 'revenge',
    name: 'Revenge & Glow-up (Cider)',
    emoji: '⚡',
    description: 'Satisfying transformation and power moves',
  },
  {
    id: 'high_teen',
    name: 'High Teen / Preppy (Academy)',
    emoji: '🎓',
    description: 'Elite school drama with gossip and hierarchy',
  },
];

export default function MoodSelector({ selectedMood, onMoodSelect }: MoodSelectorProps) {
  return (
    <div className="space-y-4">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Choose Your Story Mood
        </h2>
        <p className="text-gray-600">
          Select the style and tone for your webtoon story
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {MOOD_OPTIONS.map((mood) => (
          <button
            key={mood.id}
            onClick={() => onMoodSelect(mood.id)}
            className={`
              p-6 rounded-lg border-2 transition-all text-left
              ${selectedMood === mood.id
                ? 'border-purple-600 bg-purple-50 shadow-lg scale-105'
                : 'border-gray-200 bg-white hover:border-purple-300 hover:shadow-md'
              }
            `}
          >
            <div className="flex items-start gap-3">
              <span className="text-4xl">{mood.emoji}</span>
              <div className="flex-1">
                <h3 className="font-bold text-gray-900 mb-1 text-sm sm:text-base">
                  {mood.name}
                </h3>
                <p className="text-xs sm:text-sm text-gray-600">
                  {mood.description}
                </p>
              </div>
              {selectedMood === mood.id && (
                <div className="flex-shrink-0">
                  <div className="w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">✓</span>
                  </div>
                </div>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
