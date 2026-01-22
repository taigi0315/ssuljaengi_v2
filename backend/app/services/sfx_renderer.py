"""
SFX Renderer Service for Webtoon Enhancement.

This module provides functionality to render visual effects (SFX) onto webtoon
panels and video frames. It supports:
- Impact text (onomatopoeia) rendering with various styles
- Screen effects (flash, shake, vignette)
- Motion effects (speed lines, blur)
- Emotional effects (sparkles, hearts, dark aura)

v2.0.0: Initial implementation
"""

import math
import random
from pathlib import Path
from typing import List, Optional, Tuple, Union

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

from app.config import get_settings
from app.models.sfx import (
    ImpactText,
    ImpactTextStyle,
    ImpactTextSize,
    ImpactTextAnimation,
    MotionEffect,
    MotionEffectType,
    MotionDirection,
    ScreenEffect,
    ScreenEffectType,
    EmotionalEffect,
    EmotionalEffectType,
    EmotionalEffectPosition,
    EffectIntensity,
    SFXBundle,
    SFXEffect,
)


# ============================================================================
# Constants
# ============================================================================

# Size multipliers for impact text (relative to image height)
IMPACT_TEXT_SIZE_MULTIPLIERS = {
    ImpactTextSize.SMALL: 0.05,
    ImpactTextSize.MEDIUM: 0.08,
    ImpactTextSize.LARGE: 0.12,
    ImpactTextSize.MASSIVE: 0.18,
}

# Intensity multipliers for effects
INTENSITY_MULTIPLIERS = {
    EffectIntensity.SUBTLE: 0.3,
    EffectIntensity.MEDIUM: 0.6,
    EffectIntensity.INTENSE: 1.0,
}

# Screen shake pixel offsets by intensity
SHAKE_OFFSETS = {
    EffectIntensity.SUBTLE: 5,
    EffectIntensity.MEDIUM: 12,
    EffectIntensity.INTENSE: 25,
}

# Flash opacity by intensity
FLASH_OPACITY = {
    EffectIntensity.SUBTLE: 0.3,
    EffectIntensity.MEDIUM: 0.5,
    EffectIntensity.INTENSE: 0.8,
}


# ============================================================================
# SFX Renderer Class
# ============================================================================

