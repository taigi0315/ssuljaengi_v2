'use client';

import { StoryGenre, StoryGenreOption } from '@/types';
import Image from 'next/image';

// Import genre preview images
import modernRomanceImage from '@/assets/images/genre/MODERN_ROMANCE_DRAMA_MANHWA.png';
import fantasyRomanceImage from '@/assets/images/genre/FANTASY_ROMANCE_MANHWA.png';
import historySageukImage from '@/assets/images/genre/HISTORY_SAGEUK_ROMANCE.png';
import academySchoolImage from '@/assets/images/genre/ACADEMY_SCHOOL_LIFE.png';
import isekaiOtomeImage from '@/assets/images/genre/ISEKAI_OTOME_FANTASY.png';

interface GenreSelectorProps {
  selectedGenre: StoryGenre | null;
  onGenreSelect: (genre: StoryGenre) => void;
}

const GENRE_OPTIONS: StoryGenreOption[] = [
  {
    id: 'MODERN_ROMANCE_DRAMA_MANHWA',
    name: 'Modern Romance Drama',
    description: 'Contemporary Korean romance drama with emotional depth',
    previewImage: modernRomanceImage.src,
  },
  {
    id: 'FANTASY_ROMANCE_MANHWA',
    name: 'Fantasy Romance',
    description: 'Magical academy or mystical world romance',
    previewImage: fantasyRomanceImage.src,
  },
  {
    id: 'HISTORY_SAGEUK_ROMANCE',
    name: 'Historical Romance',
    description: 'Elegant sageuk style with dramatic lighting',
    previewImage: historySageukImage.src,
  },
  {
    id: 'ACADEMY_SCHOOL_LIFE',
    name: 'School Life',
    description: 'Contemporary high school or university romance',
    previewImage: academySchoolImage.src,
  },
  {
    id: 'ISEKAI_OTOME_FANTASY',
    name: 'Isekai Otome Fantasy',
    description: 'Reincarnation/transmigration into fantasy world',
    previewImage: isekaiOtomeImage.src,
  },
];

export default function GenreSelector({ selectedGenre, onGenreSelect }: GenreSelectorProps) {
  return (
    <div className="space-y-4">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Choose Your Story Genre
        </h2>
        <p className="text-gray-600">
          Select the style and tone for your webtoon story
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {GENRE_OPTIONS.map((genre) => (
          <button
            key={genre.id}
            onClick={() => onGenreSelect(genre.id)}
            className={`
              relative overflow-hidden rounded-lg border-2 transition-all
              ${selectedGenre === genre.id
                ? 'border-purple-600 ring-2 ring-purple-600 ring-offset-2 scale-105'
                : 'border-gray-300 hover:border-purple-400 hover:shadow-md'
              }
            `}
          >
            {/* Preview Image */}
            <div className="aspect-[3/4] bg-gray-100">
              <img
                src={genre.previewImage}
                alt={genre.name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="133"%3E%3Crect fill="%23ddd" width="100" height="133"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999"%3EGenre%3C/text%3E%3C/svg%3E';
                }}
              />
            </div>
            
            {/* Genre Info */}
            <div className="p-3 bg-white">
              <p className="text-sm font-bold text-gray-900 text-center">
                {genre.name}
              </p>
              <p className="text-xs text-gray-600 text-center mt-1 line-clamp-2">
                {genre.description}
              </p>
            </div>

            {/* Selected Indicator */}
            {selectedGenre === genre.id && (
              <div className="absolute top-2 right-2 bg-purple-600 text-white rounded-full p-1">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
