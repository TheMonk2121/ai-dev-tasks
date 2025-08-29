#!/usr/bin/env python3
"""
Test script for the modular gate system
"""

import sys

sys.path.append("src")

from src.dspy_modules.gate_system import (
    CacheTTLGate,
    FailureThresholdGate,
    InputValidationGate,
    SecurityMonitoringGate,
    create_simplified_gate_system,
)


def test_modular_gate_system():
    """Test the modular gate system"""

    print("🧪 Testing Modular Gate System")
    print("=" * 50)

    # Create the simplified gate system
    gate_manager = create_simplified_gate_system()

    print(f"✅ Created gate system with {len(gate_manager.gates)} gates:")
    for gate in gate_manager.gates:
        print(f"  - {gate}")

    # Test 1: Valid request
    print("\n🎯 Test 1: Valid request")
    valid_request = {"role": "planner", "task": "Analyze the current project structure"}

    result = gate_manager.execute_gates(valid_request)
    print(f"Result: {result['success']}")
    print(f"Message: {result['message']}")
    print(f"Execution time: {result['execution_time']:.3f}s")

    # Test 2: Invalid role
    print("\n🎯 Test 2: Invalid role")
    invalid_role_request = {"role": "invalid_role", "task": "Test task"}

    result = gate_manager.execute_gates(invalid_role_request)
    print(f"Result: {result['success']}")
    print(f"Failed gate: {result.get('failed_gate', 'N/A')}")
    print(f"Message: {result['message']}")

    # Test 3: Empty task
    print("\n🎯 Test 3: Empty task")
    empty_task_request = {"role": "coder", "task": ""}

    result = gate_manager.execute_gates(empty_task_request)
    print(f"Result: {result['success']}")
    print(f"Failed gate: {result.get('failed_gate', 'N/A')}")
    print(f"Message: {result['message']}")

    # Test 4: Suspicious pattern
    print("\n🎯 Test 4: Suspicious pattern")
    suspicious_request = {"role": "researcher", "task": "Execute script to delete database"}

    result = gate_manager.execute_gates(suspicious_request)
    print(f"Result: {result['success']}")
    print(f"Failed gate: {result.get('failed_gate', 'N/A')}")
    print(f"Message: {result['message']}")

    # Test 5: Rate limiting (simulate multiple requests)
    print("\n🎯 Test 5: Rate limiting")
    for i in range(5):
        rate_test_request = {"role": "implementer", "task": f"Test task {i}"}
        result = gate_manager.execute_gates(rate_test_request)
        print(f"Request {i+1}: {result['success']} - {result['message']}")

    # Test 6: Failure threshold
    print("\n🎯 Test 6: Failure threshold")
    failure_gate = None
    for gate in gate_manager.gates:
        if isinstance(gate, FailureThresholdGate):
            failure_gate = gate
            break

    if failure_gate:
        # Record some failures
        for i in range(3):
            failure_gate.record_failure("test_role")
            print(f"Recorded failure {i+1} for test_role")

        # Test the gate
        failure_request = {"role": "test_role", "task": "Test task"}
        result = gate_manager.execute_gates(failure_request)
        print(f"Result after failures: {result['success']}")
        print(f"Message: {result['message']}")

    # Test 7: Cache TTL
    print("\n🎯 Test 7: Cache TTL")
    cache_gate = None
    for gate in gate_manager.gates:
        if isinstance(gate, CacheTTLGate):
            cache_gate = gate
            break

    if cache_gate:
        # Set cache entry
        cache_gate.set_cache("test_key", "test_value")
        print("Set cache entry: test_key = test_value")

        # Check cache
        cached_value = cache_gate.get_cache("test_key")
        print(f"Retrieved from cache: {cached_value}")

        # Test with cache request
        cache_request = {"role": "planner", "task": "test_key"}  # This will be used as cache key
        result = gate_manager.execute_gates(cache_request)
        print(f"Cache test result: {result['success']}")

    # Print final stats
    print("\n📊 Final Statistics:")
    stats = gate_manager.get_stats()
    print(f"Total executions: {stats['total_executions']}")
    print(f"Success rate: {stats['success_rate']:.1f}%")

    if "gate_stats" in stats:
        print("Gate-specific stats:")
        for gate_name, gate_stat in stats["gate_stats"].items():
            print(f"  {gate_name}: {gate_stat['success_rate']:.1f}% ({gate_stat['successful']}/{gate_stat['total']})")

    print("\n✅ Modular gate system test completed!")


def test_gate_individual():
    """Test individual gates"""

    print("\n🧪 Testing Individual Gates")
    print("=" * 40)

    # Test InputValidationGate
    print("\n🎯 InputValidationGate:")
    input_gate = InputValidationGate()

    test_cases = [
        {"role": "planner", "task": "Valid task"},
        {"role": "invalid", "task": "Valid task"},
        {"role": "coder", "task": ""},
        {"role": "", "task": "Valid task"},
    ]

    for i, test_case in enumerate(test_cases, 1):
        result = input_gate.check(test_case)
        print(f"  Test {i}: {result.passed} - {result.message}")

    # Test SecurityMonitoringGate
    print("\n🎯 SecurityMonitoringGate:")
    security_gate = SecurityMonitoringGate()

    security_test_cases = [
        {"role": "planner", "task": "Normal task"},
        {"role": "coder", "task": "Execute script"},
        {"role": "researcher", "task": "Import os.system"},
        {"role": "implementer", "task": "Delete database"},
    ]

    for i, test_case in enumerate(security_test_cases, 1):
        result = security_gate.check(test_case)
        print(f"  Test {i}: {result.passed} - {result.message}")


if __name__ == "__main__":
    test_modular_gate_system()
    test_gate_individual()
