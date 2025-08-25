#!/usr/bin/env python3
"""
Tests for Error Taxonomy Models
Validates structured error taxonomy for B-1007
"""

import pytest

from src.dspy_modules.error_taxonomy import (
    CoherenceError,
    ConfigurationError,
    ConstitutionErrorMapper,
    DependencyError,
    ErrorClassifier,
    ErrorFactory,
    ErrorSeverity,
    ErrorType,
    PydanticError,
    RuntimeError,
    SecurityError,
    ValidationError,
)


class TestPydanticError:
    """Test base error model functionality"""

    def test_base_error_creation(self):
        """Test basic error creation"""
        error = PydanticError(
            error_type=ErrorType.VALIDATION_ERROR, severity=ErrorSeverity.MEDIUM, message="Test error message"
        )

        assert error.error_type == ErrorType.VALIDATION_ERROR
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.message == "Test error message"
        assert error.context == {}

    def test_error_message_validation(self):
        """Test error message validation"""
        # Valid message
        error = PydanticError(
            error_type=ErrorType.VALIDATION_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message="Valid error message with sufficient detail",
        )
        assert len(error.message) >= 5

        # Invalid message (too short)
        with pytest.raises(ValueError, match="Error message must be at least 5 characters"):
            PydanticError(error_type=ErrorType.VALIDATION_ERROR, severity=ErrorSeverity.MEDIUM, message="Hi")

    def test_error_code_validation(self):
        """Test error code validation"""
        # Valid error code
        error = PydanticError(
            error_type=ErrorType.VALIDATION_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message="Test error message",
            error_code="VAL001",
        )
        assert error.error_code == "VAL001"

        # Invalid error code (too short)
        with pytest.raises(ValueError, match="Error code must be at least 3 characters"):
            PydanticError(
                error_type=ErrorType.VALIDATION_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message="Test error message",
                error_code="AB",
            )


class TestValidationError:
    """Test validation error model"""

    def test_validation_error_creation(self):
        """Test validation error creation"""
        error = ValidationError(
            severity=ErrorSeverity.MEDIUM,
            message="Field validation failed",
            field_name="test_field",
            expected_value="string",
            actual_value="123",
            validation_rule="type_check",
        )

        assert error.error_type == ErrorType.VALIDATION_ERROR
        assert error.field_name == "test_field"
        assert error.expected_value == "string"
        assert error.actual_value == "123"
        assert error.validation_rule == "type_check"

    def test_field_name_validation(self):
        """Test field name validation"""
        # Valid field name
        error = ValidationError(
            severity=ErrorSeverity.MEDIUM, message="Test validation error", field_name="valid_field_name"
        )
        assert error.field_name == "valid_field_name"

        # Invalid field name (empty)
        with pytest.raises(ValueError, match="Field name cannot be empty"):
            ValidationError(severity=ErrorSeverity.MEDIUM, message="Test validation error", field_name="")


class TestCoherenceError:
    """Test coherence error model"""

    def test_coherence_error_creation(self):
        """Test coherence error creation"""
        error = CoherenceError(
            severity=ErrorSeverity.HIGH,
            message="Logical inconsistency detected",
            conflicting_elements=["element1", "element2"],
            coherence_rule="mutual_exclusion",
            suggested_resolution="Remove one of the conflicting elements",
        )

        assert error.error_type == ErrorType.COHERENCE_ERROR
        assert error.conflicting_elements == ["element1", "element2"]
        assert error.coherence_rule == "mutual_exclusion"
        assert error.suggested_resolution == "Remove one of the conflicting elements"

    def test_conflicting_elements_validation(self):
        """Test conflicting elements validation"""
        error = CoherenceError(
            severity=ErrorSeverity.HIGH,
            message="Test coherence error",
            conflicting_elements=["  element1  ", "", "element2", "  "],
        )

        # Should filter out empty elements and strip whitespace
        assert error.conflicting_elements == ["element1", "element2"]


