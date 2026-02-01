@echo off
REM Start the FastAPI backend with hot-reloading
python -m uvicorn app.main:app --reload --port 8000