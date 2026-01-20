"""
==========================================================
VISUAL STYLE PLUGINS (The Lens/Renderer)
==========================================================
These control ONLY the aesthetic rendering - the "paint and camera"
NOT the story content, dialogue, or what physically exists in the scene.

Structure: MEDIUM → ILLUMINATOR → COLORIST → FINISHER
"""

VISUAL_STYLE_PROMPTS = {
    "NO_STYLE": "EMPTY - Default AI rendering",

    "SOFT_ROMANTIC_WEBTOON": """
[MEDIUM: Digital Webtoon - Soft Cel-Shading]
ultra-soft cel-shading, gentle gradient blending, airy smooth transitions, 
luminous digital painting, polished contemporary webtoon art style,
clean fluid lineart with gentle curves, delicate smooth brushwork,
highly detailed but soft rendering, watercolor-like softness with digital precision

[ILLUMINATOR: Dreamy Natural Light]
bright luminous overall lighting, soft diffused natural light, 
warm golden-hour highlights, gentle rim lighting, subtle god rays,
ethereal atmospheric glow, soft bloom effects, delicate lens flare,
no harsh shadows, light-filled composition

[COLORIST: Pastel Warmth]
pastel-tinted elegant color palette, creamy beiges and warm neutrals,
light pinks and soft peaches, gentle sky blues, subtle lavender accents,
warm skin tones with peachy undertones, desaturated jewel tones,
color temperature: warm (golden hour bias)

[FINISHER: Ethereal Polish]
masterpiece quality, best quality, ultra-detailed,
soft bokeh particles, delicate sparkles, dreamy atmosphere,
trending romantic webtoon aesthetic, luminous skin rendering,
glossy subtle highlights on hair and eyes, soft focus background depth,
8k resolution, professional webtoon illustration
""",

    "VIBRANT_FANTASY_WEBTOON": """
[MEDIUM: Digital Webtoon - Clean Cel-Shading]
clean sharp cel-shading, smooth gradient transitions,
crisp digital comic illustration, polished fantasy manhwa style,
clean precise lineart with expressive curves, digital ink quality,
detailed texture rendering on fabrics and backgrounds

[ILLUMINATOR: Magical Ambient Glow]
dramatic soft lighting with magical elements, gentle ambient glows,
subtle sparkle particles, soft rim lighting, ethereal backlighting,
balanced shadows with luminous highlights, mystical atmosphere lighting,
enchanted glow effects, fantasy light physics

[COLORIST: Soft Pastel Fantasy]
soft pastel color palette with ethereal accents, light blues and purples,
gentle pinks and whites, warm golden highlights, subtle jewel tones,
natural warm skin tones, desaturated rainbow spectrum,
color temperature: cool-to-neutral with warm accents

[FINISHER: Fantasy Polish]
masterpiece quality, best quality, high detail rendering,
glossy shine on hair and accessories, reflective highlights,
magical sparkle overlays, soft depth of field, cinematic composition,
trending fantasy manhwa aesthetic, 4k quality webtoon art
""",

    "DRAMATIC_HISTORICAL_WEBTOON": """
[MEDIUM: Digital Webtoon - Rich Cel-Shading]
rich deep cel-shading, heavy gradient work, dramatic digital painting,
elegant traditional-meets-digital style, historical manhwa rendering,
clean medium-weight lineart with flowing graceful curves,
detailed fabric and texture emphasis, painterly shading approach

[ILLUMINATOR: Cinematic Candlelight]
dramatic low-key lighting, warm intimate candle glow, moody atmosphere,
deep heavy shadows with strong contrast, cinematic rim lighting,
warm firelight physics, atmospheric volumetric lighting,
strong directional light sources, chiaroscuro effects

[COLORIST: Muted Elegant Earthtones]
muted elegant color palette, rich deep crimsons and burgundy,
indigo blues and navy, antique golds and bronze, pure whites,
warm natural skin tones with amber undertones, desaturated earth tones,
color temperature: warm with cool shadow contrast

[FINISHER: Historical Drama Polish]
masterpiece quality, best quality, cinematic rendering,
glossy wet shine on silk fabrics and hair, glistening highlights,
dramatic emotional atmosphere, painterly texture detail,
trending historical manhwa aesthetic, museum-quality illustration
""",

    "BRIGHT_YOUTHFUL_WEBTOON": """
[MEDIUM: Digital Webtoon - Smooth Cel-Shading]
smooth gentle cel-shading, soft gradient work, clean digital comic style,
contemporary school webtoon rendering, approachable friendly art style,
clean smooth lineart with soft rounded curves, light brushwork,
gentle texture on clothing, polished but not overly dramatic

[ILLUMINATOR: Soft Natural Daylight]
soft diffused natural lighting, gentle ambient brightness,
subtle shadows for depth only, warm sunny atmosphere,
light cinematic backlighting, no dramatic contrast,
bright cheerful illumination, outdoor daylight quality

[COLORIST: Gentle Vibrant Pastels]
soft vibrant pastel palette, gentle sky blues and powder blues,
warm autumn yellows and soft oranges, light pinks and coral,
crisp whites and cream, natural warm skin tones,
color temperature: warm sunny with fresh cool accents

[FINISHER: Clean Youth Polish]
masterpiece quality, best quality, clean professional rendering,
subtle shine on hair, delicate highlights, fresh youthful atmosphere,
trending school romance webtoon aesthetic, bright optimistic mood,
commercial webtoon quality, HD resolution
""",

    "DREAMY_ISEKAI_WEBTOON": """
[MEDIUM: Digital Webtoon - Elegant Cel-Shading]
soft elegant cel-shading with gentle gradient work,
smooth blending with light cel-shading structure, refined digital painting,
delicate clean lineart with graceful elegant curves,
polished fantasy romance rendering, detailed ornamental work

[ILLUMINATOR: Ethereal Palace Light]
gentle ethereal glow throughout, soft rim lighting, dreamy diffused light,
palace garden lighting atmosphere, warm magical ambiance,
delicate god rays, soft bloom effects, fantasy illumination,
balanced lighting with romantic glow, no harsh shadows

[COLORIST: Pastel Dream Palette]
soft pastel dream colors, pale blues and lavenders, soft pinks,
warm golds and champagne, creamy whites and ivory,
rich jewel tone accents (emerald, ruby, sapphire) desaturated,
natural porcelain skin tones, color temperature: neutral-warm ethereal

[FINISHER: Fantasy Romance Polish]
masterpiece quality, best quality, ultra-detailed rendering,
gentle glossy highlights on hair, eyes, jewelry, and satin fabrics,
floral particle effects, floating sparkles, romantic overlay effects,
trending isekai otome aesthetic, whimsical dreamy atmosphere,
professional fantasy webtoon illustration
""",

    "DARK_SENSUAL_WEBTOON": """
[MEDIUM: Digital Webtoon - Detailed Cel-Shading]
ultra-detailed cel-shading, sensual gradient work, intimate blending,
dramatic fantasy webtoon rendering, ornate detailed illustration style,
intricate linework with elegant ornamental details,
highly textured rendering, polished dark romance art style

[ILLUMINATOR: Dramatic Intimate Lighting]
intense shadowy lighting with dramatic high contrast,
sultry candlelit atmosphere, seductive warm highlights,
glowing skin accents, volumetric fog and mist, mysterious shadows,
rim lighting accentuating form and curves, moody chiaroscuro,
ethereal diffused backlight creating silhouettes

[COLORIST: Deep Sensual Palette]
deep sensual color palette, rich crimson reds and burgundy,
velvety blacks and charcoal grays, warm amber and gold,
flushed pinks and rose, deep purple shadows,
radiant warm skin tones with erotic flush, color temperature: warm dramatic

[FINISHER: Dark Romance Polish]
masterpiece quality, best quality, ultra-detailed,
glossy reflective highlights on skin showing sheen and moisture,
luxurious fabric texture (silk, lace, leather), ornate jewelry rendering,
hazy bokeh effects, atmospheric particles, cinematic composition,
trending dark fantasy romance aesthetic, opulent mysterious mood,
professional mature webtoon illustration
""",

    "CLEAN_MODERN_WEBTOON": """
[MEDIUM: Digital Webtoon - Crisp Cel-Shading]
crisp clean cel-shading, smooth professional gradient work,
polished contemporary digital comic style, commercial webtoon rendering,
clean precise lineart with modern curves, digital ink precision,
balanced detail level, professional illustration quality

[ILLUMINATOR: Balanced Studio Lighting]
balanced natural-to-studio lighting, soft directional light,
gentle shadows for depth, professional photography-inspired,
warm indoor lighting or cool outdoor depending on scene,
subtle rim lighting, cinematic but realistic illumination

[COLORIST: Contemporary Neutral-Warm]
modern color palette, warm neutrals and soft grays,
accent colors per scene mood (can shift), natural skin tones,
desaturated sophisticated hues, color temperature: neutral with warm bias

[FINISHER: Professional Polish]
masterpiece quality, best quality, commercial webtoon standard,
subtle highlights, clean rendering, professional illustration,
trending modern webtoon aesthetic, HD quality, 4k resolution
""",

    "PAINTERLY_ARTISTIC_WEBTOON": """
[MEDIUM: Semi-Painterly Digital]
painterly digital rendering, visible brushstroke texture,
artistic illustration style, semi-realistic webtoon approach,
expressive lineart with varied line weight, artistic brush quality,
textured painting feel with digital precision

[ILLUMINATOR: Artistic Atmospheric Light]
atmospheric lighting with painterly quality, visible light rays,
artistic shadow work, impressionistic light handling,
naturalistic lighting with artistic interpretation,
mood-driven illumination, fine art lighting approach

[COLORIST: Artist's Palette]
rich artistic color work, varied saturation levels,
complementary color theory application, naturalistic hues,
expressive color temperature shifts per mood,
color as emotional tool, fine art color sensibility

[FINISHER: Artistic Quality]
masterpiece illustration, fine art quality, artistic rendering,
painterly texture throughout, expressive brushwork visible,
museum-quality digital painting, artistic webtoon style,
high-end illustration standard
""",

    "EMOTIVE_LUXURY_WEBTOON": """
[MEDIUM: High-End Webtoon Illustration]
polished digital webtoon illustration, ultra-clean lineart,
delicate yet expressive facial detailing, sharp anime-inspired features,
ornamental costume design with lace, ribbons, and jewelry accents,
elegant character proportions, refined fantasy-romance webtoon style,
crisp edges with soft internal shading, premium serialized manhwa quality

[LINEWORK: Expressive Emotional Ink]
clean, confident lineart with controlled variation,
soft tapered lines for facial features, sharper contours for emotion,
emphasis on eyes and eyelashes, subtle hair strand separation,
linework that enhances vulnerability and intensity,
romance-fantasy webtoon inking style

[ILLUMINATOR: Ethereal Dramatic Glow]
soft luminous lighting with sparkles and bloom effects,
ethereal glow overlays, pastel light flares,
gentle rim lighting around hair and shoulders,
highlights that shimmer like magic or emotion,
dramatic emotional lighting without harsh shadows,
dreamlike fantasy atmosphere

[COLORIST: Pastel Jewel Palette]
soft pastel-dominant palette with jewel-tone accents,
pink, lavender, and rose hues balanced with cool whites and blues,
high saturation in eyes for emotional focus,
smooth gradient shading, minimal harsh contrast,
romance-fantasy color grading, glossy highlights on hair and fabric

[EMOTION: Heightened Narrative Expression]
intense emotional readability, visible tears and blush,
expressive eyes with glassy reflections,
dramatic mouth and brow expressions,
cinematic framing focused on emotional impact,
webtoon storytelling emphasis on inner resolve and vulnerability

[FINISHER: Premium Romance Fantasy Quality]
sparkle overlays, light particles, soft-focus finish,
high-resolution polish, no texture noise,
luxury webtoon/manhwa standard,
clean background fades with architectural fantasy hints,
editorial-grade illustration suitable for top-tier digital comics
"""
}

