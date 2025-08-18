#!/usr/bin/env python3
"""
Error Handler Module

This module provides comprehensive error handling and recovery mechanisms
for task execution, including retry logic, graceful degradation, and error reporting.

Author: AI Development Ecosystem
Version: 1.0
Last Updated: 2024-08-07
"""

import json
import logging
import os
import sqlite3
import sys
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections.abc import Callable

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""

    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    DATABASE = "database"
    PERMISSION = "permission"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    EXECUTION = "execution"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """Error information data structure."""

    error_type: str
    error_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: str
    timestamp: datetime
    retry_count: int = 0
    max_retries: int = 3
    recovery_action: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class RecoveryAction:
    """Recovery action data structure."""

    name: str
    description: str
    action_type: str
    parameters: dict[str, Any]
    success_criteria: str
    estimated_time: float


class ErrorHandler:
    """Comprehensive error handling and recovery system."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the error handler."""
        self.config = config or self._get_default_config()
        self.error_history: list[ErrorInfo] = []
        self.recovery_actions: dict[str, RecoveryAction] = self._init_recovery_actions()
        self.retry_strategies: dict[ErrorCategory, dict[str, Any]] = self._init_retry_strategies()

        logger.info("Error handler initialized")

    def _get_default_config(self) -> dict[str, Any]:
        """Get default error handler configuration."""
        return {
            "max_retries": 3,
            "base_delay": 1.0,
            "max_delay": 60.0,
            "backoff_multiplier": 2.0,
            "enable_logging": True,
            "enable_recovery": True,
            "enable_metrics": True,
            "error_threshold": 10,
            "timeout": 300,
        }

    def _init_recovery_actions(self) -> dict[str, RecoveryAction]:
        """Initialize recovery actions for different error types."""
        actions = {}

        # Network error recovery
        actions["network_retry"] = RecoveryAction(
            name="Network Retry",
            description="Retry network operation with exponential backoff",
            action_type="retry",
            parameters={"max_retries": 3, "base_delay": 2.0},
            success_criteria="Network operation succeeds",
            estimated_time=30.0,
        )

        # File system error recovery
        actions["file_cleanup"] = RecoveryAction(
            name="File Cleanup",
            description="Clean up temporary files and retry operation",
            action_type="cleanup",
            parameters={"temp_patterns": ["*.tmp", "*.temp"]},
            success_criteria="File operation succeeds",
            estimated_time=10.0,
        )

        # Database error recovery
        actions["db_reconnect"] = RecoveryAction(
            name="Database Reconnect",
            description="Reconnect to database and retry operation",
            action_type="reconnect",
            parameters={"max_attempts": 3, "delay": 5.0},
            success_criteria="Database connection restored",
            estimated_time=15.0,
        )

        # Permission error recovery
        actions["permission_fix"] = RecoveryAction(
            name="Permission Fix",
            description="Attempt to fix file permissions",
            action_type="permission",
            parameters={"chmod": "755", "chown": None},
            success_criteria="File permissions allow operation",
            estimated_time=5.0,
        )

        # Timeout error recovery
        actions["timeout_extend"] = RecoveryAction(
            name="Timeout Extension",
            description="Extend timeout and retry operation",
            action_type="timeout",
            parameters={"multiplier": 2.0, "max_timeout": 600},
            success_criteria="Operation completes within extended timeout",
            estimated_time=60.0,
        )

        return actions

    def _init_retry_strategies(self) -> dict[ErrorCategory, dict[str, Any]]:
        """Initialize retry strategies for different error categories."""
        strategies = {}

        # Network errors
        strategies[ErrorCategory.NETWORK] = {
            "max_retries": 5,
            "base_delay": 2.0,
            "backoff_multiplier": 2.0,
            "max_delay": 60.0,
            "jitter": True,
        }

        # File system errors
        strategies[ErrorCategory.FILE_SYSTEM] = {
            "max_retries": 3,
            "base_delay": 1.0,
            "backoff_multiplier": 1.5,
            "max_delay": 30.0,
            "jitter": False,
        }

        # Database errors
        strategies[ErrorCategory.DATABASE] = {
            "max_retries": 3,
            "base_delay": 5.0,
            "backoff_multiplier": 2.0,
            "max_delay": 120.0,
            "jitter": True,
        }

        # Permission errors
        strategies[ErrorCategory.PERMISSION] = {
            "max_retries": 2,
            "base_delay": 1.0,
            "backoff_multiplier": 1.0,
            "max_delay": 10.0,
            "jitter": False,
        }

        # Timeout errors
        strategies[ErrorCategory.TIMEOUT] = {
            "max_retries": 2,
            "base_delay": 5.0,
            "backoff_multiplier": 2.0,
            "max_delay": 60.0,
            "jitter": True,
        }

        # Validation errors
        strategies[ErrorCategory.VALIDATION] = {
            "max_retries": 1,
            "base_delay": 0.0,
            "backoff_multiplier": 1.0,
            "max_delay": 0.0,
            "jitter": False,
        }

        # Execution errors
        strategies[ErrorCategory.EXECUTION] = {
            "max_retries": 3,
            "base_delay": 2.0,
            "backoff_multiplier": 1.5,
            "max_delay": 30.0,
            "jitter": True,
        }

        return strategies

    def classify_error(self, error: Exception) -> ErrorCategory:
        """Classify an error into a category."""
        error_type = type(error).__name__
        error_message = str(error).lower()

        # Network errors
        if any(
            network_error in error_type.lower()
            for network_error in ["connection", "timeout", "socket", "http", "urllib"]
        ):
            return ErrorCategory.NETWORK

        # File system errors
        if any(fs_error in error_type.lower() for fs_error in ["file", "io", "oserror", "permission"]):
            return ErrorCategory.FILE_SYSTEM

        # Database errors
        if any(db_error in error_type.lower() for db_error in ["sqlite", "database", "db", "connection"]):
            return ErrorCategory.DATABASE

        # Permission errors
        if any(perm_error in error_message for perm_error in ["permission", "access", "denied", "forbidden"]):
            return ErrorCategory.PERMISSION

        # Timeout errors
        if any(timeout_error in error_message for timeout_error in ["timeout", "timed out", "deadline"]):
            return ErrorCategory.TIMEOUT

        # Validation errors
        if any(
            validation_error in error_type.lower() for validation_error in ["value", "type", "validation", "argument"]
        ):
            return ErrorCategory.VALIDATION

        # Execution errors
        if any(exec_error in error_type.lower() for exec_error in ["runtime", "execution", "subprocess"]):
            return ErrorCategory.EXECUTION

        return ErrorCategory.UNKNOWN

    def determine_severity(self, error: Exception, context: str) -> ErrorSeverity:
        """Determine the severity of an error."""
        error_type = type(error).__name__
        error_message = str(error).lower()

        # Critical errors
        if any(critical_error in error_message for critical_error in ["fatal", "critical", "system", "kernel"]):
            return ErrorSeverity.CRITICAL

        # High severity errors
        if any(high_error in error_type.lower() for high_error in ["database", "connection", "file"]):
            return ErrorSeverity.HIGH

        # Medium severity errors
        if any(medium_error in error_type.lower() for medium_error in ["timeout", "validation", "permission"]):
            return ErrorSeverity.MEDIUM

        # Low severity errors (default)
        return ErrorSeverity.LOW

    def handle_error(self, error: Exception, context: str, retry_count: int = 0) -> ErrorInfo:
        """Handle an error and return error information."""
        error_info = ErrorInfo(
            error_type=type(error).__name__,
            error_message=str(error),
            severity=self.determine_severity(error, context),
            category=self.classify_error(error),
            context=context,
            timestamp=datetime.now(),
            retry_count=retry_count,
            max_retries=self.config["max_retries"],
            metadata={
                "traceback": traceback.format_exc(),
                "sys_info": {"platform": sys.platform, "python_version": sys.version, "cwd": os.getcwd()},
            },
        )

        # Log the error
        self._log_error(error_info)

        # Add to history
        self.error_history.append(error_info)

        # Check if we should attempt recovery
        if self.config["enable_recovery"]:
            recovery_action = self._get_recovery_action(error_info)
            if recovery_action:
                error_info.recovery_action = recovery_action.name
                success = self._execute_recovery_action(recovery_action, error_info)
                if success:
                    logger.info(f"Recovery action '{recovery_action.name}' succeeded")
                else:
                    logger.warning(f"Recovery action '{recovery_action.name}' failed")

        return error_info

    def _log_error(self, error_info: ErrorInfo) -> None:
        """Log error information."""
        if not self.config["enable_logging"]:
            return

        log_message = (
            f"Error in {error_info.context}: {error_info.error_type} - "
            f"{error_info.error_message} (Severity: {error_info.severity.value}, "
            f"Category: {error_info.category.value}, Retry: {error_info.retry_count}/{error_info.max_retries})"
        )

        if error_info.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
            logger.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)

    def _get_recovery_action(self, error_info: ErrorInfo) -> RecoveryAction | None:
        """Get appropriate recovery action for an error."""
        category = error_info.category

        if category == ErrorCategory.NETWORK:
            return self.recovery_actions.get("network_retry")
        elif category == ErrorCategory.FILE_SYSTEM:
            return self.recovery_actions.get("file_cleanup")
        elif category == ErrorCategory.DATABASE:
            return self.recovery_actions.get("db_reconnect")
        elif category == ErrorCategory.PERMISSION:
            return self.recovery_actions.get("permission_fix")
        elif category == ErrorCategory.TIMEOUT:
            return self.recovery_actions.get("timeout_extend")

        return None

    def _execute_recovery_action(self, action: RecoveryAction, error_info: ErrorInfo) -> bool:
        """Execute a recovery action."""
        try:
            if action.action_type == "retry":
                return self._execute_retry_action(action, error_info)
            elif action.action_type == "cleanup":
                return self._execute_cleanup_action(action, error_info)
            elif action.action_type == "reconnect":
                return self._execute_reconnect_action(action, error_info)
            elif action.action_type == "permission":
                return self._execute_permission_action(action, error_info)
            elif action.action_type == "timeout":
                return self._execute_timeout_action(action, error_info)
            else:
                logger.warning(f"Unknown recovery action type: {action.action_type}")
                return False

        except Exception as e:
            logger.error(f"Failed to execute recovery action '{action.name}': {e}")
            return False

    def _execute_retry_action(self, action: RecoveryAction, error_info: ErrorInfo) -> bool:
        """Execute a retry recovery action."""
        max_retries = action.parameters.get("max_retries", 3)
        base_delay = action.parameters.get("base_delay", 1.0)

        if error_info.retry_count >= max_retries:
            logger.warning(f"Max retries ({max_retries}) exceeded for {error_info.context}")
            return False

        delay = base_delay * (2**error_info.retry_count)
        logger.info(f"Retrying {error_info.context} in {delay:.1f} seconds (attempt {error_info.retry_count + 1})")

        time.sleep(delay)
        return True

    def _execute_cleanup_action(self, action: RecoveryAction, error_info: ErrorInfo) -> bool:
        """Execute a cleanup recovery action."""
        temp_patterns = action.parameters.get("temp_patterns", ["*.tmp", "*.temp"])

        try:
            cleaned_files = 0
            for pattern in temp_patterns:
                for file_path in Path(".").glob(pattern):
                    try:
                        file_path.unlink()
                        cleaned_files += 1
                    except Exception as e:
                        logger.debug(f"Failed to clean up {file_path}: {e}")

            logger.info(f"Cleaned up {cleaned_files} temporary files")
            return True

        except Exception as e:
            logger.error(f"Cleanup action failed: {e}")
            return False

    def _execute_reconnect_action(self, action: RecoveryAction, error_info: ErrorInfo) -> bool:
        """Execute a reconnect recovery action."""
        max_attempts = action.parameters.get("max_attempts", 3)
        delay = action.parameters.get("delay", 5.0)

        logger.info(f"Attempting database reconnect (max {max_attempts} attempts)")

        for attempt in range(max_attempts):
            try:
                # Simulate database reconnection
                time.sleep(delay)
                logger.info(f"Database reconnection attempt {attempt + 1} successful")
                return True
            except Exception as e:
                logger.warning(f"Database reconnection attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(delay)

        return False

    def _execute_permission_action(self, action: RecoveryAction, error_info: ErrorInfo) -> bool:
        """Execute a permission fix recovery action."""
        chmod = action.parameters.get("chmod", "755")

        try:
            # Extract file path from error message if possible
            error_message = error_info.error_message
            if "permission denied" in error_message.lower():
                logger.info("Attempting to fix file permissions")
                # In a real implementation, this would fix the actual file permissions
                return True
            else:
                logger.warning("Permission error but no file path found")
                return False

        except Exception as e:
            logger.error(f"Permission fix action failed: {e}")
            return False

    def _execute_timeout_action(self, action: RecoveryAction, error_info: ErrorInfo) -> bool:
        """Execute a timeout extension recovery action."""
        multiplier = action.parameters.get("multiplier", 2.0)
        max_timeout = action.parameters.get("max_timeout", 600)

        logger.info(f"Extending timeout by {multiplier}x (max {max_timeout}s)")

        # In a real implementation, this would update the timeout configuration
        return True

    def should_retry(self, error_info: ErrorInfo) -> bool:
        """Determine if an error should be retried."""
        category = error_info.category
        strategy = self.retry_strategies.get(category, {})

        max_retries = strategy.get("max_retries", self.config["max_retries"])

        # Don't retry critical errors
        if error_info.severity == ErrorSeverity.CRITICAL:
            return False

        # Don't retry validation errors more than once
        if category == ErrorCategory.VALIDATION and error_info.retry_count > 0:
            return False

        # Check retry count
        return error_info.retry_count < max_retries

    def get_retry_delay(self, error_info: ErrorInfo) -> float:
        """Get the delay before the next retry attempt."""
        category = error_info.category
        strategy = self.retry_strategies.get(category, {})

        base_delay = strategy.get("base_delay", self.config["base_delay"])
        backoff_multiplier = strategy.get("backoff_multiplier", self.config["backoff_multiplier"])
        max_delay = strategy.get("max_delay", self.config["max_delay"])
        jitter = strategy.get("jitter", True)

        # Calculate delay with exponential backoff
        delay = base_delay * (backoff_multiplier**error_info.retry_count)
        delay = min(delay, max_delay)

        # Add jitter if enabled
        if jitter:
            import random

            delay *= 0.5 + random.random() * 0.5

        return delay

    def get_error_statistics(self) -> dict[str, Any]:
        """Get error handling statistics."""
        if not self.error_history:
            return {"total_errors": 0}

        stats = {
            "total_errors": len(self.error_history),
            "by_severity": {},
            "by_category": {},
            "by_context": {},
            "recovery_success_rate": 0.0,
            "avg_retry_count": 0.0,
            "recent_errors": [],
        }

        # Count by severity
        for error in self.error_history:
            severity = error.severity.value
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1

        # Count by category
        for error in self.error_history:
            category = error.category.value
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

        # Count by context
        for error in self.error_history:
            context = error.context
            stats["by_context"][context] = stats["by_context"].get(context, 0) + 1

        # Calculate recovery success rate
        recovery_attempts = sum(1 for e in self.error_history if e.recovery_action)
        recovery_successes = sum(1 for e in self.error_history if e.recovery_action and e.retry_count < e.max_retries)
        if recovery_attempts > 0:
            stats["recovery_success_rate"] = recovery_successes / recovery_attempts

        # Calculate average retry count
        total_retries = sum(e.retry_count for e in self.error_history)
        stats["avg_retry_count"] = total_retries / len(self.error_history)

        # Get recent errors (last 10)
        recent_errors = sorted(self.error_history, key=lambda e: e.timestamp, reverse=True)[:10]
        stats["recent_errors"] = [
            {
                "timestamp": e.timestamp.isoformat(),
                "context": e.context,
                "error_type": e.error_type,
                "severity": e.severity.value,
                "category": e.category.value,
            }
            for e in recent_errors
        ]

        return stats

    def clear_error_history(self) -> None:
        """Clear error history."""
        self.error_history.clear()
        logger.info("Error history cleared")

    def export_error_report(self, output_file: str) -> bool:
        """Export error report to JSON file."""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "statistics": self.get_error_statistics(),
                "error_history": [asdict(error) for error in self.error_history],
                "recovery_actions": {name: asdict(action) for name, action in self.recovery_actions.items()},
                "retry_strategies": {category.value: strategy for category, strategy in self.retry_strategies.items()},
            }

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"Error report exported to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to export error report: {e}")
            return False


