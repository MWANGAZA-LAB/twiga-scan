# 🚀 Quick Start Guide

## Starting Development Environment

### 📋 Prerequisites
- **Python 3.11+** (already set up ✅)
- **Node.js 18+** (install from [nodejs.org](https://nodejs.org/))

### 🎮 Start Both Servers

Choose your preferred method:

#### Method 1: Python Script (Recommended)
```bash
# Windows PowerShell
python start-dev.py

# Command Prompt / Git Bash
python start-dev.py
```

#### Method 2: Windows Batch File
```bash
start-dev.bat
```

#### Method 3: Manual (Two Terminals)
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend  
cd frontend
npm install    # first time only
npm start
```

### 🌐 Access Your App
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 🛑 Stopping Servers
- Python script: Press `Ctrl+C`
- Batch file: Close the terminal windows
- Manual: Press `Ctrl+C` in each terminal

### 💡 PowerShell Tips
- Use `;` instead of `&&` for command chaining: `cd backend; python main.py`
- Or use separate commands on different lines

---

*Backend is 100% ready! Frontend just needs Node.js installation.* ✅
