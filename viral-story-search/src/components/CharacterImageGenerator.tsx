'use client';

import { useState, useEffect } from 'react';
import { WebtoonScript, Character, CharacterImage } from '@/types';
import { generateWebtoonScript, generateCharacterImage } from '@/lib/apiClient';
import CharacterList from './CharacterList';
import CharacterImageDisplay from './CharacterImageDisplay';

interface CharacterImageGeneratorProps {
  storyId: string;
}

export default function CharacterImageGenerator({ storyId }: CharacterImageGeneratorProps) {
  const [webtoonScript, setWebtoonScript] = useState<WebtoonScript | null>(null);
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [isGeneratingScript, setIsGeneratingScript] = useState(false);
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generate webtoon script on mount
  useEffect(() => {
    generateScript();
  }, [storyId]);

  const generateScript = async () => {
    try {
      setIsGeneratingScript(true);
      setError(null);

      const script = await generateWebtoonScript(storyId);
      setWebtoonScript(script);

      // Auto-select first character
      if (script.characters.length > 0) {
        setSelectedCharacter(script.characters[0]);
      }
    } catch (err) {
      console.error('Script generation error:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate webtoon script');
    } finally {
      setIsGeneratingScript(false);
    }
  };

  const handleGenerateImage = async (characterName: string, description: string) => {
    if (!webtoonScript) return;

    try {
      setIsGeneratingImage(true);
      setError(null);

      const image = await generateCharacterImage({
        script_id: webtoonScript.script_id,
        character_name: characterName,
        description,
      });

      // Update webtoon script with new image
      setWebtoonScript(prev => {
        if (!prev) return prev;

        const updatedImages = { ...prev.character_images };
        if (!updatedImages[characterName]) {
          updatedImages[characterName] = [];
        }
        updatedImages[characterName].push(image);

        return {
          ...prev,
          character_images: updatedImages,
        };
      });
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

  // Loading state
  if (isGeneratingScript) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mb-4"></div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Converting Story to Webtoon Script...
          </h2>
          <p className="text-gray-600">
            Analyzing characters and breaking down scenes
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !webtoonScript) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          <div className="text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Script Generation Failed
          </h2>
          <p className="text-red-600 mb-6">{error}</p>
          <button
            onClick={generateScript}
            className="px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Main layout
  return (
    <div className="space-y-6">
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
                characterImages={webtoonScript.character_images}
                selectedCharacter={selectedCharacter}
                onCharacterSelect={handleCharacterSelect}
              />
            </div>

            {/* Right side: Image Display (70%) */}
            <div className="w-2/3">
              {selectedCharacter ? (
                <CharacterImageDisplay
                  character={selectedCharacter}
                  images={webtoonScript.character_images[selectedCharacter.name] || []}
                  onGenerateImage={handleGenerateImage}
                  isGenerating={isGeneratingImage}
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
                {Object.values(webtoonScript.character_images).reduce((sum, imgs) => sum + imgs.length, 0)}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
