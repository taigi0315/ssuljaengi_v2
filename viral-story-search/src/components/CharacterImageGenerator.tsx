'use client';

import { useState, useEffect } from 'react';
import { WebtoonScript, Character, CharacterImage, ImageStyle } from '@/types';
import { generateCharacterImage, selectCharacterImage, saveCharacterToLibrary } from '@/lib/apiClient';
import { formatGenreName } from '@/utils/formatters';
import CharacterList from './CharacterList';

import CharacterImageDisplay from './CharacterImageDisplay';
import CharacterLibraryModal from './CharacterLibraryModal';

interface CharacterImageGeneratorProps {
  storyId: string;
  webtoonScript: WebtoonScript;
  imageStyle: ImageStyle;  // Required image style for rendering
  onUpdateScript?: (script: WebtoonScript) => void;
  onProceedToScenes?: () => void;
}

export default function CharacterImageGenerator({
  storyId,
  webtoonScript,
  imageStyle,
  onUpdateScript,
  onProceedToScenes
}: CharacterImageGeneratorProps) {
  // Use the passed script as source of truth
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLibraryOpen, setIsLibraryOpen] = useState(false);

  // Main Layout State
  const [libraryMode, setLibraryMode] = useState<'load' | 'reference'>('load');
  const [pendingGeneration, setPendingGeneration] = useState<{
        name: string;
        description: string;
        gender: string;
  } | null>(null);

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
        image_style: imageStyle,  // Use the selected image style
      });

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

  const handleGenerateWithReference = (name: string, description: string, gender: string) => {
      setPendingGeneration({ name, description, gender });
      setLibraryMode('reference');
      setIsLibraryOpen(true);
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

  const handleLoadCharacter = (saved: { character: Character, image_url?: string }) => {
    if (!selectedCharacter || !onUpdateScript || !webtoonScript) return;
    
    // Check mode
    if (libraryMode === 'reference' && saved.image_url && pendingGeneration) {
        // IMAGE-TO-IMAGE GENERATION MODE
        setIsLibraryOpen(false); // Close modal
        
        // Trigger generation with reference image
        setIsGeneratingImage(true);
        setError(null);
        
        import('@/lib/apiClient').then(({ generateCharacterImage }) => {
            generateCharacterImage({
                script_id: webtoonScript.script_id,
                character_name: pendingGeneration.name,
                description: pendingGeneration.description,
                gender: pendingGeneration.gender,
                image_style: imageStyle,
                reference_image_url: saved.image_url // Pass the reference image!
            }).then(image => {
                 if (onUpdateScript && webtoonScript) {
                    const charName = pendingGeneration.name;
                    const currentImages = { ...(webtoonScript.character_images || {}) };
                    if (!currentImages[charName]) {
                        currentImages[charName] = [];
                    }
                    currentImages[charName].push(image);
                    
                    onUpdateScript({
                        ...webtoonScript,
                        character_images: currentImages
                    });
                 }
            }).catch(err => {
                console.error("Failed to generate with reference:", err);
                setError("Failed to generate character with reference image");
            }).finally(() => {
                setIsGeneratingImage(false);
                setPendingGeneration(null);
                setLibraryMode('load'); // Reset mode
            });
        });
        return;
    }

    // NORMAL LOAD MODE
    // We want to apply the saved character's visual description (and maybe name?) to the CURRENT selected character in the script.
    
    const updatedCharacters = webtoonScript.characters.map(c => {
      if (c.name === selectedCharacter.name) {
        return {
          ...c,
          // Update visual traits
          gender: saved.character.gender,
          age: saved.character.age,
          face: saved.character.face,
          hair: saved.character.hair,
          body: saved.character.body,
          outfit: saved.character.outfit,
          visual_description: saved.character.visual_description,
          // Keep name
        };
      }
      return c;
    });

    // If there is an image, import it to get a valid backend ID
    if (saved.image_url) {
        const charName = selectedCharacter.name;
        
        import('@/lib/apiClient').then(({ importCharacterImage }) => {
            importCharacterImage(
                webtoonScript.script_id, 
                charName, 
                saved.image_url!, 
                saved.character.visual_description
            ).then(importedImage => {
                 if (onUpdateScript && webtoonScript) {
                     const currentImages = { ...(webtoonScript.character_images || {}) };
                     if (!currentImages[charName]) {
                         currentImages[charName] = [];
                     }
                     currentImages[charName].push(importedImage);
                     
                     onUpdateScript({
                         ...webtoonScript,
                         characters: updatedCharacters,
                         character_images: currentImages
                     });
                 }
            }).catch(err => {
                console.error("Failed to import character image:", err);
                setError("Failed to import character image reference");
            });
        });
    } else {
        // Just update characters if no image
        onUpdateScript({
          ...webtoonScript,
          characters: updatedCharacters,
        });
    }

    // Update local selection to trigger re-render
    const newSelected = updatedCharacters.find(c => c.name === selectedCharacter.name);
    if (newSelected) setSelectedCharacter(newSelected);
    
    setIsLibraryOpen(false);
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

  // Main layout
  return (
    <div className="space-y-6">
      {/* Image Style Badge - Always visible */}
      <div className="flex items-center justify-center gap-2 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
        <span className="text-sm font-semibold text-gray-700">Image Style:</span>
        <span className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-full text-sm font-bold shadow-md">
          🎨 {formatGenreName(imageStyle)}
        </span>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <span>🎨</span>
          <span>Character Image Generation</span>
        </h2>
        <div className="flex justify-between items-center mb-6">
            <p className="text-gray-600">
            Generate images for each character. Edit descriptions and regenerate as needed.
            </p>
            <button
            onClick={() => setIsLibraryOpen(true)}
            disabled={!selectedCharacter}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-50 hover:border-purple-300 transition-all text-gray-700 font-medium text-sm"
            >
            <span>📂</span>
            <span>Load Character Design</span>
            </button>
        </div>

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
                  onGenerateWithReference={handleGenerateWithReference} // Add this
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
      <CharacterLibraryModal
        isOpen={isLibraryOpen}
        onClose={() => setIsLibraryOpen(false)}
        onSelect={handleLoadCharacter}
      />
    </div>
  );
}
