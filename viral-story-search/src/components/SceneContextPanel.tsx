'use client';

import { WebtoonPanel } from '@/types';

interface SceneContextPanelProps {
  panel: WebtoonPanel;
  onGenerateImage: () => void;
  isGenerating: boolean;
}

export default function SceneContextPanel({
  panel,
  onGenerateImage,
  isGenerating,
}: SceneContextPanelProps) {
  // Parse dialogue into multiple lines if needed
  const dialogueLines = panel.dialogue
    ? panel.dialogue.split('\n').filter(line => line.trim())
    : [];

  return (
    <div className="w-64 bg-green-400 rounded-lg overflow-hidden flex flex-col">
      {/* Generate Button */}
      <div className="p-4">
        <button
          onClick={onGenerateImage}
          disabled={isGenerating}
          className={`
            w-full py-4 px-6 rounded-lg font-bold text-lg transition-all
            ${isGenerating
              ? 'bg-green-600 text-green-200 cursor-wait'
              : 'bg-green-600 text-white hover:bg-green-700 hover:shadow-lg transform hover:scale-105'
            }
          `}
        >
          {isGenerating ? (
            <span className="flex items-center justify-center gap-2">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
              Generating...
            </span>
          ) : (
            <span>Generate Scene Image</span>
          )}
        </button>
      </div>
      
      {/* Dialogue Section */}
      <div className="flex-1 p-4 space-y-3 overflow-y-auto">
        {dialogueLines.length > 0 ? (
          dialogueLines.map((line, index) => (
            <div
              key={index}
              className="bg-green-500 rounded-lg p-3 text-white text-sm"
            >
              <span className="font-semibold text-green-200 text-xs">Dialogue #{index + 1}</span>
              <p className="mt-1">{line}</p>
            </div>
          ))
        ) : (
          <>
            <div className="bg-green-500 rounded-lg p-3 text-green-200 text-sm italic">
              <span className="font-semibold text-xs">Dialogue #1</span>
              <p className="mt-1">No dialogue</p>
            </div>
            <div className="bg-green-500 rounded-lg p-3 text-green-200 text-sm italic">
              <span className="font-semibold text-xs">Dialogue #2</span>
              <p className="mt-1">No dialogue</p>
            </div>
          </>
        )}
        
        {/* Scene Metadata */}
        <div className="mt-4 pt-4 border-t border-green-500">
          <div className="text-sm text-green-800 space-y-2">
            <div>
              <span className="font-semibold">Shot Type:</span>
              <span className="ml-2">{panel.shot_type}</span>
            </div>
            <div>
              <span className="font-semibold">Characters:</span>
              <span className="ml-2">
                {panel.active_character_names.length > 0
                  ? panel.active_character_names.join(', ')
                  : 'None'
                }
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