class TestDependencyError:
    """Test dependency error model"""

    def test_dependency_error_creation(self):
        """Test dependency error creation"""
        error = DependencyError(
            severity=ErrorSeverity.HIGH,
            message="Missing required dependencies",
            missing_dependencies=["module1", "module2"],
            incompatible_dependencies=["module3"],
            dependency_type="python_module",
            resolution_steps=["Install module1", "Update module3"],
        )

        assert error.error_type == ErrorType.DEPENDENCY_ERROR
        assert error.missing_dependencies == ["module1", "module2"]
        assert error.incompatible_dependencies == ["module3"]
        assert error.dependency_type == "python_module"
        assert error.resolution_steps == ["Install module1", "Update module3"]


class TestRuntimeError:
    """Test runtime error model"""

    def test_runtime_error_creation(self):
        """Test runtime error creation"""
        error = RuntimeError(
            severity=ErrorSeverity.MEDIUM,
            message="Operation failed during execution",
            operation="database_query",
            resource="postgresql_connection",
            retry_count=2,
            max_retries=5,
        )

        assert error.error_type == ErrorType.RUNTIME_ERROR
        assert error.operation == "database_query"
        assert error.resource == "postgresql_connection"
        assert error.retry_count == 2
        assert error.max_retries == 5

    def test_retry_count_validation(self):
        """Test retry count validation"""
        # Valid retry count
        error = RuntimeError(severity=ErrorSeverity.MEDIUM, message="Test runtime error", retry_count=0)
        assert error.retry_count == 0

        # Invalid retry count (negative)
        with pytest.raises(ValueError, match="Retry count cannot be negative"):
            RuntimeError(severity=ErrorSeverity.MEDIUM, message="Test runtime error", retry_count=-1)

    def test_max_retries_validation(self):
        """Test max retries validation"""
        # Valid max retries
        error = RuntimeError(severity=ErrorSeverity.MEDIUM, message="Test runtime error", max_retries=3)
        assert error.max_retries == 3

        # Invalid max retries (zero)
        with pytest.raises(ValueError, match="Max retries must be positive"):
            RuntimeError(severity=ErrorSeverity.MEDIUM, message="Test runtime error", max_retries=0)


class TestConfigurationError:
    """Test configuration error model"""

    def test_configuration_error_creation(self):
        """Test configuration error creation"""
        error = ConfigurationError(
            severity=ErrorSeverity.HIGH,
            message="Invalid configuration detected",
            config_file="config.yaml",
            config_section="database",
            missing_config=["host", "port"],
            invalid_config=["timeout"],
        )

        assert error.error_type == ErrorType.CONFIGURATION_ERROR
        assert error.config_file == "config.yaml"
        assert error.config_section == "database"
        assert error.missing_config == ["host", "port"]
        assert error.invalid_config == ["timeout"]


class TestSecurityError:
    """Test security error model"""

    def test_security_error_creation(self):
        """Test security error creation"""
        error = SecurityError(
            severity=ErrorSeverity.CRITICAL,
            message="Security violation detected",
            security_violation="unauthorized_access",
            affected_resource="user_database",
            threat_level="high",
            mitigation_steps=["Block IP", "Review logs", "Update firewall"],
        )

        assert error.error_type == ErrorType.SECURITY_ERROR
        assert error.security_violation == "unauthorized_access"
        assert error.affected_resource == "user_database"
        assert error.threat_level == "high"
        assert error.mitigation_steps == ["Block IP", "Review logs", "Update firewall"]


