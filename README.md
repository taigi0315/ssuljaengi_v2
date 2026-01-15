# Viral Story Search

A full-stack application for discovering viral Reddit stories with a Next.js frontend and Python FastAPI backend.

## Architecture

- **Frontend**: Next.js 14 with React and TypeScript
- **Backend**: Python FastAPI with async support
- **API**: RESTful API with automatic documentation

## Prerequisites

### Backend Requirements
- Python 3.10 or higher
- pip (Python package manager)

### Frontend Requirements
- Node.js 18 or higher
- npm (Node package manager)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd viral-story-search-monorepo
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create environment file from example
cp .env.example .env

# IMPORTANT: Set up Reddit API credentials
# Follow the guide in backend/REDDIT_SETUP.md to get your credentials
# Then edit .env and add your Reddit API credentials:
#   REDDIT_CLIENT_ID=your_actual_client_id
#   REDDIT_CLIENT_SECRET=your_actual_client_secret
#   REDDIT_USER_AGENT=viral-story-search/1.0
```

**⚠️ REQUIRED**: You must set up Reddit API credentials or you'll get authentication errors.
See detailed instructions in [`backend/REDDIT_SETUP.md`](backend/REDDIT_SETUP.md)

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd viral-story-search

# Install Node dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Edit .env.local and set backend URL (default: http://localhost:8000)
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Environment Variables

#### Backend (.env)
```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# CORS
FRONTEND_URL=http://localhost:3000

# Reddit API (Required)
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=viral-story-search/1.0

# Cache Configuration
CACHE_TTL=300
CACHE_MAX_SIZE=100
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### Option 1: Run Both Services Concurrently (Recommended)

**IMPORTANT**: Run this from the **project root** directory (gossiptoon_v2_2), NOT from inside viral-story-search!

```bash
# From project root (gossiptoon_v2_2)
cd /path/to/gossiptoon_v2_2

# Install concurrently (first time only)
npm install

# Run both frontend and backend
npm run dev
```

This will start:
- Backend on http://localhost:8000
- Frontend on http://localhost:3000

### Option 2: Run Services Separately

#### Terminal 1 - Backend
```bash
cd backend
./run.sh
# Or manually: uvicorn app.main:app --reload --port 8000
```

#### Terminal 2 - Frontend
```bash
cd viral-story-search
npm run dev
```

## Using the Application

1. Open your browser to http://localhost:3000
2. Select subreddits from the dropdown
3. Choose a time range (1h, 1d, 10d, 100d)
4. Set the number of posts to retrieve
5. Click "Search" to find viral stories
6. Results are sorted by viral score (combination of upvotes, comments, and recency)

## API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

## Development

### Backend Development

```bash
cd backend

# Run with hot-reload
./run.sh

# Run tests (when available)
pytest

# Check code style
black app/
flake8 app/
```

### Frontend Development

```bash
cd viral-story-search

# Run development server
npm run dev

# Run tests
npm test

# Run linter
npm run lint

# Build for production
npm run build
```

## Project Structure

```
.
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── config.py          # Configuration management
│   │   ├── models/            # Pydantic data models
│   │   ├── services/          # Business logic (Reddit API, etc.)
│   │   ├── routers/           # API endpoints
│   │   └── utils/             # Utilities (cache, viral score, etc.)
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   └── run.sh                # Backend startup script
│
├── viral-story-search/        # Next.js frontend
│   ├── src/
│   │   ├── app/              # Next.js app directory
│   │   ├── components/       # React components
│   │   ├── lib/              # API client and utilities
│   │   └── types/            # TypeScript type definitions
│   ├── package.json
│   └── .env.local            # Frontend environment variables
│
├── package.json              # Root package.json for concurrent scripts
└── README.md                 # This file
```

## Features

### Current Features (Phase 1)
- ✅ Reddit post search across multiple subreddits
- ✅ Viral score calculation (upvotes + comments + recency)
- ✅ Time range filtering (1h, 1d, 10d, 100d)
- ✅ Response caching for improved performance
- ✅ Error handling and rate limiting
- ✅ CORS-enabled API
- ✅ Automatic API documentation

### Future Features (Planned)
- 🔄 LangChain-powered story generation
- 🔄 LangGraph workflow orchestration
- 🔄 AI-generated images from stories
- 🔄 Story customization (style, length)
- 🔄 Image generation with multiple providers

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**Missing dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

**Reddit API errors:**
- Verify your Reddit API credentials in `.env`
- Check that your Reddit app is configured correctly at https://www.reddit.com/prefs/apps

### Frontend Issues

**Port already in use:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

**Cannot connect to backend:**
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS settings in backend `config.py`

**Missing dependencies:**
```bash
cd viral-story-search
npm install
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly (both frontend and backend)
4. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub.
