"""
Production-ready structured logging configuration.

This module provides a comprehensive logging solution for production environments with
support for structured logging, request tracking, performance monitoring, and security
best practices.
"""

import logging
import os
import sys
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from logging.handlers import RotatingFileHandler, SysLogHandler
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Optional,
    TypeVar,
    ParamSpec,
    Union,
)

import structlog
from structlog.types import Processor

T = TypeVar("T")
P = ParamSpec("P")

# Global context variables for request tracking
REQUEST_ID: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
USER_ID: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
SESSION_ID: ContextVar[Optional[str]] = ContextVar("session_id", default=None)


class LogConfig:
    """
    Configuration class for logging settings.
    """

    def __init__(self) -> None:
        """
        Initialize logging configuration from environment variables.
        """
        self.app_name = os.getenv("APP_NAME", "uv_boilerplate")
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_format = os.getenv("LOG_FORMAT", "json").lower()
        self.log_dir = os.getenv("LOG_DIR", "logs")
        self.max_bytes = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
        self.backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))
        self.enable_console = os.getenv("LOG_ENABLE_CONSOLE", "true").lower() == "true"
        self.enable_file = os.getenv("LOG_ENABLE_FILE", "true").lower() == "true"
        self.enable_syslog = os.getenv("LOG_ENABLE_SYSLOG", "false").lower() == "true"
        self.syslog_address = os.getenv("LOG_SYSLOG_ADDRESS", "/dev/log")
        self.enable_structured = (
            os.getenv("LOG_ENABLE_STRUCTURED", "true").lower() == "true"
        )
        self.enable_colors = os.getenv("LOG_ENABLE_COLORS", "false").lower() == "true"
        self.enable_request_tracking = (
            os.getenv("LOG_ENABLE_REQUEST_TRACKING", "true").lower() == "true"
        )
        self.enable_performance_logging = (
            os.getenv("LOG_ENABLE_PERFORMANCE", "true").lower() == "true"
        )
        self.sensitive_fields = set(
            os.getenv("LOG_SENSITIVE_FIELDS", "password,token,secret,key").split(",")
        )


