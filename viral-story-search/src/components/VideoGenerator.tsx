'use client';

import { useState, useRef, useEffect } from 'react';
import { WebtoonScript, StoryGenre } from '@/types';

interface VideoGeneratorProps {
  webtoonScript: WebtoonScript;
  genre: StoryGenre;
}

// ============================================
// VIDEO GENERATION CONFIG - ADJUST HERE
// ============================================
const VIDEO_CONFIG = {
  // Canvas/Video dimensions (9:16 for TikTok/Shorts/Reels)
  CANVAS_WIDTH: 1080,
  CANVAS_HEIGHT: 1920,

  // Timing (in milliseconds)
  // Timing (in milliseconds)
  BASE_IMAGE_DURATION_MS: 350,     // How long to show image before first bubble
  // Dynamic Dialogue Duration Config
  MIN_BUBBLE_DURATION_MS: 1000,    // Minimum duration for any bubble
  PER_CHAR_DURATION_MS: 50,        // Additional duration per character
  // DIALOGUE_DURATION_MS: 2000,   // REMOVED: Static duration replaced by dynamic logic
  FINAL_PAUSE_MS: 450,             // Pause after last bubble before next panel
  TRANSITION_DURATION_MS: 400,    // Duration of scroll transition between panels

  // Bubble styling - WEBTOON STYLE (matching frontend EXACTLY)
  BUBBLE_FONT_SIZE: 45,            // Font size for dialogue text
  BUBBLE_PADDING: 12,              // Reduced padding for tighter bubbles
  BUBBLE_BORDER_RADIUS: 20,        // Matches frontend rounded-[20px]
  BUBBLE_BORDER_WIDTH: 2.5,        // Matches frontend border-[2.5px]
  BUBBLE_BG_COLOR: '#FFFFFF',      // Pure white background
  BUBBLE_BG_OPACITY: 1.0,          // Solid white (not transparent)
  BUBBLE_BORDER_COLOR: '#000000',  // Black border (webtoon style)
  BUBBLE_TEXT_COLOR: '#000000',    // Black text
  BUBBLE_SHADOW_OFFSET: 3,         // Matches frontend shadow-[3px_3px...]
  BUBBLE_SHADOW_COLOR: 'rgba(0,0,0,0.15)', // Matches frontend

  // Video quality - MAXIMUM QUALITY SETTINGS
  VIDEO_BITRATE: 16000000,         // 16 Mbps for maximum quality
  FPS: 30,
};

