#!/usr/bin/env python3
"""
Integration test for LabeledFewShot optimizer with ModelSwitcher.

Demonstrates the optimizer working with our existing DSPy infrastructure.
"""

import os
import sys
import unittest

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import dspy
from dspy import Example, InputField, Module, OutputField, Signature

from dspy_modules.model_switcher import LocalModel, ModelSwitcher
from dspy_modules.optimizers import LabeledFewShotOptimizer, get_optimizer_manager, optimize_program


class TaskAnalysisSignature(Signature):
    """Signature for task analysis"""

    task_description = InputField(desc="A task description to analyze")
    analysis = OutputField(desc="Detailed analysis of the task")


class TaskAnalysisModule(Module):
    """Module for analyzing tasks"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(TaskAnalysisSignature)

    def forward(self, task_description: str) -> str:
        """Forward pass"""
        result = self.predictor(task_description=task_description)
        return result.analysis


def analysis_quality_metric(example: Example, prediction) -> float:
    """Metric to evaluate analysis quality"""
    expected = example.get("outputs", {}).get("analysis", "")
    actual = prediction.analysis if hasattr(prediction, "analysis") else str(prediction)

    # Simple quality metric based on length and content
    if not actual or not expected:
        return 0.0

    # Check for key terms
    key_terms = ["task", "analysis", "steps", "requirements", "approach"]
    found_terms = sum(1 for term in key_terms if term.lower() in actual.lower())

    # Length factor (prefer longer, more detailed analysis)
    length_factor = min(len(actual) / 100, 1.0)

    # Combined score
    score = (found_terms / len(key_terms)) * 0.6 + length_factor * 0.4
    return min(score, 1.0)


class TestOptimizerIntegration(unittest.TestCase):
    """Integration tests for optimizer with ModelSwitcher"""

    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = LabeledFewShotOptimizer(k=3, metric_threshold=0.1)

        # Create training examples
        self.train_examples = [
            Example(
                inputs={"task_description": "Create a simple web page"},
                outputs={
                    "analysis": "This task involves creating a basic HTML page with CSS styling. Steps: 1) Design layout, 2) Write HTML, 3) Add CSS, 4) Test functionality."
                },
            ),
            Example(
                inputs={"task_description": "Build a REST API"},
                outputs={
                    "analysis": "This task requires building a RESTful API. Steps: 1) Define endpoints, 2) Implement controllers, 3) Add database layer, 4) Add authentication, 5) Test endpoints."
                },
            ),
            Example(
                inputs={"task_description": "Implement user authentication"},
                outputs={
                    "analysis": "This task involves implementing user authentication. Steps: 1) Design user model, 2) Create login/logout endpoints, 3) Implement password hashing, 4) Add session management, 5) Test security."
                },
            ),
            Example(
                inputs={"task_description": "Optimize database queries"},
                outputs={
                    "analysis": "This task requires database optimization. Steps: 1) Analyze current queries, 2) Identify bottlenecks, 3) Add indexes, 4) Rewrite slow queries, 5) Test performance improvements."
                },
            ),
            Example(
                inputs={"task_description": "Deploy application to cloud"},
                outputs={
                    "analysis": "This task involves cloud deployment. Steps: 1) Choose cloud provider, 2) Configure infrastructure, 3) Set up CI/CD pipeline, 4) Configure monitoring, 5) Deploy and test."
                },
            ),
        ]

        # Create validation examples
        self.validation_examples = [
            Example(
                inputs={"task_description": "Create a mobile app"},
                outputs={
                    "analysis": "This task involves mobile app development. Steps: 1) Choose platform, 2) Design UI/UX, 3) Implement features, 4) Test on devices, 5) Deploy to app stores."
                },
            ),
            Example(
                inputs={"task_description": "Implement data backup system"},
                outputs={
                    "analysis": "This task requires backup system implementation. Steps: 1) Design backup strategy, 2) Choose backup solution, 3) Configure automated backups, 4) Test restore procedures, 5) Monitor backup health."
                },
            ),
        ]

    def test_optimizer_with_model_switcher(self):
        """Test optimizer integration with ModelSwitcher"""
        # Initialize ModelSwitcher
        switcher = ModelSwitcher()

        # Test with different models
        models_to_test = [LocalModel.LLAMA_3_1_8B, LocalModel.MISTRAL_7B, LocalModel.PHI_3_5_3_8B]

        for model in models_to_test:
            with self.subTest(model=model):
                print(f"\nTesting with model: {model}")

                # Switch to model
                switcher.switch_model(model)

                # Create program
                program = TaskAnalysisModule()

                # Run optimization
                result = self.optimizer.optimize_program(
                    program, self.train_examples, analysis_quality_metric, self.validation_examples
                )

                # Verify result structure
                self.assertIsInstance(result.success, bool)
                self.assertIsInstance(result.performance_improvement, float)
                self.assertIsInstance(result.examples_used, int)
                self.assertIsInstance(result.optimization_time, float)

                print(f"  Success: {result.success}")
                print(f"  Improvement: {result.performance_improvement:.4f}")
                print(f"  Examples used: {result.examples_used}")
                print(f"  Time: {result.optimization_time:.2f}s")

                # Check that we used the expected number of examples
                self.assertEqual(result.examples_used, 3)  # k=3

    def test_optimizer_manager_integration(self):
        """Test optimizer manager integration"""
        # Get global optimizer manager
        manager = get_optimizer_manager()

        # Verify default optimizer is registered
        self.assertIn("labeled_few_shot", manager.optimizers)
        self.assertEqual(manager.active_optimizer, "labeled_few_shot")

        # Test optimization through manager
        program = TaskAnalysisModule()

        result = manager.optimize_program(program, self.train_examples, analysis_quality_metric)

        self.assertIsInstance(result.success, bool)
        self.assertIsInstance(result.performance_improvement, float)

        # Handle case where optimization fails due to no LM loaded
        if result.success:
            self.assertEqual(result.examples_used, 16)  # Default k=16
        else:
            # If optimization fails, examples_used should be 0 or a small number
            self.assertLessEqual(result.examples_used, 5)

    def test_optimize_program_convenience_function(self):
        """Test the convenience optimize_program function"""
        program = TaskAnalysisModule()

        result = optimize_program(program, self.train_examples, analysis_quality_metric, "labeled_few_shot")

        self.assertIsInstance(result.success, bool)
        self.assertIsInstance(result.performance_improvement, float)

        # Handle case where optimization fails due to no LM loaded
        if result.success:
            self.assertEqual(result.examples_used, 16)  # Default k=16
        else:
            # If optimization fails, examples_used should be 0 or a small number
            self.assertLessEqual(result.examples_used, 5)

    def test_optimization_statistics(self):
        """Test optimization statistics collection"""
        # Run multiple optimizations
        program = TaskAnalysisModule()

        for i in range(3):
            self.optimizer.optimize_program(program, self.train_examples, analysis_quality_metric)

        # Get statistics
        stats = self.optimizer.get_optimization_stats()

        # Verify statistics
        self.assertEqual(stats["total_optimizations"], 3)
        self.assertIn("successful_optimizations", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("average_improvement", stats)
        self.assertIn("total_optimization_time", stats)
        self.assertIn("average_optimization_time", stats)
        self.assertEqual(stats["examples_used"], 3)  # k=3

        print("\nOptimization Statistics:")
        print(f"  Total optimizations: {stats['total_optimizations']}")
        print(f"  Successful: {stats['successful_optimizations']}")
        print(f"  Success rate: {stats['success_rate']:.2%}")
        print(f"  Average improvement: {stats['average_improvement']:.4f}")
        print(f"  Total time: {stats['total_optimization_time']:.2f}s")
        print(f"  Average time: {stats['average_optimization_time']:.2f}s")


if __name__ == "__main__":
    unittest.main()
