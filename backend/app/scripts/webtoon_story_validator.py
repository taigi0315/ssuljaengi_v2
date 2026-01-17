"""
Story Input Validator

Use this to diagnose if your story generation is producing the right format
for the webtoon writer to work with.
"""

def validate_story_for_webtoon(story_text: str) -> dict:
    """
    Validates if a story is structured correctly for webtoon panel breakdown.
    
    Returns:
        dict with validation results and recommendations
    """
    import re
    
    results = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
        "stats": {}
    }
    
    # Split into paragraphs
    paragraphs = [p.strip() for p in story_text.split('\n\n') if p.strip()]
    
    # Remove title if present
    if paragraphs and (paragraphs[0].startswith('Title:') or len(paragraphs[0]) < 100):
        title = paragraphs[0]
        paragraphs = paragraphs[1:]
    
    # Stats
    results["stats"]["total_paragraphs"] = len(paragraphs)
    results["stats"]["avg_paragraph_length"] = sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0
    
    # Check 1: Paragraph count (should be 8-16 beats)
    if len(paragraphs) < 8:
        results["valid"] = False
        results["issues"].append(
            f"❌ Only {len(paragraphs)} paragraphs. Need 8-16 beats for webtoon. "
            "Story is too short or not structured in beats."
        )
    elif len(paragraphs) > 16:
        results["warnings"].append(
            f"⚠️  {len(paragraphs)} paragraphs. Might be too many for 8-12 scenes. "
            "Consider condensing some beats."
        )
    else:
        results["stats"]["paragraph_count_ok"] = True
    
    # Check 2: Beat structure (each paragraph should be a moment, not flowing prose)
    prose_indicators = 0
    for i, para in enumerate(paragraphs, 1):
        # Red flags for prose-style writing
        if len(para) > 500:  # Too long for a single beat
            prose_indicators += 1
            results["warnings"].append(
                f"⚠️  Paragraph {i} is {len(para)} chars. Single beats should be 100-300 chars. "
                "Might be flowing prose instead of discrete moment."
            )
        
        # Check for multiple actions in one paragraph (sign of prose)
        action_verbs = re.findall(r'\b(walked|ran|thought|remembered|felt|realized|decided|looked|turned|spoke|said)\b', para.lower())
        if len(action_verbs) > 5:
            prose_indicators += 1
    
    if prose_indicators > len(paragraphs) * 0.3:  # More than 30% problematic
        results["valid"] = False
        results["issues"].append(
            "❌ Story appears to be PROSE-STYLE, not BEAT-BASED. "
            "Paragraphs are too long or contain multiple actions. "
            "Each paragraph should describe ONE visual moment."
        )
    
    # Check 3: Present tense (beats should be in present tense)
    past_tense_count = 0
    for para in paragraphs:
        past_tense = re.findall(r'\b(walked|thought|remembered|felt|realized|decided|looked|turned|spoke|said|was|were|had)\b', para.lower())
        if len(past_tense) > 3:
            past_tense_count += 1
    
    if past_tense_count > len(paragraphs) * 0.5:
        results["warnings"].append(
            f"⚠️  {past_tense_count}/{len(paragraphs)} paragraphs use past tense. "
            "Beat-based stories should use present tense for immediacy. "
            "Example: 'stands' not 'stood', 'reaches' not 'reached'"
        )
    
    # Check 4: Specific locations (each beat needs a location)
    location_words = ['platform', 'hallway', 'room', 'street', 'bridge', 'shop', 'café', 'building', 'park', 'station']
    paragraphs_with_locations = sum(1 for p in paragraphs if any(loc in p.lower() for loc in location_words))
    
    if paragraphs_with_locations < len(paragraphs) * 0.6:
        results["warnings"].append(
            f"⚠️  Only {paragraphs_with_locations}/{len(paragraphs)} paragraphs mention specific locations. "
            "Each beat should ground the reader in a physical space."
        )
    
    # Check 5: Dialogue presence
    dialogue_count = sum(1 for p in paragraphs if '"' in p or '"' in p or '"' in p)
    results["stats"]["paragraphs_with_dialogue"] = dialogue_count
    
    if dialogue_count < len(paragraphs) * 0.4:
        results["warnings"].append(
            f"⚠️  Only {dialogue_count}/{len(paragraphs)} paragraphs contain dialogue. "
            "Webtoons are dialogue-driven. Aim for 60-80% of beats having dialogue."
        )
    
    # Check 6: Character consistency
    # Look for character names
    potential_names = re.findall(r'\b[A-Z][a-z]+(?:-[a-z]+)?\b', story_text)
    unique_names = set(n for n in potential_names if len(n) > 2 and n not in ['The', 'A', 'In', 'On', 'At'])
    results["stats"]["unique_character_names"] = len(unique_names)
    
    if len(unique_names) > 4:
        results["warnings"].append(
            f"⚠️  Detected {len(unique_names)} potential character names: {list(unique_names)[:5]}. "
            "Keep cast to 2-4 characters for visual clarity."
        )
    
    # Generate recommendations
    if not results["valid"]:
        results["recommendations"].append(
            "🔧 CRITICAL: Regenerate story using the BEAT-BASED story prompt. "
            "Current story is prose-style and won't panel-ize well."
        )
    
    if dialogue_count < 5:
        results["recommendations"].append(
            "🔧 Add more dialogue. Conversations drive webtoon stories. "
            "Each beat should show characters talking, reacting, expressing."
        )
    
    if len(paragraphs) < 8:
        results["recommendations"].append(
            "🔧 Expand story to 8-16 beats. Add more moments: reactions, conversations, "
            "setting changes, emotional beats."
        )
    
    return results


