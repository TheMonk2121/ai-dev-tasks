#!/usr/bin/env python3
"""
Error Taxonomy for DSPy AI System
Implements structured error taxonomy with constitution mapping for B-1007
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

_LOG = logging.getLogger("error_taxonomy")

# ---------- Error Types ----------


class ErrorType(Enum):
    """Error types for structured error taxonomy"""

    VALIDATION_ERROR = "validation_error"
    COHERENCE_ERROR = "coherence_error"
    DEPENDENCY_ERROR = "dependency_error"
    RUNTIME_ERROR = "runtime_error"
    CONFIGURATION_ERROR = "configuration_error"
    SECURITY_ERROR = "security_error"


class ErrorSeverity(Enum):
    """Error severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ---------- Base Error Models ----------


class PydanticError(BaseModel):
    """Base error model for structured error taxonomy"""

    error_type: ErrorType = Field(..., description="Type of error")
    severity: ErrorSeverity = Field(..., description="Error severity level")
    message: str = Field(..., description="Human-readable error message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error occurrence timestamp")
    context: dict[str, Any] = Field(default_factory=dict, description="Error context information")
    stack_trace: str | None = Field(None, description="Stack trace if available")
    error_code: str | None = Field(None, description="Error code for programmatic handling")

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate error message is meaningful"""
        if not v or len(v.strip()) < 5:
            raise ValueError("Error message must be at least 5 characters")
        return v.strip()

    @field_validator("error_code")
    @classmethod
    def validate_error_code(cls, v: str | None) -> str | None:
        """Validate error code format"""
        if v is not None:
            if not v.strip() or len(v.strip()) < 3:
                raise ValueError("Error code must be at least 3 characters")
            return v.strip().upper()
        return v


# ---------- Specific Error Models ----------


class ValidationError(PydanticError):
    """Validation error for input/output validation failures"""

    error_type: ErrorType = Field(default=ErrorType.VALIDATION_ERROR, description="Validation error")
    field_name: str | None = Field(None, description="Field that failed validation")
    expected_value: str | None = Field(None, description="Expected value or format")
    actual_value: str | None = Field(None, description="Actual value that failed validation")
    validation_rule: str | None = Field(None, description="Validation rule that was violated")

    @field_validator("field_name")
    @classmethod
    def validate_field_name(cls, v: str | None) -> str | None:
        """Validate field name format"""
        if v is not None and not v.strip():
            raise ValueError("Field name cannot be empty")
        return v.strip() if v else v


class CoherenceError(PydanticError):
    """Coherence error for logical consistency failures"""

    error_type: ErrorType = Field(default=ErrorType.COHERENCE_ERROR, description="Coherence error")
    conflicting_elements: list[str] = Field(default_factory=list, description="Elements that are in conflict")
    coherence_rule: str | None = Field(None, description="Coherence rule that was violated")
    suggested_resolution: str | None = Field(None, description="Suggested resolution approach")

    @field_validator("conflicting_elements")
    @classmethod
    def validate_conflicting_elements(cls, v: list[str]) -> list[str]:
        """Validate conflicting elements list"""
        return [elem.strip() for elem in v if elem.strip()]


class DependencyError(PydanticError):
    """Dependency error for missing or incompatible dependencies"""

    error_type: ErrorType = Field(default=ErrorType.DEPENDENCY_ERROR, description="Dependency error")
    missing_dependencies: list[str] = Field(default_factory=list, description="Missing dependencies")
    incompatible_dependencies: list[str] = Field(default_factory=list, description="Incompatible dependencies")
    dependency_type: str | None = Field(None, description="Type of dependency (module, service, etc.)")
    resolution_steps: list[str] = Field(default_factory=list, description="Steps to resolve dependency issues")

    @field_validator("missing_dependencies")
    @classmethod
    def validate_missing_dependencies(cls, v: list[str]) -> list[str]:
        """Validate missing dependencies list"""
        return [dep.strip() for dep in v if dep.strip()]

    @field_validator("incompatible_dependencies")
    @classmethod
    def validate_incompatible_dependencies(cls, v: list[str]) -> list[str]:
        """Validate incompatible dependencies list"""
        return [dep.strip() for dep in v if dep.strip()]


class RuntimeError(PydanticError):
    """Runtime error for execution-time failures"""

    error_type: ErrorType = Field(default=ErrorType.RUNTIME_ERROR, description="Runtime error")
    operation: str | None = Field(None, description="Operation that failed")
    resource: str | None = Field(None, description="Resource that caused the error")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")

    @field_validator("retry_count")
    @classmethod
    def validate_retry_count(cls, v: int) -> int:
        """Validate retry count is non-negative"""
        if v < 0:
            raise ValueError("Retry count cannot be negative")
        return v

    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        """Validate max retries is positive"""
        if v <= 0:
            raise ValueError("Max retries must be positive")
        return v


class ConfigurationError(PydanticError):
    """Configuration error for setup and configuration failures"""

    error_type: ErrorType = Field(default=ErrorType.CONFIGURATION_ERROR, description="Configuration error")
    config_file: str | None = Field(None, description="Configuration file that caused the error")
    config_section: str | None = Field(None, description="Configuration section with the error")
    missing_config: list[str] = Field(default_factory=list, description="Missing configuration items")
    invalid_config: list[str] = Field(default_factory=list, description="Invalid configuration items")

    @field_validator("missing_config")
    @classmethod
    def validate_missing_config(cls, v: list[str]) -> list[str]:
        """Validate missing config list"""
        return [config.strip() for config in v if config.strip()]

    @field_validator("invalid_config")
    @classmethod
    def validate_invalid_config(cls, v: list[str]) -> list[str]:
        """Validate invalid config list"""
        return [config.strip() for config in v if config.strip()]


class SecurityError(PydanticError):
    """Security error for security-related failures"""

    error_type: ErrorType = Field(default=ErrorType.SECURITY_ERROR, description="Security error")
    security_violation: str | None = Field(None, description="Type of security violation")
    affected_resource: str | None = Field(None, description="Resource affected by security issue")
    threat_level: str | None = Field(None, description="Threat level assessment")
    mitigation_steps: list[str] = Field(default_factory=list, description="Steps to mitigate security issue")

    @field_validator("mitigation_steps")
    @classmethod
    def validate_mitigation_steps(cls, v: list[str]) -> list[str]:
        """Validate mitigation steps list"""
        return [step.strip() for step in v if step.strip()]


# ---------- Error Factory ----------


class ErrorFactory:
    """Factory for creating structured error models"""

    @staticmethod
    def create_validation_error(
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        field_name: str | None = None,
        expected_value: str | None = None,
        actual_value: str | None = None,
        validation_rule: str | None = None,
        **kwargs,
    ) -> ValidationError:
        """Create a validation error"""
        return ValidationError(
            severity=severity,
            message=message,
            field_name=field_name,
            expected_value=expected_value,
            actual_value=actual_value,
            validation_rule=validation_rule,
            **kwargs,
        )

    @staticmethod
    def create_coherence_error(
        message: str,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        conflicting_elements: list[str] | None = None,
        coherence_rule: str | None = None,
        suggested_resolution: str | None = None,
        **kwargs,
    ) -> CoherenceError:
        """Create a coherence error"""
        return CoherenceError(
            severity=severity,
            message=message,
            conflicting_elements=conflicting_elements or [],
            coherence_rule=coherence_rule,
            suggested_resolution=suggested_resolution,
            **kwargs,
        )

    @staticmethod
    def create_dependency_error(
        message: str,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        missing_dependencies: list[str] | None = None,
        incompatible_dependencies: list[str] | None = None,
        dependency_type: str | None = None,
        resolution_steps: list[str] | None = None,
        **kwargs,
    ) -> DependencyError:
        """Create a dependency error"""
        return DependencyError(
            severity=severity,
            message=message,
            missing_dependencies=missing_dependencies or [],
            incompatible_dependencies=incompatible_dependencies or [],
            dependency_type=dependency_type,
            resolution_steps=resolution_steps or [],
            **kwargs,
        )

    @staticmethod
    def create_runtime_error(
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        operation: str | None = None,
        resource: str | None = None,
        retry_count: int = 0,
        max_retries: int = 3,
        **kwargs,
    ) -> RuntimeError:
        """Create a runtime error"""
        return RuntimeError(
            severity=severity,
            message=message,
            operation=operation,
            resource=resource,
            retry_count=retry_count,
            max_retries=max_retries,
            **kwargs,
        )

    @staticmethod
    def create_configuration_error(
        message: str,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        config_file: str | None = None,
        config_section: str | None = None,
        missing_config: list[str] | None = None,
        invalid_config: list[str] | None = None,
        **kwargs,
    ) -> ConfigurationError:
        """Create a configuration error"""
        return ConfigurationError(
            severity=severity,
            message=message,
            config_file=config_file,
            config_section=config_section,
            missing_config=missing_config or [],
            invalid_config=invalid_config or [],
            **kwargs,
        )

    @staticmethod
    def create_security_error(
        message: str,
        severity: ErrorSeverity = ErrorSeverity.CRITICAL,
        security_violation: str | None = None,
        affected_resource: str | None = None,
        threat_level: str | None = None,
        mitigation_steps: list[str] | None = None,
        **kwargs,
    ) -> SecurityError:
        """Create a security error"""
        return SecurityError(
            severity=severity,
            message=message,
            security_violation=security_violation,
            affected_resource=affected_resource,
            threat_level=threat_level,
            mitigation_steps=mitigation_steps or [],
            **kwargs,
        )


# ---------- Constitution Mapping ----------


class ConstitutionErrorMapper:
    """Maps constitution failure modes to error types"""

    # Mapping from constitution failure modes to error types
    CONSTITUTION_ERROR_MAPPING = {
        "validation_failure": ErrorType.VALIDATION_ERROR,
        "coherence_violation": ErrorType.COHERENCE_ERROR,
        "dependency_missing": ErrorType.DEPENDENCY_ERROR,
        "runtime_exception": ErrorType.RUNTIME_ERROR,
        "configuration_invalid": ErrorType.CONFIGURATION_ERROR,
        "security_violation": ErrorType.SECURITY_ERROR,
    }

    @staticmethod
    def map_constitution_failure_to_error(
        failure_mode: str, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, **kwargs
    ) -> PydanticError:
        """Map constitution failure mode to appropriate error type"""

        error_type = ConstitutionErrorMapper.CONSTITUTION_ERROR_MAPPING.get(failure_mode, ErrorType.RUNTIME_ERROR)

        error_factories = {
            ErrorType.VALIDATION_ERROR: ErrorFactory.create_validation_error,
            ErrorType.COHERENCE_ERROR: ErrorFactory.create_coherence_error,
            ErrorType.DEPENDENCY_ERROR: ErrorFactory.create_dependency_error,
            ErrorType.RUNTIME_ERROR: ErrorFactory.create_runtime_error,
            ErrorType.CONFIGURATION_ERROR: ErrorFactory.create_configuration_error,
            ErrorType.SECURITY_ERROR: ErrorFactory.create_security_error,
        }

        factory = error_factories.get(error_type, ErrorFactory.create_runtime_error)
        return factory(message=message, severity=severity, **kwargs)

    @staticmethod
    def get_error_classification_stats(errors: list[PydanticError]) -> dict[str, int]:
        """Get statistics on error classification"""
        stats = {}
        for error in errors:
            error_type = error.error_type.value
            stats[error_type] = stats.get(error_type, 0) + 1
        return stats


# ---------- Error Classification ----------


class ErrorClassifier:
    """Classifies errors for measurable improvement in error handling"""

    @staticmethod
    def classify_error_by_severity(errors: list[PydanticError]) -> dict[ErrorSeverity, list[PydanticError]]:
        """Classify errors by severity level"""
        classification = {}
        for error in errors:
            severity = error.severity
            if severity not in classification:
                classification[severity] = []
            classification[severity].append(error)
        return classification

    @staticmethod
    def classify_error_by_type(errors: list[PydanticError]) -> dict[ErrorType, list[PydanticError]]:
        """Classify errors by error type"""
        classification = {}
        for error in errors:
            error_type = error.error_type
            if error_type not in classification:
                classification[error_type] = []
            classification[error_type].append(error)
        return classification

    @staticmethod
    def get_error_handling_metrics(errors: list[PydanticError]) -> dict[str, Any]:
        """Get comprehensive error handling metrics"""
        if not errors:
            return {
                "total_errors": 0,
                "error_types": {},
                "severity_distribution": {},
                "avg_severity_score": 0.0,
                "most_common_error_type": None,
                "critical_errors_count": 0,
            }

        # Basic counts
        total_errors = len(errors)

        # Error type distribution
        error_types = ConstitutionErrorMapper.get_error_classification_stats(errors)

        # Severity distribution
        severity_distribution = {}
        severity_scores = {
            ErrorSeverity.LOW: 1,
            ErrorSeverity.MEDIUM: 2,
            ErrorSeverity.HIGH: 3,
            ErrorSeverity.CRITICAL: 4,
        }
        total_severity_score = 0

        for error in errors:
            severity = error.severity
            severity_distribution[severity.value] = severity_distribution.get(severity.value, 0) + 1
            total_severity_score += severity_scores[severity]

        avg_severity_score = total_severity_score / total_errors

        # Most common error type
        most_common_error_type = max(error_types.items(), key=lambda x: x[1])[0] if error_types else None

        # Critical errors count
        critical_errors_count = len([e for e in errors if e.severity == ErrorSeverity.CRITICAL])

        return {
            "total_errors": total_errors,
            "error_types": error_types,
            "severity_distribution": severity_distribution,
            "avg_severity_score": avg_severity_score,
            "most_common_error_type": most_common_error_type,
            "critical_errors_count": critical_errors_count,
        }
