"""API v1 router and endpoints."""

from fastapi import APIRouter

from app.api.v1.routes import auth, users, tenders, suppliers, health

api_v1_router = APIRouter()

# Include route modules
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(users.router, prefix="/users", tags=["Users"])
api_v1_router.include_router(tenders.router, prefix="/tenders", tags=["Tenders"])
api_v1_router.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
api_v1_router.include_router(health.router, tags=["Health"])


@api_v1_router.get("", summary="API v1 Info")
async def api_info():
    """API v1 information endpoint."""
    return {
        "version": "v1",
        "status": "active",
        "endpoints": [
            "/auth",
            "/users",
            "/tenders",
            "/suppliers",
            "/health",
        ],
    }
