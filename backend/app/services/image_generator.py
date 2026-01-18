"""
Image Generator service for creating character images.

This module implements the ImageGenerator service that generates character images
using Gemini 2.5 Flash Image model with proper prompt templates.
"""

import logging
import os
import base64
import uuid
from pathlib import Path
from typing import Literal, Tuple, List, Optional
from google import genai
from app.config import get_settings
from app.prompt.character_image import (
    MALE, FEMALE,
    MALE_KID, MALE_TEEN, MALE_20_30, MALE_40_50, MALE_60_70,
    FEMALE_KID, FEMALE_TEEN, FEMALE_20_30, FEMALE_40_50, FEMALE_60_70,
    CHARACTER_IMAGE_TEMPLATE
)
from app.prompt.image_mood import CHARACTER_GENRE_MODIFIERS


logger = logging.getLogger(__name__)

# Cache directory for generated images
CACHE_DIR = Path(__file__).parent.parent.parent / "cache" / "images"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class ImageGenerator:
    """
    Image Generator service for creating character images.
    
    Uses Gemini 2.5 Flash Image model to generate consistent character images
    with proper base style and image mood.
    """
    
    def __init__(self):
        """Initialize the image generator with Gemini 2.5 Flash Image."""
        self.image_styles = CHARACTER_GENRE_MODIFIERS
        
        # Configure Gemini API
        try:
            settings = get_settings()
            api_key = settings.google_api_key
            self.client = genai.Client(api_key=api_key)
            self.use_real_generation = True
            logger.info(f"Image generator initialized with model: {settings.model_image_gen}")
        except Exception as e:
            self.client = None
            self.use_real_generation = False
            logger.warning(f"Failed to initialize Gemini API: {str(e)}, using placeholder images")
    
    async def generate_character_image(
        self, 
        description: str, 
        character_name: str,
        gender: str,
        image_style: str
    ) -> Tuple[str, str]:
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
            
            # Select base style based on gender and description (for age detection)
            base_style = self._get_base_style(gender, description)
            
            # Get image style prompt
            image_style_prompt = self.image_styles.get(image_style, self.image_styles["MODERN_ROMANCE_DRAMA_MANHWA"])
            
            # Build final prompt using template
            final_prompt = CHARACTER_IMAGE_TEMPLATE.format(
                gender_style=base_style,
                character_description=description,
                genre_style=image_style_prompt
            )
            
            logger.info(f"Final prompt length: {len(final_prompt)} characters")
            
            # Try to generate with Gemini Imagen if available
            if self.use_real_generation:
                # Direct call, let exception propagate as requested
                image_url = await self._generate_with_gemini(final_prompt, character_name)
                logger.info(f"Image generated with Gemini for {character_name}")
                return image_url, final_prompt
            else:
                raise Exception("Gemini API not initialized, cannot generate image.")
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}", exc_info=True)
            raise Exception(f"Image generation failed: {str(e)}")
    
    async def generate_scene_image_with_references(
        self,
        prompt: str,
        reference_images: List[str],
        image_style: str
    ) -> str:
        """
        Generate a scene image with character reference images for consistency.
        
        Args:
            prompt: Scene description prompt with character descriptions
            reference_images: List of base64 data URLs of selected character images
            image_style: Image style/mood selection
            
        Returns:
            Base64 encoded image data URL
            
        Raises:
            Exception: If image generation fails
        """
        try:
            logger.info(f"Generating scene image with {len(reference_images)} reference images")
            logger.info(f"Style: {image_style}")
            logger.info(f"Prompt (first 200 chars): {prompt[:200]}...")
            
            if not self.use_real_generation:
                raise Exception("Gemini API not initialized, cannot generate image.")
            
            # Get model name from settings
            settings = get_settings()
            model_name = settings.model_image_gen
            
            logger.info(f"Using model: {model_name}")
            
            # Build multimodal contents with reference images
            contents = []
            
            # Add reference images first using correct Part format
            for i, image_url in enumerate(reference_images):
                try:
                    # Extract base64 data from data URL
                    if image_url.startswith('data:'):
                        # Format: data:image/png;base64,xxxxx
                        parts = image_url.split(',', 1)
                        if len(parts) == 2:
                            mime_part = parts[0]  # data:image/png;base64
                            image_data = parts[1]  # base64 data
                            
                            # Extract MIME type
                            mime_type = "image/png"
                            if "image/" in mime_part:
                                mime_type = mime_part.split(';')[0].replace('data:', '')
                            
                            # Decode base64 to bytes
                            image_bytes = base64.b64decode(image_data)
                            
                            # Use types.Part.from_bytes for correct format
                            from google.genai import types
                            image_part = types.Part.from_bytes(
                                data=image_bytes,
                                mime_type=mime_type
                            )
                            contents.append(image_part)
                            logger.info(f"Added reference image {i+1} ({mime_type}, {len(image_bytes)} bytes)")
                except Exception as e:
                    logger.warning(f"Failed to process reference image {i+1}: {str(e)}")
            
            # Add the text prompt
            contents.append(prompt)
            
            logger.info(f"Total contents parts: {len(contents)}")
            
            # Generate with multimodal input
            response = self.client.models.generate_content(
                model=model_name,
                contents=contents,
                config={
                    "safety_settings": [
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}, # 
                    ],
                }
            )
            
            # Extract image from response
            image_bytes = None
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_bytes = part.inline_data.data
                        break
            
            if not image_bytes:
                logger.error(f"No image in response. Candidates: {response.candidates}")
                raise Exception("No image data in response")
            
            # Get MIME type
            mime_type = 'image/png'
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        if hasattr(part.inline_data, 'mime_type'):
                            mime_type = part.inline_data.mime_type
                        break
            
            # Process bytes to base64
            if isinstance(image_bytes, bytes):
                prefix = image_bytes[:20]
                is_raw_image = prefix.startswith(b'\x89PNG') or prefix.startswith(b'\xff\xd8')
                
                if is_raw_image:
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                else:
                    try:
                        image_base64 = image_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            elif isinstance(image_bytes, str):
                image_base64 = image_bytes
            else:
                raise Exception(f"Unexpected image data type: {type(image_bytes)}")
            
            # Save to cache
            self._save_image_to_cache(image_base64, "scene", mime_type)
            
            logger.info(f"Scene image generated successfully with references")
            return f"data:{mime_type};base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Scene image generation with references failed: {str(e)}", exc_info=True)
            raise Exception(f"Scene image generation failed: {str(e)}")
    
    def _get_base_style(self, gender: str, description: str = "") -> str:
        """
        Get base style based on gender and age indicators.
        
        Args:
            gender: Character gender
            description: Character description (to check for age)
            
        Returns:
            Base style prompt
        """
        gender_lower = gender.lower()
        desc_lower = description.lower()
        is_female = "female" in gender_lower or "girl" in gender_lower or "woman" in gender_lower
        
        # Default age group
        age_group = "20_30"
        
        # 1. Check explicit age numbers
        import re
        # Match "age 10", "10 years old", "10yo", etc.
        age_match = re.search(r'(?:age\s+|)(\d+)\s*(?:years|yrs|y/o|old)?', desc_lower)
        if age_match:
            try:
                # Add check to ensure the number is actually an age (simple heuristic e.g. < 120)
                # and not "Top 10" or "Year 2024"
                age_str = age_match.group(1)
                # Only trust if followed by explicit age marker OR if explicitly "age X"
                if "year" in age_match.group(0) or "y/o" in age_match.group(0) or "age" in age_match.group(0):
                     age = int(age_str)
                     if age <= 12: age_group = "KID"
                     elif 13 <= age <= 19: age_group = "TEEN"
                     elif 20 <= age <= 39: age_group = "20_30"
                     elif 40 <= age <= 59: age_group = "40_50"
                     elif age >= 60: age_group = "60_70"
            except:
                pass
        
        # 2. Check detected age against keywords (Logic: Keywords override default, but explicit number overrides keywords)
        # But since we set age_group above, we only apply keyword logic if current is '20_30' (default)
        # OR if we want to support keywords like "elderly man" which implies age even if no number.
        
        if age_group == "20_30":
            if any(w in desc_lower for w in ["baby", "infant", "toddler", "child", "kid", "little girl", "little boy"]):
                age_group = "KID"
            elif any(w in desc_lower for w in ["teen", "high school", "student", "youth"]):
                age_group = "TEEN"
            elif any(w in desc_lower for w in ["40s", "50s", "middle age", "middle-aged"]):
                age_group = "40_50"
            elif any(w in desc_lower for w in ["60s", "70s", "elderly", "senior", "grandma", "grandpa", "old man", "old woman"]):
                age_group = "60_70"
        
        # Map to constants
        if is_female:
            return {
                "KID": FEMALE_KID, "TEEN": FEMALE_TEEN, "20_30": FEMALE_20_30,
                "40_50": FEMALE_40_50, "60_70": FEMALE_60_70
            }.get(age_group, FEMALE_20_30)
        else:
            return {
                "KID": MALE_KID, "TEEN": MALE_TEEN, "20_30": MALE_20_30,
                "40_50": MALE_40_50, "60_70": MALE_60_70
            }.get(age_group, MALE_20_30)
    
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
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ],
                }
            )
            
            # Extract image from response - check candidates first
            # Extract image from response - check candidates first
            image_bytes = None
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_bytes = part.inline_data.data
                        break
                    if hasattr(part, 'text') and part.text:
                        logger.warning(f"Text in response instead of image: {part.text[:200]}...")
            
            if not image_bytes:
                logger.error(f"Full response candidate: {response.candidates[0] if response.candidates else 'No candidates'}")
                if response.prompt_feedback:
                    logger.error(f"Prompt feedback: {response.prompt_feedback}")
                raise Exception("No image data in response")
            
            # Get MIME type
            mime_type = 'image/png'  # Default
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        if hasattr(part.inline_data, 'mime_type'):
                            mime_type = part.inline_data.mime_type
                        break
            
            logger.info(f"Image generated successfully")
            logger.info(f"Image data type: {type(image_bytes)}")
            
            # Encode to base64
            image_base64 = ""
            if isinstance(image_bytes, bytes):
                # Check if it's already base64 encoded (simple check for common chars and length)
                # But safer is to assume if it's bytes, it's raw data unless it only contains b64 chars
                logger.info(f"Image bytes length: {len(image_bytes)}")
                prefix = image_bytes[:20]
                logger.info(f"Image bytes prefix: {prefix!r}")
                
                # Signatures
                # PNG Raw: b'\x89PNG'
                # JPEG Raw: b'\xff\xd8'
                # PNG Base64: b'iVBORw0KGgo'
                # JPEG Base64: b'/9j/'
                # WebP Base64: b'UklGR'
                
                is_raw_image = prefix.startswith(b'\x89PNG') or prefix.startswith(b'\xff\xd8')
                is_base64_bytes = prefix.startswith(b'iVBORw0KGgo') or prefix.startswith(b'/9j/') or prefix.startswith(b'UklGR')
                
                if is_raw_image:
                    logger.info("Detected raw image headers. Encoding to base64.")
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                elif is_base64_bytes:
                    logger.info("Detected Base64 signature in bytes. Converting to string.")
                    image_base64 = image_bytes.decode('utf-8')
                else:
                    # Ambiguous case. Previous log showed b'iVBORw0KGgo' which matched is_base64_bytes.
                    # If we fall here, it's something else.
                    # Try to see if it decodes as utf-8 and looks like base64
                    try:
                        as_str = image_bytes.decode('utf-8')
                        # Heuristic: if it has no high bits and no control chars, it's likely base64 text
                        import string
                        # printable = string.printable # includes whitespace
                        # Base64 chars: A-Za-z0-9+/=
                        # Fast check: just use it.
                        logger.info("Ambiguous bytes. Attempting to use as Base64 string.")
                        image_base64 = as_str
                    except UnicodeDecodeError:
                        # Binary data -> Encode
                        logger.info("Ambiguous bytes failed UTF-8 decode. Treating as raw binary.")
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

            elif isinstance(image_bytes, str):
                logger.info("Image data is string, using as is (assuming base64).")
                image_base64 = image_bytes
            else:
                 logger.warning(f"Unexpected image data type: {type(image_bytes)}")
                 image_base64 = str(image_bytes)

            logger.info(f"MIME type: {mime_type}")
            logger.info(f"Base64 length: {len(image_base64)}")
            
            # Save image to cache folder
            file_path = self._save_image_to_cache(image_base64, character_name, mime_type)
            logger.info(f"Image saved to cache: {file_path}")
            
            # Return as data URL with correct MIME type
            return f"data:{mime_type};base64,{image_base64}"
                
        except Exception as e:
            logger.error(f"Gemini image generation failed: {str(e)}")
            raise
    
    def _save_image_to_cache(self, image_base64: str, character_name: str, mime_type: str) -> str:
        """
        Save a generated image to the cache folder.
        
        Args:
            image_base64: Base64 encoded image data
            character_name: Name of the character
            mime_type: MIME type of the image
            
        Returns:
            Path to the saved image file
        """
        try:
            # Determine file extension from MIME type
            ext_map = {
                'image/png': 'png',
                'image/jpeg': 'jpg',
                'image/webp': 'webp',
            }
            ext = ext_map.get(mime_type, 'png')
            
            # Generate unique filename
            safe_name = "".join(c if c.isalnum() else "_" for c in character_name)
            filename = f"{safe_name}_{uuid.uuid4().hex[:8]}.{ext}"
            file_path = CACHE_DIR / filename
            
            # Decode base64 and save to file
            image_bytes = base64.b64decode(image_base64)
            
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            logger.info(f"Image saved to cache: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to save image to cache: {str(e)}")
            return ""
    
# Global image generator instance
image_generator = ImageGenerator()
