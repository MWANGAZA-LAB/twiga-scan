from fastapi import APIRouter
import time

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "twiga-scan-api"
    } 