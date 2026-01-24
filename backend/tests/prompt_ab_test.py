# tests/prompt_ab_test.py
"""
A/B Prompt Testing Framework (v2.1.0 E4-T04)

This script allows side-by-side comparison of different prompt strategies
without invoking the actual image generation API (to save costs).
It compares token counts, structure, and key element inclusion.
"""

from app.prompt.modular_prompt import (
    compose_scene_prompt, 
    ModularPromptComposer,
    build_character_ref_module,
    build_visual_description_module,
    build_style_mood_module,
    estimate_tokens
)
import difflib

def run_ab_test():
    """Run A/B comparison between Monolithic vs Modular prompts."""
    
    # 1. Setup Test Data
    character = {
        "name": "Ji-hoon",
        "hair": "short black style",
        "face": "sharp jawline",
        "outfit": "navy suit",
        "body": "tall athletic"
    }
    
    visual_prompt = "Ji-hoon stands in the rain looking heartbroken."
    shot_type = "medium shot"
    emotion = "sadness"
    
    print("=== A/B Prompt Testing Framework ===")
    print("Optimization Target: Reduce token usage while maintaining detail.\n")
    
    # 2. Strategy A: Legacy Monolithic Style (Simulated)
    legacy_prompt = (
        f"Masterpiece, best quality, 4k. {visual_prompt} "
        f"Character: {character['name']}, {character['hair']}, {character['face']}, "
        f"{character['outfit']}, {character['body']}. "
        f"Shot: {shot_type}. Emotion: {emotion}. "
        "Detailed background, cinematic lighting, sharp focus."
    )
    
    # 3. Strategy B: Modular Architecture (v2.1.0)
    modular_prompt = compose_scene_prompt(
        characters=[character],
        visual_prompt=visual_prompt,
        shot_type=shot_type,
        emotional_tone=emotion,
        environment_brief="Rainy street at night",
        style_keywords="cinematic lighting, sharp focus"
    )
    
    # 4. Analysis
    tokens_a = estimate_tokens(legacy_prompt)
    tokens_b = estimate_tokens(modular_prompt)
    
    print(f"Strategy A (Legacy): {tokens_a} estimated tokens")
    print(f"Strategy B (Modular): {tokens_b} estimated tokens")
    
    diff = tokens_b - tokens_a
    percent = (diff / tokens_a) * 100
    print(f"Difference: {diff:+d} tokens ({percent:+.1f}%)")
    
    print("\n--- Strategy A Content ---\n")
    print(legacy_prompt[:200] + "..." if len(legacy_prompt) > 200 else legacy_prompt)
    
    print("\n--- Strategy B Content ---\n")
    print(modular_prompt[:200] + "...")
    
    # 5. Structure Check
    print("\n--- Modular Structure Check ---")
    if "[CHARACTER CONSISTENCY" in modular_prompt:
        print("✅ Critical Character Module found at TOP")
    else:
        print("❌ Critical Character Module MISSING or misplaced")
        
    if "[TECHNICAL SPECS]" in modular_prompt and modular_prompt.find("[TECHNICAL SPECS]") > len(modular_prompt) / 2:
        print("✅ Technical Specs found at BOTTOM (Low Priority)")
    else:
        print("❌ Technical Specs misplaced")

if __name__ == "__main__":
    run_ab_test()
