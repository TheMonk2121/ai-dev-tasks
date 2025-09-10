#!/usr/bin/env python3
"""
Test Phase 3 optimizations for the gate system
"""

import asyncio
import sys
import time

sys.path.append("src")

from src.dspy_modules.gate_system import (
    CacheTTLGate,
    FailureThresholdGate,
    SecurityMonitoringGate,
    create_simplified_gate_system,
)


def test_performance_metrics():
    """Test performance metrics collection"""
    print("📊 Testing Performance Metrics")
    print("=" * 50)

    gate_manager = create_simplified_gate_system()

    # Run multiple requests to generate metrics
    test_requests = [
        {"role": "planner", "task": "Analyze project structure"},
        {"role": "coder", "task": "Implement feature"},
        {"role": "researcher", "task": "Research best practices"},
        {"role": "implementer", "task": "Deploy system"},
        {"role": "reviewer", "task": "Code review"},
    ]

    print("Running performance test with multiple requests...")
    for i, request in enumerate(test_requests, 1):
        result = gate_manager.execute_gates(request)
        print(f"Request {i}: {result['success']} ({result['execution_time']:.4f}s)")

    # Get comprehensive stats
    stats = gate_manager.get_stats()
    print("\n📈 Performance Metrics:")
    print(f"Total executions: {stats['performance_metrics']['total_executions']}")
    print(f"Successful executions: {stats['performance_metrics']['successful_executions']}")
    print(f"Failed executions: {stats['performance_metrics']['failed_executions']}")
    print(f"Average execution time: {stats['performance_metrics']['average_execution_time']:.4f}s")
    print(f"Total execution time: {stats['performance_metrics']['total_execution_time']:.4f}s")
    print(f"Cache hit rate: {stats['performance_metrics']['cache_hit_rate']:.1f}%")
    print(f"Security blocks: {stats['performance_metrics']['security_blocks']}")
    print(f"Input validation failures: {stats['performance_metrics']['input_validation_failures']}")
    print(f"Failure threshold exceeded: {stats['performance_metrics']['failure_threshold_exceeded']}")

    # Gate-specific stats
    print("\n🎯 Gate-Specific Stats:")
    for gate_name, gate_stat in stats["gate_stats"].items():
        print(f"  {gate_name}:")
        print(f"    Success rate: {gate_stat['success_rate']:.1f}%")
        print(f"    Total: {gate_stat['total']}")
        print(f"    Successful: {gate_stat['successful']}")

        # Detailed stats for specific gates
        if "security_stats" in gate_stat:
            sec_stats = gate_stat["security_stats"]
            print(f"    Security blocks: {sec_stats.get('security_blocks', 0)}")
            print(f"    Avg execution time: {sec_stats.get('average_execution_time', 0):.4f}s")

        if "cache_stats" in gate_stat:
            cache_stats = gate_stat["cache_stats"]
            print(f"    Cache hits: {cache_stats.get('cache_hits', 0)}")
            print(f"    Cache misses: {cache_stats.get('cache_misses', 0)}")
            print(f"    Cache hit rate: {cache_stats.get('cache_hit_rate', 0):.1f}%")
            print(f"    Cache size: {cache_stats.get('cache_size', 0)}")

        if "failure_stats" in gate_stat:
            fail_stats = gate_stat["failure_stats"]
            print(f"    Threshold exceeded: {fail_stats.get('threshold_exceeded', 0)}")
            print(f"    Active failures: {fail_stats.get('active_failures', 0)}")


