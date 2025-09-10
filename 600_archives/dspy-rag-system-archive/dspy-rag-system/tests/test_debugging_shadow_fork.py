#!/usr/bin/env python3
"""
Unit tests for enhanced debugging capabilities
"""

from datetime import datetime

import pytest

from src.dspy_modules.context_models import AIRole, PlannerContext
from src.dspy_modules.dynamic_prompts import PromptContext
from src.dspy_modules.enhanced_debugging import (
    ContextCorrelation,
    DebuggingContext,
    EnhancedDebuggingManager,
    RichErrorMessage,
    StructuredLogEntry,
    analyze_error_patterns,
    correlate_errors,
    enhanced_debugging,
)
from src.dspy_modules.error_taxonomy import ErrorSeverity


class TestDebuggingContext:
    """Test DebuggingContext model"""

    def test_debugging_context_creation(self):
        """Test creating a debugging context"""
        context = DebuggingContext(
            context_id="test_context_123", user_context=None, role_context=None, correlation_id=None
        )

        assert context.context_id == "test_context_123"
        assert context.user_context is None
        assert context.role_context is None
        assert isinstance(context.timestamp, datetime)
        assert context.execution_stack == []
        assert context.variable_snapshot == {}

    def test_debugging_context_with_user_context(self):
        """Test debugging context with user context"""
        user_context = PromptContext(
            user_id="test_user", session_id="test_session", user_preferences={}, dynamic_variables={}, role_context=None
        )

        context = DebuggingContext(
            context_id="test_context_456", user_context=user_context, role_context=None, correlation_id=None
        )

        assert context.user_context == user_context
        assert context.user_context is not None
        assert context.user_context.user_id == "test_user"

    def test_debugging_context_with_role_context(self):
        """Test debugging context with role context"""
        role_context = PlannerContext(
            session_id="test_session", project_scope="test_project", backlog_priority="P1", user_id=None
        )

        context = DebuggingContext(
            context_id="test_context_789", role_context=role_context, user_context=None, correlation_id=None
        )

        assert context.role_context == role_context
        assert context.role_context is not None
        assert context.role_context.role == AIRole.PLANNER

    def test_debugging_context_validation(self):
        """Test debugging context validation"""
        # Test valid context ID
        context = DebuggingContext(context_id="valid_id", user_context=None, role_context=None, correlation_id=None)
        assert context.context_id == "valid_id"

        # Test invalid context ID
        with pytest.raises(ValueError, match="Context ID must be at least 3 characters"):
            DebuggingContext(context_id="ab", user_context=None, role_context=None, correlation_id=None)

    def test_debugging_context_with_variables(self):
        """Test debugging context with variable snapshot"""
        variables = {"test_var": "test_value", "number_var": 42, "list_var": [1, 2, 3]}

        context = DebuggingContext(
            context_id="test_context",
            variable_snapshot=variables,
            user_context=None,
            role_context=None,
            correlation_id=None,
        )

        assert context.variable_snapshot == variables