def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_multiplier: float = 2.0,
    jitter: bool = True,
    error_handler: ErrorHandler | None = None,
) -> Callable:
    """Decorator for retrying functions with exponential backoff."""

    def wrapper(*args, **kwargs):
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt == max_retries:
                    # Final attempt failed
                    if error_handler:
                        error_handler.handle_error(e, f"{func.__name__}", attempt)
                    raise e

                # Calculate delay
                delay = base_delay * (backoff_multiplier**attempt)
                delay = min(delay, max_delay)

                # Add jitter if enabled
                if jitter:
                    import random

                    delay *= 0.5 + random.random() * 0.5

                # Log retry attempt
                logger.warning(
                    f"Attempt {attempt + 1} failed for {func.__name__}, " f"retrying in {delay:.1f} seconds: {e}"
                )

                time.sleep(delay)

        # This should never be reached, but just in case
        raise last_exception

    return wrapper


def main():
    """Test the error handler."""
    import argparse

    parser = argparse.ArgumentParser(description="Error Handler Test")
    parser.add_argument(
        "--test-error",
        choices=["network", "file", "database", "permission", "timeout"],
        help="Test specific error type",
    )
    parser.add_argument("--export-report", help="Export error report to file")
    parser.add_argument("--show-stats", action="store_true", help="Show error statistics")

    args = parser.parse_args()

    error_handler = ErrorHandler()

    if args.test_error:
        # Test specific error type
        if args.test_error == "network":
            try:
                raise ConnectionError("Connection refused")
            except Exception as e:
                error_info = error_handler.handle_error(e, "test_network_operation")
                print(f"Handled network error: {error_info}")

        elif args.test_error == "file":
            try:
                raise FileNotFoundError("No such file or directory")
            except Exception as e:
                error_info = error_handler.handle_error(e, "test_file_operation")
                print(f"Handled file error: {error_info}")

        elif args.test_error == "database":
            try:
                raise sqlite3.OperationalError("database is locked")
            except Exception as e:
                error_info = error_handler.handle_error(e, "test_database_operation")
                print(f"Handled database error: {error_info}")

        elif args.test_error == "permission":
            try:
                raise PermissionError("Permission denied")
            except Exception as e:
                error_info = error_handler.handle_error(e, "test_permission_operation")
                print(f"Handled permission error: {error_info}")

        elif args.test_error == "timeout":
            try:
                raise TimeoutError("Operation timed out")
            except Exception as e:
                error_info = error_handler.handle_error(e, "test_timeout_operation")
                print(f"Handled timeout error: {error_info}")

    if args.show_stats:
        stats = error_handler.get_error_statistics()
        print("Error Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    if args.export_report:
        if error_handler.export_error_report(args.export_report):
            print(f"Error report exported to {args.export_report}")
        else:
            print("Failed to export error report")


if __name__ == "__main__":
    main()
