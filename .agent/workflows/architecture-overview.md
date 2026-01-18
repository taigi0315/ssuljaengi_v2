# Architecture Overview

## System Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend (Next.js 16)"]
        UI[React Components]
        API_CLIENT[API Client]
        HOOKS[Custom Hooks]
        SESSION[Session Storage]
    end

    subgraph Backend["Backend (FastAPI)"]
        ROUTERS[API Routers]
        SERVICES[Business Services]
        WORKFLOWS[LangGraph Workflows]
        MODELS[Pydantic Models]
        UTILS[Utilities]
    end

    subgraph External["External Services"]
        REDDIT[Reddit API]
        GEMINI[Google Gemini AI]
    end

    subgraph Storage["Data Storage"]
        JSON_STORE[JSON File Store]
        ASSETS[Generated Assets]
    end

    UI --> API_CLIENT
    API_CLIENT --> ROUTERS
    ROUTERS --> SERVICES
    SERVICES --> WORKFLOWS
    WORKFLOWS --> GEMINI
    SERVICES --> REDDIT
    SERVICES --> JSON_STORE
    SERVICES --> ASSETS
```

## Request Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Reddit
    participant Gemini
    participant Storage

    User->>Frontend: Search for viral posts
    Frontend->>Backend: POST /api/v1/search/
    Backend->>Reddit: OAuth + Fetch posts
    Reddit-->>Backend: Posts data
    Backend->>Backend: Calculate viral scores
    Backend-->>Frontend: Ranked posts

    User->>Frontend: Select post + Generate story
    Frontend->>Backend: POST /api/v1/story/generate
    Backend->>Gemini: Generate story (LangGraph)
    Gemini-->>Backend: Story content
    Backend->>Gemini: Evaluate quality
    Gemini-->>Backend: Score (0-10)
    alt Score < 7.0
        Backend->>Gemini: Rewrite story
        Gemini-->>Backend: Improved story
    end
    Backend->>Storage: Save story
    Backend-->>Frontend: Story ID + Status

    User->>Frontend: Generate webtoon
    Frontend->>Backend: POST /api/v1/webtoon/generate
    Backend->>Gemini: Generate script (LangGraph)
    Backend->>Storage: Save script
    Backend-->>Frontend: Script data

    User->>Frontend: Generate images
    Frontend->>Backend: POST /api/v1/webtoon/character-image
    Backend->>Gemini: Generate character images
    Backend->>Storage: Save images
    Backend-->>Frontend: Image URLs
```

## Module Dependency Graph

```mermaid
graph LR
    subgraph Routers
        R_SEARCH[search.py]
        R_STORY[story.py]
        R_WEBTOON[webtoon.py]
        R_CHAR[character_library.py]
    end

    subgraph Services
        S_REDDIT[reddit.py]
        S_STORY_W[story_writer.py]
        S_STORY_E[story_evaluator.py]
        S_STORY_R[story_rewriter.py]
        S_WEBTOON_W[webtoon_writer.py]
        S_WEBTOON_E[webtoon_evaluator.py]
        S_IMAGE[image_generator.py]
        S_VIDEO[video_service.py]
    end

    subgraph Workflows
        W_STORY[story_workflow.py]
        W_WEBTOON[webtoon_workflow.py]
    end

    R_SEARCH --> S_REDDIT
    R_STORY --> W_STORY
    R_WEBTOON --> W_WEBTOON
    R_WEBTOON --> S_IMAGE
    R_WEBTOON --> S_VIDEO

    W_STORY --> S_STORY_W
    W_STORY --> S_STORY_E
    W_STORY --> S_STORY_R

    W_WEBTOON --> S_WEBTOON_W
    W_WEBTOON --> S_WEBTOON_E
```

## Technology Stack

### Frontend
| Layer | Technology | Purpose |
|-------|------------|---------|
| Framework | Next.js 16 | React server components, App Router |
| UI Library | React 19 | Component rendering |
| Language | TypeScript 5.x | Type safety |
| Styling | TailwindCSS 4.x | Utility-first CSS |
| State | Session Storage + Hooks | Client-side persistence |

### Backend
| Layer | Technology | Purpose |
|-------|------------|---------|
| Framework | FastAPI 0.109 | Async API with OpenAPI |
| Server | Uvicorn 0.27 | ASGI server |
| Validation | Pydantic 2.5 | Data validation |
| AI Orchestration | LangGraph 0.0.20 | Workflow state machines |
| LLM Client | Google Generative AI | Gemini API |
| Storage | JSON Files | Lightweight persistence |

### External APIs
| Service | Purpose | Auth |
|---------|---------|------|
| Reddit API | Fetch viral posts | OAuth 2.0 |
| Google Gemini | Text/Image generation | API Key |

## Directory Structure

```
gossiptoon_v2_2/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings (Pydantic)
│   │   ├── models/              # Data models
│   │   │   ├── search.py        # Search request/response
│   │   │   ├── story.py         # Story/Webtoon models
│   │   │   └── video_models.py  # Video generation
│   │   ├── routers/             # API endpoints
│   │   │   ├── search.py        # /api/v1/search/
│   │   │   ├── story.py         # /api/v1/story/
│   │   │   ├── webtoon.py       # /api/v1/webtoon/
│   │   │   └── character_library.py
│   │   ├── services/            # Business logic (12 modules)
│   │   ├── workflows/           # LangGraph definitions
│   │   ├── prompt/              # AI prompt templates
│   │   └── utils/               # Cache, persistence, etc.
│   └── data/                    # Generated JSON storage
├── viral-story-search/
│   ├── src/
│   │   ├── app/                 # Next.js pages
│   │   ├── components/          # React components (30+)
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # API client, constants
│   │   ├── types/               # TypeScript definitions
│   │   └── utils/               # Utility functions
│   └── public/                  # Static assets
└── .agent/workflows/            # This documentation
```

## Configuration

### Required Environment Variables
```env
# Reddit API (Required)
REDDIT_CLIENT_ID=xxx
REDDIT_CLIENT_SECRET=xxx

# Google Gemini (Required)
GOOGLE_API_KEY=xxx

# Optional
DEBUG=False
FRONTEND_URL=http://localhost:3000
GEMINI_MODEL=gemini-2.0-flash-exp
MODEL_IMAGE_GEN=gemini-2.5-flash-image
STORY_EVALUATION_THRESHOLD=7.0
STORY_MAX_REWRITES=2
```

### Ports
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
