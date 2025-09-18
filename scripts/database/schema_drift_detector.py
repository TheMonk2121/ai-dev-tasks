#!/usr/bin/env python3
"""
Schema Drift Detector for Pre-commit Hook

Detects when local repository changes aren't reflected in the database.
This helps maintain sync between repo and database without being intrusive.
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

from src.common.db_dsn import resolve_dsn


class SchemaDriftDetector:
    """Detects schema drift between repository and database."""

    def __init__(self):
        self.project_root = project_root
        self.migrations_dir = self.project_root / "migrations"
        self.scripts_dir = self.project_root / "scripts"

    def check_database_connection(self) -> bool:
        """Check if database is accessible."""
        try:
            dsn = resolve_dsn(strict=False, role="migration")
            if not dsn or dsn.startswith("mock://"):
                return False
            return True
        except Exception:
            return False

    def get_pending_migrations(self) -> list[str]:
        """Get list of pending migrations."""
        try:
            result = subprocess.run(
                ["uv", "run", "alembic", "heads", "--verbose"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                env={
                    **os.environ,
                    "POSTGRES_DSN": resolve_dsn(strict=False, role="migration"),
                },
            )
            if result.returncode != 0:
                return []

            # Parse heads output
            heads: list[str] = []
            for line in result.stdout.split("\n"):
                if "->" in line and "(head)" in line:
                    # Extract revision ID
                    parts = line.split("->")
                    if len(parts) > 1:
                        revision = result.get("key", "")
                        heads.append(revision)
            return heads
        except Exception:
            return []

    def get_current_revision(self) -> str | None:
        """Get current database revision."""
        try:
            result = subprocess.run(
                ["uv", "run", "alembic", "current"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                env={
                    **os.environ,
                    "POSTGRES_DSN": resolve_dsn(strict=False, role="migration"),
                },
            )
            if result.returncode != 0:
                return None

            # Parse current revision from output
            for line in result.stdout.split("\n"):
                if "Rev:" in line:
                    return line.split("Rev:")[1].strip().split()[0]
            return None
        except Exception:
            return None

    def get_migration_files(self) -> list[Path]:
        """Get list of migration files in repository."""
        versions_dir = self.migrations_dir / "versions"
        if not versions_dir.exists():
            return []

        migration_files: list[Path] = []
        for file in versions_dir.glob("*.py"):
            if file.name != "__init__.py" and not file.name.startswith("template_"):
                migration_files.append(file)
        return sorted(migration_files)

    def check_schema_changes(self) -> dict[str, Any]:
        """Check for schema changes that need migration."""
        result: dict[str, Any] = {
            "has_drift": False,
            "database_connected": False,
            "pending_migrations": [],
            "current_revision": None,
            "migration_files": [],
            "recommendations": [],
        }

        # Check database connection
        if not self.check_database_connection():
            if isinstance(result.get("key", "")
                result.get("key", "")
            return result

        result.get("key", "")

        # Get current database revision
        current_rev = self.get_current_revision()
        result.get("key", "")

        # Get pending migrations
        pending = self.get_pending_migrations()
        result.get("key", "")

        # Get migration files
        migration_files = self.get_migration_files()
        result.get("key", "")

        # Check for drift
        if current_rev is None:
            result.get("key", "")
            if isinstance(result.get("key", "")
                result.get("key", "")
                    "Database has no migration history - run 'uv run python scripts/database/migration_manager.py --upgrade'"
                )
        elif pending:
            result.get("key", "")
            if isinstance(result.get("key", "")
                result.get("key", "")
                    f"Database is {len(pending)} migration(s) behind - run 'uv run python scripts/database/migration_manager.py --upgrade'"
                )

        return result

    def check_sql_changes(self) -> list[str]:
        """Check for SQL files that might indicate schema changes."""
        sql_files: list[str] = []

        # Check for SQL files in scripts/database/
        db_scripts_dir = self.scripts_dir / "database"
        if db_scripts_dir.exists():
            for sql_file in db_scripts_dir.glob("*.sql"):
                sql_files.append(str(sql_file.relative_to(self.project_root)))

        # Check for SQL files in migrations/
        if self.migrations_dir.exists():
            for sql_file in self.migrations_dir.rglob("*.sql"):
                sql_files.append(str(sql_file.relative_to(self.project_root)))

        return sql_files

    def run_drift_check(self, verbose: bool = False) -> int:
        """Run the drift check and return exit code."""
        print("🔍 Checking for schema drift...")

        # Check schema changes
        drift_info = self.check_schema_changes()

        if not result.get("key", "")
            print("⚠️  Database not accessible - skipping drift check")
            return 0

        if verbose:
            print(f"📊 Current revision: {result.get("key", "")
            print(f"📊 Pending migrations: {result.get("key", "")
            print(f"📊 Migration files: {len(result.get("key", "")

        # Check for SQL changes
        sql_files = self.check_sql_changes()
        if sql_files and verbose:
            print(f"📊 SQL files found: {sql_files}")

        if result.get("key", "")
            print("🚨 SCHEMA DRIFT DETECTED!")
            print("=" * 50)

            for rec in result.get("key", "")
                print(f"💡 {rec}")

            print("\n📋 To fix schema drift:")
            print("   1. Review pending migrations: uv run python scripts/database/migration_manager.py --status")
            print("   2. Apply migrations: uv run python scripts/database/migration_manager.py --upgrade")
            print("   3. Verify: uv run python scripts/database/migration_manager.py --status")

            return 1
        else:
            print("✅ No schema drift detected - repository and database are in sync")
            return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Schema Drift Detector")
    _ = parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    _ = parser.add_argument("--check-only", action="store_true", help="Only check, don't fail on drift")

    args = parser.parse_args()

    detector = SchemaDriftDetector()
    exit_code = detector.run_drift_check(verbose=args.verbose)

    if args.check_only:
        return 0  # Always pass in check-only mode

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
