'use client';

import { WebtoonPanel } from '@/types';

interface SceneSidebarProps {
  panels: WebtoonPanel[];
  currentPanelIndex: number;
  onPanelSelect: (index: number) => void;
  sceneImages: Record<number, string | null>; // panel_number -> image_url
}

export default function SceneSidebar({
  panels,
  currentPanelIndex,
  onPanelSelect,
  sceneImages,
}: SceneSidebarProps) {
  return (
    <div className="w-48 bg-gray-800 rounded-lg overflow-hidden flex flex-col">
      <div className="p-3 bg-gray-900 border-b border-gray-700">
        <h3 className="text-sm font-bold text-white">Scenes</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {panels.map((panel, index) => {
          const imageUrl = sceneImages[panel.panel_number];
          const isActive = index === currentPanelIndex;
          
          return (
            <button
              key={panel.panel_number}
              onClick={() => onPanelSelect(index)}
              className={`
                w-full p-3 rounded-lg text-left transition-all
                ${isActive
                  ? 'bg-purple-600 text-white ring-2 ring-purple-400'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }
              `}
            >
              <div className="text-sm font-semibold mb-1">
                Scene #{panel.panel_number}
              </div>
              
              {/* Thumbnail or placeholder */}
              <div className="aspect-video bg-gray-600 rounded overflow-hidden mb-2">
                {imageUrl ? (
                  <img
                    src={imageUrl}
                    alt={`Scene ${panel.panel_number}`}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                    No image
                  </div>
                )}
              </div>
              
              <div className="text-xs text-gray-400 truncate">
                {panel.shot_type}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
