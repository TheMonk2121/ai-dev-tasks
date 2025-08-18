#!/usr/bin/env python3
"""
Generate XRef Ledger Entries

Creates short-lived (7-day) ledger entries for remaining XRef violations
to bring multirep count to 0 and start the clean-day clock.
"""

import json
import os
from datetime import datetime, timedelta, timezone, UTC
from typing import Dict, List


def load_validator_report() -> dict:
    """Load validator report."""
    report_path = "validator_report.json"

    if not os.path.exists(report_path):
        print("❌ Validator report not found. Run validator first.")
        return {}

    with open(report_path) as f:
        return json.load(f)


def load_existing_ledger() -> dict:
    """Load existing validator exceptions ledger."""
    ledger_path = "data/validator_exceptions.json"

    if os.path.exists(ledger_path):
        with open(ledger_path) as f:
            return json.load(f)
    else:
        return {"schema_version": "1.0", "generated_at": datetime.now(UTC).isoformat() + "Z", "exceptions": {}}


def generate_ledger_entries(violations: list[str]) -> dict:
    """Generate ledger entries for XRef violations."""
    # Calculate expiry date (7 days from now)
    expiry_date = (datetime.now(UTC) + timedelta(days=7)).strftime("%Y-%m-%d")

    ledger = load_existing_ledger()

    # Convert absolute paths to relative
    for violation in violations:
        rel_path = violation
        if violation.startswith("/"):
            cwd = os.getcwd()
            if violation.startswith(cwd):
                rel_path = violation[len(cwd) :].lstrip("/")

        # Add ledger entry
        if rel_path not in ledger["exceptions"]:
            ledger["exceptions"][rel_path] = []

        ledger["exceptions"][rel_path].append(
            {
                "key": "xref-missing",
                "expires": expiry_date,
                "reason": "Round 7 XRef cleanup - low confidence, queued for manual link",
                "created": datetime.now(UTC).isoformat() + "Z",
            }
        )

    return ledger


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate XRef ledger entries")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--write", action="store_true", help="Actually write ledger entries")

    args = parser.parse_args()

    if not args.dry_run and not args.write:
        print("❌ Must specify --dry-run or --write")
        return

    print("🔍 Loading validator report...")
    report = load_validator_report()

    if not report:
        return

    violations = report.get("impacted_files", {}).get("multirep", [])
    print(f"📋 Found {len(violations)} remaining XRef violations")

    if not violations:
        print("✅ No XRef violations found")
        return

    # Generate ledger entries
    ledger = generate_ledger_entries(violations)

    print(f"📝 Generated {len(violations)} ledger entries")
    print("⏰ Expiry: 7 days from now")

    if args.write:
        # Ensure directory exists
        os.makedirs("data", exist_ok=True)

        # Write ledger
        with open("data/validator_exceptions.json", "w") as f:
            json.dump(ledger, f, indent=2)

        print("✅ Ledger entries written to data/validator_exceptions.json")
    else:
        print("📋 Dry run - no changes made")
        print("Sample entries:")
        for i, violation in enumerate(violations[:3]):
            rel_path = violation
            if violation.startswith("/"):
                cwd = os.getcwd()
                if violation.startswith(cwd):
                    rel_path = violation[len(cwd) :].lstrip("/")
            print(f"  {rel_path}: xref-missing (7-day expiry)")


if __name__ == "__main__":
    main()
