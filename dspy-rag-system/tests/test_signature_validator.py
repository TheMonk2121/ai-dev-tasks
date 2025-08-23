#!/usr/bin/env python3
"""
Tests for Signature Validator
-----------------------------
Comprehensive tests for runtime validation of DSPy signatures.
"""


import pytest
from dspy import InputField, OutputField, Signature

from src.dspy_modules.signature_validator import (
    DSPySignatureValidator,
    ValidationResult,
    get_signature_performance,
    get_validation_summary,
    validate_signature,
    validate_signature_io,
)


class TestSignature(Signature):
    """Test signature for validation testing"""

    input_field_1 = InputField(desc="First input field")
    input_field_2 = InputField(desc="Second input field")

    output_field_1 = OutputField(desc="First output field")
    output_field_2 = OutputField(desc="Second output field")


class TestSignatureValidator:
    """Test cases for DSPySignatureValidator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.validator = DSPySignatureValidator()
        # Create signature with default values
        self.test_signature = TestSignature(
            input_field_1="default", input_field_2="default", output_field_1="default", output_field_2="default"
        )

    def test_validate_inputs_success(self):
        """Test successful input validation"""
        inputs = {"input_field_1": "test value 1", "input_field_2": "test value 2"}

        result = self.validator.validate_inputs(self.test_signature, inputs)

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.input_tokens > 0
        assert result.execution_time > 0

    def test_validate_inputs_missing_field(self):
        """Test input validation with missing required field"""
        inputs = {
            "input_field_1": "test value 1"
            # Missing input_field_2
        }

        result = self.validator.validate_inputs(self.test_signature, inputs)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Missing required input field: input_field_2" in result.errors[0]

    def test_validate_inputs_unexpected_field(self):
        """Test input validation with unexpected field"""
        inputs = {
            "input_field_1": "test value 1",
            "input_field_2": "test value 2",
            "unexpected_field": "unexpected value",
        }

        result = self.validator.validate_inputs(self.test_signature, inputs)

        assert result.is_valid is True  # Unexpected fields are warnings, not errors
        assert len(result.warnings) == 1
        assert "unexpected_field" in result.warnings[0]

    def test_validate_outputs_success(self):
        """Test successful output validation"""
        outputs = {"output_field_1": "test result 1", "output_field_2": "test result 2"}

        result = self.validator.validate_outputs(self.test_signature, outputs)

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.output_tokens > 0
        assert result.execution_time > 0

    def test_validate_outputs_missing_field(self):
        """Test output validation with missing required field"""
        outputs = {
            "output_field_1": "test result 1"
            # Missing output_field_2
        }

        result = self.validator.validate_outputs(self.test_signature, outputs)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Missing required output field: output_field_2" in result.errors[0]

    def test_validate_signature_complete(self):
        """Test complete signature validation"""
        inputs = {"input_field_1": "test value 1", "input_field_2": "test value 2"}
        outputs = {"output_field_1": "test result 1", "output_field_2": "test result 2"}

        result = self.validator.validate_signature(self.test_signature, inputs, outputs)

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.input_tokens > 0
        assert result.output_tokens > 0
        assert result.execution_time > 0

    def test_validate_signature_with_errors(self):
        """Test signature validation with errors"""
        inputs = {
            "input_field_1": "test value 1"
            # Missing input_field_2
        }
        outputs = {
            "output_field_1": "test result 1"
            # Missing output_field_2
        }

        result = self.validator.validate_signature(self.test_signature, inputs, outputs)

        assert result.is_valid is False
        assert len(result.errors) == 2
        assert any("input_field_2" in error for error in result.errors)
        assert any("output_field_2" in error for error in result.errors)

    def test_estimate_tokens(self):
        """Test token estimation"""
        text = "This is a test string with multiple words"
        tokens = self.validator._estimate_tokens(text)

        assert tokens > 0
        assert tokens <= len(text)  # Should be less than or equal to character count

    def test_record_metrics(self):
        """Test metrics recording"""
        result = ValidationResult(
            is_valid=True, errors=[], warnings=[], execution_time=0.1, input_tokens=50, output_tokens=30
        )

        self.validator._record_metrics(self.test_signature, result)

        assert "TestSignature" in self.validator.metrics
        assert len(self.validator.metrics["TestSignature"]) == 1

        metrics = self.validator.metrics["TestSignature"][0]
        assert metrics.signature_name == "TestSignature"
        assert metrics.execution_time == 0.1
        assert metrics.input_tokens == 50
        assert metrics.output_tokens == 30
        assert metrics.success_count == 1
        assert metrics.error_count == 0

    def test_get_signature_performance(self):
        """Test performance metrics retrieval"""
        # Add some test metrics
        result1 = ValidationResult(is_valid=True, execution_time=0.1, input_tokens=50, output_tokens=30)
        result2 = ValidationResult(is_valid=False, execution_time=0.2, input_tokens=60, output_tokens=40)

        self.validator._record_metrics(self.test_signature, result1)
        self.validator._record_metrics(self.test_signature, result2)

        performance = self.validator.get_signature_performance("TestSignature")

        assert performance["total_executions"] == 2
        assert performance["success_rate"] == 0.5
        assert performance["avg_execution_time"] == 0.15
        assert performance["avg_input_tokens"] == 55
        assert performance["avg_output_tokens"] == 35

    def test_get_validation_summary(self):
        """Test validation summary"""
        # Add some test validations
        result1 = ValidationResult(is_valid=True, errors=[], warnings=["warning1"])
        result2 = ValidationResult(is_valid=False, errors=["error1"], warnings=[])

        self.validator.validation_history = [result1, result2]

        summary = self.validator.get_validation_summary()

        assert summary["total_validations"] == 2
        assert summary["success_rate"] == 0.5
        assert summary["total_errors"] == 1
        assert summary["total_warnings"] == 1


class TestGlobalFunctions:
    """Test global convenience functions"""

    def setup_method(self):
        """Set up test fixtures"""
        self.test_signature = TestSignature(
            input_field_1="default", input_field_2="default", output_field_1="default", output_field_2="default"
        )

    def test_validate_signature_io(self):
        """Test global validate_signature_io function"""
        inputs = {"input_field_1": "test value 1", "input_field_2": "test value 2"}
        outputs = {"output_field_1": "test result 1", "output_field_2": "test result 2"}

        result = validate_signature_io(self.test_signature, inputs, outputs)

        assert isinstance(result, ValidationResult)
        assert result.is_valid is True

    def test_get_signature_performance(self):
        """Test global get_signature_performance function"""
        # First add some metrics
        inputs = {"input_field_1": "test", "input_field_2": "test"}
        outputs = {"output_field_1": "test", "output_field_2": "test"}
        validate_signature_io(self.test_signature, inputs, outputs)

        performance = get_signature_performance("TestSignature")

        assert isinstance(performance, dict)
        assert "total_executions" in performance

    def test_get_validation_summary(self):
        """Test global get_validation_summary function"""
        # First add some validations
        inputs = {"input_field_1": "test", "input_field_2": "test"}
        outputs = {"output_field_1": "test", "output_field_2": "test"}
        validate_signature_io(self.test_signature, inputs, outputs)

        summary = get_validation_summary()

        assert isinstance(summary, dict)
        assert "total_validations" in summary


class TestValidateSignatureDecorator:
    """Test the validate_signature decorator"""

    def test_decorator_success(self):
        """Test decorator with successful validation"""

        @validate_signature
        def test_function(signature, **kwargs):
            return {"output_field_1": "result1", "output_field_2": "result2"}

        test_signature = TestSignature()
        result = test_function(test_signature, input_field_1="test1", input_field_2="test2")

        assert result["output_field_1"] == "result1"
        assert result["output_field_2"] == "result2"

    def test_decorator_validation_failure(self):
        """Test decorator with validation failure"""

        @validate_signature
        def test_function(signature, **kwargs):
            return {
                "output_field_1": "result1"
                # Missing output_field_2
            }

        test_signature = TestSignature()

        # Should still return result but log validation errors
        result = test_function(test_signature, input_field_1="test1", input_field_2="test2")

        assert result["output_field_1"] == "result1"

    def test_decorator_non_signature(self):
        """Test decorator with non-signature function"""

        @validate_signature
        def test_function(value):
            return value * 2

        result = test_function(5)
        assert result == 10


class TestRealDSPySignatures:
    """Test with actual DSPy signatures from the system"""

    def test_model_selection_signature(self):
        """Test validation with ModelSelectionSignature"""
        from src.dspy_modules.model_switcher import ModelSelectionSignature

        signature = ModelSelectionSignature()

        # Valid inputs
        inputs = {
            "task": "Implement a new feature",
            "task_type": "coding",
            "complexity": "moderate",
            "context_size": 8192,
        }

        # Valid outputs
        outputs = {
            "selected_model": "cursor-native",
            "reasoning": "Best for coding tasks",
            "confidence": 0.85,
            "expected_performance": "High accuracy for code generation",
        }

        result = validate_signature_io(signature, inputs, outputs)
        assert result.is_valid is True

    def test_documentation_query_signature(self):
        """Test validation with DocumentationQuerySignature"""
        from src.dspy_modules.documentation_retrieval import DocumentationQuerySignature

        signature = DocumentationQuerySignature()

        # Valid inputs
        inputs = {
            "user_query": "How do I use DSPy signatures?",
            "context_type": "implementation",
            "query_type": "reference",
        }

        # Valid outputs
        outputs = {
            "processed_query": "DSPy signature usage implementation reference",
            "search_categories": ["dspy", "signatures", "implementation"],
            "expected_context": "Code examples and usage patterns",
        }

        result = validate_signature_io(signature, inputs, outputs)
        assert result.is_valid is True

    def test_entity_extraction_signature(self):
        """Test validation with EntityExtractionSignature"""
        from src.dspy_modules.lang_extract_system import EntityExtractionSignature

        signature = EntityExtractionSignature()

        # Valid inputs
        inputs = {
            "text": "The user wants to implement a new feature using Python.",
            "entity_types": ["person", "language", "task"],
        }

        # Valid outputs
        outputs = {
            "entities": [
                {"text": "user", "type": "person", "span": (4, 8)},
                {"text": "Python", "type": "language", "span": (35, 41)},
            ],
            "confidence": 0.9,
            "spans": [(4, 8), (35, 41)],
        }

        result = validate_signature_io(signature, inputs, outputs)
        assert result.is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
