import time
from datetime import datetime
from typing import Any, Dict

import psutil
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config import settings
from models.database import get_db

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with database connectivity"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {"database": db_status, "api": "healthy"},
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "uptime": time.time() - psutil.boot_time(),
        },
    }


@router.get("/metrics")
async def get_metrics():
    """System metrics endpoint (Prometheus compatible)"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    metrics = {
        "twiga_scan_cpu_usage_percent": cpu_percent,
        "twiga_scan_memory_usage_percent": memory.percent,
        "twiga_scan_disk_usage_percent": disk.percent,
        "twiga_scan_memory_available_bytes": memory.available,
        "twiga_scan_disk_free_bytes": disk.free,
        "twiga_scan_uptime_seconds": time.time() - psutil.boot_time(),
    }

    # Format as Prometheus metrics
    prometheus_metrics = []
    for metric_name, value in metrics.items():
        prometheus_metrics.append(f"{metric_name} {value}")

    return "\n".join(prometheus_metrics)


@router.get("/status")
async def system_status():
    """Comprehensive system status"""
    return {
        "application": {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
        },
        "system": {
            "platform": psutil.sys.platform,
            "python_version": (
                f"{psutil.sys.version_info.major}."
                f"{psutil.sys.version_info.minor}."
                f"{psutil.sys.version_info.micro}"
            ),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/info")
async def application_info():
    """Application information and configuration"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "Bitcoin and Lightning Network QR/URL Authentication Platform",
        "features": [
            "QR Code Scanning",
            "Bitcoin URI Parsing",
            "Lightning Network Support",
            "Provider Verification",
            "Scan History",
            "Real-time Bitcoin Price",
        ],
        "api_endpoints": {
            "scan": "/api/scan",
            "providers": "/api/providers",
            "health": "/monitoring/health",
            "docs": "/docs",
        },
        "configuration": {
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE,
            "rate_limit_per_hour": settings.RATE_LIMIT_PER_HOUR,
            "max_file_size": settings.MAX_FILE_SIZE,
            "allowed_file_types": settings.ALLOWED_FILE_TYPES,
        },
    }
