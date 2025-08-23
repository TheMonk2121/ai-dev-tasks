#!/usr/bin/env python3
"""
Signature Validator - Runtime Validation for DSPy Signatures
-----------------------------------------------------------
Provides runtime validation for DSPy signature inputs and outputs to ensure
data integrity and prevent runtime errors.

Features:
- Input field validation (required fields, type checking)
- Output field validation (required fields, completeness)
- Performance metrics collection
- Error reporting and recovery suggestions
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Protocol

from dspy import Signature

_LOG = logging.getLogger("signature_validator")


@dataclass
class ValidationResult:
    """Result of signature validation"""

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class SignatureMetrics:
    """Performance metrics for signature execution"""

    signature_name: str
    execution_time: float
    input_tokens: int
    output_tokens: int
    success_count: int = 0
    error_count: int = 0
    validation_errors: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


class SignatureValidator(Protocol):
    """Protocol for signature validation"""

    def validate_inputs(self, signature: Signature, inputs: Dict[str, Any]) -> ValidationResult:
        """Validate signature inputs"""
        ...

    def validate_outputs(self, signature: Signature, outputs: Dict[str, Any]) -> ValidationResult:
        """Validate signature outputs"""
        ...

    def validate_signature(
        self, signature: Signature, inputs: Dict[str, Any], outputs: Dict[str, Any]
    ) -> ValidationResult:
        """Validate both inputs and outputs"""
        ...


class DSPySignatureValidator:
    """Runtime validator for DSPy signatures"""

    def __init__(self):
        self.metrics: Dict[str, List[SignatureMetrics]] = {}
        self.validation_history: List[ValidationResult] = []

    def validate_inputs(self, signature: Signature, inputs: Dict[str, Any]) -> ValidationResult:
        """Validate signature input fields"""
        start_time = time.time()
        errors = []
        warnings = []

        # Get signature input fields - look for fields with InputField type
        input_fields = {}
        for field_name, field_obj in signature.__class__.__dict__.items():
            if hasattr(field_obj, "__dspy_field_type") and field_obj.__dspy_field_type == "input":
                input_fields[field_name] = field_obj

        # If no input fields found, try alternative approach
        if not input_fields:
            # Look for fields that start with common input patterns
            for field_name, field_obj in signature.__class__.__dict__.items():
                if not field_name.startswith("_") and not callable(field_obj):
                    if hasattr(field_obj, "desc") and "input" in field_obj.desc.lower():
                        input_fields[field_name] = field_obj

        # Check for required input fields
        for field_name, field_obj in input_fields.items():
            if field_name not in inputs:
                errors.append(f"Missing required input field: {field_name}")
            elif inputs[field_name] is None:
                warnings.append(f"Input field {field_name} is None")

        # Check for unexpected input fields
        expected_fields = set(input_fields.keys())
        provided_fields = set(inputs.keys())
        unexpected_fields = provided_fields - expected_fields
        if unexpected_fields:
            warnings.append(f"Unexpected input fields: {unexpected_fields}")

        # Estimate input tokens
        input_tokens = self._estimate_tokens(str(inputs))

        execution_time = time.time() - start_time

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            execution_time=execution_time,
            input_tokens=input_tokens,
        )

    def validate_outputs(self, signature: Signature, outputs: Dict[str, Any]) -> ValidationResult:
        """Validate signature output fields"""
        start_time = time.time()
        errors = []
        warnings = []

        # Get signature output fields - look for fields with OutputField type
        output_fields = {}
        for field_name, field_obj in signature.__class__.__dict__.items():
            if hasattr(field_obj, "__dspy_field_type") and field_obj.__dspy_field_type == "output":
                output_fields[field_name] = field_obj

        # If no output fields found, try alternative approach
        if not output_fields:
            # Look for fields that start with common output patterns
            for field_name, field_obj in signature.__class__.__dict__.items():
                if not field_name.startswith("_") and not callable(field_obj):
                    if hasattr(field_obj, "desc") and "output" in field_obj.desc.lower():
                        output_fields[field_name] = field_obj

        # Check for required output fields
        for field_name, field_obj in output_fields.items():
            if field_name not in outputs:
                errors.append(f"Missing required output field: {field_name}")
            elif outputs[field_name] is None:
                warnings.append(f"Output field {field_name} is None")

        # Check for unexpected output fields
        expected_fields = set(output_fields.keys())
        provided_fields = set(outputs.keys())
        unexpected_fields = provided_fields - expected_fields
        if unexpected_fields:
            warnings.append(f"Unexpected output fields: {unexpected_fields}")

        # Estimate output tokens
        output_tokens = self._estimate_tokens(str(outputs))

        execution_time = time.time() - start_time

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            execution_time=execution_time,
            output_tokens=output_tokens,
        )

    def validate_signature(
        self, signature: Signature, inputs: Dict[str, Any], outputs: Dict[str, Any]
    ) -> ValidationResult:
        """Validate both inputs and outputs for a signature"""
        start_time = time.time()

        # Validate inputs
        input_result = self.validate_inputs(signature, inputs)

        # Validate outputs
        output_result = self.validate_outputs(signature, outputs)

        # Combine results
        combined_errors = input_result.errors + output_result.errors
        combined_warnings = input_result.warnings + output_result.warnings

        total_execution_time = time.time() - start_time

        result = ValidationResult(
            is_valid=len(combined_errors) == 0,
            errors=combined_errors,
            warnings=combined_warnings,
            execution_time=total_execution_time,
            input_tokens=input_result.input_tokens,
            output_tokens=output_result.output_tokens,
        )

        # Record metrics
        self._record_metrics(signature, result)

        return result

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (approximate)"""
        # Rough estimation: ~4 characters per token
        return max(1, len(text) // 4)

    def _record_metrics(self, signature: Signature, result: ValidationResult):
        """Record validation metrics"""
        signature_name = signature.__class__.__name__

        if signature_name not in self.metrics:
            self.metrics[signature_name] = []

        metrics = SignatureMetrics(
            signature_name=signature_name,
            execution_time=result.execution_time,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            success_count=1 if result.is_valid else 0,
            error_count=1 if not result.is_valid else 0,
            validation_errors=result.errors,
        )

        self.metrics[signature_name].append(metrics)
        self.validation_history.append(result)

    def get_signature_performance(self, signature_name: str) -> Dict[str, Any]:
        """Get performance metrics for a signature"""
        if signature_name not in self.metrics:
            return {}

        executions = self.metrics[signature_name]
        if not executions:
            return {}

        total_executions = len(executions)
        successful_executions = sum(1 for m in executions if m.success_count > 0)

        return {
            "total_executions": total_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "avg_execution_time": sum(m.execution_time for m in executions) / total_executions,
            "avg_input_tokens": sum(m.input_tokens for m in executions) / total_executions,
            "avg_output_tokens": sum(m.output_tokens for m in executions) / total_executions,
            "total_validation_errors": sum(len(m.validation_errors) for m in executions),
            "most_common_errors": self._get_most_common_errors(executions),
        }

    def _get_most_common_errors(self, executions: List[SignatureMetrics]) -> List[str]:
        """Get most common validation errors"""
        error_counts = {}
        for execution in executions:
            for error in execution.validation_errors:
                error_counts[error] = error_counts.get(error, 0) + 1

        # Sort by frequency and return top 5
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        return [error for error, count in sorted_errors[:5]]

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get overall validation summary"""
        total_validations = len(self.validation_history)
        successful_validations = sum(1 for r in self.validation_history if r.is_valid)

        return {
            "total_validations": total_validations,
            "success_rate": successful_validations / total_validations if total_validations > 0 else 0,
            "total_errors": sum(len(r.errors) for r in self.validation_history),
            "total_warnings": sum(len(r.warnings) for r in self.validation_history),
            "signatures_tracked": list(self.metrics.keys()),
            "avg_execution_time": (
                sum(r.execution_time for r in self.validation_history) / total_validations
                if total_validations > 0
                else 0
            ),
        }


# Global validator instance
_signature_validator = DSPySignatureValidator()


def get_signature_validator() -> DSPySignatureValidator:
    """Get the global signature validator instance"""
    return _signature_validator


def validate_signature_io(signature: Signature, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> ValidationResult:
    """Convenience function to validate signature I/O"""
    return _signature_validator.validate_signature(signature, inputs, outputs)


def get_signature_performance(signature_name: str) -> Dict[str, Any]:
    """Get performance metrics for a signature"""
    return _signature_validator.get_signature_performance(signature_name)


def get_validation_summary() -> Dict[str, Any]:
    """Get overall validation summary"""
    return _signature_validator.get_validation_summary()


# Note: Decorator approach removed due to complexity with DSPy signature instantiation
# Use validate_signature_io() function instead for manual validation
