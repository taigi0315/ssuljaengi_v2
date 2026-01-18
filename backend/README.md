# Gossiptoon V2 - Backend

FastAPI backend for the Gossiptoon V2 application, providing Reddit search, AI-powered story generation, webtoon script creation, and image generation.

---

## 🚀 Features

| Feature                    | Description                                          |
| -------------------------- | ---------------------------------------------------- |
| **Reddit Search API**      | Fetch and rank viral posts from multiple subreddits  |
| **Story Generation**       | AI-powered story generation using LangChain + Gemini |
| **Webtoon Scripts**        | Transform stories into webtoon-style scripts         |
| **Character Generation**   | Generate and manage character designs                |
| **Scene Image Generation** | Create scene images with Gemini 2.5 Flash            |
| **Video Assembly**         | Combine assets into video content                    |
| **Caching**                | In-memory caching with file persistence              |

---

## 📋 Requirements

- Python 3.10+
- pip (or virtualenv)

---

## 🛠️ Setup

### 1. Install Dependencies

```bash
cd backend

# Recommended: Use a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Reddit API (Required)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# Google Gemini API (Required)
GOOGLE_API_KEY=your_api_key
```

### 3. Run the Server

```bash
./run.sh
# Or manually:
uvicorn app.main:app --reload --port 8000
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Pydantic Settings configuration
│   ├── models/              # Pydantic data models
│   │   ├── search.py        # Reddit search models
│   │   ├── story.py         # Story & webtoon models
│   │   └── video_models.py  # Video generation models
│   ├── services/            # Business logic layer
│   │   ├── reddit.py        # Reddit API client
│   │   ├── story_writer.py  # Story generation service
│   │   ├── webtoon_writer.py # Webtoon script generation
│   │   ├── image_generator.py # Image generation with Gemini
│   │   ├── video_service.py # Video assembly service
│   │   └── llm_config.py    # LLM configuration
│   ├── routers/             # API endpoint handlers
│   │   ├── search.py        # /api/v1/search endpoints
│   │   ├── story.py         # /api/v1/story endpoints
│   │   ├── webtoon.py       # /api/v1/webtoon endpoints
│   │   └── character_library.py # Character library endpoints
│   ├── prompt/              # AI prompt templates
│   │   ├── story_writer.py  # Story generation prompts
│   │   ├── webtoon_writer.py # Webtoon script prompts
│   │   ├── character_image.py # Character image prompts
│   │   └── scene_image.py   # Scene image prompts
│   ├── utils/               # Utility modules
│   │   ├── cache.py         # In-memory cache
│   │   ├── persistence.py   # File-based persistence
│   │   ├── exceptions.py    # Custom exception classes
│   │   └── viral_score.py   # Viral score calculator
│   └── workflows/           # LangGraph workflow definitions
├── docs/                    # Backend documentation
├── tests/                   # Test files
├── data/                    # Persistent data storage
├── cache/                   # Cache storage (images)
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
└── run.sh                   # Server startup script
```

---

## 🔌 API Endpoints

### Health & Status

| Method | Endpoint  | Description  |
| ------ | --------- | ------------ |
| GET    | `/health` | Health check |

### Search API

| Method | Endpoint          | Description         |
| ------ | ----------------- | ------------------- |
| POST   | `/api/v1/search/` | Search Reddit posts |

### Story API

| Method | Endpoint                 | Description              |
| ------ | ------------------------ | ------------------------ |
| POST   | `/api/v1/story/generate` | Generate story from post |

### Webtoon API

| Method | Endpoint                          | Description               |
| ------ | --------------------------------- | ------------------------- |
| GET    | `/api/v1/webtoon/`                | List all workflows        |
| POST   | `/api/v1/webtoon/`                | Create new workflow       |
| GET    | `/api/v1/webtoon/{id}`            | Get workflow status       |
| GET    | `/api/v1/webtoon/{id}/story`      | Get story content         |
| POST   | `/api/v1/webtoon/{id}/script`     | Generate webtoon script   |
| POST   | `/api/v1/webtoon/{id}/characters` | Generate character images |
| POST   | `/api/v1/webtoon/{id}/scenes`     | Generate scene images     |
| POST   | `/api/v1/webtoon/{id}/video`      | Generate video            |

### Character Library API

| Method | Endpoint                  | Description               |
| ------ | ------------------------- | ------------------------- |
| GET    | `/api/v1/characters/`     | List saved characters     |
| POST   | `/api/v1/characters/`     | Save character to library |
| DELETE | `/api/v1/characters/{id}` | Delete character          |

---

## ⚙️ Environment Variables

| Variable               | Description            | Default                  | Required |
| ---------------------- | ---------------------- | ------------------------ | -------- |
| `HOST`                 | Server host            | `0.0.0.0`                | No       |
| `PORT`                 | Server port            | `8000`                   | No       |
| `DEBUG`                | Debug mode             | `False`                  | No       |
| `FRONTEND_URL`         | Frontend URL for CORS  | `http://localhost:3000`  | No       |
| `REDDIT_CLIENT_ID`     | Reddit API client ID   | -                        | **Yes**  |
| `REDDIT_CLIENT_SECRET` | Reddit API secret      | -                        | **Yes**  |
| `GOOGLE_API_KEY`       | Google Gemini API key  | -                        | **Yes**  |
| `GEMINI_MODEL`         | Gemini model name      | `gemini-2.0-flash-exp`   | No       |
| `MODEL_IMAGE_GEN`      | Image generation model | `gemini-2.5-flash-image` | No       |
| `CACHE_TTL`            | Cache TTL (seconds)    | `300`                    | No       |
| `CACHE_MAX_SIZE`       | Max cache entries      | `100`                    | No       |

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_video_service.py
```

---

## 📖 Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

For more detailed documentation, see the `docs/` folder.

---

## 🐛 Troubleshooting

### Import Errors

- Ensure you're in the `backend/` directory
- Verify virtual environment is activated
- Run `pip install -r requirements.txt`

### Reddit API Errors

- **401**: Check credentials in `.env`
- **429**: Rate limited - wait a few minutes
- **403**: Verify user agent is set

### Google API Errors

- Verify `GOOGLE_API_KEY` is valid
- Check API quotas at Google Cloud Console

### Port in Use

```bash
lsof -ti:8000 | xargs kill -9
```
