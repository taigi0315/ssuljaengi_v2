"""
Test script for VideoService.

Run: python -m tests.test_video_service
"""
import os
import sys
import asyncio

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.video_service import VideoService
from app.models.video_models import BubbleData, VideoPanelData, VideoConfig


def test_render_bubble():
    """Test single bubble rendering."""
    print("\n=== Test: Render Bubble ===")
    
    service = VideoService()
    
    # Create a test image (solid color)
    from PIL import Image
    test_img = Image.new("RGBA", (1080, 1350), color=(100, 150, 200, 255))
    
    # Render bubble
    result = service.render_bubble(
        test_img, 
        "Hello, this is a test bubble!", 
        50.0,  # center X
        30.0   # 30% from top
    )
    
    # Save for visual inspection
    output_path = os.path.join(os.path.dirname(__file__), "test_bubble_output.png")
    result.save(output_path)
    print(f"✅ Bubble rendered and saved to: {output_path}")
    
    return result


def test_crop_to_cover():
    """Test image cropping to cover target dimensions."""
    print("\n=== Test: Crop to Cover ===")
    
    service = VideoService()
    
    # Create a test image (1:1 square, larger than target)
    from PIL import Image, ImageDraw
    test_img = Image.new("RGBA", (1500, 1500), color=(50, 100, 150, 255))
    draw = ImageDraw.Draw(test_img)
    
    # Draw a cross to visualize center
    draw.line([(750, 0), (750, 1500)], fill="red", width=5)
    draw.line([(0, 750), (1500, 750)], fill="red", width=5)
    draw.ellipse([(700, 700), (800, 800)], fill="yellow")
    
    # Crop
    result = service.crop_to_cover(test_img)
    
    print(f"  Input: {test_img.size}")
    print(f"  Output: {result.size}")
    print(f"  Expected: ({service.config.width}, {service.config.height})")
    
    assert result.size == (service.config.width, service.config.height), "Size mismatch!"
    
    output_path = os.path.join(os.path.dirname(__file__), "test_crop_output.png")
    result.save(output_path)
    print(f"✅ Crop successful, saved to: {output_path}")
    
    return result


def test_generate_frame():
    """Test frame generation with bubbles."""
    print("\n=== Test: Generate Frame ===")
    
    service = VideoService()
    
    # Create a test image file
    from PIL import Image
    test_img = Image.new("RGBA", (1500, 1500), color=(80, 120, 180, 255))
    test_path = os.path.join(os.path.dirname(__file__), "test_input.png")
    test_img.save(test_path)
    
    # Generate frame
    bubbles = [
        BubbleData(text="First bubble at top", x=50.0, y=20.0),
        BubbleData(text="Second bubble at center", x=50.0, y=50.0),
    ]
    
    result = service.generate_frame(test_path, bubbles)
    
    output_path = os.path.join(os.path.dirname(__file__), "test_frame_output.png")
    result.save(output_path)
    print(f"✅ Frame generated, saved to: {output_path}")
    
    # Cleanup
    os.remove(test_path)
    
    return result


def test_generate_video():
    """Test full video generation."""
    print("\n=== Test: Generate Video ===")
    
    service = VideoService(VideoConfig(
        base_duration_ms=1000,  # Shorter for test
        bubble_duration_ms=1000,
        final_pause_ms=500,
    ))
    
    # Create test images
    from PIL import Image, ImageDraw
    test_dir = os.path.dirname(__file__)
    
    panels = []
    for i in range(2):  # 2 panels for quick test
        img = Image.new("RGBA", (1500, 1500), color=(50 + i*50, 100, 150, 255))
        draw = ImageDraw.Draw(img)
        draw.text((750, 750), f"Panel {i+1}", fill="white", anchor="mm")
        
        img_path = os.path.join(test_dir, f"test_panel_{i+1}.png")
        img.save(img_path)
        
        panels.append(VideoPanelData(
            panel_number=i+1,
            image_url=img_path,
            bubbles=[
                BubbleData(text=f"Bubble for panel {i+1}", x=50.0, y=30.0)
            ]
        ))
    
    # Generate video
    output_path = os.path.join(test_dir, "test_video_output.mp4")
    result_path = service.generate_video(panels, output_path)
    
    # Check file exists and has size
    assert os.path.exists(result_path), "Video file not created!"
    file_size = os.path.getsize(result_path)
    print(f"✅ Video generated: {result_path} ({file_size / 1024:.1f} KB)")
    
    # Cleanup test images
    for i in range(2):
        img_path = os.path.join(test_dir, f"test_panel_{i+1}.png")
        if os.path.exists(img_path):
            os.remove(img_path)
    
    return result_path


if __name__ == "__main__":
    print("=" * 50)
    print("VideoService Test Suite")
    print("=" * 50)
    
    try:
        test_crop_to_cover()
        test_render_bubble()
        test_generate_frame()
        test_generate_video()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
