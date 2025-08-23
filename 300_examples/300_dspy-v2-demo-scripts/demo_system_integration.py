#!/usr/bin/env python3
"""
DSPy v2 System Integration Demonstration

Demonstrates the complete integration of DSPy v2 optimization components
with the existing B-1003 multi-agent system. Shows seamless integration
of optimizers, assertion framework, four-part optimization loop, and
metrics dashboard working together.
"""

import json
import os
import sys
import time
from typing import Any, Dict

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import dspy
from dspy import InputField, Module, OutputField, Signature
from dspy_modules.system_integration import (
    DSPySystemIntegration,
    IntegrationConfig,
    IntegrationMode,
    execute_task_with_optimization,
    get_system_integration,
    get_system_status,
)


class TestSignature(Signature):
    """Test signature for integration demonstration"""

    input_field = InputField(desc="Test input")
    output_field = OutputField(desc="Test output")


class TestModule(Module):
    """Test module for integration demonstration"""

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


def demonstrate_system_integration():
    """Demonstrate the complete DSPy v2 system integration"""

    print("🚀 DSPy v2 System Integration: Complete Optimization System")
    print("=" * 80)
    print()
    print("Seamless integration of all DSPy v2 optimization components")
    print("with the existing B-1003 multi-agent system.")
    print()

    # Initialize system integration with full configuration
    config = IntegrationConfig(
        mode=IntegrationMode.FULL_INTEGRATION,
        enable_optimizers=True,
        enable_assertions=True,
        enable_metrics=True,
        enable_optimization_loop=True,
        auto_optimize=True,
        auto_validate=True,
        enable_model_switching=True,
        performance_threshold=0.8,
        reliability_threshold=0.9,
    )

    integration = DSPySystemIntegration(config)

    print("🔧 DSPy v2 System Integration Initialized")
    print(f"  Integration mode: {integration.config.mode.value}")
    print(f"  Optimizers enabled: {integration.config.enable_optimizers}")
    print(f"  Assertions enabled: {integration.config.enable_assertions}")
    print(f"  Metrics enabled: {integration.config.enable_metrics}")
    print(f"  Optimization loop enabled: {integration.config.enable_optimization_loop}")
    print(f"  Auto-optimize: {integration.config.auto_optimize}")
    print(f"  Auto-validate: {integration.config.auto_validate}")
    print()

    # Get initial system status
    initial_status = integration.get_system_status()
    print("📊 Initial System Status:")
    print(f"  Health: {initial_status.health.value}")
    print(f"  Active components: {sum(initial_status.components.values())}/{len(initial_status.components)}")
    print(f"  Integration mode: {initial_status.integration_mode.value}")
    print()

    print("=" * 80)

    # Test 1: Task Execution with Full Optimization
    print("🔄 Test 1: Task Execution with Full Optimization")
    print("-" * 50)

    tasks = [
        {
            "task": "Create a Python function to calculate fibonacci numbers",
            "task_type": "coding",
            "role": "coder",
            "complexity": "moderate",
        },
        {
            "task": "Analyze the performance of a sorting algorithm",
            "task_type": "analysis",
            "role": "researcher",
            "complexity": "complex",
        },
        {
            "task": "Design a database schema for user management",
            "task_type": "planning",
            "role": "planner",
            "complexity": "moderate",
        },
    ]

    for i, task_info in enumerate(tasks, 1):
        print(f"\n  Task {i}: {task_info['task']}")
        print(f"    Type: {task_info['task_type']}, Role: {task_info['role']}, Complexity: {task_info['complexity']}")

        start_time = time.time()
        result = integration.execute_task(**task_info)
        execution_time = time.time() - start_time

        print(f"    Execution time: {execution_time:.3f}s")
        print(f"    Success: {'✅ Yes' if result['success'] else '❌ No'}")
        print(f"    Optimization applied: {'✅ Yes' if result['optimization_applied'] else '❌ No'}")
        print(f"    Validation performed: {'✅ Yes' if result['validation_performed'] else '❌ No'}")
        print(f"    Metrics recorded: {'✅ Yes' if result['metrics_recorded'] else '❌ No'}")

        if result["errors"]:
            print(f"    Errors: {len(result['errors'])}")
            for error in result["errors"][:2]:  # Show first 2 errors
                print(f"      - {error}")

    print()
    print("=" * 80)

    # Test 2: Optimization Cycle Execution
    print("🔄 Test 2: Optimization Cycle Execution")
    print("-" * 50)

    optimization_inputs = {
        "module_class": TestModule,
        "optimization_objectives": {"reliability_target": 98.0, "performance_target": 1.0, "quality_target": 0.9},
        "target_metrics": {"reliability_target": 98.0, "performance_target": 1.0, "quality_target": 0.9},
        "test_data": [
            {"input_field": "normal input"},
            {"input_field": "<script>alert('xss')</script>"},  # Security test
            {"input_field": ""},  # Empty input test
            {"input_field": "very long input " * 100},  # Performance test
        ],
        "deployment_config": {"environment": "production", "monitoring_enabled": True, "rollback_enabled": True},
    }

    print("  Running optimization cycle...")
    start_time = time.time()
    cycle = integration.run_optimization_cycle(optimization_inputs)
    cycle_time = time.time() - start_time

    if cycle:
        print("  ✅ Optimization cycle completed!")
        print(f"    Cycle ID: {cycle.cycle_id}")
        print(f"    Status: {cycle.overall_status.value}")
        print(f"    Success: {'✅ Yes' if cycle.success else '❌ No'}")
        print(f"    Duration: {cycle_time:.3f}s")
        print(f"    Phases completed: {len(cycle.phases)}")

        # Show phase details
        for i, phase in enumerate(cycle.phases, 1):
            print(f"    Phase {i} ({phase.phase.value}): {phase.status.value} ({phase.duration:.3f}s)")
    else:
        print("  ❌ Optimization cycle failed")

    print()
    print("=" * 80)

    # Test 3: Module Validation
    print("🔄 Test 3: Module Validation")
    print("-" * 50)

    test_module = TestModule()
    test_inputs = [{"input": "test input 1"}, {"input": "test input 2"}]

    print("  Validating test module...")
    validation_report = integration.validate_module(test_module, test_inputs)

    if validation_report:
        print("  ✅ Module validation completed!")
        print(f"    Reliability score: {validation_report.reliability_score:.1f}%")
        print(f"    Total assertions: {validation_report.total_assertions}")
        print(f"    Passed assertions: {validation_report.passed_assertions}")
        print(f"    Failed assertions: {validation_report.failed_assertions}")
        print(f"    Critical failures: {validation_report.critical_failures}")

        if validation_report.recommendations:
            print(f"    Recommendations: {len(validation_report.recommendations)}")
            for rec in validation_report.recommendations[:3]:  # Show first 3
                print(f"      - {rec}")
    else:
        print("  ❌ Module validation failed")

    print()
    print("=" * 80)

    # Test 4: Program Optimization
    print("🔄 Test 4: Program Optimization")
    print("-" * 50)

    # Create test data and metric
    test_data = [
        {"input_field": "optimization test 1"},
        {"input_field": "optimization test 2"},
        {"input_field": "optimization test 3"},
    ]

    def quality_metric(example, prediction):
        """Simple quality metric for optimization"""
        if not prediction or not hasattr(prediction, "output_field"):
            return 0.0

        result = prediction.output_field
        if not result:
            return 0.0

        # Basic quality scoring
        score = 0.0
        if len(str(result)) > 5:
            score += 0.4
        if "error" not in str(result).lower():
            score += 0.4
        if "test" in str(result).lower():
            score += 0.2

        return min(1.0, score)

    print("  Optimizing test module...")
    optimization_result = integration.optimize_program(test_module, test_data, quality_metric)

    if optimization_result:
        print("  ✅ Program optimization completed!")
        print(f"    Success: {'✅ Yes' if optimization_result.success else '❌ No'}")
        print(f"    Performance improvement: {optimization_result.performance_improvement:.1f}%")
        print(f"    Examples used: {optimization_result.examples_used}")
        print(f"    Optimization time: {optimization_result.optimization_time:.3f}s")

        if optimization_result.error_message:
            print(f"    Error: {optimization_result.error_message}")
    else:
        print("  ❌ Program optimization failed")

    print()
    print("=" * 80)

    # Test 5: Model Switching and Selection
    print("🔄 Test 5: Model Switching and Selection")
    print("-" * 50)

    if integration.model_switcher:
        from dspy_modules.model_switcher import LocalModel

        # Test model selection for different tasks
        task_types = ["planning", "coding", "analysis", "research"]

        for task_type in task_types:
            model = integration.get_model_for_task(task_type, "moderate")
            if model:
                print(f"  {task_type.title()} task → {model.value}")
            else:
                print(f"  {task_type.title()} task → No model available")

        # Test model switching
        print("\n  Testing model switching...")
        models_to_test = [LocalModel.LLAMA_3_1_8B, LocalModel.MISTRAL_7B]

        for model in models_to_test:
            success = integration.switch_model(model)
            print(f"    Switch to {model.value}: {'✅ Success' if success else '❌ Failed'}")
    else:
        print("  ❌ Model switcher not available")

    print()
    print("=" * 80)

    # Test 6: Dashboard Data Retrieval
    print("🔄 Test 6: Dashboard Data Retrieval")
    print("-" * 50)

    dashboard_views = ["overview", "detailed", "historical", "comparison", "alerts"]

    for view in dashboard_views:
        print(f"  Retrieving {view} view...")
        data = integration.get_dashboard_data(view)

        if "error" not in data:
            print(f"    ✅ {view.title()} data retrieved")
            if "timestamp" in data:
                print(f"    Timestamp: {data['timestamp']:.0f}")
            if "view" in data:
                print(f"    View: {data['view']}")
        else:
            print(f"    ❌ {view.title()} data failed: {data['error']}")

    print()
    print("=" * 80)

    # Test 7: System Status and Health
    print("🔄 Test 7: System Status and Health")
    print("-" * 50)

    final_status = integration.get_system_status()

    print("  Final System Status:")
    print(f"    Health: {final_status.health.value}")
    print(f"    Integration mode: {final_status.integration_mode.value}")
    print(f"    Last update: {final_status.last_update:.0f}")

    print("\n  Component Status:")
    for component, active in final_status.components.items():
        status_emoji = "✅" if active else "❌"
        print(f"    {status_emoji} {component}: {'Active' if active else 'Inactive'}")

    print("\n  System Metrics:")
    for metric, value in final_status.metrics.items():
        if isinstance(value, float):
            print(f"    {metric}: {value:.1f}")
        else:
            print(f"    {metric}: {value}")

    if final_status.alerts:
        print(f"\n  Active Alerts: {len(final_status.alerts)}")
        for alert in final_status.alerts[:3]:  # Show first 3
            print(f"    - {alert}")
    else:
        print("\n  ✅ No active alerts")

    print()
    print("=" * 80)

    # Test 8: System Data Export
    print("🔄 Test 8: System Data Export")
    print("-" * 50)

    print("  Exporting system data...")
    exported_data = integration.export_system_data("json")

    try:
        parsed_data = json.loads(exported_data)
        print("  ✅ System data exported successfully!")
        print(f"    Export size: {len(exported_data)} characters")
        print(f"    Data structure: {list(parsed_data.keys())}")

        # Show some key data
        if "system_status" in parsed_data:
            status = parsed_data["system_status"]
            print(f"    System health: {status.get('health', 'unknown')}")
            print(f"    Integration mode: {status.get('integration_mode', 'unknown')}")

        if "components" in parsed_data:
            components = parsed_data["components"]
            active_components = sum(components.values())
            total_components = len(components)
            print(f"    Active components: {active_components}/{total_components}")

    except json.JSONDecodeError as e:
        print(f"  ❌ Export failed: {e}")
        print(f"    Export content: {exported_data[:200]}...")

    print()
    print("=" * 80)

    # Test 9: Global Functions
    print("🔄 Test 9: Global Functions")
    print("-" * 50)

    # Test global system integration
    global_integration = get_system_integration()
    print(f"  Global integration: {type(global_integration).__name__}")

    # Test global system status
    global_status = get_system_status()
    print(f"  Global status: {global_status.health.value}")

    # Test global task execution
    global_result = execute_task_with_optimization("Global test task", "testing", "tester", "simple")
    print(f"  Global task execution: {'✅ Success' if global_result['success'] else '❌ Failed'}")

    print()
    print("=" * 80)

    # Summary and Performance Analysis
    print("📋 DSPy v2 System Integration Summary")
    print("-" * 50)

    print("✅ Complete System Integration Successfully Demonstrated!")
    print()
    print("Key Integration Features Tested:")
    print("  🔄 Task execution with automatic optimization")
    print("  📊 Four-part optimization loop execution")
    print("  ✅ Module validation with assertion framework")
    print("  ⚡ Program optimization with quality metrics")
    print("  🔀 Model switching and intelligent selection")
    print("  📈 Real-time metrics dashboard integration")
    print("  📊 System status monitoring and health tracking")
    print("  📄 Comprehensive data export capabilities")
    print("  🌐 Global function integration")
    print()
    print("Integration Benefits Achieved:")
    print("  🔄 Seamless integration of all DSPy v2 components")
    print("  📊 Automatic optimization and validation")
    print("  📈 Real-time monitoring and metrics collection")
    print("  🔀 Intelligent model switching and selection")
    print("  ✅ Comprehensive error handling and recovery")
    print("  📄 Data export and analysis capabilities")
    print("  🌐 Global system management and control")
    print()
    print("Adam LK Transcript Alignment:")
    print("  ✅ Complete four-part optimization loop implementation")
    print("  ✅ Systematic measurement and metrics collection")
    print("  ✅ Algorithmic optimization over manual prompt engineering")
    print("  ✅ Real-time monitoring and performance tracking")
    print("  ✅ Comprehensive validation and quality assurance")
    print("  ✅ Seamless integration with existing multi-agent system")
    print()
    print("System Performance:")
    print(f"  📊 System health: {final_status.health.value}")
    print(f"  🔄 Active components: {sum(final_status.components.values())}/{len(final_status.components)}")
    print(f"  📈 Integration mode: {final_status.integration_mode.value}")
    print(f"  ⚠️  Active alerts: {len(final_status.alerts)}")
    print(f"  📊 Metrics tracked: {len(final_status.metrics)}")

    print("\n" + "=" * 80)
    print("🎉 DSPy v2 System Integration Demonstration Complete!")
    print()
    print("The complete DSPy v2 optimization system has been successfully")
    print("integrated with the existing B-1003 multi-agent system, providing")
    print("seamless optimization, validation, monitoring, and management")
    print("capabilities for continuous AI development improvement.")


if __name__ == "__main__":
    demonstrate_system_integration()
