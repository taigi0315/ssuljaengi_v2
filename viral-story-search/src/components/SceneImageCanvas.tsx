'use client';

import { SceneImage } from '@/types';

interface SceneImageCanvasProps {
  image: SceneImage | null;
  isGenerating: boolean;
  panelNumber: number;
}

export default function SceneImageCanvas({
  image,
  isGenerating,
  panelNumber,
}: SceneImageCanvasProps) {
  return (
    <div className="relative bg-gray-200 rounded-lg overflow-hidden" style={{ aspectRatio: '16/9' }}>
      {/* Border handles (decorative) */}
      <div className="absolute inset-0 border-4 border-purple-500 rounded-lg pointer-events-none z-10">
        {/* Corner handles */}
        <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-4 h-2 bg-white border border-gray-400 rounded-sm" />
        <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-4 h-2 bg-white border border-gray-400 rounded-sm" />
        <div className="absolute top-1/2 -left-1 -translate-y-1/2 w-2 h-4 bg-white border border-gray-400 rounded-sm" />
        <div className="absolute top-1/2 -right-1 -translate-y-1/2 w-2 h-4 bg-white border border-gray-400 rounded-sm" />
      </div>
      
      {/* Loading state */}
      {isGenerating && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-300 z-20">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mb-4" />
          <p className="text-gray-700 font-semibold">Generating Scene Image...</p>
          <p className="text-gray-500 text-sm">This may take a moment</p>
        </div>
      )}
      
      {/* Generated image */}
      {image && !isGenerating && (
        <img
          src={image.image_url}
          alt={`Scene ${panelNumber}`}
          className="w-full h-full object-contain"
        />
      )}
      
      {/* Placeholder */}
      {!image && !isGenerating && (
        <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500">
          <svg className="w-24 h-24 mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p className="text-lg font-semibold">IMAGE GENERATED</p>
          <p className="text-sm">Click "Generate Scene Image" to create</p>
        </div>
      )}
    </div>
  );
}
