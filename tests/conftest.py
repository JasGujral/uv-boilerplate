"""
Test configuration and fixtures.
"""

import logging
import os
import sys
from pathlib import Path


# Add src directory to Python path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Set test environment variables
os.environ["APP_NAME"] = "test_app"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["LOG_DIR"] = "test_logs"

# Configure root logger for tests
logging.basicConfig(level=logging.DEBUG)
