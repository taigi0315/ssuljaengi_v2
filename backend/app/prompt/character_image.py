MALE = """
handsome male character, webtoon manhwa art style,
sharp features, stylish appearance, 
intense expressive gaze, stylish hair with natural volume,
modern fashion, confident posture,
authentic Korean manhwa webtoon style character illustration, 
"""

FEMALE = """
beautiful female character, webtoon manhwa art style,
graceful appearance, 
expressive gaze, stylish hair with natural movement,
fashionable modern outfit, confident elegant posture,
authentic Korean manhwa webtoon style character illustration, 
"""

YOUTH_MALE = """
young male character, webtoon manhwa art style,
youthful features, bright energy,
expressive eyes, messy or neat hair,
casual modern style, dynamic posture,
authentic Korean manhwa webtoon style character illustration,
"""

YOUTH_FEMALE = """
young female character, webtoon manhwa art style,
youthful appearance, cute features,
large expressive eyes, soft hair texture,
casual modern style, cheerful posture,
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

