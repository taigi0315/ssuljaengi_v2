# Design Document: Python Backend Migration

## Overview

This design describes the migration from a Next.js monolithic architecture to a decoupled architecture with:
- **Frontend**: Next.js React application (unchanged UI)
- **Backend**: Python FastAPI server with LangChain/LangGraph integration

The migration maintains all existing Reddit search functionality while adding AI-powered story generation and image creation capabilities.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Next.js Frontend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Search UI    │  │ Story UI     │  │ Image UI     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Python)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Reddit       │  │ Story        │  │ Image        │     │
│  │ Service      │  │ Generator    │  │ Generator    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │         LangGraph Workflow Engine                │     │
│  └──────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │  External APIs              │
              │  - Reddit API               │
              │  - OpenAI API               │
              │  - Image Generation API     │
              └─────────────────────────────┘
```

### Directory Structure

```
project-root/
├── viral-story-search/          # Next.js Frontend (existing)
│   ├── src/
│   ├── public/
│   └── package.json
│
└── backend/                     # New Python Backend
    ├── app/
    │   ├── __init__.py
    │   ├── main.py             # FastAPI app entry point
    │   ├── config.py           # Configuration management
    │   ├── models/             # Pydantic models
    │   │   ├── __init__.py
    │   │   ├── search.py
    │   │   ├── story.py
    │   │   └── image.py
    │   ├── services/           # Business logic
    │   │   ├── __init__.py
    │   │   ├── reddit.py
    │   │   ├── story_generator.py
    │   │   └── image_generator.py
    │   ├── workflows/          # LangGraph workflows
    │   │   ├── __init__.py
    │   │   └── story_workflow.py
    │   ├── routers/            # API endpoints
    │   │   ├── __init__.py
    │   │   ├── search.py
    │   │   ├── story.py
    │   │   └── image.py
    │   └── utils/              # Utilities
    │       ├── __init__.py
    │       ├── cache.py
    │       └── viral_score.py
    ├── tests/
    ├── requirements.txt
    ├── .env.example
    └── README.md
```


## Components and Interfaces

### 1. FastAPI Application (main.py)

**Responsibilities:**
- Initialize FastAPI app with CORS middleware
- Register API routers
- Configure logging and error handlers
- Provide health check endpoint

**Key Methods:**
```python
def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
def setup_cors(app: FastAPI) -> None:
    """Configure CORS for frontend communication"""
    
def setup_logging() -> None:
    """Configure application logging"""
```

### 2. Configuration Manager (config.py)

**Responsibilities:**
- Load environment variables
- Validate required configuration
- Provide typed configuration access

**Configuration Schema:**
```python
class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    
    # Reddit API
    reddit_client_id: str
    reddit_client_secret: str
    reddit_user_agent: str
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4"
    
    # Image Generation
    image_api_provider: str = "openai"  # or "stability"
    image_api_key: str
    
    # Cache
    cache_ttl: int = 300  # 5 minutes
    cache_max_size: int = 100
```

### 3. Reddit Service (services/reddit.py)

**Responsibilities:**
- Fetch posts from Reddit API
- Transform Reddit API responses to internal format
- Handle rate limiting and errors
- Calculate viral scores

**Key Methods:**
```python
async def fetch_posts(
    subreddit: str,
    time_range: str,
    limit: int
) -> List[RedditPost]:
    """Fetch posts from a subreddit"""
    
def calculate_viral_score(post: RedditPost) -> float:
    """Calculate viral score for a post"""
    
async def fetch_multiple_subreddits(
    subreddits: List[str],
    time_range: str,
    limit: int
) -> List[RedditPost]:
    """Fetch posts from multiple subreddits in parallel"""
```

### 4. Story Generator Service (services/story_generator.py)

**Responsibilities:**
- Generate stories from Reddit posts using LangChain
- Support different story styles and lengths
- Handle LLM errors and retries

**Key Methods:**
```python
async def generate_story(
    post: RedditPost,
    style: str = "creative",
    length: str = "medium"
) -> Story:
    """Generate a story from a Reddit post"""
    
def create_prompt(post: RedditPost, style: str, length: str) -> str:
    """Create LLM prompt from post content"""
