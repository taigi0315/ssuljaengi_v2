'use client';

import { useState } from 'react';
import { CharacterImage, StoryGenre, Character } from '@/types';
import { generateCharacterImage } from '@/lib/apiClient';
import CharacterImageDisplay from './CharacterImageDisplay';
import GenreSelector from './GenreSelector';
import CharacterLibraryModal from './CharacterLibraryModal';

const initialCharacter: Character = {
    name: '',
    gender: '',
    age: '',
    face: '',
    hair: '',
    body: '',
    outfit: '',
    mood: '',
    visual_description: '',
};

interface EyeCandyGeneratorProps {
    onProceedToShorts?: (selectedImage: CharacterImage) => void;
}

export default function EyeCandyGenerator({ onProceedToShorts }: EyeCandyGeneratorProps = {}) {
    const [genre, setGenre] = useState<StoryGenre>('MODERN_ROMANCE_DRAMA_MANHWA');
    const [allImages, setAllImages] = useState<CharacterImage[]>([]);
    const [isGenerating, setIsGenerating] = useState(false);
    // Create a session ID for this visit to group images if needed by backend, 
    // though we are mocking the strict script relationship.
    const [mockScriptId] = useState(() => `eye-candy-${Date.now()}`);

    // State for character editing and loading
    const [editingCharacter, setEditingCharacter] = useState<Character>(initialCharacter);
    const [isLibraryOpen, setIsLibraryOpen] = useState(false);

    const handleGenerateImage = async (name: string, description: string, gender: string) => {
        if (!name.trim()) {
            alert('Please enter a character name');
            return;
        }

        try {
            setIsGenerating(true);

            // We map the incoming request to the API. 
            // Note: Backend expects a script_id. We pass our unique session ID.
            // If the backend enforces foreign key constraints on script_id, this might fail unless
            // there is a "guest" or "sandbox" mode. 
            // User indicated "mocking script_id is fine", so we proceed.
            const newImage = await generateCharacterImage({
                script_id: mockScriptId,
                character_name: name,
                description,
                gender,
                image_style: genre,
            });

            // Add to session history
            setAllImages(prev => [...prev, newImage]);
        } catch (error) {
            console.error('Generation error:', error);
            alert('Failed to generate image. The backend might require a real story context.');
        } finally {
            setIsGenerating(false);
        }
    };

    const handleSaveToLibrary = async (character: Character, imageUrl: string) => {
        // We can implement this if the API supports it
        // For now, we reuse the existing functionality which might just work
        // The CharacterImageDisplay calls this prop.
        // We need to import saveCharacterToLibrary from apiClient if we want to use it here wrapper-style
        // or just pass a handler.
        // Importing dynamically to avoid unused import if we don't use it directly in the body
        const { saveCharacterToLibrary } = await import('@/lib/apiClient');
        await saveCharacterToLibrary(character, imageUrl);
    };

    // Dummy select handler (the history view in CharacterImageDisplay handles selection UI locally for reference)
    // We might not need to do anything with it in this standalone mode
    const handleSelectImage = (imageId: string) => {
        setAllImages(prev => prev.map(img => ({
            ...img,
            is_selected: img.id === imageId ? !img.is_selected : img.is_selected
        })));
    };

    const handleLoadCharacter = (savedCharacter: { character: Character, image_url?: string }) => {
        setEditingCharacter(savedCharacter.character);

        // If the saved character has an image, add it to our history so it can be selected
        if (savedCharacter.image_url) {
            const loadedImage: CharacterImage = {
                id: `loaded-${Date.now()}`, // Temporary ID for session
                character_name: savedCharacter.character.name,
                description: savedCharacter.character.visual_description,
                image_url: savedCharacter.image_url,
                created_at: new Date().toISOString(),
                is_selected: false
            };
            setAllImages(prev => [...prev, loadedImage]);
        }

        setIsLibraryOpen(false);
    };

    const handleProceedClick = () => {
        const selectedImage = allImages.find(img => img.is_selected);
        if (selectedImage && onProceedToShorts) {
            onProceedToShorts(selectedImage);
        }
    };

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            {/* Header Section */}
            <div className="text-center space-y-4 relative">
                <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-violet-500">
                    🍬 Create Eye Candy
                </h2>
                <p className="text-gray-600 max-w-2xl mx-auto">
                    Experiment with character designs freely! Choose a genre, describe your character, and generate stunning visuals without creating a full story.
                </p>

                {/* Load Button */}
                <div className="absolute top-0 right-0">
                    <button
                        onClick={() => setIsLibraryOpen(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-50 hover:border-purple-300 transition-all text-gray-700 font-medium"
                    >
                        <span>📂</span>
                        <span>Load Character</span>
                    </button>
                </div>
            </div>

            {/* Genre Selector */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-pink-100">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <span>🎨</span> Choose Art Style
                </h3>
                <GenreSelector
                    selectedGenre={genre}
                    onGenreSelect={setGenre}
                />
            </div>

            {/* Main Generation Area */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 md:p-8">
                <CharacterImageDisplay
                    character={editingCharacter}
                    images={allImages}
                    onGenerateImage={handleGenerateImage}
                    onSelectImage={handleSelectImage}
                    isGenerating={isGenerating}
                    onSaveToLibrary={handleSaveToLibrary}
                    isNameEditable={true}
                />
            </div>

            {/* Tips */}
            <div className="bg-blue-50 rounded-lg p-4 text-sm text-blue-700">
                <p className="font-semibold flex items-center gap-2">
                    <span>💡</span> Pro Tip:
                </p>
                <p className="mt-1">
                    All images you generate in this session will be saved in the history above.
                    You can change the name and attributes anytime to create a completely new character,
                    and scroll back to see previous ones!
                </p>
            </div>

            {/* Proceed Button - Show when reference is selected */}
            {allImages.some(img => img.is_selected) && (
                <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border-2 border-purple-300 shadow-lg">
                    <div className="text-center space-y-4">
                        <div className="flex items-center justify-center gap-2 text-green-700">
                            <span className="text-2xl">✅</span>
                            <span className="font-semibold text-lg">Reference Image Selected!</span>
                        </div>
                        <p className="text-gray-600 text-sm">
                            Ready to generate your shorts script using this character as reference.
                        </p>
                        <button
                            onClick={handleProceedClick}
                            className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold text-lg rounded-xl hover:shadow-xl hover:scale-105 transition-all flex items-center gap-3 mx-auto"
                        >
                            <span>🎬</span>
                            <span>Proceed to Shorts Generator</span>
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                            </svg>
                        </button>
                    </div>
                </div>
            )}

            {/* Library Modal */}
            <CharacterLibraryModal
                isOpen={isLibraryOpen}
                onClose={() => setIsLibraryOpen(false)}
                onSelect={handleLoadCharacter}
            />
        </div>
    );
}