export default function VideoGenerator({ webtoonScript, genre }: VideoGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0); // 0 to 100
  const [statusText, setStatusText] = useState('');
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Helper to load image
  const loadImage = (url: string): Promise<HTMLImageElement> => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = url;
    });
  };

  const handleGenerateVideo = async () => {
    if (!canvasRef.current || isGenerating) return;
    
    setIsGenerating(true);
    setError(null);
    setVideoUrl(null);
    setProgress(0);
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      setError('Could not get canvas context');
      setIsGenerating(false);
      return;
    }

    // Canvas settings from config
    canvas.width = VIDEO_CONFIG.CANVAS_WIDTH;
    canvas.height = VIDEO_CONFIG.CANVAS_HEIGHT;
    
    // MediaRecorder setup with higher quality
    const stream = canvas.captureStream(VIDEO_CONFIG.FPS);
    const chunks: Blob[] = [];
    const mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'video/webm;codecs=vp9',
      videoBitsPerSecond: VIDEO_CONFIG.VIDEO_BITRATE
    });
    
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };
    
    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'video/webm' });
      const url = URL.createObjectURL(blob);
      setVideoUrl(url);
      setIsGenerating(false);
      setStatusText('Video generated successfully!');
    };
    
    mediaRecorder.start();
    
    // Give the recorder a moment to initialize
    await new Promise(r => setTimeout(r, 300));

    console.log('Starting video generation for script:', webtoonScript.script_id);
    console.log('Total panels:', webtoonScript.panels.length);

    // Track the image area for bubble positioning
    let imageRect = { x: 0, y: 0, width: canvas.width, height: canvas.height };

    // Helper to draw image in COVER mode (zoom to fill, crop sides)
    const drawImageCover = async (imageUrl: string) => {
      try {
        const img = await loadImage(imageUrl);
        
        // Cover logic: Scale to fit the LARGER dimension (Height in this case for 9:16 target vs 1:1 source)
        // Since we want to display the center vertical strip of a square image
        const scale = Math.max(canvas.width / img.width, canvas.height / img.height);
        
        const width = img.width * scale;
        const height = img.height * scale;
        
        const x = (canvas.width - width) / 2;
        const y = (canvas.height - height) / 2;
        
        // Store image rectangle for bubble positioning (will be larger than canvas)
        imageRect = { x, y, width, height };
        
        // Draw image (centered, cropping sides)
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, x, y, width, height);
        return true;
      } catch (e) {
        console.error('Failed to load image', e);
        ctx.fillStyle = '#333';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        return false;
      }
    };

    // Helper to draw bubble with auto-sizing based on text
    // xPercent and yPercent are relative to the IMAGE area
    // Helper to wrap text for canvas
    const wrapText = (ctx: CanvasRenderingContext2D, text: string, maxWidth: number) => {
        const words = text.split(' ');
        const lines = [];
        let currentLine = words[0];

        for (let i = 1; i < words.length; i++) {
            const word = words[i];
            const width = ctx.measureText(currentLine + " " + word).width;
            if (width < maxWidth) {
                currentLine += " " + word;
            } else {
                lines.push(currentLine);
                currentLine = word;
            }
        }
        lines.push(currentLine);
        return lines;
    };

    // Helper to draw bubble with auto-sizing based on text
    // xPercent and yPercent are relative to the IMAGE area
    // WEBTOON STYLE: No character name, rounded bubble with shadow
    const drawBubble = (
      text: string, 
      xPercent: number, 
      yPercent: number, 
      wPercent?: number, 
      hPercent?: number,
      characterName?: string // Keep for narrator detection only
    ) => {
      const { 
        BUBBLE_PADDING, BUBBLE_BORDER_RADIUS, 
        BUBBLE_BORDER_WIDTH, BUBBLE_BG_OPACITY, BUBBLE_BORDER_COLOR, BUBBLE_TEXT_COLOR,
        BUBBLE_SHADOW_OFFSET, BUBBLE_SHADOW_COLOR
      } = VIDEO_CONFIG;
      
      // 1. Calculate base scaling for resolution independence
      const editorWidth = 400; 
      const scaleRef = canvas.width / editorWidth;
      
      // 2. Calculate dynamic font size matching editor logic
      const calcBaseFontSize = Math.min(wPercent || 35, (hPercent || 12) * 2);
      const calcEditorFontSize = Math.max(8, Math.min(24, calcBaseFontSize * 0.4));
      const finalFontSize = Math.floor(calcEditorFontSize * scaleRef);
      
      // Use Comic-style font like frontend
      ctx.font = `600 ${finalFontSize}px Arial, sans-serif`;
      
      // 3. Dimensions - width from percent, but height auto-fits text
      const bw = (wPercent || 35) / 100 * canvas.width;
      // Use tighter padding like frontend: vertical = fontSize * 0.5, horizontal = fontSize * 0.8
      const paddingV = Math.max(6 * scaleRef, finalFontSize * 0.5);
      const paddingH = Math.max(10 * scaleRef, finalFontSize * 0.8);
      
      // 4. Wrap text and height - AUTO-FIT to text content
      const wrappedLines = wrapText(ctx, text, bw - (paddingH * 2));
      const textHeight = wrappedLines.length * finalFontSize * 1.2;

      // Height based on text only (no minimum from hPercent) for tight fit
      const bh = textHeight + (paddingV * 2);
      
      // 5. Centered Position
      const absoluteX = (xPercent / 100) * canvas.width;
      const absoluteY = (yPercent / 100) * canvas.height;
      let bx = absoluteX - bw / 2;
      let by = absoluteY - bh / 2;
      
      // Clamp to CANVAS bounds (visible area), not image bounds
      // keeping 20px padding from edges to match backend
      bx = Math.max(20, Math.min(canvas.width - bw - 20, bx));
      by = Math.max(20, Math.min(canvas.height - bh - 20, by));
      
      const isNarrator = characterName?.toLowerCase() === 'narrator';
      const scaledBorderRadius = BUBBLE_BORDER_RADIUS * (scaleRef * 0.5);
      const scaledShadowOffset = BUBBLE_SHADOW_OFFSET * scaleRef;

      // Draw Bubble Background (Skip for Narrator)
      if (!isNarrator) {
        // Draw shadow first (offset to bottom-right)
        ctx.fillStyle = BUBBLE_SHADOW_COLOR;
        ctx.beginPath();
        ctx.moveTo(bx + scaledShadowOffset + scaledBorderRadius, by + scaledShadowOffset);
        ctx.lineTo(bx + scaledShadowOffset + bw - scaledBorderRadius, by + scaledShadowOffset);
        ctx.quadraticCurveTo(bx + scaledShadowOffset + bw, by + scaledShadowOffset, bx + scaledShadowOffset + bw, by + scaledShadowOffset + scaledBorderRadius);
        ctx.lineTo(bx + scaledShadowOffset + bw, by + scaledShadowOffset + bh - scaledBorderRadius);
        ctx.quadraticCurveTo(bx + scaledShadowOffset + bw, by + scaledShadowOffset + bh, bx + scaledShadowOffset + bw - scaledBorderRadius, by + scaledShadowOffset + bh);
        ctx.lineTo(bx + scaledShadowOffset + scaledBorderRadius, by + scaledShadowOffset + bh);
        ctx.quadraticCurveTo(bx + scaledShadowOffset, by + scaledShadowOffset + bh, bx + scaledShadowOffset, by + scaledShadowOffset + bh - scaledBorderRadius);
        ctx.lineTo(bx + scaledShadowOffset, by + scaledShadowOffset + scaledBorderRadius);
        ctx.quadraticCurveTo(bx + scaledShadowOffset, by + scaledShadowOffset, bx + scaledShadowOffset + scaledBorderRadius, by + scaledShadowOffset);
        ctx.closePath();
        ctx.fill();

        // Draw main bubble (white background with black border)
        ctx.fillStyle = `rgba(255, 255, 255, ${BUBBLE_BG_OPACITY})`; 
        ctx.strokeStyle = BUBBLE_BORDER_COLOR;
        ctx.lineWidth = BUBBLE_BORDER_WIDTH * scaleRef;
        
        // Rounded rect - webtoon style
        ctx.beginPath();
        ctx.moveTo(bx + scaledBorderRadius, by);
        ctx.lineTo(bx + bw - scaledBorderRadius, by);
        ctx.quadraticCurveTo(bx + bw, by, bx + bw, by + scaledBorderRadius);
        ctx.lineTo(bx + bw, by + bh - scaledBorderRadius);
        ctx.quadraticCurveTo(bx + bw, by + bh, bx + bw - scaledBorderRadius, by + bh);
        ctx.lineTo(bx + scaledBorderRadius, by + bh);
        ctx.quadraticCurveTo(bx, by + bh, bx, by + bh - scaledBorderRadius);
        ctx.lineTo(bx, by + scaledBorderRadius);
        ctx.quadraticCurveTo(bx, by, bx + scaledBorderRadius, by);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      }
      
      // Draw Text - CENTERED, NO CHARACTER NAME (webtoon style)
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      // Configure Text Colors
      if (isNarrator) {
        // Narrator: White text with heavy black stroke
        ctx.fillStyle = '#FFFFFF';
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 3 * scaleRef;
      } else {
        // Webtoon style: Black text, no stroke
        ctx.fillStyle = BUBBLE_TEXT_COLOR;
        ctx.strokeStyle = 'transparent';
        ctx.lineWidth = 0;
      }
      
      const centerX = bx + bw / 2;
      // Vertically center the text block
      const totalTextHeight = wrappedLines.length * finalFontSize * 1.2;
      let currentY = by + (bh - totalTextHeight) / 2 + (finalFontSize * 0.6);
      
      // Draw Message Lines (NO character name for webtoon style)
      ctx.font = `600 ${finalFontSize}px Arial, sans-serif`; 
      
      wrappedLines.forEach((line) => {
          if (isNarrator) {
              ctx.strokeText(line, centerX, currentY);
          }
          ctx.fillText(line, centerX, currentY);
          currentY += finalFontSize * 1.2;
      });
    };

    try {
      // Iterate scenes - GROUP BY PAGES to avoid repeating same image
      const panels = webtoonScript.panels;
      const totalPanels = panels.length;
      const processedPages = new Set<string>(); // Track processed page keys

      console.log(`Starting loop for ${totalPanels} panels`);

      // Count unique pages for accurate progress
      const uniquePageKeys = new Set<string>();
      panels.forEach(panel => {
        if (webtoonScript.page_images) {
          for (const pageKey in webtoonScript.page_images) {
            const pageImgs = webtoonScript.page_images[pageKey];
            const pageImg = pageImgs[0];
            if (pageImg?.panel_indices?.includes(panel.panel_number - 1)) {
              uniquePageKeys.add(pageKey);
              break;
            }
          }
        }
      });
      const totalUniquePages = uniquePageKeys.size || totalPanels;
      let processedCount = 0;

      for (let i = 0; i < totalPanels; i++) {
        const panel = panels[i];

        // Find which page this panel belongs to
        let pageKey: string | null = null;
        if (webtoonScript.page_images) {
          for (const pKey in webtoonScript.page_images) {
            const pageImgs = webtoonScript.page_images[pKey];
            const pageImg = pageImgs[0];
            if (pageImg?.panel_indices?.includes(panel.panel_number - 1)) {
              pageKey = pKey;
              break;
            }
          }
        }

        // Skip if this page was already processed (multi-panel page)
        if (pageKey && processedPages.has(pageKey)) {
          console.log(`Skipping Panel ${panel.panel_number} - page ${pageKey} already processed`);
          continue;
        }
        if (pageKey) {
          processedPages.add(pageKey);
        }

        processedCount++;
        console.log(`--- Processing Panel ${panel.panel_number} (Page: ${pageKey || 'single'}) ---`);
        setStatusText(`Processing Page ${processedCount}/${totalUniquePages}...`);
        setProgress(((processedCount) / totalUniquePages) * 100);
        
        // Get Scene Image - Prioritize selected Page Image, then selected Scene Image, then fallback
        let selectedImage = null;
        
        // 1. Check for selected Page Image (multi-panel)
        if (webtoonScript.page_images) {
          console.log('Checking page_images for panel', panel.panel_number);
          for (const pageKey in webtoonScript.page_images) {
            const pageImgs = webtoonScript.page_images[pageKey];
            
            // Selection strategy for Page Image:
            // a) User selected
            let targetPage = pageImgs.find((img: import('@/types').PageImage) => img.is_selected);
            
            // b) Fallback to any non-mockup page image if none selected
            if (!targetPage) {
              targetPage = pageImgs.find((img: import('@/types').PageImage) => 
                !img.image_url.includes('/page1_') && !img.image_url.includes('/page2_')
              );
            }
            
            // c) Final fallback to first
            if (!targetPage) targetPage = pageImgs[0];
            
            // Check if this page includes our current panel (indices are 0-based)
            if (targetPage && targetPage.panel_indices.includes(panel.panel_number - 1)) {
              selectedImage = targetPage;
              console.log(`Panel ${panel.panel_number} using Page Image:`, targetPage.id);
              break;
            }
          }
        }
        
        // 2. If no selected Page Image, check Scene Images
        if (!selectedImage) {
          console.log('No Page Image found, checking scene_images for panel', panel.panel_number);
          const sceneImages = webtoonScript.scene_images?.[panel.panel_number] || [];
          
          // Selection strategy:
          // a) User selected
          selectedImage = sceneImages.find(img => img.is_selected);
          
          if (!selectedImage) {
             // b) Any image that looks like a real generated image (data URL or not a mockup path)
             selectedImage = sceneImages.find(img => 
               img.image_url.startsWith('data:') || 
               (!img.image_url.includes('/api/assets/cache/images/char_') && 
                !img.image_url.includes('/api/assets/cache/images/scene_') &&
                !img.image_url.includes('/api/assets/cache/images/panel'))
             );
          }
          
          // c) First available
          if (!selectedImage) {
             selectedImage = sceneImages[0];
          }
          
          if (selectedImage) {
             console.log(`Panel ${panel.panel_number} using Scene Image:`, selectedImage.id, selectedImage.image_url.substring(0, 50));
          }
        }
        
        if (!selectedImage) {
          // Draw placeholder text if no image
          ctx.fillStyle = '#000';
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.fillStyle = '#fff';
          ctx.font = '40px Arial';
          ctx.textAlign = 'center';
          ctx.fillText(`Panel ${panel.panel_number} (No Image)`, canvas.width/2, canvas.height/2);
        } else {
          // Draw image using cover (crop) mode
          await drawImageCover(selectedImage.image_url);
        }
        
        // Get Bubbles for this page/panel
        // First try page_dialogue_bubbles (new format from WebtoonSceneEditor)
        // Then fallback to dialogue_bubbles, then to panel.dialogue
        let bubbles: any[] = [];

        // Extract page number from pageKey (format: "scriptId:pageNum" or just "pageNum")
        const pageNumberForPanel = pageKey ? parseInt(pageKey.split(':').pop() || pageKey) : null;

        // Try page_dialogue_bubbles first (keyed by page number)
        if (pageNumberForPanel && webtoonScript.page_dialogue_bubbles?.[pageNumberForPanel]) {
          bubbles = webtoonScript.page_dialogue_bubbles[pageNumberForPanel];
          console.log(`Page ${pageNumberForPanel} using page_dialogue_bubbles:`, bubbles.length, 'bubbles');
        }
        // Fallback to old dialogue_bubbles (keyed by panel number)
        else if (webtoonScript.dialogue_bubbles?.[panel.panel_number]) {
          bubbles = webtoonScript.dialogue_bubbles[panel.panel_number];
          console.log(`Panel ${panel.panel_number} using dialogue_bubbles:`, bubbles.length, 'bubbles');
        }
        // Final fallback to panel.dialogue - if multi-panel page, collect all panel dialogues
        else if (selectedImage && 'panel_indices' in selectedImage && Array.isArray((selectedImage as any).panel_indices)) {
          // Multi-panel page - collect dialogues from all panels in this page
          const pageImg = selectedImage as any;
          console.log(`Collecting dialogues from panels:`, pageImg.panel_indices);
          pageImg.panel_indices.forEach((panelIdx: number) => {
            const p = webtoonScript.panels[panelIdx];
            if (p?.dialogue && Array.isArray(p.dialogue)) {
              p.dialogue.forEach((d: any, idx: number) => {
                bubbles.push({
                  text: d.text,
                  characterName: d.character,
                  x: 50,
                  y: 20 + (bubbles.length * 12), // Stack vertically
                  width: 35,
                  height: 10
                });
              });
            }
          });
          console.log(`Collected ${bubbles.length} dialogues from multi-panel page`);
        }
        else if (panel.dialogue && Array.isArray(panel.dialogue) && panel.dialogue.length > 0) {
          console.log(`Using fallback dialogue from panel ${panel.panel_number}`);
          bubbles = panel.dialogue.map((d: any, idx: number) => ({
            text: d.text,
            characterName: d.character,
            x: 50,
            y: 20 + (idx * 12),
            width: 35,
            height: 10
          }));
        }
        
        console.log(`Panel ${panel.panel_number} has ${bubbles.length} bubbles`);
        
        // Sequential bubble appearance
        // First show image for BASE_DURATION (no bubbles)
        await new Promise(r => setTimeout(r, VIDEO_CONFIG.BASE_IMAGE_DURATION_MS));
        
        // Then show each bubble one at a time
        for (let bubbleIdx = 0; bubbleIdx < bubbles.length; bubbleIdx++) {
          // Redraw image (clears previous bubble)
          if (selectedImage) {
            await drawImageCover(selectedImage.image_url);
          }
          
          // Draw ONLY the current bubble (auto-sized)
          const bubble = bubbles[bubbleIdx];
          drawBubble(
            bubble.text, 
            bubble.x, 
            bubble.y, 
            bubble.width, 
            bubble.height, 
            bubble.characterName
          );
          
          // Dynamic Duration Calculation
          const textLength = bubble.text.length;
          const { MIN_BUBBLE_DURATION_MS, PER_CHAR_DURATION_MS } = VIDEO_CONFIG;
          const duration = MIN_BUBBLE_DURATION_MS + (textLength * PER_CHAR_DURATION_MS);

          // Wait for calculating dynamic duration
          await new Promise(r => setTimeout(r, duration));
        }
        
        // Final frame: just the image (last bubble disappears)
        if (selectedImage) {
          await drawImageCover(selectedImage.image_url);
        }
        await new Promise(r => setTimeout(r, VIDEO_CONFIG.FINAL_PAUSE_MS));

        // Scroll transition to next page (not panel)
        // Find the NEXT unprocessed page
        let nextSelectedImage = null;
        let nextPageKey: string | null = null;

        for (let j = i + 1; j < totalPanels; j++) {
          const nextPanel = panels[j];

          // Find page key for next panel
          if (webtoonScript.page_images) {
            for (const pKey in webtoonScript.page_images) {
              const pageImgs = webtoonScript.page_images[pKey];
              const pageImg = pageImgs[0];
              if (pageImg?.panel_indices?.includes(nextPanel.panel_number - 1)) {
                // Check if this page hasn't been processed yet
                if (!processedPages.has(pKey)) {
                  nextPageKey = pKey;
                  const selectedPage = pageImgs.find((img: import('@/types').PageImage) => img.is_selected) || pageImgs[0];
                  nextSelectedImage = selectedPage;
                }
                break;
              }
            }
          }

          if (nextSelectedImage) break;

          // Fallback to scene images
          if (!nextSelectedImage) {
            const nextSceneImages = webtoonScript.scene_images?.[nextPanel.panel_number] || [];
            nextSelectedImage = nextSceneImages.find(img => img.is_selected) ||
                               nextSceneImages.find(img => !img.image_url.includes('/api/assets/images/')) ||
                               nextSceneImages[0];
            if (nextSelectedImage) break;
          }
        }

        // ONLY transition if we found a different next image
        if (nextSelectedImage && selectedImage && nextSelectedImage.image_url !== selectedImage.image_url) {
            const nextPageDisplay = nextPageKey?.split(':').pop() || 'next';
            setStatusText(`Transitioning to Page ${nextPageDisplay}...`);

            try {
              // Load current and next images
              const currentImg = await loadImage(selectedImage.image_url);
              const nextImg = await loadImage(nextSelectedImage.image_url);

              // Calculate transition frames (60 frames for smooth 2-second transition at 30fps)
              const transitionFrames = Math.floor(VIDEO_CONFIG.TRANSITION_DURATION_MS / (1000 / VIDEO_CONFIG.FPS));
              const frameDelay = VIDEO_CONFIG.TRANSITION_DURATION_MS / transitionFrames;

              for (let t = 0; t < transitionFrames; t++) {
                const progress = t / transitionFrames; // 0.0 to 1.0
                // Ease-in-out for smoother transition
                const eased = progress < 0.5
                  ? 2 * progress * progress
                  : 1 - Math.pow(-2 * progress + 2, 2) / 2;

                // Current image moves up
                const currentYOffset = -canvas.height * eased;
                // Next image comes from below
                const nextYOffset = canvas.height * (1 - eased);

                // Clear canvas
                ctx.fillStyle = '#000';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                // Draw current image (scrolling up) - using cover mode calculations
                const currentScale = Math.max(canvas.width / currentImg.width, canvas.height / currentImg.height);
                const currentWidth = currentImg.width * currentScale;
                const currentHeight = currentImg.height * currentScale;
                const currentX = (canvas.width - currentWidth) / 2;
                const currentY = (canvas.height - currentHeight) / 2 + currentYOffset;
                ctx.drawImage(currentImg, currentX, currentY, currentWidth, currentHeight);

                // Draw next image (scrolling up from below) - using cover mode calculations
                const nextScale = Math.max(canvas.width / nextImg.width, canvas.height / nextImg.height);
                const nextWidth = nextImg.width * nextScale;
                const nextHeight = nextImg.height * nextScale;
                const nextX = (canvas.width - nextWidth) / 2;
                const nextY = (canvas.height - nextHeight) / 2 + nextYOffset;
                ctx.drawImage(nextImg, nextX, nextY, nextWidth, nextHeight);

                await new Promise(r => setTimeout(r, frameDelay));
              }
            } catch (transitionErr) {
              console.warn('Could not generate scroll transition:', transitionErr);
              // Continue without transition if it fails
            }
          }
        }

      // Add a final pause at the end of the entire video
      await new Promise(r => setTimeout(r, 1000));
      setStatusText('Finishing video recording...');

    } catch (err) {
      console.error(err);
      setError('Error generating video');
    } finally {
      mediaRecorder.stop();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">🎬 Final Video Generation</h2>
        <p className="text-gray-600">Create a video from your webtoon scenes</p>
      </div>

      {!videoUrl ? (
        <div className="flex flex-col items-center justify-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          {!isGenerating ? (
            <div className="flex flex-col gap-4">
              {/* Browser-based generation (existing) */}
              <button
                onClick={handleGenerateVideo}
                className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white text-xl font-bold rounded-full shadow-lg hover:shadow-xl hover:scale-105 transition-all flex items-center gap-3"
              >
                <span>🎥</span>
                <span>Create Media-Webtoon (Browser)</span>
              </button>
              
              {/* Backend FFmpeg generation (new, high quality) */}
              <button
                onClick={async () => {
                  setIsGenerating(true);
                  setStatusText('Generating HQ video on server...');
                  setProgress(0);
                  
                  try {
                    // Prepare panel data with bubbles
                    // Group by PAGES (not panels) since page_images contain multi-panel images
                    const panelsData: any[] = [];
                    const processedPages = new Set<number>();

                    webtoonScript.panels.forEach(panel => {
                      // Find which page this panel belongs to
                      let pageNumber: number | null = null;
                      let selectedImage = null;

                      if (webtoonScript.page_images) {
                        for (const pageKey in webtoonScript.page_images) {
                          const pageImgs = webtoonScript.page_images[pageKey];
                          const pageImg = pageImgs[0];
                          if (pageImg?.panel_indices?.includes(panel.panel_number - 1)) {
                            pageNumber = parseInt(pageKey);
                            // Get selected image or first one
                            selectedImage = pageImgs.find((img: import('@/types').PageImage) => img.is_selected) || pageImgs[0];
                            break;
                          }
                        }
                      }

                      // Fallback to Scene Image if no page image
                      if (!selectedImage) {
                        const sceneImages = webtoonScript.scene_images?.[panel.panel_number] || [];
                        selectedImage = sceneImages.find(img => img.is_selected) || sceneImages[0];
                      }

                      // Skip if we've already processed this page (for multi-panel pages)
                      if (pageNumber && processedPages.has(pageNumber)) {
                        return;
                      }
                      if (pageNumber) {
                        processedPages.add(pageNumber);
                      }

                      // Get bubbles - prioritize page_dialogue_bubbles (new format)
                      let bubbles: any[] = [];
                      if (pageNumber && webtoonScript.page_dialogue_bubbles?.[pageNumber]) {
                        bubbles = webtoonScript.page_dialogue_bubbles[pageNumber];
                        console.log(`[Video] Page ${pageNumber} using page_dialogue_bubbles:`, bubbles.length, 'bubbles');
                      } else if (webtoonScript.dialogue_bubbles?.[panel.panel_number]) {
                        bubbles = webtoonScript.dialogue_bubbles[panel.panel_number];
                        console.log(`[Video] Panel ${panel.panel_number} using dialogue_bubbles:`, bubbles.length, 'bubbles');
                      } else {
                        console.log(`[Video] No bubbles found for page ${pageNumber} / panel ${panel.panel_number}`);
                      }

                      if (selectedImage?.image_url) {
                        const mappedBubbles = bubbles.map(b => ({
                          text: b.text,
                          x: b.x,
                          y: b.y,
                          width: b.width,
                          height: b.height,
                          character_name: b.characterName
                        }));

                        console.log(`[Video] Panel ${pageNumber || panel.panel_number} bubbles:`, mappedBubbles);

                        panelsData.push({
                          panel_number: pageNumber || panel.panel_number,
                          image_url: selectedImage.image_url,
                          bubbles: mappedBubbles
                        });
                      }
                    });
                    
                    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                    
                    setProgress(20);
                    setStatusText('Sending to server...');
                    
                    const response = await fetch(`${API_BASE_URL}/webtoon/video/generate`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({
                        script_id: webtoonScript.script_id,
                        panels: panelsData
                      })
                    });
                    
                    if (!response.ok) {
                      const error = await response.json();
                      throw new Error(error.detail || 'Video generation failed');
                    }
                    
                    setProgress(80);
                    setStatusText('Downloading video...');
                    
                    // Download the video
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    setVideoUrl(url);
                    setStatusText('HQ Video generated!');
                    
                  } catch (err) {
                    console.error('Backend video generation error:', err);
                    setError(err instanceof Error ? err.message : 'Backend video generation failed');
                  } finally {
                    setIsGenerating(false);
                    setProgress(100);
                  }
                }}
                className="px-8 py-4 bg-gradient-to-r from-green-600 to-teal-600 text-white text-xl font-bold rounded-full shadow-lg hover:shadow-xl hover:scale-105 transition-all flex items-center gap-3"
              >
                <span>⚡</span>
                <span>Create HQ Video (Server FFmpeg)</span>
              </button>
              
              <p className="text-sm text-gray-500 text-center mt-2">
                HQ version uses server-side FFmpeg for better quality
              </p>
            </div>
          ) : (
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-lg font-semibold text-gray-700">{statusText}</p>
              <div className="w-64 h-3 bg-gray-200 rounded-full mt-4 overflow-hidden">
                <div 
                  className="h-full bg-purple-600 transition-all duration-300"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          <div className="aspect-[9/16] max-w-sm mx-auto bg-black rounded-lg overflow-hidden shadow-2xl">
            <video 
              ref={videoRef}
              src={videoUrl} 
              controls 
              className="w-full h-full object-contain"
            />
          </div>
          
          <div className="flex justify-center gap-4 flex-wrap">
            <button
              onClick={async () => {
                if (!videoUrl) return;
                setStatusText('Converting to MP4...');
                setIsGenerating(true);
                
                try {
                  // Fetch the webm blob
                  const response = await fetch(videoUrl);
                  const webmBlob = await response.blob();
                  
                  // Create form data
                  const formData = new FormData();
                  formData.append('file', webmBlob, 'video.webm');
                  
                  // Upload to backend for conversion
                  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                  const convertResponse = await fetch(`${API_BASE_URL}/webtoon/video/convert-to-mp4`, {
                    method: 'POST',
                    body: formData,
                  });
                  
                  if (!convertResponse.ok) {
                    const error = await convertResponse.json();
                    throw new Error(error.detail || 'Conversion failed');
                  }
                  
                  // Download the MP4
                  const mp4Blob = await convertResponse.blob();
                  const mp4Url = URL.createObjectURL(mp4Blob);
                  
                  const a = document.createElement('a');
                  a.href = mp4Url;
                  a.download = `webtoon_story_${webtoonScript.script_id.slice(0, 8)}.mp4`;
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                  URL.revokeObjectURL(mp4Url);
                  
                  setStatusText('Download complete!');
                } catch (error) {
                  console.error('MP4 conversion error:', error);
                  setError(error instanceof Error ? error.message : 'MP4 conversion failed');
                } finally {
                  setIsGenerating(false);
                  setStatusText('');
                }
              }}
              disabled={isGenerating}
              className="px-6 py-3 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <span>📥</span>
              Download MP4 (YouTube Shorts)
            </button>
            
            <a 
              href={videoUrl} 
              download={`webtoon_story_${webtoonScript.script_id.slice(0, 8)}.webm`}
              className="px-6 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <span>⬇️</span>
              Download WebM
            </a>
            
            <button
              onClick={() => setVideoUrl(null)}
              className="px-6 py-3 bg-gray-200 text-gray-700 font-bold rounded-lg hover:bg-gray-300 transition-colors"
            >
              Generate New
            </button>
          </div>
        </div>
      )}

      {/* Hidden Canvas for Processing */}
      <canvas 
        ref={canvasRef} 
        className="hidden" // Hidden from view, used for processing
      />
      
      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-center">
          {error}
        </div>
      )}
    </div>
  );
}
