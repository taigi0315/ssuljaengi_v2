'use client';

import { Character, CharacterImage } from '@/types';

interface CharacterListProps {
  characters: Character[];
  characterImages: Record<string, CharacterImage[]>;
  selectedCharacter: Character | null;
  onCharacterSelect: (character: Character) => void;
}

export default function CharacterList({
  characters,
  characterImages,
  selectedCharacter,
  onCharacterSelect,
}: CharacterListProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Characters</h3>
      
      {characters.map((character) => {
        const imageCount = characterImages[character.name]?.length || 0;
        const isSelected = selectedCharacter?.name === character.name;

        return (
          <button
            key={character.name}
            onClick={() => onCharacterSelect(character)}
            className={`
              w-full text-left p-4 rounded-lg border-2 transition-all
              ${isSelected
                ? 'border-purple-600 bg-purple-50'
                : 'border-gray-200 bg-white hover:border-purple-300 hover:bg-purple-50'
              }
            `}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-1">
                  {character.name}
                </h4>
                <p className="text-xs text-gray-600 line-clamp-2">
                  {character.visual_description}
                </p>
              </div>
              
              {/* Image count badge */}
              {imageCount > 0 && (
                <div className="ml-2 flex-shrink-0">
                  <span className="inline-flex items-center justify-center w-8 h-8 bg-green-100 text-green-700 rounded-full text-xs font-bold">
                    {imageCount}
                  </span>
                </div>
              )}
            </div>

            {/* Status indicator */}
            <div className="mt-2 flex items-center gap-2">
              {imageCount === 0 ? (
                <span className="text-xs text-gray-500 flex items-center gap-1">
                  <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                  No images yet
                </span>
              ) : (
                <span className="text-xs text-green-600 flex items-center gap-1">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  {imageCount} {imageCount === 1 ? 'image' : 'images'}
                </span>
              )}
            </div>
          </button>
        );
      })}
    </div>
  );
}
