'use client';

import { useState, useEffect } from 'react';
import { Character } from '@/types';
import { getLibraryCharacters } from '@/lib/apiClient';

interface CharacterLibraryModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSelect: (savedCharacter: { character: Character, image_url?: string }) => void;
}

interface SavedCharacter {
    id: string;
    character: Character;
    image_url?: string;
    created_at: string;
}

export default function CharacterLibraryModal({ isOpen, onClose, onSelect }: CharacterLibraryModalProps) {
    const [characters, setCharacters] = useState<SavedCharacter[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (isOpen) {
            loadCharacters();
        }
    }, [isOpen]);

    const loadCharacters = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const data = await getLibraryCharacters();
            setCharacters(data);
        } catch (err) {
            console.error('Failed to load library:', err);
            setError('Failed to load characters. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden">
                {/* Header */}
                <div className="p-6 border-b flex justify-between items-center bg-gray-50">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-800">📂 Load Character</h2>
                        <p className="text-gray-500 text-sm">Select a saved character to use as a template</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-200 rounded-full transition-colors"
                    >
                        <svg className="w-6 h-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 bg-gray-50/50">
                    {isLoading ? (
                        <div className="flex flex-col items-center justify-center h-64">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mb-4"></div>
                            <p className="text-gray-500 font-medium">Loading library...</p>
                        </div>
                    ) : error ? (
                        <div className="flex flex-col items-center justify-center h-64 text-red-500">
                            <div className="text-5xl mb-4">⚠️</div>
                            <p className="font-medium">{error}</p>
                            <button
                                onClick={loadCharacters}
                                className="mt-4 px-4 py-2 bg-red-100 rounded-lg hover:bg-red-200 transition-colors"
                            >
                                Retry
                            </button>
                        </div>
                    ) : characters.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-64 text-gray-500">
                            <div className="text-5xl mb-4">📭</div>
                            <p className="font-medium">Library is empty</p>
                            <p className="text-sm mt-1">Save some characters first!</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                            {characters.map((item) => (
                                <div
                                    key={item.id}
                                    onClick={() => onSelect({ character: item.character, image_url: item.image_url })}
                                    className="group bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md hover:border-purple-300 hover:ring-2 hover:ring-purple-400 hover:ring-offset-2 transition-all cursor-pointer flex flex-col"
                                >
                                    {/* Image / Avatar */}
                                    <div className="aspect-[3/4] bg-gray-100 relative overflow-hidden">
                                        {item.image_url ? (
                                            <img
                                                src={item.image_url}
                                                alt={item.character.name}
                                                className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-300"
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-indigo-50 to-purple-50">
                                                <span className="text-4xl">👤</span>
                                            </div>
                                        )}
                                        {/* Overlay Date */}
                                        <div className="absolute bottom-0 w-full bg-gradient-to-t from-black/70 to-transparent p-3 pt-8">
                                            <p className="text-white text-xs font-medium">
                                                {new Date(item.created_at).toLocaleDateString()}
                                            </p>
                                        </div>
                                    </div>

                                    {/* Info */}
                                    <div className="p-4 flex-1 flex flex-col">
                                        <h3 className="font-bold text-gray-900 truncate mb-1">
                                            {item.character.name || 'Unnamed'}
                                        </h3>
                                        <div className="space-y-1 mt-auto">
                                            <div className="flex gap-2 text-xs text-gray-500">
                                                {item.character.gender && (
                                                    <span className="px-2 py-0.5 bg-gray-100 rounded-full capitalize">
                                                        {item.character.gender}
                                                    </span>
                                                )}
                                                {item.character.age && (
                                                    <span className="px-2 py-0.5 bg-gray-100 rounded-full capitalize">
                                                        {item.character.age}
                                                    </span>
                                                )}
                                            </div>
                                            <p className="text-xs text-gray-400 line-clamp-2 mt-2">
                                                {item.character.visual_description || 'No description'}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
