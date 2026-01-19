
import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw
from app.services.video_service import video_service
from app.models.video_models import BubbleData

async def test_bubble_render_centered():
    print("Starting Bubble Render Test (Centered)...")
    
    # 1. Create a dummy image 9:16 (1080x1920) for simulating the crop
    # Actually generate_frame handles cropping, but render_bubble renders on the PASSED image.
    # In my fixed pipeline, render_bubble receives the CROPPED image (1080x1920).
    
    w, h = 1080, 1920
    img = Image.new('RGBA', (w, h), (200, 200, 200, 255))
    
    # Draw crosshair at center (50%, 50%) = (540, 960)
    draw = ImageDraw.Draw(img)
    draw.line((0, 960, 1080, 960), fill="red", width=2)
    draw.line((540, 0, 540, 1920), fill="red", width=2)
    
    bubbles = [
        # Center Bubble
        BubbleData(
            text="Center Bubble",
            x=50, # Center
            y=50, # Center
            character_name="TestName"
        ),
        # Top Left Bubble
        BubbleData(
            text="Top Left",
            x=10, 
            y=10,
            character_name="TL"
        )
    ]
    
    print("Rendering bubbles...")
    # Directly call render_bubble to test positioning on an existing image
    res = img
    for b in bubbles:
        res = video_service.render_bubble(
            res, b.text, b.x, b.y, 
            character_name=b.character_name
        )
        
    output_path = "test_centered.png"
    res.save(output_path)
    print(f"Saved {output_path}")

if __name__ == "__main__":
    asyncio.run(test_bubble_render_centered())