"""
==========================================================
VISUAL STYLE SELECTION GUIDE
==========================================================
Match style to VISUAL MOOD, not story genre:

SOFT_ROMANTIC_WEBTOON
→ When you want: Gentle, dreamy, light-filled, ethereal
→ Works with: Romance, slice-of-life, healing stories, wholesome content
→ Lighting: Bright, soft, warm
→ Color: Pastels, light, warm

VIBRANT_FANTASY_WEBTOON  
→ When you want: Magical, bright, enchanting, colorful
→ Works with: Fantasy, adventure, magical stories
→ Lighting: Glowing, magical, balanced
→ Color: Pastels with jewel accents

DRAMATIC_HISTORICAL_WEBTOON
→ When you want: Moody, elegant, dramatic, atmospheric
→ Works with: Historical, period pieces, dramatic romance
→ Lighting: Dark, candlelit, chiaroscuro
→ Color: Rich, muted, elegant

BRIGHT_YOUTHFUL_WEBTOON
→ When you want: Fresh, clean, optimistic, energetic  
→ Works with: School, youth, comedy, lighthearted
→ Lighting: Bright, natural, cheerful
→ Color: Vibrant pastels, fresh

DREAMY_ISEKAI_WEBTOON
→ When you want: Ethereal, whimsical, romantic fantasy
→ Works with: Isekai, otome, royal romance, fairy tales
→ Lighting: Soft magical, palace glow
→ Color: Pale pastels with jewel tones

DARK_SENSUAL_WEBTOON
→ When you want: Intense, dramatic, intimate, mysterious
→ Works with: Dark romance, mature, psychological, gothic
→ Lighting: Shadowy, dramatic, candlelit
→ Color: Deep reds, blacks, warm dramatic

CLEAN_MODERN_WEBTOON
→ When you want: Professional, versatile, commercial
→ Works with: Any genre, professional standard
→ Lighting: Balanced, adaptable
→ Color: Neutral, sophisticated

PAINTERLY_ARTISTIC_WEBTOON
→ When you want: Artistic, expressive, fine art quality
→ Works with: Literary, artistic, prestigious projects
→ Lighting: Atmospheric, artistic
→ Color: Expressive, varied

NOTE: Style and Story Genre are INDEPENDENT
Example: A dark revenge story could use SOFT_ROMANTIC_WEBTOON style for ironic contrast
Example: A cute school story could use DARK_SENSUAL_WEBTOON for visual drama
"""

