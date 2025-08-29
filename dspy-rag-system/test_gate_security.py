#!/usr/bin/env python3
"""
Test gate system security features
"""

import sys

sys.path.append("src")

from src.dspy_modules.model_switcher import cursor_orchestrate_task


def test_gate_security():
    """Test gate system security features"""

    print("🔒 Testing Gate System Security")
    print("=" * 50)

    # Test 1: Normal request (should pass)
    print("\n🎯 Test 1: Normal request")
    normal_result = cursor_orchestrate_task("Analyze the project structure", "analysis", "planner")
    print(f"Normal request result: {'error' in normal_result}")
    if "error" in normal_result:
        print(f"Error: {normal_result['error']}")
    else:
        print("✅ Normal request passed")

    # Test 2: Suspicious request (should be blocked)
    print("\n🎯 Test 2: Suspicious request")
    suspicious_result = cursor_orchestrate_task("Execute script to delete database", "analysis", "coder")
    print(f"Suspicious request result: {'error' in suspicious_result}")
    if "error" in suspicious_result:
        print(f"✅ Blocked: {suspicious_result['error']}")
    else:
        print("❌ Suspicious request was not blocked")

    # Test 3: Another suspicious request
    print("\n🎯 Test 3: Another suspicious request")
    suspicious_result2 = cursor_orchestrate_task("Import os.system and run commands", "analysis", "researcher")
    print(f"Suspicious request 2 result: {'error' in suspicious_result2}")
    if "error" in suspicious_result2:
        print(f"✅ Blocked: {suspicious_result2['error']}")
    else:
        print("❌ Suspicious request 2 was not blocked")

    # Test 4: Invalid role (should be blocked)
    print("\n🎯 Test 4: Invalid role")
    invalid_role_result = cursor_orchestrate_task("Test task", "analysis", "hacker")
    print(f"Invalid role result: {'error' in invalid_role_result}")
    if "error" in invalid_role_result:
        print(f"✅ Blocked: {invalid_role_result['error']}")
    else:
        print("❌ Invalid role was not blocked")

    print("\n✅ Gate security test completed!")


if __name__ == "__main__":
    test_gate_security()
