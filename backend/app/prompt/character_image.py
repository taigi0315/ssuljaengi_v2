# GENERAL GENDER DESCRIPTIONS
# ====================================================================

MALE = """
handsome male character, webtoon manhwa art style,
sharp features, stylish appearance, 
intense expressive gaze, stylish hair with natural volume,
modern fashion, confident posture,
authentic webtoon style character illustration, 
"""

FEMALE = """
beautiful female character, webtoon manhwa art style,
graceful appearance, 
expressive gaze, stylish hair with natural movement,
fashionable modern outfit, confident elegant posture,
authentic webtoon style character illustration, 
"""

# ====================================================================

# AGE GROUP DESCRIPTIONS

MALE_KID = """
cute little boy, webtoon manhwa art style,
childlike innocent features, big expressive eyes,
round face, soft cheeks, small stature,
playful energy, colorful casual clothes,
authentic webtoon style character illustration,
"""
MALE_TEEN = """
teenage boy character, webtoon manhwa art style,
high school student look, fresh youthful energy,
trendy hairstyle, sharp but young features,
school uniform or trendy street fashion, lean build,
authentic webtoon style character illustration,
"""
MALE_20_30 = """
handsome features, mature but youthful,
stylish hair, confident expression, fit build,
contemporay adult fashion, professional or casual chic,
authentic webtoon style character illustration,
very tall elegant stature, long legs, long torso, statuesque model-like figure, elongated graceful proportions
"""
MALE_40_50 = """
middle-aged male character, webtoon manhwa art style,
mature facial features, slight laugh lines, dignified presence,
professional or fatherly appearance, well-groomed,
business casual or mature fashion, stable posture,
authentic webtoon style character illustration,
"""
MALE_60_70 = """
elderly male character, webtoon manhwa art style,
aged features, wrinkles, grey or white hair,
wise or stern expression, grandfatherly figure,
classic or comfortable clothing, slower posture,
authentic webtoon style character illustration,
"""

#--------------------------------------------------------------------

FEMALE_KID = """
cute little girl, webtoon manhwa art style,
childlike innocent features, big sparkly eyes,
round face, rosy cheeks, small petite stature,
adorable appearance, colorful dress or casual clothes,
authentic webtoon style character illustration,
"""
FEMALE_TEEN = """
teenage girl character, webtoon manhwa art style,
high school student look, fresh youthful charm,
trendy hairstyle, bright expressive eyes,
school uniform or trendy teen fashion, slender build,
authentic webtoon style character illustration,
"""
FEMALE_20_30 = """
tall elegant stature over 165cm, statuesque supermodel-like figure, extremely long toned legs (leg length exceeding torso),
dramatically elongated graceful proportions, long elegant torso, perfect posture, hourglass silhouette with prominent nice natural breasts,
full voluptuous bust, narrow waist, wide hips, sexy mature curves, flawless glossy skin, seductive confident expression, 
modern chic fashion highlighting long legs and bust, in authentic webtoon style with realistic human proportions and no exaggeration
"""
FEMALE_40_50 = """
middle-aged female character, webtoon manhwa art style,
mature beauty, elegant aging, slight fine lines,
motherly or professional appearance, sophisticated style,
business casual or elegant fashion, composed posture,
authentic webtoon style character illustration,
"""
FEMALE_60_70 = """
elderly female character, webtoon manhwa art style,
aged features, wrinkles, grey or white hair,
kind or strict grandmotherly expression,
classic or comfortable clothing, gentle posture,
authentic webtoon style character illustration,
"""

# ====================================================================

# CHARACTER IMAGE TEMPLATE

CHARACTER_IMAGE_TEMPLATE = """
**CRITICAL ASPECT RATIO: VERTICAL 9:16 (Portrait Mode)**
- This MUST be a tall vertical image, NOT square, NOT horizontal
- Height significantly greater than width (ratio 9:16)
- Optimized for mobile vertical scrolling webtoon format

full body front view, largest and most prominent, 
masterpiece best quality professional Naver webtoon illustration,
vertical portrait orientation, tall format, 9:16 aspect ratio

BASE_STYLE: {gender_style}

CHARACTER_DETAILS (USE THESE EXACT DESCRIPTIONS):
{character_description}

ART_STYLE_REFERENCE: {genre_style}

IMPORTANT: 
- Follow the CHARACTER_DETAILS exactly for body type, height, and build
- Do not add conflicting physical attributes
- Image MUST be vertical 9:16 ratio (portrait mode)

NEGATIVE: text, watermark, signature, logo, conflicting descriptions, square image, 1:1 ratio, horizontal image, landscape orientation
"""

# CHARACTER_IMAGE_TEMPLATE EXAMPLE
# BASE_STYLE = {MALE}

# CHARACTER_DETAILS = {DESCRIPTION FROM LLM RESPONSE}

# ART_STYLE_REFERENCE = {GENRE_STYLE FROM image_mood.py}

