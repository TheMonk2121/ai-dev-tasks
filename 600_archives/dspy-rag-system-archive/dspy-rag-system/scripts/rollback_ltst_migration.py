#!/usr/bin/env python3
# type: ignore
"""
LTST Memory System Migration Rollback Script

This script safely rolls back the LTST memory system migration,
removing all new tables, functions, and views while preserving existing data.

Note: Type ignore is used because RealDictCursor returns dictionary-like objects
that the type checker doesn't properly recognize, and database connection objects
are properly handled with null checks at runtime.
"""

import argparse
import logging
import os
import sys
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor


class LTSTRollbackManager:
    """Manages LTST memory system rollback."""

    def __init__(self, database_url: str | None = None, dry_run: bool = False):
        """Initialize rollback manager."""
        self.database_url = database_url or os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")
        self.dry_run = dry_run
        self.connection = None
        self.cursor = None
        self.rollback_log = []

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("ltst_rollback.log"), logging.StreamHandler(sys.stdout)],
        )
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(self.database_url)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            self.logger.info("Database connection established")
            return True
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            return False

    def disconnect(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        self.logger.info("Database connection closed")

    def log_rollback_step(self, step: str, query: str | None = None, success: bool = True, error: str | None = None):
        """Log rollback step for audit trail."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "query": query,
            "success": success,
            "error": error,
            "dry_run": self.dry_run,
        }
        self.rollback_log.append(log_entry)

        if success:
            self.logger.info(f"✅ {step}")
        else:
            self.logger.error(f"❌ {step}: {error}")

    def check_existing_ltst_tables(self) -> list:
        """Check which LTST tables exist."""
        try:
            self.cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN (
                    'conversation_sessions', 'conversation_messages', 'conversation_context',
                    'user_preferences', 'memory_retrieval_cache', 'session_relationships',
                    'memory_performance_metrics'
                )
            """
            )
            existing_tables = [row["table_name"] for row in self.cursor.fetchall()]
            self.logger.info(f"Found {len(existing_tables)} LTST tables: {existing_tables}")
            return existing_tables
        except Exception as e:
            self.logger.error(f"Failed to check existing tables: {e}")
            return []

    def backup_ltst_data(self) -> bool:
        """Create backup of LTST data before rollback."""
        if self.dry_run:
            self.logger.info("DRY RUN: Would create backup")
            return True

        try:
            self.logger.info("Creating backup of LTST data...")

            existing_tables = self.check_existing_ltst_tables()
            if not existing_tables:
                self.logger.info("No LTST tables found, skipping backup")
                return True

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            for table in existing_tables:
                backup_table = f"{table}_backup_{timestamp}"
                self.cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM {table};")
                self.log_rollback_step(f"Created backup table: {backup_table}")

            self.connection.commit()
            self.logger.info(f"Backup completed: {len(existing_tables)} tables backed up")
            return True

        except Exception as e:
            self.log_rollback_step("Backup creation failed", success=False, error=str(e))
            return False

    def rollback_tables(self) -> bool:
        """Drop LTST tables in correct order."""
        try:
            self.logger.info("Dropping LTST tables...")

            # Drop tables in reverse dependency order
            tables_to_drop = [
                "memory_performance_metrics",  # No dependencies
                "session_relationships",  # Depends on conversation_sessions
                "memory_retrieval_cache",  # No dependencies
                "conversation_context",  # Depends on conversation_sessions
                "conversation_messages",  # Depends on conversation_sessions
                "user_preferences",  # No dependencies
                "conversation_sessions",  # Base table
            ]

            for table in tables_to_drop:
                try:
                    if not self.dry_run:
                        self.cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")

                    self.log_rollback_step(f"Dropped table: {table}")

                except Exception as e:
                    self.log_rollback_step(f"Failed to drop table {table}", success=False, error=str(e))

            if not self.dry_run:
                self.connection.commit()

            return True

        except Exception as e:
            self.log_rollback_step("Table rollback failed", success=False, error=str(e))
            if not self.dry_run:
                self.connection.rollback()
            return False

    def rollback_functions(self) -> bool:
        """Drop LTST functions."""
        try:
            self.logger.info("Dropping LTST functions...")

            functions_to_drop = ["update_session_length", "clean_expired_cache", "clean_expired_context"]

            for func in functions_to_drop:
                try:
                    if not self.dry_run:
                        self.cursor.execute(f"DROP FUNCTION IF EXISTS {func} CASCADE;")

                    self.log_rollback_step(f"Dropped function: {func}")

                except Exception as e:
                    self.log_rollback_step(f"Failed to drop function {func}", success=False, error=str(e))

            if not self.dry_run:
                self.connection.commit()

            return True

        except Exception as e:
            self.log_rollback_step("Function rollback failed", success=False, error=str(e))
            if not self.dry_run:
                self.connection.rollback()
            return False

    def rollback_views(self) -> bool:
        """Drop LTST views."""
        try:
            self.logger.info("Dropping LTST views...")

            views_to_drop = ["session_summary", "user_preference_summary"]

            for view in views_to_drop:
                try:
                    if not self.dry_run:
                        self.cursor.execute(f"DROP VIEW IF EXISTS {view} CASCADE;")

                    self.log_rollback_step(f"Dropped view: {view}")

                except Exception as e:
                    self.log_rollback_step(f"Failed to drop view {view}", success=False, error=str(e))

            if not self.dry_run:
                self.connection.commit()

            return True

        except Exception as e:
            self.log_rollback_step("View rollback failed", success=False, error=str(e))
            if not self.dry_run:
                self.connection.rollback()
            return False

    def validate_rollback(self) -> bool:
        """Validate that rollback was successful."""
        try:
            self.logger.info("Validating rollback...")

            # Check that LTST tables are gone
            existing_tables = self.check_existing_ltst_tables()
            if existing_tables:
                self.logger.error(f"LTST tables still exist: {existing_tables}")
                return False

            # Check that existing tables are preserved
            self.cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('conversation_memory', 'document_chunks', 'documents')
            """
            )
            preserved_tables = [row["table_name"] for row in self.cursor.fetchall()]

            expected_preserved = ["conversation_memory", "document_chunks", "documents"]
            missing_tables = set(expected_preserved) - set(preserved_tables)

            if missing_tables:
                self.logger.error(f"Missing preserved tables: {missing_tables}")
                return False

            self.logger.info("✅ Rollback validation successful")
            return True

        except Exception as e:
            self.logger.error(f"Rollback validation failed: {e}")
            return False

    def save_rollback_log(self, filename: str | None = None):
        """Save rollback log to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ltst_rollback_log_{timestamp}.json"

        try:
            import json

            with open(filename, "w") as f:
                json.dump(self.rollback_log, f, indent=2)
            self.logger.info(f"Rollback log saved to: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save rollback log: {e}")

    def run_rollback(self) -> bool:
        """Run the complete rollback process."""
        self.logger.info("Starting LTST Memory System rollback...")

        try:
            # Step 1: Check existing LTST tables
            existing_tables = self.check_existing_ltst_tables()
            if not existing_tables:
                self.logger.info("No LTST tables found. Rollback not needed.")
                return True

            # Step 2: Create backup
            if not self.backup_ltst_data():
                self.logger.error("Backup creation failed. Aborting rollback.")
                return False

            # Step 3: Rollback views
            if not self.rollback_views():
                self.logger.error("View rollback failed.")
                return False

            # Step 4: Rollback functions
            if not self.rollback_functions():
                self.logger.error("Function rollback failed.")
                return False

            # Step 5: Rollback tables
            if not self.rollback_tables():
                self.logger.error("Table rollback failed.")
                return False

            # Step 6: Validate rollback
            if not self.validate_rollback():
                self.logger.error("Rollback validation failed.")
                return False

            # Step 7: Save rollback log
            self.save_rollback_log()

            self.logger.info("🎉 LTST Memory System rollback completed successfully!")
            return True

        except Exception as e:
            self.logger.error(f"Rollback failed with unexpected error: {e}")
            return False


def main():
    """Main rollback script entry point."""
    parser = argparse.ArgumentParser(description="LTST Memory System Database Rollback")
    parser.add_argument("--database-url", help="Database connection URL")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without making changes")
    parser.add_argument("--check-only", action="store_true", help="Only check what would be rolled back")

    args = parser.parse_args()

    rollback_manager = LTSTRollbackManager(database_url=args.database_url, dry_run=args.dry_run)

    if not rollback_manager.connect():
        sys.exit(1)

    try:
        if args.check_only:
            existing_tables = rollback_manager.check_existing_ltst_tables()
            print(f"Found {len(existing_tables)} LTST tables: {existing_tables}")
            success = True
        else:
            success = rollback_manager.run_rollback()

        if success:
            sys.exit(0)
        else:
            sys.exit(1)

    finally:
        rollback_manager.disconnect()


if __name__ == "__main__":
    main()
