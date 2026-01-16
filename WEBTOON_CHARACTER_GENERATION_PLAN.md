# Webtoon Character Image Generation - Implementation Plan

## Overview

Add a third page for character image generation. After users create and review a story, they can click "Generate Images" to convert the story into a webtoon script with character descriptions and scene breakdowns. Users can then generate character images using AI.

## User Flow

```
Tab 2: Story Building (Current)
├── Select mood
├── Generate story
├── View generated story
└── Click "Generate Images" button
    ↓
Tab 3: Character Generation (NEW)
├── Backend: Convert story → WebtoonScript (characters + panels)
├── Display character list on left side
├── For each character:
│   ├── Show editable text box with visual_description
│   ├── "Generate Image" button
│   ├── Display generated image next to description
│   ├── Allow re-generation with updated description
│   └── Show image carousel if multiple versions (< -> arrows)
└── User selects best image for each character
```

## Backend Tasks

### 1. Create Webtoon Writer Service
**File**: `backend/app/services/webtoon_writer.py`
- Import `WEBTOON_WRITER_PROMPT` from `app.prompt.webtoon_writer`
- Create `WebtoonWriter` class
- Implement `convert_story_to_script(story: str) -> WebtoonScript`
- Use LangChain with structured output (JSON mode)
- Parse response into `WebtoonScript` model
- Handle errors gracefully

### 2. Create Image Generation Service
**File**: `backend/app/services/image_generator.py`
- Create `ImageGenerator` class
- Implement `generate_character_image(description: str) -> str` (returns image URL or base64)
- Use simple prompt: "Generate a webtoon-style character: {description}"
- Use Gemini's image generation or external API (Stability AI, DALL-E, etc.)
- For initial development: Use placeholder or simple generation
- Return image data (URL or base64 encoded)

### 3. Add Webtoon API Endpoints
**File**: `backend/app/routers/webtoon.py`

#### Endpoint 1: POST /webtoon/generate
- Accept: `{"story_id": "string"}`
- Load story from storage
- Call `webtoon_writer.convert_story_to_script(story.content)`
- Store `WebtoonScript` with unique `script_id`
- Return: `{"script_id": "string", "characters": [...], "panels": [...]}`

#### Endpoint 2: POST /webtoon/character/image
- Accept: `{"script_id": "string", "character_name": "string", "description": "string"}`
- Call `image_generator.generate_character_image(description)`
- Store image with metadata
- Return: `{"image_id": "string", "image_url": "string", "character_name": "string"}`

#### Endpoint 3: GET /webtoon/{script_id}
- Return full webtoon script with characters and panels
- Include any generated images

#### Endpoint 4: GET /webtoon/character/{character_name}/images
- Return all generated images for a specific character
- Support pagination if needed

### 4. Update Data Models
**File**: `backend/app/models/story.py` (already has Character, WebtoonPanel, WebtoonScript)

Add new models:
```python
class CharacterImage(BaseModel):
    id: str
    character_name: str
    description: str
    image_url: str
    created_at: datetime
    is_selected: bool = False

class WebtoonScriptResponse(BaseModel):
    script_id: str
    story_id: str
    characters: List[Character]
    panels: List[WebtoonPanel]
    character_images: Dict[str, List[CharacterImage]]  # character_name -> images
    created_at: datetime
```

### 5. Register Webtoon Router
**File**: `backend/app/main.py`
- Import webtoon router
- Add to app: `app.include_router(webtoon.router, tags=["Webtoon"])`

## Frontend Tasks

### 6. Add Tab 3 to Navigation
**File**: `viral-story-search/src/components/StoryTabs.tsx`
- Add third tab: "🎨 Character Images"
- Enable only when story is generated
- Handle tab switching

### 7. Add "Generate Images" Button
**File**: `viral-story-search/src/components/StoryBuilder.tsx`
- Add button below generated story
- Show only after story is complete
- On click: Call API and switch to Tab 3

