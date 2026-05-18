"""API v1 routes package."""

from app.api.v1.routes import auth, users, tenders, suppliers, health

__all__ = ["auth", "users", "tenders", "suppliers", "health"]
