#!/usr/bin/env python3
"""
Four-Part Optimization Loop Tests

Comprehensive test suite for the Create → Evaluate → Optimize → Deploy workflow.
"""

import os
import sys
import unittest
from typing import Any, Dict

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import dspy
from dspy import InputField, Module, OutputField, Signature

from dspy_modules.optimization_loop import (
    CreatePhase,
    DeployPhase,
    EvaluatePhase,
    FourPartOptimizationLoop,
    OptimizationCycle,
    OptimizationPhase,
    OptimizationStatus,
    OptimizePhase,
    PhaseResult,
    get_optimization_loop,
    run_optimization_cycle,
)


class TestSignature(Signature):
    """Test signature for optimization"""

    input_field = InputField(desc="Test input")
    output_field = OutputField(desc="Test output")


class BaselineModule(Module):
    """Baseline module for testing"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(TestSignature)

    def forward(self, input_field):  # Missing type hints
        # Missing docstring
        result = self.predictor(input_field=input_field)
        return {"output_field": result.output_field}


class OptimizedModule(Module):
    """Optimized module for testing"""

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


class TestOptimizationLoop(unittest.TestCase):
    """Test cases for the four-part optimization loop"""

    def setUp(self):
        """Set up test fixtures"""
        self.loop = FourPartOptimizationLoop()
        self.test_inputs = {
            "module_class": OptimizedModule,
            "optimization_objectives": {"reliability_target": 98.0, "performance_target": 1.0, "quality_target": 0.9},
            "target_metrics": {"reliability_target": 98.0, "performance_target": 1.0, "quality_target": 0.9},
            "test_data": [
                {"input_field": "normal input"},
                {"input_field": "<script>alert('xss')</script>"},
                {"input_field": ""},
                {"input_field": "very long input " * 100},
            ],
            "deployment_config": {"environment": "test", "monitoring_enabled": True},
        }

    def test_create_phase(self):
        """Test the Create phase"""
        create_phase = CreatePhase()
        result = create_phase.execute(self.test_inputs)

        # Validate result
        self.assertIsInstance(result, PhaseResult)
        self.assertEqual(result.phase, OptimizationPhase.CREATE)
        self.assertEqual(result.status, OptimizationStatus.COMPLETED)
        self.assertTrue(result.success)

        # Validate outputs
        self.assertIn("module", result.outputs)
        self.assertIn("objectives", result.outputs)
        self.assertIn("baseline_metrics", result.outputs)

        # Validate metrics
        self.assertIn("module_created", result.metrics)
        self.assertIn("objectives_defined", result.metrics)
        self.assertIn("baseline_reliability", result.metrics)

        self.assertTrue(result.metrics["module_created"])
        self.assertGreater(result.metrics["objectives_defined"], 0)

        print("\nCreate Phase Results:")
        print(f"  Status: {result.status.value}")
        print(f"  Duration: {result.duration:.3f}s")
        print(f"  Module created: {result.metrics['module_created']}")
        print(f"  Objectives defined: {result.metrics['objectives_defined']}")
        print(f"  Baseline reliability: {result.metrics['baseline_reliability']:.1f}%")

    def test_evaluate_phase(self):
        """Test the Evaluate phase"""
        # First create a module
        create_phase = CreatePhase()
        create_result = create_phase.execute(self.test_inputs)

        evaluate_phase = EvaluatePhase()
        evaluate_inputs = {**self.test_inputs, **create_result.outputs}
        result = evaluate_phase.execute(evaluate_inputs)

        # Validate result
        self.assertIsInstance(result, PhaseResult)
        self.assertEqual(result.phase, OptimizationPhase.EVALUATE)
        self.assertEqual(result.status, OptimizationStatus.COMPLETED)
        self.assertTrue(result.success)

        # Validate outputs
        self.assertIn("evaluation_results", result.outputs)
        self.assertIn("gap_analysis", result.outputs)
        self.assertIn("improvement_areas", result.outputs)
        self.assertIn("recommendations", result.outputs)

        # Validate metrics
        self.assertIn("reliability_score", result.metrics)
        self.assertIn("performance_score", result.metrics)
        self.assertIn("quality_score", result.metrics)
        self.assertIn("gap_score", result.metrics)
        self.assertIn("improvement_areas_count", result.metrics)

        print("\nEvaluate Phase Results:")
        print(f"  Status: {result.status.value}")
        print(f"  Duration: {result.duration:.3f}s")
        print(f"  Reliability score: {result.metrics['reliability_score']:.1f}%")
        print(f"  Performance score: {result.metrics['performance_score']:.1f}%")
        print(f"  Quality score: {result.metrics['quality_score']:.1f}%")
        print(f"  Gap score: {result.metrics['gap_score']:.1f}%")
        print(f"  Improvement areas: {result.metrics['improvement_areas_count']}")

    def test_optimize_phase(self):
        """Test the Optimize phase"""
        # First create and evaluate
        create_phase = CreatePhase()
        create_result = create_phase.execute(self.test_inputs)

        evaluate_phase = EvaluatePhase()
        evaluate_inputs = {**self.test_inputs, **create_result.outputs}
        evaluate_result = evaluate_phase.execute(evaluate_inputs)

        optimize_phase = OptimizePhase()
        optimize_inputs = {**evaluate_inputs, **evaluate_result.outputs}
        result = optimize_phase.execute(optimize_inputs)

        # Validate result
        self.assertIsInstance(result, PhaseResult)
        self.assertEqual(result.phase, OptimizationPhase.OPTIMIZE)
        self.assertEqual(result.status, OptimizationStatus.COMPLETED)
        self.assertTrue(result.success)

        # Validate outputs
        self.assertIn("optimized_module", result.outputs)
        self.assertIn("optimization_results", result.outputs)
        self.assertIn("improvement_metrics", result.outputs)

        # Validate metrics
        self.assertIn("optimizations_applied", result.metrics)
        self.assertIn("reliability_improvement", result.metrics)
        self.assertIn("performance_improvement", result.metrics)
        self.assertIn("quality_improvement", result.metrics)
        self.assertIn("overall_improvement", result.metrics)

        print("\nOptimize Phase Results:")
        print(f"  Status: {result.status.value}")
        print(f"  Duration: {result.duration:.3f}s")
        print(f"  Optimizations applied: {result.metrics['optimizations_applied']}")
        print(f"  Reliability improvement: {result.metrics['reliability_improvement']:.1f}%")
        print(f"  Performance improvement: {result.metrics['performance_improvement']:.1f}%")
        print(f"  Quality improvement: {result.metrics['quality_improvement']:.1f}%")
        print(f"  Overall improvement: {result.metrics['overall_improvement']:.1f}%")

    def test_deploy_phase(self):
        """Test the Deploy phase"""
        # First create, evaluate, and optimize
        create_phase = CreatePhase()
        create_result = create_phase.execute(self.test_inputs)

        evaluate_phase = EvaluatePhase()
        evaluate_inputs = {**self.test_inputs, **create_result.outputs}
        evaluate_result = evaluate_phase.execute(evaluate_inputs)

        optimize_phase = OptimizePhase()
        optimize_inputs = {**evaluate_inputs, **evaluate_result.outputs}
        optimize_result = optimize_phase.execute(optimize_inputs)

        deploy_phase = DeployPhase()
        deploy_inputs = {**optimize_inputs, **optimize_result.outputs}
        result = deploy_phase.execute(deploy_inputs)

        # Validate result
        self.assertIsInstance(result, PhaseResult)
        self.assertEqual(result.phase, OptimizationPhase.DEPLOY)
        self.assertEqual(result.status, OptimizationStatus.COMPLETED)
        self.assertTrue(result.success)

        # Validate outputs
        self.assertIn("deployment_results", result.outputs)
        self.assertIn("monitoring_setup", result.outputs)
        self.assertIn("deployment_validation", result.outputs)
        self.assertIn("deployed_module", result.outputs)

        # Validate metrics
        self.assertIn("deployment_success", result.metrics)
        self.assertIn("monitoring_active", result.metrics)
        self.assertIn("validation_passed", result.metrics)
        self.assertIn("deployment_time", result.metrics)

        print("\nDeploy Phase Results:")
        print(f"  Status: {result.status.value}")
        print(f"  Duration: {result.duration:.3f}s")
        print(f"  Deployment success: {result.metrics['deployment_success']}")
        print(f"  Monitoring active: {result.metrics['monitoring_active']}")
        print(f"  Validation passed: {result.metrics['validation_passed']}")
        print(f"  Deployment time: {result.metrics['deployment_time']:.3f}s")

    def test_complete_optimization_cycle(self):
        """Test a complete optimization cycle"""
        result = self.loop.run_cycle(self.test_inputs)

        # Validate result
        self.assertIsInstance(result, OptimizationCycle)
        self.assertTrue(result.success)
        self.assertEqual(result.overall_status, OptimizationStatus.COMPLETED)

        # Validate phases
        self.assertEqual(len(result.phases), 4)
        for phase in result.phases:
            self.assertTrue(phase.success)
            self.assertEqual(phase.status, OptimizationStatus.COMPLETED)

        # Validate overall metrics
        self.assertIn("total_duration", result.overall_metrics)
        self.assertIn("phases_completed", result.overall_metrics)
        self.assertIn("total_phases", result.overall_metrics)
        self.assertIn("success_rate", result.overall_metrics)

        self.assertEqual(result.overall_metrics["total_phases"], 4)
        self.assertEqual(result.overall_metrics["phases_completed"], 4)
        self.assertEqual(result.overall_metrics["success_rate"], 1.0)

        print("\nComplete Optimization Cycle Results:")
        print(f"  Cycle ID: {result.cycle_id}")
        print(f"  Status: {result.overall_status.value}")
        print(f"  Duration: {result.duration:.3f}s")
        print(
            f"  Phases completed: {result.overall_metrics['phases_completed']}/{result.overall_metrics['total_phases']}"
        )
        print(f"  Success rate: {result.overall_metrics['success_rate']:.1%}")

        # Print phase details
        for i, phase in enumerate(result.phases, 1):
            print(f"  Phase {i} ({phase.phase.value}): {phase.status.value} ({phase.duration:.3f}s)")

    def test_optimization_loop_statistics(self):
        """Test optimization loop statistics"""
        # Run multiple cycles
        for i in range(3):
            self.loop.run_cycle(self.test_inputs)

        stats = self.loop.get_statistics()

        # Validate statistics
        self.assertIn("total_cycles", stats)
        self.assertIn("successful_cycles", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("average_duration", stats)
        self.assertIn("recent_cycles", stats)

        self.assertEqual(stats["total_cycles"], 3)
        self.assertEqual(stats["successful_cycles"], 3)
        self.assertEqual(stats["success_rate"], 1.0)
        self.assertGreater(stats["average_duration"], 0.0)
        self.assertEqual(len(stats["recent_cycles"]), 3)

        print("\nOptimization Loop Statistics:")
        print(f"  Total cycles: {stats['total_cycles']}")
        print(f"  Successful cycles: {stats['successful_cycles']}")
        print(f"  Success rate: {stats['success_rate']:.1%}")
        print(f"  Average duration: {stats['average_duration']:.3f}s")
        print(f"  Recent cycles: {stats['recent_cycles']}")

    def test_global_optimization_loop(self):
        """Test global optimization loop instance"""
        loop = get_optimization_loop()
        self.assertIsInstance(loop, FourPartOptimizationLoop)

        # Test convenience function
        result = run_optimization_cycle(self.test_inputs)
        self.assertIsInstance(result, OptimizationCycle)
        self.assertTrue(result.success)

        print("\nGlobal Optimization Loop Test:")
        print(f"  Loop instance: {type(loop).__name__}")
        print(f"  Cycle result: {result.cycle_id}")
        print(f"  Success: {result.success}")

    def test_phase_error_handling(self):
        """Test error handling in phases"""
        # Test with invalid inputs
        invalid_inputs = {"invalid_key": "invalid_value"}

        create_phase = CreatePhase()
        result = create_phase.execute(invalid_inputs)

        # Should fail gracefully
        self.assertIsInstance(result, PhaseResult)
        self.assertEqual(result.status, OptimizationStatus.FAILED)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)

        print("\nError Handling Test:")
        print(f"  Phase: {result.phase.value}")
        print(f"  Status: {result.status.value}")
        print(f"  Error: {result.error_message}")

    def test_cycle_rollback(self):
        """Test cycle rollback functionality"""
        # Run a cycle
        cycle = self.loop.run_cycle(self.test_inputs)

        # Rollback the cycle
        success = self.loop.rollback_cycle(cycle.cycle_id)
        self.assertTrue(success)

        # Check that cycle status changed
        cycle = next((c for c in self.loop.cycles if c.cycle_id == cycle.cycle_id), None)
        self.assertIsNotNone(cycle)
        self.assertEqual(cycle.overall_status, OptimizationStatus.ROLLED_BACK)

        print("\nCycle Rollback Test:")
        print(f"  Cycle ID: {cycle.cycle_id}")
        print(f"  Rollback success: {success}")
        print(f"  Final status: {cycle.overall_status.value}")

    def test_phase_metrics_aggregation(self):
        """Test phase metrics aggregation"""
        result = self.loop.run_cycle(self.test_inputs)

        # Check that phase metrics are aggregated
        overall_metrics = result.overall_metrics

        # Should have metrics from each phase
        phase_metrics = [
            "create_module_created",
            "create_objectives_defined",
            "create_baseline_reliability",
            "evaluate_reliability_score",
            "evaluate_performance_score",
            "evaluate_quality_score",
            "evaluate_gap_score",
            "evaluate_improvement_areas_count",
            "optimize_optimizations_applied",
            "optimize_reliability_improvement",
            "optimize_performance_improvement",
            "optimize_quality_improvement",
            "optimize_overall_improvement",
            "deploy_deployment_success",
            "deploy_monitoring_active",
            "deploy_validation_passed",
            "deploy_deployment_time",
        ]

        for metric in phase_metrics:
            self.assertIn(metric, overall_metrics, f"Missing metric: {metric}")

        print("\nPhase Metrics Aggregation Test:")
        print(f"  Total metrics: {len(overall_metrics)}")
        print(f"  Phase metrics found: {sum(1 for m in phase_metrics if m in overall_metrics)}/{len(phase_metrics)}")

        # Print some key metrics
        key_metrics = [
            "create_baseline_reliability",
            "evaluate_reliability_score",
            "optimize_reliability_improvement",
            "deploy_deployment_success",
        ]

        for metric in key_metrics:
            if metric in overall_metrics:
                print(f"  {metric}: {overall_metrics[metric]}")


if __name__ == "__main__":
    unittest.main()