class SensitiveDataFilter:
    """
    Filter to remove sensitive data from log entries.
    """

    def __init__(self, sensitive_fields: set[str]) -> None:
        """
        Initialize with sensitive field names.
        """
        self.sensitive_fields = sensitive_fields

    def __call__(
        self, logger: Any, method_name: str, event_dict: Dict[str, Any]
    ) -> Union[Dict[str, Any], str, bytes, bytearray, tuple[Any, ...]]:
        """
        Filter sensitive data from log entries.
        """
        self._filter_sensitive_data(event_dict)
        return event_dict

    def _filter_sensitive_data(self, data: Any) -> None:
        """
        Recursively filter sensitive data from nested structures.
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if key in self.sensitive_fields:
                    data[key] = "[REDACTED]"
                elif isinstance(value, (dict, list)):
                    self._filter_sensitive_data(value)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._filter_sensitive_data(item)


class RequestContextProcessor:
    """
    Processor to add request context to log entries.
    """

    def __call__(
        self, logger: Any, method_name: str, event_dict: Dict[str, Any]
    ) -> Union[Dict[str, Any], str, bytes, bytearray, tuple[Any, ...]]:
        """
        Add request context to log entries.
        """
        if REQUEST_ID.get():
            event_dict["request_id"] = REQUEST_ID.get()
        if USER_ID.get():
            event_dict["user_id"] = USER_ID.get()
        if SESSION_ID.get():
            event_dict["session_id"] = SESSION_ID.get()
        return event_dict


class PerformanceProcessor:
    """
    Processor to add performance metrics to log entries.
    """

    def __call__(
        self, logger: Any, method_name: str, event_dict: Dict[str, Any]
    ) -> Union[Dict[str, Any], str, bytes, bytearray, tuple[Any, ...]]:
        """
        Add performance metrics to log entries.
        """
        event_dict["timestamp"] = time.time()
        event_dict["timestamp_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return event_dict


class LogManager:
    """
    Production-ready logging manager with structured logging support.
    """

    def __init__(self, config: Optional[LogConfig] = None) -> None:
        """
        Initialize the LogManager.

        Args:
            config: Logging configuration object
        """
        self.config = config or LogConfig()
        self._configure_logging()

    def _configure_logging(self) -> None:
        """
        Configure the logging system with structlog.
        """
        # Create log directory if file logging is enabled
        if self.config.enable_file:
            log_dir = Path(self.config.log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)

        # Build processors list
        processors: list[Processor] = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            PerformanceProcessor(),  # type: ignore
        ]

        # Add request context if enabled
        if self.config.enable_request_tracking:
            processors.append(RequestContextProcessor())  # type: ignore

        # Add sensitive data filter
        processors.append(SensitiveDataFilter(self.config.sensitive_fields))  # type: ignore

        # Add timestamp processor
        processors.append(structlog.processors.TimeStamper(fmt="iso"))

        # Add stack info for errors
        processors.append(structlog.processors.StackInfoRenderer())

        # Add exception info for errors
        processors.append(structlog.processors.format_exc_info)

        # Add output format
        if self.config.log_format == "json":
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(
                structlog.dev.ConsoleRenderer(colors=self.config.enable_colors)
            )

        # Configure structlog
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, self.config.log_level)
            ),
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Configure standard library logging
        self._configure_standard_logging()

    def _configure_standard_logging(self) -> None:
        """
        Configure standard library logging handlers.
        """
        logger = logging.getLogger(self.config.app_name)
        logger.setLevel(getattr(logging, self.config.log_level))

        # Remove existing handlers
        logger.handlers.clear()

        # File handler
        if self.config.enable_file:
            file_handler = RotatingFileHandler(
                Path(self.config.log_dir) / f"{self.config.app_name}.log",
                maxBytes=self.config.max_bytes,
                backupCount=self.config.backup_count,
            )
            file_handler.setLevel(getattr(logging, self.config.log_level))
            logger.addHandler(file_handler)

        # Console handler
        if self.config.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.config.log_level))
            logger.addHandler(console_handler)

        # Syslog handler
        if self.config.enable_syslog:
            try:
                syslog_handler = SysLogHandler(address=self.config.syslog_address)
                syslog_handler.setLevel(getattr(logging, self.config.log_level))
                logger.addHandler(syslog_handler)
            except Exception as e:
                # Log the error but don't fail if syslog is not available
                print(
                    f"Warning: Could not configure syslog handler: {e}", file=sys.stderr
                )

        # Configure root logger to use the same handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(getattr(logging, self.config.log_level))

        # Add the same handlers to root logger
        for handler in logger.handlers:
            root_logger.addHandler(handler)

    def get_logger(self, name: Optional[str] = None) -> structlog.BoundLogger:
        """
        Get a structured logger instance.

        Args:
            name: Logger name (defaults to app name)

        Returns:
            structlog.BoundLogger: Configured logger instance
        """
        return structlog.get_logger(name or self.config.app_name)  # type: ignore

    @contextmanager
    def log_context(
        self, operation: str, **context: Any
    ) -> Generator[structlog.BoundLogger, None, None]:
        """
        Context manager for logging operations with context.

        Args:
            operation: Name of the operation
            **context: Additional context variables

        Yields:
            structlog.BoundLogger: Logger instance with context
        """
        logger = self.get_logger()
        start_time = time.time()

        # Add operation context
        context["operation"] = operation
        context["start_time"] = start_time

        try:
            yield logger
        except Exception as e:
            duration = time.time() - start_time
            # Create a new context dict to avoid duplicate keys
            error_context = context.copy()
            error_context.update(
                {
                    "operation": operation,
                    "duration": duration,
                    "error": str(e),
                }
            )
            logger.error(f"Operation {operation} failed", **error_context)
            raise
        else:
            duration = time.time() - start_time
            # Create a new context dict to avoid duplicate keys
            success_context = context.copy()
            success_context.update(
                {
                    "operation": operation,
                    "duration": duration,
                }
            )
            logger.info(f"Operation {operation} completed", **success_context)

    def log_execution_time(self, func: Callable[P, T]) -> Callable[P, T]:
        """
        Decorator to log function execution time.

        Args:
            func: Function to decorate

        Returns:
            Callable[P, T]: Decorated function
        """

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            logger = self.get_logger()
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                logger.info(
                    f"Function {func.__name__} executed successfully",
                    function=func.__name__,
                    duration=duration,
                    module=func.__module__,
                )

                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Function {func.__name__} failed",
                    function=func.__name__,
                    duration=duration,
                    error=str(e),
                    module=func.__module__,
                )
                raise

        # The wrapper function preserves the original function's type signature
        # This is the correct way to handle type-safe decorators
        return wrapper

    def log_exceptions(self, func: Callable[P, T]) -> Callable[P, T]:
        """
        Decorator to log exceptions with full context.

        Args:
            func: Function to decorate

        Returns:
            Callable[P, T]: Decorated function
        """

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            logger = self.get_logger()

            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(
                    f"Exception in {func.__name__}",
                    function=func.__name__,
                    module=func.__module__,
                    exception_type=type(e).__name__,
                    exception_message=str(e),
                )
                raise

        # Type-safe return - the wrapper preserves the original function's signature
        return wrapper


# Request tracking utilities
def set_request_id(request_id: Optional[str] = None) -> str:
    """
    Set request ID for current context.

    Args:
        request_id: Request ID to set (generates UUID if None)

    Returns:
        str: The request ID
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    REQUEST_ID.set(request_id)
    return request_id


def get_request_id() -> Optional[str]:
    """
    Get current request ID.

    Returns:
        Optional[str]: Current request ID
    """
    return REQUEST_ID.get()


def set_user_id(user_id: str) -> None:
    """
    Set user ID for current context.

    Args:
        user_id: User ID to set
    """
    USER_ID.set(user_id)


def set_session_id(session_id: str) -> None:
    """
    Set session ID for current context.

    Args:
        session_id: Session ID to set
    """
    SESSION_ID.set(session_id)


def clear_context() -> None:
    """
    Clear all context variables.
    """
    REQUEST_ID.set(None)
    USER_ID.set(None)
    SESSION_ID.set(None)


# Create default logger instance
log_manager = LogManager()

# Export logger instance and utilities
logger = log_manager.get_logger()

__all__ = [
    "LogManager",
    "LogConfig",
    "logger",
    "set_request_id",
    "get_request_id",
    "set_user_id",
    "set_session_id",
    "clear_context",
]
