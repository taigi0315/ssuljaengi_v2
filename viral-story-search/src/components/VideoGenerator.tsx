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
  // Canvas/Video dimensions (4:5 for Instagram/Facebook Feed)
  CANVAS_WIDTH: 1080,
  CANVAS_HEIGHT: 1920,
  
  // Timing (in milliseconds)
  BASE_IMAGE_DURATION_MS: 2000,    // How long to show image before first bubble
  DIALOGUE_DURATION_MS: 2000,      // How long each dialogue bubble shows
  FINAL_PAUSE_MS: 500,             // Pause after last bubble before next panel
  
  // Bubble styling
  BUBBLE_FONT_SIZE: 43,            // Font size for dialogue text
  BUBBLE_PADDING: 35,              // Padding inside bubble
  BUBBLE_BORDER_RADIUS: 20,        // Rounded corner radius
  BUBBLE_BORDER_WIDTH: 5,          // Border thickness
  BUBBLE_BG_OPACITY: 0.1,          // Background opacity (0-1)
  BUBBLE_BORDER_COLOR: '#4a4a4a',  // Border color
  BUBBLE_TEXT_COLOR: '#1a1a1a',    // Text color
  
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
    const drawBubble = (text: string, xPercent: number, yPercent: number) => {
      const { 
        BUBBLE_FONT_SIZE, BUBBLE_PADDING, BUBBLE_BORDER_RADIUS, 
        BUBBLE_BORDER_WIDTH, BUBBLE_BG_OPACITY, BUBBLE_BORDER_COLOR, BUBBLE_TEXT_COLOR 
      } = VIDEO_CONFIG;
      
      // Measure text to auto-size bubble
      ctx.font = `bold ${BUBBLE_FONT_SIZE}px Arial`;
      const textMetrics = ctx.measureText(text);
      const textWidth = Math.min(textMetrics.width, canvas.width * 0.85); // Max 85% of CANVAS width (visible area)
      const textHeight = BUBBLE_FONT_SIZE;
      
      // Calculate bubble dimensions
      const bw = textWidth + BUBBLE_PADDING * 2;
      const bh = textHeight + BUBBLE_PADDING * 2;
      
      // Position relative to IMAGE area (transforming user placement on original 1:1 image to zoomed canvas space)
      const absoluteX = imageRect.x + (xPercent / 100) * imageRect.width;
      const absoluteY = imageRect.y + (yPercent / 100) * imageRect.height;
      
      // Center bubble on the point
      let bx = absoluteX - bw / 2;
      let by = absoluteY - bh / 2;
      
      // Clamp to CANVAS bounds (visible area), not image bounds
      // keeping 20px padding from edges
      bx = Math.max(20, Math.min(canvas.width - bw - 20, bx));
      by = Math.max(20, Math.min(canvas.height - bh - 20, by));
      
      // Draw Bubble Background with semi-transparent white
      ctx.fillStyle = `rgba(255, 255, 255, 0.85)`; // More visible background
      ctx.strokeStyle = BUBBLE_BORDER_COLOR;
      ctx.lineWidth = BUBBLE_BORDER_WIDTH;
      
      // Rounded rect
      const radius = BUBBLE_BORDER_RADIUS;
      ctx.beginPath();
      ctx.moveTo(bx + radius, by);
      ctx.lineTo(bx + bw - radius, by);
      ctx.quadraticCurveTo(bx + bw, by, bx + bw, by + radius);
      ctx.lineTo(bx + bw, by + bh - radius);
      ctx.quadraticCurveTo(bx + bw, by + bh, bx + bw - radius, by + bh);
      ctx.lineTo(bx + radius, by + bh);
      ctx.quadraticCurveTo(bx, by + bh, bx, by + bh - radius);
      ctx.lineTo(bx, by + radius);
      ctx.quadraticCurveTo(bx, by, bx + radius, by);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      
      // Draw Text (guaranteed visible with dark color on light background)
      ctx.fillStyle = '#000000';
      ctx.font = `bold ${BUBBLE_FONT_SIZE}px Arial`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, bx + bw / 2, by + bh / 2, bw - BUBBLE_PADDING);
    };

    try {
      // Iterate scenes
      const panels = webtoonScript.panels;
      const totalPanels = panels.length;
      
      for (let i = 0; i < totalPanels; i++) {
        const panel = panels[i];
        setStatusText(`Processing Panel ${panel.panel_number}/${totalPanels}...`);
        setProgress(((i) / totalPanels) * 100);
        
        // Get Scene Image
        const sceneImages = webtoonScript.scene_images?.[panel.panel_number] || [];
        const selectedImage = sceneImages.find(img => img.is_selected) || sceneImages[0];
        
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
        
        // Get Bubbles for this panel
        const bubbles = webtoonScript.dialogue_bubbles?.[panel.panel_number] || [];
        
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
          drawBubble(bubble.text, bubble.x, bubble.y);
          
          // Wait for bubble display duration
          await new Promise(r => setTimeout(r, VIDEO_CONFIG.DIALOGUE_DURATION_MS));
        }
        
        // Final frame: just the image (last bubble disappears)
        if (selectedImage) {
          await drawImageCover(selectedImage.image_url);
        }
        await new Promise(r => setTimeout(r, VIDEO_CONFIG.FINAL_PAUSE_MS));
      }
      
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
                    const panelsData = webtoonScript.panels.map(panel => {
                      const sceneImages = webtoonScript.scene_images?.[panel.panel_number] || [];
                      const selectedImage = sceneImages.find(img => img.is_selected) || sceneImages[0];
                      const bubbles = webtoonScript.dialogue_bubbles?.[panel.panel_number] || [];
                      
                      return {
                        panel_number: panel.panel_number,
                        image_url: selectedImage?.image_url || '',
                        bubbles: bubbles.map(b => ({
                          text: b.text,
                          x: b.x,
                          y: b.y
                        }))
                      };
                    }).filter(p => p.image_url);
                    
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
