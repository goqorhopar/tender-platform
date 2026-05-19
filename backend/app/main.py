"""
Tender Platform - Main Application Entry Point
Production-grade FastAPI application with middleware, error handling, and lifecycle management.
"""

import contextvars
from datetime import datetime
from typing import AsyncGenerator
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from prometheus_fastapi_instrumentator import Instrumentator
import uuid

from app.core.config import settings
from app.core.logging_config import get_logger, setup_logging, set_correlation_id
from app.db.database import close_db_connections, init_db
from app.api.v1.router import api_router


# ============================================================================
# APPLICATION FACTORY
# ============================================================================
def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)
    
    # Create application
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Enterprise-grade Tender Platform API for automated tender search, analysis, and participation",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
    )
    
    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    
    # Add correlation ID middleware
    @application.middleware("http")
    async def correlation_id_middleware(request: Request, call_next) -> Response:
        """Add correlation ID to each request for tracing."""
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        contextvars.copy_context().run(lambda: setattr(contextvars, "correlation_id", correlation_id))
        
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
    
    # Add request logging middleware
    @application.middleware("http")
    async def request_logging_middleware(request: Request, call_next) -> Response:
        """Log all incoming requests."""
        logger = get_logger("request")
        start_time = datetime.utcnow()
        
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": request.client.host if request.client else "unknown",
            }
        )
        
        response = await call_next(request)
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"Request completed: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            }
        )
        
        return response
    
    # Setup rate limiter
    rate_limiter = Limiter(key_func=get_remote_address)
    application.state.limiter = rate_limiter
    application.add_exception_handler(429, _rate_limit_exceeded_handler)
    
    # Setup Prometheus metrics
    if settings.PROMETHEUS_ENABLED:
        Instrumentator().instrument(application).expose(
            application,
            endpoint="/metrics",
            tags=["Monitoring"],
        )
    
    # Include routers
    application.include_router(api_router, prefix=settings.API_V1_PREFIX if hasattr(settings, 'API_V1_PREFIX') else "/api/v1")
    
    # Register event handlers
    register_event_handlers(application)
    
    logger.info(f"Application {settings.APP_NAME} v{settings.APP_VERSION} created successfully")
    
    return application


# ============================================================================
# EVENT HANDLERS
# ============================================================================
def register_event_handlers(application: FastAPI) -> None:
    """Register startup and shutdown event handlers."""
    logger = get_logger(__name__)
    
    @application.on_event("startup")
    async def startup_event() -> None:
        """Handle application startup."""
        logger.info("Application startup initiated")
        
        try:
            # Initialize database
            init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
        
        logger.info("Application startup completed")
    
    @application.on_event("shutdown")
    async def shutdown_event() -> None:
        """Handle application shutdown."""
        logger.info("Application shutdown initiated")
        
        try:
            # Close database connections
            await close_db_connections()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
        
        logger.info("Application shutdown completed")


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================
def register_exception_handlers(application: FastAPI) -> None:
    """Register global exception handlers."""
    logger = get_logger("exceptions")
    
    @application.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unhandled exceptions."""
        correlation_id = request.headers.get("X-Correlation-ID", "N/A")
        
        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={
                "correlation_id": correlation_id,
                "path": request.url.path,
                "method": request.method,
            },
            exc_info=True,
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred" if not settings.DEBUG else str(exc),
                "correlation_id": correlation_id,
            },
        )
    
    @application.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Handle validation errors."""
        return JSONResponse(
            status_code=400,
            content={
                "error": "Validation error",
                "detail": str(exc),
            },
        )


# ============================================================================
# CREATE APP INSTANCE
# ============================================================================
app = create_application()
register_exception_handlers(app)


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Basic health check endpoint.
    Returns service status.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health/ready", tags=["Health"])
async def readiness_check() -> dict:
    """
    Readiness check endpoint.
    Verifies all dependencies are available.
    """
    from app.db.database import sync_engine
    from sqlalchemy import text
    
    checks = {
        "database": False,
        "redis": False,
    }
    
    logger = get_logger("health")
    
    # Check database
    try:
        with sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis
    try:
        import redis
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
        )
        r.ping()
        checks["redis"] = True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
    
    all_healthy = all(checks.values())
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health/live", tags=["Health"])
async def liveness_check() -> dict:
    """
    Liveness check endpoint.
    Simple check to verify the service is running.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============================================================================
# ROOT ENDPOINT
# ============================================================================
@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Enterprise-grade Tender Platform API",
        "docs": "/docs" if settings.DEBUG else "Disabled in production",
        "health": "/health",
    }
