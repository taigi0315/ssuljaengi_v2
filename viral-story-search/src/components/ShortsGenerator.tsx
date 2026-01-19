'use client';

import { useState } from 'react';
import { ShortsScript, CharacterImage } from '@/types';
import { generateShortsScript, generateCharacterImage } from '@/lib/apiClient';

interface ShortsGeneratorProps {
    referenceImage?: CharacterImage;
}

export default function ShortsGenerator({ referenceImage }: ShortsGeneratorProps = {}) {
    const [topic, setTopic] = useState('');
    const [script, setScript] = useState<ShortsScript | null>(null);
    const [scriptId, setScriptId] = useState<string | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [sceneImages, setSceneImages] = useState<Record<number, string>>({});
    const [generatingScenes, setGeneratingScenes] = useState<Set<number>>(new Set());
    const [editablePrompts, setEditablePrompts] = useState<Record<number, { imagePrompt: string; videoPrompt: string }>>({});
    const [copiedSceneId, setCopiedSceneId] = useState<number | null>(null);
    const [isGeneratingAll, setIsGeneratingAll] = useState(false);

    const handleGenerate = async () => {
        try {
            setIsGenerating(true);
            setError(null);

            const result = await generateShortsScript(topic.trim() || undefined);
            setScript(result);

            // Store the script ID for image generation
            const newScriptId = `shorts-${Date.now()}`;
            setScriptId(newScriptId);

            // Initialize editable prompts from the generated script
            const initialPrompts: Record<number, { imagePrompt: string; videoPrompt: string }> = {};
            result.scenes.forEach(scene => {
                initialPrompts[scene.scene_id] = {
                    imagePrompt: scene.image_prompt,
                    videoPrompt: scene.video_prompt
                };
            });
            setEditablePrompts(initialPrompts);
        } catch (err) {
            console.error('Shorts generation error:', err);
            setError(err instanceof Error ? err.message : 'Failed to generate shorts');
        } finally {
            setIsGenerating(false);
        }
    };

    const handleGenerateSceneImage = async (sceneId: number) => {
        if (!scriptId) {
            alert('No script ID available. Please generate a script first.');
            return;
        }

        try {
            setGeneratingScenes(prev => new Set(prev).add(sceneId));

            // Use the edited prompt from state
            const currentPrompt = editablePrompts[sceneId]?.imagePrompt || '';

            const image = await generateCharacterImage({
                script_id: scriptId, // Use the persistent script ID
                character_name: `Scene ${sceneId}`,
                description: currentPrompt,
                gender: 'male', // Default, could be made dynamic
                image_style: 'MODERN_ROMANCE_DRAMA_MANHWA',
                reference_image_url: referenceImage?.image_url // Pass reference image if available
            });

            setSceneImages(prev => ({ ...prev, [sceneId]: image.image_url }));
        } catch (err) {
            console.error(`Scene ${sceneId} image generation error:`, err);
            alert(`Failed to generate image for scene ${sceneId}`);
        } finally {
            setGeneratingScenes(prev => {
                const next = new Set(prev);
                next.delete(sceneId);
                return next;
            });
        }
    };

    const handleCopyVideoPrompt = (sceneId: number) => {
        const videoPrompt = editablePrompts[sceneId]?.videoPrompt || '';
        navigator.clipboard.writeText(videoPrompt).then(() => {
            setCopiedSceneId(sceneId);
            setTimeout(() => setCopiedSceneId(null), 2000); // Hide after 2 seconds
        }).catch(err => {
            console.error('Failed to copy:', err);
        });
    };

    const handleGenerateAll = async () => {
        if (!scriptId || !script) {
            alert('Please generate a script first.');
            return;
        }

        setIsGeneratingAll(true);
        try {
            // Generate images sequentially (one by one)
            for (const scene of script.scenes) {
                // Check current state to see if this scene already has an image
                const hasImage = sceneImages[scene.scene_id];
                if (!hasImage) {
                    // Use a nested try-catch to continue even if one fails
                    try {
                        setGeneratingScenes(prev => new Set(prev).add(scene.scene_id));

                        // Use the edited prompt from state
                        const currentPrompt = editablePrompts[scene.scene_id]?.imagePrompt || scene.image_prompt;

                        const image = await generateCharacterImage({
                            script_id: scriptId,
                            character_name: `Scene ${scene.scene_id}`,
                            description: currentPrompt,
                            gender: 'male',
                            image_style: 'MODERN_ROMANCE_DRAMA_MANHWA',
                            reference_image_url: referenceImage?.image_url
                        });

                        // Use functional setState to avoid race conditions
                        setSceneImages(prev => ({ ...prev, [scene.scene_id]: image.image_url }));

                        setGeneratingScenes(prev => {
                            const next = new Set(prev);
                            next.delete(scene.scene_id);
                            return next;
                        });
                    } catch (err) {
                        console.error(`Failed to generate image for scene ${scene.scene_id}:`, err);
                        setGeneratingScenes(prev => {
                            const next = new Set(prev);
                            next.delete(scene.scene_id);
                            return next;
                        });
                        // Continue to next scene even if this one failed
                    }
                }
            }
        } catch (error) {
            console.error('Batch generation error:', error);
        } finally {
            setIsGeneratingAll(false);
        }
    };

    const handlePromptChange = (sceneId: number, field: 'imagePrompt' | 'videoPrompt', value: string) => {
        setEditablePrompts(prev => ({
            ...prev,
            [sceneId]: {
                ...prev[sceneId],
                [field]: value
            }
        }));
    };

    const handleDownloadImage = (imageUrl: string, sceneId: number) => {
        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = `scene_${sceneId}_${Date.now()}.png`;
        link.click();
    };

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            {/* Header Section */}
            <div className="text-center space-y-4">
                <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-violet-500">
                    🎬 Shorts Generator
                </h2>
                <p className="text-gray-600 max-w-2xl mx-auto">
                    Generate a 6-scene Manhwa shorts script! Enter a topic or leave it blank for a random idea.
                </p>
            </div>

            {/* Topic Input */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-pink-100">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <span>💡</span> Topic
                </h3>
                <input
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="Enter a topic (e.g., 'A CEO who secretly loves baking') or leave empty for random"
                    className="w-full p-4 text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                />
                <button
                    onClick={handleGenerate}
                    disabled={isGenerating}
                    className={`mt-4 w-full px-6 py-4 rounded-lg font-bold text-lg transition-all ${isGenerating
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:shadow-xl hover:scale-105'
                        }`}
                >
                    {isGenerating ? '✨ Generating...' : '🎬 Generate Shorts Script'}
                </button>
            </div>

            {/* Error Display */}
            {error && (
                <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6 text-center">
                    <p className="text-red-600 font-semibold">{error}</p>
                </div>
            )}

            {/* Script Display */}
            {script && (
                <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 md:p-8">
                    <div className="mb-6">
                        <h3 className="text-2xl font-bold text-gray-900 mb-2">
                            📖 {script.metadata.topic}
                        </h3>
                        <p className="text-sm text-gray-500">{script.metadata.style}</p>
                    </div>

                    {/* Create All Button */}
                    <div className="mb-6">
                        <button
                            onClick={handleGenerateAll}
                            disabled={isGeneratingAll || Object.keys(sceneImages).length === script.scenes.length}
                            className={`w-full px-6 py-4 rounded-lg font-bold text-lg transition-all ${isGeneratingAll
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : Object.keys(sceneImages).length === script.scenes.length
                                    ? 'bg-green-100 text-green-700 border-2 border-green-300'
                                    : 'bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:shadow-xl hover:scale-105'
                                }`}
                        >
                            {isGeneratingAll
                                ? `⏳ Generating... (${Object.keys(sceneImages).length}/${script.scenes.length})`
                                : Object.keys(sceneImages).length === script.scenes.length
                                    ? '✅ All Images Generated'
                                    : '🚀 Create All Images'}
                        </button>
                    </div>

                    {/* Scenes with Two-Column Layout */}
                    <div className="space-y-8">
                        {script.scenes.map((scene) => (
                            <div
                                key={scene.scene_id}
                                className="border-2 border-purple-300 rounded-xl overflow-hidden bg-white shadow-md"
                            >
                                {/* Scene Header */}
                                <div className="bg-gradient-to-r from-purple-600 to-blue-600 px-6 py-4">
                                    <div className="flex items-center gap-3">
                                        <span className="w-10 h-10 rounded-full bg-white text-purple-600 flex items-center justify-center font-bold text-lg">
                                            {scene.scene_id}
                                        </span>
                                        <h4 className="text-lg font-bold text-white">
                                            {scene.action}
                                        </h4>
                                    </div>
                                </div>

                                {/* Two-Column Content */}
                                <div className="grid md:grid-cols-2 gap-6 p-6">
                                    {/* Left Side: Prompts */}
                                    <div className="space-y-4">
                                        {/* Image Prompt */}
                                        <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                                            <p className="text-xs font-bold text-purple-700 mb-2 uppercase tracking-wide">
                                                🖼️ Image Prompt
                                            </p>
                                            <textarea
                                                value={editablePrompts[scene.scene_id]?.imagePrompt || scene.image_prompt}
                                                onChange={(e) => handlePromptChange(scene.scene_id, 'imagePrompt', e.target.value)}
                                                className="w-full text-sm text-gray-800 leading-relaxed bg-white border border-purple-300 rounded-md p-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                                                rows={4}
                                            />
                                        </div>

                                        {/* Video Prompt with Copy Button */}
                                        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                                            <div className="flex items-center justify-between mb-2">
                                                <p className="text-xs font-bold text-blue-700 uppercase tracking-wide">
                                                    🎥 Video Motion
                                                </p>
                                                <button
                                                    onClick={() => handleCopyVideoPrompt(scene.scene_id)}
                                                    className={`px-3 py-1 text-xs rounded-md font-semibold transition-colors ${copiedSceneId === scene.scene_id
                                                        ? 'bg-green-600 text-white'
                                                        : 'bg-blue-600 text-white hover:bg-blue-700'
                                                        }`}
                                                >
                                                    {copiedSceneId === scene.scene_id ? '✅ Copied!' : '📋 Copy'}
                                                </button>
                                            </div>
                                            <textarea
                                                value={editablePrompts[scene.scene_id]?.videoPrompt || scene.video_prompt}
                                                onChange={(e) => handlePromptChange(scene.scene_id, 'videoPrompt', e.target.value)}
                                                className="w-full text-sm text-gray-800 leading-relaxed bg-white border border-blue-300 rounded-md p-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                                                rows={4}
                                            />
                                        </div>

                                        {/* Generate Image Button */}
                                        <button
                                            onClick={() => handleGenerateSceneImage(scene.scene_id)}
                                            disabled={generatingScenes.has(scene.scene_id)}
                                            className={`w-full px-4 py-3 rounded-lg font-bold text-sm transition-all ${generatingScenes.has(scene.scene_id)
                                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                                : 'bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:shadow-lg hover:scale-105'
                                                }`}
                                        >
                                            {generatingScenes.has(scene.scene_id) ? '⏳ Generating...' : '✨ Generate Image'}
                                        </button>
                                    </div>

                                    {/* Right Side: Generated Image */}
                                    <div className="flex flex-col items-center justify-center bg-gray-50 rounded-lg p-4 border-2 border-dashed border-gray-300">
                                        {sceneImages[scene.scene_id] ? (
                                            <>
                                                <img
                                                    src={sceneImages[scene.scene_id]}
                                                    alt={`Scene ${scene.scene_id}`}
                                                    className="w-full h-auto rounded-lg shadow-lg mb-4"
                                                />
                                                <button
                                                    onClick={() => handleDownloadImage(sceneImages[scene.scene_id], scene.scene_id)}
                                                    className="w-full px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold rounded-lg hover:shadow-lg transition-all"
                                                >
                                                    ⬇️ Download Image
                                                </button>
                                            </>
                                        ) : (
                                            <div className="text-center py-12">
                                                <div className="text-6xl mb-4">🖼️</div>
                                                <p className="text-gray-500 font-semibold">
                                                    Click "Generate Image" to create
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
