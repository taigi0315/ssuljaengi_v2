@echo off
title FFmpeg Quick Installer

echo.
echo ========================================
echo    🎬 FFMPEG QUICK INSTALLER 🎬
echo ========================================
echo.
echo This script will help you install FFmpeg for video generation.
echo.
echo Choose an installation method:
echo.
echo 1. Download and setup FFmpeg automatically (Recommended)
echo 2. Open FFmpeg download page in browser (Manual)
echo 3. Check if FFmpeg is already installed
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto auto_install
if "%choice%"=="2" goto manual_install
if "%choice%"=="3" goto check_install
if "%choice%"=="4" goto end

:auto_install
echo.
echo ========================================
echo  Automatic Installation
echo ========================================
echo.
echo This will:
echo 1. Download FFmpeg essentials
echo 2. Extract to C:\ffmpeg
echo 3. Guide you to add it to PATH
echo.
echo Note: You'll need to add to PATH manually (we'll show you how)
echo.
pause

REM Download using PowerShell
echo Downloading FFmpeg... (this may take a minute)
powershell -Command "& {Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile '%TEMP%\ffmpeg.zip'}"

if not exist "%TEMP%\ffmpeg.zip" (
    echo.
    echo ❌ Download failed. Please try manual installation.
    goto manual_install
)

echo.
echo Download complete! Extracting...

REM Extract
powershell -Command "& {Expand-Archive -Path '%TEMP%\ffmpeg.zip' -DestinationPath 'C:\ffmpeg_temp' -Force}"

REM Move ffmpeg.exe to a clean location
if not exist "C:\ffmpeg\bin" mkdir "C:\ffmpeg\bin"

echo Moving files to C:\ffmpeg...
xcopy "C:\ffmpeg_temp\ffmpeg-*\bin\ffmpeg.exe" "C:\ffmpeg\bin\" /Y

REM Cleanup
rd /s /q "C:\ffmpeg_temp"
del "%TEMP%\ffmpeg.zip"

echo.
echo ========================================
echo  ✅ FFmpeg Downloaded!
echo ========================================
echo.
echo Location: C:\ffmpeg\bin\ffmpeg.exe
echo.
echo 🚨 IMPORTANT: You must add FFmpeg to PATH
echo.
echo Follow these steps:
echo.
echo 1. Press Windows Key + X
echo 2. Select "System"
echo 3. Click "Advanced system settings"
echo 4. Click "Environment Variables"
echo 5. Under "System variables", find "Path"
echo 6. Click "Edit"
echo 7. Click "New"
echo 8. Type: C:\ffmpeg\bin
echo 9. Click OK on all windows
echo 10. RESTART your terminal/cmd
echo.
echo After adding to PATH, restart the app!
echo.
pause
goto end

:manual_install
echo.
echo ========================================
echo  Manual Installation
echo ========================================
echo.
echo Opening FFmpeg download page in your browser...
echo.
echo Please:
echo 1. Download "ffmpeg-release-essentials.zip"
echo 2. Extract to C:\ffmpeg
echo 3. Add C:\ffmpeg\bin to your system PATH
echo.
echo See INSTALL_FFMPEG.md for detailed instructions.
echo.
start https://www.gyan.dev/ffmpeg/builds/
pause
goto end

:check_install
echo.
echo ========================================
echo  Checking FFmpeg Installation
echo ========================================
echo.
echo Running: ffmpeg -version
echo.
ffmpeg -version
if errorlevel 1 (
    echo.
    echo ❌ FFmpeg is NOT installed or not in PATH
    echo.
    echo Please install FFmpeg first.
    echo.
) else (
    echo.
    echo ========================================
    echo  ✅ FFmpeg is Installed!
    echo ========================================
    echo.
    echo You can now use video generation features.
    echo Restart the app if it's currently running.
    echo.
)
pause
goto end

:end
echo.
echo Exiting installer...
