#!/usr/bin/env python3
"""
Test with a very simple story to see if the basic functionality works.
"""

import requests
import json
import time

def test_simple_webtoon():
    """Test with a very simple story."""
    
    url = "http://localhost:8000/webtoon/generate"
    
    # Very simple story
    story = """
    A girl meets a boy. They talk. They smile. They become friends.
    """
    
    payload = {
        "story_id": "simple_test_123",
        "story_content": story.strip(),
        "story_genre": "MODERN_ROMANCE_DRAMA",
        "image_style": "BRIGHT_YOUTHFUL_WEBTOON"
    }
    
    print("Testing simple webtoon generation...")
    print(f"Story: {story.strip()}")
    print("Sending request...")
    
    try:
        response = requests.post(url, json=payload, timeout=180)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Success!")
            print(f"  Generated panels: {len(result.get('panels', []))}")
            print(f"  Characters: {len(result.get('characters', []))}")
            
            # Show first few panels
            panels = result.get('panels', [])
            for i, panel in enumerate(panels[:3]):
                print(f"  Panel {i+1}: {panel.get('visual_prompt', 'No prompt')[:50]}...")
            
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out after 3 minutes")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_simple_webtoon()
    if success:
        print("\n✓ Simple webtoon test passed!")
    else:
        print("\n✗ Simple webtoon test failed!")