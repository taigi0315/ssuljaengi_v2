#!/usr/bin/env python
"""
Quick test script for VideoService.
Run: cd backend && python test_video_quick.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.services.video_service import VideoService
from app.models.video_models import BubbleData, VideoPanelData, VideoConfig


def main():
    print("=" * 50)
    print("Quick VideoService Test")
    print("=" * 50)
    
    # Use shorter durations for quick test
    config = VideoConfig(
        base_duration_ms=500,
        bubble_duration_ms=500,
        final_pause_ms=200,
    )
    
    service = VideoService(config)
    
    # Create test images using Pillow
    from PIL import Image, ImageDraw
    
    test_dir = os.path.join(os.path.dirname(__file__), 'cache', 'images')
    os.makedirs(test_dir, exist_ok=True)
    
    panels = []
    for i in range(2):  # 2 panels for quick test
        # Create a test image (1:1 square like Gemini generates)
        img = Image.new("RGBA", (1024, 1024), color=(50 + i*50, 100, 150, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw some content to make it identifiable
        draw.rectangle([(200, 200), (824, 824)], outline="white", width=5)
        draw.text((512, 512), f"Panel {i+1}", fill="white", anchor="mm")
        
        img_path = os.path.join(test_dir, f"test_panel_{i+1}.png")
        img.save(img_path)
        print(f"Created test image: {img_path}")
        
        panels.append(VideoPanelData(
            panel_number=i+1,
            image_url=img_path,
            bubbles=[
                BubbleData(text=f"Hello from panel {i+1}!", x=50.0, y=25.0)
            ]
        ))
    
    # Generate video
    print("\nGenerating video...")
    output_path = os.path.join(test_dir, "test_output.mp4")
    
    try:
        result_path = service.generate_video(panels, output_path)
        file_size = os.path.getsize(result_path)
        print(f"\n✅ SUCCESS! Video generated: {result_path}")
        print(f"   File size: {file_size / 1024:.1f} KB")
        print(f"\nOpen with: open '{result_path}'")
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Cleanup test images
    for i in range(2):
        img_path = os.path.join(test_dir, f"test_panel_{i+1}.png")
        if os.path.exists(img_path):
            os.remove(img_path)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
