"""
Example usage of the logging module.
"""

import time
from typing import List

from uv_boilerplate.utils.logging import LogManager, logger

# Create a custom log manager
custom_log_manager = LogManager(
    app_name="example_app",
    log_level="DEBUG",
    log_dir="example_logs",
    json_output=True,
)

# Example 1: Basic logging
logger.info("This is a basic info message")
logger.warning("This is a warning message")
logger.error("This is an error message")

# Example 2: Logging with extra context
logger.info(
    "User action completed",
    extra={
        "user_id": "12345",
        "action": "login",
        "status": "success",
        "duration_ms": 150,
    },
)


# Example 3: Using log context manager
def process_items(items: List[str]) -> None:
    """
    Process a list of items with logging context.
    """
    with custom_log_manager.log_context(
        "process_items",
        item_count=len(items),
    ) as log:
        log.info("Starting to process items")
        for item in items:
            log.info(f"Processing item: {item}")
            time.sleep(0.1)  # Simulate processing
        log.info("Finished processing items")


# Example 4: Using execution time decorator
@custom_log_manager.log_execution_time
def calculate_sum(numbers: List[int]) -> int:
    """
    Calculate the sum of numbers with execution time logging.
    """
    return sum(numbers)


# Example 5: Using exception logging decorator
@custom_log_manager.log_exceptions
def divide_numbers(a: int, b: int) -> float:
    """
    Divide two numbers with exception logging.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def main() -> None:
    """
    Run the logging examples.
    """
    # Example 3: Process items
    items = ["item1", "item2", "item3"]
    process_items(items)

    # Example 4: Calculate sum
    numbers = [1, 2, 3, 4, 5]
    result = calculate_sum(numbers)
    logger.info(f"Sum calculation result: {result}")

    # Example 5: Division with exception
    try:
        divide_numbers(10, 0)
    except ValueError as e:
        logger.error(f"Division error: {e}")


if __name__ == "__main__":
    main()
