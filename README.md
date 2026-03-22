# 🎬 Gossiptoon V2 (Viral Story Search)

A full-stack application for discovering viral Reddit stories and transforming them into webtoon-style content with AI-powered story generation.

![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-16.1-black?style=flat&logo=next.js)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat&logo=typescript)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Easy Launcher (For Non-Technical Users)](#-easy-launcher-for-non-technical-users)
- [Development](#development)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Gossiptoon V2 is a monorepo containing:

| Component    | Technology                             | Description                                                |
| ------------ | -------------------------------------- | ---------------------------------------------------------- |
| **Frontend** | Next.js 16 + React 19 + TypeScript     | Modern web interface for story discovery and visualization |
| **Backend**  | Python FastAPI + LangChain + LangGraph | AI-powered story processing and generation                 |

---

## Features

### ✅ Current Features

- 🔍 **Reddit Story Search** - Search viral posts across multiple subreddits
- 📊 **Viral Score Calculation** - Intelligent scoring based on upvotes, comments, and recency
- 📅 **Time Range Filtering** - Filter by 1h, 1d, 10d, or 100d
- 🎨 **Webtoon Generation** - Transform stories into webtoon-style scripts
- 🖼️ **AI Image Generation** - Generate character and scene images using Gemini
- 🎞️ **Multi-Panel Generation** - Create consistent vertical webtoon pages with multiple panels using structured prompts
- 🤖 **Phase 4 Agent Pipeline** - Story analysis, scene planning, cinematography, mood, SFX, and panel composition modules for higher-quality webtoon output
- 🎬 **Video Assembly** - Create video content from generated assets
- ⚡ **Response Caching** - Optimized performance with intelligent caching
- 🔐 **CORS-enabled API** - Secure frontend-backend communication

### 🔄 Active Improvement Areas

- Enhanced LangGraph workflow orchestration stabilization
- Additional prompt tuning and evaluation loops for higher-quality webtoon output
- Multiple AI provider support for image generation

---

## Architecture

```
gossiptoon_v2_2/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── config.py          # Configuration management
│   │   ├── models/            # Pydantic data models
│   │   ├── services/          # Business logic (Reddit, LLM, Image Gen)
│   │   ├── routers/           # API endpoints
│   │   ├── prompt/            # AI prompt templates
│   │   ├── utils/             # Utilities (cache, persistence)
│   │   └── workflows/         # LangGraph workflows
│   ├── docs/                  # Backend documentation
│   ├── tests/                 # Test files
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment template
│
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # Next.js app router
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # API client utilities
│   │   ├── types/             # TypeScript definitions
│   │   └── utils/             # Utility functions
│   ├── public/                # Static assets
│   └── .env.local.example     # Environment template
│
├── docs/                       # Project documentation & guides
│   ├── archive/               # Historical development notes
│   ├── CHANGELOG.md           # Version history
│   ├── CONTRIBUTING.md        # Contribution guidelines
│   ├── HOW_TO_RUN.md          # User manual
│   ├── LAUNCHER_README.md     # Launcher documentation
│   └── QUICK_REFERENCE.md     # Quick start guide
│
├── scripts/                    # Automation scripts
│   ├── START_APP.bat          # Main launcher script
│   ├── build_exe.bat          # Executable builder
│   └── INSTALL_FFMPEG.bat     # FFmpeg installer
│
├── launchers/                  # GUI launchers
│   ├── launcher_gui.py        # Python GUI launcher
│   └── Ssuljaengi Launcher.spec # PyInstaller spec
│
└── package.json               # Root package for monorepo scripts
```

---

## Quick Start

### Prerequisites

| Requirement | Version | Notes                                                                       |
| ----------- | ------- | --------------------------------------------------------------------------- |
| Python      | 3.10+   | Required                                                                    |
| Node.js     | 18+     | Required                                                                    |
| npm         | 9+      | Required                                                                    |
| **FFmpeg**  | Latest  | **Required for video generation** - [Installation Guide](docs/INSTALL_FFMPEG.md) |

⚠️ **Important:** FFmpeg must be installed and added to your system PATH for video generation to work. Run `scripts/INSTALL_FFMPEG.bat` for automatic setup.

### 1. Clone & Install

```bash
# Clone the repository
git clone <repository-url>
cd gossiptoon_v2_2

# Install root dependencies (for concurrent scripts)
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure Environment

#### Backend Configuration

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` with your credentials:

```env
# Required: Reddit API credentials
# Get from: https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# Required: Google Gemini API key
# Get from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_api_key
```

#### Frontend Configuration

```bash
cd frontend
cp .env.local.example .env.local
```

### 3. Run the Application

```bash
# From project root - runs both frontend and backend
npm run dev
```

| Service  | URL                        |
| -------- | -------------------------- |
| Frontend | http://localhost:3000      |
| Backend  | http://localhost:8000      |
| API Docs | http://localhost:8000/docs |

---

## 🚀 Easy Launcher (For Non-Technical Users)

**Don't want to use the terminal?** We've got you covered! You can now launch the entire application with a simple double-click – perfect for non-technical users.

### Option 1: Batch File Launcher ⚡ (Quickest)

**Just double-click: `scripts/START_APP.bat`**

- ✅ Works immediately, no setup required
- ✅ Automatically starts both backend and frontend
- ✅ Opens your browser to the app
- ✅ Shows helpful status messages

**How to use:**

1. Find the `START_APP.bat` file in the `scripts/` folder
2. Double-click it
3. Two console windows will open (keep them running!)
4. Your browser will open automatically
5. Start using the app! 🎉

### Option 2: GUI Launcher 🎨 (Best User Experience)

**Double-click: `launchers/launcher_gui.py`** (requires Python)

- ✅ Beautiful graphical interface
- ✅ Progress bar showing launch status
- ✅ Detailed status log
- ✅ User-friendly buttons and error messages

**How to use:**

1. Double-click `launchers/launcher_gui.py`
2. Click the "🚀 Launch App" button
3. Watch the progress bar
4. Browser opens automatically when ready!

### Option 3: Standalone .exe 📦 (For Distribution)

**Create a single executable file that anyone can run:**

1. Double-click `scripts/build_exe.bat`
2. Choose option 2 (GUI Launcher - recommended)
3. Wait for the build to complete
4. Find `Ssuljaengi Launcher.exe` in the `dist/` folder
5. Distribute this file to users – no Python needed on their machine!

**Benefits:**

- ✅ No Python installation required for end users
- ✅ Single-file distribution
- ✅ Professional appearance
- ✅ Perfect for non-technical team members

### 📚 Complete Launcher Documentation

For detailed instructions, troubleshooting, and more:

- **[docs/LAUNCHER_README.md](docs/LAUNCHER_README.md)** - Complete launcher guide
- **[docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - One-page quick start
- **[docs/HOW_TO_RUN.md](docs/HOW_TO_RUN.md)** - User manual with troubleshooting

### What the Launchers Do Automatically

All launcher options perform these steps for you:

1. Clean up any existing processes on ports 8000 and 3000
2. Start the FastAPI backend server
3. Wait for backend to initialize
4. Start the Next.js frontend server
5. Wait for frontend to start
6. Open your browser to http://localhost:3000

**No terminal commands needed!** 🎉

---

## Development

### Available Scripts

From the **project root**:

| Command              | Description                                   |
| -------------------- | --------------------------------------------- |
| `npm run dev`        | Start both frontend and backend (clean start) |
| `npm run dev:resume` | Start without cleaning cache                  |
| `npm run dev:test`   | Setup test data and start servers             |
| `npm run kill`       | Stop servers (preserve data)                  |
| `npm run stop`       | Stop servers and clean data                   |
| `npm run clean`      | Remove cached data files                      |

### Backend Development

```bash
cd backend

# Run with hot-reload
./run.sh

# Run tests
pytest

# Code formatting
black app/
flake8 app/
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Run tests
npm test

# Linting
npm run lint
npm run lint:fix

# Formatting
npm run format

# Production build
npm run build
```

---

## API Documentation

Once the backend is running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Key Endpoints

| Method | Endpoint                 | Description              |
| ------ | ------------------------ | ------------------------ |
| GET    | `/health`                | Health check             |
| GET    | `/api/v1/search/`        | Search Reddit posts      |
| POST   | `/api/v1/story/generate` | Generate story from post |
| POST   | `/api/v1/webtoon/`       | Create webtoon workflow  |
| GET    | `/api/v1/webtoon/{id}`   | Get webtoon status       |

---

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Kill processes on ports 3000 and 8000
npm run kill

# Or manually:
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

#### Backend Won't Start

1. Verify Python version: `python --version` (need 3.10+)
2. Check dependencies: `pip install -r requirements.txt`
3. Verify `.env` file exists with valid credentials
4. Check Reddit API setup: See `backend/docs/REDDIT_SETUP.md`

#### Frontend Won't Connect to Backend

1. Ensure backend is running on port 8000
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS settings in backend `config.py`

#### Reddit API Errors

- Verify credentials at https://www.reddit.com/prefs/apps
- Ensure app type is "script"
- Check rate limiting (Reddit allows ~60 requests/minute)

---

## Contributing

1. Create a feature branch from `main`
2. Make your changes following the code style guidelines
3. Ensure all tests pass
4. Submit a pull request with a clear description

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## License

This project is proprietary. All rights reserved.

---

## Support

For issues and questions, please open an issue on GitHub.

---

## ⚡ WHERE TO TUNE THE SPEED

To adjust video timing (scene duration, bubble display time, transitions), you must update **BOTH** of these files to keep them consistent:

### 1. Backend (HQ Video / FFmpeg)

- **File**: `backend/app/models/video_models.py`
- **Class**: `VideoConfig`

```python
class VideoConfig(BaseModel):
    base_duration_ms: int = 300      # Time before first bubble
    bubble_duration_ms: int = 4000   # Duration per bubble
    final_pause_ms: int = 300        # Pause after last bubble
    transition_duration_ms: int = 1500 # Scroll transition time
```

### 2. Frontend (Browser Preview)

- **File**: `frontend/src/components/VideoGenerator.tsx`
- **Object**: `VIDEO_CONFIG`

```typescript
const VIDEO_CONFIG = {
  BASE_IMAGE_DURATION_MS: 300,
  DIALOGUE_DURATION_MS: 4000,
  FINAL_PAUSE_MS: 300,
  TRANSITION_DURATION_MS: 1500,
};
```
