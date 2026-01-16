'use client';

import { useState } from 'react';
import { Character, CharacterImage } from '@/types';

interface CharacterImageDisplayProps {
  character: Character;
  images: CharacterImage[];
  onGenerateImage: (characterName: string, description: string) => Promise<void>;
  isGenerating: boolean;
}

export default function CharacterImageDisplay({
  character,
  images,
  onGenerateImage,
  isGenerating,
}: CharacterImageDisplayProps) {
  const [description, setDescription] = useState(character.visual_description);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  const handleGenerate = async () => {
    await onGenerateImage(character.name, description);
    // After generating, show the newest image
    setCurrentImageIndex(images.length);
  };

  const handlePrevious = () => {
    setCurrentImageIndex((prev) => Math.max(0, prev - 1));
  };

  const handleNext = () => {
    setCurrentImageIndex((prev) => Math.min(images.length - 1, prev + 1));
  };

  const currentImage = images[currentImageIndex];

  return (
    <div className="space-y-6">
      {/* Character Name */}
      <div>
        <h3 className="text-2xl font-bold text-gray-900 mb-2">{character.name}</h3>
        <p className="text-sm text-gray-600">Edit the description and generate images</p>
      </div>

      {/* Description Editor */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Visual Description
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent resize-none"
          placeholder="Describe the character's appearance (face, hair, body, outfit)..."
        />
        <p className="mt-2 text-xs text-gray-500">
          Tip: Be specific about hair color, eye color, clothing style, and body type for better results
        </p>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={isGenerating || !description.trim()}
        className={`
          w-full px-6 py-4 rounded-lg font-bold text-lg transition-all
          ${isGenerating || !description.trim()
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:shadow-xl hover:scale-105'
          }
        `}
      >
        {isGenerating ? (
          <span className="flex items-center justify-center gap-2">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            Generating Image...
          </span>
        ) : (
          <span>🎨 Generate Image</span>
        )}
      </button>

      {/* Image Display */}
      {images.length > 0 && (
        <div className="space-y-4">
          <div className="border-t pt-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">
              Generated Images ({images.length})
            </h4>

            {/* Image Container */}
            <div className="relative bg-gray-100 rounded-lg overflow-hidden" style={{ minHeight: '400px' }}>
              {currentImage && (
                <div className="flex items-center justify-center p-4">
                  <img
                    src={currentImage.image_url}
                    alt={`${character.name} - Image ${currentImageIndex + 1}`}
                    className="max-w-full max-h-[500px] object-contain rounded-lg shadow-lg"
                  />
                </div>
              )}
            </div>

            {/* Image Navigation */}
            {images.length > 1 && (
              <div className="flex items-center justify-between mt-4">
                <button
                  onClick={handlePrevious}
                  disabled={currentImageIndex === 0}
                  className={`
                    px-4 py-2 rounded-lg font-semibold transition-all
                    ${currentImageIndex === 0
                      ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      : 'bg-purple-600 text-white hover:bg-purple-700'
                    }
                  `}
                >
                  ← Previous
                </button>

                <span className="text-sm text-gray-600 font-medium">
                  {currentImageIndex + 1} / {images.length}
                </span>

                <button
                  onClick={handleNext}
                  disabled={currentImageIndex === images.length - 1}
                  className={`
                    px-4 py-2 rounded-lg font-semibold transition-all
                    ${currentImageIndex === images.length - 1
                      ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      : 'bg-purple-600 text-white hover:bg-purple-700'
                    }
                  `}
                >
                  Next →
                </button>
              </div>
            )}

            {/* Image Info */}
            {currentImage && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">
                  <span className="font-semibold">Description used:</span>
                </p>
                <p className="text-sm text-gray-800">{currentImage.description}</p>
                <p className="text-xs text-gray-500 mt-2">
                  Generated: {new Date(currentImage.created_at).toLocaleString()}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* No Images State */}
      {images.length === 0 && !isGenerating && (
        <div className="border-t pt-6">
          <div className="bg-gray-50 rounded-lg p-12 text-center">
            <div className="text-6xl mb-4">🖼️</div>
            <p className="text-gray-600">No images generated yet</p>
            <p className="text-sm text-gray-500 mt-2">
              Click "Generate Image" to create your first character image
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
