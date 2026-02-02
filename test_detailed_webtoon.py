#!/usr/bin/env python3
"""
Test with a very detailed story to reach target panel count.
"""

import requests
import json

def test_detailed_webtoon():
    """Test with a very detailed story."""
    
    url = "http://localhost:8000/webtoon/generate"
    
    # Very detailed story with many scenes
    story = """
    Chapter 1: The Library
    
    Hana sits alone in the university library, surrounded by towering bookshelves. 
    She's always been the quiet type, preferring the company of books to people.
    Her fingers trace the spine of an old literature book as she searches for her next read.
    
    The afternoon sun streams through the tall windows, casting golden light across the wooden tables.
    Other students chat quietly in the distance, but Hana remains focused on her solitary world.
    She reaches for a book on the highest shelf, standing on her tiptoes.
    
    Chapter 2: The Fall
    
    The book is just out of reach. Hana stretches further, losing her balance.
    Time seems to slow as she begins to fall backward, books tumbling around her.
    Just then, strong arms catch her from behind, steadying her gently.
    
    She turns around, heart racing, to see who saved her.
    It's Jae-hyun, the student council president she's admired from afar.
    His kind brown eyes meet hers with genuine concern.
    "Are you alright?" he asks softly, his voice warm and reassuring.
    
    Chapter 3: First Words
    
    Hana's cheeks flush pink as she realizes how close they are.
    "I... I'm fine. Thank you," she whispers, quickly stepping back.
    Jae-hyun smiles gently, bending down to help collect the scattered books.
    "These look interesting," he comments, examining her literature choices.
    
    Hana is surprised by his genuine interest in her books.
    "You read poetry?" she asks, her voice barely audible.
    "I love it," Jae-hyun replies, his eyes lighting up. "Especially the classics."
    
    Chapter 4: An Invitation
    
    They spend the next few minutes discussing their favorite authors.
    Hana finds herself opening up more than she ever has with a stranger.
    "Would you like to study together sometime?" Jae-hyun asks hopefully.
    
    Hana's heart skips a beat. She nods shyly, unable to believe this is happening.
    "Tomorrow? Same time?" he suggests, gesturing to a quiet corner table.
    "I'd like that," Hana manages to say, her voice growing stronger.
    
    Chapter 5: The Next Day
    
    The next afternoon, Hana arrives at the library early, nervously arranging her books.
    She's chosen her favorite sweater and spent extra time on her appearance.
    When Jae-hyun arrives with his own stack of books, he smiles warmly at her.
    
    "You're already here," he says, settling into the chair across from her.
    They begin studying, but conversation flows naturally between them.
    Hana discovers that Jae-hyun is not just popular, but genuinely kind and thoughtful.
    
    Chapter 6: Growing Closer
    
    Days turn into weeks of library meetings.
    Hana slowly comes out of her shell, laughing at Jae-hyun's gentle humor.
    He listens intently when she shares her thoughts about literature.
    
    Other students begin to notice them together, whispering curiously.
    But in their quiet corner, Hana and Jae-hyun create their own little world.
    She starts to believe that maybe, just maybe, she's found someone special.
    
    Chapter 7: The Confession
    
    One evening, as cherry blossoms bloom outside the library windows,
    Jae-hyun walks Hana to the campus entrance.
    The pink petals drift gently in the spring breeze around them.
    
    "Hana," he says, stopping under a blooming tree.
    "These past weeks have been the best part of my day."
    He takes her hand gently, his touch warm and reassuring.
    
    "I feel the same way," Hana admits, her heart racing.
    "I never thought someone like you would notice someone like me."
    Jae-hyun shakes his head, squeezing her hand softly.
    
    "You're the most genuine person I've ever met," he tells her.
    Under the falling cherry blossoms, they share their first kiss.
    Hana finally feels like she belongs somewhere, with someone who truly sees her.
    """
    
    payload = {
        "story_id": "detailed_test_789",
        "story_content": story.strip(),
        "story_genre": "MODERN_ROMANCE_DRAMA",
        "image_style": "BRIGHT_YOUTHFUL_WEBTOON"
    }
    
    print("Testing detailed webtoon generation...")
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
                print(f"  ✓ Panel count {panel_count} meets ideal range (25+)")
            elif panel_count >= 20:
                print(f"  ✓ Panel count {panel_count} meets minimum range (20+)")
            else:
                print(f"  ⚠ Panel count {panel_count} is below minimum (20)")
            
            # Show character names
            characters = result.get('characters', [])
            if characters:
                char_names = [char.get('name', 'Unknown') for char in characters]
                print(f"  Characters: {', '.join(char_names)}")
            
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
    success = test_detailed_webtoon()
    if success:
        print("\n✓ Detailed webtoon test completed!")
    else:
        print("\n✗ Detailed webtoon test failed!")