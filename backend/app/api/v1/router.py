"""
Tender Platform - API Router v1
Central router that includes all API endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.routes import auth, users, tenders, documents, health


# ============================================================================
# API V1 ROUTER
# ============================================================================
api_router = APIRouter()


# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(tenders.router, prefix="/tenders", tags=["Tenders"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])


# ============================================================================
# API VERSION INFO
# ============================================================================
@api_router.get("", tags=["Root"])
@api_router.get("/", tags=["Root"])
async def api_root() -> dict:
    """API v1 root endpoint."""
    return {
        "version": "v1",
        "status": "operational",
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "tenders": "/api/v1/tenders",
            "documents": "/api/v1/documents",
            "health": "/api/v1/health",
        },
    }