def test_advanced_caching():
    """Test advanced caching strategies"""
    print("\n🗄️ Testing Advanced Caching")
    print("=" * 40)

    cache_gate = CacheTTLGate(ttl_seconds=5)  # 5 second TTL for testing

    # Test cache operations
    print("Setting cache entries...")
    cache_gate.set_cache("key1", "value1")
    cache_gate.set_cache("key2", "value2")
    cache_gate.set_cache("key3", "value3")

    print("Retrieving cache entries...")
    print(f"key1: {cache_gate.get_cache('key1')}")
    print(f"key2: {cache_gate.get_cache('key2')}")
    print(f"key3: {cache_gate.get_cache('key3')}")
    print(f"nonexistent: {cache_gate.get_cache('nonexistent')}")

    # Test cache expiration
    print("\nWaiting for cache expiration (5 seconds)...")
    time.sleep(6)
    print("After expiration:")
    print(f"key1: {cache_gate.get_cache('key1')}")
    print(f"key2: {cache_gate.get_cache('key2')}")

    # Test cache statistics
    cache_stats = cache_gate.get_cache_stats()
    print("\nCache Statistics:")
    print(f"Cache hits: {cache_stats['cache_hits']}")
    print(f"Cache misses: {cache_stats['cache_misses']}")
    print(f"Cache hit rate: {cache_stats['cache_hit_rate']:.1f}%")
    print(f"Cache evictions: {cache_stats['cache_evictions']}")
    print(f"Cache size: {cache_stats['cache_size']}")

    # Test cache clearing
    print("\nTesting cache clearing...")
    cache_gate.set_cache("new_key", "new_value")
    print(f"Cache size before clear: {len(cache_gate.cache)}")
    cleared = cache_gate.clear_expired_entries()
    print(f"Cleared {cleared} expired entries")
    print(f"Cache size after clear: {len(cache_gate.cache)}")


def test_security_monitoring():
    """Test security monitoring features"""
    print("\n🔒 Testing Security Monitoring")
    print("=" * 40)

    security_gate = SecurityMonitoringGate()

    # Test suspicious patterns
    suspicious_tasks = [
        "Execute script to delete database",
        "Import os.system and run commands",
        "Use eval() to execute code",
        "Run subprocess to delete files",
        "Drop table users",
    ]

    print("Testing suspicious pattern detection:")
    for task in suspicious_tasks:
        result = security_gate.check({"role": "coder", "task": task})
        print(f"  '{task}': {'BLOCKED' if not result.passed else 'ALLOWED'}")

    # Test rate limiting
    print("\nTesting rate limiting:")
    for i in range(5):
        result = security_gate.check({"role": "planner", "task": f"Task {i}"})
        print(f"  Request {i+1}: {'BLOCKED' if not result.passed else 'ALLOWED'}")

    # Get security statistics
    security_stats = security_gate.get_security_stats()
    print("\nSecurity Statistics:")
    print(f"Total executions: {security_stats['execution_count']}")
    print(f"Security blocks: {security_stats['security_blocks']}")
    print(f"Average execution time: {security_stats['average_execution_time']:.4f}s")


def test_failure_threshold():
    """Test failure threshold mechanism"""
    print("\n⚠️ Testing Failure Threshold")
    print("=" * 40)

    failure_gate = FailureThresholdGate(max_failures=2)

    # Test normal operation
    print("Testing normal operation:")
    for i in range(3):
        result = failure_gate.check({"role": "test_role", "task": f"Task {i}"})
        print(f"  Request {i+1}: {'BLOCKED' if not result.passed else 'ALLOWED'}")

    # Record failures
    print("\nRecording failures:")
    for i in range(3):
        failure_gate.record_failure("test_role")
        print(f"  Recorded failure {i+1}")

    # Test after failures
    print("\nTesting after failures:")
    result = failure_gate.check({"role": "test_role", "task": "Test task"})
    print(f"  Result: {'BLOCKED' if not result.passed else 'ALLOWED'}")

    # Get failure statistics
    failure_stats = failure_gate.get_failure_stats()
    print("\nFailure Statistics:")
    print(f"Total executions: {failure_stats['execution_count']}")
    print(f"Threshold exceeded: {failure_stats['threshold_exceeded']}")
    print(f"Active failures: {failure_stats['active_failures']}")
    print(f"Average execution time: {failure_stats['average_execution_time']:.4f}s")


