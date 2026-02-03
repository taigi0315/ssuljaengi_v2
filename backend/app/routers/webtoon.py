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
import time
from typing import Dict, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
import os

from app.models.story import (
    GenerateWebtoonRequest,
    GenerateCharacterImageRequest,
    GenerateSceneImageRequest,
    WebtoonScriptResponse,
    CharacterImage,
    SceneImage,
    WebtoonScript,
    GenerateSceneImageRequest,
    WebtoonScriptResponse,
    CharacterImage,
    SceneImage,
    PageImage,
    WebtoonScript,
    GenerateShortsRequest,
    ImportCharacterImageRequest,
    WebtoonPanel
)
from app.services.webtoon_writer import webtoon_writer
from app.services.image_generator import image_generator
from app.services.shorts_generator import shorts_generator
from app.models.shorts import ShortsScript
from app. workflows.webtoon_workflow import run_webtoon_workflow
from app.models.video_models import GenerateVideoRequest, VideoPanelData, BubbleData
from app.services.multi_panel_generator import multi_panel_generator
from app.services.panel_composer import group_panels_into_pages


from app.config import get_settings
from app.utils.persistence import JsonStore
from app.prompt.story_genre import STORY_GENRE_PROMPTS
from app.prompt.image_style import VISUAL_STYLE_PROMPTS
from app.services.style_composer import get_legacy_style_with_mood
from app.services.mood_designer import detect_context_from_text, MoodAssignment, mood_designer
from app.services.panel_composer import group_panels_into_pages, calculate_page_statistics, Page
from app.prompt.multi_panel import format_panels_from_webtoon_panels, PanelData, format_multi_panel_prompt
from app.utils.dialogue_formatter import format_dialogue_as_visual_context, get_dominant_scene_emotion
from app.config.enhanced_panel_config import get_enhanced_panel_config, update_enhanced_panel_config, EnhancedPanelConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webtoon", tags=["Webtoon"])

# Initialize persistent storage
settings = get_settings()
webtoon_scripts: JsonStore[dict] = JsonStore(
    os.path.join(settings.data_dir, "webtoon_scripts.json")
)
character_images: JsonStore[List[dict]] = JsonStore(
    os.path.join(settings.data_dir, "character_images.json")
)
scene_images: JsonStore[List[dict]] = JsonStore(
    os.path.join(settings.data_dir, "scene_images.json")
)
page_images: JsonStore[List[dict]] = JsonStore(
    os.path.join(settings.data_dir, "page_images.json")
)

# Import stories from story router
from app.routers.story import stories


@router.get("/image-styles")
async def get_image_styles():
    """
    Get available image/visual styles with metadata.
    These are visual rendering styles (colors, lighting, art style) for images.

    Returns:
        List of image style options with IDs, names, and descriptions
    """
    # Metadata for image styles - provides human-readable info
    IMAGE_STYLE_METADATA = {
        "NO_STYLE": {
            "name": "Default Style",
            "description": "Default AI rendering without specific style"
        },
        "SOFT_ROMANTIC_WEBTOON": {
            "name": "Soft Romantic",
            "description": "Gentle, dreamy, light-filled, ethereal aesthetic"
        },
        "VIBRANT_FANTASY_WEBTOON": {
            "name": "Vibrant Fantasy",
            "description": "Magical, bright, enchanting, colorful style"
        },
        "DRAMATIC_HISTORICAL_WEBTOON": {
            "name": "Dramatic Historical",
            "description": "Moody, elegant, dramatic, candlelit atmosphere"
        },
        "BRIGHT_YOUTHFUL_WEBTOON": {
            "name": "Bright Youthful",
            "description": "Fresh, clean, optimistic, energetic feel"
        },
        "DREAMY_ISEKAI_WEBTOON": {
            "name": "Dreamy Isekai",
            "description": "Ethereal, whimsical, romantic fantasy glow"
        },
        "DARK_SENSUAL_WEBTOON": {
            "name": "Dark Sensual",
            "description": "Intense, dramatic, intimate, mysterious mood"
        },
        "CLEAN_MODERN_WEBTOON": {
            "name": "Clean Modern",
            "description": "Professional, versatile, commercial standard"
        },
        "PAINTERLY_ARTISTIC_WEBTOON": {
            "name": "Painterly Artistic",
            "description": "Artistic, expressive, fine art quality"
        }
    }

    styles = []
    for key in VISUAL_STYLE_PROMPTS.keys():
        metadata = IMAGE_STYLE_METADATA.get(key, {})
        name = metadata.get("name", key.replace("_", " ").title())
        description = metadata.get("description", "Visual style for webtoon art")

        styles.append({
            "id": key,
            "name": name,
            "description": description,
            "preview_url": f"/api/assets/images/image_style/{key}.png"
        })

    return styles


@router.post("/shorts/generate", response_model=ShortsScript)
async def generate_shorts_script(request: GenerateShortsRequest):
    """
    Generate a 6-scene shorts script based on a topic.
    If topic is empty, a random topic will be used.
    """
    topic = request.topic
    if not topic or not topic.strip():
        topic = "random"
    
    return await shorts_generator.generate_script(topic)


@router.get("/genres", response_model=List[dict])
async def get_genres():
    """
    Get available story genres for narrative content creation.
    These define the story/narrative style (setting, dialogue, themes, tropes).
    NOT the visual rendering style - use /image-styles for that.

    Returns a list of genre objects with id, name, description, and preview_url.
    """
    # Metadata for story genres - provides human-readable info
    STORY_GENRE_METADATA = {
        "NO_GENRE": {
            "name": "Free Style",
            "description": "No narrative constraints - write any story"
        },
        "MODERN_ROMANCE_DRAMA": {
            "name": "Modern Romance Drama",
            "description": "Contemporary urban romance with emotional depth"
        },
        "FANTASY_ROMANCE": {
            "name": "Fantasy Romance",
            "description": "Magical worlds, enchanted academies, mystical love"
        },
        "HISTORICAL_PERIOD_ROMANCE": {
            "name": "Historical Period Romance",
            "description": "Joseon-era sageuk with forbidden love and duty"
        },
        "SCHOOL_YOUTH_ROMANCE": {
            "name": "School Youth Romance",
            "description": "Sweet high school/university first love stories"
        },
        "REINCARNATION_FANTASY": {
            "name": "Reincarnation/Isekai Fantasy",
            "description": "Transmigrated into a novel/game world romance"
        },
        "DARK_OBSESSIVE_ROMANCE": {
            "name": "Dark Obsessive Romance",
            "description": "Intense possessive love with psychological depth"
        },
        "WORKPLACE_ROMANCE": {
            "name": "Workplace Romance",
            "description": "Office romance with professional tension"
        },
        "CHILDHOOD_FRIENDS_TO_LOVERS": {
            "name": "Childhood Friends to Lovers",
            "description": "Long friendship evolving into romance"
        }
    }

    genres = []
    for key in STORY_GENRE_PROMPTS.keys():
        metadata = STORY_GENRE_METADATA.get(key, {})
        name = metadata.get("name", key.replace("_", " ").title())
        description = metadata.get("description", "Story genre for webtoon narrative")

        genres.append({
            "id": key,
            "name": name,
            "description": description,
            "preview_url": f"/api/assets/images/genre/{key}.png"
        })

    return genres

