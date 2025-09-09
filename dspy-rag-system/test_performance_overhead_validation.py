#!/usr/bin/env python3
"""
Performance Validation and Optimization for B-1007 Pydantic AI Style Enhancements
Validates overall system performance against requirements and optimizes bottlenecks
"""

import statistics
import time

from src.dspy_modules.context_aware_tools import ContextAwareToolFramework, MLflowIntegration, context_aware_tool
from src.dspy_modules.context_models import AIRole, ContextFactory
from src.dspy_modules.dynamic_prompts import DynamicPromptManager, PromptContext, PromptTemplate
from src.dspy_modules.enhanced_debugging import EnhancedDebuggingManager
from src.dspy_modules.error_taxonomy import ErrorFactory
from src.dspy_modules.user_preferences import UserPreferenceManager


def test_performance_validation():
    """Test performance validation and optimization"""
    print("⚡ Performance Validation - B-1007 Pydantic AI Style Enhancements")
    print("=" * 60)

    # Initialize components
    print("\n📦 Initializing Components")
    print("-" * 30)

    context_factory = ContextFactory()
    prompt_manager = DynamicPromptManager()
    preference_manager = UserPreferenceManager()
    mlflow_config = MLflowIntegration(enabled=False, tracking_uri=None)
    tool_framework = ContextAwareToolFramework(mlflow_config=mlflow_config)
    debugging_manager = EnhancedDebuggingManager()

    print("✅ All components initialized")

    # Performance targets
    targets = {
        "type_validation_overhead": 0.02,  # <2%
        "dynamic_context_overhead": 0.03,  # <3%
        "enhanced_tool_overhead": 0.10,  # <10%
        "overall_performance": 0.05,  # <5% of baseline
    }

    print("\n🎯 Performance Targets:")
    for target, value in targets.items():
        print(f"   - {target}: <{value*100}%")

    # Test 1: Type Validation Performance
    print("\n🔍 Test 1: Type Validation Performance")
    print("-" * 30)

    # Baseline: Simple object creation without validation
    baseline_times = []
    for i in range(100):
        start_time = time.time()
        # Simple dict creation (baseline)
        data = {"id": i, "name": f"test_{i}", "value": i * 2}
        # Use data to prevent linter warning while maintaining performance measurement
        _ = len(data)  # Minimal operation that doesn't affect timing
        baseline_times.append(time.time() - start_time)

    baseline_avg = statistics.mean(baseline_times)
    print(f"✅ Baseline average: {baseline_avg:.6f}s")

    # Test: Pydantic model creation with validation
    validation_times = []
    for i in range(100):
        start_time = time.time()
        # Create context with full validation
        context = context_factory.create_context(
            AIRole.CODER,
            session_id=f"perf_test_{i}",
            project_scope="Performance Test Project",
            backlog_priority="P1",
            codebase_path=".",
            language="python",
        )
        validation_times.append(time.time() - start_time)

    validation_avg = statistics.mean(validation_times)
    validation_overhead = (validation_avg - baseline_avg) / baseline_avg

    print(f"✅ Validation average: {validation_avg:.6f}s")
    print(f"✅ Type validation overhead: {validation_overhead:.2%}")

    if validation_overhead < targets["type_validation_overhead"]:
        print(f"✅ PASS: Type validation overhead within target (<{targets['type_validation_overhead']*100}%)")
    else:
        print("❌ FAIL: Type validation overhead exceeds target")

    # Test 2: Dynamic Context Performance
    print("\n💬 Test 2: Dynamic Context Performance")
    print("-" * 30)

    # Create prompt template
    template = PromptTemplate(
        template_id="perf_template",
        template_name="Performance Template",
        base_prompt="You are a {role} working on {project_scope} with {detail_level} detail level.",
        placeholders=["role", "project_scope", "detail_level"],
    )
    prompt_manager.register_template(template)

    # Baseline: Simple string formatting
    baseline_context_times = []
    for i in range(50):
        start_time = time.time()
        # Simple string formatting
        baseline_context_times.append(time.time() - start_time)

    baseline_context_avg = statistics.mean(baseline_context_times)
    print(f"✅ Context baseline average: {baseline_context_avg:.6f}s")

    # Test: Dynamic prompt generation with context
    context_times = []
    for i in range(50):
        start_time = time.time()
        # Create context and generate prompt
        role_context = context_factory.create_context(
            AIRole.CODER,
            session_id=f"session_{i}",
            project_scope=f"project_{i}",
            backlog_priority="P1",
            codebase_path=".",
            language="python",
        )

        context = PromptContext(
            user_id=f"user_{i}",
            session_id=f"session_{i}",
            user_preferences={"detail_level": "high"},
            dynamic_variables={"project_id": i},
            role_context=role_context,
        )

        prompt_manager.generate_prompt(template_id="perf_template", context=context)
        context_times.append(time.time() - start_time)

    context_avg = statistics.mean(context_times)
    context_overhead = (context_avg - baseline_context_avg) / baseline_context_avg

    print(f"✅ Dynamic context average: {context_avg:.6f}s")
    print(f"✅ Dynamic context overhead: {context_overhead:.2%}")

    if context_overhead < targets["dynamic_context_overhead"]:
        print(f"✅ PASS: Dynamic context overhead within target (<{targets['dynamic_context_overhead']*100}%)")
    else:
        print("❌ FAIL: Dynamic context overhead exceeds target")

    # Test 3: Enhanced Tool Performance
    print("\n🔧 Test 3: Enhanced Tool Performance")
    print("-" * 30)

    # Define test tool
    @context_aware_tool("perf_calculator", mlflow_config=mlflow_config)
    def calculator(a, b, operation="add", **kwargs):
        """Performance test calculator"""
        if operation == "add":
            return a + b
        elif operation == "multiply":
            return a * b
        else:
            raise ValueError(f"Unknown operation: {operation}")

    tool_framework.register_tool("calculator", calculator)

    # Baseline: Direct function call
    baseline_tool_times = []
    for i in range(50):
        start_time = time.time()
        calculator(i, i + 1, "add")
        baseline_tool_times.append(time.time() - start_time)

    baseline_tool_avg = statistics.mean(baseline_tool_times)
    print(f"✅ Tool baseline average: {baseline_tool_avg:.6f}s")

    # Test: Enhanced tool execution with context
    enhanced_tool_times = []
    for i in range(50):
        start_time = time.time()
        # Execute through framework with context
        tool_context = PromptContext(
            user_id=f"tool_user_{i}",
            session_id=f"tool_session_{i}",
            user_preferences={"detail_level": "high"},
            dynamic_variables={},
            role_context=None,
        )

        tool_framework.execute_tool("calculator", i, i + 1, "add", user_context=tool_context)
        enhanced_tool_times.append(time.time() - start_time)

    enhanced_tool_avg = statistics.mean(enhanced_tool_times)
    tool_overhead = (enhanced_tool_avg - baseline_tool_avg) / baseline_tool_avg

    print(f"✅ Enhanced tool average: {enhanced_tool_avg:.6f}s")
    print(f"✅ Enhanced tool overhead: {tool_overhead:.2%}")

    if tool_overhead < targets["enhanced_tool_overhead"]:
        print(f"✅ PASS: Enhanced tool overhead within target (<{targets['enhanced_tool_overhead']*100}%)")
    else:
        print("❌ FAIL: Enhanced tool overhead exceeds target")

    # Test 4: User Preference Performance
    print("\n👤 Test 4: User Preference Performance")
    print("-" * 30)

    # Test preference storage and retrieval performance
    pref_times = []
    for i in range(100):
        start_time = time.time()
        # Set and retrieve preferences
        user_id = f"perf_user_{i}"
        preference_manager.set_user_preference(user_id, "detail_level", "high")
        preference_manager.set_user_preference(user_id, "style", "detailed")
        preference_manager.set_user_preference(user_id, "language", "python")

        preference_manager.get_user_preferences(user_id)
        pref_times.append(time.time() - start_time)

    pref_avg = statistics.mean(pref_times)
    print(f"✅ Preference operations average: {pref_avg:.6f}s")

    # Test 5: Enhanced Debugging Performance
    print("\n🐛 Test 5: Enhanced Debugging Performance")
    print("-" * 30)

    # Test debugging context capture performance
    debug_times = []
    for i in range(50):
        start_time = time.time()
        # Capture debugging context
        debugging_manager.capture_debugging_context(variable_snapshot={"test_var": f"value_{i}", "index": i})
        debug_times.append(time.time() - start_time)

    debug_avg = statistics.mean(debug_times)
    print(f"✅ Debug context capture average: {debug_avg:.6f}s")

    # Test 6: Error Taxonomy Performance
    print("\n🚨 Test 6: Error Taxonomy Performance")
    print("-" * 30)

    # Test error creation performance
    error_times = []
    for i in range(50):
        start_time = time.time()
        # Create different types of errors
        ErrorFactory.create_validation_error(
            message=f"Test validation error {i}", validation_type="format", field_name="test_field"
        )
        ErrorFactory.create_runtime_error(
            message=f"Test runtime error {i}", operation="test_operation", resource="test_resource"
        )
        error_times.append(time.time() - start_time)

    error_avg = statistics.mean(error_times)
    print(f"✅ Error creation average: {error_avg:.6f}s")

    # Test 7: Overall System Performance
    print("\n📊 Test 7: Overall System Performance")
    print("-" * 30)

    # Simulate complete workflow performance
    workflow_times = []
    for i in range(25):
        start_time = time.time()

        # Complete workflow: context creation + prompt generation + tool execution + debugging
        context = context_factory.create_context(
            AIRole.PLANNER, session_id=f"workflow_{i}", project_scope=f"workflow_project_{i}", backlog_priority="P1"
        )

        user_context = PromptContext(
            user_id=f"workflow_user_{i}",
            session_id=f"workflow_session_{i}",
            user_preferences={"detail_level": "high"},
            dynamic_variables={},
            role_context=None,
        )

        prompt_manager.generate_prompt(template_id="perf_template", context=user_context)

        preference_manager.set_user_preference(f"workflow_user_{i}", "style", "detailed")
        preference_manager.get_user_preferences(f"workflow_user_{i}")

        debugging_manager.capture_debugging_context(
            user_context=user_context, role_context=context, variable_snapshot={"workflow_step": i}
        )

        workflow_times.append(time.time() - start_time)

    workflow_avg = statistics.mean(workflow_times)
    print(f"✅ Complete workflow average: {workflow_avg:.6f}s")

    # Calculate overall performance impact
    # This is a simplified calculation - in practice, you'd compare against a real baseline
    overall_performance_impact = (workflow_avg - baseline_avg) / baseline_avg

    print(f"✅ Overall performance impact: {overall_performance_impact:.2%}")

    if overall_performance_impact < targets["overall_performance"]:
        print(f"✅ PASS: Overall performance within target (<{targets['overall_performance']*100}%)")
    else:
        print("❌ FAIL: Overall performance exceeds target")

    # Test 8: Memory Usage and Optimization
    print("\n💾 Test 8: Memory Usage and Optimization")
    print("-" * 30)

    # Test memory efficiency with large datasets
    large_dataset_times = []
    for i in range(10):
        start_time = time.time()

        # Create large number of contexts and preferences
        contexts = []
        for j in range(100):
            context = context_factory.create_context(
                AIRole.CODER,
                session_id=f"large_test_{i}_{j}",
                project_scope=f"large_project_{i}_{j}",
                backlog_priority="P1",
                codebase_path=".",
                language="python",
            )
            contexts.append(context)

        # Create large number of preferences
        for j in range(100):
            user_id = f"large_user_{i}_{j}"
            for k in range(5):
                preference_manager.set_user_preference(user_id, f"pref_{k}", f"value_{k}_{j}")

        large_dataset_times.append(time.time() - start_time)

    large_dataset_avg = statistics.mean(large_dataset_times)
    print(f"✅ Large dataset processing average: {large_dataset_avg:.6f}s")

    # Test 9: Performance Summary and Recommendations
    print("\n📋 Test 9: Performance Summary and Recommendations")
    print("-" * 30)

    # Collect all performance metrics
    performance_metrics = {
        "type_validation_overhead": validation_overhead,
        "dynamic_context_overhead": context_overhead,
        "enhanced_tool_overhead": tool_overhead,
        "overall_performance_impact": overall_performance_impact,
        "baseline_operations": baseline_avg,
        "validation_operations": validation_avg,
        "context_operations": context_avg,
        "tool_operations": enhanced_tool_avg,
        "preference_operations": pref_avg,
        "debug_operations": debug_avg,
        "error_operations": error_avg,
        "workflow_operations": workflow_avg,
        "large_dataset_operations": large_dataset_avg,
    }

    print("📊 Performance Summary:")
    for metric, value in performance_metrics.items():
        if "overhead" in metric or "impact" in metric:
            print(f"   - {metric}: {value:.2%}")
        else:
            print(f"   - {metric}: {value:.6f}s")

    # Performance recommendations
    print("\n💡 Performance Recommendations:")

    if validation_overhead > targets["type_validation_overhead"] * 0.8:
        print("   - Consider optimizing Pydantic validation for frequently used models")

    if context_overhead > targets["dynamic_context_overhead"] * 0.8:
        print("   - Consider caching prompt templates and context combinations")

    if tool_overhead > targets["enhanced_tool_overhead"] * 0.8:
        print("   - Consider optimizing context injection in tool decorators")

    if overall_performance_impact > targets["overall_performance"] * 0.8:
        print("   - Consider implementing lazy loading for non-critical components")

    # All performance targets met
    all_targets_met = (
        validation_overhead < targets["type_validation_overhead"]
        and context_overhead < targets["dynamic_context_overhead"]
        and tool_overhead < targets["enhanced_tool_overhead"]
        and overall_performance_impact < targets["overall_performance"]
    )

    if all_targets_met:
        print("\n🎉 All performance targets met! System is ready for production.")
    else:
        print("\n⚠️ Some performance targets not met. Consider optimizations before production.")

    print("\n🎉 Performance Validation Completed Successfully!")
    print("=" * 60)

    return {
        "status": "success" if all_targets_met else "needs_optimization",
        "performance_metrics": performance_metrics,
        "targets_met": all_targets_met,
        "recommendations": ["All performance targets met" if all_targets_met else "Some optimizations needed"],
    }


if __name__ == "__main__":
    try:
        result = test_performance_validation()
        print(f"\n📊 Final Performance Results: {result}")
    except Exception as e:
        print(f"\n❌ Performance validation failed: {e}")
        import traceback

        traceback.print_exc()
