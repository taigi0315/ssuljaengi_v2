#!/usr/bin/env python3
"""
Test the webtoon API endpoint to verify the fix.
"""

import requests
import json
import time

def test_webtoon_generation():
    """Test webtoon generation with a simple story."""
    
    url = "http://localhost:8000/webtoon/generate"
    
    # Simple test story
    story = """
    Hana is a shy high school student who loves reading books in the library. 
    One day, she accidentally bumps into Jae-hyun, the popular student council president. 
    Their books scatter everywhere, and as they pick them up together, their eyes meet. 
    Jae-hyun smiles warmly and helps her gather her books. 
    "I'm sorry," Hana whispers, blushing. 
    "No problem at all," Jae-hyun replies kindly. 
    From that moment, Hana can't stop thinking about his gentle smile.
    """
    
    payload = {
        "story_id": "test_story_123",
        "story_content": story.strip(),
        "story_genre": "MODERN_ROMANCE_DRAMA",
        "image_style": "BRIGHT_YOUTHFUL_WEBTOON"
    }
    
    print("Testing webtoon generation...")
    print(f"Story length: {len(story)} characters")
    print("Sending request...")
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Success!")
            print(f"  Generated panels: {len(result.get('panels', []))}")
            print(f"  Characters: {len(result.get('characters', []))}")
            print(f"  Script ID: {result.get('script_id', 'N/A')}")
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_webtoon_generation()
    if success:
        print("\n✓ Webtoon generation test passed!")
    else:
        print("\n✗ Webtoon generation test failed!")