"""
Webtoon generation API endpoints.

This module provides REST API endpoints for webtoon script generation and character image generation:
- POST /webtoon/generate: Convert story to webtoon script
- POST /webtoon/character/image: Generate character image
- GET /webtoon/{script_id}: Retrieve webtoon script
- GET /webtoon/character/{character_name}/images: Get all images for a character
- GET /webtoon/image-styles: Get available image styles with preview images
"""

import logging
import uuid
from typing import Dict, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

from app.models.story import (
    GenerateWebtoonRequest,
    GenerateCharacterImageRequest,
    WebtoonScriptResponse,
    CharacterImage,
    WebtoonScript
)
from app.services.webtoon_writer import webtoon_writer
from app.services.image_generator import image_generator


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webtoon", tags=["Webtoon"])

# In-memory storage (use Redis/database in production)
webtoon_scripts: Dict[str, dict] = {}
character_images: Dict[str, List[dict]] = {}  # script_id -> list of images

# Import stories from story router
from app.routers.story import stories


@router.get("/image-styles")
async def get_image_styles():
    """
    Get available image styles with metadata.
    
    Returns:
        List of image style options with IDs, names, and descriptions
    """
    return [
        {
            "id": "HISTORY_SAGEUK_ROMANCE",
            "name": "Historical Romance",
            "description": "Elegant sageuk style with dramatic lighting",
            "preview_url": "/api/assets/images/HISTORY_SAGEUK_ROMANCE.png"
        },
        {
            "id": "ISEKAI_OTOME_FANTASY",
            "name": "Fantasy Romance",
            "description": "Dreamy isekai otome style with soft pastels",
            "preview_url": "/api/assets/images/ISEKAI_OTOME_FANTASY.png"
        },
        {
            "id": "MODERN_KOREAN_ROMANCE",
            "name": "Modern Romance",
            "description": "Contemporary K-drama style with warm tones",
            "preview_url": "/api/assets/images/MODERN_KOREAN_ROMANCE.png"
        }
    ]


@router.post("/generate")
async def generate_webtoon_script(request: GenerateWebtoonRequest) -> WebtoonScriptResponse:
    """
    Convert a story into a webtoon script with characters and panels.
    
    Args:
        request: Request with story_id
        
    Returns:
        WebtoonScriptResponse with script_id, characters, and panels
        
    Raises:
        HTTPException: If story not found or conversion fails
    """
    logger.info(f"Generating webtoon script for story: {request.story_id}")
    
    # Check if story exists
    if request.story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")
    
    story_data = stories[request.story_id]
    story_content = story_data["content"]
    
    try:
        # Convert story to webtoon script
        webtoon_script = await webtoon_writer.convert_story_to_script(story_content)
        
        # Generate unique script ID
        script_id = str(uuid.uuid4())
        
        # Store script
        webtoon_scripts[script_id] = {
            "script_id": script_id,
            "story_id": request.story_id,
            "characters": [char.model_dump() for char in webtoon_script.characters],
            "panels": [panel.model_dump() for panel in webtoon_script.panels],
            "character_images": {}
        }
        
        logger.info(f"Webtoon script created: {script_id}")
        logger.info(f"Characters: {len(webtoon_script.characters)}, Panels: {len(webtoon_script.panels)}")
        
        return WebtoonScriptResponse(
            script_id=script_id,
            story_id=request.story_id,
            characters=webtoon_script.characters,
            panels=webtoon_script.panels,
            character_images={}
        )
        
    except Exception as e:
        logger.error(f"Webtoon script generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Webtoon script generation failed: {str(e)}")