async def test_async_execution():
    """Test asynchronous gate execution"""
    print("\n⚡ Testing Async Execution")
    print("=" * 40)

    gate_manager = create_simplified_gate_system()

    # Test async execution
    test_request = {"role": "planner", "task": "Async test task"}

    print("Running async gate execution...")
    start_time = time.time()
    result = await gate_manager.execute_gates_async(test_request)
    async_time = time.time() - start_time

    print(f"Async execution result: {result['success']}")
    print(f"Async execution time: {async_time:.4f}s")

    # Compare with synchronous execution
    print("\nComparing with synchronous execution...")
    start_time = time.time()
    sync_result = gate_manager.execute_gates(test_request)
    sync_time = time.time() - start_time

    print(f"Sync execution result: {sync_result['success']}")
    print(f"Sync execution time: {sync_time:.4f}s")

    print("\nPerformance comparison:")
    print(f"Async: {async_time:.4f}s")
    print(f"Sync:  {sync_time:.4f}s")
    print(f"Difference: {abs(async_time - sync_time):.4f}s")


def test_integration_scenarios():
    """Test integration scenarios with real-world use cases"""
    print("\n🔗 Testing Integration Scenarios")
    print("=" * 50)

    gate_manager = create_simplified_gate_system()

    # Scenario 1: Normal development workflow
    print("Scenario 1: Normal development workflow")
    scenarios = [
        {"role": "planner", "task": "Plan the next sprint"},
        {"role": "researcher", "task": "Research best practices for microservices"},
        {"role": "coder", "task": "Implement user authentication"},
        {"role": "implementer", "task": "Deploy to staging environment"},
        {"role": "reviewer", "task": "Review pull request #123"},
    ]

    for i, scenario in enumerate(scenarios, 1):
        result = gate_manager.execute_gates(scenario)
        print(f"  {i}. {scenario['role']}: {'✅ PASS' if result['success'] else '❌ BLOCK'}")

    # Scenario 2: Security testing
    print("\nScenario 2: Security testing")
    security_scenarios = [
        {"role": "coder", "task": "Execute script to delete database"},
        {"role": "hacker", "task": "Normal task"},
        {"role": "researcher", "task": "Import os.system and run commands"},
        {"role": "implementer", "task": "Drop table users"},
    ]

    for i, scenario in enumerate(security_scenarios, 1):
        result = gate_manager.execute_gates(scenario)
        print(f"  {i}. {scenario['role']}: {'✅ PASS' if result['success'] else '❌ BLOCK'}")

    # Scenario 3: Performance under load
    print("\nScenario 3: Performance under load")
    load_test_requests = [{"role": "planner", "task": f"Load test task {i}"} for i in range(10)]

    start_time = time.time()
    for request in load_test_requests:
        result = gate_manager.execute_gates(request)
    total_time = time.time() - start_time

    print(f"  Processed {len(load_test_requests)} requests in {total_time:.4f}s")
    print(f"  Average time per request: {total_time/len(load_test_requests):.4f}s")

    # Final statistics
    final_stats = gate_manager.get_stats()
    print("\n📊 Final Integration Statistics:")
    print(f"Total executions: {final_stats['performance_metrics']['total_executions']}")
    print(f"Success rate: {final_stats['success_rate']:.1f}%")
    print(f"Average execution time: {final_stats['performance_metrics']['average_execution_time']:.4f}s")
    print(f"Security blocks: {final_stats['performance_metrics']['security_blocks']}")
    print(f"Cache hit rate: {final_stats['performance_metrics']['cache_hit_rate']:.1f}%")


async def main():
    """Run all Phase 3 tests"""
    print("🚀 Phase 3 Optimization Tests")
    print("=" * 60)

    # Run all tests
    test_performance_metrics()
    test_advanced_caching()
    test_security_monitoring()
    test_failure_threshold()
    await test_async_execution()
    test_integration_scenarios()

    print("\n✅ All Phase 3 tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
