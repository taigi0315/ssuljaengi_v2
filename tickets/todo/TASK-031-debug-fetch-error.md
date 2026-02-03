# Task: Debug Failed to Fetch Error in GenreSelector

## Status

- [x] Investigate Backend Status
- [x] Verify API Endpoint Exists
- [x] Check CORS/Network Issues
- [x] Fix Issue

## Context

User reported `TypeError: Failed to fetch` at `getGenres` in `src/lib/apiClient.ts`.
The error occurs when fetching `${API_BASE_URL}/webtoon/genres`.
Next.js version 16.1.2.

## Investigation Findings

1. The backend server was not running.
2. The `package.json` `dev` script was trying to execute `backend/run.bat`, which is a Windows batch file and does not work on Mac.
3. Updated `package.json` to use a cross-platform command (`python -m uvicorn ...`) instead of `run.bat`.
4. The `API_BASE_URL` correctly defaults to `http://localhost:8000`.

## Resolution

- Modified `package.json` to replace `run.bat` with `python -m uvicorn app.main:app --reload --port 8000`.
- User needs to restart `make dev` for changes to take effect.
