#!/usr/bin/env python3
"""
Ssuljaengi Application Launcher
This script starts both backend and frontend servers and opens the browser.
Can be compiled to an .exe using PyInstaller for easy distribution.
"""

import subprocess
import time
import webbrowser
import os
import sys
import signal
from pathlib import Path

# Terminal colors for better UX
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.RESET):
    """Print colored message to console"""
    print(f"{color}{message}{Colors.RESET}")

def print_header():
    """Print application header"""
    print("\n" + "="*50)
    print_colored("    🚀 SSULJAENGI APP LAUNCHER 🚀", Colors.CYAN + Colors.BOLD)
    print("="*50 + "\n")

def kill_port_process(port):
    """Kill any process running on the specified port"""
    try:
        if os.name == 'nt':  # Windows
            # Find and kill process on port
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
        else:  # Unix-like systems
            subprocess.run(f'lsof -ti:{port} | xargs kill -9', shell=True, capture_output=True)
    except Exception as e:
        pass  # Silently fail if no process is running

def get_project_root():
    """Get the project root directory"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent

def main():
    """Main launcher function"""
    print_header()
    
    project_root = get_project_root()
    backend_dir = project_root / "backend"
    frontend_dir = project_root / "viral-story-search"
    
    # Verify directories exist
    if not backend_dir.exists():
        print_colored(f"❌ Error: Backend directory not found at {backend_dir}", Colors.RED)
        input("\nPress Enter to exit...")
        return 1
    
    if not frontend_dir.exists():
        print_colored(f"❌ Error: Frontend directory not found at {frontend_dir}", Colors.RED)
        input("\nPress Enter to exit...")
        return 1
    
    print_colored("🧹 Cleaning up existing processes...", Colors.YELLOW)
    kill_port_process(8000)  # Backend port
    kill_port_process(3000)  # Frontend port
    time.sleep(1)
    
    processes = []
    
    try:
        # Start Backend Server
        print_colored("\n🔧 Starting Backend Server...", Colors.GREEN)
        backend_cmd = [
            sys.executable if not getattr(sys, 'frozen', False) else 'python',
            '-m', 'uvicorn',
            'app.main:app',
            '--reload',
            '--host', '0.0.0.0',
            '--port', '8000'
        ]
        
        if os.name == 'nt':  # Windows
            backend_process = subprocess.Popen(
                backend_cmd,
                cwd=backend_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            backend_process = subprocess.Popen(
                backend_cmd,
                cwd=backend_dir
            )
        processes.append(backend_process)
        print_colored("   ✓ Backend server starting...", Colors.GREEN)
        
        # Wait for backend to initialize
        print_colored("\n⏳ Waiting for backend to initialize...", Colors.YELLOW)
        time.sleep(5)
        
        # Start Frontend Server
        print_colored("\n🎨 Starting Frontend Server...", Colors.GREEN)
        npm_cmd = ['npm.cmd' if os.name == 'nt' else 'npm', 'run', 'dev']
        
        if os.name == 'nt':  # Windows
            frontend_process = subprocess.Popen(
                npm_cmd,
                cwd=frontend_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            frontend_process = subprocess.Popen(
                npm_cmd,
                cwd=frontend_dir
            )
        processes.append(frontend_process)
        print_colored("   ✓ Frontend server starting...", Colors.GREEN)
        
        # Wait for frontend to start
        print_colored("\n⏳ Waiting for frontend to start...", Colors.YELLOW)
        time.sleep(10)
        
        # Open browser
        print_colored("\n🌐 Opening browser...", Colors.CYAN)
        webbrowser.open('http://localhost:3000')
        
        # Success message
        print("\n" + "="*50)
        print_colored("    ✅ APPLICATION LAUNCHED! ✅", Colors.GREEN + Colors.BOLD)
        print("="*50)
        print_colored("\n📱 App URL: http://localhost:3000", Colors.CYAN)
        print_colored("🔧 Backend API: http://localhost:8000", Colors.CYAN)
        print_colored("\n⚠️  Two server windows are now running.", Colors.YELLOW)
        print_colored("   DO NOT CLOSE THEM until you're done using the app!", Colors.YELLOW)
        print_colored("\n💡 You can safely close THIS window.", Colors.BLUE)
        print_colored("   The app will keep running in the background.\n", Colors.BLUE)
        
        input("Press Enter to exit launcher...")
        return 0
        
    except KeyboardInterrupt:
        print_colored("\n\n⚠️  Launcher interrupted by user.", Colors.YELLOW)
        return 0
    except Exception as e:
        print_colored(f"\n❌ Error: {str(e)}", Colors.RED)
        print_colored("\nPlease check that:", Colors.YELLOW)
        print_colored("  1. Python is installed and in PATH", Colors.YELLOW)
        print_colored("  2. Node.js is installed and in PATH", Colors.YELLOW)
        print_colored("  3. Backend dependencies are installed (pip install -r requirements.txt)", Colors.YELLOW)
        print_colored("  4. Frontend dependencies are installed (npm install)", Colors.YELLOW)
        input("\nPress Enter to exit...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