class TestRichErrorMessage:
    """Test RichErrorMessage model"""

    def test_rich_error_message_creation(self):
        """Test creating a rich error message"""
        error_msg = RichErrorMessage(
            error_id="test_error_123",
            error_type="ValueError",
            error_message="Test error message",
            technical_details="Technical details here",
            user_friendly_message="User-friendly message",
            severity=ErrorSeverity.MEDIUM,
            debugging_context=None,
        )

        assert error_msg.error_id == "test_error_123"
        assert error_msg.error_type == "ValueError"
        assert error_msg.error_message == "Test error message"
        assert error_msg.severity == ErrorSeverity.MEDIUM
        assert isinstance(error_msg.timestamp, datetime)

    def test_rich_error_message_validation(self):
        """Test rich error message validation"""
        # Test valid error ID
        error_msg = RichErrorMessage(
            error_id="valid_error_id",
            error_type="TestError",
            error_message="Valid error message",
            technical_details="Details",
            user_friendly_message="User message",
            severity=ErrorSeverity.LOW,
            debugging_context=None,
        )
        assert error_msg.error_id == "valid_error_id"

        # Test invalid error ID
        with pytest.raises(ValueError, match="Error ID must be at least 3 characters"):
            RichErrorMessage(
                error_id="ab",
                error_type="TestError",
                error_message="Valid error message",
                technical_details="Details",
                user_friendly_message="User message",
                severity=ErrorSeverity.LOW,
                debugging_context=None,
            )

        # Test invalid error message
        with pytest.raises(ValueError, match="Error message must be at least 5 characters"):
            RichErrorMessage(
                error_id="valid_id",
                error_type="TestError",
                error_message="test",
                technical_details="Details",
                user_friendly_message="User message",
                severity=ErrorSeverity.LOW,
                debugging_context=None,
            )

    def test_rich_error_message_with_suggestions(self):
        """Test rich error message with suggested actions"""
        error_msg = RichErrorMessage(
            error_id="test_error",
            error_type="ValidationError",
            error_message="Validation failed",
            technical_details="Technical details",
            user_friendly_message="Please check your input",
            severity=ErrorSeverity.MEDIUM,
            suggested_actions=["Check format", "Verify data"],
            debugging_context=None,
        )

        assert len(error_msg.suggested_actions) == 2
        assert "Check format" in error_msg.suggested_actions


class TestContextCorrelation:
    """Test ContextCorrelation model"""

    def test_context_correlation_creation(self):
        """Test creating a context correlation"""
        primary_context = DebuggingContext(
            context_id="primary", user_context=None, role_context=None, correlation_id=None
        )
        related_contexts = [
            DebuggingContext(context_id="related1", user_context=None, role_context=None, correlation_id=None),
            DebuggingContext(context_id="related2", user_context=None, role_context=None, correlation_id=None),
        ]

        correlation = ContextCorrelation(
            correlation_id="test_correlation",
            primary_context=primary_context,
            related_contexts=related_contexts,
            correlation_patterns=["pattern1", "pattern2"],
            confidence_score=0.8,
        )

        assert correlation.correlation_id == "test_correlation"
        assert correlation.primary_context == primary_context
        assert len(correlation.related_contexts) == 2
        assert correlation.confidence_score == 0.8

    def test_context_correlation_validation(self):
        """Test context correlation validation"""
        primary_context = DebuggingContext(
            context_id="primary", user_context=None, role_context=None, correlation_id=None
        )

        # Test valid correlation ID
        correlation = ContextCorrelation(
            correlation_id="valid_correlation", primary_context=primary_context, confidence_score=0.5
        )
        assert correlation.correlation_id == "valid_correlation"

        # Test invalid correlation ID
        with pytest.raises(ValueError, match="Correlation ID must be at least 3 characters"):
            ContextCorrelation(correlation_id="ab", primary_context=primary_context, confidence_score=0.5)

        # Test invalid confidence score
        with pytest.raises(Exception):  # Pydantic validation error
            ContextCorrelation(correlation_id="valid_id", primary_context=primary_context, confidence_score=1.5)


