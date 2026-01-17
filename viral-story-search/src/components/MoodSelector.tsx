'use client';

import { StoryGenre, StoryGenreOption } from '@/types';

interface MoodSelectorProps {
  selectedMood: StoryGenre | null;
  onMoodSelect: (mood: StoryGenre) => void;
}

const MOOD_OPTIONS: StoryGenreOption[] = [
  {
    id: 'MODERN_ROMANCE_DRAMA_MANHWA',
    name: 'Modern Romance Drama',
    description: 'Contemporary Korean romance with emotional depth',
    previewImage: '',
  },
  {
    id: 'FANTASY_ROMANCE_MANHWA',
    name: 'Fantasy Romance',
    description: 'Magical academy or mystical world romance',
    previewImage: '',
  },
  {
    id: 'HISTORY_SAGEUK_ROMANCE',
    name: 'Historical Romance',
    description: 'Elegant sageuk style with dramatic lighting',
    previewImage: '',
  },
  {
    id: 'ACADEMY_SCHOOL_LIFE',
    name: 'School Life',
    description: 'Contemporary high school or university romance',
    previewImage: '',
  },
  {
    id: 'ISEKAI_OTOME_FANTASY',
    name: 'Isekai Otome Fantasy',
    description: 'Reincarnation/transmigration into fantasy world',
    previewImage: '',
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