```

**LangChain Integration:**
```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

class StoryGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4")
        self.parser = PydanticOutputParser(pydantic_object=Story)
        self.prompt = ChatPromptTemplate.from_template(...)
```

### 5. LangGraph Workflow (workflows/story_workflow.py)

**Responsibilities:**
- Orchestrate multi-step story generation
- Manage workflow state
- Handle step failures and retries

**Workflow Steps:**
1. **Analyze**: Extract key themes from Reddit post
2. **Outline**: Create story structure
3. **Generate**: Write story content
4. **Refine**: Polish and improve story

**Implementation:**
```python
from langgraph.graph import StateGraph, END

class StoryWorkflowState(TypedDict):
    post: RedditPost
    themes: List[str]
    outline: str
    draft: str
    final_story: str
    error: Optional[str]

def create_story_workflow() -> StateGraph:
    workflow = StateGraph(StoryWorkflowState)
    
    workflow.add_node("analyze", analyze_post)
    workflow.add_node("outline", create_outline)
    workflow.add_node("generate", generate_draft)
    workflow.add_node("refine", refine_story)
    
    workflow.add_edge("analyze", "outline")
    workflow.add_edge("outline", "generate")
    workflow.add_edge("generate", "refine")
    workflow.add_edge("refine", END)
    
    return workflow
```

### 6. Image Generator Service (services/image_generator.py)

**Responsibilities:**
- Generate images from story prompts
- Support multiple image generation providers
- Handle image storage and URLs

**Key Methods:**
```python
async def generate_image(
    prompt: str,
    style: str = "realistic",
    dimensions: Tuple[int, int] = (1024, 1024)
) -> ImageResult:
    """Generate an image from a text prompt"""
    
async def generate_from_story(story: Story) -> ImageResult:
    """Generate an image based on a story"""
```

### 7. Cache Utility (utils/cache.py)

**Responsibilities:**
- In-memory caching with TTL
- LRU eviction policy
- Thread-safe operations

**Implementation:**
```python
from cachetools import TTLCache
import asyncio

class SearchCache:
    def __init__(self, maxsize: int = 100, ttl: int = 300):
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        async with self.lock:
            return self.cache.get(key)
    
    async def set(self, key: str, value: Any) -> None:
        async with self.lock:
            self.cache[key] = value
```

### 8. API Routers

#### Search Router (routers/search.py)
```python
@router.post("/search", response_model=SearchResponse)
async def search_posts(request: SearchRequest):
    """Search for viral Reddit posts"""
```

#### Story Router (routers/story.py)
```python
@router.post("/story/generate", response_model=StoryResponse)
async def generate_story(request: StoryRequest):
    """Generate a story from a Reddit post"""

