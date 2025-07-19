#!/usr/bin/env python3
"""
Simple startup script for the Twiga Scan backend
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting Twiga Scan Backend...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("❤️  Health Check: http://localhost:8000/health")
    print("🔍 Scan Endpoint: POST http://localhost:8000/api/scan")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 