MALE = """
handsome Korean man, webtoon manhwa art style,
sharp chiseled jawline, high cheekbones, 
intense piercing gaze, stylish hair with natural volume,
form-fitting modern fashion, confident posture,
authentic Korean manhwa webtoon style character illustration, 
"""

FEMALE = """
beautiful woman, webtoon manhwa art style,
graceful elegant appearance, 
alluring gaze, stylish hair with natural movement,
fashionable modern outfit, confident elegant posture,
authentic Korean manhwa webtoon style character illustration, 
"""

CHARACTER_IMAGE_TEMPLATE = """
full body front view, largest and most prominent, 
masterpiece best quality professional Naver webtoon illustration

BASE_STYLE: {gender_style}

CHARACTER_DETAILS (USE THESE EXACT DESCRIPTIONS):
{character_description}

ART_STYLE_REFERENCE: {genre_style}

IMPORTANT: Follow the CHARACTER_DETAILS exactly for body type, height, and build.
Do not add conflicting physical attributes.

NEGATIVE: text, watermark, signature, logo, conflicting descriptions
"""

# CHARACTER_IMAGE_TEMPLATE EXAMPLE
# BASE_STYLE = {MALE}

# CHARACTER_DETAILS = {DESCRIPTION FROM LLM RESPONSE}

# ART_STYLE_REFERENCE = {GENRE_STYLE FROM image_mood.py}

