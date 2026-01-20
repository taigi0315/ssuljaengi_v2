'use client';

import { StoryGenre, StoryGenreOption } from '@/types';
import { useState, useEffect, useRef } from 'react';
import { getGenres } from '@/lib/apiClient';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import Image from 'next/image';

// Import genre preview images
// Import genre preview images
import modernRomanceImage from '@/assets/images/genre/MODERN_ROMANCE_DRAMA_MANHWA.png';
import fantasyRomanceImage from '@/assets/images/genre/FANTASY_ROMANCE_MANHWA.png';
import historySageukImage from '@/assets/images/genre/HISTORY_SAGEUK_ROMANCE.png';
import academySchoolImage from '@/assets/images/genre/ACADEMY_SCHOOL_LIFE.png';
import isekaiOtomeImage from '@/assets/images/genre/ISEKAI_OTOME_FANTASY.png';
import darkRomanceImage from '@/assets/images/genre/DARK_ROMANCE_REVENGE_MANHWA.png'; // New Image
import noGenreImage from '@/assets/images/genre/NO_GENRE.png'; // New Image

interface GenreSelectorProps {
  selectedGenre: StoryGenre | null;
  onGenreSelect: (genre: StoryGenre) => void;
}

const GENRE_METADATA: Record<string, { name: string; description: string; previewImage: string }> = {
  MODERN_ROMANCE_DRAMA: {
    name: 'Modern Romance Drama',
    description: 'Contemporary Korean romance drama with emotional depth',
    previewImage: modernRomanceImage.src,
  },
  FANTASY_ROMANCE: {
    name: 'Fantasy Romance',
    description: 'Magical academy or mystical world romance',
    previewImage: fantasyRomanceImage.src,
  },
  HISTORICAL_PERIOD_ROMANCE: {
    name: 'Historical Romance',
    description: 'Elegant sageuk style with dramatic lighting',
    previewImage: historySageukImage.src,
  },
  SCHOOL_YOUTH_ROMANCE: {
    name: 'School Life',
    description: 'Contemporary high school or university romance',
    previewImage: academySchoolImage.src,
  },
  REINCARNATION_FANTASY: {
    name: 'Isekai Otome Fantasy',
    description: 'Slow-burn tender feeling with light comedic palace fantasy touch',
    previewImage: isekaiOtomeImage.src,
  },
  DARK_OBSESSIVE_ROMANCE: {
    name: 'Dark Obsessive Romance',
    description: 'Intense, vengeful passion involving seduction or entrapment',
    previewImage: darkRomanceImage.src,
  },
  WORKPLACE_ROMANCE: {
    name: 'Workplace Romance',
    description: 'Office romance with professional tension',
    previewImage: modernRomanceImage.src, // Reusing modern romance image
  },
  CHILDHOOD_FRIENDS_TO_LOVERS: {
    name: 'Friends to Lovers',
    description: 'Long friendship evolving into romance',
    previewImage: academySchoolImage.src, // Reusing school image
  },
  NO_GENRE: {
    name: 'Free Style',
    description: 'No specific genre restrictions. Create your own unique story!',
    previewImage: noGenreImage.src,
  },
};


// Fallback image for new genres
const DEFAULT_GENRE_IMAGE = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="400"%3E%3Crect fill="%23f3f4f6" width="300" height="400"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%239ca3af" font-family="sans-serif" font-size="24"%3EGenre%3C/text%3E%3C/svg%3E';

