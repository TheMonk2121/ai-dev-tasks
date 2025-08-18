#!/usr/bin/env python3.12.123.11
"""
Comprehensive Test Suite Entrypoint (Round 1)
Routes tests by --tiers / --kinds markers for selective execution.
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional

import pytest


class TestSuiteRouter:
    """Routes test execution based on tier and kind markers."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = self.project_root / "tests"

    def build_marker_expression(
        self, tiers: list[str] | None = None, kinds: list[str] | None = None, custom_markers: str | None = None
    ) -> str:
        """Build pytest marker expression from tiers and kinds."""

        if custom_markers:
            return custom_markers

        expressions = []

        if tiers:
            tier_expr = " or ".join([f"tier{tier}" for tier in tiers])
            expressions.append(f"({tier_expr})")

        if kinds:
            kind_expr = " or ".join([f"kind_{kind}" for kind in kinds])
            expressions.append(f"({kind_expr})")

        if expressions:
            return " and ".join(expressions)

        return ""  # Run all tests if no markers specified

    def run_tests(
        self,
        marker_expression: str = "",
        timeout: int = 300,
        coverage_threshold: float = 80.0,
        generate_report: bool = False,
        parallel: bool = False,
        workers: int = 4,
    ) -> int:
        """Run tests with specified configuration."""

        # Build pytest arguments
        args = [str(self.test_dir), "-v", "--tb=short"]

        if marker_expression:
            args.extend(["-m", marker_expression])

        if timeout:
            args.extend(["--timeout", str(timeout)])

        if coverage_threshold > 0:
            args.extend(
                ["--cov=src", "--cov=scripts", f"--cov-fail-under={coverage_threshold}", "--cov-report=term-missing"]
            )

        if generate_report:
            args.append("--cov-report=html")

        if parallel:
            args.extend(["-n", str(workers)])

        print(f"🧪 Running tests with markers: {marker_expression or 'all'}")
        print(f"📁 Test directory: {self.test_dir}")
        print(f"⏱️  Timeout: {timeout}s")
        print(f"📊 Coverage threshold: {coverage_threshold}%")
        print(f"🔄 Parallel: {parallel} (workers: {workers})")
        print("=" * 60)

        start_time = time.time()

        # Run pytest
        exit_code = pytest.main(args)

        end_time = time.time()
        duration = end_time - start_time

        print("=" * 60)
        print(f"⏱️  Test execution completed in {duration:.2f}s")
        print(f"📊 Exit code: {exit_code}")

        return exit_code


def main():
    """Main entry point for comprehensive test suite."""

    parser = argparse.ArgumentParser(description="Comprehensive Test Suite Router")

    # Marker selection
    parser.add_argument("--tiers", nargs="+", help="Test tiers to run (e.g., 1 2)")
    parser.add_argument("--kinds", nargs="+", help="Test kinds to run (e.g., unit integration e2e)")
    parser.add_argument("--markers", help="Custom marker expression")

    # Execution options
    parser.add_argument("--timeout", type=int, default=300, help="Test timeout in seconds")
    parser.add_argument("--coverage-threshold", type=float, default=80.0, help="Coverage threshold percentage")
    parser.add_argument("--generate-report", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--parallel", action="store_true", help="Enable parallel execution")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel workers")

    # Validation options
    parser.add_argument("--strict-markers", action="store_true", help="Enable strict marker validation")
    parser.add_argument("--min-cov", type=float, help="Minimum coverage threshold")

    # Show suggestions
    parser.add_argument("--show-suggestions", action="store_true", help="Show usage examples")

    args = parser.parse_args()

    if args.show_suggestions:
        print("📋 Usage Examples:")
        print("  python tests/comprehensive_test_suite.py --tiers 1 --kinds smoke")
        print("  python tests/comprehensive_test_suite.py --tiers 1 2 --kinds unit integration")
        print("  python tests/comprehensive_test_suite.py --markers 'tier1 and not e2e'")
        print("  python tests/comprehensive_test_suite.py --parallel --workers 8")
        print("  python tests/comprehensive_test_suite.py --coverage-threshold 90.0")
        return 0

    router = TestSuiteRouter()

    # Build marker expression
    marker_expression = router.build_marker_expression(tiers=args.tiers, kinds=args.kinds, custom_markers=args.markers)

    # Run tests
    exit_code = router.run_tests(
        marker_expression=marker_expression,
        timeout=args.timeout,
        coverage_threshold=args.coverage_threshold,
        generate_report=args.generate_report,
        parallel=args.parallel,
        workers=args.workers,
    )

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
