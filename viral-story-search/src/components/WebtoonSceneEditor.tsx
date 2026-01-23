'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { WebtoonScript, ImageStyle, PageImage, DialogueBubble } from '@/types';
import { formatGenreName } from '@/utils/formatters';
import { getScriptLayout, generatePageImage, selectPageImage } from '@/lib/apiClient';

interface WebtoonSceneEditorProps {
  webtoonScript: WebtoonScript;
  imageStyle: ImageStyle;
  onUpdateScript?: (script: WebtoonScript) => void;
}

interface PageLayout {
  page_number: number;
  panel_indices: number[];
  layout_type: string;
  is_single_panel: boolean;
  reasoning: string;
}

interface EditableDialogue {
  id: string;
  characterName: string;
  text: string;
  originalIndex: number;
  panelIndex: number;
}

export default function WebtoonSceneEditor({
  webtoonScript,
  imageStyle,
  onUpdateScript
}: WebtoonSceneEditorProps) {
  // Layout & Navigation State
  const [layout, setLayout] = useState<PageLayout[]>([]);
  const [selectedSceneIndex, setSelectedSceneIndex] = useState(0);

  // Generated Images State
  const [generatedPages, setGeneratedPages] = useState<Record<number, PageImage[]>>({});
  const [currentImageIndices, setCurrentImageIndices] = useState<Record<number, number>>({});

  // Bubbles State (per page)
  const [pageBubbles, setPageBubbles] = useState<Record<number, DialogueBubble[]>>({});

  // Editable Dialogues State
  const [editableDialogues, setEditableDialogues] = useState<EditableDialogue[]>([]);

  // UI State
  const [isGenerating, setIsGenerating] = useState<Record<number, boolean>>({});
  const [isGeneratingAll, setIsGeneratingAll] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Drag State
  const [draggedDialogue, setDraggedDialogue] = useState<EditableDialogue | null>(null);
  const [draggingBubble, setDraggingBubble] = useState<{
    id: string;
    startX: number;
    startY: number;
    startBubbleX: number;
    startBubbleY: number;
  } | null>(null);
  const [resizingBubble, setResizingBubble] = useState<{
    id: string;
    startX: number;
    startY: number;
    startWidth: number;
    startHeight: number;
  } | null>(null);

  const canvasRef = useRef<HTMLDivElement | null>(null);

  // Get current scene
  const currentScene = layout[selectedSceneIndex];
  const currentPageNumber = currentScene?.page_number || 1;
  const currentImages = generatedPages[currentPageNumber] || [];
  const currentImageIndex = currentImageIndices[currentPageNumber] || 0;
  const currentImage = currentImages[currentImageIndex];
  const currentBubbles = pageBubbles[currentPageNumber] || [];

  // Initialize layout
  useEffect(() => {
    const fetchLayout = async () => {
      try {
        setIsLoading(true);
        const layoutData = await getScriptLayout(webtoonScript.script_id);
        setLayout(layoutData);
      } catch (err) {
        console.error('Failed to load layout:', err);
        setError('Failed to load page layout. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    if (webtoonScript.script_id) {
      fetchLayout();
    }
  }, [webtoonScript.script_id]);

  // Load existing images and bubbles
  useEffect(() => {
    if (webtoonScript.page_images) {
      setGeneratedPages(webtoonScript.page_images);

      const initialIndices: Record<number, number> = {};
      Object.entries(webtoonScript.page_images).forEach(([pageNumStr, images]) => {
        const pageNum = parseInt(pageNumStr);
        const selectedIdx = images.findIndex(img => img.is_selected);
        initialIndices[pageNum] = selectedIdx >= 0 ? selectedIdx : images.length - 1;
      });
      setCurrentImageIndices(initialIndices);
    }

    if (webtoonScript.page_dialogue_bubbles) {
      setPageBubbles(webtoonScript.page_dialogue_bubbles);
    }
  }, [webtoonScript.page_images, webtoonScript.page_dialogue_bubbles]);

  // Update editable dialogues when scene changes
  useEffect(() => {
    if (!currentScene) return;

    const dialogues: EditableDialogue[] = [];
    currentScene.panel_indices.forEach((panelIdx) => {
      const panel = webtoonScript.panels[panelIdx];
      if (!panel?.dialogue || !Array.isArray(panel.dialogue)) return;

      panel.dialogue.forEach((d: any, idx: number) => {
        dialogues.push({
          id: `${panelIdx}-${idx}`,
          characterName: d.character || 'Unknown',
          text: d.text || '',
          originalIndex: idx,
          panelIndex: panelIdx
        });
      });
    });

    setEditableDialogues(dialogues);
  }, [currentScene, webtoonScript.panels]);

  // Update script bubbles
  const updateScriptBubbles = useCallback((pageNum: number, bubbles: DialogueBubble[]) => {
    if (onUpdateScript) {
      const updatedBubbles = { ...(webtoonScript.page_dialogue_bubbles || {}), [pageNum]: bubbles };
      onUpdateScript({
        ...webtoonScript,
        page_dialogue_bubbles: updatedBubbles
      });
    }
  }, [onUpdateScript, webtoonScript]);

  // Generate single page
  const handleGeneratePage = async (page: PageLayout) => {
    if (isGenerating[page.page_number]) return;

    setIsGenerating(prev => ({ ...prev, [page.page_number]: true }));

    try {
      const newImage = await generatePageImage(
        webtoonScript.script_id,
        page.page_number,
        page.panel_indices,
        [imageStyle]
      );

      setGeneratedPages(prev => {
        const currentList = prev[page.page_number] || [];
        return {
          ...prev,
          [page.page_number]: [...currentList, newImage]
        };
      });

      setCurrentImageIndices(prev => ({
        ...prev,
        [page.page_number]: (generatedPages[page.page_number]?.length || 0)
      }));

    } catch (err) {
      console.error(`Failed to generate page ${page.page_number}:`, err);
    } finally {
      setIsGenerating(prev => ({ ...prev, [page.page_number]: false }));
    }
  };

  // Generate all pages
  const handleGenerateAll = async () => {
    if (isGeneratingAll) return;
    setIsGeneratingAll(true);

    for (const page of layout) {
      if (!generatedPages[page.page_number]?.length) {
        await handleGeneratePage(page);
      }
    }

    setIsGeneratingAll(false);
  };

  // Select image
  const handleSelectImage = async (pageNumber: number, imageId: string) => {
    try {
      await selectPageImage(webtoonScript.script_id, imageId);

      setGeneratedPages(prev => {
        const images = prev[pageNumber] || [];
        const updatedImages = images.map(img => ({
          ...img,
          is_selected: img.id === imageId
        }));

        if (onUpdateScript) {
          onUpdateScript({
            ...webtoonScript,
            page_images: {
              ...(webtoonScript.page_images || {}),
              [pageNumber]: updatedImages
            }
          });
        }

        return {
          ...prev,
          [pageNumber]: updatedImages
        };
      });
    } catch (err) {
      console.error("Failed to select image:", err);
    }
  };

  // Update dialogue text
  const handleDialogueTextChange = (dialogueId: string, newText: string) => {
    setEditableDialogues(prev =>
      prev.map(d => d.id === dialogueId ? { ...d, text: newText } : d)
    );
  };

  // Drag start from dialogue list
  const handleDragStart = (e: React.DragEvent, dialogue: EditableDialogue) => {
    setDraggedDialogue(dialogue);
    e.dataTransfer.effectAllowed = 'copy';
  };

  // Drop on canvas
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (!draggedDialogue || !canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;

    const newBubble: DialogueBubble = {
      id: `bubble-${Date.now()}`,
      text: draggedDialogue.text,
      characterName: draggedDialogue.characterName,
      x: Math.max(5, Math.min(95, x)),
      y: Math.max(5, Math.min(95, y)),
      width: 35,
      height: 12
    };

    const newPageBubbles = [...currentBubbles, newBubble];
    setPageBubbles(prev => ({
      ...prev,
      [currentPageNumber]: newPageBubbles
    }));
    updateScriptBubbles(currentPageNumber, newPageBubbles);

    setDraggedDialogue(null);
  };

  // Bubble drag/resize handlers
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!canvasRef.current) return;
      const rect = canvasRef.current.getBoundingClientRect();

      if (draggingBubble) {
        const deltaX = ((e.clientX - draggingBubble.startX) / rect.width) * 100;
        const deltaY = ((e.clientY - draggingBubble.startY) / rect.height) * 100;

        setPageBubbles(prev => {
          const list = prev[currentPageNumber] || [];
          return {
            ...prev,
            [currentPageNumber]: list.map(b =>
              b.id === draggingBubble.id
                ? { ...b, x: draggingBubble.startBubbleX + deltaX, y: draggingBubble.startBubbleY + deltaY }
                : b
            )
          };
        });
      }

      if (resizingBubble) {
        const deltaX = ((e.clientX - resizingBubble.startX) / rect.width) * 100;
        const deltaY = ((e.clientY - resizingBubble.startY) / rect.height) * 100;

        setPageBubbles(prev => {
          const list = prev[currentPageNumber] || [];
          return {
            ...prev,
            [currentPageNumber]: list.map(b =>
              b.id === resizingBubble.id
                ? { ...b, width: Math.max(15, resizingBubble.startWidth + deltaX), height: Math.max(8, resizingBubble.startHeight + deltaY) }
                : b
            )
          };
        });
      }
    };

    const handleMouseUp = () => {
      if (draggingBubble || resizingBubble) {
        updateScriptBubbles(currentPageNumber, pageBubbles[currentPageNumber] || []);
        setDraggingBubble(null);
        setResizingBubble(null);
      }
    };

    if (draggingBubble || resizingBubble) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [draggingBubble, resizingBubble, currentPageNumber, pageBubbles, updateScriptBubbles]);

  // Delete bubble
  const handleDeleteBubble = (bubbleId: string) => {
    const newBubbles = currentBubbles.filter(b => b.id !== bubbleId);
    setPageBubbles(prev => ({
      ...prev,
      [currentPageNumber]: newBubbles
    }));
    updateScriptBubbles(currentPageNumber, newBubbles);
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-gray-500">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-purple-600 mb-4"></div>
        <p>Analyzing script structure...</p>
      </div>
    );
  }

  if (error) {
    return <div className="p-8 text-red-600 bg-red-50 rounded-xl">{error}</div>;
  }

  return (
    <div className="h-[calc(100vh-200px)] min-h-[700px] flex flex-col bg-gray-100 rounded-xl overflow-hidden">
      {/* Top Header */}
      <div className="bg-white px-6 py-4 border-b border-gray-200 flex items-center justify-between shrink-0">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Scene Editor</h2>
          <p className="text-sm text-gray-500">
            {layout.length} scenes | Style: {formatGenreName(imageStyle)}
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleGenerateAll}
            disabled={isGeneratingAll}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
              isGeneratingAll
                ? 'bg-gray-200 text-gray-500'
                : 'bg-gradient-to-r from-purple-600 to-blue-500 text-white hover:shadow-lg'
            }`}
          >
            {isGeneratingAll ? 'Generating...' : 'Generate All Scenes'}
          </button>
        </div>
      </div>

      {/* Main 3-Column Layout */}
      <div className="flex-1 flex overflow-hidden">

        {/* LEFT: Scene List */}
        <div className="w-48 bg-white border-r border-gray-200 flex flex-col shrink-0">
          <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
            <h3 className="font-semibold text-gray-700 text-sm">Scenes</h3>
          </div>
          <div className="flex-1 overflow-y-auto">
            {layout.map((page, index) => {
              const hasImage = (generatedPages[page.page_number]?.length || 0) > 0;
              const isSelected = index === selectedSceneIndex;
              const isPageGenerating = isGenerating[page.page_number];

              return (
                <button
                  key={page.page_number}
                  onClick={() => setSelectedSceneIndex(index)}
                  className={`w-full px-4 py-3 text-left border-b border-gray-100 transition-all ${
                    isSelected
                      ? 'bg-purple-50 border-l-4 border-l-purple-600'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className={`font-medium ${isSelected ? 'text-purple-700' : 'text-gray-700'}`}>
                      Scene {page.page_number}
                    </span>
                    {isPageGenerating ? (
                      <span className="w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></span>
                    ) : hasImage ? (
                      <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    ) : (
                      <span className="w-2 h-2 bg-gray-300 rounded-full"></span>
                    )}
                  </div>
                  <div className="mt-1 text-xs text-gray-500">
                    {page.panel_indices.length} panel{page.panel_indices.length > 1 ? 's' : ''}
                    <span className="ml-2 text-purple-600">{page.layout_type.replace('_', ' ')}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* MIDDLE: Image Canvas */}
        <div className="flex-1 flex flex-col bg-gray-900 min-w-0">
          {/* Image Controls Bar */}
          <div className="bg-gray-800 px-4 py-2 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-4">
              <span className="text-white font-medium">Scene {currentPageNumber}</span>
              {currentImages.length > 0 && (
                <span className="text-gray-400 text-sm">
                  Version {currentImageIndex + 1} / {currentImages.length}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button
                disabled={currentImageIndex <= 0}
                onClick={() => setCurrentImageIndices(p => ({ ...p, [currentPageNumber]: currentImageIndex - 1 }))}
                className="px-3 py-1 bg-gray-700 text-white rounded hover:bg-gray-600 disabled:opacity-30 text-sm"
              >
                ← Prev
              </button>
              <button
                disabled={currentImageIndex >= currentImages.length - 1}
                onClick={() => setCurrentImageIndices(p => ({ ...p, [currentPageNumber]: currentImageIndex + 1 }))}
                className="px-3 py-1 bg-gray-700 text-white rounded hover:bg-gray-600 disabled:opacity-30 text-sm"
              >
                Next →
              </button>
              <div className="w-px h-6 bg-gray-600 mx-2"></div>
              <button
                onClick={() => currentImage && handleSelectImage(currentPageNumber, currentImage.id)}
                disabled={!currentImage}
                className={`px-3 py-1 rounded text-sm font-medium ${
                  currentImage?.is_selected
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-700 text-white hover:bg-gray-600'
                }`}
              >
                {currentImage?.is_selected ? '✓ Selected' : 'Select'}
              </button>
              <button
                onClick={() => currentScene && handleGeneratePage(currentScene)}
                disabled={isGenerating[currentPageNumber]}
                className="px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-500 text-sm font-medium"
              >
                {isGenerating[currentPageNumber] ? 'Generating...' : '+ Generate New'}
              </button>
            </div>
          </div>

          {/* Image Canvas Area */}
          <div className="flex-1 flex items-center justify-center p-4 overflow-hidden">
            {currentImage ? (
              <div
                ref={canvasRef}
                className="relative max-h-full max-w-full"
                style={{ aspectRatio: '9/16' }}
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={currentImage.image_url}
                  alt={`Scene ${currentPageNumber}`}
                  className="h-full w-full object-contain rounded-lg shadow-2xl"
                  draggable={false}
                />

                {/* Dialogue Bubbles Overlay */}
                {currentBubbles.map(bubble => (
                  <div
                    key={bubble.id}
                    className="absolute group"
                    style={{
                      left: `${bubble.x}%`,
                      top: `${bubble.y}%`,
                      width: `${bubble.width}%`,
                      minHeight: `${bubble.height}%`,
                      transform: 'translate(-50%, -50%)',
                    }}
                  >
                    <div
                      className="bg-white border-2 border-black rounded-xl p-2 shadow-lg cursor-move"
                      onMouseDown={(e) => {
                        e.stopPropagation();
                        setDraggingBubble({
                          id: bubble.id,
                          startX: e.clientX,
                          startY: e.clientY,
                          startBubbleX: bubble.x,
                          startBubbleY: bubble.y,
                        });
                      }}
                    >
                      <div className="text-xs leading-tight">
                        <span className="font-bold text-purple-700 block mb-1">{bubble.characterName}</span>
                        <span className="text-gray-800">{bubble.text}</span>
                      </div>

                      {/* Bubble tail */}
                      <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-[8px] border-l-transparent border-r-[8px] border-r-transparent border-t-[10px] border-t-white"></div>
                      <div className="absolute -bottom-[11px] left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-[9px] border-l-transparent border-r-[9px] border-r-transparent border-t-[11px] border-t-black -z-10"></div>
                    </div>

                    {/* Resize Handle */}
                    <div
                      className="absolute bottom-0 right-0 w-4 h-4 bg-purple-500 rounded-tl cursor-se-resize opacity-0 group-hover:opacity-100 transition-opacity"
                      onMouseDown={(e) => {
                        e.stopPropagation();
                        setResizingBubble({
                          id: bubble.id,
                          startX: e.clientX,
                          startY: e.clientY,
                          startWidth: bubble.width ?? 35,
                          startHeight: bubble.height ?? 12,
                        });
                      }}
                    />

                    {/* Delete Button */}
                    <button
                      className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                      onClick={() => handleDeleteBubble(bubble.id)}
                    >
                      ×
                    </button>
                  </div>
                ))}

                {/* Drop Zone Indicator */}
                {draggedDialogue && (
                  <div className="absolute inset-0 border-4 border-dashed border-purple-400 rounded-lg bg-purple-500/10 pointer-events-none flex items-center justify-center">
                    <span className="bg-purple-600 text-white px-4 py-2 rounded-lg font-medium">
                      Drop here to place dialogue
                    </span>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center">
                <div className="w-32 h-56 bg-gray-800 rounded-lg mb-4 flex items-center justify-center mx-auto border-2 border-dashed border-gray-600">
                  <span className="text-gray-500 text-sm">No Image</span>
                </div>
                <button
                  onClick={() => currentScene && handleGeneratePage(currentScene)}
                  disabled={isGenerating[currentPageNumber]}
                  className={`px-6 py-3 rounded-lg font-medium text-white ${
                    isGenerating[currentPageNumber]
                      ? 'bg-gray-600'
                      : 'bg-gradient-to-r from-purple-600 to-blue-500 hover:shadow-lg'
                  }`}
                >
                  {isGenerating[currentPageNumber] ? 'Generating...' : 'Generate Scene Image'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT: Dialogue Panel */}
        <div className="w-80 bg-white border-l border-gray-200 flex flex-col shrink-0">
          <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
            <h3 className="font-semibold text-gray-700 text-sm">Dialogue</h3>
            <p className="text-xs text-gray-500 mt-1">Drag to image or edit text below</p>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {editableDialogues.length > 0 ? (
              editableDialogues.map((dialogue) => {
                // Check if this dialogue is already placed as a bubble
                const isPlaced = currentBubbles.some(
                  b => b.text === dialogue.text && b.characterName === dialogue.characterName
                );

                return (
                  <div
                    key={dialogue.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, dialogue)}
                    className={`p-3 rounded-lg border-2 transition-all cursor-grab active:cursor-grabbing ${
                      isPlaced
                        ? 'bg-green-50 border-green-200'
                        : 'bg-white border-gray-200 hover:border-purple-300 hover:shadow-md'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-purple-700 text-sm">{dialogue.characterName}</span>
                      {isPlaced && (
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Placed</span>
                      )}
                    </div>
                    <textarea
                      value={dialogue.text}
                      onChange={(e) => handleDialogueTextChange(dialogue.id, e.target.value)}
                      className="w-full text-sm text-gray-700 bg-gray-50 border border-gray-200 rounded p-2 resize-none focus:outline-none focus:ring-2 focus:ring-purple-300 focus:border-transparent"
                      rows={2}
                    />
                    <div className="mt-2 flex justify-end">
                      <span className="text-xs text-gray-400">Panel {dialogue.panelIndex + 1}</span>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center text-gray-400 py-8">
                <p className="text-sm">No dialogue for this scene</p>
              </div>
            )}
          </div>

          {/* Placed Bubbles Summary */}
          {currentBubbles.length > 0 && (
            <div className="border-t border-gray-200 p-4 bg-gray-50">
              <h4 className="font-medium text-gray-700 text-sm mb-2">
                Placed Bubbles ({currentBubbles.length})
              </h4>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {currentBubbles.map((bubble, idx) => (
                  <div key={bubble.id} className="flex items-center justify-between text-xs bg-white p-2 rounded border">
                    <span className="truncate flex-1">
                      <strong className="text-purple-700">{bubble.characterName}:</strong>{' '}
                      {bubble.text.substring(0, 30)}...
                    </span>
                    <button
                      onClick={() => handleDeleteBubble(bubble.id)}
                      className="ml-2 text-red-500 hover:text-red-700"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
