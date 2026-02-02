#!/usr/bin/env python3
"""
Test with a longer story to see if we can reach the target panel count.
"""

import requests
import json

def test_longer_webtoon():
    """Test with a longer, more detailed story."""
    
    url = "http://localhost:8000/webtoon/generate"
    
    # Longer story with more details
    story = """
    Hana is a shy college student who spends most of her time in the library. 
    She's always been invisible to others, preferring books to people.
    
    One rainy afternoon, while reaching for a book on the top shelf, she loses her balance.
    Just as she's about to fall, strong arms catch her from behind.
    
    She turns around to see Jae-hyun, the popular student council president.
    Their eyes meet for a moment, and Hana feels her heart skip a beat.
    "Are you okay?" he asks with genuine concern.
    
    Embarrassed, Hana quickly pulls away. "I'm fine, thank you," she whispers.
    But as she hurries away, she can't stop thinking about his warm smile.
    
    The next day, Hae-hyun approaches her table in the library.
    "Mind if I sit here?" he asks, holding a stack of books.
    Surprised but pleased, Hana nods shyly.
    
    They begin studying together, and slowly, Hana starts to open up.
    She discovers that behind his popular exterior, Jae-hyun is kind and thoughtful.
    
    As days pass, their friendship grows stronger.
    Jae-hyun helps Hana gain confidence, while she shows him the joy of quiet moments.
    
    One evening, as they walk together under the cherry blossoms,
    Jae-hyun takes her hand gently.
    "I'm glad I caught you that day," he says softly.
    Hana smiles, finally feeling like she belongs somewhere.
    """
    
    payload = {
        "story_id": "longer_test_456",
        "story_content": story.strip(),
        "story_genre": "MODERN_ROMANCE_DRAMA",
        "image_style": "BRIGHT_YOUTHFUL_WEBTOON"
    }
    
    print("Testing longer webtoon generation...")
    print(f"Story length: {len(story)} characters")
    print("Sending request...")
    
    try:
        response = requests.post(url, json=payload, timeout=180)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Success!")
            print(f"  Generated panels: {len(result.get('panels', []))}")
            print(f"  Characters: {len(result.get('characters', []))}")
            
            # Check if it meets the target range
            panel_count = len(result.get('panels', []))
            if panel_count >= 25:
                print(f"  ✓ Panel count {panel_count} meets target range (25+)")
            elif panel_count >= 20:
                print(f"  ⚠ Panel count {panel_count} is acceptable but below ideal (25+)")
            else:
                print(f"  ✗ Panel count {panel_count} is below minimum (20)")
            
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
        print("✗ Request timed out")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_longer_webtoon()
    if success:
        print("\n✓ Longer webtoon test completed!")
    else:
        print("\n✗ Longer webtoon test failed!")