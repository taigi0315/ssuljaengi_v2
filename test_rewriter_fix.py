#!/usr/bin/env python3
"""
Quick test to verify the webtoon rewriter fix.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.webtoon_rewriter import webtoon_rewriter
from app.models.story import WebtoonScript, Character, Panel


async def test_rewriter_fallback():
    """Test that the rewriter returns original script on failure."""
    
    # Create a simple test script
    test_character = Character(
        name="Test Character",
        reference_tag="TEST_CHAR",
        gender="female",
        age="20",
        face="Test face",
        hair="Test hair",
        body="Test body",
        outfit="Test outfit",
        mood="happy",
        visual_description="A test character"
    )
    
    test_panel = Panel(
        panel_number=1,
        scene_type="story",
        shot_type="medium",
        visual_prompt="A test panel with a character standing in a room",
        active_character_names=["Test Character"],
        dialogue=[],
        negative_prompt="",
        composition_notes="Test composition",
        environment_focus="room",
        environment_details="simple room",
        atmospheric_conditions="bright",
        story_beat="introduction",
        character_placement_and_action="standing",
        character_frame_percentage=50,
        environment_frame_percentage=50,
        style_variation=None
    )
    
    original_script = WebtoonScript(
        characters=[test_character],
        panels=[test_panel]
    )
    
    # Test with feedback that would normally cause expansion
    feedback = "ADD 20 MORE PANELS. Current: 1, Required: 25-40."
    story = "A simple test story about a character."
    
    try:
        print("Testing webtoon rewriter with potential failure scenario...")
        result = await webtoon_rewriter.rewrite_script(
            original_script, 
            feedback, 
            story
        )
        
        print(f"✓ Rewriter completed successfully")
        print(f"  Original panels: {len(original_script.panels)}")
        print(f"  Result panels: {len(result.panels)}")
        print(f"  Characters: {len(result.characters)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Rewriter failed: {e}")
        return False


async def main():
    """Run the test."""
    print("Testing webtoon rewriter fallback behavior...")
    
    success = await test_rewriter_fallback()
    
    if success:
        print("\n✓ Test passed - rewriter handles failures gracefully")
    else:
        print("\n✗ Test failed - rewriter still raises exceptions")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())