#!/usr/bin/env python3
"""
Test suite for DSPy Assertion Framework

Tests the assertion-based validation framework targeting 37% → 98% reliability
improvement as mentioned in the Adam LK transcript.
"""

import os
import sys
import time
import unittest
from typing import Any, Dict

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import dspy
from dspy import InputField, Module, OutputField, Signature

from dspy_modules.assertions import (
    AssertionSeverity,
    AssertionType,
    DSPyAssertionFramework,
    ValidationReport,
    assert_reliability_target,
    validate_dspy_module,
)


class TestSignature(Signature):
    """Test signature for validation"""

    input_field = InputField(desc="Test input")
    output_field = OutputField(desc="Test output")


class GoodQualityModule(Module):
    """Module with good code quality for testing"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(TestSignature)

    def forward(self, input_field: str) -> Dict[str, Any]:
        """
        Forward pass with good quality code

        Args:
            input_field: Input string to process

        Returns:
            Dictionary with processed result
        """
        try:
            # Input validation
            if not isinstance(input_field, str):
                raise ValueError("Input must be a string")

            # Process input
            result = self.predictor(input_field=input_field)

            return {"output_field": result.output_field, "input_field": input_field}

        except Exception as e:
            # Error handling
            return {"error": str(e)}


class PoorQualityModule(Module):
    """Module with poor code quality for testing"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(TestSignature)

    def forward(self, input_field):  # Missing type hints
        # Missing docstring
        result = self.predictor(input_field=input_field)
        return {"output_field": result.output_field}  # No error handling


