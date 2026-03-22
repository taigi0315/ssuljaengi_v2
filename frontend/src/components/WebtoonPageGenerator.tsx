'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { WebtoonScript, ImageStyle, PageImage, DialogueBubble, DialogueLine } from '@/types';
import { formatGenreName } from '@/utils/formatters';
import { getScriptLayout, generatePageImage, selectPageImage } from '@/lib/apiClient';

interface WebtoonPageGeneratorProps {
  webtoonScript: WebtoonScript;
  imageStyle: ImageStyle;
  onUpdateScript?: (script: WebtoonScript) => void;
}

interface PageLayout {
  page_number: number;
  panel_indices: number[];
  layout_type: string;
  is_single_panel: boolean;
  reasoning?: string;
}

export default function WebtoonPageGenerator({
  webtoonScript,
  imageStyle,
  onUpdateScript
}: WebtoonPageGeneratorProps) {
  const [layout, setLayout] = useState<PageLayout[]>([]);
  // Store array of images per page
  const [generatedPages, setGeneratedPages] = useState<Record<number, PageImage[]>>({});
  const [currentImageIndices, setCurrentImageIndices] = useState<Record<number, number>>({});
  
  // Track bubbles per pageId
  const [pageBubbles, setPageBubbles] = useState<Record<number, DialogueBubble[]>>({});

  const [isGenerating, setIsGenerating] = useState<Record<number, boolean>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Drag state
  const [draggedDialogue, setDraggedDialogue] = useState<{ text: string; characterName: string } | null>(null);
  const [draggingBubble, setDraggingBubble] = useState<{ id: string; startX: number; startY: number; startBubbleX: number; startBubbleY: number; pageNum: number } | null>(null);
  const [resizingBubble, setResizingBubble] = useState<{ id: string; startX: number; startY: number; startWidth: number; startHeight: number; pageNum: number } | null>(null);

  const canvasRefs = useRef<Record<number, HTMLDivElement | null>>({});

  // Initialize data
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

  // Load existing images and bubbbles
  useEffect(() => {
    if (webtoonScript.page_images) {
      setGeneratedPages(webtoonScript.page_images);
      
      // Initialize indices to selected image or last image
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

  const updateScriptBubbles = useCallback((pageNum: number, bubbles: DialogueBubble[]) => {
      if (onUpdateScript) {
          const updatedBubbles = { ...(webtoonScript.page_dialogue_bubbles || {}), [pageNum]: bubbles };
          onUpdateScript({
              ...webtoonScript,
              page_dialogue_bubbles: updatedBubbles
          });
      }
  }, [onUpdateScript, webtoonScript]);

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
      
      // Auto-select the new image index
      setCurrentImageIndices(prev => ({
          ...prev,
          [page.page_number]: (generatedPages[page.page_number]?.length || 0) // Index is current length (before update was effectively length)
      }));

    } catch (err) {
      console.error(`Failed to generate page ${page.page_number}:`, err);
    } finally {
      setIsGenerating(prev => ({ ...prev, [page.page_number]: false }));
    }
  };

  const handleSelectImage = async (pageNumber: number, imageId: string) => {
      try {
          await selectPageImage(webtoonScript.script_id, imageId);
          
          // Update local state to reflect selection
           setGeneratedPages(prev => {
              const images = prev[pageNumber] || [];
              const updatedImages = images.map(img => ({
                    ...img,
                    is_selected: img.id === imageId
              }));
              
              // Also update script if prop function provided
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

  // --- Dialogue Drag & Drop Logic ---

  const handleDragStart = (e: React.DragEvent, dialogue: { characterName: string; text: string }) => {
     setDraggedDialogue(dialogue);
  };

  const handleDrop = (e: React.DragEvent, pageNum: number) => {
      e.preventDefault();
      if (!draggedDialogue) return;
      
      const canvas = canvasRefs.current[pageNum];
      if (!canvas) return;
      
      const rect = canvas.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      
      const newBubble: DialogueBubble = {
          id: `bubble-${Date.now()}`,
          text: draggedDialogue.text,
          characterName: draggedDialogue.characterName,
          x: Math.max(5, Math.min(95, x)),
          y: Math.max(5, Math.min(95, y)),
          width: 40,
          height: 10
      };
      
      const newPageBubbles = [...(pageBubbles[pageNum] || []), newBubble];
      setPageBubbles(prev => ({
          ...prev,
          [pageNum]: newPageBubbles
      }));
      updateScriptBubbles(pageNum, newPageBubbles);
      
      setDraggedDialogue(null);
  };

  // --- Bubble Intearaction (Move/Resize) ---
  
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (draggingBubble) {
        const canvas = canvasRefs.current[draggingBubble.pageNum];
        if (!canvas) return;
        const rect = canvas.getBoundingClientRect();
        const deltaX = ((e.clientX - draggingBubble.startX) / rect.width) * 100;
        const deltaY = ((e.clientY - draggingBubble.startY) / rect.height) * 100;

        setPageBubbles(prev => {
          const list = prev[draggingBubble.pageNum] || [];
          return {
            ...prev,
            [draggingBubble.pageNum]: list.map(b => 
              b.id === draggingBubble.id 
                ? { ...b, x: draggingBubble.startBubbleX + deltaX, y: draggingBubble.startBubbleY + deltaY } 
                : b
            )
          };
        });
      }
      
      if (resizingBubble) {
          const canvas = canvasRefs.current[resizingBubble.pageNum];
          if (!canvas) return;
          const rect = canvas.getBoundingClientRect();
          const deltaX = ((e.clientX - resizingBubble.startX) / rect.width) * 100;
          const deltaY = ((e.clientY - resizingBubble.startY) / rect.height) * 100;
          
          setPageBubbles(prev => {
            const list = prev[resizingBubble.pageNum] || [];
            return {
              ...prev,
              [resizingBubble.pageNum]: list.map(b => 
                b.id === resizingBubble.id 
                  ? { ...b, width: Math.max(10, resizingBubble.startWidth + deltaX), height: Math.max(5, resizingBubble.startHeight + deltaY) } 
                  : b
              )
            };
          });
      }
    };

    const handleMouseUp = () => {
      if (draggingBubble) {
          // Update script on mouse up
          updateScriptBubbles(draggingBubble.pageNum, pageBubbles[draggingBubble.pageNum] || []);
          setDraggingBubble(null);
      }
      if (resizingBubble) {
          // Update script on mouse up
          updateScriptBubbles(resizingBubble.pageNum, pageBubbles[resizingBubble.pageNum] || []);
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
  }, [draggingBubble, pageBubbles, resizingBubble, updateScriptBubbles]);


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
    <div className="space-y-8 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Webtoon Page Layout</h2>
          <p className="text-gray-600">
            {layout.length} pages structured from {webtoonScript.panels.length} panels
          </p>
        </div>
        <div className="px-4 py-2 bg-purple-50 text-purple-700 rounded-full text-sm font-bold border border-purple-100">
          Style: {formatGenreName(imageStyle)}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {layout.map((page) => {
            const images = generatedPages[page.page_number] || [];
            const currentIndex = currentImageIndices[page.page_number] || (images.length > 0 ? images.length - 1 : 0);
            const currentImage = images[currentIndex];
            const bubbles = pageBubbles[page.page_number] || [];
            
            // Collect dialogues for this page
            const pageDialogues = page.panel_indices.flatMap(pidx => {
                const panel = webtoonScript.panels[pidx];
                if (!panel || !panel.dialogue) return [];
                 // Parse dialogue logic (from previous component)
                 // Assuming dialogue is object or parsed properly in backend
                 // For now, assume consistent backend format List[dict]
                 if (Array.isArray(panel.dialogue)) {
                     return panel.dialogue.map((d: DialogueLine) => ({ characterName: d.character || 'Unknown', text: d.text || '' }));
                 }
                 return [];
            });

            return (
              <div 
                key={page.page_number}
                className="flex flex-col bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden h-[800px]"
              >
                {/* Header */}
                <div className="bg-gray-50 px-4 py-3 border-b border-gray-100 flex justify-between items-center shrink-0">
                  <span className="font-bold text-gray-700">Page {page.page_number}</span>
                  <div className="flex items-center gap-2">
                     {images.length > 0 && (
                         <span className="text-xs text-gray-500">v{currentIndex + 1}/{images.length}</span>
                     )}
                     <span className={`text-xs px-2 py-1 rounded-full ${page.is_single_panel ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'}`}>
                        {page.layout_type.replace('_', ' ').toUpperCase()}
                     </span>
                  </div>
                </div>

                {/* Content Area - Split into Image and Dialogue/Controls */}
                <div className="flex-1 flex overflow-hidden">
                    {/* Image Area */}
                    <div className="flex-1 bg-gray-100 relative group overflow-hidden flex items-center justify-center">
                      {currentImage ? (
                        <div 
                           ref={(el) => { canvasRefs.current[page.page_number] = el; }}
                           className="relative h-full w-full flex items-center justify-center"
                           onDragOver={(e) => e.preventDefault()}
                           onDrop={(e) => handleDrop(e, page.page_number)}
                        >
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img 
                            src={currentImage.image_url} 
                            alt={`Page ${page.page_number}`}
                            className="max-h-full max-w-full object-contain"
                          />
                          
                          {/* Bubbles Overlay */}
                          {bubbles.map(bubble => (
                             <div
                                key={bubble.id}
                                style={{
                                    left: `${bubble.x}%`,
                                    top: `${bubble.y}%`,
                                    width: `${bubble.width}%`,
                                    height: `${bubble.height}%`,
                                    transform: 'translate(-50%, -50%)',
                                    position: 'absolute',
                                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                                    border: '2px solid #000',
                                    borderRadius: '12px',
                                    padding: '8px',
                                    cursor: 'move',
                                    fontSize: '10px'
                                }}
                                onMouseDown={(e) => {
                                    e.stopPropagation();
                                    setDraggingBubble({
                                        id: bubble.id,
                                        startX: e.clientX,
                                        startY: e.clientY,
                                        startBubbleX: bubble.x,
                                        startBubbleY: bubble.y,
                                        pageNum: page.page_number
                                    });
                                }}
                             >
                                <div className="w-full h-full flex flex-col overflow-hidden text-center leading-tight">
                                     <span className="font-bold text-purple-700 mr-1 text-[9px]">{bubble.characterName}</span>
                                     <span>{bubble.text}</span>
                                </div>
                                <div
                                   className="absolute bottom-0 right-0 w-4 h-4 cursor-se-resize bg-purple-200 opacity-50 hover:opacity-100 rounded-tl"
                                   onMouseDown={(e) => {
                                       e.stopPropagation();
                                       setResizingBubble({
                                           id: bubble.id,
                                           startX: e.clientX,
                                           startY: e.clientY,
                                           startWidth: bubble.width || 40,
                                           startHeight: bubble.height || 10,
                                           pageNum: page.page_number
                                       });
                                   }}
                                />
                                <button 
                                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-4 h-4 flex items-center justify-center text-[10px] opacity-0 group-hover:opacity-100"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setPageBubbles(prev => ({
                                            ...prev,
                                            [page.page_number]: prev[page.page_number].filter(b => b.id !== bubble.id)
                                        }));
                                    }}
                                >×</button>
                             </div>
                          ))}
                        </div>
                      ) : (
                        <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center z-10">
                           <div className="mb-4 space-y-2 w-32">
                             {/* Mini mockup */}
                             {page.panel_indices.map((idx) => (
                               <div key={idx} className="h-8 w-full bg-white border border-gray-300 rounded flex items-center justify-center text-[10px] text-gray-400">P{idx + 1}</div>
                             ))}
                           </div>
                           <button
                            onClick={() => handleGeneratePage(page)}
                            disabled={isGenerating[page.page_number]}
                            className={`
                              px-4 py-2 rounded-full font-bold text-white text-sm shadow-md transition-all
                              ${isGenerating[page.page_number] ? 'bg-gray-400' : 'bg-gradient-to-r from-purple-600 to-blue-500 hover:scale-105'}
                            `}
                          >
                             {isGenerating[page.page_number] ? 'Generating...' : 'Generate Page'}
                          </button>
                        </div>
                      )}
                    </div>
                </div>

                {/* Footer Controls */}
                <div className="bg-white p-3 border-t border-gray-100 shrink-0">
                    {/* Controls Row */}
                    <div className="flex items-center justify-between mb-3">
                         <div className="flex gap-1">
                             <button
                               disabled={!currentImage || currentIndex <= 0}
                               onClick={() => setCurrentImageIndices(p => ({ ...p, [page.page_number]: currentIndex - 1 }))}
                               className="p-1 hover:bg-gray-100 rounded disabled:opacity-30"
                             >⬅️</button>
                             <button
                               disabled={!currentImage || currentIndex >= images.length - 1}
                               onClick={() => setCurrentImageIndices(p => ({ ...p, [page.page_number]: currentIndex + 1 }))}
                               className="p-1 hover:bg-gray-100 rounded disabled:opacity-30"
                             >➡️</button>
                         </div>
                         <div className="flex gap-2">
                             <button
                               onClick={() => currentImage && handleSelectImage(page.page_number, currentImage.id)}
                               disabled={!currentImage}
                               className={`px-3 py-1 rounded-full text-xs font-bold ${
                                   currentImage?.is_selected 
                                   ? 'bg-green-100 text-green-700' 
                                   : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                               }`}
                             >
                                 {currentImage?.is_selected ? '✓ Selected' : 'Select'}
                             </button>
                             <button
                               onClick={() => handleGeneratePage(page)}
                               disabled={isGenerating[page.page_number]}
                               className="px-3 py-1 rounded-full text-xs font-bold bg-purple-50 text-purple-700 hover:bg-purple-100"
                             >
                                 ↻ New
                             </button>
                         </div>
                    </div>
                    
                    {/* Dialogue List for Dragging */}
                    <div className="border-t pt-2 max-h-32 overflow-y-auto">
                        <p className="text-[10px] text-gray-400 uppercase font-bold mb-2">Drag Dialogues to Image</p>
                        <div className="space-y-1">
                            {pageDialogues.length > 0 ? (
                                pageDialogues.map((d, i) => (
                                    <div
                                       key={i}
                                       draggable
                                       onDragStart={(e) => handleDragStart(e, d)}
                                       className="text-xs p-2 bg-gray-50 border border-gray-200 rounded cursor-grab hover:bg-purple-50 hover:border-purple-200 transition-colors"
                                    >
                                        <strong className="text-purple-700 mr-1">{d.characterName}:</strong>
                                        <span className="text-gray-700">{d.text.substring(0, 50)}{d.text.length > 50 ? '...' : ''}</span>
                                    </div>
                                ))
                            ) : (
                                <p className="text-xs text-center text-gray-400 py-2">No dialogue</p>
                            )}
                        </div>
                    </div>
                </div>
              </div>
            );
        })}
      </div>
    </div>
  );
}
