"""
Production logging module for the project.
"""

import logging
import os
import sys
import time
from contextlib import contextmanager
from functools import wraps
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Callable, Dict, Generator, TypeVar, ParamSpec

from pythonjsonlogger.json import JsonFormatter

T = TypeVar("T")
P = ParamSpec("P")


class CustomJsonFormatter(JsonFormatter):
    """
    Custom JSON formatter for structured logging.
    """

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """
        Add custom fields to the log record.
        """
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = self.formatTime(record)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name


class LogManager:
    """
    Manager class for handling logging configuration and operations.
    """

    def __init__(
        self,
        app_name: str,
        log_level: str = "INFO",
        log_dir: str = "logs",
        max_bytes: int = 10485760,  # 10MB
        backup_count: int = 5,
        json_output: bool = True,
    ) -> None:
        """
        Initialize the LogManager.

        Args:
            app_name: Name of the application
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory to store log files
            max_bytes: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
            json_output: Whether to use JSON formatting for logs
        """
        self.app_name = app_name
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = Path(log_dir)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.json_output = json_output

        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Configure logging
        self._configure_logging()

    def _configure_logging(self) -> None:
        """
        Configure the logging system.
        """
        # Create logger
        logger = logging.getLogger(self.app_name)
        logger.setLevel(self.log_level)

        # Remove existing handlers
        logger.handlers = []

        # Create formatters
        formatter = None
        if self.json_output:
            formatter = CustomJsonFormatter(
                "%(timestamp)s %(level)s %(name)s %(message)s %(extra)s"
            )
        else:
            formatter = CustomJsonFormatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        file_handler = RotatingFileHandler(
            self.log_dir / f"{self.app_name}.log",
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        """
        Get the configured logger.

        Returns:
            logging.Logger: Configured logger instance
        """
        return logging.getLogger(self.app_name)

    @contextmanager
    def log_context(
        self, operation: str, **context: Any
    ) -> Generator[logging.Logger, None, None]:
        """
        Context manager for logging operations with context.

        Args:
            operation: Name of the operation
            **context: Additional context variables

        Yields:
            logging.Logger: Logger instance with context
        """
        logger = self.get_logger()
        context["operation"] = operation
        context["timestamp"] = time.time()

        try:
            yield logger
        finally:
            context["duration"] = time.time() - context["timestamp"]
            logger.info(
                f"Operation {operation} completed",
                extra={"context": context},
            )

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
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            logger.info(
                f"Function {func.__name__} executed",
                extra={
                    "function": func.__name__,
                    "duration": duration,
                    "func_args": str(args),
                    "func_kwargs": str(kwargs),
                },
            )

            return result

        return wrapper

    def log_exceptions(self, func: Callable[P, T]) -> Callable[P, T]:
        """
        Decorator to log exceptions.

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
                    extra={
                        "function": func.__name__,
                        "exception": str(e),
                        "func_args": str(args),
                        "func_kwargs": str(kwargs),
                    },
                )
                raise

        return wrapper


# Create default logger instance
log_manager = LogManager(
    app_name=os.getenv("APP_NAME", "uv_boilerplate"),
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_dir=os.getenv("LOG_DIR", "logs"),
)

# Export logger instance
logger = log_manager.get_logger()
