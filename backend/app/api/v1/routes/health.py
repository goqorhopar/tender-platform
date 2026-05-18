"""
Tender Platform - Health Check Routes
Health, readiness, and liveness check endpoints.
"""

from datetime import datetime
from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import redis

from app.db.database import get_db, sync_engine
from app.core.config import settings
from app.core.logging_config import get_logger


router = APIRouter()
logger = get_logger(__name__)


@router.get("")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.
    Checks database and Redis connectivity.
    """
    checks: Dict[str, Any] = {
        "database": {"status": "unknown", "latency_ms": None},
        "redis": {"status": "unknown", "latency_ms": None},
    }
    
    overall_status = "healthy"
    
    # Check database
    try:
        start = datetime.utcnow()
        with sync_engine.connect() as conn:
            conn.execute("SELECT 1")
        latency = (datetime.utcnow() - start).total_seconds() * 1000
        checks["database"] = {"status": "healthy", "latency_ms": round(latency, 2)}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "unhealthy"
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis
    try:
        start = datetime.utcnow()
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            socket_timeout=5,
        )
        r.ping()
        latency = (datetime.utcnow() - start).total_seconds() * 1000
        checks["redis"] = {"status": "healthy", "latency_ms": round(latency, 2)}
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "degraded" if overall_status == "healthy" else overall_status
        logger.error(f"Redis health check failed: {e}")
    
    return {
        "status": overall_status,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Readiness check - verifies all dependencies are available.
    Used by Kubernetes readiness probes.
    """
    is_ready = True
    checks: Dict[str, bool] = {}
    
    # Check database
    try:
        with sync_engine.connect() as conn:
            conn.execute("SELECT 1")
        checks["database"] = True
    except Exception:
        checks["database"] = False
        is_ready = False
    
    # Check Redis
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            socket_timeout=5,
        )
        r.ping()
        checks["redis"] = True
    except Exception:
        checks["redis"] = False
        is_ready = False
    
    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "ready": is_ready,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check - simple check to verify the service is running.
    Used by Kubernetes liveness probes.
    """
    return {
        "alive": True,
        "service": settings.APP_NAME,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/metrics/summary")
async def metrics_summary() -> Dict[str, Any]:
    """
    Summary of application metrics.
    """
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime": "N/A",  # Would be calculated from startup time
        "timestamp": datetime.utcnow().isoformat(),
    }