export default function GenreSelector({ selectedGenre, onGenreSelect }: GenreSelectorProps) {
  const [genres, setGenres] = useState<StoryGenreOption[]>([]);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  // Function to check scrollability
  const checkScrollability = () => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 1); // -1 for potential sub-pixel differences
    }
  };

  // Fetch dynamic genres from backend
  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const apiGenres = await getGenres();

        if (apiGenres && apiGenres.length > 0) {
          // Merge API genres with local metadata (images/descriptions)
          // tailored to preserve the rich assets we have, but include new ones

          const mergedGenres: StoryGenreOption[] = apiGenres.map(apiGenre => {
            // Find existing local definition to get image/desc
            const local = GENRE_METADATA[apiGenre.id as StoryGenre];

            return {
              id: apiGenre.id as StoryGenre,
              name: local?.name || apiGenre.name, // Use local name if available (might have better formatting), else API
              description: local?.description || 'Exploring this new genre...',
              previewImage: local?.previewImage || DEFAULT_GENRE_IMAGE
            };
          });

          setGenres(mergedGenres);
        } else {
          // If API returns no genres, use a default set from metadata
          setGenres(Object.entries(GENRE_METADATA).map(([id, data]) => ({ id: id as StoryGenre, ...data })));
        }
      } catch (err) {
        console.error("Using static genres due to fetch error", err);
        // Fallback to local metadata if API fails
        setGenres(Object.entries(GENRE_METADATA).map(([id, data]) => ({ id: id as StoryGenre, ...data })));
      }
    };

    fetchGenres();
  }, []);

  useEffect(() => {
    // Check scrollability after genres are loaded and rendered
    checkScrollability();
    const container = scrollContainerRef.current;
    if (container) {
      container.addEventListener('scroll', checkScrollability);
      window.addEventListener('resize', checkScrollability);
      return () => {
        container.removeEventListener('scroll', checkScrollability);
        window.removeEventListener('resize', checkScrollability);
      };
    }
  }, [genres]); // Re-run when genres change

  const scroll = (direction: 'left' | 'right') => {
    if (scrollContainerRef.current) {
      const scrollAmount = 300; // Approx card width + gap
      const currentScroll = scrollContainerRef.current.scrollLeft;
      const targetScroll = direction === 'left'
        ? currentScroll - scrollAmount
        : currentScroll + scrollAmount;

      scrollContainerRef.current.scrollTo({
        left: targetScroll,
        behavior: 'smooth'
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Choose Your Story Genre
        </h2>
        <p className="text-gray-600">
          Select the style and tone for your webtoon story
        </p>
      </div>

      <div className="relative group px-4">
        {/* Left Arrow */}
        {canScrollLeft && (
          <button
            onClick={() => scroll('left')}
            className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-50 bg-white/90 p-3 rounded-full shadow-xl hover:bg-white transition-all hover:scale-110 active:scale-95 border border-purple-100"
            aria-label="Scroll left"
          >
            <ChevronLeft className="w-8 h-8 text-purple-600" />
          </button>
        )}

        {/* Right Arrow */}
        {canScrollRight && (
          <button
            onClick={() => scroll('right')}
            className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-50 bg-white/90 p-3 rounded-full shadow-xl hover:bg-white transition-all hover:scale-110 active:scale-95 border border-purple-100"
            aria-label="Scroll right"
          >
            <ChevronRight className="w-8 h-8 text-purple-600" />
          </button>
        )}

        {/* Carousel Container */}
        <div 
            ref={scrollContainerRef}
            className="flex overflow-x-auto gap-5 py-4 px-2 scrollbar-hide snap-x"
            style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
        {genres.map((genre) => (
          <div
            key={genre.id}
            onClick={() => onGenreSelect(genre.id)}
            className={`
              flex-shrink-0 w-[200px] md:w-[220px] snap-center
              relative overflow-hidden rounded-xl border-2 transition-all duration-300
              flex flex-col text-left group/card cursor-pointer
              ${selectedGenre === genre.id
                ? 'border-purple-600 ring-4 ring-purple-100 scale-105 shadow-xl z-10'
                : 'border-transparent hover:border-purple-200 hover:scale-105 hover:shadow-lg shadow-md bg-white'
              }
            `}
          >
            {/* Preview Image */}
            <div className="aspect-[3/4] bg-gray-100 relative overflow-hidden">
              <img
                src={genre.previewImage}
                alt={genre.name}
                className={`w-full h-full object-cover transition-transform duration-500 ${selectedGenre === genre.id ? 'scale-110' : 'group-hover/card:scale-110'}`}
                onError={(e) => {
                  e.currentTarget.src = DEFAULT_GENRE_IMAGE;
                }}
              />
              {/* Gradient Overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-90" />
              
              {/* Text Overlay (Bottom) */}
              <div className="absolute bottom-0 left-0 right-0 p-4 transform transition-transform">
                <p className={`text-white font-bold text-lg leading-tight mb-1 ${selectedGenre === genre.id ? 'text-purple-200' : ''}`}>
                    {genre.name}
                </p>
                {selectedGenre === genre.id && (
                    <p className="text-white/80 text-xs line-clamp-3 animate-fadeIn">
                        {genre.description}
                    </p>
                )}
              </div>
              
              {/* Selected Checkmark */}
              {selectedGenre === genre.id && (
                <div className="absolute top-3 right-3 bg-purple-600 rounded-full p-1 shadow-lg animate-scaleIn">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              )}
            </div>
          </div>
        ))}
        </div>
      </div>
    </div>
  );
}
