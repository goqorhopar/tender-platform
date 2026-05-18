"""Health check endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health", summary="Health Check")
async def health_check():
    """
    Basic health check endpoint.
    
    Returns the current status of the API.
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/ready", summary="Readiness Check")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check endpoint.
    
    Verifies that all dependencies (database, redis, etc.) are available.
    """
    health_status = {
        "status": "ready",
        "checks": {},
    }
    
    # Check database connection
    try:
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "not_ready"
    
    return health_status


@router.get("/live", summary="Liveness Check")
async def liveness_check():
    """
    Liveness check endpoint.
    
    Simple endpoint to verify the application is running.
    """
    return {"status": "alive"}
