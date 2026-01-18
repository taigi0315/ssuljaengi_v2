'use client';

import { useState, useEffect } from 'react';
import { WebtoonScript, WebtoonPanel, SceneImage, StoryGenre } from '@/types';
import { generateSceneImage, getSceneImages, selectSceneImage } from '@/lib/apiClient';
import { formatGenreName } from '@/utils/formatters';
import SceneSidebar from './SceneSidebar';
import ScenePromptEditor from './ScenePromptEditor';
import SceneImageCanvas from './SceneImageCanvas';
import SceneContextPanel from './SceneContextPanel';

interface SceneImageGeneratorProps {
  webtoonScript: WebtoonScript;
  genre?: StoryGenre;
}

export default function SceneImageGenerator({ webtoonScript, genre: propGenre }: SceneImageGeneratorProps) {
  const [currentPanelIndex, setCurrentPanelIndex] = useState(0);
  const [panelPrompts, setPanelPrompts] = useState<Record<number, string>>({});
  const [lockedPanels, setLockedPanels] = useState<Set<number>>(new Set());
  const [sceneImages, setSceneImages] = useState<Record<number, SceneImage[]>>({});
  const [currentImageIndices, setCurrentImageIndices] = useState<Record<number, number>>({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Get genre from prop or sessionStorage
  const genre = propGenre || (typeof window !== 'undefined'
    ? (sessionStorage.getItem('selectedGenre') as StoryGenre) || 'MODERN_ROMANCE_DRAMA_MANHWA'
    : 'MODERN_ROMANCE_DRAMA_MANHWA');

  const panels = webtoonScript.panels;
  const currentPanel = panels[currentPanelIndex];
  
  // Initialize prompts from panels
  useEffect(() => {
    const initialPrompts: Record<number, string> = {};
    panels.forEach(panel => {
      initialPrompts[panel.panel_number] = panel.visual_prompt;
    });
    setPanelPrompts(initialPrompts);
  }, [panels]);

  // Get current prompt
  const currentPrompt = panelPrompts[currentPanel?.panel_number] || currentPanel?.visual_prompt || '';
  const originalPrompt = currentPanel?.visual_prompt || '';

  // Get current images for this panel
  const currentPanelImages = sceneImages[currentPanel?.panel_number] || [];
  const currentImageIndex = currentImageIndices[currentPanel?.panel_number] || 0;
  const currentImage = currentPanelImages[currentImageIndex] || null;

  // Build scene images map for sidebar (selected image URL per panel)
  const sidebarSceneImages: Record<number, string | null> = {};
  panels.forEach(panel => {
    const images = sceneImages[panel.panel_number] || [];
    const selected = images.find(img => img.is_selected) || images[0];
    sidebarSceneImages[panel.panel_number] = selected?.image_url || null;
  });

  const handlePromptChange = (prompt: string) => {
    if (!lockedPanels.has(currentPanel.panel_number)) {
      setPanelPrompts(prev => ({
        ...prev,
        [currentPanel.panel_number]: prompt,
      }));
    }
  };

  const handleLockToggle = () => {
    setLockedPanels(prev => {
      const newSet = new Set(prev);
      if (newSet.has(currentPanel.panel_number)) {
        newSet.delete(currentPanel.panel_number);
      } else {
        newSet.add(currentPanel.panel_number);
      }
      return newSet;
    });
  };

  const handleGenerateImage = async () => {
    if (!currentPanel || isGenerating) return;
    
    setIsGenerating(true);
    setError(null);
    
    try {
      const newImage = await generateSceneImage({
        script_id: webtoonScript.script_id,
        panel_number: currentPanel.panel_number,
        visual_prompt: currentPrompt,
        genre: genre,
      });
      
      // Add new image to state
      setSceneImages(prev => ({
        ...prev,
        [currentPanel.panel_number]: [...(prev[currentPanel.panel_number] || []), newImage],
      }));
      
      // Set to newest image
      setCurrentImageIndices(prev => ({
        ...prev,
        [currentPanel.panel_number]: (sceneImages[currentPanel.panel_number]?.length || 0),
      }));
      
    } catch (err) {
      console.error('Scene image generation error:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate scene image');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSelectImage = async () => {
    if (!currentImage) return;
    
    try {
      await selectSceneImage(webtoonScript.script_id, currentPanel.panel_number, currentImage.id);
      
      // Update local state
      setSceneImages(prev => ({
        ...prev,
        [currentPanel.panel_number]: prev[currentPanel.panel_number].map(img => ({
          ...img,
          is_selected: img.id === currentImage.id,
        })),
      }));
    } catch (err) {
      console.error('Select scene image error:', err);
    }
  };

  const handleDownloadImage = () => {
    if (!currentImage) return;
    
    const base64Match = currentImage.image_url.match(/^data:([^;]+);base64,(.+)$/);
    if (!base64Match) return;
    
    const mimeType = base64Match[1];
    const base64Data = base64Match[2];
    const ext = mimeType.split('/')[1] || 'png';
    
    try {
      const binaryString = atob(base64Data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      const blob = new Blob([bytes], { type: mimeType });
      const blobUrl = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = `scene_${currentPanel.panel_number}.${ext}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setTimeout(() => URL.revokeObjectURL(blobUrl), 100);
    } catch (error) {
      console.error('Download error:', error);
    }
  };

  const handlePrevPanel = () => {
    setCurrentPanelIndex(prev => Math.max(0, prev - 1));
  };

  const handleNextPanel = () => {
    setCurrentPanelIndex(prev => Math.min(panels.length - 1, prev + 1));
  };

  if (!currentPanel) {
    return (
      <div className="text-center p-8">
        <p className="text-gray-500">No panels available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Genre Badge */}
      <div className="flex items-center justify-center gap-2 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
        <span className="text-sm font-semibold text-gray-700">Selected Genre:</span>
        <span className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-full text-sm font-bold shadow-md">
          🎭 {formatGenreName(genre)}
        </span>
      </div>

      {/* Main Layout */}
      <div className="flex gap-4">
        {/* Left Sidebar - Scene List */}
        <SceneSidebar
          panels={panels}
          currentPanelIndex={currentPanelIndex}
          onPanelSelect={setCurrentPanelIndex}
          sceneImages={sidebarSceneImages}
        />
        
        {/* Center Content */}
        <div className="flex-1 space-y-4">
          {/* Prompt Editor */}
          <ScenePromptEditor
            prompt={currentPrompt}
            originalPrompt={originalPrompt}
            onPromptChange={handlePromptChange}
            isLocked={lockedPanels.has(currentPanel.panel_number)}
            onLockToggle={handleLockToggle}
          />
          
          {/* Image Canvas */}
          <SceneImageCanvas
            image={currentImage}
            isGenerating={isGenerating}
            panelNumber={currentPanel.panel_number}
          />
          
          {/* Error display */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}
        </div>
        
        {/* Right Sidebar - Context Panel */}
        <SceneContextPanel
          panel={currentPanel}
          onGenerateImage={handleGenerateImage}
          isGenerating={isGenerating}
        />
      </div>
      
      {/* Bottom Navigation */}
      <div className="flex items-center justify-center gap-6 py-4">
        <button
          onClick={handlePrevPanel}
          disabled={currentPanelIndex === 0}
          className={`
            p-3 rounded-lg transition-all
            ${currentPanelIndex === 0
              ? 'text-gray-300 cursor-not-allowed'
              : 'text-blue-800 hover:bg-blue-100'
            }
          `}
        >
          <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        </button>
        
        <button
          onClick={handleSelectImage}
          disabled={!currentImage}
          className={`
            px-8 py-3 rounded-lg font-bold transition-all
            ${currentImage
              ? currentImage.is_selected
                ? 'bg-green-600 text-white'
                : 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          {currentImage?.is_selected ? '✓ SELECTED' : 'SELECT'}
        </button>
        
        <button
          onClick={handleDownloadImage}
          disabled={!currentImage}
          className={`
            px-6 py-3 rounded-lg font-semibold transition-all flex items-center gap-2
            ${currentImage
              ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }
          `}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          DOWNLOAD
        </button>
        
        <button
          onClick={handleNextPanel}
          disabled={currentPanelIndex === panels.length - 1}
          className={`
            p-3 rounded-lg transition-all
            ${currentPanelIndex === panels.length - 1
              ? 'text-gray-300 cursor-not-allowed'
              : 'text-blue-800 hover:bg-blue-100'
            }
          `}
        >
          <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
  );
}
