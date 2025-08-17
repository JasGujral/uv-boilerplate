"""
Comprehensive example demonstrating production-ready logging features.

This example shows how to use the structured logging system with request tracking,
performance monitoring, security features, and real-world use cases for enterprise
applications.
"""

import time
import random
from typing import Dict, Any

from ..utils.logging import (
    logger,
    log_manager,
    LogManager,
    LogConfig,
    set_request_id,
    set_user_id,
    set_session_id,
    clear_context,
)


def basic_logging_example() -> None:
    """
    Demonstrate basic structured logging.
    """
    logger.info("Application started", version="1.0.0", environment="production")

    # Log with structured data
    logger.info(
        "User action performed",
        action="login",
        user_id="user123",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0...",
    )

    # Log errors with context
    try:
        raise ValueError("Invalid input provided")
    except ValueError as e:
        logger.error(
            "Failed to process request",
            error=str(e),
            input_data={"field": "value"},
            operation="data_processing",
        )


def request_tracking_example() -> None:
    """
    Demonstrate request tracking across function calls.
    """
    # Set request context
    set_request_id()
    set_user_id("user456")
    set_session_id("session789")

    logger.info("Request started", endpoint="/api/users", method="GET")

    # Simulate processing
    process_user_data()

    logger.info("Request completed", status_code=200, response_time=0.15)


def process_user_data() -> None:
    """
    Simulate processing user data with request tracking.
    """
    logger.info("Processing user data", step="validation")

    # The request_id is automatically included in all log entries
    validate_input()

    logger.info("User data processed successfully", step="complete")


def validate_input() -> None:
    """
    Simulate input validation.
    """
    logger.debug("Validating input fields", fields=["email", "password"])

    # Simulate some validation logic
    time.sleep(0.01)

    logger.debug("Input validation completed", valid_fields=2)


def performance_monitoring_example() -> None:
    """
    Demonstrate performance monitoring with decorators.
    """

    # Execute operations
    result = _slow_operation()
    logger.info("Slow operation result", result_size=len(result["data"]))

    try:
        _risky_operation()
    except RuntimeError:
        logger.warning("Risky operation failed, continuing...")


@log_manager.log_execution_time
def _slow_operation() -> Dict[str, Any]:
    """
    Simulate a slow operation.
    """
    time.sleep(random.uniform(0.1, 0.5))  # nosec
    return {"result": "success", "data": [1, 2, 3, 4, 5]}


@log_manager.log_exceptions
def _risky_operation() -> str:
    """
    Simulate an operation that might fail.
    """
    if random.random() < 0.3:  # nosec
        raise RuntimeError("Random failure occurred")
    return "Operation successful"


def context_manager_example() -> None:
    """
    Demonstrate logging context managers.
    """

    with log_manager.log_context("database_transaction", table="users") as log:
        log.info("Starting database transaction")

        # Simulate database operations
        time.sleep(0.05)
        log.info("User record inserted", user_id="new_user_123")

        time.sleep(0.03)
        log.info("Transaction committed")


def custom_configuration_example() -> None:
    """
    Demonstrate custom logging configuration.
    """

    # Create custom configuration
    config = LogConfig()
    config.log_level = "DEBUG"
    config.log_format = "console"  # Use console instead of JSON
    config.enable_colors = True
    config.enable_file = False  # Disable file logging for this example

    # Create custom log manager
    custom_log_manager = LogManager(config)
    custom_logger = custom_log_manager.get_logger("custom_app")

    custom_logger.info("Custom logger configured", config_type="development")


def security_example() -> None:
    """
    Demonstrate security features (sensitive data filtering).
    """

    # Log data that might contain sensitive information
    user_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "secret_password_123",  # This will be redacted
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",  # This will be redacted
        "preferences": {"theme": "dark", "language": "en"},
    }

    logger.info("User data received", user_data=user_data)

    # The password and token fields will be automatically redacted
    # Output will show: "password": "[REDACTED]", "token": "[REDACTED]"


