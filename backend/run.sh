#!/bin/bash

# Start the FastAPI backend with hot-reloading
uvicorn app.main:app --reload --port 8000
