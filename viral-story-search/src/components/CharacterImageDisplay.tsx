'use client';

import { useState, useEffect, useRef } from 'react';
import { Character, CharacterImage } from '@/types';
import { CHARACTER_PRESETS, AGE_OPTIONS } from '@/constants/characterPresets';

interface CharacterImageDisplayProps {
  character: Character;
  images: CharacterImage[];
  onGenerateImage: (characterName: string, description: string, gender: string) => Promise<void>;
  onSelectImage: (imageId: string) => void;
  isGenerating: boolean;
  onSaveToLibrary?: (character: Character, imageUrl: string) => Promise<void>;
  isNameEditable?: boolean;
}



export default function CharacterImageDisplay({
  character,
  images,
  onGenerateImage,
  onSelectImage,
  isGenerating,
  onSaveToLibrary,
  isNameEditable = false,
}: CharacterImageDisplayProps) {
  // Individual field states
  const [gender, setGender] = useState(character.gender || '');
  const [age, setAge] = useState(character.age || '');
  const [face, setFace] = useState(character.face || '');
  const [hair, setHair] = useState(character.hair || '');
  const [body, setBody] = useState(character.body || '');
  const [outfit, setOutfit] = useState(character.outfit || '');
  const [mood, setMood] = useState(character.mood || '');

  // Name state for editable mode
  const [name, setName] = useState(character.name || '');

  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const prevImagesLengthRef = useRef(images.length);

  // Reset fields when character changes
  useEffect(() => {
    setName(character.name || '');
    setGender(character.gender || '');
    setAge(character.age || '');

    // Map new fields to old UI fields if old ones are missing
    setFace(character.face || '');
    setHair(character.hair || '');
    setBody(character.body || '');

    setOutfit(character.outfit || '');
    setMood(character.mood || '');

    setCurrentImageIndex(0);
    prevImagesLengthRef.current = images.length;
  }, [character]);

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
    if (age) parts.push(`${age} years old`);
    if (face) parts.push(face);
    if (hair) parts.push(hair);
    if (body) parts.push(body);
    if (outfit) parts.push(`wearing ${outfit}`);
    if (mood) parts.push(mood);
    return parts.join(', ');
  };

  const handleGenerate = async () => {
    const description = getCombinedDescription();
    await onGenerateImage(name || character.name, description, gender);
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

  const getRandomItem = (arr: readonly string[]) => {
    return arr[Math.floor(Math.random() * arr.length)];
  };

  const handleRandomize = () => {
    if (!gender) {
      alert('Please select a gender first to generate random attributes!');
      return;
    }

    const normGender = gender.toLowerCase().trim();
    let presetKey: 'male' | 'female' | null = null;

    if (normGender === 'male' || normGender === 'man' || normGender === 'boy') {
      presetKey = 'male';
    } else if (normGender === 'female' || normGender === 'woman' || normGender === 'girl') {
      presetKey = 'female';
    } else {
      // Default to one or random if unspecific? User said "given a gender".
      // Let's fallback to random if possible, or just error. 
      // For now, let's just pick one randomly if it's ambiguous, or force user to pick one of the dropdowns.
      // Since we are changing to dropdown, validation is easier.
      presetKey = Math.random() > 0.5 ? 'male' : 'female';
    }

    const presets = CHARACTER_PRESETS[presetKey];

    setFace(getRandomItem(presets.face));
    setHair(getRandomItem(presets.hair));
    setBody(getRandomItem(presets.body));
    setOutfit(getRandomItem(presets.outfit));
    setMood(getRandomItem(presets.mood));

    // Also randomize age if empty? User said "between gender and age". 
    // Maybe we leave age alone or randomize it too?
    // "And this will create randomly select the face hair body outfit and the mood personally anything." -> "anything" might imply all fields.
    // Let's randomize age too if they want full random.
    setAge(getRandomItem(AGE_OPTIONS));
  };

  const currentImage = images[currentImageIndex];

  return (
    <div className="space-y-6">
      {/* Character Name */}
      <div>
        {isNameEditable ? (
          <div className="mb-4">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Character Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 text-xl font-bold border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent text-gray-900 placeholder-gray-400"
              placeholder="Enter character name..."
            />
          </div>
        ) : (
          <h3 className="text-2xl font-bold text-gray-900 mb-2">{character.name}</h3>
        )}
        <p className="text-sm text-gray-600">Edit individual attributes and generate images</p>
      </div>

      {/* Individual Attribute Editors */}
      <div className="space-y-4">
        {/* Gender and Age Row with Dice */}
        <div className="flex items-end gap-4">
          {/* Gender */}
          <div className="flex-1">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Gender
            </label>
            <select
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent text-gray-900 bg-white"
            >
              <option value="">Select Gender</option>
              <option value="female">Female</option>
              <option value="male">Male</option>
            </select>
          </div>

          {/* Random Dice Button */}
          <button
            onClick={handleRandomize}
            className="mb-[2px] p-2 bg-gradient-to-br from-pink-500 to-purple-600 text-white rounded-lg hover:shadow-lg hover:scale-105 transition-all"
            title="Randomize Attributes"
            type="button"
          >
            <span className="text-2xl">🎲</span>
          </button>

          {/* Age */}
          <div className="flex-1">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Age
            </label>
            <select
              value={age}
              onChange={(e) => setAge(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent text-gray-900 bg-white"
            >
              <option value="">Select Age</option>
              {AGE_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt.charAt(0).toUpperCase() + opt.slice(1)}
                </option>
              ))}
            </select>
          </div>
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

                {/* Save to Library Button */}
                {onSaveToLibrary && (
                  <button
                    onClick={async () => {
                      try {
                        await onSaveToLibrary({
                          ...character,
                          name: isNameEditable ? name : character.name,
                          gender,
                          age,
                          face,
                          hair,
                          body,
                          outfit,
                          mood,
                          visual_description: getCombinedDescription(),
                          // Add other required fields if missing
                          reference_tag: 'eye_candy_generated',
                          personality: mood, // Fallback for personality
                        }, currentImage.image_url);
                        alert('Character saved to library!');
                      } catch (e) {
                        console.error(e);
                        alert('Failed to save character');
                      }
                    }}
                    className="w-full px-4 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition-all flex items-center justify-center gap-2"
                  >
                    <span>💾 Save Character to Library</span>
                  </button>
                )}

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
