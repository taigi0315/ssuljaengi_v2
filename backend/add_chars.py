import json
import os
import shutil
import uuid
from datetime import datetime

# Paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BACKEND_DIR, "data")
CACHE_IMAGES_DIR = os.path.join(BACKEND_DIR, "cache", "images")
TEMP_DIR = os.path.join(BACKEND_DIR, "temp")
LIBRARY_FILE = os.path.join(DATA_DIR, "character_library.json")

# Ensure directories exist
os.makedirs(CACHE_IMAGES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Files to process
files_to_process = [
    {
        "src": "Ji-hoon_image_2.png",
        "dest_name": "Ji-hoon_image_2.png",
        "name": "Ji-hoon",
        "gender": "male", # Guessing
        "age": "20s"      # Guessing
    },
    {
        "src": "Min-ji_image_1 (1).png",
        "dest_name": "Min-ji_image_1.png",
        "name": "Min-ji",
        "gender": "female", # Guessing
        "age": "20s"        # Guessing
    }
]

def load_library():
    if not os.path.exists(LIBRARY_FILE):
        return {}
    try:
        with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading library: {e}")
        return {}

def save_library(data):
    try:
        with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Library saved successfully.")
    except Exception as e:
        print(f"Error saving library: {e}")

def main():
    library = load_library()
    
    for item in files_to_process:
        src_path = os.path.join(TEMP_DIR, item["src"])
        if not os.path.exists(src_path):
            print(f"Source file not found: {src_path}")
            continue
            
        dest_path = os.path.join(CACHE_IMAGES_DIR, item["dest_name"])
        
        # Copy file
        try:
            shutil.copy2(src_path, dest_path)
            print(f"Copied {item['src']} to {dest_path}")
        except Exception as e:
            print(f"Error copying file {item['src']}: {e}")
            continue
            
        # Create character entry
        char_id = str(uuid.uuid4())
        
        # Construct Character model data (matching app.models.story.Character fields)
        character_data = {
            "name": item["name"],
            "reference_tag": f"{item['name']}({item['age']}, {item['gender']})",
            "gender": item["gender"],
            "age": item["age"],
            "face": "",
            "hair": "",
            "body": "",
            "outfit": "",
            "mood": "",
            "appearance_notes": "Imported from existing image.",
            "typical_outfit": "",
            "personality_brief": "",
            "visual_description": f"{item['gender']}, {item['age']}, imported character image."
        }
        
        entry = {
            "id": char_id,
            "character": character_data,
            "image_url": f"/api/assets/cache/images/{item['dest_name']}",
            "created_at": datetime.now().isoformat(),
            "tags": ["imported"]
        }
        
        library[char_id] = entry
        print(f"Added character {item['name']} with ID {char_id}")

    save_library(library)

if __name__ == "__main__":
    main()
