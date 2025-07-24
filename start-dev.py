#!/usr/bin/env python3
"""
Start both frontend and backend development servers simultaneously
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python
    try:
        import uvicorn
        print("✅ Python backend dependencies available")
    except ImportError:
        print("❌ Backend dependencies missing. Run: pip install -r backend/requirements.txt")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js available: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found. Install from https://nodejs.org/")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Install from https://nodejs.org/")
        return False
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm available: {result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not found")
        return False
    
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting backend server...")
    backend_dir = Path(__file__).parent / "backend"
    
    if sys.platform == "win32":
        python_path = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
    else:
        python_path = Path(__file__).parent / ".venv" / "bin" / "python"
    
    cmd = [str(python_path), "main.py"]
    return subprocess.Popen(cmd, cwd=backend_dir)

def start_frontend():
    """Start the React frontend server"""
    print("⚛️ Starting frontend server...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    # First check if node_modules exists, if not run npm install
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        install_result = subprocess.run(["npm", "install"], cwd=frontend_dir)
        if install_result.returncode != 0:
            print("❌ Failed to install frontend dependencies")
            return None
    
    cmd = ["npm", "start"]
    return subprocess.Popen(cmd, cwd=frontend_dir)

def main():
    """Main function to start both servers"""
    print("🦒 Twiga Scan - Starting Development Environment")
    print("=" * 50)
    
    if not check_requirements():
        print("\n❌ Requirements not met. Please install missing dependencies.")
        sys.exit(1)
    
    print("\n🚀 Starting servers...")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend")
        sys.exit(1)
    
    # Give backend a moment to start
    time.sleep(2)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend")
        backend_process.terminate()
        sys.exit(1)
    
    print("\n🎉 Both servers starting!")
    print("📍 Backend:  http://localhost:8000")
    print("📍 Frontend: http://localhost:3000")
    print("📍 API Docs: http://localhost:8000/docs")
    print("\n💡 Press Ctrl+C to stop both servers")
    
    try:
        # Wait for both processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        
    finally:
        # Clean shutdown
        if backend_process.poll() is None:
            backend_process.terminate()
            print("✅ Backend stopped")
        
        if frontend_process and frontend_process.poll() is None:
            frontend_process.terminate()
            print("✅ Frontend stopped")
        
        print("🎯 Development environment stopped")

if __name__ == "__main__":
    main()
