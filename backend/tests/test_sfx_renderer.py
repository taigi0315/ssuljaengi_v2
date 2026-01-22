"""
Unit tests for SFX Renderer service.

Tests the SFX rendering functionality including impact text, screen effects,
motion effects, and the composite function.
"""

import pytest
from PIL import Image
from unittest.mock import patch, MagicMock

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
    SFXTiming,
)
from app.services.sfx_renderer import (
    SFXRenderer,
    create_sfx_renderer,
    IMPACT_TEXT_SIZE_MULTIPLIERS,
    INTENSITY_MULTIPLIERS,
    SHAKE_OFFSETS,
    FLASH_OPACITY,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    with patch('app.services.sfx_renderer.get_settings') as mock:
        settings = MagicMock()
        settings.sfx_font_path = None
        settings.sfx_assets_dir = "assets/sfx"
        settings.sfx_default_text_color = "#FFFFFF"
        settings.sfx_default_outline_color = "#000000"
        mock.return_value = settings
        yield settings


@pytest.fixture
def renderer(mock_settings):
    """Create SFX renderer instance."""
    return SFXRenderer()


@pytest.fixture
def test_image():
    """Create a test image for rendering."""
    # Create a simple 200x300 test image (9:16 aspect ratio scaled down)
    img = Image.new("RGB", (200, 300), color=(100, 100, 100))
    return img


@pytest.fixture
def small_image():
    """Create a small test image."""
    return Image.new("RGB", (100, 100), color=(50, 50, 50))


# ============================================================================
# Test Constants
# ============================================================================

class TestConstants:
    """Test that constants are properly defined."""
    
    def test_impact_text_size_multipliers(self):
        """Test size multipliers are defined for all sizes."""
        assert ImpactTextSize.SMALL in IMPACT_TEXT_SIZE_MULTIPLIERS
        assert ImpactTextSize.MEDIUM in IMPACT_TEXT_SIZE_MULTIPLIERS
        assert ImpactTextSize.LARGE in IMPACT_TEXT_SIZE_MULTIPLIERS
        assert ImpactTextSize.MASSIVE in IMPACT_TEXT_SIZE_MULTIPLIERS
        
        # Verify increasing order
        assert IMPACT_TEXT_SIZE_MULTIPLIERS[ImpactTextSize.SMALL] < IMPACT_TEXT_SIZE_MULTIPLIERS[ImpactTextSize.MEDIUM]
        assert IMPACT_TEXT_SIZE_MULTIPLIERS[ImpactTextSize.MEDIUM] < IMPACT_TEXT_SIZE_MULTIPLIERS[ImpactTextSize.LARGE]
        assert IMPACT_TEXT_SIZE_MULTIPLIERS[ImpactTextSize.LARGE] < IMPACT_TEXT_SIZE_MULTIPLIERS[ImpactTextSize.MASSIVE]
    
    def test_intensity_multipliers(self):
        """Test intensity multipliers are defined for all levels."""
        assert EffectIntensity.SUBTLE in INTENSITY_MULTIPLIERS
        assert EffectIntensity.MEDIUM in INTENSITY_MULTIPLIERS
        assert EffectIntensity.INTENSE in INTENSITY_MULTIPLIERS
        
        # Verify increasing order
        assert INTENSITY_MULTIPLIERS[EffectIntensity.SUBTLE] < INTENSITY_MULTIPLIERS[EffectIntensity.MEDIUM]
        assert INTENSITY_MULTIPLIERS[EffectIntensity.MEDIUM] < INTENSITY_MULTIPLIERS[EffectIntensity.INTENSE]
    
    def test_shake_offsets(self):
        """Test shake offsets are defined."""
        assert EffectIntensity.SUBTLE in SHAKE_OFFSETS
        assert EffectIntensity.MEDIUM in SHAKE_OFFSETS
        assert EffectIntensity.INTENSE in SHAKE_OFFSETS
    
    def test_flash_opacity(self):
        """Test flash opacity values are defined."""
        assert EffectIntensity.SUBTLE in FLASH_OPACITY
        assert EffectIntensity.MEDIUM in FLASH_OPACITY
        assert EffectIntensity.INTENSE in FLASH_OPACITY
        
        # All values should be between 0 and 1
        for value in FLASH_OPACITY.values():
            assert 0.0 <= value <= 1.0


# ============================================================================
# Test SFXRenderer Initialization
# ============================================================================

class TestSFXRendererInit:
    """Test SFXRenderer initialization."""
    
    def test_init_default(self, mock_settings):
        """Test default initialization."""
        renderer = SFXRenderer()
        assert renderer._settings is not None
        assert renderer._font_cache == {}
    
    def test_init_with_font_path(self, mock_settings):
        """Test initialization with custom font path."""
        renderer = SFXRenderer(font_path="/custom/font.ttf")
        assert renderer._font_path == "/custom/font.ttf"
    
    def test_factory_function(self, mock_settings):
        """Test create_sfx_renderer factory function."""
        renderer = create_sfx_renderer()
        assert isinstance(renderer, SFXRenderer)
        
        renderer_with_font = create_sfx_renderer(font_path="/custom/font.ttf")
        assert renderer_with_font._font_path == "/custom/font.ttf"


# ============================================================================
# Test Impact Text Rendering
# ============================================================================

class TestRenderImpactText:
    """Test impact text rendering."""
    
    def test_basic_impact_text(self, renderer, test_image):
        """Test rendering basic impact text."""
        impact = ImpactText(
            text="CRASH!",
            style=ImpactTextStyle.BOLD,
            position=(0.5, 0.5),
            size=ImpactTextSize.MEDIUM
        )
        
        result = renderer.render_impact_text(test_image, impact)
        
        assert result is not None
        assert isinstance(result, Image.Image)
        assert result.size == test_image.size
        assert result.mode == "RGBA"
    
    def test_impact_text_with_rotation(self, renderer, test_image):
        """Test rendering impact text with rotation."""
        impact = ImpactText(
            text="POW!",
            rotation=-15,
            position=(0.7, 0.3)
        )
        
        result = renderer.render_impact_text(test_image, impact)
        
        assert result is not None
        assert result.size == test_image.size
    
    def test_impact_text_all_sizes(self, renderer, test_image):
        """Test all impact text sizes render correctly."""
        for size in ImpactTextSize:
            impact = ImpactText(
                text="TEST",
                size=size,
                position=(0.5, 0.5)
            )
            
            result = renderer.render_impact_text(test_image, impact)
            assert result is not None
    
    def test_impact_text_all_styles(self, renderer, test_image):
        """Test all impact text styles render correctly."""
        for style in ImpactTextStyle:
            impact = ImpactText(
                text="TEST",
                style=style,
                position=(0.5, 0.5)
            )
            
            result = renderer.render_impact_text(test_image, impact)
            assert result is not None
    
    def test_impact_text_custom_colors(self, renderer, test_image):
        """Test impact text with custom colors."""
        impact = ImpactText(
            text="BOOM!",
            color="#FF0000",
            outline_color="#FFFF00",
            position=(0.5, 0.5)
        )
        
        result = renderer.render_impact_text(test_image, impact)
        assert result is not None


# ============================================================================
# Test Screen Effects
# ============================================================================

class TestScreenEffects:
    """Test screen effect rendering."""
    
    def test_render_screen_flash(self, renderer, test_image):
        """Test screen flash effect."""
        effect = ScreenEffect(
            type=ScreenEffectType.FLASH,
            intensity=EffectIntensity.MEDIUM,
            duration_ms=200
        )
        
        result = renderer.render_screen_flash(test_image, effect)
        
        assert result is not None
        assert result.size == test_image.size
    
    def test_render_screen_flash_all_intensities(self, renderer, test_image):
        """Test flash effect at all intensities."""
        for intensity in EffectIntensity:
            effect = ScreenEffect(
                type=ScreenEffectType.FLASH,
                intensity=intensity
            )
            
            result = renderer.render_screen_flash(test_image, effect)
            assert result is not None
    
    def test_render_screen_flash_custom_color(self, renderer, test_image):
        """Test flash effect with custom color."""
        effect = ScreenEffect(
            type=ScreenEffectType.FLASH,
            intensity=EffectIntensity.MEDIUM,
            color="#FF0000"
        )
        
        result = renderer.render_screen_flash(test_image, effect)
        assert result is not None
    
    def test_render_screen_shake(self, renderer, test_image):
        """Test screen shake effect."""
        effect = ScreenEffect(
            type=ScreenEffectType.SHAKE,
            intensity=EffectIntensity.MEDIUM
        )
        
        # Test multiple frames to verify animation
        for frame in range(5):
            result = renderer.render_screen_shake(test_image, effect, frame_index=frame)
            assert result is not None
            assert result.size == test_image.size
    
    def test_render_screen_shake_all_intensities(self, renderer, test_image):
        """Test shake effect at all intensities."""
        for intensity in EffectIntensity:
            effect = ScreenEffect(
                type=ScreenEffectType.SHAKE,
                intensity=intensity
            )
            
            result = renderer.render_screen_shake(test_image, effect)
            assert result is not None
    
    def test_render_vignette(self, renderer, test_image):
        """Test vignette effect."""
        effect = ScreenEffect(
            type=ScreenEffectType.VIGNETTE,
            intensity=EffectIntensity.MEDIUM
        )
        
        result = renderer.render_vignette(test_image, effect)
        
        assert result is not None
        assert result.size == test_image.size
    
    def test_render_vignette_all_intensities(self, renderer, test_image):
        """Test vignette at all intensities."""
        for intensity in EffectIntensity:
            effect = ScreenEffect(
                type=ScreenEffectType.VIGNETTE,
                intensity=intensity
            )
            
            result = renderer.render_vignette(test_image, effect)
            assert result is not None


# ============================================================================
# Test Motion Effects
# ============================================================================

class TestMotionEffects:
    """Test motion effect rendering."""
    
    def test_render_speed_lines(self, renderer, test_image):
        """Test speed lines rendering."""
        effect = MotionEffect(
            type=MotionEffectType.SPEED_LINES,
            direction=MotionDirection.LEFT,
            intensity=EffectIntensity.MEDIUM
        )
        
        result = renderer.render_motion_lines(test_image, effect)
        
        assert result is not None
        assert result.size == test_image.size
    
    def test_render_speed_lines_all_directions(self, renderer, test_image):
        """Test speed lines in all directions."""
        for direction in MotionDirection:
            effect = MotionEffect(
                type=MotionEffectType.SPEED_LINES,
                direction=direction,
                intensity=EffectIntensity.MEDIUM
            )
            
            result = renderer.render_motion_lines(test_image, effect)
            assert result is not None
    
    def test_render_zoom_lines(self, renderer, test_image):
        """Test zoom lines rendering."""
        effect = MotionEffect(
            type=MotionEffectType.ZOOM_LINES,
            direction=MotionDirection.CENTER,
            intensity=EffectIntensity.INTENSE
        )
        
        result = renderer.render_motion_lines(test_image, effect)
        
        assert result is not None
        assert result.size == test_image.size
    
    def test_render_impact_burst(self, renderer, test_image):
        """Test impact burst rendering."""
        effect = MotionEffect(
            type=MotionEffectType.IMPACT_BURST,
            direction=MotionDirection.RADIAL,
            intensity=EffectIntensity.INTENSE
        )
        
        result = renderer.render_motion_lines(test_image, effect)
        
        assert result is not None
        assert result.size == test_image.size
    
    def test_render_motion_custom_color(self, renderer, test_image):
        """Test motion lines with custom color."""
        effect = MotionEffect(
            type=MotionEffectType.SPEED_LINES,
            color="#FF0000",
            opacity=0.8
        )
        
        result = renderer.render_motion_lines(test_image, effect)
        assert result is not None


# ============================================================================
# Test Composite Function
# ============================================================================

class TestCompositeSFX:
    """Test the main composite_sfx_on_frame function."""
    
    def test_composite_empty_bundle(self, renderer, test_image):
        """Test compositing with empty bundle."""
        bundle = SFXBundle(panel_number=1)
        
        result = renderer.composite_sfx_on_frame(test_image, bundle)
        
        assert result is not None
        assert result.size == test_image.size
    
    def test_composite_with_impact_text(self, renderer, test_image):
        """Test compositing with impact text."""
        bundle = SFXBundle(
            panel_number=1,
            impact_texts=[
                ImpactText(text="CRASH!", position=(0.5, 0.3)),
                ImpactText(text="BANG!", position=(0.5, 0.7))
            ]
        )
        
        result = renderer.composite_sfx_on_frame(test_image, bundle)
        
        assert result is not None
        assert result.size == test_image.size
    
    def test_composite_with_screen_effects(self, renderer, test_image):
        """Test compositing with screen effects."""
        bundle = SFXBundle(
            panel_number=1,
            screen_effects=[
                ScreenEffect(type=ScreenEffectType.FLASH, intensity=EffectIntensity.SUBTLE),
                ScreenEffect(type=ScreenEffectType.VIGNETTE, intensity=EffectIntensity.MEDIUM)
            ]
        )
        
        result = renderer.composite_sfx_on_frame(test_image, bundle)
        
        assert result is not None
    
    def test_composite_with_motion_effects(self, renderer, test_image):
        """Test compositing with motion effects."""
        bundle = SFXBundle(
            panel_number=1,
            motion_effects=[
                MotionEffect(type=MotionEffectType.SPEED_LINES, direction=MotionDirection.LEFT),
                MotionEffect(type=MotionEffectType.IMPACT_BURST)
            ]
        )
        
        result = renderer.composite_sfx_on_frame(test_image, bundle)
        
        assert result is not None
    
    def test_composite_with_emotional_effects(self, renderer, test_image):
        """Test compositing with emotional effects."""
        bundle = SFXBundle(
            panel_number=1,
            emotional_effects=[
                EmotionalEffect(type=EmotionalEffectType.SPARKLES),
                EmotionalEffect(type=EmotionalEffectType.HEARTS)
            ]
        )
        
        result = renderer.composite_sfx_on_frame(test_image, bundle)
        
        assert result is not None
    
    def test_composite_full_bundle(self, renderer, test_image):
        """Test compositing with all effect types."""
        bundle = SFXBundle(
            panel_number=1,
            impact_texts=[
                ImpactText(text="SLAM!", style=ImpactTextStyle.EXPLOSIVE, position=(0.8, 0.2))
            ],
            motion_effects=[
                MotionEffect(type=MotionEffectType.IMPACT_BURST, intensity=EffectIntensity.INTENSE)
            ],
            screen_effects=[
                ScreenEffect(type=ScreenEffectType.SHAKE, intensity=EffectIntensity.MEDIUM)
            ],
            emotional_effects=[
                EmotionalEffect(type=EmotionalEffectType.DARK_AURA)
            ]
        )
        
        result = renderer.composite_sfx_on_frame(test_image, bundle, frame_index=0)
        
        assert result is not None
        assert result.size == test_image.size
    
    def test_composite_animation_frames(self, renderer, test_image):
        """Test compositing across multiple animation frames."""
        bundle = SFXBundle(
            panel_number=1,
            screen_effects=[
                ScreenEffect(type=ScreenEffectType.SHAKE, intensity=EffectIntensity.INTENSE)
            ]
        )
        
        # Render multiple frames
        frames = []
        for i in range(10):
            result = renderer.composite_sfx_on_frame(test_image, bundle, frame_index=i)
            frames.append(result)
        
        assert len(frames) == 10
        # All frames should be valid images
        for frame in frames:
            assert isinstance(frame, Image.Image)


# ============================================================================
# Test Utility Functions
# ============================================================================

class TestUtilityFunctions:
    """Test utility methods."""
    
    def test_hex_to_rgba_six_digit(self, renderer):
        """Test hex to RGBA conversion for 6-digit hex."""
        result = renderer._hex_to_rgba("#FF0000")
        assert result == (255, 0, 0, 255)
        
        result = renderer._hex_to_rgba("#00FF00")
        assert result == (0, 255, 0, 255)
        
        result = renderer._hex_to_rgba("#0000FF")
        assert result == (0, 0, 255, 255)
    
    def test_hex_to_rgba_eight_digit(self, renderer):
        """Test hex to RGBA conversion for 8-digit hex with alpha."""
        result = renderer._hex_to_rgba("#FF000080")
        assert result == (255, 0, 0, 128)
    
    def test_hex_to_rgba_custom_alpha(self, renderer):
        """Test hex to RGBA with custom alpha."""
        result = renderer._hex_to_rgba("#FF0000", alpha=128)
        assert result == (255, 0, 0, 128)
    
    def test_hex_to_rgba_without_hash(self, renderer):
        """Test hex to RGBA without # prefix."""
        result = renderer._hex_to_rgba("FF0000")
        assert result == (255, 0, 0, 255)
    
    def test_hex_to_rgba_invalid(self, renderer):
        """Test hex to RGBA with invalid input falls back to white."""
        result = renderer._hex_to_rgba("invalid")
        assert result == (255, 255, 255, 255)


# ============================================================================
# Test Emotional Effects
# ============================================================================

class TestEmotionalEffects:
    """Test emotional effect rendering."""
    
    def test_sparkles_effect(self, renderer, test_image):
        """Test sparkles rendering."""
        bundle = SFXBundle(
            panel_number=1,
            emotional_effects=[
                EmotionalEffect(
                    type=EmotionalEffectType.SPARKLES,
                    position=EmotionalEffectPosition.AROUND_CHARACTER,
                    intensity=EffectIntensity.MEDIUM
                )
            ]
        )
        
        result = renderer.composite_sfx_on_frame(test_image, bundle)
        assert result is not None
    
    def test_hearts_effect(self, renderer, test_image):
        """Test hearts rendering."""
        bundle = SFXBundle(
            panel_number=1,
            emotional_effects=[
                EmotionalEffect(
                    type=EmotionalEffectType.HEARTS,
                    position=EmotionalEffectPosition.BACKGROUND
                )
            ]
        )
        
        result = renderer.composite_sfx_on_frame(test_image, bundle)
        assert result is not None
    
    def test_sweat_drop_effect(self, renderer, test_image):
        """Test sweat drop rendering."""
        bundle = SFXBundle(
            panel_number=1,
            emotional_effects=[
                EmotionalEffect(
                    type=EmotionalEffectType.SWEAT_DROP,
                    position=EmotionalEffectPosition.FACE
                )
            ]
        )
        
        result = renderer.composite_sfx_on_frame(test_image, bundle)
        assert result is not None
    
    def test_dark_aura_effect(self, renderer, test_image):
        """Test dark aura rendering."""
        bundle = SFXBundle(
            panel_number=1,
            emotional_effects=[
                EmotionalEffect(
                    type=EmotionalEffectType.DARK_AURA,
                    intensity=EffectIntensity.INTENSE
                )
            ]
        )
        
        result = renderer.composite_sfx_on_frame(test_image, bundle)
        assert result is not None
    
    def test_all_emotional_positions(self, renderer, test_image):
        """Test emotional effects at all positions."""
        for position in EmotionalEffectPosition:
            bundle = SFXBundle(
                panel_number=1,
                emotional_effects=[
                    EmotionalEffect(
                        type=EmotionalEffectType.SPARKLES,
                        position=position
                    )
                ]
            )
            
            result = renderer.composite_sfx_on_frame(test_image, bundle)
            assert result is not None
