#!/usr/bin/env python
"""
E2E Test Setup Script - Updated for Current Schema
- 1 story
- 1 webtoon script with 5 panels
- Page 1: Panels 1, 2
- Page 2: Panels 3, 4, 5
- Proper dialogue_bubbles (panel-keyed) and page_dialogue_bubbles (page-keyed) for video generation
- All WebtoonPanel fields populated
"""
import os
import sys
import json
import uuid
from datetime import datetime
from PIL import Image, ImageDraw

# Setup paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BACKEND_DIR, 'data')
CACHE_DIR = os.path.join(BACKEND_DIR, 'cache', 'images')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)


def create_test_image(filename: str, text: str, color: tuple, size: tuple = (1080, 1920)) -> str:
    """Create a simple test image with text."""
    img = Image.new("RGB", size, color=color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([(20, 20), (size[0]-20, size[1]-20)], outline="white", width=5)
    cx, cy = size[0]//2, size[1]//2
    draw.line([(cx-100, cy), (cx+100, cy)], fill="white", width=4)
    draw.line([(cx, cy-100), (cx, cy+100)], fill="white", width=4)
    filepath = os.path.join(CACHE_DIR, filename)
    img.save(filepath, "PNG")
    return filepath


def main():
    print("=" * 60)
    print("E2E Test Setup (5 Panels, 2 Multi-Panel Pages)")
    print("Updated for current WebtoonPanel schema")
    print("=" * 60)

    story_id = str(uuid.uuid4())
    script_id = str(uuid.uuid4())
    workflow_id = str(uuid.uuid4())

    print(f"\n Creating test data...")

    # 1. Mock Images
    char_img_id = str(uuid.uuid4())
    char_img_path = create_test_image(f"char_{char_img_id[:8]}.png", "Character", (80, 100, 140))
    char_img_url = f"/api/assets/cache/images/{os.path.basename(char_img_path)}"

    page1_id = uuid.uuid4().hex[:8]
    page1_url = f"/api/assets/cache/images/page1_{page1_id}.png"
    create_test_image(f"page1_{page1_id}.png", "Page 1", (100, 80, 120))

    page2_id = uuid.uuid4().hex[:8]
    page2_url = f"/api/assets/cache/images/page2_{page2_id}.png"
    create_test_image(f"page2_{page2_id}.png", "Page 2", (120, 100, 80))

    panel_urls = []
    for i in range(1, 6):
        p_filename = f"panel{i}_{uuid.uuid4().hex[:8]}.png"
        create_test_image(p_filename, f"Panel {i}", (40 + i*20, 60 + i*15, 80))
        panel_urls.append(f"/api/assets/cache/images/{p_filename}")

    # 2. Characters with full schema
    characters = [
        {
            "name": "Mina",
            "reference_tag": "Mina(20s, female, long black hair)",
            "gender": "female",
            "age": "25",
            "face": "soft oval face, large expressive eyes, gentle smile",
            "hair": "long flowing black hair, slightly wavy",
            "body": "slender figure, graceful posture",
            "outfit": "cream colored sweater, light blue jeans",
            "mood": "warm and optimistic",
            "appearance_notes": "",
            "typical_outfit": "casual modern fashion",
            "personality_brief": "kind and thoughtful",
            "visual_description": "A young woman in her mid-20s with soft oval face, large expressive eyes, and a gentle smile. She has long flowing black hair that's slightly wavy, a slender figure with graceful posture. She wears a cream colored sweater and light blue jeans, giving off a warm and optimistic vibe."
        },
        {
            "name": "Jihoon",
            "reference_tag": "Jihoon(late 20s, male, short dark hair)",
            "gender": "male",
            "age": "28",
            "face": "sharp jawline, deep brown eyes, thoughtful expression",
            "hair": "short dark brown hair, neatly styled",
            "body": "tall athletic build, broad shoulders",
            "outfit": "navy blazer over white shirt, dark pants",
            "mood": "reserved but caring",
            "appearance_notes": "",
            "typical_outfit": "smart casual business attire",
            "personality_brief": "quiet and dependable",
            "visual_description": "A tall man in his late 20s with a sharp jawline, deep brown eyes, and a thoughtful expression. He has short dark brown hair neatly styled, an athletic build with broad shoulders. He wears a navy blazer over a white shirt with dark pants, appearing reserved but caring."
        }
    ]

    # 3. Panels with full WebtoonPanel schema
    panels = [
        {
            "panel_number": 1,
            "shot_type": "wide",
            "active_character_names": ["Mina", "Jihoon"],
            "visual_prompt": "Wide shot of a cozy coffee shop interior with warm lighting. A young woman (Mina) and a tall man (Jihoon) sit across from each other at a small wooden table by the window. Afternoon sunlight streams through, creating a warm atmosphere. Both appear slightly nervous but hopeful.",
            "negative_prompt": "text, speech bubbles, dialogue boxes, words, letters, watermark",
            "composition_notes": "Establish the setting and both characters. Window on the right provides natural lighting.",
            "environment_focus": "Modern Korean coffee shop",
            "environment_details": "Wooden furniture, potted plants, warm pendant lights, large windows, coffee cups on table",
            "atmospheric_conditions": "Warm afternoon sunlight, cozy indoor ambiance",
            "story_beat": "Mina and Jihoon meet at a coffee shop after a long time apart.",
            "emotional_intensity": 4,
            "character_frame_percentage": 30,
            "environment_frame_percentage": 70,
            "character_placement_and_action": "Mina sits on the left side, Jihoon on the right. They face each other across a small table, both holding coffee cups.",
            "sfx_effects": None,
            "dialogue": [
                {"character": "Mina", "text": "It's been so long..."},
                {"character": "Jihoon", "text": "Three years. I wasn't sure you'd come."}
            ]
        },
        {
            "panel_number": 2,
            "shot_type": "close_up",
            "active_character_names": ["Mina"],
            "visual_prompt": "Close-up of a young woman's face (Mina). She has soft oval features, large expressive eyes glistening with emotion, and long black hair. Her expression shows a mix of nervousness and hope. Soft lighting from the side.",
            "negative_prompt": "text, speech bubbles, dialogue boxes, words, letters, watermark",
            "composition_notes": "Focus on Mina's emotional state. Eyes are the focal point.",
            "environment_focus": "Coffee shop interior (blurred)",
            "environment_details": "Soft bokeh background of warm cafe lights",
            "atmospheric_conditions": "Warm indoor lighting with soft shadows",
            "story_beat": "Mina's internal conflict shows on her face.",
            "emotional_intensity": 6,
            "character_frame_percentage": 85,
            "environment_frame_percentage": 15,
            "character_placement_and_action": "Mina centered in frame, looking slightly down and to the side, avoiding direct eye contact.",
            "sfx_effects": None,
            "dialogue": [
                {"character": "Mina", "text": "I almost didn't. But..."},
                {"character": "Mina", "text": "I needed to see you."}
            ]
        },
        {
            "panel_number": 3,
            "shot_type": "medium",
            "active_character_names": ["Jihoon"],
            "visual_prompt": "Medium shot of a tall man (Jihoon) with sharp jawline and short dark hair. He wears a navy blazer over a white shirt. His expression is serious but softens as he listens. His hands are wrapped around a coffee cup.",
            "negative_prompt": "text, speech bubbles, dialogue boxes, words, letters, watermark",
            "composition_notes": "Show Jihoon's reaction to Mina's words. Upper body visible.",
            "environment_focus": "Coffee shop table area",
            "environment_details": "Coffee cup, table edge, blurred background with warm tones",
            "atmospheric_conditions": "Soft warm lighting from window",
            "story_beat": "Jihoon responds with carefully chosen words.",
            "emotional_intensity": 5,
            "character_frame_percentage": 60,
            "environment_frame_percentage": 40,
            "character_placement_and_action": "Jihoon seated, leaning slightly forward, hands around coffee cup. His posture shows he's fully focused on the conversation.",
            "sfx_effects": None,
            "dialogue": [
                {"character": "Jihoon", "text": "I thought about you every day."},
                {"character": "Jihoon", "text": "I should have called sooner."}
            ]
        },
        {
            "panel_number": 4,
            "shot_type": "medium_close_up",
            "active_character_names": ["Mina", "Jihoon"],
            "visual_prompt": "Medium close-up shot showing both characters from the side. Mina and Jihoon reach across the small table, their hands almost touching but not quite. Tension and longing visible in the space between their hands. Warm golden light from the window.",
            "negative_prompt": "text, speech bubbles, dialogue boxes, words, letters, watermark",
            "composition_notes": "Focus on the hands almost touching - the emotional climax. Shallow depth of field.",
            "environment_focus": "Coffee shop table",
            "environment_details": "Wooden table surface, warm light, soft focus background",
            "atmospheric_conditions": "Golden hour lighting through window, romantic atmosphere",
            "story_beat": "The emotional turning point - they almost reconnect physically.",
            "emotional_intensity": 8,
            "character_frame_percentage": 70,
            "environment_frame_percentage": 30,
            "character_placement_and_action": "Both reaching across the table, hands hovering inches apart. Mina on left, Jihoon on right.",
            "sfx_effects": None,
            "dialogue": [
                {"character": "Mina", "text": "Can we start over?"},
                {"character": "Jihoon", "text": "I'd like that. More than anything."}
            ]
        },
        {
            "panel_number": 5,
            "shot_type": "wide",
            "active_character_names": ["Mina", "Jihoon"],
            "visual_prompt": "Wide shot of the coffee shop. Mina and Jihoon are now sitting closer together, their hands intertwined on the table. They share a warm smile. The cafe around them seems to glow with the setting sun. Other patrons are blurred in the background.",
            "negative_prompt": "text, speech bubbles, dialogue boxes, words, letters, watermark",
            "composition_notes": "Resolution shot. Show them together, connected. Warm, hopeful ending.",
            "environment_focus": "Coffee shop with sunset lighting",
            "environment_details": "Warm sunset glow through windows, cozy cafe atmosphere, other patrons as silhouettes",
            "atmospheric_conditions": "Golden sunset light, warm romantic ambiance",
            "story_beat": "They decide to give their relationship another chance.",
            "emotional_intensity": 7,
            "character_frame_percentage": 35,
            "environment_frame_percentage": 65,
            "character_placement_and_action": "Seated side by side now, hands together on table. Both smiling softly at each other.",
            "sfx_effects": None,
            "dialogue": [
                {"character": "Jihoon", "text": "Same time tomorrow?"},
                {"character": "Mina", "text": "It's a date."}
            ]
        }
    ]

    # 4. Dialogue bubbles keyed by panel number (legacy format)
    dialogue_bubbles = {}
    for panel in panels:
        panel_num = str(panel["panel_number"])
        bubbles = []
        for idx, d in enumerate(panel["dialogue"]):
            bubbles.append({
                "text": d["text"],
                "characterName": d["character"],
                "x": 25 + (idx * 50),  # Spread horizontally
                "y": 15 + (idx * 12),   # Stack vertically
                "width": 40,
                "height": 10
            })
        dialogue_bubbles[panel_num] = bubbles

    # 5. Page dialogue bubbles (new format for video generation)
    # Page 1 = Panels 1, 2; Page 2 = Panels 3, 4, 5
    page_dialogue_bubbles = {
        "1": [
            # From Panel 1
            {"text": "It's been so long...", "characterName": "Mina", "x": 20, "y": 15, "width": 35, "height": 8},
            {"text": "Three years. I wasn't sure you'd come.", "characterName": "Jihoon", "x": 55, "y": 15, "width": 40, "height": 8},
            # From Panel 2
            {"text": "I almost didn't. But...", "characterName": "Mina", "x": 20, "y": 60, "width": 35, "height": 8},
            {"text": "I needed to see you.", "characterName": "Mina", "x": 20, "y": 72, "width": 35, "height": 8},
        ],
        "2": [
            # From Panel 3
            {"text": "I thought about you every day.", "characterName": "Jihoon", "x": 55, "y": 10, "width": 40, "height": 8},
            {"text": "I should have called sooner.", "characterName": "Jihoon", "x": 55, "y": 22, "width": 40, "height": 8},
            # From Panel 4
            {"text": "Can we start over?", "characterName": "Mina", "x": 20, "y": 45, "width": 35, "height": 8},
            {"text": "I'd like that. More than anything.", "characterName": "Jihoon", "x": 55, "y": 45, "width": 40, "height": 8},
            # From Panel 5
            {"text": "Same time tomorrow?", "characterName": "Jihoon", "x": 55, "y": 80, "width": 35, "height": 8},
            {"text": "It's a date.", "characterName": "Mina", "x": 20, "y": 80, "width": 30, "height": 8},
        ]
    }

    # 6. Create webtoon script with all data
    script = {
        "script_id": script_id,
        "story_id": story_id,
        "title": "Second Chance at the Coffee Shop",
        "genre": "MODERN_ROMANCE_DRAMA",  # Updated to current genre key
        "image_style": "SOFT_ROMANTIC_WEBTOON",  # Added image style
        "characters": characters,
        "panels": panels,
        "character_images": {
            "Mina": [{"id": char_img_id, "image_url": char_img_url, "is_selected": True}],
            "Jihoon": [{"id": str(uuid.uuid4()), "image_url": char_img_url, "is_selected": True}]
        },
        "scene_images": {
            str(i): [{"id": str(uuid.uuid4()), "panel_number": i, "image_url": panel_urls[i-1], "is_selected": False}]
            for i in range(1, 6)
        },
        "page_images": {
            f"{script_id}:1": [{
                "id": str(uuid.uuid4()),
                "page_number": 1,
                "panel_indices": [0, 1],
                "image_url": page1_url,
                "is_selected": True
            }],
            f"{script_id}:2": [{
                "id": str(uuid.uuid4()),
                "page_number": 2,
                "panel_indices": [2, 3, 4],
                "image_url": page2_url,
                "is_selected": True
            }]
        },
        "dialogue_bubbles": dialogue_bubbles,
        "page_dialogue_bubbles": page_dialogue_bubbles,
        "created_at": datetime.now().isoformat(),
    }

    # Create story object
    story = {
        "story_id": story_id,
        "title": "Second Chance at the Coffee Shop",
        "content": """Mina hesitated outside the coffee shop, her hand hovering over the door handle. Three years had passed since she last saw Jihoon, three years of unanswered messages and sleepless nights. When his text came last week, asking to meet, she almost deleted it.

But here she was.

Inside, Jihoon sat by the window, exactly where they used to sit. His dark hair was shorter now, and he wore the kind of blazer she always said suited him. When their eyes met, the years seemed to collapse.

"It's been so long..." she managed, sliding into the seat across from him.

"Three years," he said softly. "I wasn't sure you'd come."

They talked for hours, about everything and nothing, dancing around the words that mattered most. It was only when the sunset turned the cafe golden that Mina found her courage.

"Can we start over?" she asked.

Jihoon's hand found hers across the table. "I'd like that. More than anything."

As the last light faded, they made a promise - same time tomorrow, and the day after that, for as long as it took to rebuild what they'd lost.""",
        "post_id": None,
        "post_title": "Second Chance at the Coffee Shop",
        "mood": "MODERN_ROMANCE_DRAMA",
        "evaluation_score": 8.5,
        "rewrite_count": 0,
        "created_at": datetime.now().isoformat()
    }

    # Save all files
    print("Saving data files...")

    with open(os.path.join(DATA_DIR, 'stories.json'), 'w') as f:
        json.dump({story_id: story}, f, indent=2)

    with open(os.path.join(DATA_DIR, 'webtoon_scripts.json'), 'w') as f:
        json.dump({script_id: script}, f, indent=2)

    with open(os.path.join(DATA_DIR, 'workflows.json'), 'w') as f:
        json.dump({workflow_id: {"workflow_id": workflow_id, "status": "COMPLETED"}}, f, indent=2)

    with open(os.path.join(DATA_DIR, 'scene_images.json'), 'w') as f:
        json.dump({f"{script_id}:{i}": script["scene_images"][str(i)] for i in range(1, 6)}, f, indent=2)

    with open(os.path.join(DATA_DIR, 'page_images.json'), 'w') as f:
        json.dump(script["page_images"], f, indent=2)

    with open(os.path.join(DATA_DIR, 'dialogue_bubbles.json'), 'w') as f:
        json.dump({f"{script_id}:{i}": dialogue_bubbles[str(i)] for i in range(1, 6)}, f, indent=2)

    with open(os.path.join(DATA_DIR, 'page_dialogue_bubbles.json'), 'w') as f:
        json.dump({f"{script_id}:{p}": page_dialogue_bubbles[p] for p in ["1", "2"]}, f, indent=2)

    print("\n" + "=" * 60)
    print("Test data created successfully!")
    print("=" * 60)
    print(f"\nStory ID: {story_id}")
    print(f"Script ID: {script_id}")
    print(f"Workflow ID: {workflow_id}")
    print(f"\nGenre: MODERN_ROMANCE_DRAMA")
    print(f"Image Style: SOFT_ROMANTIC_WEBTOON")
    print(f"\nPanels: 5 (varied shot types: wide, close_up, medium, medium_close_up)")
    print(f"Pages: 2 (Page 1: panels 1-2, Page 2: panels 3-5)")
    print(f"Characters: Mina, Jihoon")
    print(f"\nAll WebtoonPanel fields populated:")
    print("  - visual_prompt, negative_prompt, composition_notes")
    print("  - environment_focus, environment_details, atmospheric_conditions")
    print("  - character_frame_percentage, environment_frame_percentage")
    print("  - character_placement_and_action, story_beat, emotional_intensity")
    print(f"\nDialogue formats:")
    print("  - dialogue_bubbles (keyed by panel number)")
    print("  - page_dialogue_bubbles (keyed by page number - for video)")


if __name__ == "__main__":
    main()
