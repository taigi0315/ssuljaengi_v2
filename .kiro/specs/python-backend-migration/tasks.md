# Implementation Plan: Python Backend Migration (Phase 1 - Reddit Search Only)

## Overview

This plan migrates ONLY the existing Reddit search functionality from Next.js API routes to a Python FastAPI backend. This is Phase 1 - getting the backend working with the current features. LangChain/LangGraph story generation and image generation will be added in future phases.

**Goal**: Make the existing Reddit search work through Python backend instead of Next.js API routes.

## Tasks

- [x] 1. Set up Python backend project structure
  - Create `backend/` directory at project root
  - Create `app/` directory with subdirectories: `models/`, `services/`, `routers/`, `utils/`
  - Create `requirements.txt` with core dependencies: fastapi, uvicorn[standard], pydantic, python-dotenv, httpx, pydantic-settings
  - Create `.env.example` with Reddit API credentials
  - Create `backend/README.md` with setup instructions
  - _Requirements: 1.1, 1.2, 7.4, 10.4_

- [x] 2. Implement configuration management
  - [x] 2.1 Create `app/config.py` with Settings class
    - Define server config (host, port, debug)
    - Define CORS config (frontend_url)
    - Define Reddit API config (client_id, client_secret, user_agent)
    - Define cache config (ttl, max_size)
    - Load from environment variables with defaults
    - Validate required fields on startup
    - _Requirements: 7.1, 7.2, 7.3, 7.5_

- [x] 3. Create Pydantic data models for search
  - [x] 3.1 Create `app/models/search.py`
    - Implement SearchRequest model (time_range, subreddits, post_count with validation)
    - Implement ViralPost model (id, title, subreddit, url, upvotes, comments, viral_score, created_at, author)
    - Implement SearchCriteria model
    - Implement SearchResponse model (posts, total_found, search_criteria, execution_time)
    - Implement RedditPost model (internal representation)
    - _Requirements: 2.2, 2.3_

  - [x] 3.2 Create `app/models/__init__.py` with error models
    - Define ErrorType enum (REDDIT_API_ERROR, RATE_LIMIT, NETWORK_ERROR, VALIDATION_ERROR, TIMEOUT_ERROR)
    - Implement ErrorResponse model (type, message, retryable, retry_after)
    - _Requirements: 8.3_

- [x] 4. Implement utility modules
  - [x] 4.1 Create `app/utils/cache.py` with SearchCache class
    - Use cachetools.TTLCache for in-memory caching
    - Implement async get/set methods with asyncio.Lock
    - Implement LRU eviction (max 100 entries)
    - _Requirements: 2.5_

  - [x] 4.2 Create `app/utils/viral_score.py`
    - Port calculate_viral_score function from TypeScript (viral-story-search/src/utils/viralScore.ts)
    - Calculate based on upvotes, comments, and hours since posted
    - _Requirements: 2.1_

  - [x] 4.3 Create `app/utils/exceptions.py` with custom exceptions
    - Implement APIException base class
    - Implement ValidationException, RateLimitException, TimeoutException, ExternalServiceException
    - _Requirements: 8.3_

- [x] 5. Implement Reddit service
  - [x] 5.1 Create `app/services/reddit.py` with RedditService class
    - Initialize httpx.AsyncClient for Reddit API
    - Implement Reddit OAuth authentication
    - Implement fetch_posts method (subreddit, time_range, limit)
    - Transform Reddit API JSON to RedditPost models
    - Calculate viral scores for each post
    - Handle Reddit API errors (rate limits, timeouts, network errors)
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 5.2 Implement fetch_multiple_subreddits method
    - Use asyncio.gather to fetch from multiple subreddits in parallel
    - Handle individual subreddit failures gracefully (log error, continue with others)
    - Combine all results into single list
    - Sort by viral score
    - Limit to requested post_count
    - _Requirements: 2.1_

- [x] 6. Implement FastAPI application
  - [x] 6.1 Create `app/main.py`
    - Create FastAPI app instance with title and version
    - Add CORS middleware (allow frontend URL from config)
    - Configure logging (format, level from config)
    - Add request/response logging middleware
    - Add exception handlers for APIException and validation errors
    - Add health check endpoint GET `/health` (returns {"status": "healthy"})
    - Register search router
    - _Requirements: 1.1, 1.3, 1.4, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 7. Implement search API router
  - [x] 7.1 Create `app/routers/search.py`
    - Implement POST `/search` endpoint
    - Accept SearchRequest body
    - Generate cache key from request
    - Check cache first, return if valid
    - Call RedditService.fetch_multiple_subreddits
    - Calculate execution time
    - Build SearchResponse
    - Cache the response
    - Return SearchResponse
    - Handle errors and return ErrorResponse with appropriate status codes
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 8. Checkpoint - Test backend independently
  - Create `.env` file with Reddit API credentials
  - Run backend: `cd backend && uvicorn app.main:app --reload --port 8000`
  - Test health check: `curl http://localhost:8000/health`
  - Test search endpoint with curl or Postman
  - Check API docs at `http://localhost:8000/docs`
  - Verify caching works (second request is faster)
  - Ask the user if questions arise