def print_validation_report(results: dict):
    """Pretty print the validation results"""
    print("=" * 80)
    print("STORY VALIDATION REPORT")
    print("=" * 80)
    print()
    
    # Status
    if results["valid"]:
        print("✅ Story structure appears VALID for webtoon conversion")
    else:
        print("❌ Story structure has CRITICAL ISSUES")
    print()
    
    # Stats
    print("📊 STATISTICS:")
    for key, value in results["stats"].items():
        print(f"   {key}: {value}")
    print()
    
    # Issues
    if results["issues"]:
        print("🚨 CRITICAL ISSUES:")
        for issue in results["issues"]:
            print(f"   {issue}")
        print()
    
    # Warnings
    if results["warnings"]:
        print("⚠️  WARNINGS:")
        for warning in results["warnings"]:
            print(f"   {warning}")
        print()
    
    # Recommendations
    if results["recommendations"]:
        print("💡 RECOMMENDATIONS:")
        for rec in results["recommendations"]:
            print(f"   {rec}")
        print()
    
    print("=" * 80)


# Example usage
if __name__ == "__main__":
    
    # Example 1: BAD STORY (prose-style)
    bad_story = """
    Title: The Bridge
    
    Ji-hoon had been thinking about the past for weeks now. He remembered high school 
    in 2010, walking through those bustling hallways filled with students and the smell 
    of instant ramen. He thought about Soojin, how she used to laugh with her friends 
    near the notice board, her hair illuminated by sunlight. He had watched her from 
    afar, too nervous to approach, sketching in his notebook alone in the cafeteria 
    while she ate with her group of friends. Years later, standing on this bridge at 
    dusk, he clutched an old photograph and wondered what might have been if he'd just 
    said something back then.
    """
    
    print("VALIDATING BAD STORY (Prose-style):")
    print("-" * 80)
    results_bad = validate_story_for_webtoon(bad_story)
    print_validation_report(results_bad)
    print("\n\n")
    
    
    # Example 2: GOOD STORY (beat-based)
    good_story = """
    Title: The Bridge
    
    The Han River bridge stretches across the frame at dusk. Orange and purple sky 
    reflects on the water below. Ji-hoon stands at the center, alone, clutching an 
    old photograph. The city glows behind him.
    
    A high school hallway in 2010, packed with students. Lockers line the walls, 
    notice boards covered in flyers. Seventeen-year-old Ji-hoon navigates the crowd, 
    bumping into other students, looking overwhelmed.
    
    Near the notice board, Soojin laughs with her friends, sunlight streaming through 
    the windows illuminating her hair. Ji-hoon watches from a distance, hesitating.
    
    The cafeteria during lunch. Students crowd around tables, trays of food everywhere. 
    Ji-hoon sits alone at a corner table, sketching in his notebook. He glances up at 
    Soojin's table across the room. "Just go talk to her," his friend Min whispers, 
    nudging him.
    
    Soojin approaches Ji-hoon's table, holding a folded paper crane. "You dropped this," 
    she says, smiling. Ji-hoon looks up, surprised. "I... I didn't—" "I know," she 
    interrupts. "I made it for you."
    
    Ji-hoon's face flushes red. He takes the crane carefully, their fingers brushing. 
    "Why?" he manages to ask. Soojin sits down across from him. "You're always alone. 
    I thought you could use a friend."
    
    They talk for hours, the cafeteria emptying around them. Ji-hoon shows her his 
    sketches. Soojin's eyes widen. "These are amazing! You should show people." 
    Ji-hoon shakes his head. "I'm not good enough." "Yes, you are," she insists.
    
    The school rooftop at sunset. Ji-hoon and Soojin stand by the fence, looking out 
    at the city. "Thanks for today," Ji-hoon says quietly. Soojin turns to him. "Let's 
    do this again tomorrow." She smiles, and for the first time, he smiles back.
    
    Back on the bridge at dusk, present day. Ji-hoon looks down at the photograph— 
    him and Soojin on that rooftop. "If only I'd kept that promise," he whispers.
    
    His phone buzzes. A message: "Same bridge, same time tomorrow?" The sender: Soojin. 
    Ji-hoon's eyes widen. He looks up at the city lights, hope spreading across his face.
    """
    
    print("VALIDATING GOOD STORY (Beat-based):")
    print("-" * 80)
    results_good = validate_story_for_webtoon(good_story)
    print_validation_report(results_good)