#!/usr/bin/env python
"""
Quick E2E Test Setup Script

This script creates minimal test data for end-to-end testing:
- 1 story
- 1 webtoon script with 2 panels
- 1 character with 1 image
- 2 scene images (one per panel)
- 2 dialogues per panel

Run: cd backend && python setup_test_data.py
Then: npm run dev
"""
import os
import sys
import json
import uuid
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Setup paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BACKEND_DIR, 'data')
CACHE_DIR = os.path.join(BACKEND_DIR, 'cache', 'images')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)


def create_test_image(filename: str, text: str, color: tuple, size: tuple = (1024, 1024)) -> str:
    """Create a simple test image with text."""
    img = Image.new("RGB", size, color=color)
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([(20, 20), (size[0]-20, size[1]-20)], outline="white", width=3)
    
    # Draw center cross and text
    cx, cy = size[0]//2, size[1]//2
    draw.line([(cx-50, cy), (cx+50, cy)], fill="white", width=2)
    draw.line([(cx, cy-50), (cx, cy+50)], fill="white", width=2)
    
    # Try to draw text (fallback if font not available)
    try:
        draw.text((cx, cy + 80), text, fill="white", anchor="mm")
    except:
        pass
    
    filepath = os.path.join(CACHE_DIR, filename)
    img.save(filepath, "PNG")
    return filepath


