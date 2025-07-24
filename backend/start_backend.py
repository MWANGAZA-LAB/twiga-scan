#!/usr/bin/env python3
"""
Backend startup wrapper that handles import paths correctly
"""
import sys
import os
from pathlib import Path

# Add the current directory (backend) to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Now import and run the backend
if __name__ == "__main__":
    # Import and run the main app
    import main
    import uvicorn
    
    print("🚀 Starting Twiga Scan Backend...")
    print("📍 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        main.app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to avoid issues
        log_level="info"
    )
