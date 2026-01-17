'use client';

import { useState, useRef, useEffect } from 'react';
import { WebtoonScript, StoryGenre } from '@/types';

interface VideoGeneratorProps {
  webtoonScript: WebtoonScript;
  genre: StoryGenre;
}

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

    // Canvas settings (1080x1920 for vertical video, or 1080x1350?)
    // User requested "vertical full-screen images" in previous session context.
    // Let's us 1080x1920 (9:16)
    canvas.width = 1080;
    canvas.height = 1920;
    
    // MediaRecorder setup
    const stream = canvas.captureStream(30); // 30 FPS
    const chunks: Blob[] = [];
    const mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'video/webm;codecs=vp9'
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
          // Load and draw image
          try {
            const img = await loadImage(selectedImage.image_url);
            // Draw image to cover canvas
            // Simple cover logic
            const scale = Math.max(canvas.width / img.width, canvas.height / img.height);
            const x = (canvas.width / 2) - (img.width / 2) * scale;
            const y = (canvas.height / 2) - (img.height / 2) * scale;
            ctx.drawImage(img, x, y, img.width * scale, img.height * scale);
          } catch (e) {
            console.error('Failed to load image', e);
            ctx.fillStyle = '#333';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
          }
        }
        
        // Draw Bubbles
        const bubbles = webtoonScript.dialogue_bubbles?.[panel.panel_number] || [];
        // Calculate duration based on bubbles count: 4s + 0.5s * count
        // Wait, user said: "4 seconds + 0.5 second * number of dialogue"
        // Let's assume count of bubbles.
        const duration = 4000 + (bubbles.length * 500);
        
        // Render frames for this duration
        const startTime = Date.now();
        while (Date.now() - startTime < duration) {
            // Need to keep drawing for stream?
            // Actually canvas contents persist until cleared/drawn over.
            // But if we want animations (fade in bubbles), we need loop.
            // For now static image + bubbles is fine.
            // If bubbles appear sequentially? Maybe Phase 4.
            // Just draw everything and wait.
            
            // Draw bubbles (re-draw every frame if we had animation, but here static)
            // Just wait.
            
            // Re-drawing same content is redundant but ensures stream keeps flowing?
            // "requestAnimationFrame" is usually used.
            // But inside async loop, we can just use "await delay".
            
            // Draw bubbles on top
            bubbles.forEach(bubble => {
                const bx = (bubble.x / 100) * canvas.width;
                const by = (bubble.y / 100) * canvas.height;
                // Use stored width/height if available, else defaults
                const bw = ((bubble.width || 30) / 100) * canvas.width;
                const bh = ((bubble.height || 15) / 100) * canvas.height;
                
                // Draw Bubble Background
                ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
                // Rounded rect logic... simplified for now as rect
                ctx.fillRect(bx, by, bw, bh);
                
                // Draw Text
                ctx.fillStyle = '#000';
                ctx.font = '30px Arial'; // Simplified
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                // Simple text wrap or just center truncated?
                // For MVP just center text
                ctx.fillText(bubble.text, bx + bw/2, by + bh/2, bw - 20);
                
                // Draw Character Name
                ctx.fillStyle = 'purple';
                ctx.font = 'bold 24px Arial';
                ctx.fillText(bubble.characterName, bx + bw/2, by - 20);
            });
            
            // Trigger stream update?
            // In Firefox/Chrome canvas stream executes on paint?
            // We might need to make small changes or just wait?
            // Actually stream captures at frame rate.
            
            await new Promise(r => setTimeout(r, 100)); // Wait 100ms
        }
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
            <button
              onClick={handleGenerateVideo}
              className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white text-xl font-bold rounded-full shadow-lg hover:shadow-xl hover:scale-105 transition-all flex items-center gap-3"
            >
              <span>🎥</span>
              <span>Create Media-Webtoon</span>
            </button>
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
          
          <div className="flex justify-center gap-4">
            <a 
              href={videoUrl} 
              download={`webtoon_story_${webtoonScript.script_id.slice(0, 8)}.webm`}
              className="px-6 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <span>⬇️</span>
              Download Video
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
