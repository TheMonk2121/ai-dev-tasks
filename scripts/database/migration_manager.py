#!/usr/bin/env python3
"""
Database Migration Manager for psycopg3 + pgvector + TimescaleDB

This script provides a unified interface for managing database migrations
using Alembic with your existing psycopg3 setup.

Usage:
    python scripts/database/migration_manager.py --status
    python scripts/database/migration_manager.py --upgrade
    python scripts/database/migration_manager.py --downgrade
    python scripts/database/migration_manager.py --create "Add new table"
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


class MigrationManager:
    """Manages database migrations using Alembic with psycopg3."""

    def __init__(self) -> None:
        self.project_root: Any = project_root
        self.alembic_cmd: Any = ["uv", "run", "alembic"]

    def check_database_connection(self) -> bool:
        """Check if database connection is available."""
        try:
            dsn = resolve_dsn(strict=False, role="migration")
            if not dsn or dsn.startswith("mock://"):
                print("❌ No valid database connection found")
                print("   Set POSTGRES_DSN or DATABASE_URL environment variable")
                return False
            print(f"✅ Database connection: {dsn[:30]}...")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

    def run_alembic_command(self, args: list[str], capture_output: bool = False) -> Any:
        """Run an alembic command with proper environment."""
        cmd = self.alembic_cmd + args

        # Set working directory to project root
        env = os.environ.copy()

        try:
            if capture_output:
                result: Any = subprocess.run(cmd, cwd=self.project_root, env=env, capture_output=True, text=True)
                return result
            else:
                result: Any = subprocess.run(cmd, cwd=self.project_root, env=env, check=True)
                return result.returncode
        except subprocess.CalledProcessError as e:
            print(f"❌ Alembic command failed: {e}")
            return e.returncode

    def status(self) -> int:
        """Show migration status."""
        print("🔍 Checking migration status...")
        if not self.check_database_connection():
            return 1

        return self.run_alembic_command(["current"])

    def upgrade(self, revision: str = "head") -> int:
        """Upgrade database to specified revision."""
        print(f"⬆️  Upgrading database to {revision}...")
        if not self.check_database_connection():
            return 1

        # If upgrading to head, check for multiple heads first
        if revision == "head":
            result: Any = self.run_alembic_command(["heads"], capture_output=True)
            if result.returncode == 0 and "Multiple head revisions" in result.stdout:
                # Multiple heads detected, upgrade to all heads
                print("⚠️  Multiple head revisions detected, upgrading to all heads...")
                return self.run_alembic_command(["upgrade", "heads"])

        return self.run_alembic_command(["upgrade", revision])

    def downgrade(self, revision: str = "-1") -> int:
        """Downgrade database by specified number of revisions."""
        print(f"⬇️  Downgrading database by {revision}...")
        if not self.check_database_connection():
            return 1

        return self.run_alembic_command(["downgrade", revision])

    def create(self, message: str) -> int:
        """Create a new migration."""
        print(f"📝 Creating migration: {message}")
        if not self.check_database_connection():
            return 1

        return self.run_alembic_command(["revision", "-m", message])

    def history(self) -> int:
        """Show migration history."""
        print("📚 Migration history:")
        return self.run_alembic_command(["history"])

    def heads(self) -> int:
        """Show current migration heads."""
        print("🎯 Current migration heads:")
        return self.run_alembic_command(["heads"])

    def stamp(self, revision: str = "head") -> int:
        """Stamp database with current revision without running migrations."""
        print(f"🏷️  Stamping database with {revision}...")
        if not self.check_database_connection():
            return 1

        return self.run_alembic_command(["stamp", revision])


def main() -> None:
    """Main entry point."""
    parser: Any = argparse.ArgumentParser(description="Database Migration Manager")
    parser.add_argument("--status", action="store_true", help="Show migration status")
    parser.add_argument("--upgrade", nargs="?", const="head", help="Upgrade database (default: head)")
    parser.add_argument("--downgrade", nargs="?", const="-1", help="Downgrade database (default: -1)")
    parser.add_argument("--create", help="Create new migration with message")
    parser.add_argument("--history", action="store_true", help="Show migration history")
    parser.add_argument("--heads", action="store_true", help="Show current heads")
    parser.add_argument("--stamp", nargs="?", const="head", help="Stamp database (default: head)")

    args: Any = parser.parse_args()

    manager = MigrationManager()

    if args.status:
        return manager.status()
    elif args.upgrade is not None:
        return manager.upgrade(args.upgrade)
    elif args.downgrade is not None:
        return manager.downgrade(args.downgrade)
    elif args.create:
        return manager.create(args.create)
    elif args.history:
        return manager.history()
    elif args.heads:
        return manager.heads()
    elif args.stamp is not None:
        return manager.stamp(args.stamp)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
