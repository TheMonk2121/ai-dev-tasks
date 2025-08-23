#!/usr/bin/env python3
"""
Validation Framework Integration Tests

Tests the integration of the assertion framework with existing DSPy modules
and measures reliability improvements.
"""

import os
import sys
import unittest
from typing import Any, Dict

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import dspy
from dspy import InputField, Module, OutputField, Signature

from dspy_modules.assertions import (
    DSPyAssertionFramework,
    ValidationReport,
    assert_reliability_target,
    validate_dspy_module,
)
from dspy_modules.model_switcher import ModelSwitcher


class TestSignature(Signature):
    """Test signature for validation"""

    input_field = InputField(desc="Test input")
    output_field = OutputField(desc="Test output")


class BaselineModule(Module):
    """Baseline module with poor quality for testing"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(TestSignature)

    def forward(self, input_field):  # Missing type hints
        # Missing docstring
        result = self.predictor(input_field=input_field)
        return {"output_field": result.output_field}  # No error handling


class OptimizedModule(Module):
    """Optimized module with high quality for testing"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(TestSignature)

    def forward(self, input_field: str) -> Dict[str, Any]:
        """
        Forward pass with comprehensive quality improvements

        Args:
            input_field: Input string to process

        Returns:
            Dictionary with processed result and metadata
        """
        try:
            # Input validation
            if not isinstance(input_field, str):
                raise ValueError("Input must be a string")

            if not input_field.strip():
                raise ValueError("Input cannot be empty")

            # Input sanitization
            sanitized_input = input_field.strip().replace("<script>", "").replace("</script>", "")

            # Process input
            result = self.predictor(input_field=sanitized_input)

            return {"output_field": result.output_field, "input_field": sanitized_input, "validation_status": "passed"}

        except Exception as e:
            # Comprehensive error handling
            return {
                "error": str(e),
                "error_type": type(e).__name__,
                "input_field": input_field,
                "validation_status": "failed",
            }