### 8. Create Character Image Generation Page
**File**: `viral-story-search/src/components/CharacterImageGenerator.tsx`

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│  Character Images                                    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────┐  ┌─────────────────────────┐ │
│  │ Character List   │  │ Image Display Area      │ │
│  │ (Left 30%)       │  │ (Right 70%)             │ │
│  │                  │  │                         │ │
│  │ □ Character 1    │  │ ┌─────────────────┐   │ │
│  │   [Generate]     │  │ │                 │   │ │
│  │                  │  │ │  Generated      │   │ │
│  │ □ Character 2    │  │ │  Image          │   │ │
│  │   [Generate]     │  │ │                 │   │ │
│  │                  │  │ └─────────────────┘   │ │
│  │ □ Character 3    │  │  < Previous | Next >  │ │
│  │   [Generate]     │  │                         │ │
│  │                  │  │ [Regenerate]            │ │
│  └──────────────────┘  └─────────────────────────┘ │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Features:**
- Left side: List of characters from WebtoonScript
- For each character:
  - Character name
  - Editable textarea with visual_description
  - "Generate Image" button
  - Loading state during generation
- Right side (when character selected):
  - Display generated image
  - Image carousel if multiple versions (< -> arrows)
  - "Regenerate" button
  - "Select as Final" button

### 9. Create Character List Component
**File**: `viral-story-search/src/components/CharacterList.tsx`
- Display list of characters
- Show character name
- Editable description field
- Generate button for each
- Visual indicator for selected character
- Show badge if images exist

### 10. Create Character Image Display Component
**File**: `viral-story-search/src/components/CharacterImageDisplay.tsx`
- Display selected character's images
- Image carousel with navigation
- Regenerate button
- Select button
- Show generation status

### 11. Update Types
**File**: `viral-story-search/src/types/index.ts`

Add:
```typescript
export interface Character {
  name: string;
  visual_description: string;
}

export interface WebtoonPanel {
  panel_number: number;
  shot_type: string;
  active_character_names: string[];
  visual_prompt: string;
  dialogue?: string;
}

export interface WebtoonScript {
  script_id: string;
  story_id: string;
  characters: Character[];
  panels: WebtoonPanel[];
  character_images: Record<string, CharacterImage[]>;
  created_at: string;
}

export interface CharacterImage {
  id: string;
  character_name: string;
  description: string;
  image_url: string;
  created_at: string;
  is_selected: boolean;
}

export interface GenerateWebtoonRequest {
  story_id: string;
}

export interface GenerateCharacterImageRequest {
  script_id: string;
  character_name: string;
  description: string;
}
```

### 12. Update API Client
**File**: `viral-story-search/src/lib/apiClient.ts`

Add functions:
```typescript
export async function generateWebtoonScript(storyId: string): Promise<WebtoonScript>
export async function generateCharacterImage(request: GenerateCharacterImageRequest): Promise<CharacterImage>
export async function getWebtoonScript(scriptId: string): Promise<WebtoonScript>
export async function getCharacterImages(scriptId: string, characterName: string): Promise<CharacterImage[]>
```

### 13. Update Main Page
**File**: `viral-story-search/src/app/page.tsx`
- Add Tab 3 state management
- Add webtoon script state
- Handle navigation to Tab 3

## Implementation Order

### Phase 1: Backend Foundation
1. ✅ Models already exist (Character, WebtoonPanel, WebtoonScript)
2. Create `WebtoonWriter` service
3. Create `ImageGenerator` service (simple placeholder)
4. Create webtoon router with endpoints
5. Register router in main.py
6. Test with curl/Postman

### Phase 2: Frontend Structure
7. Add Tab 3 to navigation
8. Create basic CharacterImageGenerator component
9. Create CharacterList component
10. Create CharacterImageDisplay component
11. Update types
12. Update API client