class SFXRenderer:
    """
    Renderer for visual effects on webtoon panels and video frames.
    
    This class provides methods to render various SFX types onto images,
    including impact text, screen effects, motion effects, and emotional effects.
    """
    
    def __init__(self, font_path: Optional[str] = None):
        """
        Initialize the SFX renderer.
        
        Args:
            font_path: Optional path to a custom font file. If None, uses default.
        """
        self._settings = get_settings()
        self._font_path = font_path or self._settings.sfx_font_path
        self._assets_dir = Path(self._settings.sfx_assets_dir)
        self._font_cache: dict[int, ImageFont.FreeTypeFont] = {}
    
    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """
        Get a font at the specified size, with caching.
        
        Args:
            size: Font size in pixels
            bold: Whether to use bold variant (if available)
            
        Returns:
            PIL ImageFont instance
        """
        cache_key = (size, bold)
        if cache_key not in self._font_cache:
            if self._font_path and Path(self._font_path).exists():
                try:
                    font = ImageFont.truetype(self._font_path, size)
                except Exception:
                    font = ImageFont.load_default()
            else:
                # Use default font - try to load a system font
                try:
                    # Try common system fonts
                    system_fonts = [
                        "/System/Library/Fonts/Helvetica.ttc",  # macOS
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                        "C:/Windows/Fonts/arial.ttf",  # Windows
                    ]
                    font = None
                    for font_file in system_fonts:
                        if Path(font_file).exists():
                            font = ImageFont.truetype(font_file, size)
                            break
                    if font is None:
                        font = ImageFont.load_default()
                except Exception:
                    font = ImageFont.load_default()
            
            self._font_cache[cache_key] = font
        
        return self._font_cache[cache_key]
    
    # ========================================================================
    # Impact Text Rendering (1.5.3)
    # ========================================================================
    
    def render_impact_text(
        self,
        image: Image.Image,
        impact_text: ImpactText
    ) -> Image.Image:
        """
        Render impact text (onomatopoeia) onto an image.
        
        Args:
            image: Base PIL Image to render onto
            impact_text: ImpactText model with text and style settings
            
        Returns:
            New PIL Image with impact text rendered
        """
        # Create a copy to avoid modifying the original
        result = image.copy().convert("RGBA")
        width, height = result.size
        
        # Calculate font size based on image height and size setting
        size_multiplier = IMPACT_TEXT_SIZE_MULTIPLIERS.get(
            impact_text.size, 
            IMPACT_TEXT_SIZE_MULTIPLIERS[ImpactTextSize.MEDIUM]
        )
        font_size = int(height * size_multiplier)
        font = self._get_font(font_size, bold=True)
        
        # Calculate position
        x = int(impact_text.position[0] * width)
        y = int(impact_text.position[1] * height)
        
        # Create text layer for compositing
        text_layer = Image.new("RGBA", result.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        
        # Get text bounding box for centering
        bbox = draw.textbbox((0, 0), impact_text.text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text around the position
        text_x = x - text_width // 2
        text_y = y - text_height // 2
        
        # Apply style-specific rendering
        text_color = self._hex_to_rgba(impact_text.color)
        outline_color = self._hex_to_rgba(impact_text.outline_color)
        
        # Apply rotation if needed
        if impact_text.rotation != 0:
            text_layer = self._render_rotated_text(
                text_layer,
                impact_text.text,
                font,
                (text_x, text_y),
                text_color,
                outline_color,
                impact_text.rotation,
                impact_text.style
            )
        else:
            # Render outline first (multiple passes for thickness)
            outline_thickness = max(2, font_size // 15)
            for ox in range(-outline_thickness, outline_thickness + 1):
                for oy in range(-outline_thickness, outline_thickness + 1):
                    if ox * ox + oy * oy <= outline_thickness * outline_thickness:
                        draw.text(
                            (text_x + ox, text_y + oy),
                            impact_text.text,
                            font=font,
                            fill=outline_color
                        )
            
            # Render main text
            draw.text((text_x, text_y), impact_text.text, font=font, fill=text_color)
            
            # Apply style effects
            text_layer = self._apply_text_style(
                text_layer, 
                impact_text.style,
                (text_x, text_y, text_x + text_width, text_y + text_height)
            )
        
        # Composite onto result
        result = Image.alpha_composite(result, text_layer)
        
        return result
    
    def _render_rotated_text(
        self,
        layer: Image.Image,
        text: str,
        font: ImageFont.FreeTypeFont,
        position: Tuple[int, int],
        text_color: Tuple[int, int, int, int],
        outline_color: Tuple[int, int, int, int],
        rotation: int,
        style: ImpactTextStyle
    ) -> Image.Image:
        """Render text with rotation."""
        # Create a temporary larger canvas for rotation
        temp_size = max(layer.size) * 2
        temp_layer = Image.new("RGBA", (temp_size, temp_size), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_layer)
        
        # Draw text in center of temp layer
        center_x = temp_size // 2
        center_y = temp_size // 2
        
        # Draw outline
        outline_thickness = max(2, font.size // 15) if hasattr(font, 'size') else 2
        for ox in range(-outline_thickness, outline_thickness + 1):
            for oy in range(-outline_thickness, outline_thickness + 1):
                if ox * ox + oy * oy <= outline_thickness * outline_thickness:
                    temp_draw.text(
                        (center_x + ox, center_y + oy),
                        text,
                        font=font,
                        fill=outline_color
                    )
        
        # Draw main text
        temp_draw.text((center_x, center_y), text, font=font, fill=text_color)
        
        # Rotate
        rotated = temp_layer.rotate(-rotation, resample=Image.BICUBIC, expand=False)
        
        # Paste back onto original layer at correct position
        paste_x = position[0] - temp_size // 2 + layer.size[0] // 2
        paste_y = position[1] - temp_size // 2 + layer.size[1] // 2
        
        layer.paste(rotated, (paste_x, paste_y), rotated)
        
        return layer
    
    def _apply_text_style(
        self,
        layer: Image.Image,
        style: ImpactTextStyle,
        bbox: Tuple[int, int, int, int]
    ) -> Image.Image:
        """Apply style-specific effects to text layer."""
        if style == ImpactTextStyle.SHAKY:
            # Add slight random offset to simulate shakiness
            # In animation, this would be done per-frame
            pass
        elif style == ImpactTextStyle.EXPLOSIVE:
            # Add glow effect
            glow = layer.filter(ImageFilter.GaussianBlur(3))
            enhancer = ImageEnhance.Brightness(glow)
            glow = enhancer.enhance(1.5)
            # Composite glow behind text
            result = Image.new("RGBA", layer.size, (0, 0, 0, 0))
            result = Image.alpha_composite(result, glow)
            result = Image.alpha_composite(result, layer)
            return result
        
        return layer
    
    # ========================================================================
    # Screen Effects (1.5.4, 1.5.5)
    # ========================================================================
    
    def render_screen_flash(
        self,
        image: Image.Image,
        effect: ScreenEffect
    ) -> Image.Image:
        """
        Render a screen flash effect onto an image.
        
        Args:
            image: Base PIL Image
            effect: ScreenEffect with type=FLASH
            
        Returns:
            New PIL Image with flash overlay
        """
        result = image.copy().convert("RGBA")
        width, height = result.size
        
        # Determine flash color (default white, or custom color)
        flash_color = effect.color if effect.color else "#FFFFFF"
        rgba = self._hex_to_rgba(flash_color)
        
        # Adjust alpha based on intensity
        opacity = FLASH_OPACITY.get(effect.intensity, FLASH_OPACITY[EffectIntensity.MEDIUM])
        flash_alpha = int(255 * opacity)
        
        # Create flash overlay
        flash_layer = Image.new("RGBA", (width, height), (*rgba[:3], flash_alpha))
        
        # Composite
        result = Image.alpha_composite(result, flash_layer)
        
        return result
    
    def render_screen_shake(
        self,
        image: Image.Image,
        effect: ScreenEffect,
        frame_index: int = 0
    ) -> Image.Image:
        """
        Render a screen shake effect by offsetting the image.
        
        For video, call this with different frame_index values to create
        the shake animation.
        
        Args:
            image: Base PIL Image
            effect: ScreenEffect with type=SHAKE
            frame_index: Current frame index for animation
            
        Returns:
            New PIL Image with shake offset applied
        """
        result = image.copy().convert("RGBA")
        width, height = result.size
        
        # Get shake intensity
        max_offset = SHAKE_OFFSETS.get(
            effect.intensity, 
            SHAKE_OFFSETS[EffectIntensity.MEDIUM]
        )
        
        # Calculate offset based on frame index (sinusoidal shake)
        # This creates a smooth back-and-forth motion
        angle = frame_index * 0.5  # Speed of shake
        offset_x = int(max_offset * math.sin(angle * 2.3))  # Different frequencies
        offset_y = int(max_offset * math.sin(angle * 1.7))  # for x and y
        
        # Create new image with offset
        shaken = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        
        # Calculate paste position (with boundary handling)
        paste_x = max(-width, min(width, offset_x))
        paste_y = max(-height, min(height, offset_y))
        
        shaken.paste(result, (paste_x, paste_y))
        
        return shaken
    
    def render_vignette(
        self,
        image: Image.Image,
        effect: ScreenEffect
    ) -> Image.Image:
        """
        Render a vignette effect (dark edges) onto an image.
        
        Args:
            image: Base PIL Image
            effect: ScreenEffect with type=VIGNETTE
            
        Returns:
            New PIL Image with vignette overlay
        """
        result = image.copy().convert("RGBA")
        width, height = result.size
        
        # Create vignette gradient
        vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vignette)
        
        # Get intensity
        intensity = INTENSITY_MULTIPLIERS.get(
            effect.intensity,
            INTENSITY_MULTIPLIERS[EffectIntensity.MEDIUM]
        )
        
        # Draw radial gradient (elliptical)
        center_x, center_y = width // 2, height // 2
        max_radius = math.sqrt(center_x**2 + center_y**2)
        
        # Create gradient using multiple ellipses
        steps = 50
        for i in range(steps):
            ratio = i / steps
            # Vignette starts from edges (high alpha) to center (low alpha)
            alpha = int(200 * intensity * (ratio ** 2))  # Quadratic falloff
            
            # Calculate ellipse size (shrinking toward center)
            radius_ratio = 1.0 - ratio * 0.5
            rx = int(center_x * radius_ratio)
            ry = int(center_y * radius_ratio)
            
            draw.ellipse(
                [center_x - rx, center_y - ry, center_x + rx, center_y + ry],
                fill=(0, 0, 0, alpha)
            )
        
        # Composite
        result = Image.alpha_composite(result, vignette)
        
        return result
    
    # ========================================================================
    # Motion Effects (1.5.6)
    # ========================================================================
    
    def render_motion_lines(
        self,
        image: Image.Image,
        effect: MotionEffect
    ) -> Image.Image:
        """
        Render speed/motion lines onto an image.
        
        Args:
            image: Base PIL Image
            effect: MotionEffect model
            
        Returns:
            New PIL Image with motion lines overlay
        """
        result = image.copy().convert("RGBA")
        width, height = result.size
        
        # Create lines layer
        lines_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(lines_layer)
        
        # Get intensity and opacity
        intensity = INTENSITY_MULTIPLIERS.get(
            effect.intensity,
            INTENSITY_MULTIPLIERS[EffectIntensity.MEDIUM]
        )
        line_alpha = int(255 * effect.opacity * intensity)
        
        # Determine line color
        line_color = self._hex_to_rgba(effect.color) if effect.color else (255, 255, 255, line_alpha)
        line_color = (*line_color[:3], line_alpha)
        
        # Number of lines based on intensity
        num_lines = int(20 + 40 * intensity)
        
        if effect.type == MotionEffectType.SPEED_LINES:
            self._draw_speed_lines(draw, width, height, num_lines, effect.direction, line_color)
        elif effect.type == MotionEffectType.ZOOM_LINES:
            self._draw_zoom_lines(draw, width, height, num_lines, line_color)
        elif effect.type == MotionEffectType.IMPACT_BURST:
            self._draw_impact_burst(draw, width, height, num_lines, line_color)
        
        # Composite
        result = Image.alpha_composite(result, lines_layer)
        
        return result
    
    def _draw_speed_lines(
        self,
        draw: ImageDraw.Draw,
        width: int,
        height: int,
        num_lines: int,
        direction: MotionDirection,
        color: Tuple[int, int, int, int]
    ):
        """Draw horizontal/vertical speed lines."""
        for _ in range(num_lines):
            # Random line parameters
            line_width = random.randint(1, 3)
            
            if direction in [MotionDirection.LEFT, MotionDirection.RIGHT]:
                # Horizontal lines
                y = random.randint(0, height)
                x_start = random.randint(0, width // 3)
                x_end = x_start + random.randint(width // 4, width // 2)
                draw.line([(x_start, y), (x_end, y)], fill=color, width=line_width)
            else:
                # Vertical lines
                x = random.randint(0, width)
                y_start = random.randint(0, height // 3)
                y_end = y_start + random.randint(height // 4, height // 2)
                draw.line([(x, y_start), (x, y_end)], fill=color, width=line_width)
    
    def _draw_zoom_lines(
        self,
        draw: ImageDraw.Draw,
        width: int,
        height: int,
        num_lines: int,
        color: Tuple[int, int, int, int]
    ):
        """Draw converging zoom lines toward center."""
        center_x, center_y = width // 2, height // 2
        
        for _ in range(num_lines):
            # Random angle
            angle = random.uniform(0, 2 * math.pi)
            
            # Line from edge toward center (but not reaching center)
            edge_dist = max(width, height)
            start_x = center_x + int(edge_dist * math.cos(angle))
            start_y = center_y + int(edge_dist * math.sin(angle))
            
            # End point closer to center
            end_ratio = random.uniform(0.3, 0.6)
            end_x = center_x + int(edge_dist * end_ratio * math.cos(angle))
            end_y = center_y + int(edge_dist * end_ratio * math.sin(angle))
            
            line_width = random.randint(1, 3)
            draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=line_width)
    
    def _draw_impact_burst(
        self,
        draw: ImageDraw.Draw,
        width: int,
        height: int,
        num_lines: int,
        color: Tuple[int, int, int, int]
    ):
        """Draw radial impact burst lines from center."""
        center_x, center_y = width // 2, height // 2
        
        for _ in range(num_lines):
            # Random angle
            angle = random.uniform(0, 2 * math.pi)
            
            # Line starting from center going outward
            start_dist = random.randint(20, 50)
            start_x = center_x + int(start_dist * math.cos(angle))
            start_y = center_y + int(start_dist * math.sin(angle))
            
            end_dist = start_dist + random.randint(50, 150)
            end_x = center_x + int(end_dist * math.cos(angle))
            end_y = center_y + int(end_dist * math.sin(angle))
            
            line_width = random.randint(2, 5)
            draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=line_width)
    
    # ========================================================================
    # Composite Function (1.5.7)
    # ========================================================================
    
    def composite_sfx_on_frame(
        self,
        image: Image.Image,
        sfx_bundle: SFXBundle,
        frame_index: int = 0
    ) -> Image.Image:
        """
        Composite all SFX effects from a bundle onto an image.
        
        This is the main entry point for applying SFX to a frame.
        
        Args:
            image: Base PIL Image (panel or video frame)
            sfx_bundle: SFXBundle containing all effects to apply
            frame_index: Current frame index for animated effects
            
        Returns:
            New PIL Image with all SFX applied
        """
        result = image.copy().convert("RGBA")
        
        # Apply screen effects first (background layer)
        for screen_effect in sfx_bundle.screen_effects:
            if screen_effect.type == ScreenEffectType.FLASH:
                result = self.render_screen_flash(result, screen_effect)
            elif screen_effect.type == ScreenEffectType.SHAKE:
                result = self.render_screen_shake(result, screen_effect, frame_index)
            elif screen_effect.type == ScreenEffectType.VIGNETTE:
                result = self.render_vignette(result, screen_effect)
            elif screen_effect.type == ScreenEffectType.DARKEN:
                result = self._apply_darken(result, screen_effect)
        
        # Apply motion effects
        for motion_effect in sfx_bundle.motion_effects:
            if motion_effect.type in [
                MotionEffectType.SPEED_LINES,
                MotionEffectType.ZOOM_LINES,
                MotionEffectType.IMPACT_BURST
            ]:
                result = self.render_motion_lines(result, motion_effect)
        
        # Apply emotional effects (placeholder - would need sprite assets)
        for emotional_effect in sfx_bundle.emotional_effects:
            result = self._render_emotional_effect(result, emotional_effect)
        
        # Apply impact text last (foreground layer)
        for impact_text in sfx_bundle.impact_texts:
            result = self.render_impact_text(result, impact_text)
        
        return result
    
    def _apply_darken(
        self,
        image: Image.Image,
        effect: ScreenEffect
    ) -> Image.Image:
        """Apply darkening effect to image."""
        intensity = INTENSITY_MULTIPLIERS.get(
            effect.intensity,
            INTENSITY_MULTIPLIERS[EffectIntensity.MEDIUM]
        )
        
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(1.0 - intensity * 0.5)
    
    def _render_emotional_effect(
        self,
        image: Image.Image,
        effect: EmotionalEffect
    ) -> Image.Image:
        """
        Render emotional effects (sparkles, hearts, etc.).
        
        Note: Full implementation would load sprite assets from sfx_assets_dir.
        This is a simplified version that draws basic shapes.
        """
        result = image.copy().convert("RGBA")
        width, height = result.size
        
        # Create effect layer
        effect_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(effect_layer)
        
        intensity = INTENSITY_MULTIPLIERS.get(
            effect.intensity,
            INTENSITY_MULTIPLIERS[EffectIntensity.MEDIUM]
        )
        
        num_particles = int(5 + 15 * intensity)
        
        # Determine effect area based on position
        if effect.position == EmotionalEffectPosition.AROUND_CHARACTER:
            area = (width // 4, height // 4, width * 3 // 4, height * 3 // 4)
        elif effect.position == EmotionalEffectPosition.FACE:
            area = (width // 3, height // 6, width * 2 // 3, height // 2)
        elif effect.position == EmotionalEffectPosition.CORNER:
            area = (width * 3 // 4, 0, width, height // 4)
        else:  # BACKGROUND or OVERLAY
            area = (0, 0, width, height)
        
        if effect.type == EmotionalEffectType.SPARKLES:
            self._draw_sparkles(draw, area, num_particles)
        elif effect.type == EmotionalEffectType.HEARTS:
            self._draw_hearts(draw, area, num_particles)
        elif effect.type == EmotionalEffectType.SWEAT_DROP:
            self._draw_sweat_drop(draw, area)
        elif effect.type == EmotionalEffectType.DARK_AURA:
            effect_layer = self._draw_dark_aura(effect_layer, area, intensity)
        
        # Composite
        result = Image.alpha_composite(result, effect_layer)
        
        return result
    
    def _draw_sparkles(
        self,
        draw: ImageDraw.Draw,
        area: Tuple[int, int, int, int],
        count: int
    ):
        """Draw sparkle particles in the given area."""
        for _ in range(count):
            x = random.randint(area[0], area[2])
            y = random.randint(area[1], area[3])
            size = random.randint(3, 8)
            
            # Draw 4-pointed star
            color = (255, 255, 200, random.randint(150, 255))
            draw.line([(x - size, y), (x + size, y)], fill=color, width=2)
            draw.line([(x, y - size), (x, y + size)], fill=color, width=2)
    
    def _draw_hearts(
        self,
        draw: ImageDraw.Draw,
        area: Tuple[int, int, int, int],
        count: int
    ):
        """Draw heart shapes in the given area."""
        for _ in range(count):
            x = random.randint(area[0], area[2])
            y = random.randint(area[1], area[3])
            size = random.randint(8, 15)
            
            color = (255, 100, 150, random.randint(150, 230))
            # Simple heart approximation using circles and triangle
            draw.ellipse([x - size, y - size//2, x, y + size//2], fill=color)
            draw.ellipse([x, y - size//2, x + size, y + size//2], fill=color)
            draw.polygon([(x - size, y), (x + size, y), (x, y + size)], fill=color)
    
    def _draw_sweat_drop(
        self,
        draw: ImageDraw.Draw,
        area: Tuple[int, int, int, int]
    ):
        """Draw a sweat drop near edge of area."""
        x = area[2] - 20
        y = area[1] + 30
        
        # Draw teardrop shape
        color = (200, 220, 255, 200)
        draw.ellipse([x - 8, y, x + 8, y + 20], fill=color)
        draw.polygon([(x - 6, y + 2), (x + 6, y + 2), (x, y - 15)], fill=color)
    
    def _draw_dark_aura(
        self,
        layer: Image.Image,
        area: Tuple[int, int, int, int],
        intensity: float
    ) -> Image.Image:
        """Draw dark aura effect."""
        draw = ImageDraw.Draw(layer)
        
        # Draw dark wisps/smoke
        num_wisps = int(10 + 20 * intensity)
        for _ in range(num_wisps):
            x = random.randint(area[0], area[2])
            y = random.randint(area[1], area[3])
            
            # Dark purple/black color
            alpha = int(50 + 100 * intensity * random.random())
            color = (30, 0, 50, alpha)
            
            # Draw elliptical wisp
            size_x = random.randint(20, 60)
            size_y = random.randint(30, 80)
            draw.ellipse([x, y, x + size_x, y + size_y], fill=color)
        
        return layer
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def _hex_to_rgba(
        self,
        hex_color: str,
        alpha: int = 255
    ) -> Tuple[int, int, int, int]:
        """Convert hex color string to RGBA tuple."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b, alpha)
        elif len(hex_color) == 8:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            a = int(hex_color[6:8], 16)
            return (r, g, b, a)
        else:
            return (255, 255, 255, alpha)


# ============================================================================
# Convenience Functions
# ============================================================================

def create_sfx_renderer(font_path: Optional[str] = None) -> SFXRenderer:
    """
    Factory function to create an SFX renderer.
    
    Args:
        font_path: Optional custom font path
        
    Returns:
        SFXRenderer instance
    """
    return SFXRenderer(font_path=font_path)
