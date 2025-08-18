#!/usr/bin/env python3.12.123.11
"""
Validator Ratchet Gate

Prevents increases in readme and multirep violations for changed files.
Compares current violations against baseline from bot/validator-state.
"""

import json
import os
import subprocess
import sys
from typing import Any


def get_changed_files() -> set[str]:
    """Get list of changed files from environment."""
    changed_files_str = os.getenv("CHANGED_FILES", "")
    if not changed_files_str:
        return set()
    return set(changed_files_str.split())


def load_current_report(report_path: str = "validator_report.json") -> dict[str, Any]:
    """Load current validator report."""
    try:
        with open(report_path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Current validator report not found: {report_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in current report: {e}")
        sys.exit(1)


def load_baseline_metrics() -> dict[str, int]:
    """Load baseline metrics from bot/validator-state branch."""
    baseline = {"readme": 0, "multirep": 0}

    try:
        # Try to fetch metrics from bot/validator-state branch
        result = subprocess.run(
            ["git", "show", "bot/validator-state:metrics/validator_counts.json"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            prev_metrics = json.loads(result.stdout)
            baseline["readme"] = prev_metrics["counts"].get("readme", 0)
            baseline["multirep"] = prev_metrics["counts"].get("multirep", 0)
            print(f"📊 Loaded baseline: readme={baseline['readme']}, multirep={baseline['multirep']}")
        else:
            print("⚠️  Could not load baseline from bot/validator-state, using zeros")

    except Exception as e:
        print(f"⚠️  Error loading baseline: {e}, using zeros")

    return baseline


def check_ratchet_violations(current_report: dict[str, Any], baseline: dict[str, int], changed_files: set[str]) -> int:
    """Check for ratchet violations and return exit code."""
    impacted_files = current_report.get("impacted_files", {})
    categories = current_report.get("categories", {})

    def intersects(category: str) -> bool:
        """Check if changed files intersect with category violations."""
        category_files = set(impacted_files.get(category, []))
        return bool(changed_files & category_files)

    violations = 0

    for category in ("readme", "multirep"):
        current_count = categories.get(category, {}).get("violations", 0)
        baseline_count = baseline.get(category, 0)

        if current_count > baseline_count and intersects(category):
            print(
                f"❌ RATCHET FAIL: {category} increased ({baseline_count} → {current_count}) and overlaps changed files"
            )
            print(f"   Changed files: {sorted(changed_files)[:5]}{'...' if len(changed_files) > 5 else ''}")
            violations += 1
        elif current_count > baseline_count:
            print(f"⚠️  {category} increased ({baseline_count} → {current_count}) but no changed files affected")
        else:
            print(f"✅ {category}: {current_count} violations (baseline: {baseline_count})")

    return 2 if violations > 0 else 0


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Validator ratchet gate")
    parser.add_argument("--report", default="validator_report.json", help="Validator report file")
    parser.add_argument("--changed-files", help="Comma-separated list of changed files")
    parser.add_argument("--warn-only", action="store_true", help="Warn only, don't fail")

    args = parser.parse_args()

    # Get changed files
    if args.changed_files:
        changed_files = set(args.changed_files.split(","))
    else:
        changed_files = get_changed_files()

    print(f"🔍 Checking ratchet for {len(changed_files)} changed files")

    # Load current report
    current_report = load_current_report(args.report)

    # Load baseline
    baseline = load_baseline_metrics()

    # Check for violations
    exit_code = check_ratchet_violations(current_report, baseline, changed_files)

    if args.warn_only and exit_code == 2:
        print("⚠️  Ratchet violations found but continuing (warn-only mode)")
        exit_code = 0

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
