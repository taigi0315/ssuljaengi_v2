"""
Multi-panel Generator Service.

This module provides a service to generate multi-panel webtoon pages
using the Gemini 2.5 Image model. It takes a list of WebtoonPanel objects
and generates a single vertical image containing all panels.
"""

import logging
import base64
import uuid
from typing import List, Optional, Dict

from google.genai import types
from app.config import get_settings
from app.models.story import WebtoonPanel
# from app.prompt.multi_panel_generator import build_multi_panel_prompt
from app.services.image_generator import image_generator, CACHE_DIR
from app.utils.dialogue_formatter import format_dialogue_as_visual_context

logger = logging.getLogger(__name__)


class MultiPanelGenerator:
    """
    Service for generating multi-panel webtoon pages.
    """

    def __init__(self):
        """Initialize with the existing image generator instance."""
        self.image_gen = image_generator
        # We rely on image_generator to hold the initialized client

    async def generate_multi_panel_page(
        self,
        panels: List[WebtoonPanel],
        style_description: str,
        style_modifiers: Optional[List[str]] = None,
        reference_images: Optional[List[str]] = None,
        characters: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate a single vertical image containing multiple panels.

        Args:
            panels: List of WebtoonPanel objects (content for the page).
            style_description: Description of the art style.
            style_modifiers: Optional list of style keywords.
            reference_images: Optional list of base64 data URLs for reference.
            characters: Optional list of character dictionaries for rich descriptions.

        Returns:
            The data URL (base64) of the generated image.

        Raises:
            Exception: If generation fails or client is not initialized.
        """
        if not self.image_gen.client:
            raise Exception("Gemini API client not initialized via ImageGenerator.")

        # 1. Prepare character references for consistent appearance
        character_references = {}
        if characters:
            for char in characters:
                name = char.get("name", "Unknown")
                # Build rich description: "Name (Gender, Age...): Description"
                details = []
                if char.get("gender"): details.append(char["gender"])
                if char.get("age"): details.append(str(char["age"]))
                
                desc_parts = [f"{name} ({', '.join(details)})" if details else name]
                
                if char.get("visual_description"):
                    desc_parts.append(char["visual_description"])
                
                # Add specific visual traits if available
                visual_traits = []
                for trait in ["hair", "face", "outfit", "body"]:
                    if char.get(trait):
                        visual_traits.append(f"{trait}: {char[trait]}")
                
                if visual_traits:
                    desc_parts.append(f"Visual traits: {', '.join(visual_traits)}")
                
                character_references[name] = ": ".join(desc_parts)

        # 1.5. Inject dialogue expressions into visual prompts (Legacy "Good Part")
        # The legacy code correctly extracted dialogue and converted it to visual expressions.
        # We perform this enhancement here to ensure the visual prompt includes acting guidance.
        enhanced_panels = []
        for p in panels:
            # We create a copy or modify if possible. internal usage so straightforward modification is okay
            # but cleaner to not mutate input list if possible. 
            # WebtoonPanel is Pydantic, so we can use model_copy() if needed, or just set attribute if mutable.
            # Assuming we can modify or just rely on dynamic attribute for the formatter.
            
            expression_context = ""
            if hasattr(p, 'dialogue') and p.dialogue:
                if isinstance(p.dialogue, list):
                    # Convert dialogue to visual expression descriptions
                    expression_context = format_dialogue_as_visual_context(p.dialogue, max_lines=3)
                    # Extract just the expression part, not the header
                    if "CHARACTER EXPRESSIONS" in expression_context:
                        lines = expression_context.split("\n")
                        expression_lines = [l.strip("- ") for l in lines if l.startswith("- ") and ":" in l]
                        # Only take lines that look like "Name: Expression"
                        if expression_lines:
                            expression_context = ". ".join(expression_lines)
                        else:
                             # Fallback if parsing fails but content exists
                             expression_context = expression_context.replace("CHARACTER EXPRESSIONS", "").replace("\n", ". ").strip()
            
            # Append expression context to visual prompt if found
            if expression_context:
                original_prompt = getattr(p, "visual_prompt", "")
                # Avoid duplication if already present
                if expression_context[:20] not in original_prompt:
                    p.visual_prompt = f"{original_prompt} [EXPRESSION: {expression_context}]"
            
            enhanced_panels.append(p)

        # 2. Build the structured prompt using the standardized builder
        from app.prompt.multi_panel import format_panels_from_webtoon_panels
        
        # Convert explicit style modifiers to keywords string if provided
        style_keywords = "High resolution, clean line art, professional webtoon quality"
        if style_modifiers:
            style_keywords += ", " + ", ".join(style_modifiers)
            
        try:
            prompt = format_panels_from_webtoon_panels(
                webtoon_panels=enhanced_panels,
                style_description=style_description,
                style_keywords=style_keywords,
                character_references=character_references
            )
        except ValueError as e:
            logger.error(f"Failed to build prompt: {e}")
            raise

        logger.info(f"Generating multi-panel page for {len(panels)} panels. Prompt length: {len(prompt)}")
        logger.debug(f"Prompt: {prompt[:200]}...")

        # 3. Call Gemini API
        try:
            settings = get_settings()
            model_name = settings.model_image_gen

            # Prepare contents (Prompt + Text + Images)
            contents = []
            
            # Add reference images if provided
            if reference_images:
                for i, image_url in enumerate(reference_images):
                    try:
                        if image_url.startswith("data:"):
                            header, data = image_url.split(",", 1)
                            mime_type = header.split(";")[0].split(":")[1]
                            image_bytes_decoded = base64.b64decode(data)
                            
                            image_part = types.Part.from_bytes(
                                data=image_bytes_decoded,
                                mime_type=mime_type
                            )
                            contents.append(image_part)
                            logger.info(f"Added reference image {i+1} to multi-panel prompt")
                    except Exception as e:
                        logger.warning(f"Failed to process reference image {i+1}: {e}")

            # Add the text prompt
            contents.append(prompt)

            response = self.image_gen.client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    image_config=types.ImageConfig(
                        aspect_ratio="9:16",  # Vertical strip format
                    ),
                    safety_settings=[
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ],
                )
            )

            # 4. Extract and process the image
            image_bytes = None
            mime_type = "image/png"

            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_bytes = part.inline_data.data
                        if part.inline_data.mime_type:
                            mime_type = part.inline_data.mime_type
                        break
            
            if not image_bytes:
                logger.error(f"No image in response: {response}")
                raise Exception("No image data returned from Gemini.")

            # Convert to base64 string
            if isinstance(image_bytes, bytes):
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            elif isinstance(image_bytes, str):
                image_base64 = image_bytes
            else:
                image_base64 = str(image_bytes)

            # 5. Save to cache
            filename_prefix = f"multi_panel_{len(panels)}p"
            self.image_gen._save_image_to_cache(image_base64, filename_prefix, mime_type)

            # Log completion
            from app.utils.llm_logger import llm_logger
            await llm_logger.log_request(
                service_name="multi_panel_generator",
                model_name=model_name,
                prompt=prompt,
                output="<Base64 Image Data>",
                metadata={"panel_count": len(panels), "style": style_description}
            )

            return f"data:{mime_type};base64,{image_base64}"

        except Exception as e:
            logger.error(f"Multi-panel generation failed: {e}", exc_info=True)
            raise


# Global instance
multi_panel_generator = MultiPanelGenerator()
