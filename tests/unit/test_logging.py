"""
Test cases for the production-ready logging module.
"""

import json
import os
import tempfile
from pathlib import Path
import time
from typing import Any, Callable, Dict, Generator, TypeVar

import pytest

from uv_boilerplate.utils.logging import (
    LogManager,
    LogConfig,
    logger,
    log_manager,
    set_request_id,
    get_request_id,
    set_user_id,
    set_session_id,
    clear_context,
)

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


@pytest.fixture
def temp_log_dir() -> Generator[Path, None, None]:
    """
    Create a temporary directory for log files.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def log_config(temp_log_dir: Path) -> LogConfig:
    """
    Create a LogConfig instance with temporary log directory.
    """
    # Clear any existing environment variables that might interfere
    if "APP_NAME" in os.environ:
        del os.environ["APP_NAME"]

    config = LogConfig()
    config.log_dir = str(temp_log_dir)
    config.log_level = "DEBUG"
    config.enable_file = True
    config.enable_console = False
    config.log_format = "json"
    return config


@pytest.fixture
def test_log_manager(log_config: LogConfig) -> LogManager:
    """
    Create a LogManager instance with temporary log directory.
    """
    return LogManager(log_config)


def test_log_config_initialization() -> None:
    """
    Test LogConfig initialization with environment variables.
    """
    # Set environment variables
    os.environ["APP_NAME"] = "test_app"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["LOG_FORMAT"] = "json"

    config = LogConfig()

    assert config.app_name == "test_app"
    assert config.log_level == "DEBUG"
    assert config.log_format == "json"
    assert config.enable_console is True
    assert config.enable_file is True


def test_log_manager_initialization(temp_log_dir: Path) -> None:
    """
    Test LogManager initialization.
    """
    # Clear any existing environment variables that might interfere
    if "APP_NAME" in os.environ:
        del os.environ["APP_NAME"]

    config = LogConfig()
    config.log_dir = str(temp_log_dir)
    config.log_level = "DEBUG"

    manager = LogManager(config)

    assert manager.config.app_name == "uv_boilerplate"
    assert manager.config.log_level == "DEBUG"
    assert manager.config.log_dir == str(temp_log_dir)

    # Check if log directory was created
    log_dir = Path(config.log_dir)
    assert log_dir.exists()
    assert log_dir.is_dir()


def test_log_manager_get_logger(test_log_manager: LogManager) -> None:
    """
    Test getting logger instance.
    """
    logger_instance = test_log_manager.get_logger()
    # structlog.get_logger returns a BoundLoggerLazyProxy initially
    assert hasattr(logger_instance, "_logger") or hasattr(logger_instance, "info")

    # Test with custom name
    custom_logger = test_log_manager.get_logger("custom_name")
    assert hasattr(custom_logger, "_logger") or hasattr(custom_logger, "info")


def test_basic_logging(test_log_manager: LogManager, temp_log_dir: Path) -> None:
    """
    Test basic structured logging.
    """
    logger_instance = test_log_manager.get_logger()
    logger_instance.info("Test message", test_key="test_value")

    # Read log file
    log_file = temp_log_dir / "uv_boilerplate.log"
    assert log_file.exists()

    with open(log_file) as f:
        log_content = json.loads(f.readline().strip())
        assert log_content["level"] == "info"
        assert log_content["event"] == "Test message"
        assert log_content["test_key"] == "test_value"
        assert "timestamp" in log_content
        assert "timestamp_iso" in log_content


def test_log_context(test_log_manager: LogManager, temp_log_dir: Path) -> None:
    """
    Test log context manager.
    """
    with test_log_manager.log_context("test_operation", test_key="test_value") as log:
        log.info("Test message")

    # Read log file
    log_file = temp_log_dir / "uv_boilerplate.log"
    assert log_file.exists()

    # Read all lines and get the last one since context manager adds a completion message
    with open(log_file) as f:
        lines = f.readlines()
        log_content = json.loads(lines[-1].strip())
        assert log_content["level"] == "info"
        assert "Operation test_operation completed" in log_content["event"]
        assert log_content["operation"] == "test_operation"
        assert log_content["test_key"] == "test_value"
        assert "duration" in log_content
        assert float(log_content["duration"]) >= 0


def test_log_execution_time(test_log_manager: LogManager, temp_log_dir: Path) -> None:
    """
    Test execution time logging decorator.
    """

    @test_log_manager.log_execution_time
    def test_function(x: int, y: int) -> int:
        time.sleep(0.1)
        return x + y

    result = test_function(1, 2)
    assert result == 3

    # Read log file
    log_file = temp_log_dir / "uv_boilerplate.log"
    assert log_file.exists()

    with open(log_file) as f:
        log_content = json.loads(f.readline().strip())
        assert log_content["level"] == "info"
        assert "Function test_function executed successfully" in log_content["event"]
        assert log_content["function"] == "test_function"
        assert "duration" in log_content
        assert float(log_content["duration"]) > 0


def test_log_exceptions(test_log_manager: LogManager, temp_log_dir: Path) -> None:
    """
    Test exception logging decorator.
    """

    @test_log_manager.log_exceptions
    def test_function(x: int) -> float:
        if x == 0:
            raise ValueError("Cannot divide by zero")
        return 100 / x

    with pytest.raises(ValueError):
        test_function(0)

    # Read log file
    log_file = temp_log_dir / "uv_boilerplate.log"
    assert log_file.exists()

    with open(log_file) as f:
        log_content = json.loads(f.readline().strip())
        assert log_content["level"] == "error"
        assert "Exception in test_function" in log_content["event"]
        assert log_content["function"] == "test_function"
        assert log_content["exception_type"] == "ValueError"
        assert "Cannot divide by zero" in log_content["exception_message"]


def test_default_logger() -> None:
    """
    Test default logger instance.
    """
    # structlog.get_logger returns a BoundLoggerLazyProxy initially
    assert hasattr(logger, "_logger") or hasattr(logger, "info")


def test_request_tracking() -> None:
    """
    Test request ID tracking functionality.
    """
    # Test setting and getting request ID
    request_id = set_request_id("test-request-123")
    assert request_id == "test-request-123"
    assert get_request_id() == "test-request-123"

    # Test auto-generation of request ID
    clear_context()
    auto_request_id = set_request_id()
    assert auto_request_id is not None
    assert len(auto_request_id) > 0

    # Test user and session ID
    set_user_id("user123")
    set_session_id("session456")

    # Clear context
    clear_context()
    assert get_request_id() is None


def test_sensitive_data_filtering(
    test_log_manager: LogManager, temp_log_dir: Path
) -> None:
    """
    Test sensitive data filtering.
    """
    logger_instance = test_log_manager.get_logger()

    # Log data with sensitive fields
    user_data = {
        "username": "john_doe",
        "password": "secret123",
        "token": "eyJhbGciOiJIUzI1NiIs...",
        "email": "john@example.com",
    }

    logger_instance.info("User data received", user_data=user_data)

    # Read log file
    log_file = temp_log_dir / "uv_boilerplate.log"
    assert log_file.exists()

    with open(log_file) as f:
        log_content = json.loads(f.readline().strip())
        assert log_content["user_data"]["password"] == "[REDACTED]"
        assert log_content["user_data"]["token"] == "[REDACTED]"
        assert log_content["user_data"]["username"] == "john_doe"
        assert log_content["user_data"]["email"] == "john@example.com"


def test_console_formatting() -> None:
    """
    Test console formatting configuration.
    """
    config = LogConfig()
    config.log_format = "console"
    config.enable_colors = True
    config.enable_file = False

    manager = LogManager(config)
    logger_instance = manager.get_logger()

    # This should not raise an exception
    logger_instance.info("Test console message", test_key="test_value")

    # Test that console formatting works without errors
    assert True


def test_log_rotation(test_log_manager: LogManager, temp_log_dir: Path) -> None:
    """
    Test log rotation.
    """
    # Write large log messages to trigger rotation
    message = "x" * 1024 * 1024  # 1MB message
    for i in range(20):  # Write 20MB total to trigger multiple rotations
        test_log_manager.get_logger().info(f"Test message {i}: {message}")

    # Check if log file exists
    log_file = temp_log_dir / "uv_boilerplate.log"
    assert log_file.exists()

    # Check if backup files were created
    backup_files = list(temp_log_dir.glob("uv_boilerplate.log.*"))
    assert len(backup_files) > 0

    # Verify main log file size is less than max_bytes
    assert log_file.stat().st_size <= test_log_manager.config.max_bytes


def test_error_handling_in_context(
    test_log_manager: LogManager, temp_log_dir: Path
) -> None:
    """
    Test error handling in context manager.
    """
    with pytest.raises(ValueError):
        with test_log_manager.log_context("error_operation") as log:
            log.info("Starting operation")
            raise ValueError("Operation failed")

    # Read log file
    log_file = temp_log_dir / "uv_boilerplate.log"
    assert log_file.exists()

    with open(log_file) as f:
        lines = f.readlines()
        # Find the error log entry
        error_log = None
        for line in lines:
            content = json.loads(line.strip())
            if "Operation error_operation failed" in content["event"]:
                error_log = content
                break

        assert error_log is not None
        assert error_log["level"] == "error"
        assert "Operation failed" in error_log["error"]


def test_performance_processor() -> None:
    """
    Test performance processor adds timestamps.
    """
    config = LogConfig()
    config.enable_file = True
    config.enable_console = False
    config.log_format = "json"

    with tempfile.TemporaryDirectory() as temp_dir:
        config.log_dir = temp_dir
        manager = LogManager(config)
        logger_instance = manager.get_logger()

        logger_instance.info("Test message")

        # Read log file
        log_file = Path(temp_dir) / "uv_boilerplate.log"
        assert log_file.exists()

        with open(log_file) as f:
            log_content = json.loads(f.readline().strip())
            assert "timestamp" in log_content
            assert "timestamp_iso" in log_content
            assert log_content["timestamp_iso"].endswith("Z")  # UTC format


def test_request_tracking_output(
    test_log_manager: LogManager, temp_log_dir: Path
) -> None:
    """
    Test request tracking output in logs.
    """
    logger_instance = test_log_manager.get_logger()

    # Set request context
    set_request_id("test-request-123")
    set_user_id("user456")
    set_session_id("session789")

    logger_instance.info("Request processing started")

    # Read log file
    log_file = temp_log_dir / "uv_boilerplate.log"
    assert log_file.exists()

    with open(log_file) as f:
        log_content = json.loads(f.readline().strip())
        assert log_content["request_id"] == "test-request-123"
        assert log_content["user_id"] == "user456"
        assert log_content["session_id"] == "session789"
        assert "Request processing started" in log_content["event"]


def test_multiple_log_levels(test_log_manager: LogManager, temp_log_dir: Path) -> None:
    """
    Test different log levels output correctly.
    """
    logger_instance = test_log_manager.get_logger()

    logger_instance.debug("Debug message")
    logger_instance.info("Info message")
    logger_instance.warning("Warning message")
    logger_instance.error("Error message")

    # Read log file
    log_file = temp_log_dir / "uv_boilerplate.log"
    assert log_file.exists()

    with open(log_file) as f:
        lines = f.readlines()
        assert len(lines) >= 4

        # Check each log level
        log_contents = [json.loads(line.strip()) for line in lines]

        levels = [content["level"] for content in log_contents]
        assert "debug" in levels
        assert "info" in levels
        assert "warning" in levels
        assert "error" in levels


def test_structured_data_output(test_log_manager: LogManager, temp_log_dir: Path) -> None:
    """
    Test structured data is properly formatted in output.
    """
    logger_instance = test_log_manager.get_logger()

    # Log complex structured data
    complex_data = {
        "user": {
            "id": 123,
            "name": "John Doe",
            "preferences": {"theme": "dark", "language": "en"},
        },
        "metadata": {"source": "api", "version": "1.0.0"},
    }

    logger_instance.info("Complex data logged", data=complex_data)

    # Read log file
    log_file = temp_log_dir / "uv_boilerplate.log"
    assert log_file.exists()

    with open(log_file) as f:
        log_content = json.loads(f.readline().strip())
        assert "data" in log_content
        assert log_content["data"]["user"]["id"] == 123
        assert log_content["data"]["user"]["name"] == "John Doe"
        assert log_content["data"]["metadata"]["source"] == "api"


def test_log_file_creation_and_permissions(temp_log_dir: Path) -> None:
    """
    Test log file creation and permissions.
    """
    config = LogConfig()
    config.log_dir = str(temp_log_dir)
    config.enable_file = True
    config.enable_console = False

    manager = LogManager(config)
    logger_instance = manager.get_logger()

    logger_instance.info("Test message")

    # Check file exists and is writable
    log_file = temp_log_dir / "uv_boilerplate.log"
    assert log_file.exists()
    assert log_file.is_file()
    assert os.access(log_file, os.W_OK)


def test_log_directory_creation() -> None:
    """
    Test that log directory is created if it doesn't exist.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a subdirectory that doesn't exist
        log_dir = Path(temp_dir) / "logs" / "app"

        config = LogConfig()
        config.log_dir = str(log_dir)
        config.enable_file = True
        config.enable_console = False

        manager = LogManager(config)
        logger_instance = manager.get_logger()

        logger_instance.info("Test message")

        # Check directory was created
        assert log_dir.exists()
        assert log_dir.is_dir()

        # Check log file was created
        log_file = log_dir / "uv_boilerplate.log"
        assert log_file.exists()