def error_handling_example() -> None:
    """
    Demonstrate comprehensive error handling.
    """

    # Execute multiple times to see different error scenarios
    for i in range(5):
        try:
            _complex_operation()
        except Exception:
            logger.warning(f"Operation {i + 1} failed, retrying...")
            time.sleep(0.1)


@log_manager.log_exceptions
def _complex_operation() -> None:
    """
    Simulate a complex operation with multiple failure points.
    """
    logger.info("Starting complex operation")

    # Step 1: Data validation
    if random.random() < 0.2:  # nosec
        raise ValueError("Invalid data format")

    # Step 2: External API call
    if random.random() < 0.3:  # nosec
        raise ConnectionError("External service unavailable")

    # Step 3: Database operation
    if random.random() < 0.1:  # nosec
        raise RuntimeError("Database constraint violation")

    logger.info("Complex operation completed successfully")


def api_request_example() -> None:
    """
    Demonstrate API request/response logging.
    """
    # Set request context
    set_request_id()
    set_user_id("api_user_789")
    set_session_id("api_session_456")

    logger.info(
        "API request received",
        method="POST",
        endpoint="/api/v1/users",
        content_type="application/json",
        user_agent="MyApp/1.0",
    )

    # Simulate API processing
    with log_manager.log_context("api_processing", endpoint="/api/v1/users") as log:
        log.info("Validating request payload")

        # Simulate validation
        time.sleep(0.02)

        log.info("Processing business logic")
        # Simulate business logic
        time.sleep(0.03)

        log.info("Generating response")
        # Simulate response generation
        time.sleep(0.01)

    logger.info(
        "API response sent", status_code=201, response_time=0.06, response_size=1024
    )

    clear_context()


def database_operations_example() -> None:
    """
    Demonstrate database operation logging.
    """
    set_request_id("db-request-123")
    set_user_id("db_user_456")

    # Database connection
    with log_manager.log_context("database_connection", db_host="prod-db-01") as log:
        log.info("Establishing database connection")
        time.sleep(0.01)
        log.info("Database connection established", connection_id="conn-789")

    # Database transaction
    with log_manager.log_context("database_transaction", table="users") as log:
        log.info("Starting transaction")

        # Simulate multiple operations
        log.info("Inserting user record", user_id="new_user_123")
        time.sleep(0.02)

        log.info("Updating user profile", user_id="new_user_123")
        time.sleep(0.01)

        log.info("Committing transaction")
        time.sleep(0.01)

    # Database query
    with log_manager.log_context(
        "database_query", table="users", query_type="select"
    ) as log:
        log.info("Executing user query", filters={"status": "active"})
        time.sleep(0.015)
        log.info("Query completed", result_count=150)

    clear_context()


def external_service_integration_example() -> None:
    """
    Demonstrate external service integration logging.
    """
    set_request_id("ext-service-456")
    set_user_id("service_user_789")

    # External API call
    with log_manager.log_context("external_api_call", service="payment_gateway") as log:
        log.info("Initiating payment processing", amount=99.99, currency="USD")

        try:
            # Simulate external API call
            time.sleep(0.05)
            log.info("Payment processed successfully", transaction_id="txn-12345")
        except Exception as e:
            log.error("Payment processing failed", error=str(e))
            raise

    # Third-party service integration
    with log_manager.log_context(
        "third_party_integration", service="email_service"
    ) as log:
        log.info("Sending notification email", recipient="user@example.com")
        time.sleep(0.02)
        log.info("Email sent successfully", message_id="msg-67890")

    clear_context()


