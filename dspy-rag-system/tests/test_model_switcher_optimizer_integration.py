#!/usr/bin/env python3
"""
Test suite for ModelSwitcher optimizer integration.

Tests the integration of LabeledFewShot optimizer with ModelSwitcher.
"""

import os
import sys
import unittest

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import dspy
from dspy import Example, InputField, Module, OutputField, Signature

from dspy_modules.model_switcher import LocalModel, ModelSwitcher
from dspy_modules.optimizers import OptimizationResult


class SimpleQASignature(Signature):
    """Simple Q&A signature for testing"""

    question = InputField(desc="A question to answer")
    answer = OutputField(desc="The answer to the question")


class SimpleQAModule(Module):
    """Simple Q&A module for testing"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(SimpleQASignature)

    def forward(self, question: str) -> str:
        """Forward pass"""
        result = self.predictor(question=question)
        return result.answer


def simple_metric(example: Example, prediction) -> float:
    """Simple metric function for testing"""
    expected = example.get("outputs", {}).get("answer", "")
    actual = prediction.answer if hasattr(prediction, "answer") else str(prediction)

    # Simple similarity metric
    if expected.lower() == actual.lower():
        return 1.0
    elif expected.lower() in actual.lower() or actual.lower() in expected.lower():
        return 0.5
    else:
        return 0.0


class TestModelSwitcherOptimizerIntegration(unittest.TestCase):
    """Test cases for ModelSwitcher optimizer integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.switcher = ModelSwitcher()

        # Create test examples
        self.train_examples = [
            Example(inputs={"question": "What is 2+2?"}, outputs={"answer": "4"}),
            Example(inputs={"question": "What is the capital of France?"}, outputs={"answer": "Paris"}),
            Example(inputs={"question": "What color is the sky?"}, outputs={"answer": "Blue"}),
        ]

    def test_optimizer_initialization(self):
        """Test optimizer initialization in ModelSwitcher"""
        # Check if optimizer system is available
        self.assertIsNotNone(self.switcher.optimizer_enabled)

        if self.switcher.optimizer_enabled:
            self.assertIsNotNone(self.switcher.optimizer_manager)
            self.assertEqual(self.switcher.active_optimizer, "labeled_few_shot")
        else:
            self.assertIsNone(self.switcher.optimizer_manager)
            self.assertIsNone(self.switcher.active_optimizer)

    def test_enable_disable_optimizer(self):
        """Test enabling and disabling optimizer"""
        if not self.switcher.optimizer_enabled:
            self.skipTest("Optimizer system not available")

        # Test enabling optimizer
        success = self.switcher.enable_optimizer("labeled_few_shot")
        self.assertTrue(success)
        self.assertEqual(self.switcher.active_optimizer, "labeled_few_shot")

        # Test disabling optimizer
        success = self.switcher.disable_optimizer()
        self.assertTrue(success)
        self.assertIsNone(self.switcher.active_optimizer)

    def test_optimize_program_integration(self):
        """Test program optimization through ModelSwitcher"""
        if not self.switcher.optimizer_enabled:
            self.skipTest("Optimizer system not available")

        # Enable optimizer
        self.switcher.enable_optimizer("labeled_few_shot")

        # Create a mock program
        class MockProgram:
            def forward(self, question: str):
                class MockResult:
                    def __init__(self, answer):
                        self.answer = answer

                return MockResult("42" if "math" in question.lower() else "Unknown")

        program = MockProgram()

        # Test optimization
        result = self.switcher.optimize_program(program, self.train_examples, simple_metric)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, OptimizationResult)
        self.assertIsInstance(result.success, bool)
        self.assertIsInstance(result.performance_improvement, float)
        self.assertIsInstance(result.examples_used, int)

    def test_get_optimizer_stats(self):
        """Test getting optimizer statistics"""
        if not self.switcher.optimizer_enabled:
            self.skipTest("Optimizer system not available")

        # Enable optimizer
        self.switcher.enable_optimizer("labeled_few_shot")

        # Get stats
        stats = self.switcher.get_optimizer_stats()

        # Verify stats structure
        self.assertIn("enabled", stats)
        self.assertIn("active_optimizer", stats)
        self.assertIn("stats", stats)

        self.assertTrue(stats["enabled"])
        self.assertEqual(stats["active_optimizer"], "labeled_few_shot")
        self.assertIsInstance(stats["stats"], dict)

    def test_get_stats_with_optimizer(self):
        """Test getting ModelSwitcher stats with optimizer information"""
        stats = self.switcher.get_stats()

        # Verify basic stats
        self.assertIn("current_model", stats)
        self.assertIn("switch_count", stats)
        self.assertIn("model_load_times", stats)
        self.assertIn("available_models", stats)
        self.assertIn("optimizer", stats)

        # Verify optimizer stats
        optimizer_stats = stats["optimizer"]
        self.assertIn("enabled", optimizer_stats)
        self.assertIn("active_optimizer", optimizer_stats)
        self.assertIn("optimization_stats", optimizer_stats)

        if self.switcher.optimizer_enabled:
            self.assertTrue(optimizer_stats["enabled"])
            self.assertEqual(optimizer_stats["active_optimizer"], "labeled_few_shot")
            self.assertIsInstance(optimizer_stats["optimization_stats"], dict)
        else:
            self.assertFalse(optimizer_stats["enabled"])
            self.assertIsNone(optimizer_stats["active_optimizer"])
            self.assertIsNone(optimizer_stats["optimization_stats"])

    def test_optimizer_with_model_switching(self):
        """Test optimizer functionality with model switching"""
        if not self.switcher.optimizer_enabled:
            self.skipTest("Optimizer system not available")

        # Enable optimizer
        self.switcher.enable_optimizer("labeled_few_shot")

        # Switch to different models and test optimizer
        models_to_test = [LocalModel.LLAMA_3_1_8B, LocalModel.MISTRAL_7B, LocalModel.PHI_3_5_3_8B]

        for model in models_to_test:
            with self.subTest(model=model):
                # Switch model
                success = self.switcher.switch_model(model)
                self.assertTrue(success)

                # Verify optimizer is still enabled
                self.assertEqual(self.switcher.active_optimizer, "labeled_few_shot")

                # Get optimizer stats
                stats = self.switcher.get_optimizer_stats()
                self.assertTrue(stats["enabled"])
                self.assertEqual(stats["active_optimizer"], "labeled_few_shot")

    def test_optimizer_performance_overhead(self):
        """Test that optimizer integration has minimal performance overhead"""
        if not self.switcher.optimizer_enabled:
            self.skipTest("Optimizer system not available")

        import time

        # Test without optimizer
        self.switcher.disable_optimizer()
        start_time = time.time()

        # Switch model multiple times
        for _ in range(3):
            self.switcher.switch_model(LocalModel.LLAMA_3_1_8B)

        time_without_optimizer = time.time() - start_time

        # Test with optimizer
        self.switcher.enable_optimizer("labeled_few_shot")
        start_time = time.time()

        # Switch model multiple times
        for _ in range(3):
            self.switcher.switch_model(LocalModel.LLAMA_3_1_8B)

        time_with_optimizer = time.time() - start_time

        # Verify overhead is minimal (less than 50% increase)
        overhead_ratio = time_with_optimizer / time_without_optimizer
        self.assertLess(overhead_ratio, 1.5, f"Optimizer overhead too high: {overhead_ratio:.2f}x")

    def test_optimizer_error_handling(self):
        """Test error handling in optimizer integration"""
        if not self.switcher.optimizer_enabled:
            self.skipTest("Optimizer system not available")

        # Test with invalid optimizer name
        success = self.switcher.enable_optimizer("invalid_optimizer")
        self.assertFalse(success)

        # Test optimization with invalid program
        result = self.switcher.optimize_program(None, self.train_examples, simple_metric)  # Invalid program
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)

        # Test with disabled optimizer
        self.switcher.disable_optimizer()
        result = self.switcher.optimize_program("dummy_program", self.train_examples, simple_metric)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
