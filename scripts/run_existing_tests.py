#!/usr/bin/env python3
"""
Force execution of existing tests instead of creating new ones.

This script enforces the use of existing testing infrastructure
instead of creating new test files.
"""

import subprocess
import sys
from typing import Dict, List


def run_existing_test_suite(test_type: str = "smoke") -> bool:
    """Run existing test suite based on type."""

    print(f"🧪 RUNNING EXISTING {test_type.upper()} TESTS...")

    test_mapping = {
        "smoke": {
            "command": ["./dspy-rag-system/run_tests.sh", "--tiers", "1", "--kinds", "smoke"],
            "description": "Fast PR gate tests",
        },
        "unit": {
            "command": ["./dspy-rag-system/run_tests.sh", "--tiers", "1", "--kinds", "unit"],
            "description": "Critical unit tests",
        },
        "integration": {
            "command": ["./dspy-rag-system/run_tests.sh", "--tiers", "1", "2", "--kinds", "integration"],
            "description": "Production integration tests",
        },
        "performance": {
            "command": [sys.executable, "scripts/performance_benchmark.py"],
            "description": "Performance benchmarks",
        },
        "security": {
            "command": [sys.executable, "scripts/security_enhancement.py"],
            "description": "Security validation tests",
        },
        "system_health": {
            "command": [sys.executable, "scripts/system_health_check.py"],
            "description": "System health validation",
        },
        "conflict_check": {
            "command": [sys.executable, "scripts/quick_conflict_check.py"],
            "description": "Conflict detection",
        },
        "doc_validation": {
            "command": [sys.executable, "scripts/doc_coherence_validator.py", "--check-all"],
            "description": "Documentation validation",
        },
    }

    if test_type not in test_mapping:
        print(f"❌ Unknown test type: {test_type}")
        print(f"Available types: {', '.join(test_mapping.keys())}")
        return False

    test_config = test_mapping[test_type]
    print(f"  Description: {test_config['description']}")
    print(f"  Command: {' '.join(test_config['command'])}")

    try:
        if test_type in ["smoke", "unit", "integration"]:
            # These need to run from dspy-rag-system directory
            result = subprocess.run(test_config["command"], cwd="dspy-rag-system")
        else:
            result = subprocess.run(test_config["command"])

        if result.returncode == 0:
            print(f"✅ {test_type.upper()} tests passed")
            return True
        else:
            print(f"❌ {test_type.upper()} tests failed")
            return False

    except Exception as e:
        print(f"❌ {test_type.upper()} test execution error: {e}")
        return False


def run_multiple_test_types(test_types: List[str]) -> Dict[str, bool]:
    """Run multiple test types and return results."""
    results = {}

    for test_type in test_types:
        print(f"\n{'='*50}")
        success = run_existing_test_suite(test_type)
        results[test_type] = success

    return results


def run_comprehensive_test_suite() -> bool:
    """Run a comprehensive test suite using existing tests."""
    print("🧪 RUNNING COMPREHENSIVE TEST SUITE (USING EXISTING TESTS)")
    print("=" * 60)

    # Run tests in logical order
    test_sequence = [
        "conflict_check",  # Check for conflicts first
        "doc_validation",  # Validate documentation
        "smoke",  # Fast smoke tests
        "unit",  # Critical unit tests
        "security",  # Security validation
        "performance",  # Performance benchmarks
        "system_health",  # System health check
    ]

    results = run_multiple_test_types(test_sequence)

    # Summary
    print(f"\n{'='*60}")
    print("📊 COMPREHENSIVE TEST SUITE RESULTS")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_type, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {test_type.upper()}: {status}")
        if success:
            passed += 1
        else:
            failed += 1

    print(f"\n  Total: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed - review required")
        return False


def main():
    """Main function for existing test execution."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/run_existing_tests.py <test_type>")
        print("  python scripts/run_existing_tests.py comprehensive")
        print("\nAvailable test types:")
        print("  smoke, unit, integration, performance, security,")
        print("  system_health, conflict_check, doc_validation")
        sys.exit(1)

    test_type = sys.argv[1]

    if test_type == "comprehensive":
        success = run_comprehensive_test_suite()
    else:
        success = run_existing_test_suite(test_type)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
