#!/usr/bin/env python3
"""
Comprehensive test runner for the AI Dev Tasks project.

Supports running mock tests, implementation tests, or both with proper
environment setup and reporting.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def check_database_availability() -> bool:
    """Check if a real database is available for testing."""
    dsn = os.getenv("TEST_POSTGRES_DSN") or os.getenv("POSTGRES_DSN")

    if not dsn:
        return False

    if dsn.startswith("mock://"):
        return False

    return True


def run_mock_tests(verbose: bool = False, pattern: str | None = None) -> int:
    """Run mock-based unit tests."""
    cmd = ["uv", "run", "pytest"]

    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    # Add mock test directory
    cmd.append("tests/mock/")

    # Add pattern if specified
    if pattern:
        cmd.extend(["-k", pattern])

    print(f"🧪 Running mock tests: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Mock tests failed with exit code {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Make sure you're in the project directory.")
        return 1


def run_implementation_tests(verbose: bool = False, pattern: str | None = None) -> int:
    """Run real implementation tests."""
    if not check_database_availability():
        print("❌ Real database required for implementation tests.")
        print("   Set TEST_POSTGRES_DSN or POSTGRES_DSN to a real database connection.")
        return 1

    cmd = ["uv", "run", "pytest"]

    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    # Add implementation test directory
    cmd.append("tests/implementation/")

    # Add pattern if specified
    if pattern:
        cmd.extend(["-k", pattern])

    # Add markers for real database tests
    cmd.extend(["-m", "database"])

    print(f"🧪 Running implementation tests: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Implementation tests failed with exit code {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Make sure you're in the project directory.")
        return 1


def run_all_tests(verbose: bool = False, pattern: str | None = None) -> int:
    """Run all tests (mock and implementation)."""
    print("🧪 Running all tests...")

    # Run mock tests first
    print("\n📝 Running mock tests...")
    mock_result = run_mock_tests(verbose, pattern)

    if mock_result != 0:
        print("❌ Mock tests failed, skipping implementation tests")
        return mock_result

    # Run implementation tests
    print("\n🔧 Running implementation tests...")
    impl_result = run_implementation_tests(verbose, pattern)

    if impl_result != 0:
        print("❌ Implementation tests failed")
        return impl_result

    print("✅ All tests passed!")
    return 0


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for AI Dev Tasks project")

    # Test type selection
    test_group = parser.add_mutually_exclusive_group(required=True)
    test_group.add_argument("--mock", action="store_true", help="Run only mock tests")
    test_group.add_argument("--implementation", action="store_true", help="Run only implementation tests")
    test_group.add_argument("--all", action="store_true", help="Run all tests")

    # Test filtering
    parser.add_argument("--pattern", "-k", help="Test pattern to run (pytest -k syntax)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # Database check
    parser.add_argument("--check-db", action="store_true", help="Only check database availability")

    args = parser.parse_args()

    # Check database availability if requested
    if args.check_db:
        if check_database_availability():
            print("✅ Database available for implementation tests")
            return 0
        else:
            print("❌ Database not available for implementation tests")
            return 1

    # Run tests based on selection
    if args.mock:
        return run_mock_tests(args.verbose, args.pattern)
    elif args.implementation:
        return run_implementation_tests(args.verbose, args.pattern)
    elif args.all:
        return run_all_tests(args.verbose, args.pattern)

    return 0


if __name__ == "__main__":
    sys.exit(main())