@router.get("/story/workflow/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get status of a story generation workflow"""
```

#### Image Router (routers/image.py)
```python
@router.post("/image/generate", response_model=ImageResponse)
async def generate_image(request: ImageRequest):
    """Generate an image from a prompt or story"""
```


## Data Models

### Pydantic Models (models/)

#### Search Models (models/search.py)
```python
from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime

class SearchRequest(BaseModel):
    time_range: Literal["1h", "1d", "10d", "100d"]
    subreddits: List[str] = Field(min_length=1, max_length=10)
    post_count: int = Field(ge=1, le=100, default=20)

class ViralPost(BaseModel):
    id: str
    title: str
    subreddit: str
    url: str
    upvotes: int
    comments: int
    viral_score: float
    created_at: datetime
    author: str

class SearchCriteria(BaseModel):
    time_range: Literal["1h", "1d", "10d", "100d"]
    subreddits: List[str]
    post_count: int

class SearchResponse(BaseModel):
    posts: List[ViralPost]
    total_found: int
    search_criteria: SearchCriteria
    execution_time: float

class RedditPost(BaseModel):
    """Internal Reddit post representation"""
    id: str
    title: str
    subreddit: str
    permalink: str
    score: int
    num_comments: int
    created_utc: int
    author: str
    is_removed: bool = False
    is_deleted: bool = False
```

#### Story Models (models/story.py)
```python
class StoryRequest(BaseModel):
    post_id: str
    post_title: str
    post_content: str
    style: Literal["creative", "dramatic", "humorous", "serious"] = "creative"
    length: Literal["short", "medium", "long"] = "medium"

class Story(BaseModel):
    id: str
    title: str
    content: str
    style: str
    length: str
    word_count: int
    generated_at: datetime
    source_post_id: str

class StoryResponse(BaseModel):
    story: Story
    generation_time: float

class WorkflowStatus(BaseModel):
    workflow_id: str
    status: Literal["pending", "analyzing", "outlining", "generating", "refining", "completed", "failed"]
    current_step: str
    progress: float  # 0.0 to 1.0
    result: Optional[Story] = None
    error: Optional[str] = None
```

#### Image Models (models/image.py)
```python
class ImageRequest(BaseModel):
    prompt: str
    style: Literal["realistic", "artistic", "cartoon", "abstract"] = "realistic"
    width: int = Field(default=1024, ge=256, le=2048)
    height: int = Field(default=1024, ge=256, le=2048)
    story_id: Optional[str] = None

class ImageResult(BaseModel):
    id: str
    url: str
    prompt: str
    style: str
    dimensions: Tuple[int, int]
    generated_at: datetime
    provider: str

class ImageResponse(BaseModel):
    image: ImageResult
    generation_time: float
```

#### Error Models
```python
from enum import Enum

class ErrorType(str, Enum):
    REDDIT_API_ERROR = "reddit_api_error"
    RATE_LIMIT = "rate_limit"
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"
    LLM_ERROR = "llm_error"
    IMAGE_GENERATION_ERROR = "image_generation_error"

class ErrorResponse(BaseModel):
    type: ErrorType
    message: str
    retryable: bool
    retry_after: Optional[int] = None
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Search Parameter Acceptance
*For any* valid combination of subreddit list, time range, and post count within allowed bounds, the Reddit_Service should accept the parameters and return a valid response (success or error).
**Validates: Requirements 2.2**

### Property 2: Search Response Format Consistency
*For any* search result returned by the Reddit_Service, the JSON structure should conform to the SearchResponse schema with all required fields present.
**Validates: Requirements 2.3**

### Property 3: Error Response Structure
*For any* error condition (Reddit API error, validation error, timeout, etc.), the Backend should return an ErrorResponse with proper type, message, and retryable flag.
**Validates: Requirements 2.4, 8.3**

### Property 4: API Interface Parity
*For any* search request that was valid in the Next.js implementation, the Python backend should accept the same request format and return a response in the same format.
**Validates: Requirements 3.4**

### Property 5: Story Generator Input Acceptance
*For any* valid Reddit post object, the Story_Generator should accept it as input without validation errors.
**Validates: Requirements 4.1**

### Property 6: Story Customization Parameters
*For any* valid combination of style (creative, dramatic, humorous, serious) and length (short, medium, long), the Story_Generator should accept the parameters.
**Validates: Requirements 4.3**

### Property 7: Story Generation Output
*For any* successful story generation, the result should be a Story object with non-empty title and content fields.
**Validates: Requirements 4.4**

### Property 8: Story Generation Error Handling
*For any* story generation failure (LLM error, timeout, invalid input), the service should return an ErrorResponse with descriptive message.
**Validates: Requirements 4.5**

### Property 9: Workflow Error Handling
*For any* workflow step that fails, the LangGraph workflow should transition to an error state and provide feedback without crashing.
**Validates: Requirements 5.3**

### Property 10: Workflow State Queryability
*For any* active or completed workflow, querying its status should return a WorkflowStatus object with current step and progress information.
**Validates: Requirements 5.4**

### Property 11: Image Generator Input Acceptance
*For any* valid prompt string or Story object, the Image_Generator should accept it as input.
**Validates: Requirements 6.1**

### Property 12: Image Generation Output
*For any* successful image generation, the result should be an ImageResult with either a valid URL or binary data.
**Validates: Requirements 6.3**

### Property 13: Image Customization Parameters
*For any* valid combination of dimensions (256-2048) and style (realistic, artistic, cartoon, abstract), the Image_Generator should accept the parameters.
**Validates: Requirements 6.4**

### Property 14: Image Generation Error Handling
*For any* image generation failure, the service should return an ErrorResponse with descriptive message.
**Validates: Requirements 6.5**

### Property 15: Request Logging
*For any* incoming HTTP request to the Backend, a log entry should be created with timestamp, method, path, and status code.
**Validates: Requirements 8.1**

### Property 16: Error Logging
*For any* error that occurs during request processing, a log entry should be created with error message and stack trace.
**Validates: Requirements 8.2**


## Error Handling

### Error Categories

1. **Validation Errors** (400)
   - Invalid request parameters
   - Missing required fields
   - Out-of-range values

2. **Authentication Errors** (401)
   - Missing API keys
   - Invalid credentials

3. **Rate Limiting** (429)
   - Too many requests
   - Reddit API rate limits

4. **Timeout Errors** (408)
   - Reddit API timeouts
   - LLM generation timeouts

5. **External Service Errors** (502/503)
   - Reddit API failures
   - OpenAI API failures
   - Image generation service failures

6. **Internal Server Errors** (500)
   - Unexpected exceptions
   - Database errors

### Error Response Format

All errors follow a consistent structure:

```python
{
    "error": {
        "type": "error_type",
        "message": "Human-readable error message",
        "retryable": true/false,
        "retry_after": 60  # Optional, for rate limits
    }
}
```

### Error Handling Strategy

1. **Graceful Degradation**: If one subreddit fails, continue with others
2. **Retry Logic**: Automatic retries for transient failures (3 attempts with exponential backoff)
3. **Circuit Breaker**: Temporarily disable failing external services
4. **Detailed Logging**: Log all errors with context for debugging
5. **User-Friendly Messages**: Convert technical errors to user-friendly messages

### Exception Hierarchy

```python
class APIException(Exception):
    """Base exception for all API errors"""
    def __init__(self, error_type: ErrorType, message: str, retryable: bool = False):
        self.error_type = error_type
        self.message = message
        self.retryable = retryable

class ValidationException(APIException):
    """Raised for validation errors"""
    
class RateLimitException(APIException):
    """Raised when rate limit is exceeded"""
    
class TimeoutException(APIException):
    """Raised for timeout errors"""
    
class ExternalServiceException(APIException):
    """Raised for external service failures"""
```

## Testing Strategy

### Unit Testing

**Framework**: pytest with pytest-asyncio for async tests

**Coverage Areas**:
- Individual service methods (Reddit service, Story generator, Image generator)
- Pydantic model validation
- Utility functions (viral score calculation, cache operations)
- Error handling and exception raising

**Example Unit Tests**:
```python
# Test viral score calculation
def test_viral_score_calculation():
    post = RedditPost(score=1000, num_comments=100, created_utc=...)
    score = calculate_viral_score(post)
    assert score > 0

# Test request validation
def test_search_request_validation():
    with pytest.raises(ValidationError):
        SearchRequest(time_range="invalid", subreddits=[], post_count=-1)

# Test error response structure
def test_error_response_format():
    error = ErrorResponse(
        type=ErrorType.VALIDATION_ERROR,
        message="Invalid input",
        retryable=False
    )
    assert error.type == ErrorType.VALIDATION_ERROR
    assert not error.retryable
```

### Property-Based Testing

**Framework**: Hypothesis for Python

**Configuration**: Minimum 100 iterations per property test

**Coverage Areas**:
- Search parameter combinations
- Story generation with various inputs
- Image generation with various parameters
- Error handling across different error types

**Example Property Tests**:
```python
from hypothesis import given, strategies as st

@given(
    subreddits=st.lists(st.text(min_size=1), min_size=1, max_size=10),
    time_range=st.sampled_from(["1h", "1d", "10d", "100d"]),
    post_count=st.integers(min_value=1, max_value=100)
)
async def test_search_accepts_valid_parameters(subreddits, time_range, post_count):
    """Property 1: Search Parameter Acceptance"""
    request = SearchRequest(
        subreddits=subreddits,
        time_range=time_range,
        post_count=post_count
    )
    # Should not raise validation error
    assert request.subreddits == subreddits

@given(
    style=st.sampled_from(["creative", "dramatic", "humorous", "serious"]),
    length=st.sampled_from(["short", "medium", "long"])
)
async def test_story_generator_accepts_parameters(style, length):
    """Property 6: Story Customization Parameters"""
    request = StoryRequest(
        post_id="test",
        post_title="Test",
        post_content="Content",
        style=style,
        length=length
    )
    assert request.style == style
    assert request.length == length
```

### Integration Testing

**Framework**: pytest with TestClient from FastAPI

**Coverage Areas**:
- End-to-end API flows
- Frontend-backend communication
- External API integration (with mocking)
- CORS configuration
- Error propagation

**Example Integration Tests**:
```python
from fastapi.testclient import TestClient

def test_search_endpoint():
    client = TestClient(app)
    response = client.post("/search", json={
        "time_range": "1d",
        "subreddits": ["python"],
        "post_count": 10
    })
    assert response.status_code == 200
    data = response.json()
    assert "posts" in data
    assert "total_found" in data

def test_cors_headers():
    client = TestClient(app)
    response = client.options("/search")
    assert "access-control-allow-origin" in response.headers
```

### Manual Testing

**Areas**:
- LangChain story generation quality
- Image generation quality
- Frontend UI integration
- Performance under load
- Error message clarity

### Test Data

**Fixtures**:
- Sample Reddit posts with various characteristics
- Mock Reddit API responses
- Sample stories for image generation
- Error scenarios

**Test Database**:
- Use in-memory cache for testing
- Mock external API calls
- Seed data for consistent tests

## Frontend Migration Changes

### API Client Updates

**File**: `viral-story-search/src/lib/apiClient.ts` (new file)

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function searchPosts(criteria: SearchCriteria): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(criteria),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }
  
  return response.json();
}

