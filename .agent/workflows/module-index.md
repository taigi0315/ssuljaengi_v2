# Module Index

Quick reference for all modules in the Gossiptoon V2 codebase.

## Backend Modules

### Routers (`backend/app/routers/`)

| Module | Endpoints | Purpose |
|--------|-----------|---------|
| `search.py` | `POST /api/v1/search/` | Reddit post search with viral scoring |
| `story.py` | `POST /api/v1/story/generate`<br>`GET /api/v1/story/status/{id}`<br>`GET /api/v1/story/{id}` | Story generation workflow |
| `webtoon.py` | `POST /api/v1/webtoon/generate`<br>`POST /api/v1/webtoon/character-image`<br>`POST /api/v1/webtoon/scene-image`<br>`POST /api/v1/webtoon/video` | Webtoon creation pipeline |
| `character_library.py` | `GET/POST/DELETE /api/v1/characters/` | Character persistence |

### Services (`backend/app/services/`)

| Module | Class/Function | Purpose |
|--------|----------------|---------|
| `reddit.py` | `RedditService` | OAuth client, post fetching, rate limiting |
| `story_writer.py` | `StoryWriter` | Generate story from Reddit post |
| `story_evaluator.py` | `StoryEvaluator` | Score story quality (0-10) |
| `story_rewriter.py` | `StoryRewriter` | Improve story with feedback |
| `webtoon_writer.py` | `WebtoonWriter` | Generate script from story |
| `webtoon_evaluator.py` | `WebtoonEvaluator` | Validate script structure |
| `webtoon_rewriter.py` | `WebtoonRewriter` | Refine script quality |
| `webtoon_generator.py` | `WebtoonGenerator` | Character design generation |
| `image_generator.py` | `ImageGenerator` | Gemini image generation |
| `video_service.py` | `VideoService` | Video assembly from assets |
| `llm_config.py` | `LLMConfig` | Configure Gemini prompts |

### Workflows (`backend/app/workflows/`)

| Module | Purpose |
|--------|---------|
| `story_workflow.py` | LangGraph state machine for story generation |
| `webtoon_workflow.py` | LangGraph state machine for script generation |

### Models (`backend/app/models/`)

| Module | Key Classes |
|--------|-------------|
| `search.py` | `SearchRequest`, `SearchResponse`, `ViralPost` |
| `story.py` | `Story`, `WebtoonScript`, `Character`, `Panel`, `DialogueLine` |
| `video_models.py` | `VideoRequest`, `VideoResponse` |

### Utils (`backend/app/utils/`)

| Module | Purpose |
|--------|---------|
| `cache.py` | `SearchCache` - In-memory TTL cache |
| `persistence.py` | `JsonStore` - File-based JSON persistence |
| `exceptions.py` | Custom exception classes |
| `viral_score.py` | Viral score calculation algorithm |

### Prompts (`backend/app/prompt/`)

| Module | Purpose |
|--------|---------|
| `story_writer.py` | Story generation prompts |
| `story_evaluator.py` | Story evaluation rubric |
| `story_rewriter.py` | Story improvement prompts |
| `webtoon_writer.py` | Script generation prompts |
| `webtoon_evaluator.py` | Script validation prompts |
| `scene_generator.py` | Scene image prompts |
| `character_generator.py` | Character image prompts |

---

## Frontend Modules

### Pages (`viral-story-search/src/app/`)

| Module | Route | Purpose |
|--------|-------|---------|
| `page.tsx` | `/` | Main application page |
| `layout.tsx` | - | Root layout with providers |

### Components (`viral-story-search/src/components/`)

#### Search & Discovery
| Component | Purpose |
|-----------|---------|
| `SearchControls.tsx` | Subreddit & time range selection |
| `ResultsList.tsx` | Display search results |
| `ResultItem.tsx` | Individual post card |
| `SubredditSelector.tsx` | Multi-select subreddit picker |
| `TimeRangeSelector.tsx` | Time range filter |
| `PostCountInput.tsx` | Result count control |
| `RedditPostDisplay.tsx` | Detailed post view |

#### Story Generation
| Component | Purpose |
|-----------|---------|
| `StoryBuilder.tsx` | Story generation interface |
| `StoryDisplay.tsx` | Story content display |
| `StoryTabs.tsx` | Tab navigation for story views |
| `MoodSelector.tsx` | Story mood picker |
| `GenreSelector.tsx` | Story genre picker |

#### Webtoon Generation
| Component | Purpose |
|-----------|---------|
| `ScriptPreview.tsx` | Webtoon script viewer |
| `CharacterImageGenerator.tsx` | Character image generation UI |
| `CharacterImageDisplay.tsx` | Character image carousel |
| `SceneImageGenerator.tsx` | Scene image generation (v1) |
| `SceneImageGeneratorV2.tsx` | Scene image generation (current) |
| `VideoGenerator.tsx` | Video assembly and download |

#### Feedback & Progress
| Component | Purpose |
|-----------|---------|
| `WorkflowProgress.tsx` | Multi-step progress tracker |
| `LoadingSpinner.tsx` | Loading indicator |
| `ErrorMessage.tsx` | Error display |
| `VisualFeedback.tsx` | Visual state indicators |

### Hooks (`viral-story-search/src/hooks/`)

| Hook | Purpose |
|------|---------|
| `useSessionStorage.ts` | Persistent state with sessionStorage |
| `useDebounce.ts` | Debounced value updates |
| `useWorkflowStatus.ts` | Poll workflow completion |

### Library (`viral-story-search/src/lib/`)

| Module | Purpose |
|--------|---------|
| `apiClient.ts` | HTTP client for backend API |
| `constants.ts` | Application constants |

### Types (`viral-story-search/src/types/`)

| Module | Key Types |
|--------|-----------|
| `index.ts` | `ViralPost`, `Story`, `WebtoonScript`, `Character`, `Panel`, `WorkflowStatus`, `ErrorState` |

### Utils (`viral-story-search/src/utils/`)

| Module | Purpose |
|--------|---------|
| `searchCache.ts` | Client-side search caching |
| `validation.ts` | Input validation |
| `errorHandler.ts` | Error handling utilities |
| `debounce.ts` | Debounce function |
| `viralScore.ts` | Client-side score calculation |

---

## Configuration Files

### Backend
| File | Purpose |
|------|---------|
| `backend/app/config.py` | Pydantic settings |
| `backend/requirements.txt` | Python dependencies |
| `backend/run.sh` | Startup script |

### Frontend
| File | Purpose |
|------|---------|
| `viral-story-search/package.json` | Node dependencies |
| `viral-story-search/tailwind.config.js` | Tailwind configuration |
| `viral-story-search/tsconfig.json` | TypeScript configuration |

### Root
| File | Purpose |
|------|---------|
| `package.json` | Monorepo scripts |
| `.env` | Environment variables |
| `README.md` | Project documentation |