class TestErrorFactory:
    """Test error factory functionality"""

    def test_create_validation_error(self):
        """Test creating validation error via factory"""
        error = ErrorFactory.create_validation_error(
            message="Field validation failed", field_name="test_field", expected_value="string", actual_value="123"
        )

        assert isinstance(error, ValidationError)
        assert error.error_type == ErrorType.VALIDATION_ERROR
        assert error.field_name == "test_field"
        assert error.expected_value == "string"
        assert error.actual_value == "123"

    def test_create_coherence_error(self):
        """Test creating coherence error via factory"""
        error = ErrorFactory.create_coherence_error(
            message="Logical inconsistency detected",
            conflicting_elements=["element1", "element2"],
            coherence_rule="mutual_exclusion",
        )

        assert isinstance(error, CoherenceError)
        assert error.error_type == ErrorType.COHERENCE_ERROR
        assert error.conflicting_elements == ["element1", "element2"]
        assert error.coherence_rule == "mutual_exclusion"

    def test_create_dependency_error(self):
        """Test creating dependency error via factory"""
        error = ErrorFactory.create_dependency_error(
            message="Missing dependencies", missing_dependencies=["module1"], dependency_type="python_module"
        )

        assert isinstance(error, DependencyError)
        assert error.error_type == ErrorType.DEPENDENCY_ERROR
        assert error.missing_dependencies == ["module1"]
        assert error.dependency_type == "python_module"

    def test_create_runtime_error(self):
        """Test creating runtime error via factory"""
        error = ErrorFactory.create_runtime_error(message="Operation failed", operation="database_query", retry_count=1)

        assert isinstance(error, RuntimeError)
        assert error.error_type == ErrorType.RUNTIME_ERROR
        assert error.operation == "database_query"
        assert error.retry_count == 1

    def test_create_configuration_error(self):
        """Test creating configuration error via factory"""
        error = ErrorFactory.create_configuration_error(
            message="Invalid configuration", config_file="config.yaml", missing_config=["host"]
        )

        assert isinstance(error, ConfigurationError)
        assert error.error_type == ErrorType.CONFIGURATION_ERROR
        assert error.config_file == "config.yaml"
        assert error.missing_config == ["host"]

    def test_create_security_error(self):
        """Test creating security error via factory"""
        error = ErrorFactory.create_security_error(
            message="Security violation", security_violation="unauthorized_access", threat_level="high"
        )

        assert isinstance(error, SecurityError)
        assert error.error_type == ErrorType.SECURITY_ERROR
        assert error.security_violation == "unauthorized_access"
        assert error.threat_level == "high"


class TestConstitutionErrorMapper:
    """Test constitution error mapping"""

    def test_map_validation_failure(self):
        """Test mapping validation failure to error"""
        error = ConstitutionErrorMapper.map_constitution_failure_to_error(
            failure_mode="validation_failure", message="Input validation failed"
        )

        assert isinstance(error, ValidationError)
        assert error.error_type == ErrorType.VALIDATION_ERROR

    def test_map_coherence_violation(self):
        """Test mapping coherence violation to error"""
        error = ConstitutionErrorMapper.map_constitution_failure_to_error(
            failure_mode="coherence_violation", message="Logical inconsistency detected"
        )

        assert isinstance(error, CoherenceError)
        assert error.error_type == ErrorType.COHERENCE_ERROR

    def test_map_dependency_missing(self):
        """Test mapping dependency missing to error"""
        error = ConstitutionErrorMapper.map_constitution_failure_to_error(
            failure_mode="dependency_missing", message="Required dependency not found"
        )

        assert isinstance(error, DependencyError)
        assert error.error_type == ErrorType.DEPENDENCY_ERROR

    def test_map_runtime_exception(self):
        """Test mapping runtime exception to error"""
        error = ConstitutionErrorMapper.map_constitution_failure_to_error(
            failure_mode="runtime_exception", message="Runtime error occurred"
        )

        assert isinstance(error, RuntimeError)
        assert error.error_type == ErrorType.RUNTIME_ERROR

    def test_map_configuration_invalid(self):
        """Test mapping configuration invalid to error"""
        error = ConstitutionErrorMapper.map_constitution_failure_to_error(
            failure_mode="configuration_invalid", message="Configuration is invalid"
        )

        assert isinstance(error, ConfigurationError)
        assert error.error_type == ErrorType.CONFIGURATION_ERROR

    def test_map_security_violation(self):
        """Test mapping security violation to error"""
        error = ConstitutionErrorMapper.map_constitution_failure_to_error(
            failure_mode="security_violation", message="Security violation detected"
        )

        assert isinstance(error, SecurityError)
        assert error.error_type == ErrorType.SECURITY_ERROR

    def test_map_unknown_failure_mode(self):
        """Test mapping unknown failure mode to runtime error"""
        error = ConstitutionErrorMapper.map_constitution_failure_to_error(
            failure_mode="unknown_failure", message="Unknown failure occurred"
        )

        assert isinstance(error, RuntimeError)
        assert error.error_type == ErrorType.RUNTIME_ERROR

    def test_get_error_classification_stats(self):
        """Test error classification statistics"""
        errors = [
            ValidationError(severity=ErrorSeverity.MEDIUM, message="Error 1"),
            ValidationError(severity=ErrorSeverity.HIGH, message="Error 2"),
            CoherenceError(severity=ErrorSeverity.HIGH, message="Error 3"),
            RuntimeError(severity=ErrorSeverity.LOW, message="Error 4"),
        ]

        stats = ConstitutionErrorMapper.get_error_classification_stats(errors)

        assert stats["validation_error"] == 2
        assert stats["coherence_error"] == 1
        assert stats["runtime_error"] == 1


