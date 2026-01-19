# 🚀 How to Run Ssuljaengi App (Non-Technical Guide)

## 🎯 Quick Start (Easiest Method)

### Option 1: Double-Click the Batch File ⭐ **RECOMMENDED FOR QUICK START**
1. **Find the file** named `START_APP.bat` in the project folder
2. **Double-click** on it
3. Wait for two black windows to appear (these are the servers)
4. Your web browser will automatically open with the app!
5. **DO NOT CLOSE** the black windows while using the app

That's it! 🎉

### Option 2: Use the GUI Launcher 🎨 **BEST USER EXPERIENCE**
1. **Find the file** named `launcher_gui.py` in the project folder
2. **Double-click** on it (or create an .exe from it - see below)
3. A nice graphical window will appear
4. Click the **"🚀 Launch App"** button
5. Watch the progress bar and status messages
6. Your browser will automatically open when ready!

The GUI launcher provides:
- ✨ Beautiful graphical interface
- 📊 Progress bar showing startup status
- 📝 Detailed status log
- ⚠️ Clear error messages if something goes wrong
- 💡 User-friendly buttons and controls

---

## 🔧 Advanced: Creating an .exe File (Optional)

If you want an even cleaner experience with a single `.exe` file:

### Steps to Create the .exe:

1. **Open Command Prompt (CMD)**:
   - Press `Windows Key + R`
   - Type `cmd` and press Enter

2. **Navigate to the project folder**:
   ```
   cd C:\Users\ThaniaToaster\Documents\ssuljaengi_v2
   ```

3. **Install PyInstaller** (one-time only):
   ```
   pip install pyinstaller
   ```

4. **Create the .exe file**:
   ```
   pyinstaller --onefile --noconsole --icon=viral-story-search/public/favicon.ico --name="Ssuljaengi Launcher" launcher.py
   ```
   
   Or if you want to see the console for debugging:
   ```
   pyinstaller --onefile --icon=viral-story-search/public/favicon.ico --name="Ssuljaengi Launcher" launcher.py
   ```

5. **Find your .exe**:
   - After the process completes, look in the `dist` folder
   - You'll find `Ssuljaengi Launcher.exe`
   - You can move this file anywhere and double-click it to launch the app!

### 📦 Alternative: Simpler .exe Creation

If the above doesn't work, try this simpler version:
```
pyinstaller --onefile --name="Ssuljaengi Launcher" launcher.py
```

---

## 🆘 Troubleshooting

### Problem: "Python is not recognized"
**Solution**: You need to install Python first
- Download from: https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

### Problem: "npm is not recognized"  
**Solution**: You need to install Node.js first
- Download from: https://nodejs.org/
- Install the LTS (Long Term Support) version

### Problem: Servers won't start
**Solution**: Make sure dependencies are installed
1. Open Command Prompt in the project folder
2. For backend:
   ```
   cd backend
   pip install -r requirements.txt
   ```
3. For frontend:
   ```
   cd viral-story-search
   npm install
   ```

### Problem: Port already in use
**Solution**: The launcher automatically cleans up ports, but if it fails:
1. Restart your computer, or
2. Manually kill the processes in Task Manager

---

## 📋 What Each File Does

- **`START_APP.bat`** - Simple batch script to launch the app (double-click this!)
- **`launcher.py`** - Python script that can be converted to .exe
- **`start_backend.bat`** - Only starts the backend (for developers)
- **`start_dev.bat`** - Only starts the frontend (for developers)

---

## 💡 Tips for Non-Technical Users

1. **Always use `START_APP.bat`** - It's the simplest way to run the app
2. **Don't close the black windows** - They run the app in the background
3. **To stop the app** - Just close the black windows
4. **Bookmark** `http://localhost:3000` - You can access the app from here while it's running

---

## 🎨 Making it Even Easier (Desktop Shortcut)

1. Right-click on `START_APP.bat`
2. Select "Send to" → "Desktop (create shortcut)"
3. Right-click on the new desktop shortcut
4. Select "Properties"
5. Click "Change Icon" and choose an icon you like
6. Click OK

Now you have a desktop icon to launch the app! 🎉

---

## ℹ️ System Requirements

- Windows 10 or later
- Python 3.8 or later
- Node.js 16 or later
- At least 4GB RAM
- Internet connection (for initial setup)

---

**Need Help?** Contact your development team or refer to the technical documentation in the `docs` folder.
