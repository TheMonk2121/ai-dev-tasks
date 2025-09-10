#!/usr/bin/env python3
"""
Test suite for LabeledFewShot optimizer implementation.

Tests the core functionality of the LabeledFewShot optimizer based on Adam LK transcript.
"""

import os
import sys
import unittest

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import dspy
from dspy import Example, InputField, Module, OutputField, Signature

from dspy_modules.optimizers import (
    DSPyOptimizerManager,
    LabeledFewShotOptimizer,
    OptimizationResult,
    create_labeled_few_shot_optimizer,
    get_optimizer_manager,
)


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
    # For testing, return a simple score based on length
    expected = example.outputs.get("answer", "")
    actual = prediction.answer if hasattr(prediction, "answer") else str(prediction)

    # Simple similarity metric
    if expected.lower() == actual.lower():
        return 1.0
    elif expected.lower() in actual.lower() or actual.lower() in expected.lower():
        return 0.5
    else:
        return 0.0


class TestLabeledFewShotOptimizer(unittest.TestCase):
    """Test cases for LabeledFewShot optimizer"""

    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = LabeledFewShotOptimizer(k=3, metric_threshold=0.1)

        # Create test examples
        self.train_examples = [
            Example(inputs={"question": "What is 2+2?"}, outputs={"answer": "4"}),
            Example(inputs={"question": "What is the capital of France?"}, outputs={"answer": "Paris"}),
            Example(inputs={"question": "What color is the sky?"}, outputs={"answer": "Blue"}),
            Example(inputs={"question": "What is 3+3?"}, outputs={"answer": "6"}),
            Example(inputs={"question": "What is the largest planet?"}, outputs={"answer": "Jupiter"}),
        ]

        self.validation_examples = [
            Example(inputs={"question": "What is 4+4?"}, outputs={"answer": "8"}),
            Example(inputs={"question": "What is the capital of Japan?"}, outputs={"answer": "Tokyo"}),
        ]

    def test_optimizer_initialization(self):
        """Test optimizer initialization"""
        self.assertEqual(self.optimizer.k, 3)
        self.assertEqual(self.optimizer.metric_threshold, 0.1)
        self.assertEqual(len(self.optimizer.examples), 0)
        self.assertEqual(len(self.optimizer.optimization_history), 0)

    def test_add_examples(self):
        """Test adding examples to optimizer"""
        self.optimizer.add_examples(self.train_examples[:2])
        self.assertEqual(len(self.optimizer.examples), 2)

        self.optimizer.add_examples(self.train_examples[2:4])
        self.assertEqual(len(self.optimizer.examples), 4)

    def test_select_examples(self):
        """Test example selection"""
        # Test with k smaller than available examples
        selected = self.optimizer._select_examples(self.train_examples, 3)
        self.assertEqual(len(selected), 3)
        self.assertEqual(selected, self.train_examples[:3])

        # Test with k larger than available examples
        selected = self.optimizer._select_examples(self.train_examples, 10)
        self.assertEqual(len(selected), 5)
        self.assertEqual(selected, self.train_examples)

    def test_create_optimized_program(self):
        """Test optimized program creation"""
        program = SimpleQAModule()
        examples = self.train_examples[:2]

        optimized = self.optimizer._create_optimized_program(program, examples)
        self.assertIsInstance(optimized, SimpleQAModule)

    def test_measure_performance(self):
        """Test performance measurement"""

        # Create a simple mock program that works with our test data
        class MockProgram:
            def forward(self, question):
                class MockResult:
                    def __init__(self, answer):
                        self.answer = answer

                return MockResult("8" if "4+4" in question else "Tokyo")

        program = MockProgram()
        test_data = self.validation_examples

        score = self.optimizer._measure_performance(program, test_data, simple_metric)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_optimize_program_success(self):
        """Test successful program optimization"""

        # Create a simple mock program that works with our test data
        class MockProgram:
            def forward(self, question):
                class MockResult:
                    def __init__(self, answer):
                        self.answer = answer

                return MockResult("8" if "4+4" in question else "Tokyo")

        program = MockProgram()

        result = self.optimizer.optimize_program(program, self.train_examples, simple_metric, self.validation_examples)

        self.assertIsInstance(result, OptimizationResult)
        self.assertIsInstance(result.success, bool)
        self.assertIsInstance(result.performance_improvement, float)
        self.assertIsInstance(result.examples_used, int)
        self.assertIsInstance(result.optimization_time, float)
        self.assertEqual(result.examples_used, 3)  # k=3

    def test_optimize_program_failure(self):
        """Test program optimization with failure"""

        # Create a program that will fail
        class FailingModule(Module):
            def forward(self, question):
                raise Exception("Test failure")

        program = FailingModule()

        result = self.optimizer.optimize_program(program, self.train_examples, simple_metric)

        self.assertIsInstance(result, OptimizationResult)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        self.assertIn("Test failure", result.error_message)

    def test_get_optimization_stats(self):
        """Test optimization statistics"""
        # No optimizations yet
        stats = self.optimizer.get_optimization_stats()
        self.assertEqual(stats["total_optimizations"], 0)

        # Run an optimization
        class MockProgram:
            def forward(self, question):
                class MockResult:
                    def __init__(self, answer):
                        self.answer = answer

                return MockResult("8" if "4+4" in question else "Tokyo")

        program = MockProgram()

        self.optimizer.optimize_program(program, self.train_examples, simple_metric)

        # Check stats after optimization
        stats = self.optimizer.get_optimization_stats()
        self.assertEqual(stats["total_optimizations"], 1)
        self.assertIn("successful_optimizations", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("average_improvement", stats)
        self.assertIn("total_optimization_time", stats)
        self.assertIn("average_optimization_time", stats)
        self.assertEqual(stats["examples_used"], 3)


class TestDSPyOptimizerManager(unittest.TestCase):
    """Test cases for DSPy optimizer manager"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = DSPyOptimizerManager()
        self.optimizer = LabeledFewShotOptimizer()

    def test_manager_initialization(self):
        """Test manager initialization"""
        self.assertEqual(len(self.manager.optimizers), 0)
        self.assertIsNone(self.manager.active_optimizer)

    def test_register_optimizer(self):
        """Test optimizer registration"""
        self.manager.register_optimizer("test_optimizer", self.optimizer)
        self.assertIn("test_optimizer", self.manager.optimizers)
        self.assertEqual(self.manager.optimizers["test_optimizer"], self.optimizer)

    def test_get_optimizer(self):
        """Test getting optimizer"""
        self.manager.register_optimizer("test_optimizer", self.optimizer)

        retrieved = self.manager.get_optimizer("test_optimizer")
        self.assertEqual(retrieved, self.optimizer)

        # Test non-existent optimizer
        retrieved = self.manager.get_optimizer("non_existent")
        self.assertIsNone(retrieved)

    def test_set_active_optimizer(self):
        """Test setting active optimizer"""
        self.manager.register_optimizer("test_optimizer", self.optimizer)

        # Set active optimizer
        success = self.manager.set_active_optimizer("test_optimizer")
        self.assertTrue(success)
        self.assertEqual(self.manager.active_optimizer, "test_optimizer")

        # Test non-existent optimizer
        success = self.manager.set_active_optimizer("non_existent")
        self.assertFalse(success)
        self.assertEqual(self.manager.active_optimizer, "test_optimizer")  # Should remain unchanged


class TestGlobalFunctions(unittest.TestCase):
    """Test cases for global functions"""

    def test_get_optimizer_manager(self):
        """Test getting global optimizer manager"""
        manager = get_optimizer_manager()
        self.assertIsInstance(manager, DSPyOptimizerManager)

        # Should return the same instance
        manager2 = get_optimizer_manager()
        self.assertIs(manager, manager2)

    def test_create_labeled_few_shot_optimizer(self):
        """Test creating labeled few shot optimizer"""
        optimizer = create_labeled_few_shot_optimizer(k=5, metric_threshold=0.2)
        self.assertIsInstance(optimizer, LabeledFewShotOptimizer)
        self.assertEqual(optimizer.k, 5)
        self.assertEqual(optimizer.metric_threshold, 0.2)


if __name__ == "__main__":
    unittest.main()
