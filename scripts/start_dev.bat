@echo off
echo 🔧 Setting up Node.js environment...
set "PATH=%PATH%;C:\Program Files\nodejs"

echo 📂 Switching to frontend directory...
cd frontend

echo 🚀 Starting development server...
echo (You can access the app at http://localhost:3000 once it starts)
echo.
npm run dev
pause