export async function generateStory(request: StoryRequest): Promise<StoryResponse> {
  const response = await fetch(`${API_BASE_URL}/story/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  
  return response.json();
}

export async function generateImage(request: ImageRequest): Promise<ImageResponse> {
  const response = await fetch(`${API_BASE_URL}/image/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  
  return response.json();
}
```

### Environment Variables

**File**: `viral-story-search/.env.local`

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Remove Old API Routes

Delete: `viral-story-search/src/app/api/search/route.ts`

The frontend will now call the Python backend instead of Next.js API routes.

## Deployment Considerations

### Development Setup

1. **Backend**: Run with `uvicorn app.main:app --reload --port 8000`
2. **Frontend**: Run with `npm run dev` (port 3000)
3. **Concurrent**: Use `concurrently` to run both

### Production Deployment

**Backend Options**:
- Docker container with Gunicorn + Uvicorn workers
- AWS Lambda with Mangum adapter
- Google Cloud Run
- Heroku with Python buildpack

**Frontend**:
- Vercel (Next.js native)
- AWS Amplify
- Netlify

**Environment Variables**:
- Backend: Reddit API keys, OpenAI API key, Image API key
- Frontend: Backend API URL

### Performance Optimization

1. **Caching**: Redis for production (replace in-memory cache)
2. **Connection Pooling**: For Reddit API and database
3. **Async Operations**: Use asyncio for concurrent requests
4. **Response Compression**: Enable gzip compression
5. **CDN**: For static assets and generated images

### Monitoring

1. **Logging**: Structured logging with JSON format
2. **Metrics**: Request count, latency, error rate
3. **Tracing**: OpenTelemetry for distributed tracing
4. **Alerts**: Set up alerts for error rates and latency

## Migration Path

### Phase 1: Backend Setup (No Frontend Changes)
1. Create Python backend with Reddit search endpoint
2. Test backend independently
3. Ensure API parity with Next.js implementation

### Phase 2: Frontend Integration
1. Update frontend to call Python backend
2. Test end-to-end flow
3. Keep Next.js API routes as fallback

### Phase 3: New Features
1. Add story generation endpoint
2. Add image generation endpoint
3. Update frontend to use new features

### Phase 4: Cleanup
1. Remove Next.js API routes
2. Update documentation
3. Deploy to production
