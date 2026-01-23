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
from app.prompt.multi_panel_generator import build_multi_panel_prompt
from app.services.image_generator import image_generator, CACHE_DIR

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
        style_modifiers: Optional[List[str]] = None
    ) -> str:
        """
        Generate a single vertical image containing multiple panels.

        Args:
            panels: List of WebtoonPanel objects (content for the page).
            style_description: Description of the art style.
            style_modifiers: Optional list of style keywords.

        Returns:
            The data URL (base64) of the generated image.

        Raises:
            Exception: If generation fails or client is not initialized.
        """
        if not self.image_gen.client:
            raise Exception("Gemini API client not initialized via ImageGenerator.")

        # 1. Prepare panel specifications for the prompt builder
        panel_specs: List[Dict[str, str]] = []
        for p in panels:
            # Extract subject: use characters or default to generic if none
            subject = ", ".join(p.active_character_names) if p.active_character_names else "scene characters"
            
            # Construct spec dictionary
            # Note: We combine environment and atmospheric details
            details_parts = []
            if p.environment_details:
                details_parts.append(p.environment_details)
            if p.atmospheric_conditions:
                details_parts.append(p.atmospheric_conditions)
            
            spec = {
                "shot_type": p.shot_type,
                "subject": subject,
                "action": p.character_placement_and_action,
                "details": ", ".join(details_parts)
            }
            panel_specs.append(spec)

        # 2. Build the structured prompt
        try:
            prompt = build_multi_panel_prompt(
                panel_count=len(panels),
                style_description=style_description,
                panels=panel_specs,
                style_modifiers=style_modifiers
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

            response = self.image_gen.client.models.generate_content(
                model=model_name,
                contents=[prompt],
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

            return f"data:{mime_type};base64,{image_base64}"

        except Exception as e:
            logger.error(f"Multi-panel generation failed: {e}", exc_info=True)
            raise


# Global instance
multi_panel_generator = MultiPanelGenerator()