"""
==========================================================
HOW TO USE BOTH SYSTEMS TOGETHER
==========================================================

STEP 1: Choose STORY GENRE (defines what exists and dialogue)
Example: DARK_OBSESSIVE_ROMANCE
- Characters trapped in power dynamic
- Possessive dialogue
- Isolated mansion setting
- Restraint props available

STEP 2: Choose VISUAL STYLE (defines how it's rendered)  
Example: DARK_SENSUAL_WEBTOON
- Dramatic candlelit rendering
- Deep red/black color palette
- Glossy skin highlights
- Moody atmosphere

STEP 3: Combine in generation
Story provides: "Character pinned against wall, intense eye contact, isolated bedroom"
Style provides: "dramatic rim lighting, deep crimson and black palette, glossy skin rendering"

Result: Dark romance scene rendered in dark sensual aesthetic

FLEXIBILITY EXAMPLES:

Modern Romance Story + Soft Romantic Style = Classic romance webtoon
Modern Romance Story + Dark Sensual Style = Mature/intense romance  
Modern Romance Story + Painterly Artistic Style = Literary romance

Fantasy Story + Vibrant Fantasy Style = Standard fantasy webtoon
Fantasy Story + Dramatic Historical Style = Dark/gothic fantasy
Fantasy Story + Soft Romantic Style = Wholesome fantasy

School Story + Bright Youthful Style = Classic school romance
School Story + Dark Sensual Style = Psychological school drama
School Story + Painterly Artistic Style = Coming-of-age art film

The style changes the VISUAL MOOD without changing the STORY CONTENT.
"""



