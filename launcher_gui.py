#!/usr/bin/env python3
"""
Ssuljaengi Application Launcher with GUI
A user-friendly graphical launcher for the Ssuljaengi application.
Can be compiled to an .exe using PyInstaller.
"""

import subprocess
import time
import webbrowser
import os
import sys
import threading
from pathlib import Path

# Try to import tkinter, fallback to console mode if not available
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("⚠️  tkinter not available, falling back to console mode")

class LauncherGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Ssuljaengi App Launcher")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        
        # Project directories
        self.project_root = self.get_project_root()
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "viral-story-search"
        
        # Processes
        self.backend_process = None
        self.frontend_process = None
        
        # Setup UI
        self.setup_ui()
        
        # Center window
        self.center_window()
        
    def get_project_root(self):
        """Get the project root directory"""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        else:
            return Path(__file__).parent
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Setup the user interface"""
        # Header
        header_frame = tk.Frame(self.window, bg="#2196F3", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🚀 Ssuljaengi App Launcher",
            font=("Arial", 20, "bold"),
            bg="#2196F3",
            fg="white"
        )
        title_label.pack(expand=True)
        
        # Main content
        content_frame = tk.Frame(self.window, bg="#f5f5f5")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Status display
        self.status_label = tk.Label(
            content_frame,
            text="Ready to launch",
            font=("Arial", 12),
            bg="#f5f5f5",
            fg="#333"
        )
        self.status_label.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            content_frame,
            mode='indeterminate',
            length=400
        )
        self.progress.pack(pady=10)
        
        # Log area
        log_frame = tk.Frame(content_frame, bg="#f5f5f5")
        log_frame.pack(pady=10, fill="both", expand=True)
        
        tk.Label(
            log_frame,
            text="Status Log:",
            font=("Arial", 10, "bold"),
            bg="#f5f5f5",
            anchor="w"
        ).pack(anchor="w")
        
        self.log_text = tk.Text(
            log_frame,
            height=8,
            font=("Consolas", 9),
            bg="white",
            fg="#333",
            relief="solid",
            borderwidth=1
        )
        self.log_text.pack(fill="both", expand=True)
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg="#f5f5f5")
        button_frame.pack(pady=10)
        
        self.launch_button = tk.Button(
            button_frame,
            text="🚀 Launch App",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            cursor="hand2",
            width=15,
            height=2,
            command=self.launch_app_thread
        )
        self.launch_button.pack(side="left", padx=5)
        
        self.close_button = tk.Button(
            button_frame,
            text="Close",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            activebackground="#da190b",
            activeforeground="white",
            cursor="hand2",
            width=15,
            height=2,
            command=self.close_app
        )
        self.close_button.pack(side="left", padx=5)
    
    def log(self, message):
        """Add message to log"""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.window.update()
    
    def update_status(self, status):
        """Update status label"""
        self.status_label.config(text=status)
        self.window.update()
    
    def kill_port_process(self, port):
        """Kill any process running on the specified port"""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'LISTENING' in line:
                            parts = line.split()
                            pid = parts[-1]
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
            else:  # Unix-like
                subprocess.run(f'lsof -ti:{port} | xargs kill -9', shell=True, capture_output=True)
        except Exception:
            pass
    
    def launch_app_thread(self):
        """Launch app in a separate thread"""
        thread = threading.Thread(target=self.launch_app, daemon=True)
        thread.start()
    
    def launch_app(self):
        """Launch the application"""
        try:
            # Disable launch button
            self.launch_button.config(state="disabled")
            
            # Start progress bar
            self.progress.start()
            
            # Verify directories
            self.update_status("Checking project directories...")
            self.log("🔍 Verifying project structure...")
            
            if not self.backend_dir.exists():
                raise Exception(f"Backend directory not found: {self.backend_dir}")
            if not self.frontend_dir.exists():
                raise Exception(f"Frontend directory not found: {self.frontend_dir}")
            
            self.log("✓ Project directories verified")
            
            # Clean up existing processes
            self.update_status("Cleaning up existing processes...")
            self.log("🧹 Cleaning up ports...")
            self.kill_port_process(8000)
            self.kill_port_process(3000)
            time.sleep(1)
            self.log("✓ Ports cleaned")
            
            # Start Backend
            self.update_status("Starting Backend Server...")
            self.log("🔧 Starting Backend Server...")
            
            backend_cmd = [
                sys.executable if not getattr(sys, 'frozen', False) else 'python',
                '-m', 'uvicorn',
                'app.main:app',
                '--reload',
                '--host', '0.0.0.0',
                '--port', '8000'
            ]
            
            if os.name == 'nt':
                self.backend_process = subprocess.Popen(
                    backend_cmd,
                    cwd=self.backend_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                self.backend_process = subprocess.Popen(
                    backend_cmd,
                    cwd=self.backend_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            self.log("✓ Backend server started")
            time.sleep(5)
            
            # Start Frontend
            self.update_status("Starting Frontend Server...")
            self.log("🎨 Starting Frontend Server...")
            
            npm_cmd = ['npm.cmd' if os.name == 'nt' else 'npm', 'run', 'dev']
            
            if os.name == 'nt':
                self.frontend_process = subprocess.Popen(
                    npm_cmd,
                    cwd=self.frontend_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                self.frontend_process = subprocess.Popen(
                    npm_cmd,
                    cwd=self.frontend_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            self.log("✓ Frontend server started")
            time.sleep(10)
            
            # Open browser
            self.update_status("Opening browser...")
            self.log("🌐 Opening browser...")
            webbrowser.open('http://localhost:3000')
            self.log("✓ Browser opened")
            
            # Success
            self.progress.stop()
            self.update_status("✅ Application Launched Successfully!")
            self.log("\n" + "="*40)
            self.log("✅ APPLICATION RUNNING!")
            self.log("="*40)
            self.log("📱 App: http://localhost:3000")
            self.log("🔧 API: http://localhost:8000")
            self.log("\n⚠️  Keep server windows open!")
            self.log("💡 Close this launcher safely.")
            
            messagebox.showinfo(
                "Success!",
                "Application launched successfully!\n\n"
                "📱 App: http://localhost:3000\n"
                "🔧 API: http://localhost:8000\n\n"
                "Two server windows are now running.\n"
                "Keep them open while using the app.\n\n"
                "This launcher will minimize automatically."
            )
            
            # Minimize the launcher window to reduce clutter
            self.window.iconify()
            
        except Exception as e:
            self.progress.stop()
            self.update_status(f"❌ Error: {str(e)}")
            self.log(f"\n❌ ERROR: {str(e)}")
            self.log("\nPlease check:")
            self.log("1. Python is installed")
            self.log("2. Node.js is installed")
            self.log("3. Dependencies are installed")
            
            messagebox.showerror(
                "Launch Failed",
                f"Failed to launch application:\n\n{str(e)}\n\n"
                "Please check that Python and Node.js are installed "
                "and all dependencies are set up correctly."
            )
            
            self.launch_button.config(state="normal")
    
    def close_app(self):
        """Close the launcher"""
        self.window.destroy()
    
    def run(self):
        """Run the GUI"""
        self.window.mainloop()

def main():
    """Main entry point"""
    if GUI_AVAILABLE:
        app = LauncherGUI()
        app.run()
    else:
        # Fallback to console mode
        print("GUI not available, use launcher.py instead")
        return 1

if __name__ == "__main__":
    sys.exit(main() or 0)
