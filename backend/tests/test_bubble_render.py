import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
from app.services.video_service import video_service
from app.models.video_models import BubbleData, VideoPanelData

async def test_bubble_render():
    print("Starting Bubble Render Test...")
    
    # 1. Create a dummy image (1024x1024 red square)
    img_path = "test_input.png"
    img = Image.new('RGBA', (1024, 1024), (255, 0, 0, 255))
    img.save(img_path)
    
    # 2. Define Bubble with Korean Text
    bubbles = [
        BubbleData(
            text="테스트: 안녕하세요 (Hello)",
            x=50, # Center
            y=20, # Top part
            character_name="테스트캐릭터" # Korean Name
        )
    ]
    
    # 3. Generate Frame
    try:
        # Note: generate_frame is synchronous
        print("Rendering frame...")
        result_img = video_service.generate_frame(img_path, bubbles)
        
        output_path = "test_output.png"
        result_img.save(output_path)
        print(f"Successfully saved {output_path}")
        print(f"Output size: {result_img.size}")
        
        # Verify 9:16 aspect ratio (1080x1920)
        assert result_img.size == (1080, 1920), f"Expected (1080, 1920), got {result_img.size}"
        print("✅ Aspect Ratio Correct")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if os.path.exists(img_path):
            os.remove(img_path)

if __name__ == "__main__":
    asyncio.run(test_bubble_render())
