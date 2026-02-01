# 🚀 Launcher Options - Choose Your Experience

## Which Launcher Should I Use?

We have **FOUR different options** - from "show everything" to "completely invisible". Pick the one that fits your preference!

---

## Option 1: TWO TERMINALS ⭐ **RECOMMENDED**

**File:** `START_APP.bat`

**What you see:**
- ✅ TWO cmd windows (Backend + Frontend)
- ✅ Clear window titles so you know which is which  
- ✅ Reliable - works on all Windows systems
- ✅ Launcher window closes after startup
- ✅ Browser opens automatically

**Result:** 2 terminal windows + browser

**Perfect for:** Most users who want reliability and can see logs if needed

---

## Option 2: MINIMIZED WINDOWS 🔇

**File:** `START_APP_SILENT.bat`

**What you see:**
- ✅ Browser opens
- ✅ Two minimized windows in taskbar
- ✅ Clean desktop experience
- ⚠️ Logs hidden unless you open the minimized windows

**To stop servers:** Run `STOP_APP.bat` or close the minimized windows from taskbar

**Perfect for:** Clean desktops while still being able to check logs if needed

---

## Option 3: COMPLETELY INVISIBLE 👻

**File:** `START_APP_NO_WINDOWS.vbs`

**What you see:**
- ✅ Small popup notification
- ✅ Then just the browser
- ✅ Not even a launcher window
- ✅ Cleanest possible experience

**To stop servers:** Run `STOP_APP.bat`

**Perfect for:** Ultimate simplicity - double-click and forget

---

## Option 4: GUI Launcher 🎨

**File:** `launcher_gui.py`

**What you see:**
- ✅ Beautiful graphical interface
- ✅ Progress bar and status
- ✅ Two server console windows  
- ✅ Launcher minimizes automatically after starting
- ✅ Browser opens automatically

**Result:** 2 server terminals + launcher (minimized) + browser

**Perfect for:** People who want visual feedback but not terminal clutter

---

## Quick Comparison

| Launcher | Terminal Windows | Launcher Window | Best For |
|----------|-----------------|-----------------|----------|
| `START_APP.bat` | 1 (PowerShell) | Closes auto | ⭐ Most users |
| `START_APP_SILENT.bat` | 0 (background) | Closes auto | Clean desktop |
| `START_APP_NO_WINDOWS.vbs` | 0 (invisible) | Never shows | Ultimate simplicity |
| `launcher_gui.py` | 2 (servers) | Minimizes auto | GUI lovers |

---

## How To Stop The App

### If you used START_APP.bat:
- Just close the PowerShell window

### If you used Silent or No Windows versions:
- Double-click `STOP_APP.bat`
- Or restart your computer (servers will stop automatically)

### If you used GUI launcher:
- Close the server terminal windows

---

## My Recommendation 🎯

**For everyday use:** `START_APP.bat` (1 terminal only)

**For demos/presentations:** `START_APP_NO_WINDOWS.vbs` (completely invisible)

**For troubleshooting:** `launcher_gui.py` (see detailed logs in GUI)

---

## Converting to .exe

You can convert **any** Python launcher to .exe:

```batch
# Run this
build_exe.bat

# Choose option 2 for GUI launcher
# Or option 1 for console launcher
```

The .exe will behave like the original Python script but won't need Python installed!

---

## Technical Details

### What Each Does Behind The Scenes:

**START_APP.bat:**
- Uses PowerShell Jobs to run both servers in one window
- Captures output from both servers
- Auto-closes launcher after 3 seconds

**START_APP_SILENT.bat:**
- Uses `PowerShell -WindowStyle Hidden`
- Runs servers in background processes
- No windows created

**START_APP_NO_WINDOWS.vbs:**
- VBScript wrapper that runs batch file with window style 0 (hidden)
- Shows only a popup notification
- Completely invisible execution

**launcher_gui.py:**
- Python tkinter GUI
- Creates separate console windows for servers
- Auto-minimizes after success

---

**Bottom Line:** No more 3 terminal windows! Pick your favorite way to launch. 🚀
