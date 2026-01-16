"""
Image Generator service for creating character images.

This module implements the ImageGenerator service that generates character images
using Gemini 2.5 Flash Image model with proper prompt templates.
"""

import logging
import os
import base64
from typing import Literal
from google import genai
from app.config import get_settings
from app.prompt.character_image import YOUTH_MALE, YOUTH_FEMALE, CHARACTER_IMAGE_TEMPLATE
from app.prompt.image_mood import (
    HISTORY_SAGEUK_ROMANCE,
    ISEKAI_OTOME_FANTASY,
    MODERN_KOREAN_ROMANCE
)


logger = logging.getLogger(__name__)


class ImageGenerator:
    """
    Image Generator service for creating character images.
    
    Uses Gemini 2.5 Flash Image model to generate consistent character images
    with proper base style and image mood.
    """
    
    def __init__(self):
        """Initialize the image generator with Gemini 2.5 Flash Image."""
        self.image_styles = {
            "HISTORY_SAGEUK_ROMANCE": HISTORY_SAGEUK_ROMANCE,
            "ISEKAI_OTOME_FANTASY": ISEKAI_OTOME_FANTASY,
            "MODERN_KOREAN_ROMANCE": MODERN_KOREAN_ROMANCE
        }
        
        # Configure Gemini API
        try:
            settings = get_settings()
            api_key = settings.google_api_key
            self.client = genai.Client(api_key=api_key)
            self.use_real_generation = True
            logger.info("Image generator initialized with Gemini 2.5 Flash Image")
        except Exception as e:
            self.client = None
            self.use_real_generation = False
            logger.warning(f"Failed to initialize Gemini API: {str(e)}, using placeholder images")
    
    async def generate_character_image(
        self, 
        description: str, 
        character_name: str,
        gender: str,
        image_style: Literal["HISTORY_SAGEUK_ROMANCE", "ISEKAI_OTOME_FANTASY", "MODERN_KOREAN_ROMANCE"]
    ) -> str:
        """
        Generate a character image from description.
        
        Args:
            description: Visual description of the character
            character_name: Name of the character
            gender: Character gender (male/female) for base style
            image_style: Image style/mood selection
            
        Returns:
            Image URL or base64 encoded image data
            
        Raises:
            Exception: If image generation fails
        """
        try:
            logger.info(f"Generating image for character: {character_name}")
            logger.info(f"Gender: {gender}, Style: {image_style}")
            logger.info(f"Description: {description[:100]}...")
            
            # Select base style based on gender
            base_style = self._get_base_style(gender)
            
            # Get image style prompt
            image_style_prompt = self.image_styles.get(image_style, MODERN_KOREAN_ROMANCE)
            
            # Build final prompt using template
            final_prompt = CHARACTER_IMAGE_TEMPLATE.format(
                base_style=base_style,
                character_description=description,
                image_style=image_style_prompt
            )
            
            logger.info(f"Final prompt length: {len(final_prompt)} characters")
            
            # Try to generate with Gemini Imagen if available
            if self.use_real_generation:
                try:
                    image_url = await self._generate_with_gemini(final_prompt, character_name)
                    logger.info(f"Image generated with Gemini for {character_name}")
                    return image_url
                except Exception as e:
                    logger.warning(f"Gemini generation failed, using placeholder: {str(e)}")
            
            # Fallback to placeholder
            placeholder_url = self._generate_placeholder(character_name, description)
            logger.info(f"Using placeholder image for {character_name}")
            
            return placeholder_url
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}", exc_info=True)
            raise Exception(f"Image generation failed: {str(e)}")
    
    def _get_base_style(self, gender: str) -> str:
        """
        Get base style based on gender.
        
        Args:
            gender: Character gender
            
        Returns:
            Base style prompt (YOUTH_MALE or YOUTH_FEMALE)
        """
        gender_lower = gender.lower()
        
        if "male" in gender_lower and "female" not in gender_lower:
            return YOUTH_MALE
        elif "female" in gender_lower:
            return YOUTH_FEMALE
        else:
            # Default to male if unclear
            return YOUTH_MALE
    
    async def _generate_with_gemini(self, prompt: str, character_name: str) -> str:
        """
        Generate image using Gemini 2.5 Flash Image.
        
        Args:
            prompt: Image generation prompt
            character_name: Name of the character
            
        Returns:
            Base64 encoded image data URL
            
        Raises:
            Exception: If generation fails
        """
        try:
            # Get model name from settings
            settings = get_settings()
            model_name = settings.model_image_gen
            
            logger.info(f"Using model: {model_name}")
            
            # Use Gemini 2.5 Flash Image model with safety settings
            response = self.client.models.generate_content(
                model=model_name,
                contents=[prompt],
                config={
                    "safety_settings": [
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_LOW_AND_ABOVE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
                    ],
                }
            )
            
            # Extract image from response - check candidates first
            image_bytes = None
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_bytes = part.inline_data.data
                        break
            
            if not image_bytes:
                raise Exception("No image data in response")
            
            # Get MIME type
            mime_type = 'image/png'  # Default
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        if hasattr(part.inline_data, 'mime_type'):
                            mime_type = part.inline_data.mime_type
                        break
            
            # Encode to base64
            if isinstance(image_bytes, bytes):
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            else:
                image_base64 = image_bytes
            
            logger.info(f"Image generated successfully")
            logger.info(f"Image data type: {type(image_bytes)}, length: {len(image_bytes) if image_bytes else 0}")
            logger.info(f"MIME type: {mime_type}")
            logger.info(f"Base64 length: {len(image_base64)}")
            
            # Return as data URL with correct MIME type
            return f"data:{mime_type};base64,{image_base64}"
                
        except Exception as e:
            logger.error(f"Gemini image generation failed: {str(e)}")
            raise
    
    def _generate_placeholder(self, character_name: str, description: str) -> str:
        """
        Generate a placeholder image URL.
        
        Args:
            character_name: Name of the character
            description: Visual description
            
        Returns:
            Placeholder image URL
        """
        # Use a placeholder service like placeholder.com or UI Avatars
        # For now, use UI Avatars with character initials
        initials = "".join([word[0].upper() for word in character_name.split()[:2]])
        
        # Create a simple placeholder URL
        # In production, this would be replaced with actual generated images
        placeholder_url = f"https://ui-avatars.com/api/?name={initials}&size=512&background=random"
        
        return placeholder_url


# Global image generator instance
image_generator = ImageGenerator()
