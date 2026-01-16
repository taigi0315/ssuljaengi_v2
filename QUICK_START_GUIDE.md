# Quick Start Guide - Character Image Generation

## What Was Implemented

### ✅ Individual Character Field Editing
- 6 editable fields: gender, face, hair, body, outfit, mood
- Combined description preview
- Dark, readable text

### ✅ Image Style Selection
- 3 visual style buttons with preview images
- Styles: Historical Romance, Fantasy Romance, Modern Romance
- Selected style highlighted with purple border

### ✅ Prompt Template Integration
- Uses `character_image.py` prompt template
- Base style (YOUTH_MALE/YOUTH_FEMALE) selected by gender
- Image style (mood) selected by user
- Character description combined from individual fields

## How to Test

### 1. Start Backend
```bash
cd backend
./run.sh
```

### 2. Start Frontend
```bash
cd viral-story-search
npm run dev
```

### 3. Test Flow
1. Go to http://localhost:3000
2. Search for viral posts
3. Select a post and choose a mood
4. Wait for story generation (watch progress bar)
5. Click "Generate Webtoon" button
6. Wait for script generation
7. **Character List** appears on left (30% width)
8. Click a character to select it
9. **Character Editor** appears on right (70% width)
10. Edit individual fields (gender, face, hair, body, outfit, mood)
11. See combined description in purple preview box
12. **Select image style** by clicking one of 3 visual buttons
13. Click "Generate Image" button
14. Image appears below (currently placeholder)

## Key Features

### Character Fields
- **Gender**: male, female, non-binary
- **Face**: jawline, eyes, skin tone
- **Hair**: length, color, style
- **Body**: build, height, proportions
- **Outfit**: clothing, accessories
- **Mood**: personality, demeanor

### Image Styles
1. **Historical Romance** - Dramatic sageuk style
2. **Fantasy Romance** - Dreamy isekai style
3. **Modern Romance** - Contemporary K-drama style

## API Endpoints

### Get Image Styles
```bash
curl http://localhost:8000/webtoon/image-styles
```

### Generate Character Image
```bash
curl -X POST http://localhost:8000/webtoon/character/image \
  -H "Content-Type: application/json" \
  -d '{
    "script_id": "your-script-id",
    "character_name": "Ji-hoon",
    "description": "male, sharp jawline, dark eyes, short black hair, tall athletic build, wearing navy suit, confident",
    "gender": "male",
    "image_style": "MODERN_KOREAN_ROMANCE"
  }'
```

### Get Preview Images
```bash
# Historical Romance
curl http://localhost:8000/api/assets/images/HISTORY_SAGEUK_ROMANCE.png

# Fantasy Romance
curl http://localhost:8000/api/assets/images/ISEKAI_OTOME_FANTASY.png

# Modern Romance
curl http://localhost:8000/api/assets/images/MODERN_KOREAN_ROMANCE.png
```

## Troubleshooting

### Backend Issues

**Problem:** Server won't start
```bash
# Check Python version (need 3.12+)
python --version

# Install dependencies
cd backend
pip install -r requirements.txt
```

**Problem:** Gemini API errors
```bash
# Check .env file has correct API key
cat backend/.env | grep GEMINI_API_KEY

# Verify model name is correct
cat backend/.env | grep GEMINI_MODEL
# Should be: GEMINI_MODEL=gemini-2.0-flash-exp
```

**Problem:** Static images not loading
```bash
# Verify assets directory exists
ls -la backend/app/assets/images/

# Should see:
# HISTORY_SAGEUK_ROMANCE.png
# ISEKAI_OTOME_FANTASY.png
# MODERN_KOREAN_ROMANCE.png
```

### Frontend Issues

**Problem:** Can't connect to backend
```bash
# Check .env.local file
cat viral-story-search/.env.local | grep NEXT_PUBLIC_API_URL
# Should be: NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Problem:** TypeScript errors
```bash
cd viral-story-search
npm install
npm run build
```

**Problem:** Image style buttons not showing
- Check browser console for errors
- Verify backend is serving static files at /api/assets/images/
- Check CORS is configured correctly

## Next Steps

### To Implement Real Image Generation
1. Choose an AI image service (Gemini Imagen, Stability AI, DALL-E)
2. Update `backend/app/services/image_generator.py`
3. Replace `_generate_placeholder()` with actual API call
4. Use the `final_prompt` variable that's already built
5. Save generated images to storage (S3, CloudFlare R2)
6. Return real image URLs instead of placeholder

### To Add Database Persistence
1. Set up PostgreSQL database
2. Create tables for stories, scripts, characters, images
3. Replace in-memory dictionaries with database queries
4. Add SQLAlchemy models
5. Add database migrations (Alembic)

### To Deploy to Production
1. Set up production environment variables
2. Configure production database
3. Set up image storage (S3/R2)
4. Add authentication (JWT)
5. Add rate limiting
6. Set up monitoring (Sentry, DataDog)
7. Configure CI/CD pipeline
8. Deploy to cloud (AWS, GCP, Vercel)

## File Locations

### Backend
- Models: `backend/app/models/story.py`
- Prompts: `backend/app/prompt/character_image.py`, `backend/app/prompt/image_mood.py`
- Services: `backend/app/services/image_generator.py`
- Routes: `backend/app/routers/webtoon.py`
- Assets: `backend/app/assets/images/*.png`

### Frontend
- Types: `viral-story-search/src/types/index.ts`
- Components: `viral-story-search/src/components/CharacterImageDisplay.tsx`
- API Client: `viral-story-search/src/lib/apiClient.ts`

## Documentation
- `CHARACTER_FIELDS_COMPLETE.md` - Character model enhancement details
- `IMAGE_STYLE_SELECTION_COMPLETE.md` - Image style selection details
- `IMPLEMENTATION_COMPLETE_SUMMARY.md` - Complete technical summary
- `QUICK_START_GUIDE.md` - This file

---

**Status:** ✅ Implementation Complete - Ready for Testing
**Last Updated:** 2026-01-16
