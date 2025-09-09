#!/usr/bin/env python3
"""
Real Task Testing and Validation for DSPy v2 Optimization

Tests the LabeledFewShot optimizer with real DSPy programs and measures
performance improvements against Adam LK transcript benchmarks.
"""

import os
import sys
import unittest
from typing import Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import dspy
from dspy import Example, InputField, Module, OutputField, Signature

from dspy_modules.documentation_retrieval import DocumentationQueryProcessor
from dspy_modules.model_switcher import LocalModel, ModelSwitcher
from dspy_modules.optimizers import LabeledFewShotOptimizer, OptimizationResult


class TaskAnalysisSignature(Signature):
    """Signature for task analysis and planning"""

    task_description = InputField(desc="A task description to analyze")
    complexity = InputField(desc="Task complexity level")
    analysis = OutputField(desc="Detailed analysis of the task")
    approach = OutputField(desc="Recommended approach for the task")
    estimated_time = OutputField(desc="Estimated time to complete")


class TaskAnalysisModule(Module):
    """Real DSPy module for task analysis"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(TaskAnalysisSignature)

    def forward(self, task_description: str, complexity: str = "moderate") -> dict[str, Any]:
        """Analyze a task and provide recommendations"""
        result = self.predictor(task_description=task_description, complexity=complexity)

        return {
            "analysis": result.analysis,
            "approach": result.approach,
            "estimated_time": result.estimated_time,
            "task_description": task_description,
            "complexity": complexity,
        }


class CodeReviewSignature(Signature):
    """Signature for code review and quality assessment"""

    code_snippet = InputField(desc="Code snippet to review")
    review_focus = InputField(desc="Focus area for review (security, performance, style, etc.)")
    review = OutputField(desc="Detailed code review")
    quality_score = OutputField(desc="Quality score from 1-10")
    recommendations = OutputField(desc="Specific recommendations for improvement")


class CodeReviewModule(Module):
    """Real DSPy module for code review"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(CodeReviewSignature)

    def forward(self, code_snippet: str, review_focus: str = "general") -> dict[str, Any]:
        """Review code and provide quality assessment"""
        result = self.predictor(code_snippet=code_snippet, review_focus=review_focus)

        return {
            "review": result.review,
            "quality_score": result.quality_score,
            "recommendations": result.recommendations,
            "code_snippet": code_snippet,
            "review_focus": review_focus,
        }


class DocumentationQueryModule(Module):
    """Real DSPy module for documentation queries"""

    def __init__(self):
        super().__init__()
        self.processor = DocumentationQueryProcessor()

    def forward(self, user_query: str, context_type: str = "general") -> dict[str, Any]:
        """Process documentation queries"""
        result = self.processor.forward(user_query=user_query, context_type=context_type)

        return {
            "processed_query": result["processed_query"],
            "search_categories": result["search_categories"],
            "expected_context": result["expected_context"],
            "original_query": user_query,
            "context_type": context_type,
        }


def task_analysis_metric(example: Example, prediction) -> float:
    """Metric for task analysis quality"""
    expected = example.get("outputs", {})
    actual = prediction if isinstance(prediction, dict) else {}

    # Extract key fields
    expected_analysis = expected.get("analysis", "")
    actual_analysis = actual.get("analysis", "")
    expected_approach = expected.get("approach", "")
    actual_approach = actual.get("approach", "")

    # Calculate similarity scores
    analysis_score = _calculate_text_similarity(expected_analysis, actual_analysis)
    approach_score = _calculate_text_similarity(expected_approach, actual_approach)

    # Combined score
    score = (analysis_score * 0.6) + (approach_score * 0.4)
    return score


def code_review_metric(example: Example, prediction) -> float:
    """Metric for code review quality"""
    expected = example.get("outputs", {})
    actual = prediction if isinstance(prediction, dict) else {}

    # Extract key fields
    expected_review = expected.get("review", "")
    actual_review = actual.get("review", "")
    expected_score = expected.get("quality_score", 5)
    actual_score = actual.get("quality_score", 5)

    # Calculate scores
    review_score = _calculate_text_similarity(expected_review, actual_review)
    score_accuracy = 1.0 - min(abs(expected_score - actual_score) / 10.0, 1.0)

    # Combined score
    score = (review_score * 0.7) + (score_accuracy * 0.3)
    return score


