#!/usr/bin/env python3.12.123.11
"""
Ledger Sweep - Fail PRs that extend expired waiver entries without content changes.

This script checks if a PR is trying to extend expired waiver entries in the validator
exception ledger without making corresponding content changes. It's designed to prevent
waiver creep and encourage conversion to real fixes.
"""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime


def load_ledger(ledger_path: str) -> dict:
    """Load the validator exception ledger."""
    try:
        with open(ledger_path) as f:
            data = json.load(f)
        return data.get("exceptions", {})
    except Exception:
        return {}


def get_expired_entries(ledger: dict) -> list[tuple[str, str, str]]:
    """Get all expired entries from the ledger."""
    expired = []
    now = datetime.now(UTC)

    for file_path, entries in ledger.items():
        for entry in entries:
            expires = entry.get("expires")
            if not expires:
                continue

            try:
                # Parse expiry date
                if len(expires) == 10 and expires[4] == "-" and expires[7] == "-":
                    expiry = datetime.fromisoformat(expires).replace(hour=23, minute=59, second=59, tzinfo=UTC)
                else:
                    expiry = datetime.fromisoformat(expires.replace("Z", "+00:00"))

                if now > expiry:
                    expired.append((file_path, entry.get("key", ""), expires))
            except Exception:
                continue

    return expired


def get_changed_files() -> set[str]:
    """Get list of files changed in the current PR."""
    try:
        # Get changed files from git
        result = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True, check=True)
        return set(result.stdout.strip().split("\n") if result.stdout.strip() else [])
    except subprocess.CalledProcessError:
        return set()


def check_content_changes(file_path: str) -> bool:
    """Check if a file has meaningful content changes (not just ledger updates)."""
    try:
        # Get diff for the file
        result = subprocess.run(["git", "diff", "HEAD~1", "--", file_path], capture_output=True, text=True, check=True)
        diff = result.stdout

        # Check if diff contains actual content changes (not just ledger lines)
        lines = diff.split("\n")
        content_changes = 0
        ledger_changes = 0

        for line in lines:
            if line.startswith("+") and not line.startswith("+++"):
                if "validator_exceptions.json" in line or "expires" in line:
                    ledger_changes += 1
                else:
                    content_changes += 1

        # Consider it a content change if there are more content lines than ledger lines
        return content_changes > ledger_changes
    except subprocess.CalledProcessError:
        return False


def main():
    """Main function to check for expired waiver extensions."""
    ledger_path = "data/validator_exceptions.json"

    if not os.path.exists(ledger_path):
        print("X Validator exception ledger not found")
        sys.exit(1)

    # Load current ledger
    ledger = load_ledger(ledger_path)

    # Get expired entries
    expired_entries = get_expired_entries(ledger)

    if not expired_entries:
        print("OK No expired entries found in ledger")
        return

    print(f"📋 Found {len(expired_entries)} expired entries in ledger")

    # Get changed files
    changed_files = get_changed_files()

    # Check for problematic extensions
    problematic_extensions = []

    for file_path, key, expires in expired_entries:
        if file_path in changed_files:
            # Check if the file has meaningful content changes
            has_content_changes = check_content_changes(file_path)

            if not has_content_changes:
                problematic_extensions.append(
                    {"file": file_path, "key": key, "expires": expires, "reason": "No content changes detected"}
                )

    if problematic_extensions:
        print("\nX PROBLEMATIC WAIVER EXTENSIONS DETECTED:")
        print("The following files have expired waiver entries but no meaningful content changes:")

        for ext in problematic_extensions:
            print(f"  - {ext['file']} (key: {ext['key']}, expired: {ext['expires']})")
            print(f"    Reason: {ext['reason']}")

        print("\n💡 RECOMMENDATIONS:")
        print("1. Convert expired waivers to actual fixes (links, README sections, etc.)")
        print("2. Do not extend expired waivers without content changes")
        print("3. Use short-term waivers only for temporary exceptions")

        sys.exit(1)
    else:
        print("OK No problematic waiver extensions detected")
        print("All expired entries either have content changes or are not being extended")


if __name__ == "__main__":
    main()
