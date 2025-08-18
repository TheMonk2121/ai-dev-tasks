#!/usr/bin/env python3.12.123.11
"""
No-New-Ledger PR Gate

Checks if a PR adds new ledger entries without proper approval.
Fails if new entries are added without exception-approved label AND expiry ≤7 days.
"""

import json
import os
import sys
from datetime import datetime, timezone, UTC



def load_ledger(path: str) -> dict:
    """Load validator exceptions ledger."""
    if not os.path.exists(path):
        return {"exceptions": {}}

    with open(path) as f:
        return json.load(f)


def get_changed_files() -> set[str]:
    """Get list of changed files from git."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"], capture_output=True, text=True, check=True
        )
        return set(result.stdout.strip().split("\n") if result.stdout.strip() else [])
    except subprocess.CalledProcessError:
        # If we can't get git diff, assume ledger might have changed
        return {"data/validator_exceptions.json"}


def check_ledger_changes(old_ledger: dict, new_ledger: dict) -> list[dict]:
    """Check for new ledger entries."""
    old_exceptions = old_ledger.get("exceptions", {})
    new_exceptions = new_ledger.get("exceptions", {})

    new_entries = []

    for file_path, entries in new_exceptions.items():
        old_entries = old_exceptions.get(file_path, [])

        # Check for new entries
        for entry in entries:
            if entry not in old_entries:
                new_entries.append({"file": file_path, "entry": entry})

    return new_entries


def check_expiry_valid(entry: dict) -> bool:
    """Check if entry has valid expiry ≤7 days."""
    expires = entry.get("expires")
    if not expires:
        return False

    try:
        # Parse expiry date
        if len(expires) == 10 and expires[4] == "-" and expires[7] == "-":
            expiry_date = datetime.fromisoformat(expires).replace(hour=23, minute=59, second=59, tzinfo=UTC)
        else:
            expiry_date = datetime.fromisoformat(expires.replace("Z", "+00:00"))

        # Check if expiry is ≤7 days from now
        now = datetime.now(UTC)
        days_until_expiry = (expiry_date - now).days

        return days_until_expiry <= 7
    except Exception:
        return False


def load_json_safely(path: str) -> dict:
    """Load JSON file safely, return empty dict if missing."""
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {"exceptions": {}}


def get_labels_from_github_event() -> set[str]:
    """Get labels from GitHub event."""
    label = os.getenv("GITHUB_LABELS", "")
    return {s.strip() for s in label.split(",") if s.strip()}


def check_github_labels() -> bool:
    """Check if exception-approved label is present."""
    label = os.getenv("GITHUB_LABELS", "")
    return "exception-approved" in label


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="No-New-Ledger PR Gate")
    parser.add_argument(
        "--current-json",
        default="data/validator_exceptions.json",
        help="Path to current validator_exceptions.json (default repo path).",
    )
    parser.add_argument(
        "--base-json",
        default=None,
        help="Optional path to a baseline validator_exceptions.json. If provided, bypasses git.",
    )
    parser.add_argument(
        "--changed-files", default=None, help="Optional comma-separated changed files list. If provided, bypasses git."
    )
    parser.add_argument(
        "--labels", default=None, help="Optional comma-separated PR labels. If provided, bypasses GH event parsing."
    )
    parser.add_argument(
        "--approved-label", default="exception-approved", help="Label required to allow new ledger entries."
    )

    args = parser.parse_args()

    ledger_path = args.current_json

    # Check if ledger file was changed
    if args.changed_files:
        changed_files = set(f.strip() for f in args.changed_files.split(",") if f.strip())
    else:
        changed_files = get_changed_files()

    if ledger_path not in changed_files:
        print("✅ No ledger changes detected")
        return 0

    # Load current ledger
    current_ledger = load_ledger(ledger_path)

    # Load previous version
    if args.base_json:
        previous_ledger = load_json_safely(args.base_json)
    else:
        try:
            import subprocess

            result = subprocess.run(
                ["git", "show", f"HEAD~1:{ledger_path}"], capture_output=True, text=True, check=True
            )
            previous_ledger = json.loads(result.stdout)
        except Exception:
            # If we can't get previous version, assume it's empty
            previous_ledger = {"exceptions": {}}

    # Check for new entries
    new_entries = check_ledger_changes(previous_ledger, current_ledger)

    if not new_entries:
        print("✅ No new ledger entries detected")
        return 0

    print(f"⚠️  Found {len(new_entries)} new ledger entries")

    # Check if exception-approved label is present
    if args.labels is not None:
        labels = {s.strip() for s in args.labels.split(",") if s.strip()}
        has_approval = args.approved_label in labels
    else:
        has_approval = check_github_labels()

    # Check each new entry
    invalid_entries = []
    for entry_info in new_entries:
        entry = entry_info["entry"]
        file_path = entry_info["file"]

        # Check expiry
        has_valid_expiry = check_expiry_valid(entry)

        if not has_approval or not has_valid_expiry:
            invalid_entries.append(
                {"file": file_path, "entry": entry, "has_approval": has_approval, "has_valid_expiry": has_valid_expiry}
            )

    if invalid_entries:
        print("❌ Invalid ledger additions detected:")
        for invalid in invalid_entries:
            print(f"  - {invalid['file']}: {invalid['entry'].get('key', 'unknown')}")
            print(f"    Has approval: {invalid['has_approval']}")
            print(f"    Has valid expiry: {invalid['has_valid_expiry']}")

        print("\n🚫 PR Gate Failed")
        print("New ledger entries require:")
        print("1. 'exception-approved' label")
        print("2. Expiry ≤7 days from now")
        return 1

    print("✅ All new ledger entries are properly approved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
