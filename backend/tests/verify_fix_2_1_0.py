
import asyncio
import logging
from app.models.story import WebtoonPanel, Character
from app.agents.visual_prompter import run as visual_prompter_run, VisualPrompterState
from app.services.image_generator import image_generator
from app.prompt.scene_image import SCENE_IMAGE_TEMPLATE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_fixes():
    # 1. Setup Mock Data
    character = Character(
        name="Ji-hoon",
        reference_tag="Ji-hoon(male)",
        gender="male",
        age="20s",
        visual_description="Tall male with black hair, wearing a navy suit and silver watch.",
        face="sharp jawline",
        hair="black hair",
        outfit="navy suit"
    )
    
    panel = {
        "panel_number": 1,
        "visual_prompt": "Ji-hoon standing in a modern office looking out the window.",
        "active_character_names": ["Ji-hoon"],
        "shot_type": "Medium Shot",
        "style_mode": "romantic_detail"
    }
    
    # 2. Test Visual Prompter (Pruning Check)
    logger.info("--- Testing Visual Prompter (Pruning) ---")
    vp_state = VisualPrompterState(
        panels=[panel],
        mood_assignments=[{"panel_number": 1, "intensity": 5, "detected_context": "neutral"}],
        image_style="SOFT_ROMANTIC_WEBTOON",
        characters=[character.model_dump()]
    )
    
    vp_result = await visual_prompter_run(vp_state)
    enhanced_prompt = vp_result.enhanced_prompts[0]
    
    logger.info(f"Enhanced Prompt via Agent:\n{enhanced_prompt}")
    
    if "[CHARACTER CONSISTENCY]" in enhanced_prompt:
        logger.error("FAIL: [CHARACTER CONSISTENCY] block still present in enhanced prompt!")
    else:
        logger.info("PASS: [CHARACTER CONSISTENCY] block pruned.")
        
    if "[TECHNICAL]" in enhanced_prompt:
        logger.error("FAIL: [TECHNICAL] block still present in enhanced prompt!")
    else:
        logger.info("PASS: [TECHNICAL] block pruned.")
        
    # 3. Test Template Integration (Character Description Check)
    logger.info("\n--- Testing Template Integration in Webtoon Router Logic ---")
    
    # Simulate logic from routers/webtoon.py
    char_desc_text = f"- {character.name}: {character.visual_description} (reference image provided - appearance locked)"
    
    final_prompt = SCENE_IMAGE_TEMPLATE.format(
        character_description=char_desc_text,
        visual_prompt=enhanced_prompt, # Using the enhanced prompt from agent
        negative_prompt="nsfw",
        shot_type="Medium Shot",
        composition_notes="Standard",
        character_frame_percentage=40,
        environment_frame_percentage=60,
        environment_focus="Office",
        environment_details="Modern office window",
        atmospheric_conditions="Daylight",
        sfx_description="None",
        emotional_tone="Calm",
        character_placement_and_action="Standing",
        dialogue_visual_context="None"
    )
    
    logger.info(f"Final Prompt Sent to Gemini:\n{final_prompt[:1000]}...")
    
    if character.visual_description in final_prompt:
        logger.info("PASS: detailed visual_description found in final prompt.")
    else:
        logger.error("FAIL: visual_description NOT found in final prompt.")

if __name__ == "__main__":
    asyncio.run(verify_fixes())
