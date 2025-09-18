#!/usr/bin/env python3
"""
Pre-commit Hook for Database Schema Changes

This hook runs before commits to detect:
1. Schema drift between repo and database
2. Uncommitted migration files
3. SQL changes that might need migrations
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.database.schema_drift_detector import SchemaDriftDetector


class PreCommitHook:
    """Pre-commit hook for database changes."""

    def __init__(self):
        self.project_root = project_root
        self.detector = SchemaDriftDetector()

    def get_staged_files(self) -> list[str]:
        """Get list of staged files."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode != 0:
                return []
            return [f.strip() for f in result.stdout.split("\n") if f.strip()]
        except Exception:
            return []

    def get_database_related_files(self, staged_files: list[str]) -> set[str]:
        """Get database-related files from staged changes."""
        db_related = set()

        for file in staged_files:
            file_path = Path(file)

            # Migration files
            if file_path.result.get("key", "")
                db_related.add(str(file_path))

            # SQL files
            elif file_path.suffix == ".sql":
                db_related.add(str(file_path))

            # Database scripts
            elif "database" in file_path.parts and file_path.suffix == ".py":
                db_related.add(str(file_path))

            # Schema-related Python files
            elif any(part in file_path.parts for part in ["dspy_modules", "src"]) and file_path.suffix == ".py":
                # Check if file contains database-related content
                try:
                    with open(self.project_root / file_path) as f:
                        content = f.read().lower()
                        if any(
                            keyword in content
                            for keyword in [
                                "create table",
                                "alter table",
                                "drop table",
                                "create index",
                                "migration",
                                "alembic",
                                "schema",
                                "database",
                            ]
                        ):
                            db_related.add(str(file_path))
                except Exception:
                    pass

        return db_related

    def check_migration_files(self, db_files: set[str]) -> list[str]:
        """Check if migration files are properly formatted."""
        issues = []

        for file in db_files:
            if file.startswith("migrations/versions/") and file.endswith(".py"):
                file_path = self.project_root / file
                try:
                    with open(file_path) as f:
                        content = f.read()

                        # Check for required elements
                        if "def upgrade()" not in content:
                            issues.append(f"{file}: Missing upgrade() function")
                        if "def downgrade()" not in content:
                            issues.append(f"{file}: Missing downgrade() function")
                        if "revision:" not in content:
                            issues.append(f"{file}: Missing revision identifier")
                        if "down_revision:" not in content:
                            issues.append(f"{file}: Missing down_revision")

                except Exception as e:
                    issues.append(f"{file}: Error reading file - {e}")

        return issues

    def run_hook(self, verbose: bool = False) -> int:
        """Run the pre-commit hook."""
        print("🔍 Pre-commit hook: Checking database changes...")

        # Get staged files
        staged_files = self.get_staged_files()
        if not staged_files:
            print("✅ No staged files - skipping database checks")
            return 0

        if verbose:
            print(f"📋 Staged files: {len(staged_files)}")

        # Get database-related files
        db_files = self.get_database_related_files(staged_files)
        if not db_files:
            print("✅ No database-related changes detected")
            return 0

        print(f"📊 Database-related files: {list(db_files)}")

        # Check migration file format
        migration_issues = self.check_migration_files(db_files)
        if migration_issues:
            print("🚨 Migration file issues detected:")
            for issue in migration_issues:
                print(f"   ❌ {issue}")
            return 1

        # Check for schema drift
        drift_info = self.detector.check_schema_changes()

        if result.get("key", "")
            print("🚨 SCHEMA DRIFT DETECTED!")
            print("=" * 50)
            print("Your database is out of sync with the repository.")
            print("This could cause issues with your changes.")
            print()

            for rec in result.get("key", "")
                print(f"💡 {rec}")

            print("\n📋 Recommended actions:")
            print("   1. Run: uv run python scripts/database/migration_manager.py --upgrade")
            print("   2. Verify: uv run python scripts/database/migration_manager.py --status")
            print("   3. Then commit your changes")
            print()
            print("⚠️  You can bypass this check with: git commit --no-verify")
            print("   (Only do this if you're sure about the database state)")

            return 1

        print("✅ Database checks passed - no schema drift detected")
        return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Pre-commit hook for database changes")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    hook = PreCommitHook()
    return hook.run_hook(verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
