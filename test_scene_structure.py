#!/usr/bin/env python3
"""
Test the new scene structure directly.
"""

import requests
import json

def test_scene_structure():
    """Test the scene structure in the API response."""
    
    url = "http://localhost:8000/webtoon/generate"
    
    # Simple story
    story = "A girl meets a boy. They talk and become friends."
    
    payload = {
        "story_id": "scene_test_123",
        "story_content": story,
        "story_genre": "MODERN_ROMANCE_DRAMA",
        "image_style": "BRIGHT_YOUTHFUL_WEBTOON"
    }
    
    print("Testing scene structure...")
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Success!")
            
            # Check if we have scenes in the response
            if 'scenes' in result:
                print(f"  ✓ Found scenes: {len(result['scenes'])}")
                for i, scene in enumerate(result['scenes'][:2]):  # Show first 2 scenes
                    print(f"    Scene {i+1}: {scene.get('scene_title', 'No title')}")
                    print(f"      Panels: {len(scene.get('panels', []))}")
                    for j, panel in enumerate(scene.get('panels', [])[:2]):  # Show first 2 panels
                        print(f"        Panel {j+1}: {panel.get('visual_prompt', 'No prompt')[:50]}...")
            else:
                print("  ⚠ No scenes found in response")
            
            # Check backward compatibility - panels property
            if 'panels' in result:
                print(f"  ✓ Backward compatibility - flat panels: {len(result['panels'])}")
            else:
                print("  ⚠ No flat panels found (backward compatibility issue)")
            
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
    success = test_scene_structure()
    if success:
        print("\n✓ Scene structure test completed!")
    else:
        print("\n✗ Scene structure test failed!")