@echo off
echo 🦒 Twiga Scan - Starting Development Environment
echo ==================================================

echo.
echo 🔍 Checking requirements...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install from https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js is available

REM Check if Python virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Python virtual environment not found
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

echo ✅ Python virtual environment found

echo.
echo 🚀 Starting servers...

REM Start backend in new window
echo 🐍 Starting backend server...
start "Twiga Backend" cmd /k "cd /d %~dp0backend && %~dp0.venv\Scripts\python.exe main.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo ⚛️ Starting frontend server...
cd frontend
if not exist "node_modules" (
    echo 📦 Installing frontend dependencies...
    npm install
)
start "Twiga Frontend" cmd /k "npm start"

echo.
echo 🎉 Both servers are starting!
echo 📍 Backend:  http://localhost:8000
echo 📍 Frontend: http://localhost:3000  
echo 📍 API Docs: http://localhost:8000/docs
echo.
echo 💡 Each server runs in its own window
echo 💡 Close the windows to stop the servers
echo.
pause