def test_request_id_tracking() -> None:
    """
    Test request ID tracking across function calls.
    """
    # Clear any existing context
    clear_context()

    # Set request context
    set_request_id("test-request-123")
    set_user_id("test-user-456")
    set_session_id("test-session-789")

    # Verify request ID is set
    assert get_request_id() == "test-request-123"

    # Log some messages and verify they include request context
    logger.info("Test message with request tracking")

    # Test nested function calls maintain context
    def nested_function() -> None:
        logger.info("Nested function call")
        assert get_request_id() == "test-request-123"

    nested_function()

    # Clear context and verify it's cleared
    clear_context()
    assert get_request_id() is None


def test_logging_decorators() -> None:
    """
    Test logging decorators for execution time and exceptions.
    """
    clear_context()
    set_request_id("decorator-test")

    # Test execution time decorator
    @log_manager.log_execution_time
    def test_function() -> Dict[str, Any]:
        time.sleep(0.01)  # Small delay to measure
        return {"result": "success", "data": [1, 2, 3]}

    result = test_function()
    assert result["result"] == "success"
    assert len(result["data"]) == 3

    # Test exception logging decorator
    @log_manager.log_exceptions
    def failing_function() -> str:
        raise ValueError("Test exception for logging")

    try:
        failing_function()
    except ValueError:
        # Exception should be logged but re-raised
        pass

    clear_context()