class TestStructuredLogEntry:
    """Test StructuredLogEntry model"""

    def test_structured_log_entry_creation(self):
        """Test creating a structured log entry"""
        log_entry = StructuredLogEntry(
            log_id="test_log_123", level="INFO", message="Test log message", source="test_source", correlation_id=None
        )

        assert log_entry.log_id == "test_log_123"
        assert log_entry.level == "INFO"
        assert log_entry.message == "Test log message"
        assert log_entry.source == "test_source"
        assert isinstance(log_entry.timestamp, datetime)

    def test_structured_log_entry_validation(self):
        """Test structured log entry validation"""
        # Test valid log ID
        log_entry = StructuredLogEntry(
            log_id="valid_log_id", level="DEBUG", message="Test message", source="test", correlation_id=None
        )
        assert log_entry.log_id == "valid_log_id"

        # Test invalid log ID
        with pytest.raises(ValueError, match="Log ID must be at least 3 characters"):
            StructuredLogEntry(log_id="ab", level="INFO", message="Test message", source="test", correlation_id=None)

        # Test invalid level
        with pytest.raises(ValueError, match="Log level must be one of"):
            StructuredLogEntry(
                log_id="valid_id", level="INVALID", message="Test message", source="test", correlation_id=None
            )

    def test_structured_log_entry_with_context(self):
        """Test structured log entry with context data"""
        context_data = {"key1": "value1", "key2": 42}

        log_entry = StructuredLogEntry(
            log_id="test_log",
            level="WARNING",
            message="Warning message",
            source="test",
            context_data=context_data,
            correlation_id=None,
        )

        assert log_entry.context_data == context_data


class TestEnhancedDebuggingManager:
    """Test EnhancedDebuggingManager"""

    def test_debugging_manager_initialization(self):
        """Test debugging manager initialization"""
        manager = EnhancedDebuggingManager()

        assert manager.enable_privacy is True
        assert manager.max_context_history == 100
        assert len(manager.context_history) == 0
        assert len(manager.error_history) == 0
        assert len(manager.correlation_cache) == 0

    def test_capture_debugging_context(self):
        """Test capturing debugging context"""
        manager = EnhancedDebuggingManager()

        context = manager.capture_debugging_context()

        assert context.context_id.startswith("debug_")
        assert isinstance(context.timestamp, datetime)
        assert context.execution_stack is not None
        assert context.variable_snapshot == {}

    def test_capture_debugging_context_with_variables(self):
        """Test capturing debugging context with variables"""
        manager = EnhancedDebuggingManager()

        variables = {"test_var": "test_value", "sensitive_password": "secret123"}
        context = manager.capture_debugging_context(variable_snapshot=variables)

        # Check that sensitive data is redacted
        assert context.variable_snapshot["test_var"] == "test_value"
        assert context.variable_snapshot["sensitive_password"] == "[REDACTED]"

    def test_create_rich_error_message(self):
        """Test creating rich error message"""
        manager = EnhancedDebuggingManager()

        # Create a test error
        test_error = ValueError("Test validation error")

        rich_error = manager.create_rich_error_message(test_error)

        assert rich_error.error_id.startswith("error_")
        assert rich_error.error_type == "ValueError"
        assert rich_error.error_message == "Test validation error"
        assert rich_error.severity == ErrorSeverity.MEDIUM
        assert len(rich_error.suggested_actions) > 0
        assert rich_error.debugging_context is not None

    def test_create_rich_error_message_with_context(self):
        """Test creating rich error message with existing context"""
        manager = EnhancedDebuggingManager()

        # Create debugging context first
        context = manager.capture_debugging_context()

        # Create error with existing context
        test_error = ConnectionError("Connection failed")
        rich_error = manager.create_rich_error_message(test_error, debugging_context=context)

        assert rich_error.debugging_context == context
        assert rich_error.severity == ErrorSeverity.HIGH

    def test_correlate_contexts(self):
        """Test context correlation"""
        manager = EnhancedDebuggingManager()

        # Create multiple contexts
        context1 = manager.capture_debugging_context()
        manager.capture_debugging_context()  # Create additional context for correlation
        manager.capture_debugging_context()  # Create additional context for correlation

        # Correlate contexts
        correlation = manager.correlate_contexts(context1)

        assert correlation.correlation_id.startswith("corr_")
        assert correlation.primary_context == context1
        assert correlation.confidence_score >= 0.0
        assert correlation.confidence_score <= 1.0

    def test_log_structured_entry(self):
        """Test structured logging"""
        manager = EnhancedDebuggingManager()

        log_entry = manager.log_structured_entry(
            level="INFO", message="Test log message", context_data={"test_var": "test_value"}
        )

        assert log_entry.log_id.startswith("log_")
        assert log_entry.level == "INFO"
        assert log_entry.message == "Test log message"
        # test_var should not be redacted since it doesn't contain sensitive patterns
        assert log_entry.context_data["test_var"] == "test_value"

    def test_get_debugging_summary(self):
        """Test getting debugging summary"""
        manager = EnhancedDebuggingManager()

        # Create some test data
        manager.capture_debugging_context()
        manager.capture_debugging_context()

        test_error = ValueError("Test error")
        manager.create_rich_error_message(test_error)

        summary = manager.get_debugging_summary()

        # Should have 3 contexts: 2 from capture_debugging_context + 1 from create_rich_error_message
        assert summary["total_contexts"] == 3
        assert summary["total_errors"] == 1
        assert "error_distribution" in summary
        assert "context_timeline" in summary

    def test_privacy_disabled(self):
        """Test debugging manager with privacy disabled"""
        manager = EnhancedDebuggingManager(enable_privacy=False)

        variables = {"sensitive_password": "secret123"}
        context = manager.capture_debugging_context(variable_snapshot=variables)

        # Check that sensitive data is not redacted
        assert context.variable_snapshot["sensitive_password"] == "secret123"

    def test_context_history_limit(self):
        """Test context history size limit"""
        manager = EnhancedDebuggingManager(max_context_history=2)

        # Create more contexts than the limit
        for i in range(5):
            manager.capture_debugging_context()

        # Should only keep the last 2 contexts
        assert len(manager.context_history) == 2


