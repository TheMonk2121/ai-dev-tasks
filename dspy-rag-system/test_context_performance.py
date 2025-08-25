#!/usr/bin/env python3
"""
Performance test for context validation overhead
Validates that context validation overhead is <3% as required by B-1007
"""

import time

from src.dspy_modules.context_models import (
    AIRole,
    ContextFactory,
    ContextValidationBenchmark,
    PlannerContext,
)


def test_context_validation_performance():
    """Test context validation performance"""

    # Create a test context
    context = PlannerContext(
        session_id="performance-test-session",
        project_scope="This is a test project scope for performance validation",
        backlog_priority="P1",
    )

    # Benchmark validation overhead
    results = ContextValidationBenchmark.benchmark_validation_overhead(context, iterations=10000)

    print("Context Validation Performance Results:")
    print(f"  Total time: {results['total_time_ms']:.2f} ms")
    print(f"  Average time per validation: {results['avg_time_ms']:.4f} ms")
    print(f"  Iterations: {results['iterations']}")
    print(f"  Overhead percentage: {results['overhead_percent']:.2f}%")

    # Validate performance requirements
    assert results["overhead_percent"] < 3.0, f"Validation overhead {results['overhead_percent']:.2f}% exceeds 3% limit"
    print("✅ Performance validation passed - overhead is within acceptable limits")

    return results


def test_context_factory_performance():
    """Test context factory performance"""

    start_time = time.time()
    iterations = 1000

    for _ in range(iterations):
        context = ContextFactory.create_context(
            AIRole.PLANNER,
            session_id=f"factory-test-{_}",
            project_scope="Test project scope for factory performance",
            backlog_priority="P1",
        )

    end_time = time.time()
    total_time = (end_time - start_time) * 1000
    avg_time = total_time / iterations

    print("\nContext Factory Performance Results:")
    print(f"  Total time: {total_time:.2f} ms")
    print(f"  Average time per creation: {avg_time:.4f} ms")
    print(f"  Iterations: {iterations}")

    # Validate performance requirements
    assert avg_time < 1.0, f"Factory creation time {avg_time:.4f} ms exceeds 1ms limit"
    print("✅ Factory performance validation passed")


if __name__ == "__main__":
    print("Running B-1007 Context Models Performance Tests...")
    print("=" * 60)

    test_context_validation_performance()
    test_context_factory_performance()

    print("\n" + "=" * 60)
    print("✅ All performance tests passed!")
    print("Context models meet B-1007 performance requirements")
