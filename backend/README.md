# Viral Story Search - Python Backend

FastAPI backend for the Viral Story Search application, providing Reddit search functionality with future support for AI-powered story generation and image creation.

## Features

- **Reddit Search API**: Fetch viral posts from multiple subreddits
- **Caching**: In-memory caching with TTL for improved performance
- **Error Handling**: Comprehensive error handling with structured responses
- **API Documentation**: Auto-generated interactive API docs

## Requirements

- Python 3.10 or higher
- pip (Python package manager)

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Alternatively, use a virtual environment (recommended):

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your Reddit API credentials:

```
REDDIT_CLIENT_ID=your_actual_client_id
REDDIT_CLIENT_SECRET=your_actual_client_secret
REDDIT_USER_AGENT=viral-story-search/1.0
```

**Getting Reddit API Credentials:**

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" as the app type
4. Fill in the required fields
5. Copy the client ID (under the app name) and client secret

### 3. Run the Backend

```bash
uvicorn app.main:app --reload --port 8000
```

The backend will be available at:
- API: http://localhost:8000
- Interactive API Docs: http://localhost:8000/docs
- OpenAPI Schema: http://localhost:8000/openapi.json

### 4. Test the Backend

Check the health endpoint:

```bash
curl http://localhost:8000/health
```

Test the search endpoint:

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "time_range": "1d",
    "subreddits": ["python"],
    "post_count": 10
  }'
```

## Development

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── search.py
│   │   ├── story.py
│   │   └── image.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── reddit.py
│   │   ├── story_generator.py
│   │   └── image_generator.py
│   ├── routers/             # API endpoints
│   │   ├── __init__.py
│   │   ├── search.py
│   │   ├── story.py
│   │   └── image.py
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── cache.py
│       └── viral_score.py
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

### Hot Reloading

The `--reload` flag enables automatic reloading when code changes are detected. This is useful during development but should not be used in production.

### Running Tests

```bash
pytest
```

## API Endpoints

### Health Check

```
GET /health
```

Returns the health status of the backend.

### Search Posts

```
POST /search
```

Search for viral Reddit posts.

**Request Body:**
```json
{
  "time_range": "1d",
  "subreddits": ["python", "programming"],
  "post_count": 20
}
```

**Response:**
```json
{
  "posts": [...],
  "total_found": 20,
  "search_criteria": {...},
  "execution_time": 1.23
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `False` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |
| `REDDIT_CLIENT_ID` | Reddit API client ID | Required |
| `REDDIT_CLIENT_SECRET` | Reddit API client secret | Required |
| `REDDIT_USER_AGENT` | Reddit API user agent | `viral-story-search/1.0` |
| `CACHE_TTL` | Cache time-to-live (seconds) | `300` |
| `CACHE_MAX_SIZE` | Maximum cache entries | `100` |

## Troubleshooting

### Import Errors

If you encounter import errors, make sure you're running commands from the `backend/` directory and that all dependencies are installed.

### Reddit API Errors

- **401 Unauthorized**: Check your Reddit API credentials in `.env`
- **429 Rate Limited**: Wait a few minutes before making more requests
- **403 Forbidden**: Verify your user agent string is set correctly

### Port Already in Use

If port 8000 is already in use, specify a different port:

```bash
uvicorn app.main:app --reload --port 8001
```

## Future Phases

- **Phase 2**: LangChain story generation
- **Phase 3**: LangGraph workflows and image generation

## License

MIT
