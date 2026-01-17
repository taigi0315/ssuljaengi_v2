'use client';

import { useState, useEffect } from 'react';
import { WebtoonScript, StoryGenre, Character, WebtoonPanel } from '@/types';
import { generateWebtoonScript } from '@/lib/apiClient';

interface ScriptPreviewProps {
  storyId: string;
  genre: StoryGenre;
  webtoonScript: WebtoonScript | null;
  onScriptGenerated: (script: WebtoonScript) => void;
  onProceedToCharacters: () => void;
}

export default function ScriptPreview({
  storyId,
  genre,
  webtoonScript,
  onScriptGenerated,
  onProceedToCharacters,
}: ScriptPreviewProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generate script only if not already cached
  const handleGenerateScript = async () => {
    if (webtoonScript) return; // Already have script, don't regenerate
    
    try {
      setIsGenerating(true);
      setError(null);

      const script = await generateWebtoonScript(storyId);
      onScriptGenerated(script);
    } catch (err) {
      console.error('Script generation error:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate webtoon script');
    } finally {
      setIsGenerating(false);
    }
  };

  // Helper to format genre for display
  const formatGenreName = (g: StoryGenre): string => {
    return g.replace(/_/g, ' ').replace(/MANHWA/g, '').trim();
  };

  // Render loading state
  if (isGenerating) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-200 border-t-purple-600 mb-6" />
        <h3 className="text-xl font-bold text-gray-800 mb-2">Converting Story to Webtoon Script...</h3>
        <p className="text-gray-500">Analyzing characters and breaking down scenes</p>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="max-w-2xl mx-auto p-8">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={handleGenerateScript}
            className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Render prompt to generate
  if (!webtoonScript) {
    return (
      <div className="max-w-2xl mx-auto p-8">
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="text-6xl mb-6">📖</div>
          <h3 className="text-2xl font-bold text-gray-800 mb-4">Generate Webtoon Script</h3>
          <p className="text-gray-500 mb-6">
            Convert your story into a structured webtoon script with characters and panels.
          </p>
          <button
            onClick={handleGenerateScript}
            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold rounded-xl hover:shadow-lg transition-all"
          >
            🎬 Generate Script
          </button>
        </div>
      </div>
    );
  }

  // Render script preview
  return (
    <div className="space-y-6">
      {/* Genre Badge */}
      <div className="flex items-center justify-center gap-2 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl border border-purple-200">
        <span className="text-sm font-semibold text-gray-700">Selected Genre:</span>
        <span className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-full text-sm font-bold shadow-md">
          🎭 {formatGenreName(genre)}
        </span>
      </div>

      {/* Script Overview */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-800">📖 Webtoon Script Preview</h2>
          <span className="text-sm text-gray-500">
            {webtoonScript.characters.length} Characters · {webtoonScript.panels.length} Panels
          </span>
        </div>

        {/* Characters Section */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <span>🎭</span> Characters
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {webtoonScript.characters.map((char: Character, index: number) => (
              <div key={index} className="p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                <div className="flex items-start gap-3">
                  <div className="w-12 h-12 rounded-full bg-purple-200 flex items-center justify-center text-purple-700 font-bold text-lg">
                    {char.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-bold text-gray-800">{char.name}</h4>
                    <p className="text-sm text-gray-600">
                      {char.gender} · {char.age}
                    </p>
                    <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                      {char.visual_description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Panels Section */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <span>🖼️</span> Panels ({webtoonScript.panels.length})
          </h3>
          <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
            {webtoonScript.panels.map((panel: WebtoonPanel, index: number) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-purple-300 transition-colors">
                <div className="flex items-center gap-3 mb-2">
                  <span className="w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center text-sm font-bold">
                    {panel.panel_number}
                  </span>
                  <span className="text-sm font-medium text-purple-600 bg-purple-100 px-2 py-1 rounded">
                    {panel.shot_type}
                  </span>
                  {panel.active_character_names && panel.active_character_names.length > 0 && (
                    <span className="text-xs text-gray-500">
                      👥 {panel.active_character_names.join(', ')}
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-700 mb-2">{panel.visual_prompt}</p>
                {panel.dialogue && Array.isArray(panel.dialogue) && panel.dialogue.length > 0 && (
                  <div className="mt-2 p-2 bg-white rounded border-l-4 border-purple-400">
                    <p className="text-xs text-gray-500 mb-1">💬 Dialogue:</p>
                    {panel.dialogue.map((line: any, idx: number) => (
                      <p key={idx} className="text-sm text-gray-800">
                        <span className="font-semibold text-purple-700">{line.character}:</span> 
                        <span className="italic ml-1">"{line.text}"</span>
                      </p>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Proceed Button */}
        <div className="flex justify-center pt-4 border-t border-gray-200">
          <button
            onClick={onProceedToCharacters}
            className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold rounded-xl hover:shadow-lg transition-all flex items-center gap-2"
          >
            <span>🎨</span>
            <span>Proceed to Character Images</span>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
