'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { WebtoonScript, WebtoonPanel, SceneImage, StoryGenre, Character, DialogueBubble } from '@/types';
import { generateSceneImage, selectSceneImage } from '@/lib/apiClient';

interface SceneImageGeneratorV2Props {
  webtoonScript: WebtoonScript;
  genre?: StoryGenre;
  onUpdateScript?: (script: WebtoonScript) => void;
  onProceedToVideo?: () => void;
}

export default function SceneImageGeneratorV2({ webtoonScript, genre: propGenre, onUpdateScript, onProceedToVideo }: SceneImageGeneratorV2Props) {
  const [currentPanelIndex, setCurrentPanelIndex] = useState(0);
  const [panelPrompts, setPanelPrompts] = useState<Record<number, string>>({});
  // Removed local sceneImages and dialogueBubbles state in favor of webtoonScript prop
  const [currentImageIndices, setCurrentImageIndices] = useState<Record<number, number>>({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [draggedDialogue, setDraggedDialogue] = useState<{ text: string; characterName: string } | null>(null);
  
  // UX State
  const [dragPreviewPos, setDragPreviewPos] = useState<{x: number, y: number} | null>(null);
  const [resizingBubble, setResizingBubble] = useState<{ 
    id: string; 
    startX: number; 
    startY: number; 
    startWidth: number; 
    startHeight: number 
  } | null>(null);
  
  const canvasRef = useRef<HTMLDivElement>(null);
  const prevImagesLengthRef = useRef<Record<number, number>>({});
  
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

  // Track new images and auto-navigate
  useEffect(() => {
    if (currentPanel) {
      const panelImages = webtoonScript.scene_images?.[currentPanel.panel_number] || [];
      const prevLength = prevImagesLengthRef.current[currentPanel.panel_number] || 0;
      
      if (panelImages.length > prevLength) {
        setCurrentImageIndices(prev => ({
          ...prev,
          [currentPanel.panel_number]: panelImages.length - 1,
        }));
      }
      prevImagesLengthRef.current[currentPanel.panel_number] = panelImages.length;
    }
  }, [webtoonScript.scene_images, currentPanel]);

  // Handle Resize Logic
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!resizingBubble || !canvasRef.current || !onUpdateScript) return;

      const rect = canvasRef.current.getBoundingClientRect();
      const deltaX = ((e.clientX - resizingBubble.startX) / rect.width) * 100;
      const deltaY = ((e.clientY - resizingBubble.startY) / rect.height) * 100;

      const newWidth = Math.max(10, resizingBubble.startWidth + deltaX); // Min 10% width
      const newHeight = Math.max(5, resizingBubble.startHeight + deltaY); // Min 5% height

      const updatedBubbles = { ...(webtoonScript.dialogue_bubbles || {}) };
      if (updatedBubbles[currentPanel.panel_number]) {
        updatedBubbles[currentPanel.panel_number] = updatedBubbles[currentPanel.panel_number].map(b => 
          b.id === resizingBubble.id ? { ...b, width: newWidth, height: newHeight } : b
        );
        onUpdateScript({
          ...webtoonScript,
          dialogue_bubbles: updatedBubbles
        });
      }
    };

    const handleMouseUp = () => {
      setResizingBubble(null);
    };

    if (resizingBubble) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [resizingBubble, currentPanel, onUpdateScript, webtoonScript]);

  // Get current state values
  const currentPrompt = panelPrompts[currentPanel?.panel_number] || currentPanel?.visual_prompt || '';
  const currentPanelImages = webtoonScript.scene_images?.[currentPanel?.panel_number] || [];
  const currentImageIndex = currentImageIndices[currentPanel?.panel_number] || 0;
  const currentImage = currentPanelImages[currentImageIndex] || null;
  const currentBubbles = webtoonScript.dialogue_bubbles?.[currentPanel?.panel_number] || [];

  // Parse dialogue from panel
  const parseDialogues = (dialogue: any): { characterName: string; text: string }[] => {
    if (!dialogue) return [];
    
    // Check if dialogue is already in list object format
    if (Array.isArray(dialogue)) {
      return dialogue.map((line: any) => ({
        characterName: line.character || 'Character',
        text: line.text || ''
      }));
    }

    // Handle legacy string format
    if (typeof dialogue === 'string') {
      // Format: "[character_name: dialogue, character_name: dialogue, ...]"
      const dialogues: { characterName: string; text: string }[] = [];
      const regex = /\[?([^:\]]+):\s*([^\],]+)\]?/g;
      let match;
      
      while ((match = regex.exec(dialogue)) !== null) {
        dialogues.push({
          characterName: match[1].trim(),
          text: match[2].trim(),
        });
      }
      
      // If no matches, try splitting by newlines
      if (dialogues.length === 0 && dialogue.trim()) {
        dialogue.split('\n').filter(line => line.trim()).forEach(line => {
          dialogues.push({ characterName: 'Character', text: line.trim() });
        });
      }
      
      return dialogues;
    }
    
    return [];
  };

  const currentDialogues = parseDialogues(currentPanel?.dialogue);

  const handlePromptChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPanelPrompts(prev => ({
      ...prev,
      [currentPanel.panel_number]: e.target.value,
    }));
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
      
      if (onUpdateScript) {
        const updatedSceneImages = { ...(webtoonScript.scene_images || {}) };
        updatedSceneImages[currentPanel.panel_number] = [
          ...(updatedSceneImages[currentPanel.panel_number] || []),
          newImage
        ];
        
        onUpdateScript({
          ...webtoonScript,
          scene_images: updatedSceneImages
        });
      }
      
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
      
      if (onUpdateScript) {
        const updatedSceneImages = { ...(webtoonScript.scene_images || {}) };
        if (updatedSceneImages[currentPanel.panel_number]) {
          updatedSceneImages[currentPanel.panel_number] = updatedSceneImages[currentPanel.panel_number].map(img => ({
            ...img,
            is_selected: img.id === currentImage.id,
          }));
        }
        
        onUpdateScript({
          ...webtoonScript,
          scene_images: updatedSceneImages
        });
      }
    } catch (err) {
      console.error('Select scene image error:', err);
    }
  };

  const handlePrevImage = () => {
    setCurrentImageIndices(prev => ({
      ...prev,
      [currentPanel.panel_number]: Math.max(0, (prev[currentPanel.panel_number] || 0) - 1),
    }));
  };

  const handleNextImage = () => {
    const maxIndex = currentPanelImages.length - 1;
    setCurrentImageIndices(prev => ({
      ...prev,
      [currentPanel.panel_number]: Math.min(maxIndex, (prev[currentPanel.panel_number] || 0) + 1),
    }));
  };

  const handleDownload = () => {
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
      link.download = `scene_panel_${currentPanel.panel_number}_v${currentImageIndex + 1}.${ext}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setTimeout(() => URL.revokeObjectURL(blobUrl), 100);
    } catch (error) {
      console.error('Download error:', error);
    }
  };

  // Drag and Drop handlers
  const handleDragStart = (dialogue: { characterName: string; text: string }) => {
    setDraggedDialogue(dialogue);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
    
    if (canvasRef.current && draggedDialogue) {
      const rect = canvasRef.current.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      setDragPreviewPos({ x, y });
    }
  };

  const handleDragLeave = () => {
    setDragPreviewPos(null);
  };
    
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragPreviewPos(null);
    
    if (!draggedDialogue || !canvasRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    
    const newBubble: DialogueBubble = {
      id: `bubble-${Date.now()}`,
      text: draggedDialogue.text,
      characterName: draggedDialogue.characterName,
      x: Math.max(5, Math.min(85, x)),
      y: Math.max(5, Math.min(85, y)),
      width: 30, // Default width %
      height: 15, // Default height %
    };
    
    if (onUpdateScript) {
      const updatedBubbles = { ...(webtoonScript.dialogue_bubbles || {}) };
      updatedBubbles[currentPanel.panel_number] = [
        ...(updatedBubbles[currentPanel.panel_number] || []),
        newBubble
      ];
      
      onUpdateScript({
        ...webtoonScript,
        dialogue_bubbles: updatedBubbles
      });
    }
    
    setDraggedDialogue(null);
  };

  const handleRemoveBubble = (bubbleId: string) => {
    if (onUpdateScript) {
      const updatedBubbles = { ...(webtoonScript.dialogue_bubbles || {}) };
      if (updatedBubbles[currentPanel.panel_number]) {
        updatedBubbles[currentPanel.panel_number] = updatedBubbles[currentPanel.panel_number].filter(b => b.id !== bubbleId);
      }
      
      onUpdateScript({
        ...webtoonScript,
        dialogue_bubbles: updatedBubbles
      });
    }
  };

  // Helper to format genre for display
  const formatGenreName = (g: StoryGenre): string => {
    return g.replace(/_/g, ' ').replace(/MANHWA/g, '').trim();
  };

  // Get character info for active characters in panel
  const getActiveCharacterInfo = (): Character[] => {
    if (!currentPanel) return [];
    const activeNames = currentPanel.active_character_names || [];
    return webtoonScript.characters.filter(c => activeNames.includes(c.name));
  };

  // Check if all panels have a selected image
  const canProceedToVideo = panels.every(panel => {
    const images = webtoonScript.scene_images?.[panel.panel_number] || [];
    return images.some(img => img.is_selected);
  });

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
      <div className="flex items-center justify-center gap-2 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl border border-purple-200">
        <span className="text-sm font-semibold text-gray-700">Selected Genre:</span>
        <span className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-full text-sm font-bold shadow-md">
          🎭 {formatGenreName(genre)}
        </span>
      </div>

      {/* Main 3-Column Layout */}
      <div className="flex gap-4 min-h-[700px]">
        
        {/* LEFT: Scene List */}
        <div className="w-48 bg-white rounded-xl shadow-lg p-3 overflow-y-auto">
          <h3 className="text-sm font-bold text-gray-800 mb-3 px-2">📑 Scenes</h3>
          <div className="space-y-2">
            {panels.map((panel, index) => {
              const panelImages = webtoonScript.scene_images?.[panel.panel_number] || [];
              const hasImage = panelImages.length > 0;
              const isSelected = index === currentPanelIndex;
              
              return (
                <button
                  key={panel.panel_number}
                  onClick={() => setCurrentPanelIndex(index)}
                  className={`
                    w-full p-2 rounded-lg text-left transition-all
                    ${isSelected 
                      ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-md' 
                      : 'bg-gray-50 hover:bg-gray-100 text-gray-700'}
                  `}
                >
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-bold ${isSelected ? 'text-white' : 'text-gray-500'}`}>
                      #{panel.panel_number}
                    </span>
                    {hasImage && (
                      <span className="text-xs">✅</span>
                    )}
                  </div>
                  <p className={`text-xs mt-1 line-clamp-2 ${isSelected ? 'text-purple-100' : 'text-gray-500'}`}>
                    {panel.shot_type}
                  </p>
                </button>
              );
            })}
          </div>
        </div>

        {/* CENTER: Image Canvas */}
        <div className="flex-1 bg-white rounded-xl shadow-lg p-4 flex flex-col">
          {/* Scene Info Header */}
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-lg font-bold text-gray-900">
                Panel #{currentPanel.panel_number}
              </h3>
              <p className="text-sm text-gray-500">{currentPanel.shot_type}</p>
            </div>
            <div className="flex items-center gap-2">
              {getActiveCharacterInfo().map(char => (
                <span 
                  key={char.name}
                  className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium"
                >
                  {char.name}
                </span>
              ))}
            </div>
          </div>

          {/* Prompt Editor */}
          <div className="mb-3">
            <textarea
              value={currentPrompt}
              onChange={handlePromptChange}
              rows={3}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 text-sm resize-none"
              placeholder="Visual prompt for this scene..."
            />
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerateImage}
            disabled={isGenerating}
            className={`
              w-full py-3 rounded-lg font-bold text-white mb-4 transition-all
              ${isGenerating
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:shadow-lg hover:scale-[1.02]'
              }
            `}
          >
            {isGenerating ? (
              <span className="flex items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                Generating...
              </span>
            ) : (
              <span>🎨 Generate Scene Image</span>
            )}
          </button>

          {/* Image Canvas with Drop Zone */}
          <div 
            ref={canvasRef}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`
              flex-1 relative bg-gray-100 rounded-lg overflow-hidden min-h-[400px]
              ${draggedDialogue ? 'ring-4 ring-purple-400 ring-opacity-50' : ''}
            `}
          >
            {currentImage ? (
              <>
                <img
                  src={currentImage.image_url}
                  alt={`Scene Panel ${currentPanel.panel_number}`}
                  className="w-full h-full object-contain"
                />
                
                {/* Dialogue Bubbles Overlay */}
                {currentBubbles.map(bubble => {
                  const width = bubble.width || 30;
                  const height = bubble.height || 15;
                  
                  return (
                    <div
                      key={bubble.id}
                      style={{ 
                        left: `${bubble.x}%`, 
                        top: `${bubble.y}%`,
                        width: `${width}%`,
                        height: `${height}%`,
                        fontSize: `clamp(10px, ${Math.max(0.8, height / 10)}vw, 24px)`,
                        backgroundColor: 'rgba(255, 255, 255, 0.3)',
                        border: '2px solid #4a4a4a',
                      }}
                      className="absolute rounded-xl px-4 py-2 backdrop-blur-sm cursor-move group select-none flex items-center justify-center text-center overflow-hidden"
                      onClick={(e) => {
                        e.stopPropagation();
                      }}
                    >
                      {/* Tail */}
                      <div 
                        className="absolute -bottom-2 left-4 w-4 h-4 transform rotate-45" 
                        style={{ 
                          backgroundColor: 'rgba(255, 255, 255, 0.3)',
                          borderRight: '2px solid #4a4a4a',
                          borderBottom: '2px solid #4a4a4a',
                        }}
                      />
                      
                      {/* Content - Text only, no name */}
                      <div className="w-full h-full flex flex-col items-center justify-center overflow-hidden">
                        <p className="text-gray-900 font-medium leading-tight w-full break-words" style={{ fontSize: '1em' }}>{bubble.text}</p>
                      </div>

                      {/* Delete Button */}
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRemoveBubble(bubble.id);
                        }}
                        className="absolute -top-2 -right-2 hidden group-hover:flex w-5 h-5 bg-red-500 rounded-full items-center justify-center text-white text-xs z-20 shadow-sm hover:bg-red-600"
                      >
                        ×
                      </button>

                      {/* Resize Handle */}
                      <div 
                        className="absolute bottom-0 right-0 w-4 h-4 cursor-se-resize flex items-end justify-end p-0.5 z-20 opacity-0 group-hover:opacity-100 transition-opacity"
                        onMouseDown={(e) => {
                          e.stopPropagation();
                          e.preventDefault();
                          setResizingBubble({
                            id: bubble.id,
                            startX: e.clientX,
                            startY: e.clientY,
                            startWidth: width,
                            startHeight: height,
                          });
                        }}
                      >
                         <svg viewBox="0 0 10 10" className="w-3 h-3 text-purple-400 fill-current">
                           <path d="M10 10 H0 L10 0 Z" />
                         </svg>
                      </div>
                    </div>
                  );
                })}

                {/* Drag Preview (Ghost Bubble) */}
                {dragPreviewPos && draggedDialogue && (
                  <div
                    style={{ 
                      left: `${dragPreviewPos.x}%`, 
                      top: `${dragPreviewPos.y}%`,
                      width: '30%',
                      height: '15%',
                    }}
                    className="absolute bg-white/50 border-2 border-purple-400 border-dashed rounded-xl flex items-center justify-center pointer-events-none z-30"
                  >
                    <p className="text-purple-700 font-bold opacity-75 text-xs">Drop here</p>
                  </div>
                )}
              </>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-center text-gray-400">
                  <div className="text-6xl mb-4">🖼️</div>
                  <p className="text-lg font-medium">No image yet</p>
                  <p className="text-sm">Click "Generate Scene Image" to create</p>
                </div>
              </div>
            )}
            
            {/* Drop hint overlay */}
            {draggedDialogue && (
              <div className="absolute inset-0 bg-purple-500 bg-opacity-20 flex items-center justify-center pointer-events-none">
                <div className="bg-white px-6 py-3 rounded-full shadow-lg">
                  <p className="text-purple-700 font-semibold">Drop dialogue here to create bubble</p>
                </div>
              </div>
            )}
          </div>

          {/* Image Navigation */}
          {currentPanelImages.length > 1 && (
            <div className="flex items-center justify-center gap-4 mt-4">
              <button
                onClick={handlePrevImage}
                disabled={currentImageIndex === 0}
                className={`
                  p-2 rounded-lg transition-all
                  ${currentImageIndex === 0
                    ? 'text-gray-300 cursor-not-allowed'
                    : 'text-purple-600 hover:bg-purple-100'
                  }
                `}
              >
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </button>
              
              <span className="text-sm font-medium text-gray-600">
                {currentImageIndex + 1} / {currentPanelImages.length}
              </span>
              
              <button
                onClick={handleNextImage}
                disabled={currentImageIndex === currentPanelImages.length - 1}
                className={`
                  p-2 rounded-lg transition-all
                  ${currentImageIndex === currentPanelImages.length - 1
                    ? 'text-gray-300 cursor-not-allowed'
                    : 'text-purple-600 hover:bg-purple-100'
                  }
                `}
              >
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 mt-4">
            <button
              onClick={handleSelectImage}
              disabled={!currentImage}
              className={`
                flex-1 py-3 rounded-lg font-semibold transition-all flex items-center justify-center gap-2
                ${!currentImage
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : currentImage.is_selected
                    ? 'bg-green-600 text-white'
                    : 'bg-purple-600 text-white hover:bg-purple-700'
                }
              `}
            >
              {currentImage?.is_selected ? '✓ Selected' : 'Select as Reference'}
            </button>
            
            <button
              onClick={handleDownload}
              disabled={!currentImage}
              className={`
                flex-1 py-3 rounded-lg font-semibold transition-all flex items-center justify-center gap-2
                ${!currentImage
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
                }
              `}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download
            </button>
          </div>

          {/* Error display */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* RIGHT: Dialogue Panel */}
        <div className="w-64 bg-white rounded-xl shadow-lg p-4 flex flex-col">
          <h3 className="text-sm font-bold text-gray-800 mb-3">💬 Dialogues</h3>
          <p className="text-xs text-gray-500 mb-4">Drag dialogues onto the image to create speech bubbles</p>
          
          <div className="flex-1 space-y-3 overflow-y-auto">
            {currentDialogues.length > 0 ? (
              currentDialogues.map((dialogue, index) => (
                <div
                  key={index}
                  draggable
                  onDragStart={() => handleDragStart(dialogue)}
                  className="p-3 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200 cursor-grab active:cursor-grabbing hover:shadow-md transition-all"
                >
                  <p className="text-xs font-bold text-purple-700 mb-1">{dialogue.characterName}</p>
                  <p className="text-sm text-gray-800">{dialogue.text}</p>
                </div>
              ))
            ) : (
              <div className="text-center text-gray-400 py-8">
                <div className="text-4xl mb-2">💭</div>
                <p className="text-sm">No dialogue for this panel</p>
              </div>
            )}
          </div>

          {/* Bubbles placed indicator */}
          {currentBubbles.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                {currentBubbles.length} bubble(s) placed
              </p>
              <button
                onClick={() => {
                  if (onUpdateScript) {
                    const updatedBubbles = { ...(webtoonScript.dialogue_bubbles || {}) };
                    updatedBubbles[currentPanel.panel_number] = [];
                    onUpdateScript({
                      ...webtoonScript,
                      dialogue_bubbles: updatedBubbles
                    });
                  }
                }}
                className="mt-2 w-full py-2 text-xs text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                Clear all bubbles
              </button>
            </div>
          )}
        </div>
      </div>
      
      {/* Proceed to Video Button */}
      {onProceedToVideo && (
        <div className="mt-8 text-center border-t border-gray-200 pt-8">
          <button
            onClick={onProceedToVideo}
            disabled={!canProceedToVideo}
            className={`
              px-12 py-5 rounded-full font-bold text-xl transition-all shadow-lg flex items-center justify-center gap-3 mx-auto
              ${canProceedToVideo
                ? 'bg-gradient-to-r from-red-500 to-pink-600 text-white hover:shadow-xl hover:scale-105'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }
            `}
          >
            <span>🎬</span>
            <span>Create Media-Webtoon</span>
          </button>
          {!canProceedToVideo && (
            <p className="mt-3 text-sm text-red-500 font-medium bg-red-50 inline-block px-4 py-1 rounded-full">
              ⚠️ Please generate and select an image for every panel to proceed
            </p>
          )}
        </div>
      )}
    </div>
  );
}