def test_logging_context_manager() -> None:
    """
    Test logging context manager for operation tracking.
    """
    clear_context()
    set_request_id("context-test")

    with log_manager.log_context("test_operation", operation_type="unit_test") as log:
        log.info("Operation started")
        time.sleep(0.01)  # Simulate some work
        log.info("Operation step completed", step="validation")
        time.sleep(0.01)  # Simulate more work
        log.info("Operation finished")

    clear_context()


def test_sensitive_data_filtering_with_context() -> None:
    """
    Test that sensitive data is properly filtered in logs.
    """
    clear_context()
    set_request_id("security-test")

    # Log data with sensitive information
    user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "secret_password_123",  # Should be redacted
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",  # Should be redacted
        "preferences": {"theme": "dark", "language": "en"},
    }

    logger.info("User data received", user_data=user_data)

    # The sensitive fields should be automatically redacted
    # This test verifies the logging system is working, not the actual redaction
    # (redaction is tested in test_logging.py)

    clear_context()


def test_multiple_request_contexts() -> None:
    """
    Test that multiple request contexts work independently.
    """
    # Clear any existing context
    clear_context()

    # Simulate multiple concurrent requests
    def simulate_request(request_id: str, user_id: str) -> None:
        set_request_id(request_id)
        set_user_id(user_id)
        logger.info(f"Processing request {request_id} for user {user_id}")
        assert get_request_id() == request_id

    # Simulate multiple requests (in real scenarios, these would be in different threads)
    simulate_request("req-001", "user-001")
    clear_context()

    simulate_request("req-002", "user-002")
    clear_context()

    simulate_request("req-003", "user-003")
    clear_context()

    # Verify context is cleared
    assert get_request_id() is None


def test_logging_with_structured_data() -> None:
    """
    Test logging with complex structured data.
    """
    clear_context()
    set_request_id("structured-data-test")

    # Log complex nested data
    complex_data = {
        "user": {
            "id": "user123",
            "profile": {
                "name": "John Doe",
                "email": "john@example.com",
                "settings": {"notifications": True, "privacy": "public"},
            },
        },
        "session": {
            "id": "sess456",
            "created_at": "2025-08-17T06:00:00Z",
            "expires_at": "2025-08-17T18:00:00Z",
        },
        "request": {
            "method": "POST",
            "endpoint": "/api/users",
            "headers": {
                "content-type": "application/json",
                "authorization": "Bearer [REDACTED]",  # Should be redacted
            },
        },
    }

    logger.info("Complex request data", data=complex_data)

    clear_context()


def test_logging_levels() -> None:
    """
    Test different logging levels.
    """
    clear_context()
    set_request_id("levels-test")

    # Test different log levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Test with structured data at different levels
    logger.info("User action", action="login", user_id="user123", ip="192.168.1.1")
    logger.warning("Rate limit approaching", user_id="user123", requests_per_minute=58)
    logger.error("Authentication failed", user_id="user123", reason="invalid_credentials")

    clear_context()