### Phase 3: Integration
13. Add "Generate Images" button to StoryBuilder
14. Connect Tab 3 to backend APIs
15. Implement image generation flow
16. Add image carousel
17. Add regeneration functionality

### Phase 4: Polish
18. Add loading states
19. Add error handling
20. Add image selection
21. Style components
22. Test end-to-end flow

## Technical Decisions

### Image Generation Options

**Option 1: Gemini Image Generation (Recommended for MVP)**
- Use Gemini's built-in image generation
- Simple integration
- Same API key

**Option 2: External API (Future)**
- Stability AI
- DALL-E
- Midjourney API
- Better quality but more complex

**For Initial Development:**
- Use simple text-to-image with Gemini
- Prompt: "Webtoon style character portrait: {description}"
- Store as base64 or URL

### Storage Strategy

**For MVP:**
- In-memory storage (like stories)
- Store WebtoonScript and CharacterImages in dicts

**For Production:**
- Database (PostgreSQL)
- Image storage (S3, Cloudinary)
- CDN for image delivery

## API Flow Diagram

```
User clicks "Generate Images"
    ↓
POST /webtoon/generate {story_id}
    ↓
Backend: Load story
    ↓
Backend: WebtoonWriter.convert_story_to_script()
    ↓
Backend: Return {script_id, characters, panels}
    ↓
Frontend: Display Tab 3 with characters
    ↓
User edits description, clicks "Generate Image"
    ↓
POST /webtoon/character/image {script_id, character_name, description}
    ↓
Backend: ImageGenerator.generate_character_image()
    ↓
Backend: Store image
    ↓
Backend: Return {image_id, image_url}
    ↓
Frontend: Display image
    ↓
User can regenerate or select
```

## File Structure

```
backend/
├── app/
│   ├── services/
│   │   ├── webtoon_writer.py      (NEW)
│   │   └── image_generator.py     (NEW)
│   ├── routers/
│   │   └── webtoon.py             (NEW)
│   ├── models/
│   │   └── story.py               (UPDATE - add new models)
│   └── prompt/
│       └── webtoon_writer.py      (EXISTS)

frontend/
├── src/
│   ├── components/
│   │   ├── CharacterImageGenerator.tsx  (NEW)
│   │   ├── CharacterList.tsx            (NEW)
│   │   ├── CharacterImageDisplay.tsx    (NEW)
│   │   ├── StoryTabs.tsx                (UPDATE - add Tab 3)
│   │   └── StoryBuilder.tsx             (UPDATE - add button)
│   ├── types/
│   │   └── index.ts                     (UPDATE - add types)
│   └── lib/
│       └── apiClient.ts                 (UPDATE - add functions)
```

## Testing Checklist

- [ ] Backend: WebtoonWriter converts story to script
- [ ] Backend: Script has characters with descriptions
- [ ] Backend: Script has panels with visual prompts
- [ ] Backend: Image generation works (even if placeholder)
- [ ] Backend: All endpoints return correct data
- [ ] Frontend: Tab 3 appears after story generation
- [ ] Frontend: Character list displays correctly
- [ ] Frontend: Description is editable
- [ ] Frontend: Generate button triggers API call
- [ ] Frontend: Image displays after generation
- [ ] Frontend: Carousel works with multiple images
- [ ] Frontend: Regeneration updates image
- [ ] End-to-end: Full flow from story to character images

## Success Criteria

1. ✅ User can generate webtoon script from story
2. ✅ User sees list of characters with descriptions
3. ✅ User can edit character descriptions
4. ✅ User can generate character images
5. ✅ User can see generated images
6. ✅ User can regenerate with updated descriptions
7. ✅ User can navigate between multiple image versions
8. ✅ User can select final image for each character

## Future Enhancements

- Panel image generation (not just characters)
- Batch generation (all characters at once)
- Style consistency across characters
- Background generation
- Full webtoon page assembly
- Export to PDF/image files
- Share generated webtoons
