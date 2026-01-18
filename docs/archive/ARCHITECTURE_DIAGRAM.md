# Architecture Diagram - Character Image Generation System

## Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE (Next.js)                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────┐                    ┌──────────────────────────┐  │
│  │  Character List  │                    │  Character Image Display │  │
│  │    (30% width)   │                    │       (70% width)        │  │
│  ├──────────────────┤                    ├──────────────────────────┤  │
│  │ • Ji-hoon [3]    │◄───Select────────► │ Name: Ji-hoon            │  │
│  │ • Hana [1]       │                    │                          │  │
│  │ • Min-soo [0]    │                    │ ┌──────────────────────┐ │  │
│  └──────────────────┘                    │ │ Gender: [male      ] │ │  │
│                                           │ │ Face:   [sharp jaw ] │ │  │
│                                           │ │ Hair:   [black hair] │ │  │
│                                           │ │ Body:   [athletic  ] │ │  │
│                                           │ │ Outfit: [navy suit ] │ │  │
│                                           │ │ Mood:   [confident ] │ │  │
│                                           │ └──────────────────────┘ │  │
│                                           │                          │  │
│                                           │ Combined Preview:        │  │
│                                           │ [male, sharp jaw, ...]   │  │
│                                           │                          │  │
│                                           │ Select Image Style:      │  │
│                                           │ ┌────┐ ┌────┐ ┌────┐   │  │
│                                           │ │Hist│ │Fant│ │Mod │   │  │
│                                           │ │ ✓  │ │    │ │    │   │  │
│                                           │ └────┘ └────┘ └────┘   │  │
│                                           │                          │  │
│                                           │ [🎨 Generate Image]      │  │
│                                           │                          │  │
│                                           │ Generated Images:        │  │
│                                           │ [Image 1/3] ◄ ►         │  │
│                                           └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP POST /webtoon/character/image
                                    │ {
                                    │   script_id, character_name,
                                    │   description, gender, image_style
                                    │ }
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        BACKEND API (FastAPI)                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Webtoon Router                                │   │
│  │  /webtoon/character/image                                        │   │
│  └────────────────────────┬────────────────────────────────────────┘   │
│                           │                                              │
│                           │ Call generate_character_image()              │
│                           ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                  Image Generator Service                         │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │                                                                   │   │
│  │  1. Select Base Style                                            │   │
│  │     ┌─────────────────────────────────────────┐                 │   │
│  │     │ if "male" in gender and "female" not:   │                 │   │
│  │     │   base_style = YOUTH_MALE               │                 │   │
│  │     │ elif "female" in gender:                │                 │   │
│  │     │   base_style = YOUTH_FEMALE             │                 │   │
│  │     └─────────────────────────────────────────┘                 │   │
│  │                                                                   │   │
│  │  2. Get Image Style Prompt                                       │   │
│  │     ┌─────────────────────────────────────────┐                 │   │
│  │     │ image_styles = {                        │                 │   │
│  │     │   "HISTORY_SAGEUK_ROMANCE": prompt1,    │                 │   │
│  │     │   "ISEKAI_OTOME_FANTASY": prompt2,      │                 │   │
│  │     │   "MODERN_KOREAN_ROMANCE": prompt3      │                 │   │
│  │     │ }                                        │                 │   │
│  │     │ image_style_prompt = image_styles[id]   │                 │   │
│  │     └─────────────────────────────────────────┘                 │   │
│  │                                                                   │   │
│  │  3. Build Final Prompt                                           │   │
│  │     ┌─────────────────────────────────────────┐                 │   │
│  │     │ CHARACTER_IMAGE template:               │                 │   │
│  │     │                                          │                 │   │
│  │     │ BASE_STYLE: {{base_style}}              │                 │   │
│  │     │ ↓                                        │                 │   │
│  │     │ [YOUTH_MALE or YOUTH_FEMALE prompt]     │                 │   │
│  │     │                                          │                 │   │
│  │     │ CHARACTER_DESCRIPTION: {{description}}  │                 │   │
│  │     │ ↓                                        │                 │   │
│  │     │ [Combined from user fields]             │                 │   │
│  │     │                                          │                 │   │
│  │     │ IMAGE_STYLE: {{image_style}}            │                 │   │
│  │     │ ↓                                        │                 │   │
│  │     │ [Selected mood prompt]                  │                 │   │
│  │     └─────────────────────────────────────────┘                 │   │
│  │                                                                   │   │
│  │  4. Generate Image (TODO: Replace placeholder)                  │   │
│  │     ┌─────────────────────────────────────────┐                 │   │
│  │     │ # Current: Placeholder                  │                 │   │
│  │     │ return ui-avatars.com URL               │                 │   │
│  │     │                                          │                 │   │
│  │     │ # Future: Real AI Generation            │                 │   │
│  │     │ response = ai_service.generate(         │                 │   │
│  │     │   prompt=final_prompt                   │                 │   │
│  │     │ )                                        │                 │   │
│  │     │ return response.image_url               │                 │   │
│  │     └─────────────────────────────────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Prompt Template Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                      FINAL PROMPT COMPOSITION                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ BASE_STYLE (Selected by Gender)                             │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                                                               │   │
│  │  YOUTH_MALE:                                                 │   │
│  │  • youthful handsome Korean man                              │   │
│  │  • very tall elegant stature 188cm                           │   │
│  │  • statuesque supermodel-like male figure                    │   │
│  │  • extremely long toned legs                                 │   │
│  │  • dramatically elongated graceful proportions               │   │
│  │  • broad shoulders narrow waist sharp V-shaped torso         │   │
│  │  • flawless glossy skin with subtle natural sheen            │   │
│  │  • sharp chiseled jawline, high cheekbones                   │   │
│  │  • intense piercing seductive gaze                           │   │
│  │  • half-lidded smoldering eyes                               │   │
│  │  • subtle rosy cheek flush                                   │   │
│  │  • confident slight smirk or teasing expression              │   │
│  │  • wind-swept stylish hair with movement                     │   │
│  │  • modern chic form-fitting fashion                          │   │
│  │  • perfect confident posture with slight swagger             │   │
│  │  • authentic Korean manhwa webtoon style                     │   │
│  │  • full body, front view largest and most prominent          │   │
│  │  • subtle glossy highlights on hair skin lips clothing       │   │
│  │  • warm cinematic golden hour lighting                       │   │
│  │  • soft rim light, soft bokeh background                     │   │
│  │  • masterpiece, best quality, professional Naver webtoon     │   │
│  │                                                               │   │
│  │  YOUTH_FEMALE:                                               │   │
│  │  • youthful beautiful Korean woman                           │   │
│  │  • very tall elegant stature 178cm                           │   │
│  │  • supermodel-like figure                                    │   │
│  │  • extremely long toned legs                                 │   │
│  │  • dramatically elongated graceful proportions               │   │
│  │  • hourglass silhouette with prominent large natural breasts │   │
│  │  • narrow waist, wide hips                                   │   │
│  │  • flawless glossy skin                                      │   │
│  │  • alluring and seductive atmosphere                         │   │
│  │  • intense smoldering half-lidded gaze                       │   │
│  │  • subtle rosy cheek flush                                   │   │
│  │  • confident teasing yet shy inviting expression             │   │
│  │  • wind-swept long flowing hair                              │   │
│  │  • modern chic form-fitting fashion                          │   │
│  │  • deep cleavage, perfect posture                            │   │
│  │  • authentic Korean manhwa webtoon style                     │   │
│  │  • full body turnaround reference sheet                      │   │
│  │  • front view largest and most prominent                     │   │
│  │  • soft digital cel-shading                                  │   │
│  │  • gentle warm+cool gradient shadows                         │   │
│  │  • subtle glossy highlights on hair skin lips clothing       │   │
│  │  • warm cinematic golden hour lighting                       │   │
│  │  • soft rim light, soft bokeh background                     │   │
│  │  • masterpiece, best quality, ultra-detailed                 │   │
│  │  • professional Naver webtoon illustration style             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ CHARACTER_DESCRIPTION (From User Input)                      │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                                                               │   │
│  │  Combined from individual fields:                            │   │
│  │  • gender: "male"                                            │   │
│  │  • face: "sharp jawline, dark brown eyes, olive skin"        │   │
│  │  • hair: "short black hair, neatly styled"                   │   │
│  │  • body: "tall athletic build, broad shoulders"              │   │
│  │  • outfit: "tailored navy suit with white shirt"             │   │
│  │  • mood: "confident and charismatic"                         │   │
│  │                                                               │   │
│  │  Result:                                                      │   │
│  │  "male, sharp jawline, dark brown eyes, olive skin,          │   │
│  │   short black hair neatly styled, tall athletic build,       │   │
│  │   broad shoulders, wearing tailored navy suit with white     │   │
│  │   shirt, confident and charismatic"                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ IMAGE_STYLE (Selected by User)                               │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                                                               │   │
│  │  HISTORY_SAGEUK_ROMANCE:                                     │   │
│  │  • historical sageuk romance manhwa style                    │   │
│  │  • muted elegant earthy color palette                        │   │
│  │  • rich deep crimson reds, indigo blues, antique golds       │   │
│  │  • pure whites, warm natural skin tones                      │   │
│  │  • dramatic low-key lighting                                 │   │
│  │  • warm intimate candle glow                                 │   │
│  │  • deep heavy moody shadows                                  │   │
│  │  • strong cinematic rim lighting                             │   │
│  │  • glossy wet shine on hair, skin, silk fabrics              │   │
│  │  • subtle glistening highlights                              │   │
│  │  • clean medium lineart with graceful elegant flowing curves │   │
│  │  • soft gradient shading with detailed fabric texture        │   │
│  │  • heavy dramatic romantic blush                             │   │
│  │  • intense emotional atmosphere                              │   │
│  │  • sensual forbidden tension, tragic longing                 │   │
│  │  • passionate raw intimacy                                   │   │
│  │  • heartfelt classic Korean historical romance mood          │   │
│  │  • masterpiece, best quality                                 │   │
│  │                                                               │   │
│  │  ISEKAI_OTOME_FANTASY:                                       │   │
│  │  • isekai otome fantasy manhwa style                         │   │
│  │  • soft pastel dream color palette                           │   │
│  │  • pale blues pinks lavenders golds creamy whites            │   │
│  │  • rich jewel tone accents                                   │   │
│  │  • delicate floral romantic atmosphere                       │   │
│  │  • gentle ethereal glow + soft rim lighting                  │   │
│  │  • dreamy diffused palace-garden lighting                    │   │
│  │  • delicate clean lineart with graceful elegant curves       │   │
│  │  • smooth soft gradient shading combined with light cel-shading│  │
│  │  • gentle glossy highlights on hair eyes jewelry satin fabrics│  │
│  │  • subtle to prominent soft pink romantic cheek blush        │   │
│  │  • floral particle sparkles                                  │   │
│  │  • floating hearts and romantic overlays                     │   │
│  │  • whimsical dreamy romantic mood                            │   │
│  │  • slow-burn tender feeling with light comedic palace fantasy│   │
│  │  • masterpiece, best quality                                 │   │
│  │                                                               │   │
│  │  MODERN_KOREAN_ROMANCE:                                      │   │
│  │  • modern Korean romance webtoon style                       │   │
│  │  • warm soft pastel color palette dominated by gentle pinks  │   │
│  │  • romantic blushing mood                                    │   │
│  │  • clean confident medium lineart with smooth elegant curves │   │
│  │  • extremely prominent layered pink/red cheek blush          │   │
│  │  • intense glossy glass-skin shine on hair eyes lips skin    │   │
│  │  • wet-looking glossy highlights                             │   │
│  │  • soft cel-shading combined with airbrush gradients         │   │
│  │  • flattering soft rim/glow lighting                         │   │
│  │  • cozy warm atmosphere                                      │   │
│  │  • subtle dreamy sparkles and soft gradients                 │   │
│  │  • polished digital smoothness                               │   │
│  │  • subtle gradient-based shading rather than harsh lines     │   │
│  │  • playful heart-fluttering mood                             │   │
│  │  • frequent comedic exaggeration via sparkles and effects    │   │
│  │  • masterpiece, best quality                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Models

