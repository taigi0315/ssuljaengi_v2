@echo off
title Ssuljaengi App Launcher (Minimized Mode)

echo.
echo ========================================
echo    🚀 SSULJAENGI SILENT LAUNCHER 🚀
echo ========================================
echo.
echo This will start the app with minimized windows!
echo The servers will run in the background.
echo.

REM Kill any existing processes on ports 8000 and 3000
echo 🧹 Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo 🔧 Starting servers (minimized windows)...

REM Start backend minimized
start /min "Ssuljaengi Backend" cmd /c "cd /d "%~dp0backend" && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend
timeout /t 5 /nobreak >nul

REM Start frontend minimized
start /min "Ssuljaengi Frontend" cmd /c "cd /d "%~dp0frontend" && npm run dev"

REM Wait for frontend
echo ⏳ Waiting for servers to initialize...
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
echo.
echo ✓ Servers are running in minimized windows
echo ✓ Check your taskbar for "Ssuljaengi Backend" and "Ssuljaengi Frontend"
echo ✓ To stop the servers, run: STOP_APP.bat
echo   Or close the minimized windows from taskbar
echo.
echo This launcher will close in 3 seconds...
timeout /t 3 /nobreak >nul
