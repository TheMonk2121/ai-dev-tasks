#!/usr/bin/env python3
"""
Enhanced Debugging Capabilities for DSPy AI System
Implements rich error messages, context correlation, and structured debugging for B-1007
"""

import functools
import json
import logging
import traceback
from collections.abc import Callable
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .context_models import BaseContext
from .dynamic_prompts import PromptContext
from .error_taxonomy import ErrorSeverity

_LOG = logging.getLogger("enhanced_debugging")

# ---------- Enhanced Debugging Models ----------


class DebuggingContext(BaseModel):
    """Model for debugging context information"""

    context_id: str = Field(..., description="Unique debugging context identifier")
    user_context: PromptContext | None = Field(None, description="User context at time of debugging")
    role_context: BaseContext | None = Field(None, description="Role context at time of debugging")
    execution_stack: list[str] = Field(default_factory=list, description="Execution stack trace")
    variable_snapshot: dict[str, Any] = Field(default_factory=dict, description="Variable state snapshot")
    timestamp: datetime = Field(default_factory=datetime.now, description="Debugging context timestamp")
    correlation_id: str | None = Field(None, description="Correlation ID for tracing")

    @field_validator("context_id")
    @classmethod
    def validate_context_id(cls, v: str) -> str:
        """Validate context ID format"""
        if not v or len(v.strip()) < 3:
            raise ValueError("Context ID must be at least 3 characters")
        return v.strip()


class RichErrorMessage(BaseModel):
    """Model for rich error messages with full context"""

    error_id: str = Field(..., description="Unique error identifier")
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Human-readable error message")
    technical_details: str = Field(..., description="Technical error details")
    user_friendly_message: str = Field(..., description="User-friendly error message")
    debugging_context: DebuggingContext | None = Field(None, description="Debugging context")
    suggested_actions: list[str] = Field(default_factory=list, description="Suggested actions to resolve")
    severity: ErrorSeverity = Field(..., description="Error severity level")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    correlation_data: dict[str, Any] = Field(default_factory=dict, description="Correlation data")

    @field_validator("error_id")
    @classmethod
    def validate_error_id(cls, v: str) -> str:
        """Validate error ID format"""
        if not v or len(v.strip()) < 3:
            raise ValueError("Error ID must be at least 3 characters")
        return v.strip()

    @field_validator("error_message")
    @classmethod
    def validate_error_message(cls, v: str) -> str:
        """Validate error message format"""
        if not v or len(v.strip()) < 5:
            raise ValueError("Error message must be at least 5 characters")
        return v.strip()


class ContextCorrelation(BaseModel):
    """Model for context correlation analysis"""

    correlation_id: str = Field(..., description="Unique correlation identifier")
    primary_context: DebuggingContext = Field(..., description="Primary debugging context")
    related_contexts: list[DebuggingContext] = Field(default_factory=list, description="Related contexts")
    correlation_patterns: list[str] = Field(default_factory=list, description="Identified correlation patterns")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Correlation confidence score")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")

    @field_validator("correlation_id")
    @classmethod
    def validate_correlation_id(cls, v: str) -> str:
        """Validate correlation ID format"""
        if not v or len(v.strip()) < 3:
            raise ValueError("Correlation ID must be at least 3 characters")
        return v.strip()

    @field_validator("confidence_score")
    @classmethod
    def validate_confidence_score(cls, v: float) -> float:
        """Validate confidence score range"""
        if v < 0.0 or v > 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        return v


class StructuredLogEntry(BaseModel):
    """Model for structured log entries"""

    log_id: str = Field(..., description="Unique log entry identifier")
    level: str = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    context_data: dict[str, Any] = Field(default_factory=dict, description="Context data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Log timestamp")
    source: str = Field(..., description="Source of the log entry")
    correlation_id: str | None = Field(None, description="Correlation ID for tracing")

    @field_validator("log_id")
    @classmethod
    def validate_log_id(cls, v: str) -> str:
        """Validate log ID format"""
        if not v or len(v.strip()) < 3:
            raise ValueError("Log ID must be at least 3 characters")
        return v.strip()

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()


# ---------- Enhanced Debugging Manager ----------


