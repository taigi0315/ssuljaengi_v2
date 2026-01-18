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
    WebtoonScript
)
from app.services.webtoon_writer import webtoon_writer
from app.services.image_generator import image_generator
from app.workflows.webtoon_workflow import run_webtoon_workflow
from app.models.video_models import GenerateVideoRequest, VideoPanelData, BubbleData


from app.config import get_settings
from app.utils.persistence import JsonStore

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
            "id": "MODERN_ROMANCE_DRAMA_MANHWA",
            "name": "Modern Romance Drama",
            "description": "Contemporary Korean romance drama",
            "preview_url": "/api/assets/images/genre/MODERN_ROMANCE_DRAMA_MANHWA.png"
        },
        {
            "id": "FANTASY_ROMANCE_MANHWA",
            "name": "Fantasy Romance",
            "description": "Magical academy or mystical world romance",
            "preview_url": "/api/assets/images/genre/FANTASY_ROMANCE_MANHWA.png"
        },
        {
            "id": "HISTORY_SAGEUK_ROMANCE",
            "name": "Historical Romance",
            "description": "Elegant sageuk style with dramatic lighting",
            "preview_url": "/api/assets/images/genre/HISTORY_SAGEUK_ROMANCE.png"
        },
        {
            "id": "ACADEMY_SCHOOL_LIFE",
            "name": "School Life",
            "description": "Contemporary school romance",
            "preview_url": "/api/assets/images/genre/ACADEMY_SCHOOL_LIFE.png"
        },
        {
            "id": "ISEKAI_OTOME_FANTASY",
            "name": "Isekai Otome Fantasy",
            "description": "Reincarnation/transmigration romance",
            "preview_url": "/api/assets/images/genre/ISEKAI_OTOME_FANTASY.png"
        }
    ]


@router.post("/generate")
async def generate_webtoon_script(request: GenerateWebtoonRequest) -> WebtoonScriptResponse:
    """
    Convert a story into a webtoon script with characters and panels.
    
    Uses LangGraph workflow with automatic evaluation and rewriting.
    The workflow evaluates the generated script and conditionally rewrites
    it up to 2 times if quality thresholds aren't met.
    
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
        # Use the LangGraph workflow with evaluation and rewriting
        # This automatically evaluates the script and rewrites if needed (max 2 times)
        webtoon_script = await run_webtoon_workflow(
            story=story_content,
            genre="MODERN_ROMANCE_DRAMA_MANHWA"  # Default genre
        )
        
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
    
    # Check if script exists
    if request.script_id not in webtoon_scripts:
        logger.error(f"Script {request.script_id} not found in storage")
        raise HTTPException(status_code=404, detail="Webtoon script not found")
    
    try:
        # Generate image with gender and style
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
    from app.prompt.scene_image import SCENE_IMAGE_TEMPLATE
    
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
                panel_metadata["negative_prompt"] = panel.get("negative_prompt", "worst quality, low quality")
                
                # Extract SFX effects
                sfx_effects = panel.get("sfx_effects", [])
                if sfx_effects:
                    sfx_parts = []
                    for sfx in sfx_effects:
                        sfx_type = sfx.get("type", "")
                        intensity = sfx.get("intensity", "medium")
                        desc = sfx.get("description", "")
                        position = sfx.get("position", "background")
                        sfx_parts.append(f"- {sfx_type.upper()} effect ({intensity} intensity): {desc} [Position: {position}]")
                    panel_metadata["sfx_description"] = "\n".join(sfx_parts)
                    logger.info(f"SFX effects found: {len(sfx_effects)}")
                else:
                    panel_metadata["sfx_description"] = "No special visual effects for this scene"
                
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
            character_desc_text = "No specific character reference - generate generic scene"
        
        logger.info(f"Character descriptions for prompt:\n{character_desc_text}")
        
        # Build final prompt using the template
        final_prompt = SCENE_IMAGE_TEMPLATE.format(
            character_description=character_desc_text,
            visual_prompt=request.visual_prompt,
            negative_prompt=panel_metadata["negative_prompt"],
            shot_type=panel_metadata["shot_type"],
            composition_notes=panel_metadata["composition_notes"],
            character_frame_percentage=panel_metadata["character_frame_percentage"],
            environment_frame_percentage=panel_metadata["environment_frame_percentage"],
            environment_focus=panel_metadata["environment_focus"],
            environment_details=panel_metadata["environment_details"],
            atmospheric_conditions=panel_metadata["atmospheric_conditions"],
            sfx_description=panel_metadata.get("sfx_description", "No special visual effects for this scene")
        )
        
        logger.info(f"Final scene prompt (first 500 chars): {final_prompt[:500]}")
        
        # Generate image using the appropriate method
        if reference_images:
            # Use multimodal generation with reference images
            logger.info(f"Using multimodal generation with {len(reference_images)} reference images")
            image_url = await image_generator.generate_scene_image_with_references(
                prompt=final_prompt,
                reference_images=reference_images,
                image_style=request.genre
            )
        else:
            # Fallback to text-only generation
            logger.info("No reference images, using text-only generation")
            # Unpack tuple from generate_character_image
            image_url, _ = await image_generator.generate_character_image(
                description=final_prompt,
                character_name=f"scene_{request.panel_number}",
                gender="neutral",
                image_style=request.genre
            )
        
        # Create image record
        image_id = str(uuid.uuid4())
        scene_image = SceneImage(
            id=image_id,
            panel_number=request.panel_number,
            image_url=image_url,
            prompt_used=final_prompt,
            is_selected=False
        )
        
        # Store image
        image_key = f"{request.script_id}:{request.panel_number}"
        if image_key not in scene_images:
            scene_images[image_key] = []
        
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
                BubbleData(text=b.text, x=b.x, y=b.y) 
                for b in p.bubbles
            ]
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



