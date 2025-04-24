"""Type stubs for python-json-logger package."""

from typing import Any, Dict

from logging import Formatter, LogRecord

class JsonFormatter(Formatter):
    """JSON formatter for logging."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """Add custom fields to the log record."""
        ...
