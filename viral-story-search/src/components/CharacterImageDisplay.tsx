'use client';

import { useState, useEffect, useRef } from 'react';
import { Character, CharacterImage, ImageStyle, ImageStyleOption } from '@/types';
import Image from 'next/image';

// Import image assets
import historySageukImage from '@/assets/images/HISTORY_SAGEUK_ROMANCE.png';
import isekaiOtomeImage from '@/assets/images/ISEKAI_OTOME_FANTASY.png';
import modernKoreanImage from '@/assets/images/MODERN_KOREAN_ROMANCE.png';

interface CharacterImageDisplayProps {
  character: Character;
  images: CharacterImage[];
  onGenerateImage: (characterName: string, description: string, gender: string, imageStyle: ImageStyle) => Promise<void>;
  onSelectImage: (imageId: string) => void;
  isGenerating: boolean;
}

// Image style options with preview images
const IMAGE_STYLE_OPTIONS: ImageStyleOption[] = [
  {
    id: 'HISTORY_SAGEUK_ROMANCE',
    name: 'Historical Romance',
    description: 'Elegant sageuk style with dramatic lighting',
    previewImage: historySageukImage.src
  },
  {
    id: 'ISEKAI_OTOME_FANTASY',
    name: 'Fantasy Romance',
    description: 'Dreamy isekai otome style with soft pastels',
    previewImage: isekaiOtomeImage.src
  },
  {
    id: 'MODERN_KOREAN_ROMANCE',
    name: 'Modern Romance',
    description: 'Contemporary K-drama style with warm tones',
    previewImage: modernKoreanImage.src
  }
];

