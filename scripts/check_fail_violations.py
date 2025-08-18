#!/usr/bin/env python3.12.123.11
"""
Check FAIL Mode Violations (Round 2)
Checks validator report for violations in categories currently in FAIL mode.
"""

import json
import os
import sys
from pathlib import Path


def check_fail_violations(report_path: str) -> int:
    """Check for violations in categories currently in FAIL mode."""

    if not Path(report_path).exists():
        print(f"❌ Validator report not found: {report_path}")
        return 1

    # Read validator report
    with open(report_path) as f:
        report_data = json.load(f)

    # Get current FAIL flags
    fail_flags = {
        "archive": int(os.getenv("VALIDATOR_ARCHIVE_FAIL", "0")),
        "shadow_fork": int(os.getenv("VALIDATOR_SHADOW_FAIL", "0")),
        "readme": int(os.getenv("VALIDATOR_README_FAIL", "0")),
        "multi_rep": int(os.getenv("VALIDATOR_MULTIREP_FAIL", "0")),
    }

    # Extract violations per category
    category_violations = {
        "archive": 0,
        "shadow_fork": 0,
        "readme": 0,
        "multi_rep": 0,
    }

    # Parse validator report structure
    if "categories" in report_data:
        for category, data in report_data["categories"].items():
            if category in category_violations:
                category_violations[category] = data.get("violations", 0)

    # Also check for legacy format
    if "archive_violations" in report_data:
        category_violations["archive"] = report_data.get("archive_violations", 0)
    if "shadow_fork_violations" in report_data:
        category_violations["shadow_fork"] = report_data.get("shadow_fork_violations", 0)
    if "readme_violations" in report_data:
        category_violations["readme"] = report_data.get("readme_violations", 0)
    if "multi_rep_violations" in report_data:
        category_violations["multi_rep"] = report_data.get("multi_rep_violations", 0)

    # Check for violations in FAIL mode categories
    failed_categories = []

    for category, violations in category_violations.items():
        if fail_flags[category] == 1 and violations > 0:
            failed_categories.append((category, violations))

    # Print summary
    print("🔍 FAIL Mode Violation Check:")
    for category, violations in category_violations.items():
        status = "FAIL" if fail_flags[category] == 1 else "WARN"
        violation_status = f"❌ {violations} violations" if violations > 0 else "✅ Clean"
        print(f"  {category}: {violation_status} (Mode: {status})")

    # Exit with error if any FAIL mode categories have violations
    if failed_categories:
        print("\n❌ FAIL Mode Violations Found:")
        for category, violations in failed_categories:
            print(f"  {category}: {violations} violations")
        print("\n💡 Fix violations or disable FAIL mode for these categories.")
        return 2  # Exit code 2 for FAIL mode violations

    print("\n✅ All FAIL mode categories are clean!")
    return 0


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/check_fail_violations.py <validator_report.json>")
        return 1

    report_path = sys.argv[1]
    return check_fail_violations(report_path)


if __name__ == "__main__":
    sys.exit(main())
