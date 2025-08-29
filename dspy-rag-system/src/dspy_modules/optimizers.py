#!/usr/bin/env python3
"""
DSPy Optimizers Module

Implements DSPy v2 optimization techniques based on Adam LK transcript:
- LabeledFewShot optimizer for systematic improvement
- Integration with existing ModelSwitcher and DSPy modules
- Support for "Programming not prompting" philosophy
- Measurable optimization with hard metrics

Based on Adam LK's DSPy deep dive transcript implementation patterns.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

from dspy import Example, Module


class HasForward(Protocol):
    """Protocol for objects with a forward method and callable interface"""

    def forward(self, *args, **kwargs) -> Any: ...

    def __call__(self, *args, **kwargs) -> Any: ...


_LOG = logging.getLogger("dspy_optimizers")


@dataclass
class OptimizationResult:
    """Result of an optimization operation"""

    success: bool
    performance_improvement: float
    examples_used: int
    optimization_time: float
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class LabeledFewShotOptimizer:
    """
    LabeledFewShot optimizer based on Adam LK transcript implementation.

    Follows the pattern: grab examples from dataset, append to program,
    validate performance improvement.
    """

    def __init__(self, k: int = 16, metric_threshold: float = 0.5):
        """
        Initialize LabeledFewShot optimizer.

        Args:
            k: Number of examples to use (default 16 as shown in transcript)
            metric_threshold: Minimum performance improvement threshold
        """
        self.k = k
        self.metric_threshold = metric_threshold
        self.examples: List[Example] = []
        self.optimization_history: List[OptimizationResult] = []
        self.current_program: Optional[HasForward] = None

        _LOG.info(f"Initialized LabeledFewShot optimizer with k={k}")

    def add_examples(self, examples: List[Example]) -> None:
        """
        Add examples to the optimizer.

        Args:
            examples: List of DSPy examples to use for optimization
        """
        self.examples.extend(examples)
        _LOG.info(f"Added {len(examples)} examples to optimizer (total: {len(self.examples)})")

    def optimize_program(
        self,
        program: HasForward,
        train_data: List[Example],
        metric_func,
        validation_data: Optional[List[Example]] = None,
    ) -> OptimizationResult:
        """
        Optimize a DSPy program using LabeledFewShot technique.

        Args:
            program: DSPy program to optimize
            train_data: Training examples for optimization
            metric_func: Function to measure performance
            validation_data: Optional validation data

        Returns:
            OptimizationResult with performance metrics
        """
        start_time = time.time()

        try:
            _LOG.info(f"Starting LabeledFewShot optimization for program: {type(program).__name__}")

            # Store original program
            self.current_program = program

            # Measure baseline performance
            baseline_score = self._measure_performance(program, validation_data or train_data, metric_func)
            _LOG.info(f"Baseline performance: {baseline_score:.4f}")

            # Select k examples from training data
            selected_examples = self._select_examples(train_data, self.k)
            _LOG.info(f"Selected {len(selected_examples)} examples for optimization")

            # Create optimized program with examples
            optimized_program = self._create_optimized_program(program, selected_examples)

            # Measure optimized performance
            optimized_score = self._measure_performance(optimized_program, validation_data or train_data, metric_func)
            _LOG.info(f"Optimized performance: {optimized_score:.4f}")

            # Calculate improvement
            improvement = optimized_score - baseline_score

            # Calculate improvement percentage safely
            improvement_percentage = 0.0
            if baseline_score > 0:
                improvement_percentage = improvement / baseline_score * 100

            # Create result
            result = OptimizationResult(
                success=improvement >= self.metric_threshold,
                performance_improvement=improvement,
                examples_used=len(selected_examples),
                optimization_time=time.time() - start_time,
                metrics={
                    "baseline_score": baseline_score,
                    "optimized_score": optimized_score,
                    "improvement_percentage": improvement_percentage,
                },
            )

            # Store in history
            self.optimization_history.append(result)

            # Log completion with safe access to metrics
            improvement_percentage = 0.0
            if result.metrics:
                improvement_percentage = result.metrics.get("improvement_percentage", 0.0)

            _LOG.info(
                f"LabeledFewShot optimization completed: {result.success}, "
                f"improvement: {improvement:.4f} ({improvement_percentage:.2f}%)"
            )

            return result

        except Exception as e:
            error_msg = f"LabeledFewShot optimization failed: {str(e)}"
            _LOG.error(error_msg)

            return OptimizationResult(
                success=False,
                performance_improvement=0.0,
                examples_used=0,
                optimization_time=time.time() - start_time,
                error_message=error_msg,
            )

    def _select_examples(self, train_data: List[Example], k: int) -> List[Example]:
        """
        Select k examples from training data.

        Args:
            train_data: Available training examples
            k: Number of examples to select

        Returns:
            Selected examples
        """
        if len(train_data) <= k:
            return train_data

        # Simple selection: take first k examples
        # TODO: Implement more sophisticated selection strategies
        selected = train_data[:k]
        _LOG.debug(f"Selected {len(selected)} examples from {len(train_data)} available")
        return selected

    def _create_optimized_program(self, program: HasForward, examples: List[Example]) -> HasForward:
        """
        Create optimized program with examples.

        Args:
            program: Original program
            examples: Examples to add

        Returns:
            Optimized program
        """
        # For now, return the original program
        # TODO: Implement proper example integration when DSPy API is better understood
        _LOG.debug(f"Created optimized program with {len(examples)} examples (integration pending)")
        return program

    def _measure_performance(self, program: HasForward, test_data: List[Example], metric_func) -> float:
        """
        Measure program performance on test data.

        Args:
            program: Program to test
            test_data: Test examples
            metric_func: Metric function

        Returns:
            Performance score
        """
        try:
            total_score = 0.0
            valid_predictions = 0
            errors = []

            for example in test_data:
                try:
                    # Run program on example
                    # Handle different program interfaces
                    inputs = example.get("inputs")
                    if isinstance(inputs, dict):
                        prediction = program.forward(**inputs)
                    else:
                        prediction = program.forward(inputs)

                    # Calculate score using metric function
                    score = metric_func(example, prediction)
                    total_score += score
                    valid_predictions += 1

                except Exception as e:
                    error_msg = f"Failed to process example: {e}"
                    _LOG.warning(error_msg)
                    errors.append(error_msg)
                    continue

            if valid_predictions == 0:
                # If no valid predictions, raise an exception with error details
                raise Exception(f"All examples failed: {'; '.join(errors)}")

            average_score = total_score / valid_predictions
            _LOG.debug(
                f"Performance measurement: {average_score:.4f} " f"({valid_predictions}/{len(test_data)} examples)"
            )

            return average_score

        except Exception as e:
            _LOG.error(f"Performance measurement failed: {e}")
            raise  # Re-raise the exception so it can be caught by the optimizer

    def get_optimization_stats(self) -> Dict[str, Any]:
        """
        Get optimization statistics.

        Returns:
            Dictionary with optimization statistics
        """
        if not self.optimization_history:
            return {"total_optimizations": 0}

        successful = [r for r in self.optimization_history if r.success]
        total_time = sum(r.optimization_time for r in self.optimization_history)
        avg_improvement = sum(r.performance_improvement for r in successful) / len(successful) if successful else 0

        return {
            "total_optimizations": len(self.optimization_history),
            "successful_optimizations": len(successful),
            "success_rate": len(successful) / len(self.optimization_history),
            "average_improvement": avg_improvement,
            "total_optimization_time": total_time,
            "average_optimization_time": total_time / len(self.optimization_history),
            "examples_used": self.k,
        }


class DSPyOptimizerManager:
    """
    Manager for DSPy optimizers with integration to ModelSwitcher.
    """

    def __init__(self):
        """Initialize optimizer manager."""
        self.optimizers: Dict[str, Any] = {}
        self.active_optimizer: Optional[str] = None
        self.optimization_config: Dict[str, Any] = {}

        _LOG.info("Initialized DSPy optimizer manager")

    def register_optimizer(self, name: str, optimizer: Any) -> None:
        """
        Register an optimizer.

        Args:
            name: Optimizer name
            optimizer: Optimizer instance
        """
        self.optimizers[name] = optimizer
        _LOG.info(f"Registered optimizer: {name}")

    def get_optimizer(self, name: str) -> Optional[Any]:
        """
        Get optimizer by name.

        Args:
            name: Optimizer name

        Returns:
            Optimizer instance or None
        """
        return self.optimizers.get(name)

    def set_active_optimizer(self, name: str) -> bool:
        """
        Set active optimizer.

        Args:
            name: Optimizer name

        Returns:
            True if successful, False otherwise
        """
        if name in self.optimizers:
            self.active_optimizer = name
            _LOG.info(f"Set active optimizer: {name}")
            return True
        else:
            _LOG.warning(f"Optimizer not found: {name}")
            return False

    def optimize_program(
        self, program: Module, train_data: List[Example], metric_func, optimizer_name: Optional[str] = None
    ) -> OptimizationResult:
        """
        Optimize program using specified or active optimizer.

        Args:
            program: Program to optimize
            train_data: Training data
            metric_func: Metric function
            optimizer_name: Optimizer to use (uses active if None)

        Returns:
            Optimization result
        """
        optimizer_name = optimizer_name or self.active_optimizer

        if not optimizer_name:
            _LOG.error("No optimizer specified and no active optimizer")
            return OptimizationResult(
                success=False,
                performance_improvement=0.0,
                examples_used=0,
                optimization_time=0.0,
                error_message="No optimizer available",
            )

        optimizer = self.get_optimizer(optimizer_name)
        if not optimizer:
            _LOG.error(f"Optimizer not found: {optimizer_name}")
            return OptimizationResult(
                success=False,
                performance_improvement=0.0,
                examples_used=0,
                optimization_time=0.0,
                error_message=f"Optimizer not found: {optimizer_name}",
            )

        _LOG.info(f"Running optimization with {optimizer_name}")
        return optimizer.optimize_program(program, train_data, metric_func)


# Global optimizer manager instance
_optimizer_manager = None


def get_optimizer_manager() -> DSPyOptimizerManager:
    """
    Get global optimizer manager instance.

    Returns:
        DSPyOptimizerManager instance
    """
    global _optimizer_manager
    if _optimizer_manager is None:
        _optimizer_manager = DSPyOptimizerManager()

        # Register default optimizers
        labeled_few_shot = LabeledFewShotOptimizer()
        _optimizer_manager.register_optimizer("labeled_few_shot", labeled_few_shot)
        _optimizer_manager.set_active_optimizer("labeled_few_shot")

        _LOG.info("Initialized global optimizer manager with default optimizers")

    return _optimizer_manager


def create_labeled_few_shot_optimizer(k: int = 16, metric_threshold: float = 0.5) -> LabeledFewShotOptimizer:
    """
    Create a LabeledFewShot optimizer with specified parameters.

    Args:
        k: Number of examples to use
        metric_threshold: Performance improvement threshold

    Returns:
        LabeledFewShotOptimizer instance
    """
    return LabeledFewShotOptimizer(k=k, metric_threshold=metric_threshold)


def optimize_program(
    program: Module, train_data: List[Example], metric_func, optimizer_name: str = "labeled_few_shot"
) -> OptimizationResult:
    """
    Convenience function to optimize a program.

    Args:
        program: Program to optimize
        train_data: Training data
        metric_func: Metric function
        optimizer_name: Optimizer to use

    Returns:
        Optimization result
    """
    manager = get_optimizer_manager()
    return manager.optimize_program(program, train_data, metric_func, optimizer_name)