class TestEnhancedDebuggingDecorator:
    """Test enhanced debugging decorator"""

    def test_enhanced_debugging_decorator_success(self):
        """Test enhanced debugging decorator with successful execution"""

        @enhanced_debugging()
        def test_function(x, y):
            return x + y

        result = test_function(2, 3)
        assert result == 5

    def test_enhanced_debugging_decorator_error(self):
        """Test enhanced debugging decorator with error"""

        @enhanced_debugging()
        def test_function(x, y):
            raise ValueError("Test error")

        with pytest.raises(ValueError, match=".*Error ID:"):
            test_function(2, 3)

    def test_enhanced_debugging_decorator_with_variables(self):
        """Test enhanced debugging decorator with variable capture"""

        @enhanced_debugging(capture_variables=True)
        def test_function(x, y):
            return x * y

        result = test_function(4, 5)
        assert result == 20

    def test_enhanced_debugging_decorator_privacy(self):
        """Test enhanced debugging decorator with privacy settings"""

        @enhanced_debugging(enable_privacy=True)
        def test_function(password, data):
            return "success"

        # Should not raise an error even with sensitive data
        result = test_function("secret123", "normal_data")
        assert result == "success"


class TestContextCorrelationUtilities:
    """Test context correlation utility functions"""

    def test_correlate_errors(self):
        """Test error correlation utility"""
        manager = EnhancedDebuggingManager()

        # Create multiple error messages
        error1 = ValueError("Error 1")
        error2 = TypeError("Error 2")

        rich_error1 = manager.create_rich_error_message(error1)
        rich_error2 = manager.create_rich_error_message(error2)

        correlations = correlate_errors([rich_error1, rich_error2])

        assert len(correlations) == 2
        assert all(isinstance(corr, ContextCorrelation) for corr in correlations)

    def test_analyze_error_patterns(self):
        """Test error pattern analysis"""
        manager = EnhancedDebuggingManager()

        # Create multiple error messages
        error1 = ValueError("Validation error")
        error2 = ConnectionError("Connection failed")
        error3 = ValueError("Another validation error")

        rich_error1 = manager.create_rich_error_message(error1)
        rich_error2 = manager.create_rich_error_message(error2)
        rich_error3 = manager.create_rich_error_message(error3)

        analysis = analyze_error_patterns([rich_error1, rich_error2, rich_error3])

        assert analysis["total_errors"] == 3
        assert "ValueError" in analysis["error_types"]
        assert "ConnectionError" in analysis["error_types"]
        assert analysis["error_types"]["ValueError"] == 2
        assert analysis["error_types"]["ConnectionError"] == 1

    def test_analyze_error_patterns_empty(self):
        """Test error pattern analysis with empty list"""
        analysis = analyze_error_patterns([])

        assert analysis["message"] == "No error messages to analyze"