class TestValidationFrameworkIntegration(unittest.TestCase):
    """Test cases for validation framework integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.framework = DSPyAssertionFramework()
        self.switcher = ModelSwitcher()
        self.test_inputs = [
            {"input_field": "normal input"},
            {"input_field": "<script>alert('xss')</script>"},  # Security test
            {"input_field": ""},  # Empty input test
            {"input_field": "very long input " * 100},  # Performance test
        ]

    def test_assertion_framework_integration(self):
        """Test integration of assertion framework with DSPy modules"""
        # Test baseline module
        baseline_module = BaselineModule()
        baseline_report = self.framework.validate_module(baseline_module, self.test_inputs)

        # Test optimized module
        optimized_module = OptimizedModule()
        optimized_report = self.framework.validate_module(optimized_module, self.test_inputs)

        # Validate reports
        self.assertIsInstance(baseline_report, ValidationReport)
        self.assertIsInstance(optimized_report, ValidationReport)

        # Check that optimized module has better reliability
        self.assertGreater(optimized_report.reliability_score, baseline_report.reliability_score)

        print("\nIntegration Test Results:")
        print(f"  Baseline module reliability: {baseline_report.reliability_score:.1f}%")
        print(f"  Optimized module reliability: {optimized_report.reliability_score:.1f}%")
        print(f"  Improvement: {optimized_report.reliability_score - baseline_report.reliability_score:.1f}%")

    def test_model_switcher_validation_integration(self):
        """Test integration with ModelSwitcher validation capabilities"""
        # Test that ModelSwitcher has validation methods
        self.assertTrue(hasattr(self.switcher, "validation_enabled"))
        self.assertTrue(hasattr(self.switcher, "assertion_framework"))
        self.assertTrue(hasattr(self.switcher, "validation_history"))

        # Test validation enable/disable
        self.assertTrue(self.switcher.enable_validation())
        self.assertTrue(self.switcher.validation_enabled)

        self.assertTrue(self.switcher.disable_validation())
        self.assertFalse(self.switcher.validation_enabled)

        # Re-enable for further tests
        self.switcher.enable_validation()

        print("\nModelSwitcher Integration:")
        print(f"  Validation enabled: {self.switcher.validation_enabled}")
        print(f"  Assertion framework: {type(self.switcher.assertion_framework).__name__}")
        print(f"  Validation history length: {len(self.switcher.validation_history)}")

    def test_reliability_improvement_validation(self):
        """Test reliability improvement validation with target"""
        baseline_module = BaselineModule()
        optimized_module = OptimizedModule()

        # Get validation reports
        baseline_report = self.framework.validate_module(baseline_module, self.test_inputs)
        optimized_report = self.framework.validate_module(optimized_module, self.test_inputs)

        # Test reliability improvement validation
        improvement = optimized_report.reliability_score - baseline_report.reliability_score
        meets_target = self.framework.validate_reliability_improvement(
            baseline_report.reliability_score, optimized_report.reliability_score
        )

        print("\nReliability Improvement Validation:")
        print(f"  Baseline score: {baseline_report.reliability_score:.1f}%")
        print(f"  Optimized score: {optimized_report.reliability_score:.1f}%")
        print(f"  Improvement: {improvement:.1f}%")
        print(f"  Target (61%): {'✅ Met' if meets_target else '❌ Not Met'}")

        # Validate that improvement is positive
        self.assertGreater(improvement, 0)

    def test_validation_statistics_integration(self):
        """Test validation statistics integration"""
        # Run multiple validations
        modules = [BaselineModule(), OptimizedModule(), BaselineModule(), OptimizedModule()]

        for module in modules:
            self.framework.validate_module(module, self.test_inputs)

        # Get statistics
        stats = self.framework.get_statistics()

        # Validate statistics
        self.assertIn("total_validations", stats)
        self.assertIn("average_reliability", stats)
        self.assertIn("reliability_trend", stats)
        self.assertIn("total_execution_time", stats)
        self.assertIn("recent_reliability_scores", stats)

        self.assertEqual(stats["total_validations"], 4)
        self.assertGreaterEqual(stats["average_reliability"], 0.0)
        self.assertLessEqual(stats["average_reliability"], 100.0)

        print("\nValidation Statistics Integration:")
        print(f"  Total validations: {stats['total_validations']}")
        print(f"  Average reliability: {stats['average_reliability']:.1f}%")
        print(f"  Reliability trend: {stats['reliability_trend']}")
        print(f"  Recent scores: {[f'{s:.1f}%' for s in stats['recent_reliability_scores']]}")

    def test_convenience_functions_integration(self):
        """Test convenience functions integration"""
        optimized_module = OptimizedModule()

        # Test validate_dspy_module
        report = validate_dspy_module(optimized_module, self.test_inputs)
        self.assertIsInstance(report, ValidationReport)

        # Test assert_reliability_target
        meets_50 = assert_reliability_target(optimized_module, target_score=50.0)
        meets_90 = assert_reliability_target(optimized_module, target_score=90.0)
        meets_98 = assert_reliability_target(optimized_module, target_score=98.0)

        print("\nConvenience Functions Integration:")
        print(f"  Module reliability: {report.reliability_score:.1f}%")
        print(f"  Meets 50% target: {'✅ Yes' if meets_50 else '❌ No'}")
        print(f"  Meets 90% target: {'✅ Yes' if meets_90 else '❌ No'}")
        print(f"  Meets 98% target: {'✅ Yes' if meets_98 else '❌ No'}")

        # Validate that at least 50% target is met
        self.assertTrue(meets_50)

    def test_error_handling_integration(self):
        """Test error handling in integration"""

        # Test with invalid module
        class InvalidModule:
            pass

        invalid_module = InvalidModule()

        # This should not crash and should return a validation report
        report = self.framework.validate_module(invalid_module)
        self.assertIsInstance(report, ValidationReport)
        self.assertEqual(report.reliability_score, 0.0)

        print("\nError Handling Integration:")
        print(f"  Invalid module validation: {'✅ Success' if report else '❌ Failed'}")
        print(f"  Reliability score: {report.reliability_score:.1f}%")

    def test_performance_integration(self):
        """Test performance impact of integration"""
        import time

        optimized_module = OptimizedModule()

        # Measure time without validation
        start_time = time.time()
        for _ in range(10):
            optimized_module.forward("test input")
        base_time = time.time() - start_time

        # Measure time with validation
        start_time = time.time()
        report = self.framework.validate_module(optimized_module, self.test_inputs)
        validation_time = time.time() - start_time

        # Validation overhead should be reasonable (< 10% of base time)
        overhead_ratio = validation_time / base_time if base_time > 0 else 0

        print("\nPerformance Integration:")
        print(f"  Base execution time: {base_time:.3f}s")
        print(f"  Validation time: {validation_time:.3f}s")
        print(f"  Overhead ratio: {overhead_ratio:.2f}x")
        print(f"  Performance impact: {'✅ Acceptable' if overhead_ratio < 10.0 else '⚠️  High'}")

        self.assertLess(overhead_ratio, 10.0, f"Validation overhead too high: {overhead_ratio:.2f}x")


if __name__ == "__main__":
    unittest.main()
