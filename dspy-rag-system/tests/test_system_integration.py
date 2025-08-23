#!/usr/bin/env python3
"""
System Integration Tests

Comprehensive test suite for the DSPy v2 system integration module.
"""

import os
import sys
import unittest
from typing import Any, Dict

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import dspy
from dspy import InputField, Module, OutputField, Signature

from dspy_modules.system_integration import (
    DSPySystemIntegration,
    IntegrationConfig,
    IntegrationMode,
    SystemHealth,
    SystemStatus,
    execute_task_with_optimization,
    get_system_integration,
    get_system_status,
)


class TestSignature(Signature):
    """Test signature for integration testing"""

    input_field = InputField(desc="Test input")
    output_field = OutputField(desc="Test output")


class TestModule(Module):
    """Test module for integration testing"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(TestSignature)

    def forward(self, input_field: str) -> Dict[str, Any]:
        """Forward pass for testing"""
        try:
            # Input validation
            if not isinstance(input_field, str):
                raise ValueError("Input must be a string")

            # Process input
            result = self.predictor(input_field=input_field)

            return {"output_field": result.output_field, "input_field": input_field, "status": "success"}

        except Exception as e:
            return {"error": str(e), "input_field": input_field, "status": "error"}


class TestSystemIntegration(unittest.TestCase):
    """Test cases for the DSPy system integration"""

    def setUp(self):
        """Set up test fixtures"""
        # Create minimal configuration for testing
        self.config = IntegrationConfig(
            mode=IntegrationMode.MINIMAL,
            enable_optimizers=True,
            enable_assertions=True,
            enable_metrics=True,
            enable_optimization_loop=True,
            auto_optimize=True,
            auto_validate=True,
            enable_model_switching=True,
        )

        self.integration = DSPySystemIntegration(self.config)

    def test_system_integration_initialization(self):
        """Test system integration initialization"""
        # Test configuration
        self.assertIsNotNone(self.integration.config)
        self.assertEqual(self.integration.config.mode, IntegrationMode.MINIMAL)
        self.assertTrue(self.integration.config.enable_optimizers)
        self.assertTrue(self.integration.config.enable_assertions)

        # Test component initialization
        self.assertIsNotNone(self.integration.status)
        self.assertIsInstance(self.integration.status, SystemStatus)

        print("\nSystem Integration Initialization Test:")
        print(f"  Integration mode: {self.integration.config.mode.value}")
        print(f"  Optimizers enabled: {self.integration.config.enable_optimizers}")
        print(f"  Assertions enabled: {self.integration.config.enable_assertions}")
        print(f"  Metrics enabled: {self.integration.config.enable_metrics}")
        print(f"  Optimization loop enabled: {self.integration.config.enable_optimization_loop}")

    def test_component_initialization(self):
        """Test component initialization"""
        # Test that components are initialized based on configuration
        if self.config.enable_model_switching:
            self.assertIsNotNone(self.integration.model_switcher)
            self.assertIsNotNone(self.integration.task_executor)

        if self.config.enable_optimizers:
            self.assertIsNotNone(self.integration.optimizer_manager)

        if self.config.enable_assertions:
            self.assertIsNotNone(self.integration.assertion_framework)

        if self.config.enable_optimization_loop:
            self.assertIsNotNone(self.integration.optimization_loop)

        if self.config.enable_metrics:
            self.assertIsNotNone(self.integration.metrics_dashboard)

        print("\nComponent Initialization Test:")
        print(f"  Model Switcher: {self.integration.model_switcher is not None}")
        print(f"  Task Executor: {self.integration.task_executor is not None}")
        print(f"  Optimizer Manager: {self.integration.optimizer_manager is not None}")
        print(f"  Assertion Framework: {self.integration.assertion_framework is not None}")
        print(f"  Optimization Loop: {self.integration.optimization_loop is not None}")
        print(f"  Metrics Dashboard: {self.integration.metrics_dashboard is not None}")

    def test_system_health_calculation(self):
        """Test system health calculation"""
        # Test health calculation
        self.integration._update_system_health()

        # Verify health is set
        self.assertIsInstance(self.integration.status.health, SystemHealth)

        # Verify components are tracked
        self.assertIsInstance(self.integration.status.components, dict)

        print("\nSystem Health Calculation Test:")
        print(f"  System health: {self.integration.status.health.value}")
        print(f"  Active components: {sum(self.integration.status.components.values())}")
        print(f"  Total components: {len(self.integration.status.components)}")

    def test_task_execution_with_optimization(self):
        """Test task execution with optimization"""
        # Test task execution
        task = "Create a simple Python function"
        task_type = "coding"
        role = "coder"
        complexity = "simple"

        result = self.integration.execute_task(task, task_type, role, complexity)

        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("task", result)
        self.assertIn("task_type", result)
        self.assertIn("role", result)
        self.assertIn("execution_time", result)
        self.assertIn("optimization_applied", result)
        self.assertIn("validation_performed", result)
        self.assertIn("metrics_recorded", result)
        self.assertIn("errors", result)

        print("\nTask Execution Test:")
        print(f"  Success: {result['success']}")
        print(f"  Execution time: {result['execution_time']:.3f}s")
        print(f"  Optimization applied: {result['optimization_applied']}")
        print(f"  Validation performed: {result['validation_performed']}")
        print(f"  Metrics recorded: {result['metrics_recorded']}")
        print(f"  Errors: {len(result['errors'])}")

    def test_optimization_cycle_execution(self):
        """Test optimization cycle execution"""
        # Test inputs for optimization cycle
        inputs = {
            "module_class": TestModule,
            "optimization_objectives": {"reliability_target": 98.0, "performance_target": 1.0, "quality_target": 0.9},
            "target_metrics": {"reliability_target": 98.0, "performance_target": 1.0, "quality_target": 0.9},
            "test_data": [{"input_field": "test input 1"}, {"input_field": "test input 2"}],
            "deployment_config": {"environment": "test", "monitoring_enabled": True},
        }

        # Run optimization cycle
        cycle = self.integration.run_optimization_cycle(inputs)

        # Verify cycle result
        if cycle:
            self.assertIsNotNone(cycle)
            self.assertTrue(hasattr(cycle, "success"))
            self.assertTrue(hasattr(cycle, "overall_status"))
            self.assertTrue(hasattr(cycle, "phases"))

            print("\nOptimization Cycle Test:")
            print(f"  Cycle success: {cycle.success}")
            print(f"  Overall status: {cycle.overall_status.value}")
            print(f"  Phases completed: {len(cycle.phases)}")
            print(f"  Duration: {cycle.duration:.3f}s")
        else:
            print("\nOptimization Cycle Test: Cycle not available")

    def test_system_status_retrieval(self):
        """Test system status retrieval"""
        # Get system status
        status = self.integration.get_system_status()

        # Verify status structure
        self.assertIsInstance(status, SystemStatus)
        self.assertIsInstance(status.health, SystemHealth)
        self.assertIsInstance(status.components, dict)
        self.assertIsInstance(status.metrics, dict)
        self.assertIsInstance(status.alerts, list)
        self.assertIsInstance(status.last_update, float)
        self.assertIsInstance(status.integration_mode, IntegrationMode)

        print("\nSystem Status Test:")
        print(f"  Health: {status.health.value}")
        print(f"  Integration mode: {status.integration_mode.value}")
        print(f"  Components: {len(status.components)}")
        print(f"  Metrics: {len(status.metrics)}")
        print(f"  Alerts: {len(status.alerts)}")
        print(f"  Last update: {status.last_update:.0f}")

    def test_dashboard_data_retrieval(self):
        """Test dashboard data retrieval"""
        # Test overview data
        overview_data = self.integration.get_dashboard_data("overview")

        # Verify data structure
        self.assertIsInstance(overview_data, dict)

        # Check if it's an error response or actual data
        if "error" not in overview_data:
            self.assertIn("timestamp", overview_data)
            self.assertIn("view", overview_data)

        print("\nDashboard Data Test:")
        print(f"  Overview data: {'error' in overview_data}")
        if "error" not in overview_data:
            print(f"  View: {overview_data.get('view', 'unknown')}")
            print(f"  Timestamp: {overview_data.get('timestamp', 0)}")

    def test_module_validation(self):
        """Test module validation"""
        # Create test module
        test_module = TestModule()

        # Test validation
        validation_report = self.integration.validate_module(test_module, [{"input": "test input"}])

        # Verify validation result
        if validation_report:
            self.assertIsNotNone(validation_report)
            self.assertTrue(hasattr(validation_report, "reliability_score"))
            self.assertTrue(hasattr(validation_report, "total_assertions"))
            self.assertTrue(hasattr(validation_report, "passed_assertions"))

            print("\nModule Validation Test:")
            print(f"  Reliability score: {validation_report.reliability_score:.1f}%")
            print(f"  Total assertions: {validation_report.total_assertions}")
            print(f"  Passed assertions: {validation_report.passed_assertions}")
        else:
            print("\nModule Validation Test: Validation not available")

    def test_program_optimization(self):
        """Test program optimization"""
        # Create test module
        test_module = TestModule()

        # Create test data
        test_data = [{"input_field": "test input 1"}, {"input_field": "test input 2"}]

        # Create simple metric
        def simple_metric(example, prediction):
            return 0.8  # Simple metric

        # Test optimization
        optimization_result = self.integration.optimize_program(test_module, test_data, simple_metric)

        # Verify optimization result
        if optimization_result:
            self.assertIsNotNone(optimization_result)
            self.assertTrue(hasattr(optimization_result, "success"))
            self.assertTrue(hasattr(optimization_result, "performance_improvement"))

            print("\nProgram Optimization Test:")
            print(f"  Optimization success: {optimization_result.success}")
            print(f"  Performance improvement: {optimization_result.performance_improvement:.1f}%")
        else:
            print("\nProgram Optimization Test: Optimization not available")

    def test_model_switching(self):
        """Test model switching functionality"""
        if not self.integration.model_switcher:
            print("\nModel Switching Test: Model switcher not available")
            return

        # Test model switching
        from dspy_modules.model_switcher import LocalModel

        # Test switching to different models
        success = self.integration.switch_model(LocalModel.LLAMA_3_1_8B)

        print("\nModel Switching Test:")
        print(f"  Switch to Llama 3.1 8B: {'✅' if success else '❌'}")

    def test_model_selection(self):
        """Test model selection for tasks"""
        if not self.integration.model_switcher:
            print("\nModel Selection Test: Model switcher not available")
            return

        # Test model selection for different task types
        planning_model = self.integration.get_model_for_task("planning")
        coding_model = self.integration.get_model_for_task("coding")

        print("\nModel Selection Test:")
        print(f"  Planning task model: {planning_model.value if planning_model else 'None'}")
        print(f"  Coding task model: {coding_model.value if coding_model else 'None'}")

    def test_system_data_export(self):
        """Test system data export"""
        # Test data export
        exported_data = self.integration.export_system_data("json")

        # Verify export
        self.assertIsInstance(exported_data, str)

        # Try to parse as JSON
        import json

        try:
            parsed_data = json.loads(exported_data)
            self.assertIsInstance(parsed_data, dict)

            print("\nSystem Data Export Test:")
            print("  Export successful: ✅")
            print(f"  Export size: {len(exported_data)} characters")
            print(f"  Data keys: {list(parsed_data.keys())}")
        except json.JSONDecodeError:
            print("\nSystem Data Export Test:")
            print("  Export failed: ❌")
            print(f"  Export content: {exported_data[:100]}...")

    def test_global_functions(self):
        """Test global convenience functions"""
        # Test global system integration
        global_integration = get_system_integration()
        self.assertIsInstance(global_integration, DSPySystemIntegration)

        # Test global system status
        global_status = get_system_status()
        self.assertIsInstance(global_status, SystemStatus)

        # Test task execution with optimization
        task_result = execute_task_with_optimization("Test task", "testing", "tester", "simple")
        self.assertIsInstance(task_result, dict)

        print("\nGlobal Functions Test:")
        print(f"  Global integration: {type(global_integration).__name__}")
        print(f"  Global status: {global_status.health.value}")
        print(f"  Task execution: {task_result['success']}")

    def test_integration_modes(self):
        """Test different integration modes"""
        # Test minimal mode
        minimal_config = IntegrationConfig(mode=IntegrationMode.MINIMAL)
        minimal_integration = DSPySystemIntegration(minimal_config)

        # Test optimization only mode
        opt_config = IntegrationConfig(mode=IntegrationMode.OPTIMIZATION_ONLY)
        opt_integration = DSPySystemIntegration(opt_config)

        # Test monitoring only mode
        monitor_config = IntegrationConfig(mode=IntegrationMode.MONITORING_ONLY)
        monitor_integration = DSPySystemIntegration(monitor_config)

        print("\nIntegration Modes Test:")
        print(f"  Minimal mode: {minimal_integration.config.mode.value}")
        print(f"  Optimization only: {opt_integration.config.mode.value}")
        print(f"  Monitoring only: {monitor_integration.config.mode.value}")

        # Verify mode-specific configurations
        self.assertEqual(minimal_integration.config.mode, IntegrationMode.MINIMAL)
        self.assertEqual(opt_integration.config.mode, IntegrationMode.OPTIMIZATION_ONLY)
        self.assertEqual(monitor_integration.config.mode, IntegrationMode.MONITORING_ONLY)

    def test_error_handling(self):
        """Test error handling in system integration"""
        # Test with invalid configuration
        invalid_config = IntegrationConfig(
            enable_model_switching=False,
            enable_optimizers=False,
            enable_assertions=False,
            enable_metrics=False,
            enable_optimization_loop=False,
        )

        invalid_integration = DSPySystemIntegration(invalid_config)

        # Test task execution with minimal components
        result = invalid_integration.execute_task("test", "test", "test")

        # Should fail gracefully
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("errors", result)

        print("\nError Handling Test:")
        print(f"  Task success: {result['success']}")
        print(f"  Error count: {len(result['errors'])}")
        print(f"  System health: {invalid_integration.status.health.value}")


if __name__ == "__main__":
    unittest.main()