export default function CharacterImageDisplay({
  character,
  images,
  onGenerateImage,
  onSelectImage,
  isGenerating,
}: CharacterImageDisplayProps) {
  // Individual field states
  const [gender, setGender] = useState(character.gender || '');
  const [face, setFace] = useState(character.face || '');
  const [hair, setHair] = useState(character.hair || '');
  const [body, setBody] = useState(character.body || '');
  const [outfit, setOutfit] = useState(character.outfit || '');
  const [mood, setMood] = useState(character.mood || '');
  const [selectedImageStyle, setSelectedImageStyle] = useState<ImageStyle>('MODERN_KOREAN_ROMANCE');
  
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const prevImagesLengthRef = useRef(images.length);

  // Reset fields when character changes
  useEffect(() => {
    setGender(character.gender || '');
    setFace(character.face || '');
    setHair(character.hair || '');
    setBody(character.body || '');
    setOutfit(character.outfit || '');
    setMood(character.mood || '');
    setCurrentImageIndex(0);
    prevImagesLengthRef.current = images.length;
  }, [character.name]);

  // Only update index when a NEW image is added (length increases)
  useEffect(() => {
    if (images.length > prevImagesLengthRef.current) {
      setCurrentImageIndex(images.length - 1);
    }
    prevImagesLengthRef.current = images.length;
  }, [images.length]);

  // Combine all fields into visual description
  const getCombinedDescription = () => {
    const parts = [];
    if (gender) parts.push(gender);
    if (face) parts.push(face);
    if (hair) parts.push(hair);
    if (body) parts.push(body);
    if (outfit) parts.push(`wearing ${outfit}`);
    if (mood) parts.push(mood);
    return parts.join(', ');
  };

  const handleGenerate = async () => {
    const description = getCombinedDescription();
    await onGenerateImage(character.name, description, gender, selectedImageStyle);
  };

  const handlePrevious = () => {
    setCurrentImageIndex((prev) => Math.max(0, prev - 1));
  };

  const handleNext = () => {
    setCurrentImageIndex((prev) => Math.min(images.length - 1, prev + 1));
  };

  const handleDownload = (imageUrl: string, characterName: string, imageIndex: number) => {
    // Extract base64 data from data URL
    const base64Match = imageUrl.match(/^data:([^;]+);base64,(.+)$/);
    
    if (!base64Match) {
      console.error('Invalid image URL format');
      return;
    }
    
    const mimeType = base64Match[1];
    const base64Data = base64Match[2];
    
    // Determine file extension from MIME type
    const extension = mimeType.split('/')[1] || 'png';
    
    try {
      // Convert base64 to binary
      const binaryString = atob(base64Data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      // Create blob from binary data
      const blob = new Blob([bytes], { type: mimeType });
      
      // Create object URL from blob
      const blobUrl = URL.createObjectURL(blob);
      
      // Create temporary anchor element to trigger download
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = `${characterName}_image_${imageIndex + 1}.${extension}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up the blob URL after a short delay
      setTimeout(() => URL.revokeObjectURL(blobUrl), 100);
    } catch (error) {
      console.error('Error downloading image:', error);
    }
  };

  const handleSelect = (imageId: string) => {
    onSelectImage(imageId);
  };

  const currentImage = images[currentImageIndex];

  return (
    <div className="space-y-6">
      {/* Character Name */}
      <div>
        <h3 className="text-2xl font-bold text-gray-900 mb-2">{character.name}</h3>
        <p className="text-sm text-gray-600">Edit individual attributes and generate images</p>
      </div>

      {/* Individual Attribute Editors */}
      <div className="space-y-4">
        {/* Gender */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Gender
          </label>
          <input
            type="text"
            value={gender}
            onChange={(e) => setGender(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent text-gray-900"
            placeholder="e.g., male, female, non-binary"
          />
        </div>

        {/* Face */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Face
          </label>
          <input
            type="text"
            value={face}
            onChange={(e) => setFace(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent text-gray-900"
            placeholder="e.g., sharp jawline, dark brown eyes, olive skin tone"
          />
        </div>

        {/* Hair */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Hair
          </label>
          <input
            type="text"
            value={hair}
            onChange={(e) => setHair(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent text-gray-900"
            placeholder="e.g., short black hair, neatly styled"
          />
        </div>

        {/* Body */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Body
          </label>
          <input
            type="text"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent text-gray-900"
            placeholder="e.g., tall athletic build, broad shoulders"
          />
        </div>

        {/* Outfit */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Outfit
          </label>
          <input
            type="text"
            value={outfit}
            onChange={(e) => setOutfit(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent text-gray-900"
            placeholder="e.g., tailored navy suit with white shirt"
          />
        </div>

        {/* Mood */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Mood / Personality
          </label>
          <input
            type="text"
            value={mood}
            onChange={(e) => setMood(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent text-gray-900"
            placeholder="e.g., confident and charismatic"
          />
        </div>

        {/* Combined Preview */}
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <p className="text-xs font-semibold text-purple-700 mb-2">COMBINED DESCRIPTION:</p>
          <p className="text-sm text-gray-900">
            {getCombinedDescription() || 'Fill in the fields above to see the combined description'}
          </p>
        </div>
      </div>

      {/* Image Style Selection */}
      <div className="space-y-3">
        <label className="block text-sm font-semibold text-gray-700">
          Select Image Style
        </label>
        <div className="grid grid-cols-3 gap-3">
          {IMAGE_STYLE_OPTIONS.map((style) => (
            <button
              key={style.id}
              onClick={() => setSelectedImageStyle(style.id)}
              className={`
                relative overflow-hidden rounded-lg border-2 transition-all
                ${selectedImageStyle === style.id
                  ? 'border-purple-600 ring-2 ring-purple-600 ring-offset-2'
                  : 'border-gray-300 hover:border-purple-400'
                }
              `}
            >
              {/* Preview Image */}
              <div className="aspect-square bg-gray-100">
                <img
                  src={style.previewImage}
                  alt={style.name}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    // Fallback if image doesn't load
                    e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23ddd" width="100" height="100"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999"%3EStyle%3C/text%3E%3C/svg%3E';
                  }}
                />
              </div>
              
              {/* Style Info */}
              <div className="p-2 bg-white">
                <p className="text-xs font-semibold text-gray-900 text-center">
                  {style.name}
                </p>
                <p className="text-xs text-gray-600 text-center mt-1">
                  {style.description}
                </p>
              </div>

              {/* Selected Indicator */}
              {selectedImageStyle === style.id && (
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

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={isGenerating || !getCombinedDescription().trim()}
        className={`
          w-full px-6 py-4 rounded-lg font-bold text-lg transition-all
          ${isGenerating || !getCombinedDescription().trim()
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
                    onLoad={() => console.log('Image loaded successfully')}
                    onError={(e) => {
                      console.error('Image failed to load');
                      console.error('Image URL:', currentImage.image_url);
                      console.error('URL length:', currentImage.image_url.length);
                      console.error('URL prefix:', currentImage.image_url.substring(0, 100));
                    }}
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

            {/* Image Info and Actions */}
            {currentImage && (
              <div className="mt-4 space-y-3">
                {/* Action Buttons */}
                <div className="flex gap-3">
                  <button
                    onClick={() => handleSelect(currentImage.id)}
                    className={`
                      flex-1 px-4 py-3 rounded-lg font-semibold transition-all flex items-center justify-center gap-2
                      ${currentImage.is_selected
                        ? 'bg-green-600 text-white'
                        : 'bg-purple-600 text-white hover:bg-purple-700'
                      }
                    `}
                  >
                    {currentImage.is_selected ? (
                      <>
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                        <span>Selected as Reference</span>
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span>Select as Reference</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={() => handleDownload(currentImage.image_url, character.name, currentImageIndex)}
                    className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-all flex items-center justify-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    <span>Download Image</span>
                  </button>
                </div>

                {/* Selected Badge */}
                {currentImage.is_selected && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                    <p className="text-sm text-green-800 flex items-center gap-2">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span className="font-semibold">This image will be used as reference for scene generation</span>
                    </p>
                  </div>
                )}

                {/* Image Details */}
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-700 mb-2">
                    <span className="font-semibold">Description used:</span>
                  </p>
                  <p className="text-sm text-gray-900">{currentImage.description}</p>
                  <p className="text-xs text-gray-600 mt-2">
                    Generated: {new Date(currentImage.created_at).toLocaleString()}
                  </p>
                </div>
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