@router.post("/generate")
async def generate_webtoon_script(request: GenerateWebtoonRequest) -> WebtoonScriptResponse:
    """
    Convert a story into a webtoon script with characters and panels.
    
    Uses LangGraph workflow with automatic evaluation and rewriting.
    The workflow evaluates the generated script and conditionally rewrites
    it up to 2 times if quality thresholds aren't met.
    
    Enhanced with panel count validation and improved error responses.
    
    Args:
        request: Request with story_id
        
    Returns:
        WebtoonScriptResponse with script_id, characters, and panels
        
    Raises:
        HTTPException: If story not found, conversion fails, or panel count validation fails
    """
    logger.info(f"Generating webtoon script for story: {request.story_id}")

    # Use provided story_content if available, otherwise lookup from storage
    if request.story_content:
        story_content = request.story_content
        logger.info("Using provided story content (manual input)")
    else:
        # Check if story exists
        if request.story_id not in stories:
            raise HTTPException(status_code=404, detail="Story not found")
        story_data = stories[request.story_id]
        story_content = story_data["content"]
    
    try:
        # Use the LangGraph workflow with evaluation and rewriting
        # This automatically evaluates the script and rewrites if needed (max 2 times)
        webtoon_script = await run_webtoon_workflow(
            story=story_content,
            story_genre=request.genre or "MODERN_ROMANCE_DRAMA", # Assuming we need to add genre to request/workflow
            image_style=request.image_style or "SOFT_ROMANTIC_WEBTOON"
        )
        
        # Enhanced panel count validation
        panel_count = len(webtoon_script.panels)
        config = get_enhanced_panel_config()
        genre = request.genre or "MODERN_ROMANCE_DRAMA"
        
        # Log panel count for monitoring (but don't fail the request)
        min_panels, max_panels = config.get_panel_range_for_genre(genre)
        ideal_min, ideal_max = config.get_ideal_panel_range(genre)
        is_ideal = ideal_min <= panel_count <= ideal_max
        is_acceptable = min_panels <= panel_count <= max_panels
        
        if not is_acceptable:
            logger.warning(
                f"Panel count {panel_count} is outside acceptable range {min_panels}-{max_panels} for {genre}, "
                f"but allowing workflow to complete"
            )
        else:
            logger.info(f"Panel count validation passed: {panel_count} panels ({'ideal' if is_ideal else 'acceptable'} for {genre})")
        
        
        # Generate unique script ID
        script_id = str(uuid.uuid4())
        
        # Store script with enhanced metadata
        webtoon_scripts[script_id] = {
            "script_id": script_id,
            "story_id": request.story_id,
            "characters": [char.model_dump() for char in webtoon_script.characters],
            "scenes": [scene.model_dump() for scene in webtoon_script.scenes],
            "panels": [panel.model_dump() for panel in webtoon_script.panels],  # Backward compatibility
            "character_images": {},
            "enhanced_metadata": {
                "panel_count": panel_count,
                "scene_count": len(webtoon_script.scenes),
                "genre": genre,
                "is_ideal_count": is_ideal,
                "generation_timestamp": time.time(),
                "config_version": "enhanced_v1"
            }
        }
        await webtoon_scripts.save()
        
        logger.info(f"Webtoon script created: {script_id}")
        logger.info(f"Characters: {len(webtoon_script.characters)}, Panels: {len(webtoon_script.panels)}")
        
        return WebtoonScriptResponse(
            script_id=script_id,
            story_id=request.story_id,
            characters=webtoon_script.characters,
            panels=webtoon_script.panels,
            character_images={}
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (including our enhanced panel validation errors)
        raise
    except Exception as e:
        logger.error(f"Webtoon script generation failed: {str(e)}", exc_info=True)
        
        # Enhanced error response for general failures
        error_detail = {
            "error_type": "generation_failure",
            "message": f"Webtoon script generation failed: {str(e)}",
            "retryable": True,
            "suggestions": [
                "Check if the story content is valid and readable",
                "Try again with a different genre or image style",
                "Ensure the story has clear narrative structure"
            ]
        }
        
        raise HTTPException(status_code=500, detail=error_detail)


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
        
        await webtoon_scripts.save()
        
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
    
    # Check if script exists, or lazily create for eye-candy/shorts mode
    if request.script_id not in webtoon_scripts:
        if request.script_id.startswith("eye-candy-") or request.script_id.startswith("shorts-"):
            logger.info(f"Creating lazy script context for: {request.script_id}")
            webtoon_scripts[request.script_id] = {
                "script_id": request.script_id,
                "story_id": "mock_story_id",
                "characters": [],
                "panels": [],
                "character_images": {}
            }
            # We don't save immediately here, we'll save when adding the image below
        else:
            logger.error(f"Script {request.script_id} not found in storage")
            raise HTTPException(status_code=404, detail="Webtoon script not found")
    
    
    try:
        # Check if reference image is provided for multimodal generation
        if request.reference_image_url:
            logger.info("Using multimodal generation with reference image")
            logger.info(f"Reference image URL length: {len(request.reference_image_url)}")
            
            # Use multimodal generation with reference
            # Use specific character generation method that supports prompt templates + reference
            image_url, prompt_used = await image_generator.generate_character_image_with_reference(
                description=request.description,
                character_name=request.character_name,
                gender=request.gender,
                image_style=request.image_style,
                reference_image=request.reference_image_url
            )
        else:
            # Use text-only generation (existing code)
            logger.info("Using text-only generation (no reference image)")
            image_url, prompt_used = await image_generator.generate_character_image(
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
            is_selected=False,
            prompt_used=prompt_used
        )
        
        # Store image
        image_key = f"{request.script_id}:{request.character_name}"
        if image_key not in character_images:
            character_images[image_key] = []
        
        character_images[image_key].append(character_image.model_dump())
        await character_images.save()
        
        # Update script's character_images
        script_data = webtoon_scripts[request.script_id]
        if "character_images" not in script_data:
            script_data["character_images"] = {}
            
        if request.character_name not in script_data["character_images"]:
            script_data["character_images"][request.character_name] = []
        
        script_data["character_images"][request.character_name].append(character_image.model_dump())
        await webtoon_scripts.save()
        
        logger.info(f"Character image generated: {image_id}")
        
        return character_image
        
    except Exception as e:
        logger.error(f"Character image generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@router.post("/character/image/import")
async def import_character_image(request: ImportCharacterImageRequest) -> CharacterImage:
    """
    Import an existing character image (e.g. from library) into the current script context.
    
    Args:
        request: Request with script_id, character_name, image_url, description
        
    Returns:
        CharacterImage with new ID
    """
    
    logger.info(f"Importing image for character: {request.character_name}")
    
    # Check if script exists
    if request.script_id not in webtoon_scripts:
        logger.error(f"Script {request.script_id} not found in storage")
        raise HTTPException(status_code=404, detail="Webtoon script not found")
        
    try:
        # Create image record with NEW ID
        image_id = str(uuid.uuid4())
        
        character_image = CharacterImage(
            id=image_id,
            character_name=request.character_name,
            description=request.description,
            image_url=request.image_url,
            is_selected=True,  # Auto-select imported images
            prompt_used="Imported from library"
        )
        
        # Store image in global store
        image_key = f"{request.script_id}:{request.character_name}"
        if image_key not in character_images:
            character_images[image_key] = []
        
        # Deselect others for this character
        for img in character_images[image_key]:
            img["is_selected"] = False
            
        character_images[image_key].append(character_image.model_dump())
        await character_images.save()
        
        # Update script's character_images
        script_data = webtoon_scripts[request.script_id]
        if "character_images" not in script_data:
            script_data["character_images"] = {}
            
        if request.character_name not in script_data["character_images"]:
            script_data["character_images"][request.character_name] = []
            
        # Deselect others in script data too
        for img in script_data["character_images"][request.character_name]:
            img["is_selected"] = False
        
        script_data["character_images"][request.character_name].append(character_image.model_dump())
        await webtoon_scripts.save()
        
        logger.info(f"Character image imported: {image_id}")
        
        return character_image
        
    except Exception as e:
        logger.error(f"Character image import failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image import failed: {str(e)}")


@router.get("/latest")
async def get_latest_webtoon():
    """Get the most recently created webtoon script for testing purposes."""
    # Force reload from disk to ensure we have latest data generated by setup_test_data.py
    # Unconditionally reload to be safe
    logger.info(f"Reloading webtoon scripts from {webtoon_scripts.file_path}")
    webtoon_scripts._load()
        
    scripts = list(webtoon_scripts.values())
    logger.info(f"Retrieve latest: found {len(scripts)} scripts in {webtoon_scripts.file_path}")
    
    if not scripts:
        raise HTTPException(status_code=404, detail="No webtoon scripts found")
    
    # Sort by created_at desc
    sorted_scripts = sorted(
        scripts, 
        key=lambda x: x.get('created_at', ''), 
        reverse=True
    )
    
    return sorted_scripts[0]



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
    
    # Populate scene_images
    scene_images_dict = {}
    for key, val in scene_images.items():
         if key.startswith(f"{script_id}:"):
             try:
                 p_num = int(key.split(":")[-1])
                 scene_images_dict[p_num] = val
             except ValueError:
                 pass
    
    # Populate page_images
    page_images_dict = {}
    for key, val in page_images.items():
         if key.startswith(f"{script_id}:"):
             try:
                 p_num = int(key.split(":")[-1])
                 page_images_dict[p_num] = val
             except ValueError:
                 pass

    return WebtoonScriptResponse(
        script_id=script_data["script_id"],
        story_id=script_data["story_id"],
        characters=[char for char in script_data["characters"]],
        panels=[panel for panel in script_data["panels"]],
        character_images=script_data.get("character_images", {}),
        scene_images=scene_images_dict,
        page_images=page_images_dict
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




@router.post("/scene/image")
async def generate_scene_image(request: "GenerateSceneImageRequest"):
    """
    Generate an image for a scene/panel.
    
    Args:
        request: Request with script_id, panel_number, visual_prompt, and genre
        
    Returns:
        SceneImage with image URL and metadata
        
    Raises:
        HTTPException: If script not found or image generation fails
    """
    from app.models.story import GenerateSceneImageRequest, SceneImage
    from app.prompt.scene_image import SCENE_IMAGE_TEMPLATE, sfx_to_prompt_enhancement
    
    logger.info(f"Generating scene image for panel: {request.panel_number}")
    logger.info(f"Script ID: {request.script_id}")
    logger.info(f"Genre: {request.genre}")
    
    # Check if script exists
    if request.script_id not in webtoon_scripts:
        logger.error(f"Script {request.script_id} not found in storage")
        raise HTTPException(status_code=404, detail="Webtoon script not found")
    
    try:
        script_data = webtoon_scripts[request.script_id]
        characters = script_data["characters"]
        panels = script_data["panels"]
        character_images_in_script = script_data.get("character_images", {})
        
        # Find active characters for this panel and build character descriptions
        character_descriptions = []
        active_char_names = []
        
        # Panel metadata containers
        panel_metadata = {
            "shot_type": "Wide Shot",
            "composition_notes": "Standard composition",
            "environment_focus": "Background",
            "environment_details": "Detailed environment",
            "atmospheric_conditions": "Standard lighting",
            "character_frame_percentage": 40,
            "environment_frame_percentage": 60,
            "character_placement_and_action": "Characters in scene",
            "emotional_tone": "neutral",
            "negative_prompt": "worst quality, low quality"
        }
        
        for panel in panels:
            if panel["panel_number"] == request.panel_number:
                # Override active characters if provided in request
                if request.active_character_names is not None:
                     active_char_names = request.active_character_names
                     logger.info(f"Using overridden active characters: {active_char_names}")
                else:
                     active_char_names = panel.get("active_character_names", [])
                
                # Extract cinematic fields from panel
                panel_metadata["shot_type"] = panel.get("shot_type", "Wide Shot")
                panel_metadata["composition_notes"] = panel.get("composition_notes", "Standard composition")
                panel_metadata["environment_focus"] = panel.get("environment_focus", "Background")
                panel_metadata["environment_details"] = panel.get("environment_details", "Detailed environment")
                panel_metadata["atmospheric_conditions"] = panel.get("atmospheric_conditions", "Standard lighting")
                panel_metadata["character_frame_percentage"] = panel.get("character_frame_percentage", 40)
                panel_metadata["environment_frame_percentage"] = panel.get("environment_frame_percentage", 60)
                panel_metadata["character_placement_and_action"] = panel.get("character_placement_and_action", "Characters in scene")
                panel_metadata["emotional_tone"] = panel.get("emotional_tone", "neutral")
                panel_metadata["negative_prompt"] = panel.get("negative_prompt", "worst quality, low quality")

                # Extract emotional intensity for mood-aware styling (Phase 2.4 Integration)
                panel_metadata["emotional_intensity"] = panel.get("emotional_intensity", 5)
                panel_metadata["visual_prompt"] = panel.get("visual_prompt", "")
                panel_metadata["story_beat"] = panel.get("story_beat", "")

                # Extract SFX effects and convert to AI-readable descriptions
                sfx_effects = panel.get("sfx_effects", [])
                if sfx_effects:
                    # Use the new sfx_to_prompt_enhancement function for better AI understanding
                    panel_metadata["sfx_description"] = sfx_to_prompt_enhancement(sfx_effects)
                    logger.info(f"SFX effects found: {len(sfx_effects)} - Enhanced for image gen")
                else:
                    panel_metadata["sfx_description"] = "None"
                
                logger.info(f"Active characters in panel {request.panel_number}: {active_char_names}")
                
                for char_name in active_char_names:
                    for char in characters:
                        if char["name"] == char_name:
                            # Use the programmatically built visual_description
                            desc = f"- {char_name}: {char.get('gender', 'unknown')} character (reference image provided - appearance locked)"
                            character_descriptions.append(desc)
                            break
                break
        
        # Collect selected reference images for active characters
        reference_images = []
        for char_name in active_char_names:
            images_for_char = character_images_in_script.get(char_name, [])
            for img in images_for_char:
                if img.get("is_selected", False):
                    image_url = img.get("image_url", "")
                    if image_url and image_url.startswith("data:"):
                        reference_images.append(image_url)
                        logger.info(f"Added reference image for {char_name}")
                    break  # Only take the selected one per character
        
        logger.info(f"Found {len(reference_images)} selected character reference images")
        
        # Build character description text
        if character_descriptions:
            character_desc_text = "\n".join(character_descriptions)
        else:
            character_desc_text = "No characters should be visible in this panel."

        # High-priority character presence rules (prevents character-overuse)
        shot_type_raw = str(panel_metadata.get("shot_type", "")).lower()
        has_visible_characters = bool(active_char_names)
        if not has_visible_characters:
            character_presence_instructions = (
                "- This panel MUST contain NO visible people/characters.\n"
                "- Focus on environment, atmosphere, or a meaningful object/prop that communicates the story beat.\n"
                "- Do NOT add random characters in the background.\n"
                "- If any human body parts appear, it is incorrect."
            )
            # Ensure placement text doesn't accidentally ask for characters
            panel_metadata["character_placement_and_action"] = "No characters visible; environment/object-only storytelling panel"
        else:
            character_presence_instructions = (
                f"- Visible characters (or identifiable body parts) in this panel: {', '.join(active_char_names)}.\n"
                "- Avoid generic 'two characters staring at each other' staging unless explicitly required by the story beat.\n"
                "- Use the shot type to emphasize the moment (mouth/hands/eyes for detail or extreme close-ups; reactions for close-ups; context for wide shots).\n"
                "- Do NOT turn the frame into a centered studio portrait."
            )

        logger.info(f"Character descriptions for prompt:\n{character_desc_text}")

        # Extract dialogue from the panel and convert to visual context
        # This informs character expressions WITHOUT rendering text bubbles
        dialogue_visual_context = ""
        scene_emotion = ""
        for panel in panels:
            if panel["panel_number"] == request.panel_number:
                dialogue_list = panel.get("dialogue", [])
                if dialogue_list:
                    # Convert dialogue to visual expression context
                    dialogue_visual_context = format_dialogue_as_visual_context(dialogue_list)
                    scene_emotion = get_dominant_scene_emotion(dialogue_list)
                    logger.info(f"Dialogue visual context generated for panel {request.panel_number}")
                    logger.info(f"Scene emotion: {scene_emotion}")
                break

        if not dialogue_visual_context:
            dialogue_visual_context = "No specific expression guidance - use neutral/appropriate expressions based on scene context"

        # Build final prompt using the template
        final_prompt = SCENE_IMAGE_TEMPLATE.format(
            character_description=character_desc_text,
            character_presence_instructions=character_presence_instructions,
            visual_prompt=request.visual_prompt,
            negative_prompt=panel_metadata["negative_prompt"],
            shot_type=panel_metadata["shot_type"],
            composition_notes=panel_metadata["composition_notes"],
            character_frame_percentage=panel_metadata["character_frame_percentage"],
            environment_frame_percentage=panel_metadata["environment_frame_percentage"],
            environment_focus=panel_metadata["environment_focus"],
            environment_details=panel_metadata["environment_details"],
            atmospheric_conditions=panel_metadata["atmospheric_conditions"],
            sfx_description=panel_metadata.get("sfx_description", "No special visual effects for this scene"),
            emotional_tone=panel_metadata["emotional_tone"],
            character_placement_and_action=panel_metadata["character_placement_and_action"],
            dialogue_visual_context=dialogue_visual_context
        )
        
        logger.info(f"Final scene prompt (first 500 chars): {final_prompt[:500]}")

        # Phase 2.4 Integration: Mood-Aware Style Composition
        # Detect scene context from panel content for mood assignment
        combined_text_for_mood = " ".join(filter(None, [
            panel_metadata.get("visual_prompt", ""),
            panel_metadata.get("story_beat", ""),
            character_desc_text
        ]))

        # Add dialogue text to context detection
        for panel in panels:
            if panel["panel_number"] == request.panel_number:
                dialogue_list = panel.get("dialogue", [])
                if dialogue_list:
                    for d in dialogue_list:
                        if isinstance(d, dict):
                            combined_text_for_mood += " " + d.get("text", "")
                break

        # Detect emotional context and compose style with mood
        detected_context, context_confidence = detect_context_from_text(combined_text_for_mood)
        emotional_intensity = panel_metadata.get("emotional_intensity", 5)

        logger.info(f"Mood detection - context: {detected_context} (confidence: {context_confidence:.2f}), intensity: {emotional_intensity}")

        # Compose style with mood modifiers (enhances base style with per-scene mood)
        composed_style = get_legacy_style_with_mood(
            legacy_style_key=request.genre,
            emotional_intensity=emotional_intensity,
            scene_context=detected_context
        )

        logger.info(f"Composed style with mood (first 200 chars): {composed_style[:200]}...")

        # Append composed style to the final prompt for image generation
        # This incorporates mood-specific color temperature, lighting, and special effects
        final_prompt = f"{final_prompt}\n\n[VISUAL STYLE & MOOD]\n{composed_style}"

        logger.info(f"Final prompt with mood-enhanced style (last 300 chars): ...{final_prompt[-300:]}")

        # Generate image using the appropriate method
        # Note: Style is now embedded in final_prompt, image_style param is for logging/reference only
        if reference_images:
            # Use multimodal generation with reference images
            logger.info(f"Using multimodal generation with {len(reference_images)} reference images")
            image_url = await image_generator.generate_scene_image_with_references(
                prompt=final_prompt,
                reference_images=reference_images,
                image_style=request.genre  # For logging - actual style is in prompt
            )
        else:
            # Fallback to text-only generation
            logger.info("No reference images, using text-only generation")
            image_url = await image_generator.generate_scene_image(
                prompt=final_prompt,
                image_style=request.genre  # For logging - actual style is in prompt
            )
        
        # Create image record
        image_id = str(uuid.uuid4())
        image_key = f"{request.script_id}:{request.panel_number}"
        is_first_image = image_key not in scene_images or not scene_images[image_key]
        
        scene_image = SceneImage(
            id=image_id,
            panel_number=request.panel_number,
            image_url=image_url,
            prompt_used=final_prompt,
            is_selected=is_first_image
        )
        
        if image_key in scene_images:
            for img in scene_images[image_key]:
                img["is_selected"] = False
        else:
            scene_images[image_key] = []
        
        scene_images[image_key].append(scene_image.model_dump())
        await scene_images.save()
        
        # Sync to webtoon_scripts for persistence
        if request.script_id in webtoon_scripts:
            script_data = webtoon_scripts[request.script_id]
            if "scene_images" not in script_data:
                script_data["scene_images"] = {}
            
            # Update the scene_images in the script object
            script_data["scene_images"][str(request.panel_number)] = scene_images[image_key]
            await webtoon_scripts.save()
            logger.info(f"Synced scene image to webtoon script {request.script_id}")

        logger.info(f"Scene image generated: {image_id}")
        
        return scene_image
        
    except Exception as e:
        logger.error(f"Scene image generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@router.get("/{script_id}/layout")
async def get_script_layout(script_id: str):
    """
    Get the recommended page layout for a script.
    
    Args:
        script_id: Webtoon script ID
        
    Returns:
        List of Page objects containing grouped panels
    """
    if script_id not in webtoon_scripts:
        raise HTTPException(status_code=404, detail="Webtoon script not found")
        
    try:
        script_data = webtoon_scripts[script_id]
        panels = [WebtoonPanel(**p) for p in script_data["panels"]]
        
        # Use PanelComposer to group panels
        pages = group_panels_into_pages(panels)
        
        return [page.to_dict() for page in pages]
        
    except Exception as e:
        logger.error(f"Layout generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Layout generation failed: {str(e)}")


class GeneratePageImageRequest(BaseModel):
    script_id: str
    page_number: int
    panel_indices: List[int]
    style_modifiers: Optional[List[str]] = None


@router.post("/page/generate")
async def generate_page_image(request: GeneratePageImageRequest):
    """
    Generate a multi-panel page image with enhanced size limits.
    
    Respects the enhanced panel configuration for multi-panel size limits
    and provides detailed error responses for validation failures.
    
    Args:
        request: Request with script_id, page panels, and style
        
    Returns:
        Data URL of the generated image
        
    Raises:
        HTTPException: If validation fails or generation errors occur
    """
    if request.script_id not in webtoon_scripts:
        raise HTTPException(status_code=404, detail="Webtoon script not found")
        
    try:
        # Enhanced validation using configuration
        config = get_enhanced_panel_config()
        panel_count = len(request.panel_indices)
        
        # Validate multi-panel size limits
        if panel_count > config.max_multi_panel_size:
            error_detail = {
                "error_type": "multi_panel_size_exceeded",
                "message": f"Requested {panel_count} panels exceeds the maximum of {config.max_multi_panel_size} panels per multi-panel image",
                "requested_panels": panel_count,
                "maximum_allowed": config.max_multi_panel_size,
                "suggestions": [
                    f"Split into multiple requests with max {config.max_multi_panel_size} panels each",
                    "Use single-panel generation for better image quality",
                    "Consider using the automatic page grouping endpoint instead"
                ],
                "retryable": False
            }
            logger.warning(f"Multi-panel size validation failed: {error_detail}")
            raise HTTPException(status_code=422, detail=error_detail)
        
        script_data = webtoon_scripts[request.script_id]
        all_panels = [WebtoonPanel(**p) for p in script_data["panels"]]
        
        # Extract panels for this page
        page_panels = []
        invalid_indices = []
        for idx in request.panel_indices:
            if 0 <= idx < len(all_panels):
                page_panels.append(all_panels[idx])
            else:
                invalid_indices.append(idx)
        
        if invalid_indices:
            error_detail = {
                "error_type": "invalid_panel_indices",
                "message": f"Invalid panel indices: {invalid_indices}",
                "invalid_indices": invalid_indices,
                "valid_range": f"0-{len(all_panels)-1}",
                "total_panels": len(all_panels),
                "retryable": False
            }
            raise HTTPException(status_code=400, detail=error_detail)
        
        if not page_panels:
            error_detail = {
                "error_type": "no_valid_panels",
                "message": "No valid panels specified for page generation",
                "retryable": False
            }
            raise HTTPException(status_code=400, detail=error_detail)
            
        # Get style from script or request
        style_desc = "Vertical Webtoon Style, " + (request.style_modifiers[0] if request.style_modifiers else "High Quality")
        
        # Collect reference images for characters in these panels
        reference_images = []
        character_images_in_script = script_data.get("character_images", {})
        
        processed_chars = set()
        for p in page_panels:
            if p.active_character_names:
                for name in p.active_character_names:
                    if name in character_images_in_script and name not in processed_chars:
                        images_list = character_images_in_script[name]
                        if images_list:
                            # Find selected image or use the last one
                            selected_img = next((img for img in images_list if img.get("is_selected")), images_list[-1])
                            img_url = selected_img.get("image_url")
                            
                            if img_url:
                                reference_images.append(img_url)
                                processed_chars.add(name)
                            
        logger.info(f"Using {len(reference_images)} reference images for page generation")
        logger.info(f"Generating multi-panel page with {panel_count} panels (within limit of {config.max_multi_panel_size})")

        # Generate image
        image_url = await multi_panel_generator.generate_multi_panel_page(
            panels=page_panels,
            style_description=style_desc,
            style_modifiers=request.style_modifiers,
            reference_images=reference_images
        )
        
        # Store in page_images
        # Key: script_id:page_number
        image_key = f"{request.script_id}:{request.page_number}"
        if image_key in page_images:
            for img in page_images[image_key]:
                img["is_selected"] = False
        else:
            page_images[image_key] = []
            
        # Create PageImage record with enhanced metadata
        image_id = str(uuid.uuid4())
        page_image = PageImage(
            id=image_id,
            page_number=request.page_number,
            panel_indices=request.panel_indices,
            image_url=image_url,
            is_selected=True # New generated image is selected by default
        )
            
        # Add to list
        page_images[image_key].append(page_image.model_dump())
        await page_images.save()

        # Sync to webtoon_scripts for persistence with enhanced metadata
        if request.script_id in webtoon_scripts:
            script_data = webtoon_scripts[request.script_id]
            if "page_images" not in script_data:
                script_data["page_images"] = {}
            
            # Update the page_images in the script object
            script_data["page_images"][str(request.page_number)] = page_images[image_key]
            
            # Add enhanced metadata
            if "enhanced_metadata" not in script_data:
                script_data["enhanced_metadata"] = {}
            script_data["enhanced_metadata"]["last_page_generation"] = {
                "timestamp": time.time(),
                "panel_count": panel_count,
                "within_size_limits": True,
                "max_allowed": config.max_multi_panel_size
            }
            
            await webtoon_scripts.save()
            logger.info(f"Synced page image to webtoon script {request.script_id}")
        
        logger.info(f"Page image generated and saved: {image_id}")
        
        return page_image
        
    except HTTPException:
        # Re-raise HTTP exceptions (including our enhanced validation errors)
        raise
    except Exception as e:
        logger.error(f"Page generation failed: {str(e)}", exc_info=True)
        
        # Enhanced error response for general failures
        error_detail = {
            "error_type": "page_generation_failure",
            "message": f"Multi-panel page generation failed: {str(e)}",
            "retryable": True,
            "suggestions": [
                "Try reducing the number of panels in the request",
                "Check if all panel indices are valid",
                "Ensure character images are properly selected"
            ]
        }
        
        raise HTTPException(status_code=500, detail=error_detail)

        scene_images[image_key].append(scene_image.model_dump())
        await scene_images.save()
        
        logger.info(f"Scene image generated: {image_id}")
        
        return scene_image
        
    except Exception as e:
        logger.error(f"Scene image generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scene image generation failed: {str(e)}")


@router.post("/scene/image/select")
async def select_scene_image(script_id: str, panel_number: int, image_id: str):
    """
    Mark a scene image as selected.
    
    Args:
        script_id: Webtoon script ID
        panel_number: Panel number
        image_id: Image ID to select
        
    Returns:
        Success message
    """
    image_key = f"{script_id}:{panel_number}"
    
    if image_key not in scene_images:
        raise HTTPException(status_code=404, detail="No images found for this scene")
    
    image_found = False
    for img in scene_images[image_key]:
        if img["id"] == image_id:
            # Deselect all others
            for other in scene_images[image_key]:
                other["is_selected"] = False
            img["is_selected"] = True
            image_found = True
            break
    
    if image_found:
        await scene_images.save()
    
    if not image_found:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return {"message": "Scene image selected", "image_id": image_id}


@router.get("/scene/{script_id}/{panel_number}/images")
async def get_scene_images(script_id: str, panel_number: int):
    """
    Get all generated images for a specific scene/panel.
    
    Args:
        script_id: Webtoon script ID
        panel_number: Panel number
        
    Returns:
        List of SceneImage objects
    """
    from app.models.story import SceneImage
    
    image_key = f"{script_id}:{panel_number}"
    images = scene_images.get(image_key, [])
    
    return [SceneImage(**img) for img in images]


@router.post("/video/convert-to-mp4")
async def convert_video_to_mp4(
    file: UploadFile = File(...)
):
    """
    Convert WebM video to MP4 format using ffmpeg.
    
    This endpoint accepts a WebM file and returns an MP4 file
    suitable for YouTube Shorts and other platforms.
    
    Args:
        file: WebM video file upload
        
    Returns:
        MP4 video file as streaming response
        
    Raises:
        HTTPException: If conversion fails or ffmpeg not available
    """
    import subprocess
    import tempfile
    import os
    from fastapi.responses import FileResponse
    
    # Validate file type
    if not file.filename.endswith('.webm'):
        raise HTTPException(status_code=400, detail="Only WebM files are supported")
    
    # Create temp files
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, "input.webm")
    output_path = os.path.join(temp_dir, "output.mp4")
    
    try:
        # Save uploaded file
        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Converting WebM to MP4: {len(content)} bytes")
        
        # Run ffmpeg conversion with high quality settings
        # -c:v libx264 - Use H.264 codec (widely compatible)
        # -crf 18 - High quality (lower = better, 18 is visually lossless)
        # -preset slow - Better compression (slower encoding)
        # -c:a aac - AAC audio codec
        # -b:a 192k - Audio bitrate
        # -movflags +faststart - Optimize for web streaming
        cmd = [
            "ffmpeg", "-y",  # Overwrite output
            "-i", input_path,
            "-c:v", "libx264",
            "-profile:v", "high",
            "-level", "4.0",
            "-crf", "18",
            "-preset", "slow",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            "-pix_fmt", "yuv420p",  # Compatibility
            output_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Video conversion failed: {result.stderr[:500]}"
            )
        
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Output file not created")
        
        output_size = os.path.getsize(output_path)
        logger.info(f"MP4 conversion successful: {output_size} bytes")
        
        # Return the MP4 file
        return FileResponse(
            output_path,
            media_type="video/mp4",
            filename="webtoon_video.mp4",
            background=BackgroundTask(cleanup_temp_files, temp_dir)
        )
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Conversion timed out")
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="FFmpeg not found. Please install ffmpeg on the server."
        )
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def cleanup_temp_files(temp_dir: str):
    """Clean up temporary files after response is sent."""
    import shutil
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        logger.warning(f"Failed to cleanup temp dir: {e}")


def cleanup_video_file(file_path: str):
    """Clean up video file after response is sent."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.warning(f"Failed to cleanup video file: {e}")



@router.post("/page/image/select")
async def select_page_image(script_id: str, image_id: str):
    """
    Mark a page image as selected for the webtoon.
    
    Args:
        script_id: Webtoon script ID
        image_id: Image ID to select
        
    Returns:
        Success message
    """
    logger.info(f"Selecting page image: {image_id} for script: {script_id}")
    
    # Check if script exists
    if script_id not in webtoon_scripts:
        raise HTTPException(status_code=404, detail="Webtoon script not found")
        
    try:
        # Iterate over all page entries for this script
        image_found = False
        target_page_number = -1
        
        # Keys in page_images are "script_id:page_number"
        # Since we don't know the page number from the request (only image_id),
        # we have to search all keys for this script.
        for key, images in page_images.items():
            if key.startswith(f"{script_id}:"):
                for img in images:
                    if img["id"] == image_id:
                        target_page_number = img["page_number"]
                        image_found = True
                        break
            if image_found:
                break
        
        if not image_found:
             raise HTTPException(status_code=404, detail="Page image not found")
             
        # Now update the specific list
        page_key = f"{script_id}:{target_page_number}"
        if page_key in page_images:
            images = page_images[page_key]
            for img in images:
                img["is_selected"] = (img["id"] == image_id)
            
            await page_images.save()
            
            # Sync to webtoon_scripts for persistence
            if script_id in webtoon_scripts:
                script_data = webtoon_scripts[script_id]
                if "page_images" not in script_data:
                    script_data["page_images"] = {}
                script_data["page_images"][str(target_page_number)] = images
                await webtoon_scripts.save()
                logger.info(f"Synced page image selection to webtoon script {script_id}")
            
        return {"message": "Page image selected successfully", "image_id": image_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to select page image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to select page image: {str(e)}")


@router.post("/video/generate")
async def generate_video_backend(
    request: "GenerateVideoRequest"
):
    """
    Generate MP4 video from panels with dialogue bubbles using backend FFmpeg.
    
    This endpoint generates high-quality MP4 video directly on the server,
    bypassing browser limitations for better quality output.
    
    Args:
        request: GenerateVideoRequest with script_id and panels data
        
    Returns:
        MP4 video file as streaming response
        
    Raises:
        HTTPException: If video generation fails
    """
    from app.services.video_service import video_service
    
    logger.info(f"Generating video for script: {request.script_id}")
    logger.info(f"Panels: {len(request.panels)}")
    
    try:
        # Convert request panels to VideoPanelData
        panels = []
        for p in request.panels:
            bubbles = [
                BubbleData(
                    text=b.text, 
                    x=b.x, 
                    y=b.y, 
                    width=b.width, 
                    height=b.height, 
                    character_name=b.character_name
                ) 
                for b in p.bubbles
            ]
            
            # Debug log for first bubble of first panel
            if p.panel_number == 1 and bubbles:
                logger.info(f"First bubble data: text='{bubbles[0].text}', char='{bubbles[0].character_name}'")
            panels.append(VideoPanelData(
                panel_number=p.panel_number,
                image_url=p.image_url,
                bubbles=bubbles
            ))
        
        # Generate video
        video_path = video_service.generate_video(panels)
        
        if not os.path.exists(video_path):
            raise HTTPException(status_code=500, detail="Video file not created")
        
        file_size = os.path.getsize(video_path)
        logger.info(f"Video generated: {video_path} ({file_size / 1024:.1f} KB)")
        
        return FileResponse(
            video_path,
            media_type="video/mp4",
            filename=f"webtoon_{request.script_id[:8]}.mp4",
            background=BackgroundTask(cleanup_video_file, video_path)
        )
        
    except Exception as e:
        logger.error(f"Video generation error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{script_id}/mood-preview")
async def preview_mood_assignments(script_id: str):
    """
    Preview mood assignments for all panels in a webtoon script.

    This endpoint analyzes panels and returns the mood that would be
    applied during image generation. Useful for debugging and testing
    the mood system.

    Args:
        script_id: Webtoon script ID

    Returns:
        List of mood assignments for each panel with:
        - panel_number
        - emotional_intensity
        - detected_context
        - mood_settings (color_temperature, saturation, lighting, effects)
        - composed_style_preview (first 200 chars of composed style)
    """
    from app.models.story import WebtoonPanel

    if script_id not in webtoon_scripts:
        raise HTTPException(status_code=404, detail="Webtoon script not found")

    script_data = webtoon_scripts[script_id]
    panels = script_data.get("panels", [])

    mood_previews = []

    for panel_data in panels:
        # Build combined text for context detection
        combined_text = " ".join(filter(None, [
            panel_data.get("visual_prompt", ""),
            panel_data.get("story_beat", ""),
        ]))

        # Add dialogue text
        dialogue_list = panel_data.get("dialogue", [])
        if dialogue_list:
            for d in dialogue_list:
                if isinstance(d, dict):
                    combined_text += " " + d.get("text", "")

        # Detect context
        detected_context, confidence = detect_context_from_text(combined_text)
        emotional_intensity = panel_data.get("emotional_intensity", 5)

        # Create WebtoonPanel for mood assignment
        panel = WebtoonPanel(**panel_data)

        # Get mood assignment using the mood designer
        assignment = mood_designer.assign_moods([panel])[0] if mood_designer else None

        # Preview the composed style (first 200 chars)
        composed_style = get_legacy_style_with_mood(
            legacy_style_key="SOFT_ROMANTIC_WEBTOON",  # Default style for preview
            emotional_intensity=emotional_intensity,
            scene_context=detected_context
        )

        mood_preview = {
            "panel_number": panel_data.get("panel_number"),
            "emotional_intensity": emotional_intensity,
            "detected_context": detected_context,
            "context_confidence": round(confidence, 2),
            "mood_name": assignment.mood.name if assignment else "unknown",
            "mood_settings": {
                "color_temperature": assignment.mood.color_temperature.value if assignment else "neutral",
                "saturation": assignment.mood.saturation.value if assignment else "normal",
                "lighting_mood": assignment.mood.lighting_mood.value if assignment else "balanced",
                "special_effects": [e.value for e in assignment.mood.special_effects] if assignment else [],
            } if assignment else None,
            "reasoning": assignment.reasoning if assignment else "",
            "composed_style_preview": composed_style[:200] + "..." if len(composed_style) > 200 else composed_style,
        }

        mood_previews.append(mood_preview)

    return {
        "script_id": script_id,
        "total_panels": len(panels),
        "mood_assignments": mood_previews
    }


# ============================================================================
# Phase 3.3: Multi-Panel Page Generation
# ============================================================================

@router.post("/{script_id}/pages/generate")
async def generate_pages_for_script(script_id: str, image_style: str = "SOFT_ROMANTIC_WEBTOON"):
    """
    Generate multi-panel pages for a webtoon script.

    This endpoint groups panels into pages and returns page layout information.
    Use this to plan the multi-panel generation before generating images.

    Args:
        script_id: Webtoon script ID
        image_style: Image style to use for generation

    Returns:
        Page groupings with layout information and statistics
    """
    if script_id not in webtoon_scripts:
        raise HTTPException(status_code=404, detail="Webtoon script not found")

    script_data = webtoon_scripts[script_id]
    panels_data = script_data.get("panels", [])

    if not panels_data:
        raise HTTPException(status_code=400, detail="Script has no panels")

    # Convert to WebtoonPanel objects
    from app.models.story import WebtoonPanel
    panels = [WebtoonPanel(**p) for p in panels_data]

    # Group panels into pages
    pages = group_panels_into_pages(panels)
    stats = calculate_page_statistics(pages)

    # Build response
    page_data = []
    for page in pages:
        page_info = page.to_dict()
        page_info["panels"] = [
            {
                "panel_number": p.panel_number,
                "shot_type": p.shot_type,
                "emotional_intensity": p.emotional_intensity,
                "story_beat": p.story_beat,
            }
            for p in page.panels
        ]
        page_data.append(page_info)

    return {
        "script_id": script_id,
        "pages": page_data,
        "statistics": stats
    }


@router.post("/{script_id}/page/{page_number}/image")
async def generate_page_image(
    script_id: str,
    page_number: int,
    image_style: str = "SOFT_ROMANTIC_WEBTOON"
):
    """
    Generate a multi-panel page image with enhanced validation.

    This endpoint generates an image for a specific page (which may contain
    multiple panels) in a single API call. Respects enhanced panel configuration
    for size limits and provides detailed error responses.

    Args:
        script_id: Webtoon script ID
        page_number: Page number to generate (1-indexed)
        image_style: Image style to use

    Returns:
        Generated page image with metadata
        
    Raises:
        HTTPException: If validation fails or generation errors occur
    """
    from app.models.story import WebtoonPanel, SceneImage

    if script_id not in webtoon_scripts:
        raise HTTPException(status_code=404, detail="Webtoon script not found")

    script_data = webtoon_scripts[script_id]
    panels_data = script_data.get("panels", [])
    characters = script_data.get("characters", [])
    character_images_in_script = script_data.get("character_images", {})

    if not panels_data:
        error_detail = {
            "error_type": "no_panels_found",
            "message": "Script has no panels to generate pages from",
            "script_id": script_id,
            "retryable": False
        }
        raise HTTPException(status_code=400, detail=error_detail)

    # Convert to WebtoonPanel objects and group
    panels = [WebtoonPanel(**p) for p in panels_data]
    pages = group_panels_into_pages(panels)

    # Find the requested page
    target_page = None
    for page in pages:
        if page.page_number == page_number:
            target_page = page
            break

    if target_page is None:
        error_detail = {
            "error_type": "page_not_found",
            "message": f"Page {page_number} not found in script",
            "requested_page": page_number,
            "total_pages": len(pages),
            "available_pages": [p.page_number for p in pages],
            "retryable": False
        }
        raise HTTPException(status_code=404, detail=error_detail)

    # Enhanced validation using configuration
    config = get_enhanced_panel_config()
    
    # Validate multi-panel size limits for multi-panel pages
    if not target_page.is_single_panel and target_page.panel_count > config.max_multi_panel_size:
        error_detail = {
            "error_type": "page_exceeds_multi_panel_limit",
            "message": f"Page {page_number} contains {target_page.panel_count} panels, exceeding the maximum of {config.max_multi_panel_size} panels per multi-panel image",
            "page_number": page_number,
            "panel_count": target_page.panel_count,
            "maximum_allowed": config.max_multi_panel_size,
            "layout_type": target_page.layout_type.value,
            "suggestions": [
                "Use single-panel generation for individual panels",
                "Adjust panel grouping configuration",
                "Generate panels individually and combine manually"
            ],
            "retryable": False
        }
        logger.warning(f"Page multi-panel size validation failed: {error_detail}")
        raise HTTPException(status_code=422, detail=error_detail)

    logger.info(f"Generating page {page_number} with {target_page.panel_count} panels")
    logger.info(f"Layout type: {target_page.layout_type.value}")
    logger.info(f"Within enhanced limits: panel_count={target_page.panel_count} <= max={config.max_multi_panel_size}")

    # Collect character references for panels on this page
    reference_images = []
    active_chars = set()
    for panel in target_page.panels:
        for char_name in panel.active_character_names:
            active_chars.add(char_name)

    for char_name in active_chars:
        images_for_char = character_images_in_script.get(char_name, [])
        for img in images_for_char:
            if img.get("is_selected", False):
                image_url = img.get("image_url", "")
                if image_url and image_url.startswith("data:"):
                    reference_images.append(image_url)
                    logger.info(f"Added reference image for {char_name}")
                break

    # Build character reference descriptions
    char_refs = {}
    for char in characters:
        if char["name"] in active_chars:
            char_refs[char["name"]] = f"{char.get('gender', 'character')} (reference image provided)"

    # Get style description from legacy style
    style_prompt = VISUAL_STYLE_PROMPTS.get(image_style, "")
    style_description = "soft romantic manhwa style" if not style_prompt else style_prompt[:200]

    # Build panel data with mood context
    panel_data_list = []
    for panel in target_page.panels:
        # Detect context for mood
        combined_text = f"{panel.visual_prompt} {panel.story_beat}"
        for d in (panel.dialogue or []):
            if isinstance(d, dict):
                combined_text += f" {d.get('text', '')}"

        detected_context, _ = detect_context_from_text(combined_text)

        panel_data_list.append(PanelData(
            panel_number=panel.panel_number,
            shot_type=panel.shot_type,
            subject=", ".join(panel.active_character_names) or "scene",
            description=panel.visual_prompt,
            characters=panel.active_character_names,
            emotional_intensity=panel.emotional_intensity,
            mood_context=detected_context
        ))

    # Format the multi-panel prompt
    prompt = format_multi_panel_prompt(
        panels=panel_data_list,
        style_description=style_description,
        style_keywords="High resolution, clean line art, professional webtoon quality, consistent character appearance",
        character_references=char_refs if char_refs else None
    )

    # Add mood-enhanced style to prompt
    avg_intensity = sum(p.emotional_intensity for p in panel_data_list) // len(panel_data_list)
    dominant_context = panel_data_list[0].mood_context if panel_data_list else "neutral"
    composed_style = get_legacy_style_with_mood(
        legacy_style_key=image_style,
        emotional_intensity=avg_intensity,
        scene_context=dominant_context
    )
    prompt = f"{prompt}\n\n[VISUAL STYLE & MOOD]\n{composed_style}"

    logger.info(f"Multi-panel prompt (first 500 chars): {prompt[:500]}...")

    # Generate the image
    try:
        if target_page.is_single_panel:
            # Single panel - use existing scene generation
            if reference_images:
                image_url = await image_generator.generate_scene_image_with_references(
                    prompt=prompt,
                    reference_images=reference_images,
                    image_style=image_style
                )
            else:
                image_url = await image_generator.generate_scene_image(
                    prompt=prompt,
                    image_style=image_style
                )
        else:
            # Multi-panel - use new multi-panel generation
            image_url = await image_generator.generate_multi_panel_page(
                prompt=prompt,
                reference_images=reference_images if reference_images else None,
                panel_count=target_page.panel_count
            )

        # Create response with enhanced metadata
        image_id = str(uuid.uuid4())

        return {
            "id": image_id,
            "page_number": page_number,
            "panel_count": target_page.panel_count,
            "layout_type": target_page.layout_type.value,
            "is_single_panel": target_page.is_single_panel,
            "panel_numbers": [p.panel_number for p in target_page.panels],
            "image_url": image_url,
            "prompt_used": prompt[:1000],  # Truncate for response
            "enhanced_metadata": {
                "within_size_limits": target_page.panel_count <= config.max_multi_panel_size,
                "max_allowed_panels": config.max_multi_panel_size,
                "generation_timestamp": time.time(),
                "reference_images_used": len(reference_images)
            }
        }

    except Exception as e:
        logger.error(f"Page image generation failed: {str(e)}", exc_info=True)
        
        # Enhanced error response for generation failures
        error_detail = {
            "error_type": "page_image_generation_failure",
            "message": f"Failed to generate image for page {page_number}: {str(e)}",
            "page_number": page_number,
            "panel_count": target_page.panel_count,
            "layout_type": target_page.layout_type.value,
            "retryable": True,
            "suggestions": [
                "Try generating individual panels instead of multi-panel",
                "Check if character reference images are valid",
                "Retry with a different image style"
            ]
        }
        
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/{script_id}/pages/preview")
async def preview_page_groupings(script_id: str):
    """
    Preview how panels will be grouped into pages.

    This is a read-only endpoint that shows the planned page groupings
    without generating any images.

    Args:
        script_id: Webtoon script ID

    Returns:
        Page groupings with panel details and statistics
    """
    if script_id not in webtoon_scripts:
        raise HTTPException(status_code=404, detail="Webtoon script not found")

    script_data = webtoon_scripts[script_id]
    panels_data = script_data.get("panels", [])

    if not panels_data:
        return {
            "script_id": script_id,
            "pages": [],
            "statistics": {
                "total_pages": 0,
                "total_panels": 0,
                "single_panel_pages": 0,
                "multi_panel_pages": 0,
            }
        }

    # Convert and group
    from app.models.story import WebtoonPanel
    panels = [WebtoonPanel(**p) for p in panels_data]
    pages = group_panels_into_pages(panels)
    stats = calculate_page_statistics(pages)

    # Build detailed preview
    page_previews = []
    for page in pages:
        panels_preview = []
        for panel in page.panels:
            panels_preview.append({
                "panel_number": panel.panel_number,
                "shot_type": panel.shot_type,
                "emotional_intensity": panel.emotional_intensity,
                "story_beat": panel.story_beat[:100] if panel.story_beat else "",
                "characters": panel.active_character_names,
            })

        page_previews.append({
            "page_number": page.page_number,
            "layout_type": page.layout_type.value,
            "is_single_panel": page.is_single_panel,
            "panel_count": page.panel_count,
            "reasoning": page.reasoning,
            "panels": panels_preview
        })

    return {
        "script_id": script_id,
        "pages": page_previews,
        "statistics": stats,
        "api_calls_saved": stats["total_panels"] - stats["total_pages"]
    }


# ============================================================================
# Enhanced Panel Generation Configuration Endpoints
# ============================================================================

class UpdatePanelConfigRequest(BaseModel):
    """Request model for updating panel configuration."""
    panel_count_min: Optional[int] = None
    panel_count_max: Optional[int] = None
    panel_count_ideal_min: Optional[int] = None
    panel_count_ideal_max: Optional[int] = None
    single_panel_ratio: Optional[float] = None
    max_multi_panel_size: Optional[int] = None
    max_panels_per_scene: Optional[int] = None
    enable_caching: Optional[bool] = None
    enable_progress_tracking: Optional[bool] = None
    progress_threshold: Optional[int] = None


@router.get("/config/panel-settings")
async def get_panel_configuration():
    """
    Get current enhanced panel generation configuration.
    
    Returns the current configuration settings for panel count targets,
    image generation strategies, and performance optimizations.
    
    Returns:
        Current EnhancedPanelConfig settings
    """
    config = get_enhanced_panel_config()
    return {
        "panel_count_settings": {
            "min": config.panel_count_min,
            "max": config.panel_count_max,
            "ideal_min": config.panel_count_ideal_min,
            "ideal_max": config.panel_count_ideal_max,
        },
        "image_generation_settings": {
            "single_panel_ratio": config.single_panel_ratio,
            "max_multi_panel_size": config.max_multi_panel_size,
        },
        "scene_structure_settings": {
            "max_panels_per_scene": config.max_panels_per_scene,
            "min_panels_per_scene": config.min_panels_per_scene,
        },
        "three_act_distribution": {
            "act1_ratio": config.act1_panel_ratio,
            "act2_ratio": config.act2_panel_ratio,
            "act3_ratio": config.act3_panel_ratio,
        },
        "genre_specific_targets": config.genre_specific_targets,
        "performance_settings": {
            "enable_caching": config.enable_caching,
            "enable_progress_tracking": config.enable_progress_tracking,
            "progress_threshold": config.progress_threshold,
        },
        "backward_compatibility": {
            "preserve_legacy_multi_panel": config.preserve_legacy_multi_panel,
            "legacy_multi_panel_max_size": config.legacy_multi_panel_max_size,
        }
    }


@router.put("/config/panel-settings")
async def update_panel_configuration(request: UpdatePanelConfigRequest):
    """
    Update enhanced panel generation configuration.
    
    Allows updating panel count targets, image generation strategies,
    and performance settings. Changes persist across system restarts.
    
    Args:
        request: Configuration updates to apply
        
    Returns:
        Updated configuration settings
        
    Raises:
        HTTPException: If configuration validation fails
    """
    try:
        # Filter out None values
        update_data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=400, 
                detail="No configuration updates provided"
            )
        
        # Update configuration
        updated_config = update_enhanced_panel_config(**update_data)
        
        logger.info(f"Panel configuration updated: {list(update_data.keys())}")
        
        return {
            "message": "Panel configuration updated successfully",
            "updated_fields": list(update_data.keys()),
            "current_settings": {
                "panel_count_min": updated_config.panel_count_min,
                "panel_count_max": updated_config.panel_count_max,
                "panel_count_ideal_min": updated_config.panel_count_ideal_min,
                "panel_count_ideal_max": updated_config.panel_count_ideal_max,
                "single_panel_ratio": updated_config.single_panel_ratio,
                "max_multi_panel_size": updated_config.max_multi_panel_size,
            }
        }
        
    except ValueError as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Configuration validation failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to update panel configuration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update configuration: {str(e)}"
        )


@router.get("/config/panel-settings/genre/{genre}")
async def get_genre_panel_targets(genre: str):
    """
    Get panel count targets for a specific genre.
    
    Args:
        genre: Genre name (e.g., "romance", "action", "fantasy")
        
    Returns:
        Panel count range and ideal targets for the genre
        
    Raises:
        HTTPException: If genre not found
    """
    config = get_enhanced_panel_config()
    
    try:
        min_panels, max_panels = config.get_panel_range_for_genre(genre)
        ideal_min, ideal_max = config.get_ideal_panel_range(genre)
        
        return {
            "genre": genre,
            "panel_count_range": {
                "min": min_panels,
                "max": max_panels,
            },
            "ideal_range": {
                "min": ideal_min,
                "max": ideal_max,
            },
            "recommended_panels": (min_panels + max_panels) // 2,
        }
        
    except Exception as e:
        logger.error(f"Failed to get genre targets for {genre}: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=f"Genre '{genre}' not found or invalid"
        )


@router.post("/config/panel-settings/validate")
async def validate_panel_count(panel_count: int, genre: Optional[str] = None):
    """
    Validate a panel count against current configuration.
    
    Args:
        panel_count: Number of panels to validate
        genre: Optional genre for genre-specific validation
        
    Returns:
        Validation result with recommendations
    """
    config = get_enhanced_panel_config()
    
    is_valid = config.validate_panel_count(panel_count, genre)
    
    if genre:
        min_panels, max_panels = config.get_panel_range_for_genre(genre)
        ideal_min, ideal_max = config.get_ideal_panel_range(genre)
        context = f"genre '{genre}'"
    else:
        min_panels, max_panels = config.panel_count_min, config.panel_count_max
        ideal_min, ideal_max = config.panel_count_ideal_min, config.panel_count_ideal_max
        context = "general"
    
    # Generate recommendations
    recommendations = []
    if panel_count < min_panels:
        recommendations.append(f"Consider adding {min_panels - panel_count} more panels for better storytelling")
    elif panel_count > max_panels:
        recommendations.append(f"Consider reducing by {panel_count - max_panels} panels to avoid reader fatigue")
    elif panel_count < ideal_min:
        recommendations.append(f"Adding {ideal_min - panel_count} more panels would reach the ideal range")
    elif panel_count > ideal_max:
        recommendations.append(f"Reducing by {panel_count - ideal_max} panels would optimize pacing")
    else:
        recommendations.append("Panel count is in the ideal range for optimal storytelling")
    
    return {
        "panel_count": panel_count,
        "context": context,
        "is_valid": is_valid,
        "validation_range": {
            "min": min_panels,
            "max": max_panels,
        },
        "ideal_range": {
            "min": ideal_min,
            "max": ideal_max,
        },
        "is_in_ideal_range": ideal_min <= panel_count <= ideal_max,
        "recommendations": recommendations,
    }


@router.get("/config/panel-settings/genres")
async def list_supported_genres():
    """
    List all supported genres with their panel count targets.
    
    Returns:
        List of genres with their panel count ranges
    """
    config = get_enhanced_panel_config()
    
    genres = []
    for genre_key, (min_panels, max_panels) in config.genre_specific_targets.items():
        # Convert enum key to display name
        display_name = genre_key.replace("_", " ").title()
        
        genres.append({
            "key": genre_key,
            "name": display_name,
            "panel_range": {
                "min": min_panels,
                "max": max_panels,
            },
            "recommended_panels": (min_panels + max_panels) // 2,
        })
    
    return {
        "supported_genres": genres,
        "total_genres": len(genres),
    }


@router.get("/{script_id}/enhanced-stats")
async def get_enhanced_panel_statistics(script_id: str):
    """
    Get enhanced panel generation statistics for a webtoon script.
    
    Provides detailed analysis of panel distribution, image generation strategy,
    and compliance with enhanced panel configuration.
    
    Args:
        script_id: Webtoon script ID
        
    Returns:
        Enhanced statistics and analysis
        
    Raises:
        HTTPException: If script not found
    """
    if script_id not in webtoon_scripts:
        raise HTTPException(status_code=404, detail="Webtoon script not found")
    
    script_data = webtoon_scripts[script_id]
    panels_data = script_data.get("panels", [])
    enhanced_metadata = script_data.get("enhanced_metadata", {})
    
    if not panels_data:
        return {
            "script_id": script_id,
            "panel_count": 0,
            "analysis": "No panels found in script",
            "compliance": {"status": "no_data"}
        }
    
    config = get_enhanced_panel_config()
    panel_count = len(panels_data)
    genre = enhanced_metadata.get("genre", "default")
    
    # Panel count analysis
    min_panels, max_panels = config.get_panel_range_for_genre(genre)
    ideal_min, ideal_max = config.get_ideal_panel_range(genre)
    is_valid = config.validate_panel_count(panel_count, genre)
    is_ideal = ideal_min <= panel_count <= ideal_max
    
    # Three-act distribution analysis
    act_distribution = config.calculate_act_distribution(panel_count)
    
    # Scene structure analysis
    from app.models.story import WebtoonPanel
    panels = [WebtoonPanel(**p) for p in panels_data]
    
    # Group panels by scene (assuming scene_number field exists)
    scenes = {}
    for panel in panels:
        scene_num = getattr(panel, 'scene_number', 1)  # Default to scene 1 if not specified
        if scene_num not in scenes:
            scenes[scene_num] = []
        scenes[scene_num].append(panel)
    
    scene_panel_counts = [len(scene_panels) for scene_panels in scenes.values()]
    avg_panels_per_scene = sum(scene_panel_counts) / len(scene_panel_counts) if scene_panel_counts else 0
    
    # Image generation strategy analysis
    pages = group_panels_into_pages(panels)
    page_stats = calculate_page_statistics(pages)
    
    single_panel_count = page_stats.get("single_panel_pages", 0)
    multi_panel_count = page_stats.get("multi_panel_pages", 0)
    total_pages = single_panel_count + multi_panel_count
    
    actual_single_ratio = single_panel_count / total_pages if total_pages > 0 else 0
    meets_single_ratio = actual_single_ratio >= config.single_panel_ratio
    
    # Multi-panel size compliance
    oversized_pages = []
    for page in pages:
        if not page.is_single_panel and page.panel_count > config.max_multi_panel_size:
            oversized_pages.append({
                "page_number": page.page_number,
                "panel_count": page.panel_count,
                "max_allowed": config.max_multi_panel_size
            })
    
    # Overall compliance assessment
    compliance_issues = []
    if not is_valid:
        if panel_count < min_panels:
            compliance_issues.append(f"Panel count ({panel_count}) below minimum ({min_panels})")
        else:
            compliance_issues.append(f"Panel count ({panel_count}) exceeds maximum ({max_panels})")
    
    if not meets_single_ratio:
        compliance_issues.append(f"Single-panel ratio ({actual_single_ratio:.2f}) below target ({config.single_panel_ratio})")
    
    if oversized_pages:
        compliance_issues.append(f"{len(oversized_pages)} pages exceed multi-panel size limit")
    
    compliance_status = "compliant" if not compliance_issues else "non_compliant"
    
    return {
        "script_id": script_id,
        "generation_info": {
            "timestamp": enhanced_metadata.get("generation_timestamp"),
            "config_version": enhanced_metadata.get("config_version", "unknown"),
            "genre": genre,
        },
        "panel_analysis": {
            "total_panels": panel_count,
            "is_valid_count": is_valid,
            "is_ideal_count": is_ideal,
            "genre_range": {"min": min_panels, "max": max_panels},
            "ideal_range": {"min": ideal_min, "max": ideal_max},
            "three_act_distribution": act_distribution,
        },
        "scene_analysis": {
            "total_scenes": len(scenes),
            "panels_per_scene": scene_panel_counts,
            "average_panels_per_scene": round(avg_panels_per_scene, 1),
            "max_panels_per_scene": max(scene_panel_counts) if scene_panel_counts else 0,
            "min_panels_per_scene": min(scene_panel_counts) if scene_panel_counts else 0,
        },
        "image_strategy_analysis": {
            "total_pages": total_pages,
            "single_panel_pages": single_panel_count,
            "multi_panel_pages": multi_panel_count,
            "actual_single_ratio": round(actual_single_ratio, 3),
            "target_single_ratio": config.single_panel_ratio,
            "meets_single_ratio_target": meets_single_ratio,
            "oversized_multi_panel_pages": oversized_pages,
        },
        "compliance": {
            "status": compliance_status,
            "issues": compliance_issues,
            "recommendations": [
                f"Ideal panel count for {genre}: {ideal_min}-{ideal_max}",
                f"Target single-panel ratio: {config.single_panel_ratio}",
                f"Max panels per multi-panel image: {config.max_multi_panel_size}",
            ]
        },
        "performance_metrics": {
            "api_calls_saved": page_stats.get("total_panels", 0) - page_stats.get("total_pages", 0),
            "estimated_generation_time": f"{panel_count * 0.5:.1f}s",  # Rough estimate
        }
    }
