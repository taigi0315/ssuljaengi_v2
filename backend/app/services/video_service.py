"""
Video generation service using Pillow and FFmpeg.

This module handles:
- Image downloading and processing
- Dialogue bubble overlay rendering
- Video generation from image sequences
"""
import logging
import os
import subprocess
import tempfile
import shutil
from typing import List, Tuple, Optional
from pathlib import Path
from io import BytesIO

import httpx
from PIL import Image, ImageDraw, ImageFont

from app.models.video_models import BubbleData, VideoPanelData, VideoConfig

logger = logging.getLogger(__name__)


class VideoService:
    """Service for generating videos with dialogue bubble overlays."""
    
    def __init__(self, config: Optional[VideoConfig] = None):
        self.config = config or VideoConfig()
        self._font: Optional[ImageFont.FreeTypeFont] = None
    
    @property
    def font(self) -> ImageFont.FreeTypeFont:
        """Lazy load font."""
        if self._font is None:
            try:
                # Try common system fonts
                font_paths = [
                    "/System/Library/Fonts/Helvetica.ttc",  # macOS
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                    "C:\\Windows\\Fonts\\arial.ttf",  # Windows
                    "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS alt
                ]
                for path in font_paths:
                    if os.path.exists(path):
                        self._font = ImageFont.truetype(path, self.config.font_size)
                        logger.info(f"Loaded font from: {path}")
                        break
                
                if self._font is None:
                    # Fallback to default
                    self._font = ImageFont.load_default()
                    logger.warning("Using default font (may not support all characters)")
            except Exception as e:
                logger.error(f"Font loading error: {e}")
                self._font = ImageFont.load_default()
        
        return self._font
    
    async def download_image(self, url: str) -> Image.Image:
        """Download image from URL and return PIL Image."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert("RGBA")
    
    def download_image_sync(self, url: str) -> Image.Image:
        """Synchronous version of download_image."""
        with httpx.Client() as client:
            response = client.get(url, follow_redirects=True)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert("RGBA")
    
    def crop_to_cover(self, img: Image.Image) -> Image.Image:
        """
        Crop image to cover target dimensions (4:5 ratio).
        Centers the crop on the image.
        """
        target_w = self.config.width
        target_h = self.config.height
        
        # Calculate scale to cover (fit larger dimension)
        scale = max(target_w / img.width, target_h / img.height)
        
        # Resize
        new_w = int(img.width * scale)
        new_h = int(img.height * scale)
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Crop to center
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        right = left + target_w
        bottom = top + target_h
        
        return img_resized.crop((left, top, right, bottom))
    
    def render_bubble(
        self, 
        img: Image.Image, 
        text: str, 
        x_pct: float, 
        y_pct: float
    ) -> Image.Image:
        """
        Render a dialogue bubble on the image.
        
        Args:
            img: PIL Image to draw on
            text: Dialogue text
            x_pct: X position as percentage (0-100)
            y_pct: Y position as percentage (0-100)
        
        Returns:
            Image with bubble overlay
        """
        img = img.copy()
        draw = ImageDraw.Draw(img)
        
        # Measure text
        bbox = draw.textbbox((0, 0), text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Limit text width to 85% of image
        max_width = int(img.width * 0.85)
        if text_width > max_width:
            text_width = max_width
        
        # Bubble dimensions
        padding = self.config.bubble_padding
        bw = text_width + padding * 2
        bh = text_height + padding * 2
        
        # Position (centered on percentage point)
        abs_x = (x_pct / 100) * img.width
        abs_y = (y_pct / 100) * img.height
        
        bx = abs_x - bw / 2
        by = abs_y - bh / 2
        
        # Clamp to image bounds
        bx = max(20, min(img.width - bw - 20, bx))
        by = max(20, min(img.height - bh - 20, by))
        
        # Draw rounded rectangle background
        radius = 20
        bg_color = (255, 255, 255, int(self.config.bubble_bg_opacity * 255))
        border_color = self._hex_to_rgb(self.config.bubble_border_color)
        
        # Draw filled rounded rectangle
        draw.rounded_rectangle(
            [(bx, by), (bx + bw, by + bh)],
            radius=radius,
            fill=bg_color,
            outline=border_color,
            width=self.config.bubble_border_width
        )
        
        # Draw text centered in bubble
        text_x = bx + bw / 2
        text_y = by + bh / 2
        text_color = self._hex_to_rgb(self.config.bubble_text_color)
        
        draw.text(
            (text_x, text_y),
            text,
            font=self.font,
            fill=text_color,
            anchor="mm"  # Middle-middle anchor
        )
        
        return img
    
    def generate_frame(
        self, 
        image_url: str, 
        bubbles: List[BubbleData]
    ) -> Image.Image:
        """
        Generate a single frame with bubbles overlaid.
        
        Args:
            image_url: URL or local path to image
            bubbles: List of bubbles to render
        
        Returns:
            PIL Image with bubbles
        """
        # Load image
        if image_url.startswith(('http://', 'https://')):
            img = self.download_image_sync(image_url)
        else:
            img = Image.open(image_url).convert("RGBA")
        
        # Crop to cover
        img = self.crop_to_cover(img)
        
        # Render bubbles
        for bubble in bubbles:
            img = self.render_bubble(img, bubble.text, bubble.x, bubble.y)
        
        return img
    
    def generate_video(
        self, 
        panels: List[VideoPanelData],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate MP4 video from panels.
        
        Args:
            panels: List of panel data with images and bubbles
            output_path: Optional output file path
        
        Returns:
            Path to generated MP4 file
        """
        temp_dir = tempfile.mkdtemp(prefix="video_gen_")
        logger.info(f"Generating video with {len(panels)} panels in {temp_dir}")
        
        try:
            frame_paths = []
            frame_idx = 0
            
            for panel in panels:
                logger.info(f"Processing panel {panel.panel_number}")
                
                # Resolve image URL to loadable source
                image_url = panel.image_url
                logger.info(f"Image URL: {image_url[:100]}...")
                
                # Handle different URL formats
                if image_url.startswith('data:image'):
                    # Base64 data URL - decode and load
                    import base64
                    # Format: data:image/png;base64,XXXXX
                    header, encoded = image_url.split(',', 1)
                    image_data = base64.b64decode(encoded)
                    base_img = Image.open(BytesIO(image_data)).convert("RGBA")
                    logger.info(f"Loaded image from base64 data URL")
                elif image_url.startswith(('http://', 'https://')):
                    base_img = self.download_image_sync(image_url)
                elif image_url.startswith('/api/assets/cache/images/'):
                    # Convert API URL to local file path
                    # /api/assets/cache/images/filename.png -> backend/cache/images/filename.png
                    filename = image_url.split('/')[-1]
                    local_path = os.path.join(
                        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        'cache', 'images', filename
                    )
                    logger.info(f"Resolved to local path: {local_path}")
                    if os.path.exists(local_path):
                        base_img = Image.open(local_path).convert("RGBA")
                    else:
                        raise FileNotFoundError(f"Image not found: {local_path}")
                elif os.path.exists(image_url):
                    # Direct file path
                    base_img = Image.open(image_url).convert("RGBA")
                else:
                    raise ValueError(f"Cannot load image from: {image_url[:100]}")
                
                base_img = self.crop_to_cover(base_img)
                
                # Calculate frame counts
                base_frames = int(self.config.base_duration_ms / 1000 * self.config.fps)
                bubble_frames = int(self.config.bubble_duration_ms / 1000 * self.config.fps)
                final_frames = int(self.config.final_pause_ms / 1000 * self.config.fps)
                
                # 1. Base image without bubbles
                for _ in range(base_frames):
                    frame_path = os.path.join(temp_dir, f"frame_{frame_idx:06d}.png")
                    base_img.convert("RGB").save(frame_path, "PNG")
                    frame_paths.append(frame_path)
                    frame_idx += 1
                
                # 2. Each bubble sequentially
                for bubble in panel.bubbles:
                    frame_with_bubble = self.render_bubble(
                        base_img.copy(), 
                        bubble.text, 
                        bubble.x, 
                        bubble.y
                    )
                    
                    for _ in range(bubble_frames):
                        frame_path = os.path.join(temp_dir, f"frame_{frame_idx:06d}.png")
                        frame_with_bubble.convert("RGB").save(frame_path, "PNG")
                        frame_paths.append(frame_path)
                        frame_idx += 1
                
                # 3. Final pause (image only)
                for _ in range(final_frames):
                    frame_path = os.path.join(temp_dir, f"frame_{frame_idx:06d}.png")
                    base_img.convert("RGB").save(frame_path, "PNG")
                    frame_paths.append(frame_path)
                    frame_idx += 1
            
            logger.info(f"Generated {len(frame_paths)} frames")
            
            # Verify frames exist
            if len(frame_paths) == 0:
                raise RuntimeError("No frames were generated")
            
            first_frame = os.path.join(temp_dir, "frame_000000.png")
            if not os.path.exists(first_frame):
                logger.error(f"First frame not found: {first_frame}")
                raise RuntimeError(f"First frame not found at {first_frame}")
            
            logger.info(f"First frame exists: {first_frame} ({os.path.getsize(first_frame)} bytes)")
            
            # Generate MP4 using FFmpeg
            if output_path is None:
                output_path = os.path.join(temp_dir, "output.mp4")
            
            cmd = [
                "ffmpeg", "-y",
                "-framerate", str(self.config.fps),
                "-i", os.path.join(temp_dir, "frame_%06d.png"),
                "-c:v", "libx264",
                "-crf", str(self.config.crf),
                "-preset", "slow",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                output_path
            ]
            
            logger.info(f"Running FFmpeg: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                # Show the LAST 1500 chars of stderr to see actual error
                logger.error(f"FFmpeg stderr (last 1500 chars): {result.stderr[-1500:]}")
                logger.error(f"FFmpeg stdout: {result.stdout[-500:]}")
                raise RuntimeError(f"FFmpeg failed: {result.stderr[-1000:]}")
            
            logger.info(f"Video generated: {output_path}")
            
            # If output is in temp dir, copy to new temp file that won't be deleted
            if output_path.startswith(temp_dir):
                final_temp = tempfile.NamedTemporaryFile(
                    suffix=".mp4", 
                    delete=False,
                    prefix="webtoon_video_"
                )
                shutil.copy(output_path, final_temp.name)
                output_path = final_temp.name
            
            return output_path
            
        finally:
            # Cleanup temp frames (but not output if it's the final file)
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp dir: {e}")
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


# Singleton instance
video_service = VideoService()
