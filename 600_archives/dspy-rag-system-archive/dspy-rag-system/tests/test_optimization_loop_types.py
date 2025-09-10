#!/usr/bin/env python3
"""
Unit tests for optimization_loop.py type safety fixes

Tests the DSPy Coder Role recommendations for:
- HasForward Protocol validation
- Forward method access with proper type guards
- Optimizer type compatibility
- Error handling for missing forward methods
"""

import os

# Import from the module
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dspy_modules.optimization_loop import (
    EvaluatePhase,
    OptimizePhase,
    is_forward_compatible,
)


class MockModuleWithForward:
    """Mock module that implements HasForward protocol"""

    def __init__(self):
        self.__doc__ = "Mock module with forward method"

    def forward(self, **kwargs) -> str:
        """Mock forward method"""
        return "test_output"


class MockModuleWithoutForward:
    """Mock module that does NOT implement HasForward protocol"""

    def __init__(self):
        self.__doc__ = "Mock module without forward method"

    def some_other_method(self) -> str:
        return "not_forward"


class TestTypeGuards(unittest.TestCase):
    """Test type guard functions"""

    def test_is_forward_compatible_with_forward_method(self):
        """Test type guard returns True for modules with forward method"""
        module = MockModuleWithForward()
        self.assertTrue(is_forward_compatible(module))

    def test_is_forward_compatible_without_forward_method(self):
        """Test type guard returns False for modules without forward method"""
        module = MockModuleWithoutForward()
        self.assertFalse(is_forward_compatible(module))

    def test_is_forward_compatible_with_non_callable_forward(self):
        """Test type guard returns False for non-callable forward attribute"""
        module = Mock()
        module.forward = "not_callable"
        self.assertFalse(is_forward_compatible(module))


class TestEvaluatePhaseTypeSafety(unittest.TestCase):
    """Test EvaluatePhase type safety improvements"""

    def setUp(self):
        self.phase = EvaluatePhase()
        self.valid_module = MockModuleWithForward()
        self.invalid_module = MockModuleWithoutForward()

    def test_evaluate_performance_with_valid_module(self):
        """Test performance evaluation with module that has forward method"""
        test_data = [{"input": "test1"}, {"input": "test2"}]

        # Should not raise an exception
        result = self.phase._evaluate_performance(self.valid_module, test_data)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)

    def test_evaluate_performance_with_invalid_module(self):
        """Test performance evaluation with module that lacks forward method"""
        test_data = [{"input": "test1"}]

        # Should handle the error gracefully and return 0.0
        result = self.phase._evaluate_performance(self.invalid_module, test_data)
        self.assertEqual(result, 0.0)

    def test_evaluate_quality_with_valid_module(self):
        """Test quality evaluation with module that has forward method"""
        result = self.phase._evaluate_quality(self.valid_module)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        # Should get points for having docstring and forward method
        self.assertGreater(result, 0.2)  # At least docstring points

    def test_evaluate_quality_with_invalid_module(self):
        """Test quality evaluation with module that lacks forward method"""
        result = self.phase._evaluate_quality(self.invalid_module)
        self.assertIsInstance(result, float)
        # Should still get some points (e.g., for docstring) but less overall
        self.assertGreaterEqual(result, 0.0)


class TestOptimizePhaseTypeSafety(unittest.TestCase):
    """Test OptimizePhase type safety improvements"""

    def setUp(self):
        self.phase = OptimizePhase()
        self.valid_module = MockModuleWithForward()
        self.invalid_module = MockModuleWithoutForward()

    @patch("dspy_modules.optimization_loop.LabeledFewShotOptimizer")
    def test_optimize_reliability_with_valid_module(self, mock_optimizer_class):
        """Test reliability optimization with valid module"""
        # Mock the optimizer
        mock_optimizer = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.performance_improvement = 0.1
        mock_result.examples_used = 5
        mock_optimizer.optimize_program.return_value = mock_result
        mock_optimizer_class.return_value = mock_optimizer

        test_data = [{"input": "test1", "output": "expected1"}]

        result = self.phase._optimize_reliability(self.valid_module, test_data)

        self.assertIsInstance(result, dict)
        self.assertTrue(result["success"])
        self.assertEqual(result["improvement"], 0.1)
        self.assertEqual(result["examples_used"], 5)

    def test_optimize_reliability_with_invalid_module(self):
        """Test reliability optimization with invalid module (no forward method)"""
        test_data = [{"input": "test1"}]

        result = self.phase._optimize_reliability(self.invalid_module, test_data)

        self.assertIsInstance(result, dict)
        self.assertFalse(result["success"])
        self.assertIn("error", result)

    def test_optimize_reliability_with_invalid_test_data(self):
        """Test reliability optimization with invalid test data type"""
        invalid_test_data = "not_a_list"

        result = self.phase._optimize_reliability(self.valid_module, invalid_test_data)

        self.assertIsInstance(result, dict)
        self.assertFalse(result["success"])
        self.assertIn("error", result)


class TestHasForwardProtocol(unittest.TestCase):
    """Test HasForward Protocol implementation"""

    def test_protocol_compliance_with_valid_module(self):
        """Test that valid module satisfies HasForward protocol"""
        module = MockModuleWithForward()

        # Should have forward method
        self.assertTrue(hasattr(module, "forward"))
        self.assertTrue(callable(getattr(module, "forward")))

        # Should be able to call forward
        result = module.forward(test="input")
        self.assertEqual(result, "test_output")

    def test_protocol_non_compliance(self):
        """Test that invalid module does not satisfy HasForward protocol"""
        module = MockModuleWithoutForward()

        # Should not have forward method
        self.assertFalse(hasattr(module, "forward"))

        # Type guard should correctly identify this
        self.assertFalse(is_forward_compatible(module))


if __name__ == "__main__":
    unittest.main()