def authentication_authorization_example() -> None:
    """
    Demonstrate authentication and authorization logging.
    """
    set_request_id("auth-request-789")

    # Login attempt
    with log_manager.log_context("authentication") as log:
        log.info("Login attempt", username="john_doe", ip_address="192.168.1.100")

        # Simulate authentication
        time.sleep(0.01)

        # Success case
        log.info("Login successful", user_id="user_123", session_duration=3600)

    # Authorization check
    with log_manager.log_context("authorization", resource="/admin/users") as log:
        log.info("Checking user permissions", user_id="user_123", required_role="admin")

        # Simulate permission check
        time.sleep(0.005)

        log.info("Access granted", user_id="user_123", role="admin")

    # Failed authentication
    with log_manager.log_context("authentication") as log:
        log.warning(
            "Login failed",
            username="invalid_user",
            ip_address="192.168.1.101",
            reason="invalid_credentials",
        )

    clear_context()


def performance_monitoring_advanced_example() -> None:
    """
    Demonstrate advanced performance monitoring.
    """
    set_request_id("perf-monitor-123")

    # Memory usage monitoring
    @log_manager.log_execution_time
    def memory_intensive_operation() -> Dict[str, Any]:
        logger.info("Starting memory-intensive operation")
        # Simulate memory usage
        time.sleep(0.1)
        return {"memory_used_mb": 256, "objects_created": 10000}

    # CPU intensive operation
    @log_manager.log_execution_time
    def cpu_intensive_operation() -> Dict[str, Any]:
        logger.info("Starting CPU-intensive operation")
        # Simulate CPU work
        time.sleep(0.2)
        return {"cpu_usage_percent": 85, "iterations": 1000000}

    # I/O operation
    @log_manager.log_execution_time
    def io_operation() -> Dict[str, Any]:
        logger.info("Starting I/O operation")
        # Simulate I/O
        time.sleep(0.15)
        return {"bytes_read": 1024000, "files_processed": 10}

    # Execute operations
    memory_result = memory_intensive_operation()
    cpu_result = cpu_intensive_operation()
    io_result = io_operation()

    # Log performance summary
    logger.info(
        "Performance monitoring summary",
        memory_usage_mb=memory_result["memory_used_mb"],
        cpu_usage_percent=cpu_result["cpu_usage_percent"],
        io_bytes=io_result["bytes_read"],
    )

    clear_context()


