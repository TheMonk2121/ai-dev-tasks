#!/usr/bin/env python3
"""
Track Hypothesis KPI: ≥3 unique counterexamples promoted = keep, otherwise freeze.
"""

import json
import pathlib
import sys
from datetime import datetime, timedelta


def load_edge_cases() -> list[dict]:
    """Load edge cases discovered by Hypothesis."""
    edge_cases_file = pathlib.Path(__file__).parent.parent / "tests" / "data" / "edge_cases.jsonl"

    if not edge_cases_file.exists():
        return []

    cases = []
    for line in edge_cases_file.read_text().strip().splitlines():
        if line.strip():
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return cases


def analyze_hypothesis_kpi() -> dict:
    """Analyze Hypothesis KPI metrics."""
    edge_cases = load_edge_cases()

    # Count unique counterexamples by test type
    test_counts = {}
    for case in edge_cases:
        test_name = case.get("test", "unknown")
        test_counts[test_name] = test_counts.get(test_name, 0) + 1

    # Calculate metrics
    total_cases = len(edge_cases)
    unique_tests = len(test_counts)

    # KPI threshold: ≥3 unique counterexamples
    kpi_threshold = 3
    meets_kpi = unique_tests >= kpi_threshold

    return {
        "total_cases": total_cases,
        "unique_tests": unique_tests,
        "test_counts": test_counts,
        "kpi_threshold": kpi_threshold,
        "meets_kpi": meets_kpi,
        "recommendation": "KEEP" if meets_kpi else "FREEZE",
        "timestamp": datetime.now().isoformat(),
    }


def main():
    """Main function."""
    print("🔍 Hypothesis KPI Analysis")
    print("=" * 50)

    metrics = analyze_hypothesis_kpi()

    print(f"Total edge cases found: {metrics['total_cases']}")
    print(f"Unique test types: {metrics['unique_tests']}")
    print(f"KPI threshold: {metrics['kpi_threshold']}")
    print(f"Meets KPI: {'✅ YES' if metrics['meets_kpi'] else '❌ NO'}")
    print(f"Recommendation: {metrics['recommendation']}")

    if metrics["test_counts"]:
        print("\nTest breakdown:")
        for test_name, count in metrics["test_counts"].items():
            print(f"  {test_name}: {count} cases")

    print(f"\nTimestamp: {metrics['timestamp']}")

    # Exit with appropriate code
    sys.exit(0 if metrics["meets_kpi"] else 1)


if __name__ == "__main__":
    main()
