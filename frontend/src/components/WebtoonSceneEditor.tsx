'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { WebtoonScript, ImageStyle, PageImage, DialogueBubble, SfxEffect } from '@/types';
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

  // Custom dialogue input state
  const [showAddDialogue, setShowAddDialogue] = useState(false);
  const [newDialogueText, setNewDialogueText] = useState('');
  const [newDialogueCharacter, setNewDialogueCharacter] = useState('');

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

  // Sync state from props - carefully
  useEffect(() => {
    if (webtoonScript.page_images) {
      setGeneratedPages(prev => {
        // Only update if prop has more images or if local state is empty
        // This prevents "losing" newly generated images during re-render cycles
        const newPages = webtoonScript.page_images || {};
        const merged = { ...prev };
        
        Object.entries(newPages).forEach(([pageNumStr, images]) => {
          const pageNum = parseInt(pageNumStr);
          if (!merged[pageNum] || images.length >= merged[pageNum].length) {
            merged[pageNum] = images;
          }
        });
        return merged;
      });
      
      // Update indices only if they aren't set yet or if specifically needed
      setCurrentImageIndices(prev => {
        const newIndices = { ...prev };
        Object.entries(webtoonScript.page_images || {}).forEach(([pageNumStr, images]) => {
          const pageNum = parseInt(pageNumStr);
          if (newIndices[pageNum] === undefined) {
             const selectedIdx = images.findIndex(img => img.is_selected);
             newIndices[pageNum] = selectedIdx >= 0 ? selectedIdx : images.length - 1;
          }
        });
        return newIndices;
      });
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
        page_images: generatedPages, // CRITICAL: Use current local images so they aren't reverted to old script prop
        page_dialogue_bubbles: updatedBubbles
      });
    }
  }, [onUpdateScript, webtoonScript, generatedPages]);

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

      const currentList = generatedPages[page.page_number] || [];
      const newList = [...currentList, newImage];

      setGeneratedPages(prev => ({
        ...prev,
        [page.page_number]: newList
      }));

      setCurrentImageIndices(prev => ({
        ...prev,
        [page.page_number]: newList.length - 1
      }));

      // Sync to global script state AFTER updating local state
      if (onUpdateScript) {
        onUpdateScript({
          ...webtoonScript,
          page_images: {
            ...(webtoonScript.page_images || {}),
            [page.page_number]: newList
          }
        });
      }

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

      const images = generatedPages[pageNumber] || [];
      const updatedImages = images.map(img => ({
        ...img,
        is_selected: img.id === imageId
      }));

      setGeneratedPages(prev => ({
        ...prev,
        [pageNumber]: updatedImages
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

  // Add custom dialogue
  const handleAddCustomDialogue = () => {
    if (!newDialogueText.trim()) return;

    const newDialogue: EditableDialogue = {
      id: `custom-${Date.now()}`,
      characterName: newDialogueCharacter.trim() || 'Custom',
      text: newDialogueText.trim(),
      originalIndex: editableDialogues.length,
      panelIndex: -1, // -1 indicates custom dialogue
    };

    setEditableDialogues(prev => [...prev, newDialogue]);
    setNewDialogueText('');
    setNewDialogueCharacter('');
    setShowAddDialogue(false);
  };

  // Delete custom dialogue
  const handleDeleteDialogue = (dialogueId: string) => {
    // Only allow deleting custom dialogues (panelIndex === -1)
    setEditableDialogues(prev => prev.filter(d => d.id !== dialogueId || d.panelIndex !== -1));
  };

  // Move dialogue up in the list
  const handleMoveDialogueUp = (index: number) => {
    if (index <= 0) return;
    setEditableDialogues(prev => {
      const newList = [...prev];
      [newList[index - 1], newList[index]] = [newList[index], newList[index - 1]];
      return newList;
    });
  };

  // Move dialogue down in the list
  const handleMoveDialogueDown = (index: number) => {
    setEditableDialogues(prev => {
      if (index >= prev.length - 1) return prev;
      const newList = [...prev];
      [newList[index], newList[index + 1]] = [newList[index + 1], newList[index]];
      return newList;
    });
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

    console.log('[SceneEditor] Drop position:', {
      clientX: e.clientX,
      clientY: e.clientY,
      rectLeft: rect.left,
      rectTop: rect.top,
      rectWidth: rect.width,
      rectHeight: rect.height,
      aspectRatio: (rect.height / rect.width).toFixed(2),
      calculatedX: x.toFixed(2),
      calculatedY: y.toFixed(2)
    });

    const newBubble: DialogueBubble = {
      id: `bubble-${Date.now()}`,
      text: draggedDialogue.text,
      characterName: draggedDialogue.characterName,
      x: Math.max(5, Math.min(95, x)),
      y: Math.max(5, Math.min(95, y)),
      width: 35,
      height: 12
    };

    console.log('[SceneEditor] Created bubble:', newBubble);

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

        {/* LEFT: Scene List - Compact */}
        <div className="w-32 bg-white border-r border-gray-200 flex flex-col shrink-0">
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
                  className={`w-full px-2 py-2 text-left border-b border-gray-100 transition-all ${
                    isSelected
                      ? 'bg-purple-50 border-l-4 border-l-purple-600'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className={`text-sm font-medium ${isSelected ? 'text-purple-700' : 'text-gray-700'}`}>
                      #{page.page_number}
                    </span>
                    {isPageGenerating ? (
                      <span className="w-3 h-3 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></span>
                    ) : hasImage ? (
                      <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    ) : (
                      <span className="w-2 h-2 bg-gray-300 rounded-full"></span>
                    )}
                  </div>
                  <div className="text-[10px] text-gray-400 truncate">
                    {page.panel_indices.length}p · {page.layout_type.replace('_', ' ')}
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
          <div className="flex-1 flex items-center justify-center p-2 overflow-hidden">
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
                  className="h-full w-full object-cover rounded-lg shadow-2xl"
                  draggable={false}
                />

                {/* Dialogue Bubbles Overlay - Webtoon Style */}
                {currentBubbles.map((bubble, idx) => {
                  // Calculate dynamic font size based on bubble dimensions
                  // Base size scales with the smaller dimension for readability
                  const baseFontSize = Math.min(bubble.width ?? 35, (bubble.height ?? 12) * 2);
                  const fontSize = Math.max(8, Math.min(24, baseFontSize * 0.4));

                  // Calculate dynamic width based on text length
                  // Short text (< 10 chars) = compact bubble
                  // Medium text (10-30 chars) = medium bubble  
                  // Long text (> 30 chars) = use stored width or max
                  const textLength = bubble.text.length;
                  let dynamicWidth: string;
                  
                  if (textLength <= 5) {
                    dynamicWidth = 'auto'; // Very short: fit to content
                  } else if (textLength <= 15) {
                    dynamicWidth = `${Math.min(bubble.width ?? 25, 25)}%`; // Short: max 25%
                  } else if (textLength <= 30) {
                    dynamicWidth = `${Math.min(bubble.width ?? 35, 35)}%`; // Medium: max 35%
                  } else {
                    dynamicWidth = `${bubble.width ?? 50}%`; // Long: use stored or 50%
                  }

                  return (
                    <div
                      key={`bubble-overlay-${bubble.id || idx}`}
                      className="absolute group"
                      style={{
                        left: `${bubble.x}%`,
                        top: `${bubble.y}%`,
                        width: dynamicWidth,
                        maxWidth: '60%', // Never exceed 60% of image width
                        minWidth: textLength <= 5 ? 'fit-content' : undefined,
                        transform: 'translate(-50%, -50%)',
                      }}
                    >
                      {/* Webtoon-style rounded bubble - no character name, no tail */}
                      <div
                        className="bg-white border-[2.5px] border-black rounded-[20px] shadow-[3px_3px_0px_0px_rgba(0,0,0,0.15)] cursor-move flex items-center justify-center text-center"
                        style={{
                          padding: `${Math.max(8, fontSize * 0.6)}px ${Math.max(16, fontSize * 1.2)}px`,
                          minHeight: '100%',
                          whiteSpace: textLength <= 15 ? 'nowrap' : 'normal',
                        }}
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
                        <span
                          className="text-black font-medium leading-snug"
                          style={{
                            fontSize: `${fontSize}px`,
                            fontFamily: "'Comic Neue', 'Noto Sans KR', sans-serif",
                            letterSpacing: '-0.02em',
                          }}
                        >
                          {bubble.text}
                        </span>
                      </div>

                      {/* Resize Handle */}
                      <div
                        className="absolute bottom-0 right-0 w-5 h-5 bg-purple-500 rounded-tl-lg cursor-se-resize opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
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
                      >
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M22 22H20V20H22V22ZM22 18H20V16H22V18ZM18 22H16V20H18V22ZM22 14H20V12H22V14ZM18 18H16V16H18V18ZM14 22H12V20H14V22Z"/>
                        </svg>
                      </div>

                      {/* Delete Button */}
                      <button
                        className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600 shadow-md"
                        onClick={() => handleDeleteBubble(bubble.id)}
                      >
                        ×
                      </button>
                    </div>
                  );
                })}

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
        <div className="w-72 bg-white border-l border-gray-200 flex flex-col shrink-0">
          <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-700 text-sm">Dialogue</h3>
              <p className="text-xs text-gray-500 mt-0.5">Drag to place on image</p>
            </div>
            <button
              onClick={() => setShowAddDialogue(!showAddDialogue)}
              className="px-2 py-1 bg-purple-600 text-white text-xs font-medium rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-1"
            >
              <span className="text-lg leading-none">+</span>
              <span>Add</span>
            </button>
          </div>

          {/* Add Custom Dialogue Form */}
          {showAddDialogue && (
            <div className="p-3 bg-purple-50 border-b border-purple-100">
              <div className="space-y-2">
                <input
                  type="text"
                  placeholder="Character name (optional)"
                  value={newDialogueCharacter}
                  onChange={(e) => setNewDialogueCharacter(e.target.value)}
                  className="w-full text-sm px-3 py-2 border border-purple-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 bg-white text-gray-900 placeholder:text-gray-400"
                />
                <textarea
                  placeholder='Enter dialogue text (e.g., "...", "!", "What?!")'
                  value={newDialogueText}
                  onChange={(e) => setNewDialogueText(e.target.value)}
                  className="w-full text-sm px-3 py-2 border border-purple-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 resize-none bg-white text-gray-900 placeholder:text-gray-400"
                  rows={2}
                />
                <div className="flex gap-2">
                  <button
                    onClick={handleAddCustomDialogue}
                    disabled={!newDialogueText.trim()}
                    className="flex-1 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                  >
                    Add Dialogue
                  </button>
                  <button
                    onClick={() => {
                      setShowAddDialogue(false);
                      setNewDialogueText('');
                      setNewDialogueCharacter('');
                    }}
                    className="px-4 py-2 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {editableDialogues.length > 0 ? (
              editableDialogues.map((dialogue, index) => {
                // Check if this dialogue is already placed as a bubble
                const isPlaced = currentBubbles.some(
                  b => b.text === dialogue.text && b.characterName === dialogue.characterName
                );
                const isCustom = dialogue.panelIndex === -1;

                // Generate a consistent color for each character
                const charColors = [
                  { bg: 'bg-purple-100', text: 'text-purple-700', border: 'border-purple-200' },
                  { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200' },
                  { bg: 'bg-pink-100', text: 'text-pink-700', border: 'border-pink-200' },
                  { bg: 'bg-amber-100', text: 'text-amber-700', border: 'border-amber-200' },
                  { bg: 'bg-teal-100', text: 'text-teal-700', border: 'border-teal-200' },
                ];
                const colorIndex = dialogue.characterName.charCodeAt(0) % charColors.length;
                const charColor = charColors[colorIndex];

                return (
                  <div
                    key={dialogue.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, dialogue)}
                    className={`p-3 rounded-xl border-2 transition-all cursor-grab active:cursor-grabbing relative ${
                      isPlaced
                        ? 'bg-green-50 border-green-300 opacity-60'
                        : 'bg-white border-gray-200 hover:border-purple-400 hover:shadow-lg'
                    }`}
                  >
                    {/* Character Badge + Order Controls */}
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${charColor.bg} ${charColor.text}`}>
                        {dialogue.characterName}
                      </span>
                      <span className="text-xs text-gray-400">#{index + 1}</span>

                      {/* Order controls */}
                      <div className="flex items-center gap-0.5 ml-auto">
                        <button
                          onClick={(e) => { e.stopPropagation(); handleMoveDialogueUp(index); }}
                          disabled={index === 0}
                          className="w-5 h-5 flex items-center justify-center text-gray-400 hover:text-gray-700 hover:bg-gray-200 rounded disabled:opacity-30 disabled:cursor-not-allowed"
                          title="Move up"
                        >
                          ▲
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); handleMoveDialogueDown(index); }}
                          disabled={index === editableDialogues.length - 1}
                          className="w-5 h-5 flex items-center justify-center text-gray-400 hover:text-gray-700 hover:bg-gray-200 rounded disabled:opacity-30 disabled:cursor-not-allowed"
                          title="Move down"
                        >
                          ▼
                        </button>
                      </div>

                      {isPlaced && (
                        <span className="text-xs bg-green-500 text-white px-2 py-0.5 rounded-full">✓</span>
                      )}
                      {isCustom && !isPlaced && (
                        <span className="text-xs bg-purple-500 text-white px-2 py-0.5 rounded-full">+</span>
                      )}
                    </div>

                    {/* Editable Text */}
                    <textarea
                      value={dialogue.text}
                      onChange={(e) => handleDialogueTextChange(dialogue.id, e.target.value)}
                      className="w-full text-sm text-gray-800 bg-gray-50 border border-gray-200 rounded-lg p-2 resize-none focus:outline-none focus:ring-2 focus:ring-purple-300 focus:border-transparent"
                      rows={2}
                    />

                    {/* Footer */}
                    <div className="mt-2 flex items-center justify-between">
                      <span className="text-[10px] text-gray-400 uppercase tracking-wide">
                        {isCustom ? 'Custom' : `Panel ${dialogue.panelIndex + 1}`}
                      </span>
                      {isCustom && (
                        <button
                          onClick={() => handleDeleteDialogue(dialogue.id)}
                          className="text-xs text-red-500 hover:text-red-700 font-medium"
                        >
                          Delete
                        </button>
                      )}
                    </div>

                    {/* Drag Handle Indicator */}
                    <div className="absolute top-3 right-3 opacity-30 group-hover:opacity-60">
                      <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0ZM8 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0ZM8 18a2 2 0 1 1-4 0 2 2 0 0 1 4 0ZM14 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0ZM14 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0ZM14 18a2 2 0 1 1-4 0 2 2 0 0 1 4 0Z"/>
                      </svg>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center text-gray-400 py-8">
                <p className="text-sm mb-2">No dialogue for this scene</p>
                <button
                  onClick={() => setShowAddDialogue(true)}
                  className="text-purple-600 text-sm font-medium hover:underline"
                >
                  + Add custom dialogue
                </button>
              </div>
            )}
          </div>

          {/* SFX Effects Display */}
          {currentScene && (() => {
            // Collect SFX from all panels in this scene
            const sceneSfx: { type: string; description: string; intensity: string; position: string }[] = [];
            currentScene.panel_indices.forEach((panelIdx: number) => {
              const panel = webtoonScript.panels[panelIdx];
              if (panel?.sfx_effects && Array.isArray(panel.sfx_effects)) {
                panel.sfx_effects.forEach((sfx: any) => {
                  sceneSfx.push({
                    type: sfx.type || 'effect',
                    description: sfx.description || '',
                    intensity: sfx.intensity || 'medium',
                    position: sfx.position || 'screen'
                  });
                });
              }
            });

            if (sceneSfx.length === 0) return null;

            const getSfxIcon = (type: string) => {
              switch (type) {
                case 'screen_effect': return '📺';
                case 'emotional_effect': return '💧';
                case 'wind_lines': return '💨';
                case 'impact_text': return '💥';
                case 'motion_blur': return '🌀';
                case 'speed_lines': return '⚡';
                default: return '✨';
              }
            };

            const getIntensityColor = (intensity: string) => {
              switch (intensity) {
                case 'high': return 'bg-red-100 text-red-700 border-red-200';
                case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
                case 'low': return 'bg-green-100 text-green-700 border-green-200';
                default: return 'bg-gray-100 text-gray-700 border-gray-200';
              }
            };

            return (
              <div className="border-t border-gray-200 p-3 bg-gradient-to-b from-purple-50 to-white">
                <h4 className="font-semibold text-gray-700 text-xs mb-2 flex items-center gap-2">
                  <span>✨</span>
                  SFX Effects ({sceneSfx.length})
                </h4>
                <div className="space-y-1.5 max-h-32 overflow-y-auto">
                  {sceneSfx.map((sfx, idx) => (
                    <div
                      key={idx}
                      className={`flex items-center gap-2 text-xs p-2 rounded-lg border ${getIntensityColor(sfx.intensity)}`}
                    >
                      <span className="text-base">{getSfxIcon(sfx.type)}</span>
                      <div className="flex-1 min-w-0">
                        <span className="font-medium capitalize">{sfx.type.replace('_', ' ')}</span>
                        <span className="text-gray-500 ml-1 truncate">- {sfx.description}</span>
                      </div>
                      <span className="text-[10px] uppercase font-bold opacity-70">{sfx.intensity}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })()}

          {/* Placed Bubbles Summary */}
          {currentBubbles.length > 0 && (
            <div className="border-t border-gray-200 p-3 bg-gray-50">
              <h4 className="font-medium text-gray-700 text-xs mb-2 flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                Placed on Image ({currentBubbles.length})
              </h4>
              <div className="space-y-1.5 max-h-28 overflow-y-auto">
                {currentBubbles.map((bubble, idx) => {
                  // Same color logic as dialogue list
                  const charColors = [
                    { bg: 'bg-purple-100', text: 'text-purple-700' },
                    { bg: 'bg-blue-100', text: 'text-blue-700' },
                    { bg: 'bg-pink-100', text: 'text-pink-700' },
                    { bg: 'bg-amber-100', text: 'text-amber-700' },
                    { bg: 'bg-teal-100', text: 'text-teal-700' },
                  ];
                  const colorIndex = bubble.characterName.charCodeAt(0) % charColors.length;
                  const charColor = charColors[colorIndex];

                  return (
                    <div key={`${bubble.id || 'bubble'}-${idx}`} className="flex items-center gap-2 text-xs bg-white p-2 rounded-lg border border-gray-200">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${charColor.bg} ${charColor.text} shrink-0`}>
                        {bubble.characterName.substring(0, 8)}
                      </span>
                      <span className="truncate flex-1 text-gray-600">
                        "{bubble.text.substring(0, 25)}{bubble.text.length > 25 ? '...' : ''}"
                      </span>
                      <button
                        onClick={() => handleDeleteBubble(bubble.id)}
                        className="text-red-400 hover:text-red-600 shrink-0"
                      >
                        ×
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
