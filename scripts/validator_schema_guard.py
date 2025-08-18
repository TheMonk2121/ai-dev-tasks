#!/usr/bin/env python3.12.123.11
"""
Validator Schema Guard

Guards against validator schema changes without proper migration documentation.
Requires schema-migration label and docs/VALIDATOR_SCHEMA_MIGRATION.md update.
"""

import json
import os
import sys
from typing import Dict


def load_validator_report(path: str) -> dict:
    """Load validator report."""
    if not os.path.exists(path):
        print(f"❌ Validator report not found: {path}")
        return {}

    with open(path) as f:
        return json.load(f)


def check_schema_version(report: dict) -> str:
    """Check schema version in report."""
    return report.get("schema_version", "unknown")


def check_migration_doc() -> bool:
    """Check if migration doc exists and was modified."""
    migration_path = "docs/VALIDATOR_SCHEMA_MIGRATION.md"

    # Check if file exists
    if not os.path.exists(migration_path):
        return False

    # Check if file was modified in this PR
    try:
        import subprocess

        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"], capture_output=True, text=True, check=True
        )
        changed_files = result.stdout.strip().split("\n")
        return migration_path in changed_files
    except Exception:
        return False


def check_schema_migration_label() -> bool:
    """Check if schema-migration label is present."""
    label = os.getenv("GITHUB_LABELS", "")
    return "schema-migration" in label


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Guard validator schema changes")
    parser.add_argument("--report", default="validator_report.json", help="Validator report path")

    args = parser.parse_args()

    # Load validator report
    report = load_validator_report(args.report)
    if not report:
        return 1

    # Check schema version
    schema_version = check_schema_version(report)
    expected_version = "1.1.0"

    print(f"📋 Current schema version: {schema_version}")
    print(f"📋 Expected schema version: {expected_version}")

    if schema_version == expected_version:
        print("✅ Schema version matches expected version")
        return 0

    print(f"⚠️  Schema version mismatch: {schema_version} != {expected_version}")

    # Check if this is an intentional schema change
    has_migration_doc = check_migration_doc()
    has_migration_label = check_schema_migration_label()

    print(f"📋 Migration doc modified: {has_migration_doc}")
    print(f"📋 Schema-migration label: {has_migration_label}")

    if has_migration_doc and has_migration_label:
        print("✅ Schema change properly documented and labeled")
        return 0

    print("❌ Schema change detected without proper documentation")
    print()
    print("To change the validator schema:")
    print("1. Update docs/VALIDATOR_SCHEMA_MIGRATION.md with:")
    print("   - Compatibility impact")
    print("   - Rollout plan")
    print("   - Rollback plan")
    print("2. Add 'schema-migration' label to this PR")
    print("3. Ensure schema_version is updated in validator output")

    return 1


if __name__ == "__main__":
    sys.exit(main())
