'use client';

import { ImageStyle, ImageStyleOption } from '@/types';
import { useState, useEffect, useRef } from 'react';
import { getImageStyles } from '@/lib/apiClient';
import { ChevronLeft, ChevronRight, Palette } from 'lucide-react';

// Import style preview images
import softRomanticImage from '@/assets/images/image_styles/SOFT_ROMANTIC_WEBTOON.png';
import vibrantFantasyImage from '@/assets/images/image_styles/VIBRANT_FANTASY_WEBTOON.png';
import dramaticHistoricalImage from '@/assets/images/image_styles/DRAMATIC_HISTORICAL_WEBTOON.png';
import brightYouthfulImage from '@/assets/images/image_styles/BRIGHT_YOUTHFUL_WEBTOON.png';
import dreamyIsekaiImage from '@/assets/images/image_styles/DREAMY_ISEKAI_WEBTOON.png';
import darkSensualImage from '@/assets/images/image_styles/DARK_SENSUAL_WEBTOON.png';
import cleanModernImage from '@/assets/images/image_styles/CLEAN_MODERN_WEBTOON.png';
import painterlyArtisticImage from '@/assets/images/image_styles/PAINTERLY_ARTISTIC_WEBTOON.png';
import emotiveLuxuryImage from '@/assets/images/image_styles/EMOTIVE_LUXURY_WEBTOON.png';

interface ImageStyleSelectorProps {
  selectedStyle: ImageStyle | null;
  onStyleSelect: (style: ImageStyle) => void;
}

// Metadata for image styles with placeholder colors/gradients
const IMAGE_STYLE_METADATA: Record<string, { name: string; description: string; gradient: string; icon: string; previewImage?: string }> = {
  NO_STYLE: {
    name: 'Default Style',
    description: 'Default AI rendering without specific style',
    gradient: 'from-gray-400 to-gray-600',
    icon: '🎨',
  },
  SOFT_ROMANTIC_WEBTOON: {
    name: 'Soft Romantic',
    description: 'Gentle, dreamy, light-filled, ethereal aesthetic',
    gradient: 'from-pink-300 via-rose-200 to-amber-100',
    icon: '🌸',
    previewImage: softRomanticImage.src,
  },
  VIBRANT_FANTASY_WEBTOON: {
    name: 'Vibrant Fantasy',
    description: 'Magical, bright, enchanting, colorful style',
    gradient: 'from-purple-400 via-pink-300 to-blue-400',
    icon: '✨',
    previewImage: vibrantFantasyImage.src,
  },
  DRAMATIC_HISTORICAL_WEBTOON: {
    name: 'Dramatic Historical',
    description: 'Moody, elegant, dramatic, candlelit atmosphere',
    gradient: 'from-amber-700 via-red-800 to-stone-900',
    icon: '🕯️',
    previewImage: dramaticHistoricalImage.src,
  },
  BRIGHT_YOUTHFUL_WEBTOON: {
    name: 'Bright Youthful',
    description: 'Fresh, clean, optimistic, energetic feel',
    gradient: 'from-sky-300 via-yellow-200 to-orange-300',
    icon: '☀️',
    previewImage: brightYouthfulImage.src,
  },
  DREAMY_ISEKAI_WEBTOON: {
    name: 'Dreamy Isekai',
    description: 'Ethereal, whimsical, romantic fantasy glow',
    gradient: 'from-indigo-300 via-purple-200 to-pink-200',
    icon: '🌙',
    previewImage: dreamyIsekaiImage.src,
  },
  DARK_SENSUAL_WEBTOON: {
    name: 'Dark Sensual',
    description: 'Intense, dramatic, intimate, mysterious mood',
    gradient: 'from-red-900 via-purple-900 to-black',
    icon: '🖤',
    previewImage: darkSensualImage.src,
  },
  CLEAN_MODERN_WEBTOON: {
    name: 'Clean Modern',
    description: 'Professional, versatile, commercial standard',
    gradient: 'from-slate-300 via-gray-200 to-zinc-300',
    icon: '💎',
    previewImage: cleanModernImage.src,
  },
  PAINTERLY_ARTISTIC_WEBTOON: {
    name: 'Painterly Artistic',
    description: 'Artistic, expressive, fine art quality',
    gradient: 'from-teal-400 via-emerald-300 to-cyan-400',
    icon: '🎭',
    previewImage: painterlyArtisticImage.src,
  },
  EMOTIVE_LUXURY_WEBTOON: {
    name: 'Emotive Luxury',
    description: 'High-end, detailed, emotional, polished webtoon aesthetic',
    gradient: 'from-rose-400 via-fuchsia-500 to-indigo-600',
    icon: '👑',
    previewImage: emotiveLuxuryImage.src,
  },
};

