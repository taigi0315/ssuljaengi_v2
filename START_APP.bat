@echo off
title Ssuljaengi App Launcher

echo.
echo ========================================
echo    🚀 SSULJAENGI APP LAUNCHER 🚀
echo ========================================
echo.
echo Starting application...
echo.

REM Kill any existing processes on ports 8000 and 3000
echo 🧹 Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Set up Node.js environment
set "PATH=%PATH%;C:\Program Files\nodejs"

REM Start backend server in a new window
echo 🔧 Starting Backend Server...
start "Ssuljaengi Backend" cmd /c "cd /d "%~dp0backend" && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a few seconds for backend to initialize
timeout /t 5 /nobreak >nul

REM Start frontend server in a new window
echo 🎨 Starting Frontend Server...
start "Ssuljaengi Frontend" cmd /c "cd /d "%~dp0viral-story-search" && npm run dev"

REM Wait for frontend to start
echo ⏳ Waiting for servers to start...
timeout /t 10 /nobreak >nul

REM Open browser
echo 🌐 Opening browser...
start http://localhost:3000

echo.
echo ========================================
echo    ✅ APPLICATION LAUNCHED! ✅
echo ========================================
echo.
echo 📱 App: http://localhost:3000
echo 🔧 API: http://localhost:8000
echo.
echo Two server windows are now running:
echo   - "Ssuljaengi Backend" (Python/FastAPI)
echo   - "Ssuljaengi Frontend" (Next.js)
echo.
echo ⚠️  Keep those windows open while using the app!
echo 💡 You can close THIS window now.
echo.
echo To stop the app: Close the server windows
echo.
pause