- [x] 9. Update frontend to use Python backend
  - [x] 9.1 Create `viral-story-search/src/lib/apiClient.ts`
    - Get API_BASE_URL from environment variable (default: http://localhost:8000)
    - Implement searchPosts function
    - Make POST request to `${API_BASE_URL}/search`
    - Handle errors and throw with error message
    - Return SearchResponse
    - _Requirements: 3.1, 3.2, 3.4_

  - [x] 9.2 Create `viral-story-search/.env.local`
    - Add `NEXT_PUBLIC_API_URL=http://localhost:8000`
    - _Requirements: 3.2, 7.4_

  - [x] 9.3 Update `viral-story-search/src/app/page.tsx`
    - Import apiClient
    - Replace fetch to `/api/search` with `apiClient.searchPosts()`
    - Update error handling for backend unavailable
    - _Requirements: 3.1, 3.3_

  - [x] 9.4 Delete old Next.js API route
    - Delete `viral-story-search/src/app/api/search/route.ts`
    - Delete `viral-story-search/src/lib/redditApiClient.ts` (now in Python)
    - Delete `viral-story-search/src/utils/viralScore.ts` (now in Python)
    - _Requirements: 3.1_

- [x] 10. Final checkpoint - End-to-end testing
  - Start backend: `cd backend && uvicorn app.main:app --reload --port 8000`
  - Start frontend: `cd viral-story-search && npm run dev`
  - Open browser to `http://localhost:3000`
  - Test search with different subreddits and time ranges
  - Verify results display correctly
  - Test error handling (invalid subreddit, network errors)
  - Verify caching (check backend logs for cache hits)
  - Ask the user if questions arise

- [x] 11. Create development workflow
  - [x] 11.1 Create `backend/run.sh` script
    - Add shebang and make executable
    - Run uvicorn with reload flag
    - _Requirements: 10.1_

  - [x] 11.2 Create root `package.json` with concurrent script
    - Add `concurrently` as dev dependency
    - Add script: `"dev": "concurrently \"cd backend && ./run.sh\" \"cd viral-story-search && npm run dev\""`
    - _Requirements: 10.3_

  - [x] 11.3 Update root README.md
    - Add setup instructions for backend (Python 3.10+, pip install -r requirements.txt)
    - Add setup instructions for frontend (npm install)
    - Add instructions to run both: `npm run dev` from root
    - Add environment variable setup instructions
    - _Requirements: 10.2, 10.5_

## Notes

- This is Phase 1: Reddit search migration only
- Phase 2 (future): Add LangChain story generation
- Phase 3 (future): Add LangGraph workflows and image generation
- All test tasks removed to focus on getting it working first
- Each task references specific requirements for traceability
- Checkpoints ensure the system works at key milestones


- [ ] 8. Checkpoint - Test backend independently
  - Create `.env` file with Reddit API credentials
  - Run backend: `cd backend && uvicorn app.main:app --reload --port 8000`
  - Test health check: `curl http://localhost:8000/health`
  - Test search endpoint with curl or Postman
  - Check API docs at `http://localhost:8000/docs`
  - Verify caching works (second request is faster)
  - Ask the user if questions arise

- [ ] 9. Update frontend to use Python backend
  - [ ] 9.1 Create `viral-story-search/src/lib/apiClient.ts`
    - Get API_BASE_URL from environment variable (default: http://localhost:8000)
    - Implement searchPosts function
    - Make POST request to `${API_BASE_URL}/search`
    - Handle errors and throw with error message
    - Return SearchResponse
    - _Requirements: 3.1, 3.2, 3.4_

  - [ ] 9.2 Create `viral-story-search/.env.local`
    - Add `NEXT_PUBLIC_API_URL=http://localhost:8000`
    - _Requirements: 3.2, 7.4_

  - [ ] 9.3 Update `viral-story-search/src/app/page.tsx`
    - Import apiClient
    - Replace fetch to `/api/search` with `apiClient.searchPosts()`
    - Update error handling for backend unavailable
    - _Requirements: 3.1, 3.3_

  - [ ] 9.4 Delete old Next.js API route
    - Delete `viral-story-search/src/app/api/search/route.ts`
    - Delete `viral-story-search/src/lib/redditApiClient.ts` (now in Python)
    - Delete `viral-story-search/src/utils/viralScore.ts` (now in Python)
    - _Requirements: 3.1_

- [ ] 10. Final checkpoint - End-to-end testing
  - Start backend: `cd backend && uvicorn app.main:app --reload --port 8000`
  - Start frontend: `cd viral-story-search && npm run dev`
  - Open browser to `http://localhost:3000`
  - Test search with different subreddits and time ranges
  - Verify results display correctly
  - Test error handling (invalid subreddit, network errors)
  - Verify caching (check backend logs for cache hits)
  - Ask the user if questions arise

- [ ] 11. Create development workflow
  - [ ] 11.1 Create `backend/run.sh` script
    - Add shebang and make executable
    - Run uvicorn with reload flag
    - _Requirements: 10.1_

  - [ ] 11.2 Create root `package.json` with concurrent script
    - Add `concurrently` as dev dependency
    - Add script: `"dev": "concurrently \"cd backend && ./run.sh\" \"cd viral-story-search && npm run dev\""`
    - _Requirements: 10.3_

  - [ ] 11.3 Update root README.md
    - Add setup instructions for backend (Python 3.10+, pip install -r requirements.txt)
    - Add setup instructions for frontend (npm install)
    - Add instructions to run both: `npm run dev` from root
    - Add environment variable setup instructions
    - _Requirements: 10.2, 10.5_

## Notes

- This is Phase 1: Reddit search migration only
- Phase 2 (future): Add LangChain story generation
- Phase 3 (future): Add LangGraph workflows and image generation
- All test tasks removed to focus on getting it working first
- Each task references specific requirements for traceability
- Checkpoints ensure the system works at key milestones
