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
    
    def _scale_to_cover(self, img: Image.Image) -> Image.Image:
        """Scale image to cover target dimensions without cropping."""
        target_w = self.config.width
        target_h = self.config.height
        
        # Calculate scale to cover (fit larger dimension)
        scale = max(target_w / img.width, target_h / img.height)
        
        # Resize
        new_w = int(img.width * scale)
        new_h = int(img.height * scale)
        return img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    def _crop_center(self, img: Image.Image) -> Image.Image:
        """Crop image to target dimensions from center."""
        target_w = self.config.width
        target_h = self.config.height
        
        left = (img.width - target_w) // 2
        top = (img.height - target_h) // 2
        right = left + target_w
        bottom = top + target_h
        
        return img.crop((left, top, right, bottom))
    
    def render_bubble(
        self, 
        img: Image.Image, 
        text: str, 
        x_pct: float, 
        y_pct: float,
        w_pct: Optional[float] = None,
        h_pct: Optional[float] = None
    ) -> Image.Image:
        """
        Render a dialogue bubble on the image.
        
        Args:
            img: PIL Image to draw on
            text: Dialogue text
            x_pct: X position as percentage (0-100)
            y_pct: Y position as percentage (0-100)
            w_pct: Width as percentage (optional)
            h_pct: Height as percentage (optional)
        
        Returns:
            Image with bubble overlay
        """
        img = img.copy()
        draw = ImageDraw.Draw(img)
        
        # Calculate dimensions
        if w_pct is not None and h_pct is not None:
            # Use user-defined dimensions
            bw = (w_pct / 100) * img.width
            bh = (h_pct / 100) * img.height
            
            # Wrap text to fit width
            # Approximate chars per line: width / (font_size * 0.6)
            chars_per_line = int(bw / (self.config.font_size * 0.5))
            import textwrap
            wrapped_text = textwrap.fill(text, width=max(5, chars_per_line))
        else:
            # Legacy: Measure text (single line)
            bbox = draw.textbbox((0, 0), text, font=self.font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Limit text width to 85% of image
            max_width = int(img.width * 0.85)
            if text_width > max_width:
                text_width = max_width
            
            # Bubble dimensions with padding
            padding = self.config.bubble_padding
            bw = text_width + padding * 2
            bh = text_height + padding * 2
            wrapped_text = text
        
        # Position (centered on percentage point)
        # Frontend logic: top/left percentages are usually top-left of element?
        # Re-checking frontend: The bubble div uses left: x%, top: y%. 
        # But render_bubble historically treated x_pct/y_pct as CENTER or Top-Left?
        # Previous code: bx = abs_x - bw / 2 (Center)
        # Frontend default: usually assumes top-left anchor unless transform translate is used.
        # Looking at SceneImageGeneratorV2.tsx: left: `${bubble.x}%`, top: `${bubble.y}%`. 
        # Does it transform? No. So frontend is TOP-LEFT positioned.
        # But previous backend logic was CENTER positioned (bx = abs_x - bw / 2).
        # We should probably switch to TOP-LEFT to match frontend if that's what frontend does.
        # Frontend jsx: <div style={{left: ..., top: ...}}> ... </div>
        # Standard CSS positioning is top-left corner.
        
        abs_x = (x_pct / 100) * img.width
        abs_y = (y_pct / 100) * img.height
        
        # Switch to Top-Left positioning to match CSS default
        bx = abs_x
        by = abs_y
        
        # Ensure it fits in image (clamping)
        # bx = max(0, min(img.width - bw, bx))
        # by = max(0, min(img.height - bh, by))
        
        # Draw bubble background
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        bubble_img_path = os.path.join(assets_dir, "bubble.png")
        
        custom_bubble_used = False
        if os.path.exists(bubble_img_path):
            try:
                # Load custom bubble
                bubble_asset = Image.open(bubble_img_path).convert("RGBA")
                
                # Resize to target dimensions
                bubble_asset = bubble_asset.resize((int(bw), int(bh)), Image.Resampling.LANCZOS)
                
                # Apply opacity
                opacity = self.config.bubble_bg_opacity
                if opacity < 1.0:
                    r, g, b, a = bubble_asset.split()
                    a = a.point(lambda p: int(p * opacity))
                    bubble_asset.putalpha(a)
                
                # Paste
                img.alpha_composite(bubble_asset, (int(bx), int(by)))
                custom_bubble_used = True
                
            except Exception as e:
                logger.error(f"Failed to load custom bubble asset: {str(e)}")
        
        if not custom_bubble_used:
            # Fallback: Draw rounded rectangle background
            radius = 20
            bg_color = (255, 255, 255, int(self.config.bubble_bg_opacity * 255))
            border_color = self._hex_to_rgb(self.config.bubble_border_color)
            
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
        
        # Use multiline text drawing
        draw.multiline_text(
            (text_x, text_y),
            wrapped_text,
            font=self.font,
            fill=text_color,
            anchor="mm",  # Middle-middle anchor
            align="center"
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
        
        # Scale to cover (don't crop yet)
        img = self._scale_to_cover(img)
        
        # Render bubbles on scaled full image (preserves relative coordinates logic)
        for bubble in bubbles:
            img = self.render_bubble(
                img, 
                bubble.text, 
                bubble.x, 
                bubble.y,
                getattr(bubble, 'width', None),
                getattr(bubble, 'height', None)
            )
            
        # Crop to target size
        img = self._crop_center(img)
        
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
            
            for panel_idx, panel in enumerate(panels):
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
                
                # Process image pipeline logic matching frontend
                base_scaled = self._scale_to_cover(base_img)
                final_base = self._crop_center(base_scaled)
                
                # Calculate frame counts
                base_frames = int(self.config.base_duration_ms / 1000 * self.config.fps)
                bubble_frames = int(self.config.bubble_duration_ms / 1000 * self.config.fps)
                final_frames = int(self.config.final_pause_ms / 1000 * self.config.fps)
                
                # 1. Base image without bubbles
                for _ in range(base_frames):
                    frame_path = os.path.join(temp_dir, f"frame_{frame_idx:06d}.png")
                    final_base.convert("RGB").save(frame_path, "PNG")
                    frame_paths.append(frame_path)
                    frame_idx += 1
                
                # 2. Each bubble sequentially
                for bubble in panel.bubbles:
                    # Render bubble on COPY of scaled image
                    # We use scaled image (not cropped) to calculate position correctly
                    img_with_bubble = self.render_bubble(
                        base_scaled.copy(), 
                        bubble.text, 
                        bubble.x, 
                        bubble.y,
                        getattr(bubble, 'width', None),
                        getattr(bubble, 'height', None)
                    )
                    
                    # THEN crop it
                    frame_with_bubble = self._crop_center(img_with_bubble)
                    
                    for _ in range(bubble_frames):
                        frame_path = os.path.join(temp_dir, f"frame_{frame_idx:06d}.png")
                        frame_with_bubble.convert("RGB").save(frame_path, "PNG")
                        frame_paths.append(frame_path)
                        frame_idx += 1
                
                # 3. Final pause (image only)
                for _ in range(final_frames):
                    frame_path = os.path.join(temp_dir, f"frame_{frame_idx:06d}.png")
                    final_base.convert("RGB").save(frame_path, "PNG")
                    frame_paths.append(frame_path)
                    frame_idx += 1

                # 4. Scroll transition to next panel (except for last panel)
                if panel_idx < len(panels) - 1:
                    next_panel = panels[panel_idx + 1]
                    next_image_url = next_panel.image_url

                    # Load next panel image
                    try:
                        if next_image_url.startswith('data:image'):
                            import base64
                            header, encoded = next_image_url.split(',', 1)
                            image_data = base64.b64decode(encoded)
                            next_base_img = Image.open(BytesIO(image_data)).convert("RGBA")
                        elif next_image_url.startswith(('http://', 'https://')):
                            next_base_img = self.download_image_sync(next_image_url)
                        elif next_image_url.startswith('/api/assets/cache/images/'):
                            filename = next_image_url.split('/')[-1]
                            local_path = os.path.join(
                                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                'cache', 'images', filename
                            )
                            if os.path.exists(local_path):
                                next_base_img = Image.open(local_path).convert("RGBA")
                            else:
                                continue  # Skip transition if next image not found
                        elif os.path.exists(next_image_url):
                            next_base_img = Image.open(next_image_url).convert("RGBA")
                        else:
                            continue  # Skip transition if next image can't be loaded

                        # Process next image
                        next_scaled = self._scale_to_cover(next_base_img)
                        next_final = self._crop_center(next_scaled)

                        # Generate scroll transition frames
                        transition_frames = int(self.config.transition_duration_ms / 1000 * self.config.fps)

                        for t in range(transition_frames):
                            progress = t / transition_frames  # 0.0 to 1.0
                            # Ease-in-out for smoother transition
                            eased = 0.5 - 0.5 * (1 - progress * 2) ** 2 if progress < 0.5 else 0.5 + 0.5 * (1 - (1 - progress) * 2) ** 2

                            # Current image moves up
                            current_y_offset = -int(self.config.height * eased)
                            # Next image comes from below
                            next_y_offset = int(self.config.height * (1 - eased))

                            # Create transition frame
                            transition_frame = Image.new("RGB", (self.config.width, self.config.height), (0, 0, 0))

                            # Paste current image (scrolling up)
                            if current_y_offset > -self.config.height:
                                transition_frame.paste(final_base.convert("RGB"), (0, current_y_offset))

                            # Paste next image (scrolling up from below)
                            if next_y_offset < self.config.height:
                                transition_frame.paste(next_final.convert("RGB"), (0, next_y_offset))

                            frame_path = os.path.join(temp_dir, f"frame_{frame_idx:06d}.png")
                            transition_frame.save(frame_path, "PNG")
                            frame_paths.append(frame_path)
                            frame_idx += 1

                        logger.info(f"Added {transition_frames} scroll transition frames")

                    except Exception as e:
                        logger.warning(f"Could not generate scroll transition: {e}")
                        # Continue without transition if it fails

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
                "-profile:v", "high",
                "-level", "4.0",
                "-crf", str(self.config.crf),
                "-preset", "slow",
                "-pix_fmt", "yuv420p",
                "-r", str(self.config.fps),
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