```
Character {
  name: string
  gender: string
  face: string
  hair: string
  body: string
  outfit: string
  mood: string
  visual_description: string  // Combined from all above
}

GenerateCharacterImageRequest {
  script_id: string
  character_name: string
  description: string  // Combined from individual fields
  gender: string       // For base_style selection
  image_style: "HISTORY_SAGEUK_ROMANCE" | "ISEKAI_OTOME_FANTASY" | "MODERN_KOREAN_ROMANCE"
}

CharacterImage {
  id: string
  character_name: string
  description: string
  image_url: string
  created_at: datetime
  is_selected: boolean
}
```

## State Management

```
Frontend State:
├── webtoonScript: WebtoonScript | null
│   ├── script_id: string
│   ├── story_id: string
│   ├── characters: Character[]
│   ├── panels: WebtoonPanel[]
│   └── character_images: Record<string, CharacterImage[]>
│
├── selectedCharacter: Character | null
├── isGeneratingScript: boolean
├── isGeneratingImage: boolean
└── error: string | null

Component State (CharacterImageDisplay):
├── gender: string
├── face: string
├── hair: string
├── body: string
├── outfit: string
├── mood: string
├── selectedImageStyle: ImageStyle
└── currentImageIndex: number
```

---

**Visual Guide Complete** - See other documentation files for implementation details
