from __future__ import annotations

import json
import pathlib
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

#!/usr/bin/env python3
"""
Track Hypothesis KPI: Keep if ≥3 unique counterexamples promoted within a week.
"""

def track_hypothesis_kpi() -> dict:
    """Track Hypothesis KPI and provide recommendation."""
    edge_cases_file = pathlib.Path(__file__).parent.parent / "tests" / "data" / "edge_cases.jsonl"

    if not edge_cases_file.exists():
        return {
            "total_cases": 0,
            "unique_test_types": 0,
            "kpi_threshold": 3,
            "meets_kpi": False,
            "recommendation": "FREEZE",
            "test_breakdown": {},
            "timestamp": datetime.now().isoformat(),
        }

    # Load edge cases
    cases = []
    with open(edge_cases_file) as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))

    # Count unique test types
    test_types = set()
    test_breakdown = defaultdict(int)

    for case in cases:
        test_name = case.get("test", "unknown")
        test_types.add(test_name)
        test_breakdown[test_name] += 1

    # KPI evaluation
    unique_test_types = len(test_types)
    kpi_threshold = 3
    meets_kpi = unique_test_types >= kpi_threshold
    recommendation = "KEEP" if meets_kpi else "FREEZE"

    return {
        "total_cases": len(cases),
        "unique_test_types": unique_test_types,
        "kpi_threshold": kpi_threshold,
        "meets_kpi": meets_kpi,
        "recommendation": recommendation,
        "test_breakdown": dict(test_breakdown),
        "timestamp": datetime.now().isoformat(),
    }

def main() -> None:
    """Main function to run KPI tracking."""
    print("🔍 Hypothesis KPI Analysis")
    print("=" * 50)

    result = track_hypothesis_kpi()

    print(f"Total edge cases found: {result['total_cases']}")
    print(f"Unique test types: {result['unique_test_types']}")
    print(f"KPI threshold: {result['kpi_threshold']}")
    print(f"Meets KPI: {'✅ YES' if result['meets_kpi'] else '❌ NO'}")
    print(f"Recommendation: {result['recommendation']}")

    if result["test_breakdown"]:
        print("\nTest breakdown:")
        for test_name, count in result["test_breakdown"].items():
            print(f"  {test_name}: {count} cases")

    print(f"\nTimestamp: {result['timestamp']}")

if __name__ == "__main__":
    main()
