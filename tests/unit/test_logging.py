"""
Test cases for the logging module.
"""

import json
import logging
import tempfile
from pathlib import Path
import time
from typing import Any, Callable, Dict, Generator, TypeVar

import pytest

from uv_boilerplate.utils.logging import CustomJsonFormatter, LogManager, logger

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
def log_manager(temp_log_dir: Path) -> LogManager:
    """
    Create a LogManager instance with temporary log directory.
    """
    return LogManager(
        app_name="test_app",
        log_level="DEBUG",
        log_dir=str(temp_log_dir),
        json_output=True,
    )


def test_log_manager_initialization(temp_log_dir: Path) -> None:
    """
    Test LogManager initialization.
    """
    manager = LogManager(
        app_name="test_app",
        log_level="DEBUG",
        log_dir=str(temp_log_dir),
    )

    assert manager.app_name == "test_app"
    assert manager.log_level == logging.DEBUG
    assert manager.log_dir == temp_log_dir
    assert manager.json_output is True

    # Check if log directory was created
    assert temp_log_dir.exists()
    assert temp_log_dir.is_dir()


def test_log_manager_get_logger(log_manager: LogManager) -> None:
    """
    Test getting logger instance.
    """
    logger_instance = log_manager.get_logger()
    assert isinstance(logger_instance, logging.Logger)
    assert logger_instance.name == "test_app"
    assert logger_instance.level == logging.DEBUG


def test_json_formatter() -> None:
    """
    Test CustomJsonFormatter.
    """
    formatter = CustomJsonFormatter("%(message)s")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="test message",
        args=(),
        exc_info=None,
    )
    message_dict = {"message": "test message"}
    log_record: Dict[str, Any] = {}

    formatter.add_fields(log_record, record, message_dict)

    assert "timestamp" in log_record
    assert "level" in log_record
    assert log_record["level"] == "INFO"
    assert "logger" in log_record
    assert log_record["logger"] == "test"


def test_log_context(log_manager: LogManager, temp_log_dir: Path) -> None:
    """
    Test log context manager.
    """
    with log_manager.log_context("test_operation", test_key="test_value") as log:
        log.info("Test message")

    # Read log file
    log_file = temp_log_dir / "test_app.log"
    assert log_file.exists()

    # Read all lines and get the last one since context manager adds a completion message
    with open(log_file) as f:
        lines = f.readlines()
        log_content = json.loads(lines[-1].strip())
        assert log_content["level"] == "INFO"
        assert "Operation test_operation completed" in log_content["message"]
        assert "context" in log_content
        assert log_content["context"]["operation"] == "test_operation"
        assert log_content["context"]["test_key"] == "test_value"
        assert "duration" in log_content["context"]


def test_log_execution_time(log_manager: LogManager, temp_log_dir: Path) -> None:
    """
    Test execution time logging decorator.
    """

    @log_manager.log_execution_time
    def test_function(x: int, y: int) -> int:
        time.sleep(0.1)
        return x + y

    result = test_function(1, 2)
    assert result == 3

    # Read log file
    log_file = temp_log_dir / "test_app.log"
    assert log_file.exists()

    with open(log_file) as f:
        log_content = json.loads(f.readline().strip())
        assert log_content["level"] == "INFO"
        assert "Function test_function executed" in log_content["message"]
        assert "function" in log_content
        assert log_content["function"] == "test_function"
        assert "duration" in log_content
        assert float(log_content["duration"]) > 0


def test_log_exceptions(log_manager: LogManager, temp_log_dir: Path) -> None:
    """
    Test exception logging decorator.
    """

    @log_manager.log_exceptions
    def test_function(x: int) -> float:
        if x == 0:
            raise ValueError("Cannot divide by zero")
        return 100 / x

    with pytest.raises(ValueError):
        test_function(0)

    # Read log file
    log_file = temp_log_dir / "test_app.log"
    assert log_file.exists()

    with open(log_file) as f:
        log_content = json.loads(f.readline().strip())
        assert log_content["level"] == "ERROR"
        assert "Exception in test_function" in log_content["message"]
        assert "function" in log_content
        assert log_content["function"] == "test_function"
        assert "exception" in log_content
        assert "Cannot divide by zero" in log_content["exception"]


def test_default_logger() -> None:
    """
    Test default logger instance.
    """
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_app"  # Updated to match environment variable
    assert logger.level == logging.DEBUG  # Updated to match environment variable


def test_log_rotation(log_manager: LogManager, temp_log_dir: Path) -> None:
    """
    Test log rotation.
    """
    # Write large log messages to trigger rotation
    message = "x" * 1024 * 1024  # 1MB message
    for i in range(20):  # Write 20MB total to trigger multiple rotations
        log_manager.get_logger().info(f"Test message {i}: {message}")

    # Check if log file exists
    log_file = temp_log_dir / "test_app.log"
    assert log_file.exists()

    # Check if backup files were created
    backup_files = list(temp_log_dir.glob("test_app.log.*"))
    assert len(backup_files) > 0

    # Verify main log file size is less than max_bytes
    assert log_file.stat().st_size <= log_manager.max_bytes


def test_non_json_logging(temp_log_dir: Path) -> None:
    """
    Test non-JSON logging format.
    """
    manager = LogManager(
        app_name="test_app",
        log_level="DEBUG",
        log_dir=str(temp_log_dir),
        json_output=False,
    )

    manager.get_logger().info("Test message")

    # Read log file
    log_file = temp_log_dir / "test_app.log"
    assert not log_file.exists()
