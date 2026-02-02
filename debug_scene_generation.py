#!/usr/bin/env python3
"""
Debug the scene generation process.
"""

import sys
import os
import asyncio

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.webtoon_writer import webtoon_writer

async def debug_scene_generation():
    """Debug the scene generation process."""
    
    story = "A girl meets a boy. They talk and become friends."
    story_genre = "MODERN_ROMANCE_DRAMA"
    image_style = "BRIGHT_YOUTHFUL_WEBTOON"
    
    print("Testing webtoon writer directly...")
    
    try:
        script = await webtoon_writer.convert_story_to_script(story, story_genre, image_style)
        
        print(f"✓ Script generated successfully")
        print(f"  Characters: {len(script.characters)}")
        print(f"  Scenes: {len(script.scenes)}")
        print(f"  Total panels (from scenes): {len(script.panels)}")
        
        # Show scene structure
        for i, scene in enumerate(script.scenes[:2]):  # Show first 2 scenes
            print(f"  Scene {i+1}: {scene.scene_title}")
            print(f"    Type: {scene.scene_type}")
            print(f"    Panels: {len(scene.panels)}")
            for j, panel in enumerate(scene.panels):
                print(f"      Panel {j+1}: {panel.visual_prompt[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_scene_generation())
    if success:
        print("\n✓ Scene generation debug completed!")
    else:
        print("\n✗ Scene generation debug failed!")