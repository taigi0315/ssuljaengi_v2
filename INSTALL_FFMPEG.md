# 🎬 FFmpeg Installation Guide for Windows

## What is FFmpeg?

FFmpeg is a required tool for video generation in this app. It's used to create the final MP4/WebM video files from your webtoon panels.

---

## 🚀 Quick Install (Recommended)

### Method 1: Using Chocolatey (Easiest)

If you have Chocolatey package manager installed:

```powershell
# Open PowerShell as Administrator
choco install ffmpeg
```

### Method 2: Using Scoop

If you have Scoop installed:

```powershell
scoop install ffmpeg
```

### Method 3: Manual Installation (Most Common)

1. **Download FFmpeg:**
   - Go to: https://www.gyan.dev/ffmpeg/builds/
   - Download: `ffmpeg-release-essentials.zip`
   - Or use this direct link: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z

2. **Extract the files:**
   - Extract the zip file to `C:\ffmpeg`
   - You should have: `C:\ffmpeg\bin\ffmpeg.exe`

3. **Add to PATH:**
   - Press `Windows Key + X`, select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find and select "Path"
   - Click "Edit"
   - Click "New"
   - Add: `C:\ffmpeg\bin`
   - Click "OK" on all windows

4. **Verify Installation:**
   ```cmd
   # Open new Command Prompt
   ffmpeg -version
   ```
   
   You should see FFmpeg version information.

5. **Restart your app:**
   - Close the backend and frontend servers
   - Run `START_APP.bat` again
   - Try creating a video - it should work now!

---

## 🔧 Alternative: Portable Installation

If you can't modify system PATH, you can place ffmpeg in the project:

1. Download ffmpeg.exe
2. Create folder: `c:\Users\ThaniaToaster\Documents\ssuljaengi_v2\backend\bin`
3. Place `ffmpeg.exe` in that folder
4. The backend will find it automatically

---

## ✅ Verify It's Working

After installation, run this in Command Prompt:

```cmd
ffmpeg -version
```

You should see output like:
```
ffmpeg version 2024.xx.xx
built with gcc ...
```

---

## 🆘 Troubleshooting

### "ffmpeg is not recognized"
- Make sure you added `C:\ffmpeg\bin` to PATH correctly
- **Restart your terminal/command prompt** after adding to PATH
- Restart the backend server

### "Access denied" when adding to PATH
- Run Command Prompt or PowerShell as Administrator
- Or ask your system administrator for help

### Still not working?
- Check if ffmpeg.exe exists in `C:\ffmpeg\bin\ffmpeg.exe`
- Try restarting your computer
- Check if antivirus is blocking ffmpeg

---

## 📝 For Developers

The backend checks for ffmpeg in:
1. System PATH
2. `backend/bin/ffmpeg.exe` (portable)
3. Common installation locations

If you want to specify a custom location, you can modify `backend/app/services/video_service.py`.

---

## 🎥 What FFmpeg Does

FFmpeg is used for:
- Creating MP4 videos from image sequences
- Converting WebM to MP4
- Adding audio (future feature)
- Video encoding and compression

Without FFmpeg, you can still:
- ✅ Generate webtoon scripts
- ✅ Create scene images
- ✅ Add dialogue bubbles
- ❌ Cannot create final video files

---

**Once FFmpeg is installed, restart the app and try creating a video again!**
