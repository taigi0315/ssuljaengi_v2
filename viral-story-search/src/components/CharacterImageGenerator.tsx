'use client';

import { useState, useEffect } from 'react';
import { WebtoonScript, Character, CharacterImage, StoryGenre } from '@/types';
import { generateCharacterImage, selectCharacterImage, saveCharacterToLibrary } from '@/lib/apiClient';
import CharacterList from './CharacterList';
import CharacterImageDisplay from './CharacterImageDisplay';

interface CharacterImageGeneratorProps {
  storyId: string;
  webtoonScript: WebtoonScript;
  genre?: StoryGenre;
  onUpdateScript?: (script: WebtoonScript) => void;
  onProceedToScenes?: () => void;
}

export default function CharacterImageGenerator({ 
  storyId, 
  webtoonScript,
  genre: propGenre, 
  onUpdateScript,
  onProceedToScenes 
}: CharacterImageGeneratorProps) {
  // Use the passed script as source of truth
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Get genre from prop or sessionStorage
  const [genre] = useState<StoryGenre>(
    propGenre || (typeof window !== 'undefined' 
      ? (sessionStorage.getItem('selectedGenre') as StoryGenre) || 'MODERN_ROMANCE_DRAMA_MANHWA'
      : 'MODERN_ROMANCE_DRAMA_MANHWA')
  );

  // Auto-select first character on mount
  useEffect(() => {
    if (webtoonScript.characters.length > 0 && !selectedCharacter) {
      setSelectedCharacter(webtoonScript.characters[0]);
    }
  }, [webtoonScript.characters, selectedCharacter]);

  const handleGenerateImage = async (
    characterName: string, 
    description: string, 
    gender: string
  ) => {
    if (!webtoonScript) return;

    try {
      setIsGeneratingImage(true);
      setError(null);

      const image = await generateCharacterImage({
        script_id: webtoonScript.script_id,
        character_name: characterName,
        description,
        gender,
        image_style: genre,  // Use the stored genre
      });

      // Update webtoon script with new image
      // Update webtoon script with new image
      if (webtoonScript && onUpdateScript) {
        const updatedImages = { ...webtoonScript.character_images };
        if (!updatedImages[characterName]) {
          updatedImages[characterName] = [];
        }
        updatedImages[characterName].push(image);

        const newScript = {
          ...webtoonScript,
          character_images: updatedImages,
        };
        onUpdateScript(newScript);
      }
    } catch (err) {
      console.error('Image generation error:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate character image');
    } finally {
      setIsGeneratingImage(false);
    }
  };

  const handleCharacterSelect = (character: Character) => {
    setSelectedCharacter(character);
  };

  const handleSelectImage = async (imageId: string) => {
    if (!webtoonScript) return;

    try {
      setError(null);
      
      // Call API to select image
      await selectCharacterImage(webtoonScript.script_id, imageId);
      
      // Update local state to reflect selection
      // Update script with new selection
      if (webtoonScript && onUpdateScript) {
        const updatedImages = { ...(webtoonScript.character_images || {}) };
        
        // Deselect all images for all characters, then select the chosen one
        Object.keys(updatedImages).forEach(charName => {
          updatedImages[charName] = updatedImages[charName].map(img => ({
            ...img,
            is_selected: img.id === imageId
          }));
        });
        
        const newScript = { ...webtoonScript, character_images: updatedImages };
        onUpdateScript(newScript);
      }
    } catch (err) {
      console.error('Select image error:', err);
      setError(err instanceof Error ? err.message : 'Failed to select image');
    }
  };



  // Error state - only for image generation errors
  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Image Generation Error
          </h2>
          <p className="text-red-600 mb-6">{error}</p>
          <button
            onClick={() => setError(null)}
            className="px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors"
          >
            Dismiss
          </button>
        </div>
      </div>
    );
  }

  // Helper to format genre for display
  const formatGenreName = (g: StoryGenre): string => {
    return g.replace(/_/g, ' ').replace(/MANHWA/g, '').trim();
  };

  // Main layout
  return (
    <div className="space-y-6">
      {/* Genre Badge - Always visible */}
      <div className="flex items-center justify-center gap-2 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
        <span className="text-sm font-semibold text-gray-700">Selected Genre:</span>
        <span className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-full text-sm font-bold shadow-md">
          🎭 {formatGenreName(genre)}
        </span>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <span>🎨</span>
          <span>Character Image Generation</span>
        </h2>
        <p className="text-gray-600 mb-6">
          Generate images for each character. Edit descriptions and regenerate as needed.
        </p>

        {webtoonScript && (
          <div className="flex gap-6">
            {/* Left side: Character List (30%) */}
            <div className="w-1/3">
              <CharacterList
                characters={webtoonScript.characters}
                characterImages={webtoonScript.character_images || {}}
                selectedCharacter={selectedCharacter}
                onCharacterSelect={handleCharacterSelect}
              />
            </div>

            {/* Right side: Image Display (70%) */}
            <div className="w-2/3">
              {selectedCharacter ? (
                <CharacterImageDisplay
                  character={selectedCharacter}
                  images={(webtoonScript.character_images || {})[selectedCharacter.name] || []}
                  onGenerateImage={handleGenerateImage}
                  onSelectImage={handleSelectImage}
                  isGenerating={isGeneratingImage}
                  onSaveToLibrary={async (char, imgUrl) => {
                    try {
                      await saveCharacterToLibrary(char, imgUrl);
                    } catch (err) {
                      console.error(err);
                      throw err; // Propagate to display for alert
                    }
                  }}
                />
              ) : (
                <div className="bg-gray-50 rounded-lg p-12 text-center">
                  <div className="text-6xl mb-4">👈</div>
                  <p className="text-gray-600">Select a character to generate images</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Error message */}
        {error && webtoonScript && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}
      </div>

      {/* Script Info */}
      {webtoonScript && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Script Details</h3>
          <div className="flex flex-wrap gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <span className="font-semibold">Characters:</span>
              <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded">
                {webtoonScript.characters.length}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold">Panels:</span>
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
                {webtoonScript.panels.length}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold">Images Generated:</span>
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded">
                {Object.values(webtoonScript.character_images || {}).reduce((sum, imgs) => sum + imgs.length, 0)}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Proceed to Scene Image Generation */}
      {onProceedToScenes && (
        <div className="mt-8 text-center">
          <button
            onClick={() => onProceedToScenes()}
            className="px-10 py-4 rounded-lg font-bold text-lg bg-gradient-to-r from-green-500 to-teal-500 text-white hover:shadow-xl hover:scale-105 transition-all"
          >
            🖼️ Proceed to Scene Images →
          </button>
          <p className="mt-2 text-sm text-gray-500">Generate images for each scene panel</p>
        </div>
      )}
    </div>
  );
}