class TestErrorClassifier:
    """Test error classification functionality"""

    def test_classify_error_by_severity(self):
        """Test error classification by severity"""
        errors = [
            ValidationError(severity=ErrorSeverity.LOW, message="Error 1"),
            ValidationError(severity=ErrorSeverity.MEDIUM, message="Error 2"),
            CoherenceError(severity=ErrorSeverity.HIGH, message="Error 3"),
            RuntimeError(severity=ErrorSeverity.CRITICAL, message="Error 4"),
        ]

        classification = ErrorClassifier.classify_error_by_severity(errors)

        assert len(classification[ErrorSeverity.LOW]) == 1
        assert len(classification[ErrorSeverity.MEDIUM]) == 1
        assert len(classification[ErrorSeverity.HIGH]) == 1
        assert len(classification[ErrorSeverity.CRITICAL]) == 1

    def test_classify_error_by_type(self):
        """Test error classification by type"""
        errors = [
            ValidationError(severity=ErrorSeverity.MEDIUM, message="Error 1"),
            ValidationError(severity=ErrorSeverity.HIGH, message="Error 2"),
            CoherenceError(severity=ErrorSeverity.HIGH, message="Error 3"),
            RuntimeError(severity=ErrorSeverity.LOW, message="Error 4"),
        ]

        classification = ErrorClassifier.classify_error_by_type(errors)

        assert len(classification[ErrorType.VALIDATION_ERROR]) == 2
        assert len(classification[ErrorType.COHERENCE_ERROR]) == 1
        assert len(classification[ErrorType.RUNTIME_ERROR]) == 1

    def test_get_error_handling_metrics(self):
        """Test error handling metrics calculation"""
        errors = [
            ValidationError(severity=ErrorSeverity.LOW, message="Error 1"),
            ValidationError(severity=ErrorSeverity.MEDIUM, message="Error 2"),
            CoherenceError(severity=ErrorSeverity.HIGH, message="Error 3"),
            RuntimeError(severity=ErrorSeverity.CRITICAL, message="Error 4"),
        ]

        metrics = ErrorClassifier.get_error_handling_metrics(errors)

        assert metrics["total_errors"] == 4
        assert metrics["error_types"]["validation_error"] == 2
        assert metrics["error_types"]["coherence_error"] == 1
        assert metrics["error_types"]["runtime_error"] == 1
        assert metrics["severity_distribution"]["low"] == 1
        assert metrics["severity_distribution"]["medium"] == 1
        assert metrics["severity_distribution"]["high"] == 1
        assert metrics["severity_distribution"]["critical"] == 1
        assert metrics["critical_errors_count"] == 1
        assert metrics["most_common_error_type"] == "validation_error"

    def test_get_error_handling_metrics_empty(self):
        """Test error handling metrics with empty error list"""
        metrics = ErrorClassifier.get_error_handling_metrics([])

        assert metrics["total_errors"] == 0
        assert metrics["error_types"] == {}
        assert metrics["severity_distribution"] == {}
        assert metrics["avg_severity_score"] == 0.0
        assert metrics["most_common_error_type"] is None
        assert metrics["critical_errors_count"] == 0


if __name__ == "__main__":
    pytest.main([__file__])
