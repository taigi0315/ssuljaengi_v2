#!/usr/bin/env python3
"""
Test direct generation bypassing complex workflow.
"""

import requests
import json

def test_direct_generation():
    """Test with minimal story to avoid workflow issues."""
    
    url = "http://localhost:8000/webtoon/generate"
    
    # Very minimal story
    story = "Girl meets boy."
    
    payload = {
        "story_id": "minimal_test",
        "story_content": story,
        "story_genre": "MODERN_ROMANCE_DRAMA",
        "image_style": "BRIGHT_YOUTHFUL_WEBTOON"
    }
    
    print("Testing minimal story generation...")
    print(f"Story: '{story}'")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Success!")
            
            # Check structure
            print(f"  Characters: {len(result.get('characters', []))}")
            print(f"  Scenes: {len(result.get('scenes', []))}")
            print(f"  Panels: {len(result.get('panels', []))}")
            
            if result.get('scenes'):
                print("  ✓ Scene structure found!")
                scene = result['scenes'][0]
                print(f"    First scene: {scene.get('scene_title', 'No title')}")
                print(f"    Panels in scene: {len(scene.get('panels', []))}")
            
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_direct_generation()
    if success:
        print("\n✓ Direct generation test passed!")
    else:
        print("\n✗ Direct generation test failed!")