"""
Test runner for real database integration tests.

This script provides a comprehensive way to run all real database tests
with proper environment setup and reporting.
"""

#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from typing import Any


def check_database_availability() -> bool:
    """Check if a real database is available for testing."""
    dsn = os.getenv("TEST_POSTGRES_DSN") or os.getenv("POSTGRES_DSN")

    if not dsn:
        print("❌ No database DSN found. Set TEST_POSTGRES_DSN or POSTGRES_DSN")
        return False

    if dsn.startswith("mock://"):
        print("❌ Mock DSN detected. Real database required for integration tests.")
        return False

    print(f"✅ Database DSN found: {dsn[:20]}...")
    return True


def run_test_suite(test_patterns: list[str], verbose: bool = False) -> int:
    """Run the specified test patterns."""
    cmd = ["uv", "run", "pytest"]

    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    # Add test patterns
    cmd.extend(test_patterns)

    # Add markers for real database tests
    cmd.extend(["-m", "database"])

    # Add implementation test directory
    cmd.append("tests/implementation/")

    print(f"Running: {' '.join(cmd)}")

    try:
        result: Any = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Make sure you're in the project directory.")
        return 1


def main() -> Any:
    """Main test runner function."""
    parser: Any = argparse.ArgumentParser(description="Run real database integration tests")
    parser.add_argument(
        "--pattern",
        action="append",
        help="Test pattern to run (can be specified multiple times)",
    )
    parser.add_argument("--all", action="store_true", help="Run all real database tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--check-db", action="store_true", help="Only check database availability")

    args: Any = parser.parse_args()

    # Check database availability
    if not check_database_availability():
        return 1

    if args.check_db:
        print("✅ Database check passed")
        return 0

    # Determine test patterns
    if args.all:
        test_patterns = [
            "test_database_connection_patterns.py",
            "test_mcp_memory_server_real.py",
            "test_dspy_retriever_real.py",
            "test_workload_isolation_real.py",
        ]
    elif args.pattern:
        test_patterns = args.pattern
    else:
        print("❌ No test pattern specified. Use --pattern or --all")
        return 1

    print(f"🧪 Running {len(test_patterns)} test pattern(s)")

    # Run tests
    exit_code = run_test_suite(test_patterns, args.verbose)

    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