class EnhancedDebuggingManager:
    """Manager for enhanced debugging capabilities"""

    def __init__(self, enable_privacy: bool = True, max_context_history: int = 100):
        """Initialize debugging manager"""
        self.enable_privacy = enable_privacy
        self.max_context_history = max_context_history
        self.context_history: list[DebuggingContext] = []
        self.error_history: list[RichErrorMessage] = []
        self.correlation_cache: dict[str, ContextCorrelation] = {}

    def capture_debugging_context(
        self,
        user_context: PromptContext | None = None,
        role_context: BaseContext | None = None,
        variable_snapshot: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> DebuggingContext:
        """Capture debugging context information"""
        import uuid

        # Generate context ID
        context_id = f"debug_{uuid.uuid4().hex[:8]}"

        # Capture execution stack
        execution_stack = self._capture_execution_stack()

        # Sanitize variable snapshot for privacy
        sanitized_snapshot = self._sanitize_variables(variable_snapshot or {})

        # Create debugging context
        debugging_context = DebuggingContext(
            context_id=context_id,
            user_context=user_context,
            role_context=role_context,
            execution_stack=execution_stack,
            variable_snapshot=sanitized_snapshot,
            correlation_id=correlation_id,
        )

        # Store in history
        self._store_context_in_history(debugging_context)

        return debugging_context

    def create_rich_error_message(
        self,
        error: Exception,
        debugging_context: DebuggingContext | None = None,
        user_context: PromptContext | None = None,
        role_context: BaseContext | None = None,
    ) -> RichErrorMessage:
        """Create rich error message with full context"""
        import uuid

        # Generate error ID
        error_id = f"error_{uuid.uuid4().hex[:8]}"

        # Determine error type and severity
        error_type = type(error).__name__
        severity = self._determine_error_severity(error)

        # Create technical details
        technical_details = self._create_technical_details(error)

        # Create user-friendly message
        user_friendly_message = self._create_user_friendly_message(error, error_type)

        # Generate suggested actions
        suggested_actions = self._generate_suggested_actions(error, error_type)

        # Capture debugging context if not provided
        if not debugging_context:
            debugging_context = self.capture_debugging_context(user_context, role_context)

        # Create rich error message
        rich_error = RichErrorMessage(
            error_id=error_id,
            error_type=error_type,
            error_message=str(error),
            technical_details=technical_details,
            user_friendly_message=user_friendly_message,
            debugging_context=debugging_context,
            suggested_actions=suggested_actions,
            severity=severity,
            correlation_data=self._extract_correlation_data(debugging_context),
        )

        # Store in history
        self.error_history.append(rich_error)

        return rich_error

    def correlate_contexts(self, primary_context: DebuggingContext) -> ContextCorrelation:
        """Correlate debugging contexts for analysis"""
        import uuid

        # Generate correlation ID
        correlation_id = f"corr_{uuid.uuid4().hex[:8]}"

        # Find related contexts
        related_contexts = self._find_related_contexts(primary_context)

        # Identify correlation patterns
        correlation_patterns = self._identify_correlation_patterns(primary_context, related_contexts)

        # Calculate confidence score
        confidence_score = self._calculate_correlation_confidence(
            primary_context, related_contexts, correlation_patterns
        )

        # Create context correlation
        correlation = ContextCorrelation(
            correlation_id=correlation_id,
            primary_context=primary_context,
            related_contexts=related_contexts,
            correlation_patterns=correlation_patterns,
            confidence_score=confidence_score,
        )

        # Cache correlation
        self.correlation_cache[correlation_id] = correlation

        return correlation

    def log_structured_entry(
        self,
        level: str,
        message: str,
        context_data: dict[str, Any] | None = None,
        source: str = "enhanced_debugging",
        correlation_id: str | None = None,
    ) -> StructuredLogEntry:
        """Create structured log entry"""
        import uuid

        # Generate log ID
        log_id = f"log_{uuid.uuid4().hex[:8]}"

        # Sanitize context data for privacy
        sanitized_context = self._sanitize_variables(context_data or {})

        # Create structured log entry
        log_entry = StructuredLogEntry(
            log_id=log_id,
            level=level,
            message=message,
            context_data=sanitized_context,
            source=source,
            correlation_id=correlation_id,
        )

        # Log to standard logger
        self._log_to_standard_logger(log_entry)

        return log_entry

    def get_debugging_summary(self) -> dict[str, Any]:
        """Get debugging summary and statistics"""
        return {
            "total_contexts": len(self.context_history),
            "total_errors": len(self.error_history),
            "total_correlations": len(self.correlation_cache),
            "error_distribution": self._get_error_distribution(),
            "context_timeline": self._get_context_timeline(),
            "correlation_insights": self._get_correlation_insights(),
        }

    def _capture_execution_stack(self) -> list[str]:
        """Capture current execution stack"""
        try:
            # Get current stack trace
            stack = traceback.extract_stack()

            # Format stack entries
            stack_entries = []
            for frame in stack[:-1]:  # Exclude this function
                entry = f"{frame.filename}:{frame.lineno} in {frame.name}"
                stack_entries.append(entry)

            return stack_entries
        except Exception:
            return ["Unable to capture stack trace"]

    def _sanitize_variables(self, variables: dict[str, Any]) -> dict[str, Any]:
        """Sanitize variables for privacy and security"""
        if not self.enable_privacy:
            return variables

        sanitized = {}
        sensitive_patterns = ["password", "secret", "key", "token", "auth", "credential"]

        for key, value in variables.items():
            # Check if key contains sensitive patterns
            key_lower = key.lower()
            is_sensitive = any(pattern in key_lower for pattern in sensitive_patterns)

            if is_sensitive:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 100:
                # Truncate long strings
                sanitized[key] = value[:100] + "..."
            elif isinstance(value, dict | list) and len(str(value)) > 200:
                # Truncate large objects
                sanitized[key] = f"[{type(value).__name__} - {len(value)} items]"
            else:
                sanitized[key] = value

        return sanitized

    def _store_context_in_history(self, context: DebuggingContext) -> None:
        """Store context in history with size limit"""
        self.context_history.append(context)

        # Maintain size limit
        if len(self.context_history) > self.max_context_history:
            self.context_history = self.context_history[-self.max_context_history :]

    def _determine_error_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity based on error type and message"""
        error_message = str(error).lower()

        # Critical errors
        if any(critical in error_message for critical in ["security", "authentication", "authorization"]):
            return ErrorSeverity.CRITICAL

        # High severity errors
        if any(high in error_message for high in ["database", "connection", "timeout", "memory"]):
            return ErrorSeverity.HIGH

        # Medium severity errors
        if any(medium in error_message for medium in ["validation", "format", "parsing"]):
            return ErrorSeverity.MEDIUM

        # Default to low severity
        return ErrorSeverity.LOW

    def _create_technical_details(self, error: Exception) -> str:
        """Create technical details for error"""
        details = []

        # Error type and message
        details.append(f"Error Type: {type(error).__name__}")
        details.append(f"Error Message: {str(error)}")

        # Stack trace
        details.append("Stack Trace:")
        details.append(traceback.format_exc())

        # Additional context
        details.append(f"Timestamp: {datetime.now().isoformat()}")

        return "\n".join(details)

    def _create_user_friendly_message(self, error: Exception, error_type: str) -> str:
        """Create user-friendly error message"""
        error_message = str(error).lower()

        # Map error types to user-friendly messages
        if "validation" in error_message:
            return "The provided data format is not valid. Please check your input and try again."
        elif "connection" in error_message:
            return "Unable to connect to the required service. Please check your network connection and try again."
        elif "timeout" in error_message:
            return "The operation took too long to complete. Please try again with a smaller request."
        elif "permission" in error_message:
            return "You don't have permission to perform this action. Please contact your administrator."
        elif "not found" in error_message:
            return "The requested resource was not found. Please check your input and try again."
        else:
            return f"An unexpected error occurred: {error_type}. Please try again or contact support if the problem persists."

    def _generate_suggested_actions(self, error: Exception, error_type: str) -> list[str]:
        """Generate suggested actions to resolve the error"""
        error_message = str(error).lower()
        actions = []

        # Common suggested actions based on error type
        if "validation" in error_message:
            actions.extend(
                [
                    "Check the format of your input data",
                    "Ensure all required fields are provided",
                    "Verify data types match expected formats",
                ]
            )
        elif "connection" in error_message:
            actions.extend(
                ["Check your internet connection", "Verify the service is available", "Try again in a few minutes"]
            )
        elif "timeout" in error_message:
            actions.extend(
                ["Try with a smaller dataset", "Check system resources", "Contact support if the problem persists"]
            )
        elif "permission" in error_message:
            actions.extend(
                [
                    "Contact your system administrator",
                    "Verify your account permissions",
                    "Check if you need additional access",
                ]
            )
        else:
            actions.extend(
                [
                    "Try the operation again",
                    "Check the system logs for more details",
                    "Contact support with the error details",
                ]
            )

        return actions

    def _extract_correlation_data(self, debugging_context: DebuggingContext) -> dict[str, Any]:
        """Extract correlation data from debugging context"""
        correlation_data = {
            "context_id": debugging_context.context_id,
            "timestamp": debugging_context.timestamp.isoformat(),
            "correlation_id": debugging_context.correlation_id,
        }

        if debugging_context.user_context:
            correlation_data["user_id"] = debugging_context.user_context.user_id
            correlation_data["session_id"] = debugging_context.user_context.session_id

        if debugging_context.role_context:
            correlation_data["role"] = debugging_context.role_context.role.value

        return correlation_data

    def _find_related_contexts(self, primary_context: DebuggingContext) -> list[DebuggingContext]:
        """Find related debugging contexts"""
        related_contexts = []

        for context in self.context_history:
            if context.context_id == primary_context.context_id:
                continue

            # Check for temporal proximity (within 5 minutes)
            time_diff = abs((primary_context.timestamp - context.timestamp).total_seconds())
            if time_diff <= 300:  # 5 minutes
                related_contexts.append(context)

            # Check for user correlation
            if (
                primary_context.user_context
                and context.user_context
                and primary_context.user_context.user_id == context.user_context.user_id
            ):
                related_contexts.append(context)

            # Check for role correlation
            if (
                primary_context.role_context
                and context.role_context
                and primary_context.role_context.role == context.role_context.role
            ):
                related_contexts.append(context)

        return related_contexts

    def _identify_correlation_patterns(
        self, primary_context: DebuggingContext, related_contexts: list[DebuggingContext]
    ) -> list[str]:
        """Identify correlation patterns between contexts"""
        patterns = []

        if not related_contexts:
            return patterns

        # Check for temporal patterns
        timestamps = [ctx.timestamp for ctx in related_contexts]
        if len(timestamps) > 1:
            time_diffs = [abs((timestamps[i] - timestamps[i - 1]).total_seconds()) for i in range(1, len(timestamps))]
            avg_time_diff = sum(time_diffs) / len(time_diffs)
            if avg_time_diff < 60:  # Less than 1 minute average
                patterns.append("rapid_succession")

        # Check for user patterns
        user_contexts = [ctx for ctx in related_contexts if ctx.user_context]
        if len(user_contexts) > 2:
            patterns.append("user_activity_cluster")

        # Check for role patterns
        role_contexts = [ctx for ctx in related_contexts if ctx.role_context]
        if len(role_contexts) > 2:
            patterns.append("role_activity_cluster")

        # Check for error patterns
        error_contexts = [
            ctx for ctx in related_contexts if any("error" in str(v).lower() for v in ctx.variable_snapshot.values())
        ]
        if len(error_contexts) > 1:
            patterns.append("error_cascade")

        return patterns

    def _calculate_correlation_confidence(
        self, primary_context: DebuggingContext, related_contexts: list[DebuggingContext], patterns: list[str]
    ) -> float:
        """Calculate correlation confidence score"""
        if not related_contexts:
            return 0.0

        # Base confidence from number of related contexts
        base_confidence = min(len(related_contexts) / 10.0, 0.5)  # Max 0.5 from context count

        # Pattern confidence
        pattern_confidence = len(patterns) * 0.1  # 0.1 per pattern, max 0.3

        # Temporal confidence
        temporal_confidence = 0.0
        if related_contexts:
            time_diffs = [abs((primary_context.timestamp - ctx.timestamp).total_seconds()) for ctx in related_contexts]
            avg_time_diff = sum(time_diffs) / len(time_diffs)
            if avg_time_diff < 60:  # Less than 1 minute
                temporal_confidence = 0.2
            elif avg_time_diff < 300:  # Less than 5 minutes
                temporal_confidence = 0.1

        total_confidence = base_confidence + pattern_confidence + temporal_confidence
        return min(total_confidence, 1.0)

    def _log_to_standard_logger(self, log_entry: StructuredLogEntry) -> None:
        """Log to standard logger"""
        log_message = f"[{log_entry.source}] {log_entry.message}"

        if log_entry.context_data:
            log_message += f" | Context: {json.dumps(log_entry.context_data, default=str)}"

        if log_entry.correlation_id:
            log_message += f" | Correlation: {log_entry.correlation_id}"

        # Log to appropriate level
        if log_entry.level == "DEBUG":
            _LOG.debug(log_message)
        elif log_entry.level == "INFO":
            _LOG.info(log_message)
        elif log_entry.level == "WARNING":
            _LOG.warning(log_message)
        elif log_entry.level == "ERROR":
            _LOG.error(log_message)
        elif log_entry.level == "CRITICAL":
            _LOG.critical(log_message)

    def _get_error_distribution(self) -> dict[str, int]:
        """Get error distribution by type"""
        distribution = {}
        for error in self.error_history:
            error_type = error.error_type
            distribution[error_type] = distribution.get(error_type, 0) + 1
        return distribution

    def _get_context_timeline(self) -> list[dict[str, Any]]:
        """Get context timeline"""
        timeline = []
        for context in self.context_history[-20:]:  # Last 20 contexts
            timeline.append(
                {
                    "timestamp": context.timestamp.isoformat(),
                    "context_id": context.context_id,
                    "has_user_context": context.user_context is not None,
                    "has_role_context": context.role_context is not None,
                }
            )
        return timeline

    def _get_correlation_insights(self) -> dict[str, Any]:
        """Get correlation insights"""
        if not self.correlation_cache:
            return {"message": "No correlations found"}

        insights = {
            "total_correlations": len(self.correlation_cache),
            "avg_confidence": sum(corr.confidence_score for corr in self.correlation_cache.values())
            / len(self.correlation_cache),
            "common_patterns": {},
        }

        # Count common patterns
        for correlation in self.correlation_cache.values():
            for pattern in correlation.correlation_patterns:
                insights["common_patterns"][pattern] = insights["common_patterns"].get(pattern, 0) + 1

        return insights


# ---------- Debugging Decorators ----------


def enhanced_debugging(enable_privacy: bool = True, capture_variables: bool = True):
    """Decorator for enhanced debugging capabilities"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            debugging_manager = EnhancedDebuggingManager(enable_privacy=enable_privacy)

            # Capture initial context
            initial_context = debugging_manager.capture_debugging_context(
                variable_snapshot={"args": str(args), "kwargs": str(kwargs)} if capture_variables else {}
            )

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Log success
                debugging_manager.log_structured_entry(
                    level="INFO",
                    message=f"Function {func.__name__} executed successfully",
                    context_data={"function": func.__name__, "result_type": type(result).__name__},
                    source="enhanced_debugging",
                )

                return result

            except Exception as e:
                # Create rich error message
                rich_error = debugging_manager.create_rich_error_message(error=e, debugging_context=initial_context)

                # Log error
                debugging_manager.log_structured_entry(
                    level="ERROR",
                    message=f"Function {func.__name__} failed: {rich_error.user_friendly_message}",
                    context_data={"error_id": rich_error.error_id, "error_type": rich_error.error_type},
                    source="enhanced_debugging",
                )

                # Re-raise with rich context
                raise type(e)(f"{rich_error.user_friendly_message} (Error ID: {rich_error.error_id})") from e

        return wrapper

    return decorator


# ---------- Context Correlation Utilities ----------


def correlate_errors(error_messages: list[RichErrorMessage]) -> list[ContextCorrelation]:
    """Correlate multiple error messages for analysis"""
    debugging_manager = EnhancedDebuggingManager()
    correlations = []

    for error in error_messages:
        if error.debugging_context:
            correlation = debugging_manager.correlate_contexts(error.debugging_context)
            correlations.append(correlation)

    return correlations


def analyze_error_patterns(error_messages: list[RichErrorMessage]) -> dict[str, Any]:
    """Analyze patterns in error messages"""
    if not error_messages:
        return {"message": "No error messages to analyze"}

    analysis = {
        "total_errors": len(error_messages),
        "error_types": {},
        "severity_distribution": {},
        "temporal_patterns": {},
        "common_contexts": {},
    }

    # Analyze error types
    for error in error_messages:
        error_type = error.error_type
        analysis["error_types"][error_type] = analysis["error_types"].get(error_type, 0) + 1

    # Analyze severity distribution
    for error in error_messages:
        severity = error.severity.value
        analysis["severity_distribution"][severity] = analysis["severity_distribution"].get(severity, 0) + 1

    # Analyze temporal patterns
    timestamps = [error.timestamp for error in error_messages]
    if len(timestamps) > 1:
        time_diffs = [(timestamps[i] - timestamps[i - 1]).total_seconds() for i in range(1, len(timestamps))]
        analysis["temporal_patterns"] = {
            "avg_time_between_errors": sum(time_diffs) / len(time_diffs),
            "min_time_between_errors": min(time_diffs),
            "max_time_between_errors": max(time_diffs),
        }

    # Analyze common contexts
    for error in error_messages:
        if error.debugging_context and error.debugging_context.user_context:
            user_id = error.debugging_context.user_context.user_id
            analysis["common_contexts"][user_id] = analysis["common_contexts"].get(user_id, 0) + 1

    return analysis
