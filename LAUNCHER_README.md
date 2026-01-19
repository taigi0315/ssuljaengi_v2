# 🚀 Easy App Launcher - Complete Guide

## What is This?

This folder contains **everything you need** to easily run the Ssuljaengi application without using command line or terminal. Perfect for non-technical users!

---

## 🎯 I Just Want to Run the App! (Start Here)

### Quickest Way ⚡
1. Find the file named **`START_APP.bat`**
2. **Double-click it**
3. Wait for two black windows to open (these are your servers - don't close them!)
4. Your web browser will automatically open with the app
5. **You're done!** Start using the app 🎉

That's literally it. Nothing else needed.

---

## 🎨 Want a Nicer Interface?

If you want a beautiful graphical launcher instead of black console windows:

### Using the GUI Launcher (If you have Python)
1. Find the file named **`launcher_gui.py`**
2. **Double-click it**
3. A nice window will appear (see image below)
4. Click the **"🚀 Launch App"** button
5. Watch the progress bar
6. Browser opens automatically when ready!

![GUI Launcher Screenshot](launcher_gui_mockup.png)

*The GUI launcher shows you exactly what's happening with a progress bar and status messages!*

---

## 📦 For IT/Technical Person: Creating an .exe File

If you want to give users a single `.exe` file they can run:

1. Double-click **`build_exe.bat`**
2. Choose option **2** (GUI Launcher - recommended)
3. Wait for the build process to complete
4. Find the file **`Ssuljaengi Launcher.exe`** in the `dist` folder
5. Copy this `.exe` file to any computer
6. Users just double-click the `.exe` - no Python needed!

**Benefits of .exe:**
- ✅ No Python installation required
- ✅ Single file distribution
- ✅ Professional appearance
- ✅ Easy for non-technical users

---

## 📚 Documentation Files

We've created several helpful documents:

| File | Purpose | Who Should Read |
|------|---------|-----------------|
| **`QUICK_REFERENCE.md`** | One-page quick guide | Everyone (start here!) |
| **`HOW_TO_RUN.md`** | Complete user manual | Non-technical users |
| **`LAUNCHER_SOLUTION.md`** | Technical documentation | Developers/IT |

---

## 🛑 How to Stop the App

**Simple method:**
- Close the black console windows (or the launcher windows)
- That's it!

**OR:**
- In the console windows, press `Ctrl + C`
- Close the windows

---

## ❓ Common Questions

### Do I need to install anything?
- **For .bat files:** No, just double-click
- **For .py files:** Need Python installed
- **For .exe files:** No, works standalone

### Can I close the launcher window after starting?
- **Yes!** Once the app is running, you can close the launcher window
- Just keep the SERVER windows (backend/frontend) open

### Where can I access the app?
- The app will open automatically in your browser
- Manual URL: `http://localhost:3000`
- API: `http://localhost:8000`

### Can I create a desktop shortcut?
- **Yes!** Right-click on `START_APP.bat`
- Choose "Send to" → "Desktop (create shortcut)"
- Now you can launch from your desktop!

### What if something goes wrong?
- Try restarting your computer
- Make sure Python and Node.js are installed
- Check the troubleshooting section in `HOW_TO_RUN.md`
- Contact your IT support

---

## 🎯 Files Overview

### 📁 You'll Use These:

| File | What It Does |
|------|--------------|
| `START_APP.bat` | ⭐ Main launcher - just double-click this |
| `launcher_gui.py` | Beautiful GUI version (requires Python) |
| `launcher.py` | Console version (requires Python) |
| `build_exe.bat` | Creates .exe files from Python scripts |

### 📄 Documentation:

| File | Contents |
|------|----------|
| `QUICK_REFERENCE.md` | Quick start guide (1 page) |
| `HOW_TO_RUN.md` | Complete user manual |
| `LAUNCHER_SOLUTION.md` | Technical details for developers |

### 🚫 Don't Worry About These:

| File/Folder | Purpose |
|-------------|---------|
| `build/` | Temporary build files (auto-generated) |
| `dist/` | Contains .exe files after building |
| `*.spec` | PyInstaller configuration (auto-generated) |

---

## 🎓 For Developers

### What These Launchers Do:
1. Kill any existing processes on ports 8000 and 3000
2. Start the FastAPI backend server
3. Wait for backend to initialize
4. Start the Next.js frontend server
5. Wait for frontend to initialize
6. Open the default browser to http://localhost:3000

### Tech Stack:
- **Backend:** Python + FastAPI (port 8000)
- **Frontend:** Next.js (port 3000)
- **Launchers:** Batch script, Python with tkinter
- **Build Tool:** PyInstaller

### Customization:
- To change ports: Edit the launcher files
- To add custom icons: Use `--icon` flag in PyInstaller
- To add features: Modify `launcher_gui.py`

---

## 💡 Pro Tips

1. **Create a shortcut** to `START_APP.bat` on your desktop
2. **Bookmark** `http://localhost:3000` in your browser
3. **Keep server windows minimized** - don't close them while using the app
4. **For team distribution**: Build the .exe once, share it with everyone
5. **For presentations**: Use the GUI launcher - it looks more professional

---

## 🆘 Need Help?

### For Users:
- Read `QUICK_REFERENCE.md` for fast answers
- Read `HOW_TO_RUN.md` for detailed instructions
- Contact your IT team or development team

### For Developers:
- Read `LAUNCHER_SOLUTION.md` for technical details
- Check the build logs if .exe creation fails
- Ensure all dependencies are installed

---

## ✅ Quick Checklist Before Distribution

Before giving these launchers to users, verify:

- [ ] `START_APP.bat` works on your machine
- [ ] Backend and frontend start successfully
- [ ] Browser opens automatically
- [ ] App loads correctly in browser
- [ ] Tested stopping and restarting
- [ ] Built and tested .exe (if distributing)
- [ ] Created user documentation/shortcuts
- [ ] Tested on a different computer (if possible)

---

## 🎉 Success!

You now have **three easy ways** to run the app:

1. **Quick & Easy:** Double-click `START_APP.bat` ⚡
2. **Nice Interface:** Double-click `launcher_gui.py` 🎨
3. **Professional:** Build and use `Ssuljaengi Launcher.exe` 📦

Pick the one that works best for you!

---

**Last Updated:** January 18, 2026
**Version:** 1.0
**For:** Ssuljaengi V2 Project

**Questions?** Refer to the documentation files or contact your development team.
