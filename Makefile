# Gossiptoon V2 - Development Makefile
# Simple commands to manage the full-stack application

.PHONY: help install dev dev-logs backend frontend setup clean kill test lint

# Default target
help:
	@echo "Gossiptoon V2 - Available Commands:"
	@echo ""
	@echo "🚀 Development:"
	@echo "  make dev        - Start both backend and frontend (concurrently)"
	@echo "  make dev-logs   - Start both with detailed logs (separate terminals)"
	@echo "  make backend    - Start backend only"
	@echo "  make frontend   - Start frontend only"
	@echo ""
	@echo "📦 Setup:"
	@echo "  make install    - Install all dependencies"
	@echo "  make setup      - Complete setup (install + env files)"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean      - Clean cache and temp files"
	@echo "  make kill       - Stop all running servers"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test       - Run all tests"
	@echo "  make lint       - Run linting"
	@echo ""
	@echo "ℹ️  Use 'make <command>' to run any command"

# Development commands
dev:
	@echo "🚀 Starting both backend and frontend..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo ""
	npm run dev

dev-logs:
	@echo "🚀 Starting backend and frontend in separate terminals..."
	@echo "This will open two command windows for detailed logs"
	@echo ""
	@start "Backend Server" cmd /c "cd backend && python -m uvicorn app.main:app --reload --port 8000"
	@start "Frontend Server" cmd /c "cd frontend && npm run dev"
	@echo "✅ Servers starting in separate windows..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"

backend:
	@echo "🔧 Starting backend server..."
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo ""
	cd backend && python -m uvicorn app.main:app --reload --port 8000

frontend:
	@echo "🎨 Starting frontend server..."
	@echo "Frontend: http://localhost:3000"
	@echo ""
	cd frontend && npm run dev

# Setup commands
install:
	@echo "📦 Installing all dependencies..."
	@echo ""
	@echo "Installing root dependencies..."
	npm install
	@echo ""
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo ""
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo ""
	@echo "✅ All dependencies installed!"

setup: install
	@echo "⚙️ Setting up environment files..."
	@echo ""
	@if not exist "backend\.env" ( \
		echo "Creating backend/.env from template..." && \
		copy "backend\.env.example" "backend\.env" \
	) else ( \
		echo "backend/.env already exists" \
	)
	@if not exist "frontend\.env.local" ( \
		echo "Creating frontend/.env.local from template..." && \
		copy "frontend\.env.local.example" "frontend\.env.local" \
	) else ( \
		echo "frontend/.env.local already exists" \
	)
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "📝 Next steps:"
	@echo "1. Edit backend/.env with your Reddit and Google API keys"
	@echo "2. Edit frontend/.env.local if needed"
	@echo "3. Run 'make dev' to start the application"

# Maintenance commands
clean:
	@echo "🧹 Cleaning cache and temporary files..."
	@if exist "backend\data\*.json" del /q "backend\data\*.json"
	@if exist "backend\cache\images\*" del /q "backend\cache\images\*"
	@if exist "backend\__pycache__" rmdir /s /q "backend\__pycache__"
	@if exist "frontend\.next" rmdir /s /q "frontend\.next"
	@if exist "frontend\node_modules\.cache" rmdir /s /q "frontend\node_modules\.cache"
	@echo "✅ Cleanup complete!"

kill:
	@echo "⏹️ Stopping all servers..."
	@taskkill /f /im "uvicorn.exe" 2>nul || echo "No uvicorn processes found"
	@taskkill /f /im "node.exe" 2>nul || echo "No node processes found"
	@for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a 2>nul
	@for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /f /pid %%a 2>nul
	@echo "✅ Servers stopped!"

# Testing commands
test:
	@echo "🧪 Running all tests..."
	@echo ""
	@echo "Running backend tests..."
	cd backend && python -m pytest
	@echo ""
	@echo "Running frontend tests..."
	cd frontend && npm test -- --watchAll=false
	@echo ""
	@echo "✅ All tests completed!"

lint:
	@echo "🔍 Running linting..."
	@echo ""
	@echo "Linting backend..."
	cd backend && python -m flake8 app/ --max-line-length=100 --ignore=E203,W503 || echo "Backend linting completed"
	@echo ""
	@echo "Linting frontend..."
	cd frontend && npm run lint || echo "Frontend linting completed"
	@echo ""
	@echo "✅ Linting completed!"

# Quick shortcuts
start: dev
run: dev
serve: dev
up: dev
down: kill
stop: kill
logs: dev-logs