class SecurityModule(Module):
    """Module with security features for testing"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(TestSignature)

    def forward(self, input_field: str) -> Dict[str, Any]:
        """
        Forward pass with security features

        Args:
            input_field: Input string to process

        Returns:
            Dictionary with processed result
        """
        # Input sanitization
        sanitized_input = input_field.strip().replace("<script>", "").replace("</script>", "")

        try:
            result = self.predictor(input_field=sanitized_input)
            return {"output_field": result.output_field}
        except Exception as e:
            return {"error": str(e)}


class TestAssertionFramework(unittest.TestCase):
    """Test cases for the DSPy assertion framework"""

    def setUp(self):
        """Set up test fixtures"""
        self.framework = DSPyAssertionFramework()
        self.test_inputs = [
            {"input_field": "test input 1"},
            {"input_field": "test input 2"},
            {"input_field": "test input 3"},
        ]

    def test_framework_initialization(self):
        """Test framework initialization"""
        self.assertIsNotNone(self.framework)
        self.assertTrue(self.framework.enable_all_assertions)
        self.assertEqual(self.framework.validation_count, 0)
        self.assertEqual(self.framework.total_execution_time, 0.0)
        self.assertEqual(len(self.framework.reliability_history), 0)

    def test_good_quality_module_validation(self):
        """Test validation of a module with good code quality"""
        module = GoodQualityModule()
        report = self.framework.validate_module(module, self.test_inputs)

        # Validate report structure
        self.assertIsInstance(report, ValidationReport)
        self.assertEqual(report.module_name, "GoodQualityModule")
        self.assertGreater(report.total_assertions, 0)
        self.assertGreaterEqual(report.passed_assertions, 0)
        self.assertGreaterEqual(report.reliability_score, 0.0)
        self.assertLessEqual(report.reliability_score, 100.0)
        self.assertIsInstance(report.results, list)
        self.assertIsInstance(report.recommendations, list)

        print("\nGood Quality Module Validation:")
        print(f"  Total assertions: {report.total_assertions}")
        print(f"  Passed assertions: {report.passed_assertions}")
        print(f"  Failed assertions: {report.failed_assertions}")
        print(f"  Reliability score: {report.reliability_score:.1f}%")
        print(f"  Critical failures: {report.critical_failures}")
        print(f"  Execution time: {report.execution_time:.3f}s")

        # Check individual assertion results
        for result in report.results:
            self.assertIsInstance(result.assertion_type, AssertionType)
            self.assertIsInstance(result.severity, AssertionSeverity)
            self.assertIsInstance(result.passed, bool)
            self.assertIsInstance(result.message, str)
            self.assertIsInstance(result.details, dict)
            self.assertGreaterEqual(result.execution_time, 0.0)

    def test_poor_quality_module_validation(self):
        """Test validation of a module with poor code quality"""
        module = PoorQualityModule()
        report = self.framework.validate_module(module, self.test_inputs)

        print("\nPoor Quality Module Validation:")
        print(f"  Total assertions: {report.total_assertions}")
        print(f"  Passed assertions: {report.passed_assertions}")
        print(f"  Failed assertions: {report.failed_assertions}")
        print(f"  Reliability score: {report.reliability_score:.1f}%")
        print(f"  Critical failures: {report.critical_failures}")
        print(f"  Execution time: {report.execution_time:.3f}s")

        # Poor quality module should have lower reliability
        self.assertLess(report.reliability_score, 100.0)
        self.assertGreater(len(report.recommendations), 0)

    def test_security_module_validation(self):
        """Test validation of a module with security features"""
        module = SecurityModule()
        report = self.framework.validate_module(module, self.test_inputs)

        print("\nSecurity Module Validation:")
        print(f"  Total assertions: {report.total_assertions}")
        print(f"  Passed assertions: {report.passed_assertions}")
        print(f"  Failed assertions: {report.failed_assertions}")
        print(f"  Reliability score: {report.reliability_score:.1f}%")
        print(f"  Critical failures: {report.critical_failures}")
        print(f"  Execution time: {report.execution_time:.3f}s")

        # Security module should have good reliability
        self.assertGreater(report.reliability_score, 50.0)

    def test_assertion_types_coverage(self):
        """Test that all assertion types are covered"""
        module = GoodQualityModule()
        report = self.framework.validate_module(module, self.test_inputs)

        assertion_types = [result.assertion_type for result in report.results]

        # Check that we have multiple assertion types
        self.assertGreater(len(set(assertion_types)), 1)

        # Check for specific assertion types
        expected_types = [
            AssertionType.TYPE_HINTS,
            AssertionType.DOCSTRINGS,
            AssertionType.NAMING_CONVENTIONS,
            AssertionType.INPUT_VALIDATION,
            AssertionType.ERROR_HANDLING,
            AssertionType.EXECUTION_TIME,
            AssertionType.INPUT_SANITIZATION,
        ]

        for expected_type in expected_types:
            self.assertIn(expected_type, assertion_types, f"Missing assertion type: {expected_type}")

    def test_severity_levels(self):
        """Test that severity levels are properly assigned"""
        module = GoodQualityModule()
        report = self.framework.validate_module(module, self.test_inputs)

        severities = [result.severity for result in report.results]

        # Check that we have different severity levels
        self.assertGreater(len(set(severities)), 1)

        # Check for critical severity (should exist for important assertions)
        self.assertIn(AssertionSeverity.CRITICAL, severities)

    def test_reliability_improvement_validation(self):
        """Test reliability improvement validation"""
        # Test with improvement that meets target
        before_score = 37.0
        after_score = 98.0
        improvement_meets_target = self.framework.validate_reliability_improvement(before_score, after_score)
        self.assertTrue(improvement_meets_target)

        # Test with improvement that doesn't meet target
        before_score = 37.0
        after_score = 80.0  # Only 43% improvement, not 61%
        improvement_meets_target = self.framework.validate_reliability_improvement(before_score, after_score)
        self.assertFalse(improvement_meets_target)

        # Test with no improvement
        before_score = 50.0
        after_score = 50.0
        improvement_meets_target = self.framework.validate_reliability_improvement(before_score, after_score)
        self.assertFalse(improvement_meets_target)

    def test_convenience_functions(self):
        """Test convenience functions"""
        module = GoodQualityModule()

        # Test validate_dspy_module
        report = validate_dspy_module(module, self.test_inputs)
        self.assertIsInstance(report, ValidationReport)

        # Test assert_reliability_target
        meets_target = assert_reliability_target(module, target_score=50.0)
        self.assertIsInstance(meets_target, bool)

    def test_framework_statistics(self):
        """Test framework statistics collection"""
        # Run multiple validations
        modules = [GoodQualityModule(), PoorQualityModule(), SecurityModule()]

        for module in modules:
            self.framework.validate_module(module, self.test_inputs)

        stats = self.framework.get_statistics()

        # Validate statistics structure
        self.assertIn("total_validations", stats)
        self.assertIn("average_reliability", stats)
        self.assertIn("reliability_trend", stats)
        self.assertIn("total_execution_time", stats)
        self.assertIn("recent_reliability_scores", stats)

        # Validate statistics values
        self.assertEqual(stats["total_validations"], 3)
        self.assertGreaterEqual(stats["average_reliability"], 0.0)
        self.assertLessEqual(stats["average_reliability"], 100.0)
        self.assertGreaterEqual(stats["total_execution_time"], 0.0)
        self.assertEqual(len(stats["recent_reliability_scores"]), 3)

        print("\nFramework Statistics:")
        print(f"  Total validations: {stats['total_validations']}")
        print(f"  Average reliability: {stats['average_reliability']:.1f}%")
        print(f"  Reliability trend: {stats['reliability_trend']}")
        print(f"  Total execution time: {stats['total_execution_time']:.3f}s")
        print(f"  Recent scores: {stats['recent_reliability_scores']}")

    def test_validation_report_properties(self):
        """Test ValidationReport properties"""
        module = GoodQualityModule()
        report = self.framework.validate_module(module, self.test_inputs)

        # Test success_rate property
        expected_success_rate = (
            (report.passed_assertions / report.total_assertions * 100) if report.total_assertions > 0 else 0.0
        )
        self.assertAlmostEqual(report.success_rate, expected_success_rate, places=2)

        # Test is_critical_safe property
        self.assertEqual(report.is_critical_safe, report.critical_failures == 0)

    def test_error_handling(self):
        """Test error handling in validation"""

        # Test with invalid module (no source code)
        class InvalidModule(Module):
            pass

        invalid_module = InvalidModule()

        # This should not crash and should return a validation report
        report = self.framework.validate_module(invalid_module)
        self.assertIsInstance(report, ValidationReport)
        self.assertEqual(report.reliability_score, 0.0)

    def test_performance_overhead(self):
        """Test that validation overhead is reasonable"""
        module = GoodQualityModule()

        # Measure time without validation
        start_time = time.time()
        for _ in range(10):
            module.forward("test input")
        base_time = time.time() - start_time

        # Measure time with validation
        start_time = time.time()
        report = self.framework.validate_module(module, self.test_inputs)
        validation_time = time.time() - start_time

        # Validation should complete in reasonable time (< 5 seconds for this test)
        self.assertLess(validation_time, 5.0, f"Validation took too long: {validation_time:.2f}s")

        # Validation should not be more than 150x slower than base execution
        # (this is reasonable since validation does much more work)
        overhead_ratio = validation_time / base_time if base_time > 0 else 0
        self.assertLess(overhead_ratio, 150.0, f"Validation overhead too high: {overhead_ratio:.2f}x")

        print("\nPerformance Overhead Test:")
        print(f"  Base execution time: {base_time:.3f}s")
        print(f"  Validation time: {validation_time:.3f}s")
        print(f"  Overhead ratio: {overhead_ratio:.2f}x")

    def test_recommendations_generation(self):
        """Test that recommendations are generated for failed assertions"""
        module = PoorQualityModule()
        report = self.framework.validate_module(module, self.test_inputs)

        # Poor quality module should have recommendations
        self.assertGreater(len(report.recommendations), 0)

        # Check that recommendations are meaningful
        for recommendation in report.recommendations:
            self.assertIsInstance(recommendation, str)
            self.assertGreater(len(recommendation), 10)

        print("\nRecommendations for Poor Quality Module:")
        for i, recommendation in enumerate(report.recommendations, 1):
            print(f"  {i}. {recommendation}")


if __name__ == "__main__":
    unittest.main()