export default function ImageStyleSelector({ selectedStyle, onStyleSelect }: ImageStyleSelectorProps) {
  const [styles, setStyles] = useState<ImageStyleOption[]>([]);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  // Function to check scrollability
  const checkScrollability = () => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 1);
    }
  };

  // Fetch dynamic styles from backend
  useEffect(() => {
    const fetchStyles = async () => {
      try {
        const apiStyles = await getImageStyles();

        if (apiStyles && apiStyles.length > 0) {
          const mergedStyles: ImageStyleOption[] = apiStyles.map(apiStyle => {
            const local = IMAGE_STYLE_METADATA[apiStyle.id as ImageStyle];

            return {
              id: apiStyle.id as ImageStyle,
              name: local?.name || apiStyle.name,
              description: local?.description || apiStyle.description || 'Visual style for webtoon art',
              previewImage: local?.previewImage || apiStyle.preview_url || '',
            };
          });

          setStyles(mergedStyles);
        } else {
          // Fallback to local metadata
          setStyles(Object.entries(IMAGE_STYLE_METADATA).map(([id, data]) => ({
            id: id as ImageStyle,
            name: data.name,
            description: data.description,
            previewImage: '',
          })));
        }
      } catch (err) {
        console.error("Using static styles due to fetch error", err);
        setStyles(Object.entries(IMAGE_STYLE_METADATA).map(([id, data]) => ({
          id: id as ImageStyle,
          name: data.name,
          description: data.description,
          previewImage: data.previewImage || '',
        })));
      }
    };

    fetchStyles();
  }, []);

  useEffect(() => {
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
  }, [styles]);

  const scroll = (direction: 'left' | 'right') => {
    if (scrollContainerRef.current) {
      const scrollAmount = 300;
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
        <div className="flex items-center justify-center gap-2 mb-2">
          <Palette className="w-6 h-6 text-purple-600" />
          <h2 className="text-2xl font-bold text-gray-900">
            Choose Your Image Style
          </h2>
        </div>
        <p className="text-gray-600">
          Select the visual rendering style for your character and scene images
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
          {styles.map((style) => {
            const meta = IMAGE_STYLE_METADATA[style.id];
            const gradientClass = meta?.gradient || 'from-gray-400 to-gray-600';
            const icon = meta?.icon || '🎨';

            return (
              <div
                key={style.id}
                onClick={() => onStyleSelect(style.id)}
                className={`
                  flex-shrink-0 w-[200px] md:w-[220px] snap-center
                  relative overflow-hidden rounded-xl border-2 transition-all duration-300
                  flex flex-col text-left group/card cursor-pointer
                  ${selectedStyle === style.id
                    ? 'border-purple-600 ring-4 ring-purple-100 scale-105 shadow-xl z-10'
                    : 'border-transparent hover:border-purple-200 hover:scale-105 hover:shadow-lg shadow-md bg-white'
                  }
                `}
              >
                {/* Gradient Preview (placeholder for image) */}
                <div className={`aspect-[3/4] relative overflow-hidden bg-gradient-to-br ${gradientClass}`}>
                  {/* Icon Overlay */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-6xl opacity-30">{icon}</span>
                  </div>

                  {/* Actual image if available */}
                  {style.previewImage && (
                    <>
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={style.previewImage}
                        alt={style.name}
                        className={`absolute inset-0 w-full h-full object-cover transition-transform duration-500 ${selectedStyle === style.id ? 'scale-110' : 'group-hover/card:scale-110'}`}
                        onError={(e) => {
                          // Hide image on error, show gradient instead
                          e.currentTarget.style.display = 'none';
                        }}
                      />
                    </>
                  )}

                  {/* Gradient Overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-90" />

                  {/* Text Overlay (Bottom) */}
                  <div className="absolute bottom-0 left-0 right-0 p-4 transform transition-transform">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xl">{icon}</span>
                      <p className={`text-white font-bold text-lg leading-tight ${selectedStyle === style.id ? 'text-purple-200' : ''}`}>
                        {style.name}
                      </p>
                    </div>
                    {selectedStyle === style.id && (
                      <p className="text-white/80 text-xs line-clamp-3 animate-fadeIn">
                        {style.description}
                      </p>
                    )}
                  </div>

                  {/* Selected Checkmark */}
                  {selectedStyle === style.id && (
                    <div className="absolute top-3 right-3 bg-purple-600 rounded-full p-1 shadow-lg animate-scaleIn">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Style Info */}
      {selectedStyle && (
        <div className="bg-purple-50 rounded-lg p-4 border border-purple-100">
          <p className="text-sm text-purple-800">
            <span className="font-semibold">Selected Style:</span>{' '}
            {IMAGE_STYLE_METADATA[selectedStyle]?.name || selectedStyle}
          </p>
          <p className="text-xs text-purple-600 mt-1">
            {IMAGE_STYLE_METADATA[selectedStyle]?.description || 'Visual style for your webtoon images'}
          </p>
        </div>
      )}
    </div>
  );
}