@router.post("/character/image/select")
async def select_character_image(script_id: str, image_id: str):
    """
    Mark a character image as selected for scene generation reference.
    
    Args:
        script_id: Webtoon script ID
        image_id: Image ID to select
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If script or image not found
    """
    logger.info(f"Selecting image: {image_id} for script: {script_id}")
    
    # Check if script exists
    if script_id not in webtoon_scripts:
        raise HTTPException(status_code=404, detail="Webtoon script not found")
    
    try:
        script_data = webtoon_scripts[script_id]
        
        # Find the image and update is_selected
        image_found = False
        for character_name, images in script_data["character_images"].items():
            for img in images:
                if img["id"] == image_id:
                    # Deselect all other images for this character
                    for other_img in images:
                        other_img["is_selected"] = False
                    # Select this image
                    img["is_selected"] = True
                    image_found = True
                    logger.info(f"Image {image_id} selected for character {character_name}")
                    break
            if image_found:
                break
        
        if not image_found:
            raise HTTPException(status_code=404, detail="Image not found")
        
        return {"message": "Image selected successfully", "image_id": image_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to select image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to select image: {str(e)}")


@router.post("/character/image")
async def generate_character_image(request: GenerateCharacterImageRequest) -> CharacterImage:
    """
    Generate an image for a character.
    
    Args:
        request: Request with script_id, character_name, description, gender, and image_style
        
    Returns:
        CharacterImage with image URL and metadata
        
    Raises:
        HTTPException: If script not found or image generation fails
    """
    logger.info(f"Generating image for character: {request.character_name}")
    logger.info(f"Gender: {request.gender}, Style: {request.image_style}")
    logger.info(f"Script ID: {request.script_id}")
    logger.info(f"Available scripts: {list(webtoon_scripts.keys())}")
    
    # Check if script exists
    if request.script_id not in webtoon_scripts:
        logger.error(f"Script {request.script_id} not found in storage")
        raise HTTPException(status_code=404, detail="Webtoon script not found")
    
    try:
        # Generate image with gender and style
        image_url = await image_generator.generate_character_image(
            description=request.description,
            character_name=request.character_name,
            gender=request.gender,
            image_style=request.image_style
        )
        
        # Create image record
        image_id = str(uuid.uuid4())
        character_image = CharacterImage(
            id=image_id,
            character_name=request.character_name,
            description=request.description,
            image_url=image_url,
            is_selected=False
        )
        
        # Store image
        image_key = f"{request.script_id}:{request.character_name}"
        if image_key not in character_images:
            character_images[image_key] = []
        
        character_images[image_key].append(character_image.model_dump())
        
        # Update script's character_images
        script_data = webtoon_scripts[request.script_id]
        if request.character_name not in script_data["character_images"]:
            script_data["character_images"][request.character_name] = []
        
        script_data["character_images"][request.character_name].append(character_image.model_dump())
        
        logger.info(f"Character image generated: {image_id}")
        
        return character_image
        
    except Exception as e:
        logger.error(f"Character image generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@router.get("/{script_id}")
async def get_webtoon_script(script_id: str) -> WebtoonScriptResponse:
    """
    Get webtoon script with all generated images.
    
    Args:
        script_id: Unique script identifier
        
    Returns:
        WebtoonScriptResponse with characters, panels, and images
        
    Raises:
        HTTPException: If script not found
    """
    if script_id not in webtoon_scripts:
        raise HTTPException(status_code=404, detail="Webtoon script not found")
    
    script_data = webtoon_scripts[script_id]
    
    return WebtoonScriptResponse(
        script_id=script_data["script_id"],
        story_id=script_data["story_id"],
        characters=[char for char in script_data["characters"]],
        panels=[panel for panel in script_data["panels"]],
        character_images=script_data.get("character_images", {})
    )


@router.get("/character/{script_id}/{character_name}/images")
async def get_character_images(script_id: str, character_name: str) -> List[CharacterImage]:
    """
    Get all generated images for a specific character.
    
    Args:
        script_id: Unique script identifier
        character_name: Name of the character
        
    Returns:
        List of CharacterImage objects
        
    Raises:
        HTTPException: If script not found
    """
    if script_id not in webtoon_scripts:
        raise HTTPException(status_code=404, detail="Webtoon script not found")
    
    image_key = f"{script_id}:{character_name}"
    images = character_images.get(image_key, [])
    
    return [CharacterImage(**img) for img in images]