def documentation_query_metric(example: Example, prediction) -> float:
    """Metric for documentation query processing"""
    expected = example.get("outputs", {})
    actual = prediction if isinstance(prediction, dict) else {}

    # Extract key fields
    expected_processed = expected.get("processed_query", "")
    actual_processed = actual.get("processed_query", "")
    expected_categories = expected.get("search_categories", "")
    actual_categories = actual.get("search_categories", "")

    # Calculate scores
    query_score = _calculate_text_similarity(expected_processed, actual_processed)
    categories_score = _calculate_text_similarity(expected_categories, actual_categories)

    # Combined score
    score = (query_score * 0.6) + (categories_score * 0.4)
    return score


def _calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two text strings"""
    if not text1 or not text2:
        return 0.0

    # Simple word overlap similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union)


class TestRealTaskOptimization(unittest.TestCase):
    """Test cases for real task optimization with actual DSPy modules"""

    def setUp(self):
        """Set up test fixtures"""
        self.switcher = ModelSwitcher()
        self.optimizer = LabeledFewShotOptimizer(k=8, metric_threshold=0.1)

        # Create real task examples
        self.task_analysis_examples = [
            Example(
                inputs={"task_description": "Create a Python script to analyze CSV data", "complexity": "moderate"},
                outputs={
                    "analysis": "This task involves data analysis using Python. Key components: CSV reading, data processing, analysis, and output generation.",
                    "approach": "Use pandas for CSV handling, implement data validation, create analysis functions, and generate reports.",
                    "estimated_time": "4-6 hours",
                },
            ),
            Example(
                inputs={"task_description": "Build a REST API for user management", "complexity": "complex"},
                outputs={
                    "analysis": "This task requires building a complete REST API with user management features including authentication, CRUD operations, and data validation.",
                    "approach": "Use FastAPI or Flask, implement JWT authentication, create user models, add input validation, and include comprehensive testing.",
                    "estimated_time": "8-12 hours",
                },
            ),
            Example(
                inputs={"task_description": "Optimize database queries for performance", "complexity": "moderate"},
                outputs={
                    "analysis": "This task involves analyzing and optimizing database queries to improve performance and reduce response times.",
                    "approach": "Profile existing queries, identify bottlenecks, add appropriate indexes, rewrite slow queries, and test performance improvements.",
                    "estimated_time": "6-8 hours",
                },
            ),
        ]

        self.code_review_examples = [
            Example(
                inputs={"code_snippet": "def calculate_sum(a, b): return a + b", "review_focus": "general"},
                outputs={
                    "review": "Simple function that adds two numbers. Consider adding type hints and docstring for better documentation.",
                    "quality_score": 6,
                    "recommendations": "Add type hints, docstring, and input validation for edge cases.",
                },
            ),
            Example(
                inputs={"code_snippet": "for i in range(1000): print(i)", "review_focus": "performance"},
                outputs={
                    "review": "Inefficient loop that prints each number individually. Consider using more efficient approaches for large ranges.",
                    "quality_score": 4,
                    "recommendations": "Use list comprehension or generator expressions for better performance.",
                },
            ),
        ]

        self.documentation_query_examples = [
            Example(
                inputs={"user_query": "How do I add documents to the RAG system?", "context_type": "implementation"},
                outputs={
                    "processed_query": "document addition process RAG system implementation",
                    "search_categories": ["setup", "documentation", "implementation"],
                    "expected_context": "Step-by-step guide for adding documents to the RAG system",
                },
            ),
            Example(
                inputs={"user_query": "What are the best practices for DSPy optimization?", "context_type": "research"},
                outputs={
                    "processed_query": "DSPy optimization best practices guidelines",
                    "search_categories": ["optimization", "best-practices", "DSPy"],
                    "expected_context": "Comprehensive guide to DSPy optimization techniques",
                },
            ),
        ]

    def test_task_analysis_optimization(self):
        """Test optimization of task analysis module"""
        if not self.switcher.optimizer_enabled:
            self.skipTest("Optimizer system not available")

        # Create task analysis module
        module = TaskAnalysisModule()

        # Run optimization
        result = self.optimizer.optimize_program(module, self.task_analysis_examples, task_analysis_metric)

        # Validate results
        self.assertIsNotNone(result)
        self.assertIsInstance(result, OptimizationResult)
        self.assertIsInstance(result.success, bool)
        self.assertIsInstance(result.performance_improvement, float)
        self.assertIsInstance(result.examples_used, int)

        print("\nTask Analysis Optimization Results:")
        print(f"  Success: {result.success}")
        print(f"  Performance Improvement: {result.performance_improvement:.4f}")
        print(f"  Examples Used: {result.examples_used}")
        print(f"  Optimization Time: {result.optimization_time:.2f}s")

        if result.metrics:
            print(f"  Baseline Score: {result.metrics['baseline_score']:.4f}")
            print(f"  Optimized Score: {result.metrics['optimized_score']:.4f}")
            print(f"  Improvement %: {result.metrics['improvement_percentage']:.2f}%")

    def test_code_review_optimization(self):
        """Test optimization of code review module"""
        if not self.switcher.optimizer_enabled:
            self.skipTest("Optimizer system not available")

        # Create code review module
        module = CodeReviewModule()

        # Run optimization
        result = self.optimizer.optimize_program(module, self.code_review_examples, code_review_metric)

        # Validate results
        self.assertIsNotNone(result)
        self.assertIsInstance(result, OptimizationResult)
        self.assertIsInstance(result.success, bool)
        self.assertIsInstance(result.performance_improvement, float)
        self.assertIsInstance(result.examples_used, int)

        print("\nCode Review Optimization Results:")
        print(f"  Success: {result.success}")
        print(f"  Performance Improvement: {result.performance_improvement:.4f}")
        print(f"  Examples Used: {result.examples_used}")
        print(f"  Optimization Time: {result.optimization_time:.2f}s")

        if result.metrics:
            print(f"  Baseline Score: {result.metrics['baseline_score']:.4f}")
            print(f"  Optimized Score: {result.metrics['optimized_score']:.4f}")
            print(f"  Improvement %: {result.metrics['improvement_percentage']:.2f}%")

    def test_documentation_query_optimization(self):
        """Test optimization of documentation query module"""
        if not self.switcher.optimizer_enabled:
            self.skipTest("Optimizer system not available")

        # Create documentation query module
        module = DocumentationQueryModule()

        # Run optimization
        result = self.optimizer.optimize_program(module, self.documentation_query_examples, documentation_query_metric)

        # Validate results
        self.assertIsNotNone(result)
        self.assertIsInstance(result, OptimizationResult)
        self.assertIsInstance(result.success, bool)
        self.assertIsInstance(result.performance_improvement, float)
        self.assertIsInstance(result.examples_used, int)

        print("\nDocumentation Query Optimization Results:")
        print(f"  Success: {result.success}")
        print(f"  Performance Improvement: {result.performance_improvement:.4f}")
        print(f"  Examples Used: {result.examples_used}")
        print(f"  Optimization Time: {result.optimization_time:.2f}s")

        if result.metrics:
            print(f"  Baseline Score: {result.metrics['baseline_score']:.4f}")
            print(f"  Optimized Score: {result.metrics['optimized_score']:.4f}")
            print(f"  Improvement %: {result.metrics['improvement_percentage']:.2f}%")

    def test_optimization_across_models(self):
        """Test optimization performance across different models"""
        if not self.switcher.optimizer_enabled:
            self.skipTest("Optimizer system not available")

        models_to_test = [LocalModel.LLAMA_3_1_8B, LocalModel.MISTRAL_7B, LocalModel.PHI_3_5_3_8B]
        module = TaskAnalysisModule()

        results = {}

        for model in models_to_test:
            with self.subTest(model=model):
                # Switch to model
                success = self.switcher.switch_model(model)
                self.assertTrue(success)

                # Run optimization
                result = self.optimizer.optimize_program(module, self.task_analysis_examples, task_analysis_metric)

                results[model.value] = result

                print(f"\n{model.value} Optimization Results:")
                print(f"  Success: {result.success}")
                print(f"  Performance Improvement: {result.performance_improvement:.4f}")
                print(f"  Examples Used: {result.examples_used}")

                if result.metrics:
                    print(f"  Baseline Score: {result.metrics['baseline_score']:.4f}")
                    print(f"  Optimized Score: {result.metrics['optimized_score']:.4f}")
                    print(f"  Improvement %: {result.metrics['improvement_percentage']:.2f}%")

        # Compare results across models
        print("\nCross-Model Comparison:")
        for model_name, result in results.items():
            improvement = result.performance_improvement
            print(f"  {model_name}: {improvement:.4f} improvement")

    def test_optimization_with_validation_data(self):
        """Test optimization with separate validation dataset"""
        if not self.switcher.optimizer_enabled:
            self.skipTest("Optimizer system not available")

        # Create validation examples
        validation_examples = [
            Example(
                inputs={"task_description": "Implement user authentication system", "complexity": "complex"},
                outputs={
                    "analysis": "This task involves implementing a complete user authentication system with security best practices.",
                    "approach": "Use secure authentication libraries, implement password hashing, add session management, and include security testing.",
                    "estimated_time": "10-15 hours",
                },
            ),
            Example(
                inputs={"task_description": "Create a simple web page", "complexity": "simple"},
                outputs={
                    "analysis": "This task involves creating a basic web page with HTML and CSS.",
                    "approach": "Design layout, write HTML structure, add CSS styling, and test in different browsers.",
                    "estimated_time": "2-3 hours",
                },
            ),
        ]

        module = TaskAnalysisModule()

        # Run optimization with validation
        result = self.optimizer.optimize_program(
            module, self.task_analysis_examples, task_analysis_metric, validation_examples
        )

        # Validate results
        self.assertIsNotNone(result)
        self.assertIsInstance(result, OptimizationResult)

        print("\nOptimization with Validation Results:")
        print(f"  Success: {result.success}")
        print(f"  Performance Improvement: {result.performance_improvement:.4f}")
        print(f"  Examples Used: {result.examples_used}")
        print(f"  Validation Examples: {len(validation_examples)}")

        if result.metrics:
            print(f"  Baseline Score: {result.metrics['baseline_score']:.4f}")
            print(f"  Optimized Score: {result.metrics['optimized_score']:.4f}")
            print(f"  Improvement %: {result.metrics['improvement_percentage']:.2f}%")

    def test_optimization_statistics(self):
        """Test optimization statistics collection"""
        if not self.switcher.optimizer_enabled:
            self.skipTest("Optimizer system not available")

        module = TaskAnalysisModule()

        # Run multiple optimizations
        for i in range(3):
            self.optimizer.optimize_program(module, self.task_analysis_examples, task_analysis_metric)

        # Get statistics
        stats = self.optimizer.get_optimization_stats()

        # Validate statistics
        self.assertIn("total_optimizations", stats)
        self.assertIn("successful_optimizations", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("average_improvement", stats)
        self.assertIn("total_optimization_time", stats)
        self.assertIn("average_optimization_time", stats)

        self.assertEqual(stats["total_optimizations"], 3)
        self.assertGreaterEqual(stats["successful_optimizations"], 0)
        self.assertGreaterEqual(stats["success_rate"], 0.0)
        self.assertLessEqual(stats["success_rate"], 1.0)

        print("\nOptimization Statistics:")
        print(f"  Total optimizations: {stats['total_optimizations']}")
        print(f"  Successful optimizations: {stats['successful_optimizations']}")
        print(f"  Success rate: {stats['success_rate']:.2%}")
        print(f"  Average improvement: {stats['average_improvement']:.4f}")
        print(f"  Total optimization time: {stats['total_optimization_time']:.2f}s")
        print(f"  Average optimization time: {stats['average_optimization_time']:.2f}s")


if __name__ == "__main__":
    unittest.main()
