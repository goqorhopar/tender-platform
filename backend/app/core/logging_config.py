"""
Tender Platform - Logging Module
Production-grade structured logging with JSON format, correlation IDs, and log rotation.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from pythonjsonlogger import jsonlogger
import structlog
from structlog.types import Processor

from app.core.config import settings


# ============================================================================
# CONFIGURE PYTHON LOGGING
# ============================================================================
def setup_logging() -> None:
    """
    Configure application logging with JSON format and proper handlers.
    """
    # Ensure log directory exists
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Log format
    if settings.LOG_FORMAT == "json":
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S%z'
        )
    else:
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # File handler with rotation
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Error file handler
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.WARNING)


# ============================================================================
# CONFIGURE STRUCTLOG
# ============================================================================
def setup_structlog() -> None:
    """
    Configure structlog for structured logging with context.
    """
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if settings.LOG_FORMAT == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.LOG_LEVEL)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


# ============================================================================
# CORRELATION ID
# ============================================================================
import contextvars as ctx_vars

_correlation_id_var: ctx_vars.ContextVar[str] = ctx_vars.ContextVar("correlation_id", default="N/A")


class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = _correlation_id_var.get()
        return True


def get_correlation_id() -> str:
    """Get current correlation ID."""
    return _correlation_id_var.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for the current context."""
    _correlation_id_var.set(correlation_id)


# LOGGER FACTORY
# ============================================================================
def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.addFilter(CorrelationIdFilter())
    return logger


def get_structlog_logger(name: str) -> Any:
    """
    Get a structlog logger instance.
    
    Args:
        name: Logger name
    
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# ============================================================================
# LOG DECORATORS
# ============================================================================
def log_function_call(logger_name: str = "app"):
    """
    Decorator to log function calls with arguments and execution time.
    
    Usage:
        @log_function_call("my_module")
        def my_function(arg1, arg2):
            ...
    """
    def decorator(func):
        import functools
        import time
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            start_time = time.time()
            logger.info(
                f"Function call started: {func.__name__}",
                extra={"function": func.__name__, "args": args[:3], "kwargs": {k: v for k, v in list(kwargs.items())[:5]}}
            )
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(
                    f"Function call completed: {func.__name__}",
                    extra={"function": func.__name__, "duration_ms": round(duration * 1000, 2)}
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Function call failed: {func.__name__}",
                    extra={"function": func.__name__, "duration_ms": round(duration * 1000, 2), "error": str(e)}
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            start_time = time.time()
            logger.info(
                f"Function call started: {func.__name__}",
                extra={"function": func.__name__, "args": args[:3], "kwargs": {k: v for k, v in list(kwargs.items())[:5]}}
            )
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(
                    f"Function call completed: {func.__name__}",
                    extra={"function": func.__name__, "duration_ms": round(duration * 1000, 2)}
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Function call failed: {func.__name__}",
                    extra={"function": func.__name__, "duration_ms": round(duration * 1000, 2), "error": str(e)}
                )
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# ============================================================================
# AUDIT LOGGING
# ============================================================================
def log_audit_event(
    action: str,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> None:
    """
    Log an audit event for compliance and security tracking.
    
    Args:
        action: The action performed
        user_id: ID of the user who performed the action
        resource_type: Type of resource affected
        resource_id: ID of the resource affected
        details: Additional details about the action
        ip_address: IP address of the requester
    """
    logger = get_logger("audit")
    logger.info(
        f"Audit event: {action}",
        extra={
            "audit": True,
            "action": action,
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details,
            "ip_address": ip_address,
            "correlation_id": get_correlation_id()
        }
    )


# Initialize logging on module import
setup_logging()
setup_structlog()