def main():
    print("=" * 60)
    print("Quick E2E Test Setup")
    print("=" * 60)
    
    # Generate IDs
    story_id = str(uuid.uuid4())
    script_id = str(uuid.uuid4())
    workflow_id = str(uuid.uuid4())
    
    print(f"\n📝 Creating test data...")
    print(f"   Story ID: {story_id[:8]}...")
    print(f"   Script ID: {script_id[:8]}...")
    
    # 1. Create test images
    print("\n🖼️ Creating test images...")
    
    # Character image
    char_img_id = str(uuid.uuid4())
    char_img_path = create_test_image(
        f"char_{char_img_id[:8]}.png",
        "Test Character",
        (80, 100, 140),
        size=(1080, 1920)
    )
    char_img_url = f"/api/assets/cache/images/{os.path.basename(char_img_path)}"
    print(f"   Character: {char_img_url}")
    
    # Scene images
    scene1_id = str(uuid.uuid4())
    scene1_path = create_test_image(
        f"scene_{scene1_id[:8]}.png",
        "Scene 1",
        (100, 80, 120),
        size=(1080, 1920)
    )
    scene1_url = f"/api/assets/cache/images/{os.path.basename(scene1_path)}"
    print(f"   Scene 1: {scene1_url}")
    
    scene2_id = str(uuid.uuid4())
    scene2_path = create_test_image(
        f"scene_{scene2_id[:8]}.png",
        "Scene 2",
        (120, 100, 80),
        size=(1080, 1920)
    )
    scene2_url = f"/api/assets/cache/images/{os.path.basename(scene2_path)}"
    print(f"   Scene 2: {scene2_url}")
    
    # 2. Create story data
    story = {
        "story_id": story_id,
        "title": "E2E Test Story",
        "summary": "A quick test story for end-to-end testing.",
        "content": "This is a test story content for E2E testing purposes.",
        "source_url": "https://test.example.com/story",
        "created_at": datetime.now().isoformat(),
    }
    
    # 3. Create workflow data
    workflow = {
        "workflow_id": workflow_id,
        "story_id": story_id,
        "status": "COMPLETED",
        "created_at": datetime.now().isoformat(),
    }
    
    # 4. Create webtoon script
    script = {
        "script_id": script_id,
        "story_id": story_id,
        "title": "E2E Test Webtoon",
        "genre": "MODERN_ROMANCE_DRAMA_MANHWA",
        "hook": "A captivating test story",
        "characters": [
            {
                "name": "TestChar",
                "reference_tag": "TestChar(20s, female, brown hair)",
                "role": "protagonist",
                "age": "25",
                "gender": "female",
                "personality": "Cheerful and brave",
                "face": "round face, bright eyes",
                "hair": "long brown hair",
                "body": "average height",
                "outfit": "casual clothes",
                "mood": "happy",
                "appearance_notes": "Round face, bright sparkling eyes. Long brown hair styled loosely. Average height with a friendly demeanor.",
                "typical_outfit": "Casual jeans and a colorful t-shirt.",
                "personality_brief": "Cheerful and brave, always looking for adventure.",
                "visual_description": "A young woman in her mid-20s with a round friendly face, bright sparkling eyes, long brown hair styled loosely, average height, wearing casual jeans and a colorful t-shirt, cheerful and brave expression."
            }
        ],
        "panels": [
            {
                "panel_number": 1,
                "shot_type": "wide",
                "active_character_names": ["TestChar"],
                "scene_description": "A sunny park with trees",
                "visual_prompt": "A sunny park scene with green trees and a walking path under clear blue sky.",
                "negative_prompt": "text, words, blurry, low quality",
                "composition_notes": "Wide establishing shot of the park",
                "environment_focus": "Sunny park",
                "environment_details": "Oak trees, green grass, stone path",
                "atmospheric_conditions": "Bright daylight, sunny weather",
                "story_beat": "The character arrives at the park.",
                "emotional_intensity": 3,
                "character_frame_percentage": 20,
                "environment_frame_percentage": 80,
                "character_placement_and_action": "TestChar stands near a large oak tree, looking around happily.",
                "dialogue": [
                    {"character": "TestChar", "text": "What a beautiful day!"},
                    {"character": "TestChar", "text": "I love this park."}
                ],
                "mood": "happy"
            },
            {
                "panel_number": 2,
                "shot_type": "medium",
                "active_character_names": ["TestChar"],
                "scene_description": "A cozy cafe interior",
                "visual_prompt": "Cozy cafe interior with warm lighting, wooden tables, and coffee equipment in the background.",
                "negative_prompt": "text, words, blurry, low quality",
                "composition_notes": "Medium shot of the character at a table",
                "environment_focus": "Cafe interior",
                "environment_details": "Wooden counter, espresso machine, warm hanging lights",
                "atmospheric_conditions": "Warm indoor lighting",
                "story_beat": "The character enjoys a cup of coffee.",
                "emotional_intensity": 4,
                "character_frame_percentage": 50,
                "environment_frame_percentage": 50,
                "character_placement_and_action": "TestChar sits at a small table, holding a coffee cup.",
                "dialogue": [
                    {"character": "TestChar", "text": "This coffee is great!"},
                    {"character": "TestChar", "text": "I should come here more often."}
                ],
                "mood": "content"
            }
        ],
        "character_images": {
            "TestChar": [
                {
                    "id": char_img_id,
                    "image_id": char_img_id,
                    "character_name": "TestChar",
                    "style": "MODERN_ROMANCE_DRAMA_MANHWA",
                    "image_url": char_img_url,
                    "is_selected": True,
                    "created_at": datetime.now().isoformat(),
                }
            ]
        },
        "scene_images": {
            "1": [
                {
                    "id": scene1_id,
                    "image_id": scene1_id,
                    "panel_number": 1,
                    "style": "MODERN_ROMANCE_DRAMA_MANHWA",
                    "image_url": scene1_url,
                    "is_selected": False, # Changed to False so new images are easier to see
                    "created_at": datetime.now().isoformat(),
                }
            ],
            "2": [
                {
                    "id": scene2_id,
                    "image_id": scene2_id,
                    "panel_number": 2,
                    "style": "MODERN_ROMANCE_DRAMA_MANHWA",
                    "image_url": scene2_url,
                    "is_selected": False, # Changed to False
                    "created_at": datetime.now().isoformat(),
                }
            ]
        },
        "created_at": datetime.now().isoformat(),
    }
    
    # 5. Create character images data
    char_images = {
        f"{script_id}:TestChar": [
            {
                "id": char_img_id,
                "image_id": char_img_id,
                "character_name": "TestChar",
                "style": "MODERN_ROMANCE_DRAMA_MANHWA",
                "image_url": char_img_url,
                "is_selected": True,
                "created_at": datetime.now().isoformat(),
            }
        ]
    }
    
    # 6. Create scene images data
    scene_images = {
        f"{script_id}:1": [
            {
                "id": scene1_id,
                "image_id": scene1_id,
                "panel_number": 1,
                "style": "MODERN_ROMANCE_DRAMA_MANHWA",
                "image_url": scene1_url,
                "is_selected": False,
                "created_at": datetime.now().isoformat(),
            }
        ],
        f"{script_id}:2": [
            {
                "id": scene2_id,
                "image_id": scene2_id,
                "panel_number": 2,
                "style": "MODERN_ROMANCE_DRAMA_MANHWA",
                "image_url": scene2_url,
                "is_selected": False,
                "created_at": datetime.now().isoformat(),
            }
        ]
    }
    
    # Save all data
    print("\n💾 Saving data files...")
    
    with open(os.path.join(DATA_DIR, 'stories.json'), 'w') as f:
        json.dump({story_id: story}, f, indent=2)
    print(f"   ✓ stories.json")
    
    with open(os.path.join(DATA_DIR, 'workflows.json'), 'w') as f:
        json.dump({workflow_id: workflow}, f, indent=2)
    print(f"   ✓ workflows.json")
    
    with open(os.path.join(DATA_DIR, 'webtoon_scripts.json'), 'w') as f:
        json.dump({script_id: script}, f, indent=2)
    print(f"   ✓ webtoon_scripts.json")
    
    with open(os.path.join(DATA_DIR, 'character_images.json'), 'w') as f:
        json.dump(char_images, f, indent=2)
    print(f"   ✓ character_images.json")
    
    with open(os.path.join(DATA_DIR, 'scene_images.json'), 'w') as f:
        json.dump(scene_images, f, indent=2)
    print(f"   ✓ scene_images.json")
    
    print("\n" + "=" * 60)
    print("✅ Test data setup complete!")
    print("=" * 60)
    print(f"\n📌 Next steps:")
    print(f"   1. Run:  npm run dev")
    print(f"   2. Open: http://localhost:3000")
    print(f"   3. The test story should appear in the list")
    print(f"   4. Navigate to Scene Images → Video tab to test")
    print(f"\n   Script ID: {script_id}")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