class TestErrorSeverityDetermination:
    """Test error severity determination"""

    def test_critical_error_severity(self):
        """Test critical error severity detection"""
        manager = EnhancedDebuggingManager()

        error = Exception("Security violation detected")
        rich_error = manager.create_rich_error_message(error)

        assert rich_error.severity == ErrorSeverity.CRITICAL

    def test_high_error_severity(self):
        """Test high error severity detection"""
        manager = EnhancedDebuggingManager()

        error = Exception("Database connection timeout")
        rich_error = manager.create_rich_error_message(error)

        assert rich_error.severity == ErrorSeverity.HIGH

    def test_medium_error_severity(self):
        """Test medium error severity detection"""
        manager = EnhancedDebuggingManager()

        error = Exception("Data validation failed")
        rich_error = manager.create_rich_error_message(error)

        assert rich_error.severity == ErrorSeverity.MEDIUM

    def test_low_error_severity(self):
        """Test low error severity detection"""
        manager = EnhancedDebuggingManager()

        error = Exception("Unknown error occurred")
        rich_error = manager.create_rich_error_message(error)

        assert rich_error.severity == ErrorSeverity.LOW


class TestUserFriendlyMessages:
    """Test user-friendly message generation"""

    def test_validation_error_message(self):
        """Test user-friendly message for validation errors"""
        manager = EnhancedDebuggingManager()

        error = ValueError("Validation failed")
        rich_error = manager.create_rich_error_message(error)

        assert "data format is not valid" in rich_error.user_friendly_message

    def test_connection_error_message(self):
        """Test user-friendly message for connection errors"""
        manager = EnhancedDebuggingManager()

        error = ConnectionError("Connection failed")
        rich_error = manager.create_rich_error_message(error)

        assert "network connection" in rich_error.user_friendly_message

    def test_timeout_error_message(self):
        """Test user-friendly message for timeout errors"""
        manager = EnhancedDebuggingManager()

        error = TimeoutError("Operation timeout occurred")
        rich_error = manager.create_rich_error_message(error)

        # The error message should contain "timeout" which triggers the timeout message
        assert "too long to complete" in rich_error.user_friendly_message


class TestSuggestedActions:
    """Test suggested actions generation"""

    def test_validation_error_actions(self):
        """Test suggested actions for validation errors"""
        manager = EnhancedDebuggingManager()

        error = ValueError("Validation failed")
        rich_error = manager.create_rich_error_message(error)

        actions = rich_error.suggested_actions
        assert any("format" in action.lower() for action in actions)
        assert any("required fields" in action.lower() for action in actions)

    def test_connection_error_actions(self):
        """Test suggested actions for connection errors"""
        manager = EnhancedDebuggingManager()

        error = ConnectionError("Connection failed")
        rich_error = manager.create_rich_error_message(error)

        actions = rich_error.suggested_actions
        assert any("internet" in action.lower() for action in actions)
        assert any("service" in action.lower() for action in actions)

    def test_timeout_error_actions(self):
        """Test suggested actions for timeout errors"""
        manager = EnhancedDebuggingManager()

        error = TimeoutError("Operation timeout occurred")
        rich_error = manager.create_rich_error_message(error)

        actions = rich_error.suggested_actions
        assert any("smaller" in action.lower() for action in actions)
        assert any("resources" in action.lower() for action in actions)


if __name__ == "__main__":
    pytest.main([__file__])
