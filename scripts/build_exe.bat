@echo off
echo ========================================
echo  PyInstaller Build Script
echo  Creates .exe files from Python launchers
echo ========================================
echo.

REM Install PyInstaller if not already installed
echo Installing/Updating PyInstaller...
pip install --upgrade pyinstaller
echo.

echo Choose which launcher to build:
echo.
echo 1. Console Launcher (launcher.py)
echo 2. GUI Launcher (launcher_gui.py) - RECOMMENDED
echo 3. Both
echo.

set /p choice="Enter your choice (1, 2, or 3): "

if "%choice%"=="1" goto build_console
if "%choice%"=="2" goto build_gui
if "%choice%"=="3" goto build_both
goto invalid

:build_console
echo.
echo Building Console Launcher...
pyinstaller --onefile --name="Ssuljaengi Launcher Console" launcher.py
goto done

:build_gui
echo.
echo Building GUI Launcher...
pyinstaller --onefile --windowed --name="Ssuljaengi Launcher" launcher_gui.py
goto done

:build_both
echo.
echo Building Console Launcher...
pyinstaller --onefile --name="Ssuljaengi Launcher Console" launcher.py
echo.
echo Building GUI Launcher...
pyinstaller --onefile --windowed --name="Ssuljaengi Launcher" launcher_gui.py
goto done

:invalid
echo Invalid choice.
goto end

:done
echo.
echo ========================================
echo  Build Complete!
echo ========================================
echo.
echo Your .exe file(s) can be found in the 'dist' folder
echo You can distribute these files to users who don't have Python installed
echo.

:end
pause
