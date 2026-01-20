"""
Character Library API endpoints.

This module provides endpoints for saving and retrieving reusable characters.
"""
import logging
import uuid
import os
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.story import Character
from app.utils.persistence import JsonStore
from app.utils.git_ops import git_add_commit_push
from app.config import get_settings

router = APIRouter(prefix="/library", tags=["library"])
logger = logging.getLogger(__name__)

# Initialize persistent store
settings = get_settings()
character_library = JsonStore(
    os.path.join(settings.data_dir, "character_library.json")
)

class SavedCharacter(BaseModel):
    """Model for a character saved in the library."""
    id: str = Field(..., description="Unique library ID")
    character: Character = Field(..., description="Character data")
    image_url: Optional[str] = Field(default=None, description="Default image URL for this character")
    created_at: datetime = Field(default_factory=datetime.now, description="When this was saved")
    tags: List[str] = Field(default_factory=list, description="Search tags")

class SaveCharacterRequest(BaseModel):
    """Request to save a character to the library."""
    character: Character
    image_url: Optional[str] = None
    tags: List[str] = []

@router.get("/characters", response_model=List[SavedCharacter])
async def get_characters():
    """List all characters in the library."""
    # Ensure data is loaded
    if not character_library and os.path.exists(character_library.file_path):
        character_library._load()
        
    # Sort by created_at desc
    chars = list(character_library.values())
    return sorted(chars, key=lambda x: x.get('created_at', ''), reverse=True)

@router.post("/character", response_model=SavedCharacter)
async def save_character(request: SaveCharacterRequest):
    """Save a character to the library."""
    # Check if character with same name already exists (optional, but good for UX)
    # For now, just create a new entry every time
    
    char_id = str(uuid.uuid4())
    saved_char = SavedCharacter(
        id=char_id,
        character=request.character,
        image_url=request.image_url,
        tags=request.tags
    )
    
    character_library[char_id] = saved_char.model_dump()
    await character_library.save()
    
    logger.info(f"Saved character to library: {request.character.name} ({char_id})")
    
    # Sync to GitHub
    # We need to add the JSON file and the image file (if it exists)
    files_to_sync = ["backend/data/character_library.json"]
    
    # If image_url is a local path (starts with /api/assets/cache...), map it to actual file path
    # Example: /api/assets/cache/images/foo.png -> backend/cache/images/foo.png
    # But wait, 'backend/data' is where json is. 
    # 'backend/cache/images' is where images are.
    # The image_url stored is usually the full URL or relative path.
    # Let's inspect how image_url is stored. 
    # Usually: /api/assets/cache/images/CharName_hash.png
    
    if request.image_url and "/api/assets/cache/images/" in request.image_url:
        filename = request.image_url.split("/")[-1]
        # Assuming the repo root is the parent of 'backend'
        files_to_sync.append(f"backend/cache/images/{filename}")
        
    try:
        # Run in background or await? 
        # User wants to be sure it's pushed. Let's await (blocking for a few seconds).
        # But `git_add_commit_push` is synchronous in execution but wrapped? No, my implementation calls subprocess.
        # We should probably run this asynchronously if possible, but the user wants "database" behavior.
        # Let's just run it.
        # Note: We need to ensure we run from the REPO ROOT (parent of backend).
        # We can pass cwd explicitly.
        
        # Determine repo root. If we are in backend/app/routers, we are deep.
        # But the process was started in `backend` folder? 
        # Actually `npm run dev` calls `cd backend && ./run.sh`.
        # So CWD of python process IS `backend`.
        # So we need to go up one level to be in repo root.
        repo_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
        
        # Wait, if we are in `backend`, then "backend/data/..." path logic above is wrong relative to `backend`.
        # If we are in `backend` dir:
        # data/character_library.json is correct?
        # cache/images/... is correct?
        # AND if we run git from `repo_root` (parent), then "backend/data/..." IS correct.
        
        git_add_commit_push(files_to_sync, f"Save character: {request.character.name}", cwd=repo_root)
        
    except Exception as e:
        logger.error(f"Failed to sync to GitHub: {e}")

    return saved_char

@router.delete("/character/{char_id}")
async def delete_character(char_id: str):
    """Delete a character from the library."""
    if char_id not in character_library:
        raise HTTPException(status_code=404, detail="Character not found")
        
    del character_library[char_id]
    await character_library.save()
    
    # Sync to GitHub (JSON update only)
    try:
        repo_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
        # We only sync the library JSON, not the image (preserving file as requested)
        git_add_commit_push(
            ["backend/data/character_library.json"], 
            f"Delete character: {char_id}", 
            cwd=repo_root
        )
    except Exception as e:
        logger.error(f"Failed to sync delete to GitHub: {e}")
        
    return {"message": "Character deleted"}