def error_handling_advanced_example() -> None:
    """
    Demonstrate advanced error handling and recovery.
    """
    set_request_id("error-handling-456")

    @log_manager.log_exceptions
    def operation_with_retry() -> str:
        """
        Simulate operation with automatic retry logic.
        """
        logger.info("Attempting operation with retry logic")

        # Simulate different failure scenarios
        failure_type = random.choice(  # nosec
            ["timeout", "connection_error", "validation_error", "success"]
        )

        if failure_type == "timeout":
            raise TimeoutError("Operation timed out")
        elif failure_type == "connection_error":
            raise ConnectionError("Connection failed")
        elif failure_type == "validation_error":
            raise ValueError("Invalid data format")
        else:
            return "Operation successful"

    # Test retry logic
    for attempt in range(3):
        try:
            result = operation_with_retry()
            logger.info(
                "Operation completed successfully", attempt=attempt + 1, result=result
            )
            break
        except Exception as e:
            logger.warning(
                "Operation failed, retrying",
                attempt=attempt + 1,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            if attempt < 2:  # Don't sleep on last attempt
                time.sleep(0.1 * (attempt + 1))  # Exponential backoff

    clear_context()


def security_monitoring_example() -> None:
    """
    Demonstrate security monitoring and threat detection.
    """
    set_request_id("security-monitor-789")

    # Suspicious activity detection
    def detect_suspicious_activity(ip_address: str, user_id: str, action: str) -> None:
        logger.warning(
            "Suspicious activity detected",
            ip_address=ip_address,
            user_id=user_id,
            action=action,
            risk_level="medium",
            threat_type="brute_force",
        )

    # Failed login attempts
    for i in range(5):
        logger.warning(
            "Failed login attempt",
            attempt_number=i + 1,
            username="admin",
            ip_address="192.168.1.200",
            user_agent="Unknown Browser",
        )

    # Trigger security alert
    detect_suspicious_activity("192.168.1.200", "unknown", "multiple_failed_logins")

    # Data access monitoring
    logger.info(
        "Sensitive data accessed",
        user_id="user_456",
        data_type="personal_information",
        access_reason="user_request",
        data_scope="own_profile",
    )

    clear_context()


def business_metrics_example() -> None:
    """
    Demonstrate business metrics and analytics logging.
    """
    set_request_id("business-metrics-123")

    # User engagement metrics
    logger.info(
        "User engagement event",
        user_id="user_789",
        event_type="page_view",
        page="/dashboard",
        session_duration=300,
        user_segment="premium",
    )

    # E-commerce metrics
    logger.info(
        "Purchase completed",
        user_id="user_789",
        order_id="order-12345",
        total_amount=149.99,
        currency="USD",
        payment_method="credit_card",
        items_count=3,
    )

    # Feature usage metrics
    logger.info(
        "Feature usage",
        user_id="user_789",
        feature_name="advanced_search",
        usage_count=5,
        success_rate=0.8,
    )

    # Performance metrics
    logger.info(
        "System performance metrics",
        cpu_usage_percent=45.2,
        memory_usage_percent=67.8,
        disk_usage_percent=23.1,
        active_connections=1250,
        response_time_avg_ms=245,
    )

    clear_context()


def compliance_audit_example() -> None:
    """
    Demonstrate compliance and audit logging.
    """
    set_request_id("compliance-audit-456")

    # Data access audit
    logger.info(
        "Data access audit",
        user_id="admin_123",
        action="view_user_data",
        target_user_id="user_456",
        data_type="personal_information",
        compliance_requirement="GDPR",
        audit_trail_id="audit-789",
    )

    # Configuration change audit
    logger.info(
        "Configuration change audit",
        user_id="admin_123",
        action="update_system_config",
        config_key="max_login_attempts",
        old_value=3,
        new_value=5,
        change_reason="security_policy_update",
        approval_id="approval-123",
    )

    # Data retention audit
    logger.info(
        "Data retention audit",
        data_type="user_logs",
        retention_period_days=90,
        records_processed=15000,
        records_deleted=5000,
        compliance_status="compliant",
    )

    clear_context()


def main() -> None:
    """
    Run all comprehensive logging examples.
    """
    logger.info("Starting comprehensive logging examples demonstration")

    print("\n=== Basic Logging Example ===")
    basic_logging_example()

    print("\n=== Request Tracking Example ===")
    request_tracking_example()

    print("\n=== Performance Monitoring Example ===")
    performance_monitoring_example()

    print("\n=== Context Manager Example ===")
    context_manager_example()

    print("\n=== API Request/Response Example ===")
    api_request_example()

    print("\n=== Database Operations Example ===")
    database_operations_example()

    print("\n=== External Service Integration Example ===")
    external_service_integration_example()

    print("\n=== Authentication & Authorization Example ===")
    authentication_authorization_example()

    print("\n=== Advanced Performance Monitoring Example ===")
    performance_monitoring_advanced_example()

    print("\n=== Advanced Error Handling Example ===")
    error_handling_advanced_example()

    print("\n=== Security Monitoring Example ===")
    security_monitoring_example()

    print("\n=== Business Metrics Example ===")
    business_metrics_example()

    print("\n=== Compliance & Audit Example ===")
    compliance_audit_example()

    print("\n=== Custom Configuration Example ===")
    custom_configuration_example()

    print("\n=== Security Example ===")
    security_example()

    print("\n=== Error Handling Example ===")
    error_handling_example()

    # Clear context at the end
    clear_context()
    logger.info("Comprehensive logging examples demonstration completed")


if __name__ == "__main__":
    main()
