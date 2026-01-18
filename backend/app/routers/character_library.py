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
    return saved_char

@router.delete("/character/{char_id}")
async def delete_character(char_id: str):
    """Delete a character from the library."""
    if char_id not in character_library:
        raise HTTPException(status_code=404, detail="Character not found")
        
    del character_library[char_id]
    await character_library.save()
    return {"message": "Character deleted"}
