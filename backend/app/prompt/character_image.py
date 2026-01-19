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
childlike innocent features, large expressive eyes with bright highlights,
round cherubic face, soft pudgy cheeks, small petite stature,
short limbs, playful energetic posture, messy or neat styled hair,
colorful casual children's clothes (t-shirt, shorts, sneakers),
authentic webtoon style character illustration,
chibi-like proportions, head-to-body ratio 1:3, youthful innocence
"""

MALE_TEEN = """
teenage boy character, webtoon manhwa art style,
youthful angular features beginning to mature, sharp jawline developing,
trendy Korean-style haircut (side-swept, layered, or textured),
bright expressive eyes, clear unblemished skin, lean athletic build,
tall slender frame, long limbs, school uniform (blazer, dress shirt, slacks) or trendy streetwear,
authentic webtoon style character illustration,
energetic confident posture, height around 170-180cm proportions
"""

MALE_20_30 = """
handsome chiseled features, mature but youthful appearance,
sharp defined jawline, stylish contemporary hair (undercut, pompadour, or textured),
confident intense gaze, fit athletic build with broad shoulders,
very tall elegant stature over 180cm, long powerful legs, long athletic torso,
statuesque model-like figure, elongated graceful proportions,
contemporary adult fashion (tailored suit, business casual, or modern streetwear),
authentic webtoon style character illustration,
flawless skin, commanding presence, perfect posture
"""

MALE_40_50 = """
distinguished middle-aged male character, webtoon manhwa art style,
mature refined features, subtle crow's feet, slight nasolabial folds,
dignified commanding presence, well-groomed appearance (neat hair, possible grey streaks),
strong build with slight weight in torso, broad shoulders maintained,
professional business attire or sophisticated casual wear,
authentic webtoon style character illustration,
stable grounded posture, height around 175-185cm proportions,
authoritative yet approachable expression, experienced worldly look
"""

MALE_60_70 = """
elderly distinguished male character, webtoon manhwa art style,
aged weathered features, prominent wrinkles and laugh lines,
grey or white hair (balding, receding, or full head), wise penetrating eyes,
grandfatherly or patriarch appearance, slightly stooped but dignified posture,
comfortable classic clothing (cardigan, slacks, traditional wear),
authentic webtoon style character illustration,
shorter stature around 165-175cm, slightly rounded shoulders,
gentle or stern expression showing life experience, warm or authoritative presence
"""

#--------------------------------------------------------------------

FEMALE_KID = """
cute little girl, webtoon manhwa art style,
childlike innocent features, oversized sparkly eyes with long lashes,
round cherubic face, rosy plump cheeks, button nose, small petite stature,
short limbs, adorable playful posture, cute hairstyle (pigtails, bob, or ponytail with ribbons),
colorful dress, skirt, or casual children's outfit with bright colors,
authentic webtoon style character illustration,
chibi-like proportions, head-to-body ratio 1:3, innocent charming expression
"""

FEMALE_TEEN = """
teenage girl character, webtoon manhwa art style,
youthful fresh features, large expressive doe eyes with delicate lashes,
smooth clear skin with natural blush, cute button nose,
trendy hairstyle (long straight, soft waves, or side-swept bangs),
slender developing figure, long slim legs, petite frame,
school uniform (blouse, pleated skirt, knee socks) or trendy teen fashion,
authentic webtoon style character illustration,
height around 160-170cm proportions, graceful youthful posture,
bright innocent yet stylish expression, emerging beauty
"""

FEMALE_20_30 = """
tall elegant stature over 165cm, statuesque supermodel-like figure, 
extremely long toned legs (leg length exceeding torso), dramatically elongated graceful proportions,
long elegant torso, perfect upright posture, hourglass silhouette with prominent natural breasts,
full voluptuous bust, narrow defined waist, wide feminine hips, sexy mature curves,
flawless glossy porcelain skin, stunning beautiful facial features,
seductive confident expression, alluring intense gaze, glamorous makeup,
luxurious flowing hair (long wavy, sleek straight, or voluminous styled),
modern chic fashion highlighting long legs and bust (bodycon dress, tailored suit, or elegant casual),
authentic webtoon style character illustration,
sophisticated powerful presence, in realistic human proportions with no cartoon exaggeration
"""

FEMALE_40_50 = """
mature elegant female character, webtoon manhwa art style,
refined beautiful features showing graceful aging, subtle fine lines around eyes,
sophisticated appearance, well-maintained figure with feminine curves,
elegant styled hair (shoulder-length bob, soft waves, possible tasteful grey highlights),
motherly warm presence or professional commanding aura,
business professional attire or sophisticated elegant fashion,
authentic webtoon style character illustration,
height around 160-170cm proportions, composed dignified posture,
confident experienced expression, timeless beauty with character,
narrow waist maintained, mature hourglass figure
"""

FEMALE_60_70 = """
elderly distinguished female character, webtoon manhwa art style,
aged graceful features, visible wrinkles and smile lines showing wisdom,
grey or white hair (elegant updo, short styled, or soft curls),
kind gentle eyes or strict authoritative gaze, grandmotherly presence,
softer rounder figure with dignified bearing, slightly hunched but noble posture,
classic comfortable clothing (traditional hanbok, cardigan sets, or elegant simple dresses),
authentic webtoon style character illustration,
height around 155-165cm proportions, gentle or firm expression,
warm nurturing or strict matriarch aura, face showing life's journey
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

