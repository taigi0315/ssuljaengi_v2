@echo off
title Stop Ssuljaengi Servers

echo.
echo ========================================
echo    🛑 STOPPING SSULJAENGI SERVERS 🛑
echo ========================================
echo.

REM Kill processes on ports 8000 and 3000
echo 🛑 Stopping Backend Server (port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo    ✓ Backend stopped
)

echo 🛑 Stopping Frontend Server (port 3000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo    ✓ Frontend stopped
)

echo.
echo ========================================
echo    ✅ SERVERS STOPPED! ✅
echo ========================================
echo.
echo Both servers have been stopped.
echo You can restart them by running START_APP.bat
echo.
pause
