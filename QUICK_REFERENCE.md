# 🚀 Ssuljaengi App - Quick Reference Card

## For Non-Technical Users

### ⚡ Choose Your Launcher

**Option 1: ONE Terminal** ⭐ RECOMMENDED
- **File:** `START_APP.bat`
- **Windows:** 1 terminal + browser
- **Best for:** Most users

**Option 2: NO Terminals (Silent)**
- **File:** `START_APP_SILENT.bat`  
- **Windows:** Just browser (servers run in background)
- **Best for:** Clean desktop

**Option 3: Completely Invisible**
- **File:** `START_APP_NO_WINDOWS.vbs`
- **Windows:** Only browser (no terminals visible)
- **Best for:** Simplest experience

**Option 4: GUI Launcher**
- **File:** `launcher_gui.py`
- **Windows:** GUI + 2 server terminals + browser
- **Best for:** Visual feedback

---

### 🛑 How to Stop the App

**If you used START_APP.bat:**
- Close the PowerShell window

**If you used Silent or No Windows:**
- Double-click `STOP_APP.bat`

**If you used GUI launcher:**
- Close the server windows

---

### 🆘 Something Wrong?

**Problem: Nothing happens when I double-click**
- Make sure Python and Node.js are installed
- Ask your IT team for help

**Problem: Browser doesn't open**
- Manually go to: `http://localhost:3000`

**Problem: Error messages appear**
- Restart your computer
- Try again
- If still broken, contact support

---

### 📍 Bookmark This URL
Once the app is running, bookmark this:
**http://localhost:3000**

You can use this URL while the servers are running!

---

### 💡 Pro Tips
1. Try `START_APP_NO_WINDOWS.vbs` for cleanest experience
2. Use `START_APP.bat` if you want to see what's happening
3. Don't close terminal windows while using the app (if visible)
4. Run `STOP_APP.bat` to cleanly stop background servers

---

**Need Help?** Read `LAUNCHER_OPTIONS.md` for detailed comparison.

