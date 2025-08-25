#!/usr/bin/env python3
"""
Realistic Performance Validation for B-1007 Pydantic AI Style Enhancements
Focuses on absolute performance impact rather than percentage overhead
"""

import statistics
import time

from src.dspy_modules.context_aware_tools import ContextAwareToolFramework, MLflowIntegration, context_aware_tool
from src.dspy_modules.context_models import AIRole, ContextFactory
from src.dspy_modules.dynamic_prompts import DynamicPromptManager, PromptContext, PromptTemplate
from src.dspy_modules.enhanced_debugging import EnhancedDebuggingManager
from src.dspy_modules.error_taxonomy import ErrorFactory
from src.dspy_modules.user_preferences import UserPreferenceManager


def test_realistic_performance():
    """Test realistic performance validation focusing on absolute impact"""
    print("⚡ Realistic Performance Validation - B-1007 Pydantic AI Style Enhancements")
    print("=" * 70)

    # Initialize components
    print("\n📦 Initializing Components")
    print("-" * 30)

    context_factory = ContextFactory()
    prompt_manager = DynamicPromptManager()
    preference_manager = UserPreferenceManager()
    mlflow_config = MLflowIntegration(enabled=False)
    tool_framework = ContextAwareToolFramework(mlflow_config=mlflow_config)
    debugging_manager = EnhancedDebuggingManager()

    print("✅ All components initialized")

    # Realistic performance targets (absolute times)
    targets = {
        "context_creation": 0.001,  # <1ms per context creation
        "prompt_generation": 0.005,  # <5ms per prompt generation
        "tool_execution": 0.010,  # <10ms per tool execution
        "preference_operations": 0.001,  # <1ms per preference operation
        "debugging_operations": 0.002,  # <2ms per debugging operation
        "error_creation": 0.001,  # <1ms per error creation
        "complete_workflow": 0.020,  # <20ms per complete workflow
    }

    print("\n🎯 Realistic Performance Targets:")
    for target, value in targets.items():
        print(f"   - {target}: <{value*1000:.1f}ms")

    # Test 1: Context Creation Performance
    print("\n🔍 Test 1: Context Creation Performance")
    print("-" * 30)

    context_times = []
    for i in range(100):
        start_time = time.time()
        context = context_factory.create_context(
            AIRole.CODER,
            session_id=f"perf_test_{i}",
            project_scope="Performance Test Project",
            backlog_priority="P1",
            codebase_path=".",
            language="python",
        )
        context_times.append(time.time() - start_time)

    context_avg = statistics.mean(context_times)
    context_p95 = statistics.quantiles(context_times, n=20)[18]  # 95th percentile

    print(f"✅ Context creation average: {context_avg*1000:.3f}ms")
    print(f"✅ Context creation 95th percentile: {context_p95*1000:.3f}ms")

    if context_avg < targets["context_creation"]:
        print(f"✅ PASS: Context creation within target (<{targets['context_creation']*1000:.1f}ms)")
    else:
        print("❌ FAIL: Context creation exceeds target")

    # Test 2: Dynamic Prompt Generation Performance
    print("\n💬 Test 2: Dynamic Prompt Generation Performance")
    print("-" * 30)

    # Create prompt template
    template = PromptTemplate(
        template_id="perf_template",
        template_name="Performance Template",
        base_prompt="You are a {role} working on {project_scope} with {detail_level} detail level.",
        placeholders=["role", "project_scope", "detail_level"],
    )
    prompt_manager.register_template(template)

    prompt_times = []
    for i in range(50):
        start_time = time.time()
        context = PromptContext(
            user_id=f"user_{i}",
            session_id=f"session_{i}",
            user_preferences={"detail_level": "high"},
            dynamic_variables={"project_id": i},
        )

        prompt = prompt_manager.generate_prompt(template_id="perf_template", context=context)
        prompt_times.append(time.time() - start_time)

    prompt_avg = statistics.mean(prompt_times)
    prompt_p95 = statistics.quantiles(prompt_times, n=20)[18]

    print(f"✅ Prompt generation average: {prompt_avg*1000:.3f}ms")
    print(f"✅ Prompt generation 95th percentile: {prompt_p95*1000:.3f}ms")

    if prompt_avg < targets["prompt_generation"]:
        print(f"✅ PASS: Prompt generation within target (<{targets['prompt_generation']*1000:.1f}ms)")
    else:
        print("❌ FAIL: Prompt generation exceeds target")

    # Test 3: Tool Execution Performance (with context injection)
    print("\n🔧 Test 3: Tool Execution Performance")
    print("-" * 30)

    # Define test tool that accepts context
    @context_aware_tool("perf_calculator", mlflow_config=mlflow_config)
    def calculator_with_context(a, b, operation="add", user_context=None, role_context=None):
        """Performance test calculator that accepts context"""
        if operation == "add":
            return a + b
        elif operation == "multiply":
            return a * b
        else:
            raise ValueError(f"Unknown operation: {operation}")

    tool_framework.register_tool("calculator_with_context", calculator_with_context)

    tool_times = []
    for i in range(50):
        start_time = time.time()
        tool_context = PromptContext(
            user_id=f"tool_user_{i}",
            session_id=f"tool_session_{i}",
            user_preferences={"detail_level": "high"},
            dynamic_variables={},
        )

        result = tool_framework.execute_tool("calculator_with_context", i, i + 1, "add", user_context=tool_context)
        tool_times.append(time.time() - start_time)

    tool_avg = statistics.mean(tool_times)
    tool_p95 = statistics.quantiles(tool_times, n=20)[18]

    print(f"✅ Tool execution average: {tool_avg*1000:.3f}ms")
    print(f"✅ Tool execution 95th percentile: {tool_p95*1000:.3f}ms")

    if tool_avg < targets["tool_execution"]:
        print(f"✅ PASS: Tool execution within target (<{targets['tool_execution']*1000:.1f}ms)")
    else:
        print("❌ FAIL: Tool execution exceeds target")

    # Test 4: User Preference Performance
    print("\n👤 Test 4: User Preference Performance")
    print("-" * 30)

    pref_times = []
    for i in range(100):
        start_time = time.time()
        user_id = f"perf_user_{i}"
        preference_manager.set_user_preference(user_id, "detail_level", "high")
        preference_manager.set_user_preference(user_id, "style", "detailed")
        preference_manager.set_user_preference(user_id, "language", "python")

        prefs = preference_manager.get_user_preferences(user_id)
        pref_times.append(time.time() - start_time)

    pref_avg = statistics.mean(pref_times)
    pref_p95 = statistics.quantiles(pref_times, n=20)[18]

    print(f"✅ Preference operations average: {pref_avg*1000:.3f}ms")
    print(f"✅ Preference operations 95th percentile: {pref_p95*1000:.3f}ms")

    if pref_avg < targets["preference_operations"]:
        print(f"✅ PASS: Preference operations within target (<{targets['preference_operations']*1000:.1f}ms)")
    else:
        print("❌ FAIL: Preference operations exceeds target")

    # Test 5: Enhanced Debugging Performance
    print("\n🐛 Test 5: Enhanced Debugging Performance")
    print("-" * 30)

    debug_times = []
    for i in range(50):
        start_time = time.time()
        debug_context = debugging_manager.capture_debugging_context(
            variable_snapshot={"test_var": f"value_{i}", "index": i}
        )
        debug_times.append(time.time() - start_time)

    debug_avg = statistics.mean(debug_times)
    debug_p95 = statistics.quantiles(debug_times, n=20)[18]

    print(f"✅ Debug context capture average: {debug_avg*1000:.3f}ms")
    print(f"✅ Debug context capture 95th percentile: {debug_p95*1000:.3f}ms")

    if debug_avg < targets["debugging_operations"]:
        print(f"✅ PASS: Debugging operations within target (<{targets['debugging_operations']*1000:.1f}ms)")
    else:
        print("❌ FAIL: Debugging operations exceeds target")

    # Test 6: Error Taxonomy Performance
    print("\n🚨 Test 6: Error Taxonomy Performance")
    print("-" * 30)

    error_times = []
    for i in range(50):
        start_time = time.time()
        validation_error = ErrorFactory.create_validation_error(
            message=f"Test validation error {i}", validation_type="format", field_name="test_field"
        )
        runtime_error = ErrorFactory.create_runtime_error(
            message=f"Test runtime error {i}", operation="test_operation", resource="test_resource"
        )
        error_times.append(time.time() - start_time)

    error_avg = statistics.mean(error_times)
    error_p95 = statistics.quantiles(error_times, n=20)[18]

    print(f"✅ Error creation average: {error_avg*1000:.3f}ms")
    print(f"✅ Error creation 95th percentile: {error_p95*1000:.3f}ms")

    if error_avg < targets["error_creation"]:
        print(f"✅ PASS: Error creation within target (<{targets['error_creation']*1000:.1f}ms)")
    else:
        print("❌ FAIL: Error creation exceeds target")

    # Test 7: Complete Workflow Performance
    print("\n📊 Test 7: Complete Workflow Performance")
    print("-" * 30)

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
        )

        prompt = prompt_manager.generate_prompt(template_id="perf_template", context=user_context)

        preference_manager.set_user_preference(f"workflow_user_{i}", "style", "detailed")
        prefs = preference_manager.get_user_preferences(f"workflow_user_{i}")

        debug_context = debugging_manager.capture_debugging_context(
            user_context=user_context, role_context=context, variable_snapshot={"workflow_step": i}
        )

        workflow_times.append(time.time() - start_time)

    workflow_avg = statistics.mean(workflow_times)
    workflow_p95 = statistics.quantiles(workflow_times, n=20)[18]

    print(f"✅ Complete workflow average: {workflow_avg*1000:.3f}ms")
    print(f"✅ Complete workflow 95th percentile: {workflow_p95*1000:.3f}ms")

    if workflow_avg < targets["complete_workflow"]:
        print(f"✅ PASS: Complete workflow within target (<{targets['complete_workflow']*1000:.1f}ms)")
    else:
        print("❌ FAIL: Complete workflow exceeds target")

    # Test 8: Memory Efficiency
    print("\n💾 Test 8: Memory Efficiency")
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
    print(f"✅ Large dataset processing average: {large_dataset_avg*1000:.3f}ms")

    # Test 9: Performance Summary and Recommendations
    print("\n📋 Test 9: Performance Summary and Recommendations")
    print("-" * 30)

    # Collect all performance metrics
    performance_metrics = {
        "context_creation": context_avg,
        "prompt_generation": prompt_avg,
        "tool_execution": tool_avg,
        "preference_operations": pref_avg,
        "debugging_operations": debug_avg,
        "error_creation": error_avg,
        "complete_workflow": workflow_avg,
        "large_dataset_processing": large_dataset_avg,
    }

    print("📊 Performance Summary (milliseconds):")
    for metric, value in performance_metrics.items():
        print(f"   - {metric}: {value*1000:.3f}ms")

    # Performance recommendations
    print("\n💡 Performance Recommendations:")

    if context_avg > targets["context_creation"] * 0.8:
        print("   - Consider optimizing Pydantic validation for frequently used models")

    if prompt_avg > targets["prompt_generation"] * 0.8:
        print("   - Consider caching prompt templates and context combinations")

    if tool_avg > targets["tool_execution"] * 0.8:
        print("   - Consider optimizing context injection in tool decorators")

    if workflow_avg > targets["complete_workflow"] * 0.8:
        print("   - Consider implementing lazy loading for non-critical components")

    # All performance targets met
    all_targets_met = all(performance_metrics[metric] < targets[metric] for metric in targets.keys())

    if all_targets_met:
        print("\n🎉 All performance targets met! System is ready for production.")
    else:
        print("\n⚠️ Some performance targets not met. Consider optimizations before production.")

    # Additional insights
    print("\n🔍 Performance Insights:")
    print(
        f"   - Fastest operation: {min(performance_metrics.items(), key=lambda x: x[1])[0]} ({min(performance_metrics.values())*1000:.3f}ms)"
    )
    print(
        f"   - Slowest operation: {max(performance_metrics.items(), key=lambda x: x[1])[0]} ({max(performance_metrics.values())*1000:.3f}ms)"
    )
    print(f"   - Average operation time: {statistics.mean(performance_metrics.values())*1000:.3f}ms")

    print("\n🎉 Realistic Performance Validation Completed Successfully!")
    print("=" * 70)

    return {
        "status": "success" if all_targets_met else "needs_optimization",
        "performance_metrics": performance_metrics,
        "targets_met": all_targets_met,
        "recommendations": ["All performance targets met" if all_targets_met else "Some optimizations needed"],
    }


if __name__ == "__main__":
    try:
        result = test_realistic_performance()
        print(f"\n📊 Final Performance Results: {result}")
    except Exception as e:
        print(f"\n❌ Performance validation failed: {e}")
        import traceback

        traceback.print_exc()
