#!/usr/bin/env python3
"""
LTST Memory System Database Migration Script

This script safely migrates the database to include the LTST Memory System schema
with rollback capability, data validation, and audit logging.
"""

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.database_resilience import DatabaseResilienceManager
from utils.logger import setup_logger

logger = setup_logger(__name__)


class LTSTMigrationManager:
    """Manages LTST Memory System database migration."""

    def __init__(self, db_url: Optional[str] = None):
        """Initialize migration manager."""
        self.db_url = db_url or os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")
        self.db_manager = DatabaseResilienceManager(self.db_url)
        self.migration_log = []
        self.backup_tables = []
        self.rollback_commands = []

    def log_migration(self, message: str, level: str = "INFO"):
        """Log migration step."""
        timestamp = datetime.now().isoformat()
        log_entry = {"timestamp": timestamp, "level": level, "message": message}
        self.migration_log.append(log_entry)
        logger.info(f"[{timestamp}] {message}")

    def create_backup(self) -> bool:
        """Create backup of existing data."""
        try:
            self.log_migration("Creating backup of existing data...")

            # Get list of existing tables
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name LIKE 'conversation_%'
                    """
                    )
                    existing_tables = [row[0] for row in cursor.fetchall()]

                    if not existing_tables:
                        self.log_migration("No existing conversation tables found, skipping backup")
                        return True

                    # Create backup tables
                    for table in existing_tables:
                        backup_table = f"{table}_backup_{int(time.time())}"
                        cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM {table}")
                        self.backup_tables.append(backup_table)
                        self.rollback_commands.append(f"DROP TABLE IF EXISTS {backup_table}")
                        self.log_migration(f"Created backup table: {backup_table}")

                    conn.commit()
                    self.log_migration(f"Backup completed: {len(self.backup_tables)} tables backed up")
                    return True

        except Exception as e:
            self.log_migration(f"Backup failed: {e}", "ERROR")
            return False

    def validate_prerequisites(self) -> bool:
        """Validate migration prerequisites."""
        try:
            self.log_migration("Validating migration prerequisites...")

            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Check PostgreSQL version
                    cursor.execute("SELECT version()")
                    version = cursor.fetchone()[0]
                    if "PostgreSQL" not in version:
                        self.log_migration("Not a PostgreSQL database", "ERROR")
                        return False

                    # Check pgvector extension
                    cursor.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM pg_extension
                            WHERE extname = 'vector'
                        )
                    """
                    )
                    pgvector_exists = cursor.fetchone()[0]
                    if not pgvector_exists:
                        self.log_migration("pgvector extension not found", "ERROR")
                        return False

                    # Check database permissions
                    cursor.execute("SELECT current_user")
                    current_user = cursor.fetchone()[0]
                    self.log_migration(f"Connected as user: {current_user}")

                    # Test CREATE TABLE permission
                    test_table = f"test_migration_{int(time.time())}"
                    cursor.execute(f"CREATE TABLE {test_table} (id INTEGER)")
                    cursor.execute(f"DROP TABLE {test_table}")

                    self.log_migration("Prerequisites validation passed")
                    return True

        except Exception as e:
            self.log_migration(f"Prerequisites validation failed: {e}", "ERROR")
            return False

    def run_migration(self, dry_run: bool = False) -> bool:
        """Run the migration."""
        try:
            self.log_migration(f"Starting LTST migration (dry_run: {dry_run})...")

            # Read migration SQL
            migration_file = Path(__file__).parent.parent / "config" / "database" / "ltst_schema_migration.sql"
            if not migration_file.exists():
                self.log_migration(f"Migration file not found: {migration_file}", "ERROR")
                return False

            with open(migration_file, "r") as f:
                migration_sql = f.read()

            if dry_run:
                self.log_migration("DRY RUN: Would execute migration SQL")
                self.log_migration(f"SQL Preview:\n{migration_sql[:500]}...")
                return True

            # Execute migration
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Split SQL into individual statements
                    statements = [stmt.strip() for stmt in migration_sql.split(";") if stmt.strip()]

                    for i, statement in enumerate(statements, 1):
                        if statement.startswith("--") or not statement:
                            continue

                        try:
                            self.log_migration(f"Executing statement {i}/{len(statements)}")
                            cursor.execute(statement)
                            self.log_migration(f"Statement {i} executed successfully")
                        except Exception as e:
                            self.log_migration(f"Statement {i} failed: {e}", "ERROR")
                            self.log_migration(f"Failed SQL: {statement[:200]}...", "ERROR")
                            return False

                    conn.commit()
                    self.log_migration("Migration completed successfully")
                    return True

        except Exception as e:
            self.log_migration(f"Migration failed: {e}", "ERROR")
            return False

    def validate_migration(self) -> bool:
        """Validate the migration was successful."""
        try:
            self.log_migration("Validating migration results...")

            expected_tables = [
                "conversation_sessions",
                "conversation_messages",
                "conversation_context",
                "user_preferences",
                "session_relationships",
                "session_summary",
            ]

            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    for table in expected_tables:
                        cursor.execute(
                            """
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables
                                WHERE table_name = %s
                            )
                        """,
                            (table,),
                        )
                        exists = cursor.fetchone()[0]
                        if not exists:
                            self.log_migration(f"Table {table} not found after migration", "ERROR")
                            return False
                        self.log_migration(f"Table {table} validated")

                    # Check indexes
                    expected_indexes = [
                        "idx_conversation_sessions_user_id",
                        "idx_conversation_messages_session_id",
                        "idx_conversation_messages_embedding",
                    ]

                    for index in expected_indexes:
                        cursor.execute(
                            """
                            SELECT EXISTS (
                                SELECT FROM pg_indexes
                                WHERE indexname = %s
                            )
                        """,
                            (index,),
                        )
                        exists = cursor.fetchone()[0]
                        if not exists:
                            self.log_migration(f"Index {index} not found after migration", "ERROR")
                            return False
                        self.log_migration(f"Index {index} validated")

                    # Check functions
                    expected_functions = ["update_session_activity", "clean_expired_context", "update_session_summary"]

                    for func in expected_functions:
                        cursor.execute(
                            """
                            SELECT EXISTS (
                                SELECT FROM pg_proc p
                                JOIN pg_namespace n ON p.pronamespace = n.oid
                                WHERE n.nspname = 'public'
                                AND p.proname = %s
                            )
                        """,
                            (func,),
                        )
                        exists = cursor.fetchone()[0]
                        if not exists:
                            self.log_migration(f"Function {func} not found after migration", "ERROR")
                            return False
                        self.log_migration(f"Function {func} validated")

                    self.log_migration("Migration validation completed successfully")
                    return True

        except Exception as e:
            self.log_migration(f"Migration validation failed: {e}", "ERROR")
            return False

    def rollback(self) -> bool:
        """Rollback the migration."""
        try:
            self.log_migration("Starting rollback...")

            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Drop new tables
                    tables_to_drop = [
                        "session_summary",
                        "session_relationships",
                        "user_preferences",
                        "conversation_context",
                        "conversation_messages",
                        "conversation_sessions",
                    ]

                    for table in tables_to_drop:
                        try:
                            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                            self.log_migration(f"Dropped table: {table}")
                        except Exception as e:
                            self.log_migration(f"Failed to drop table {table}: {e}", "WARNING")

                    # Drop functions
                    functions_to_drop = [
                        "update_session_activity",
                        "clean_expired_context",
                        "update_session_summary",
                        "trigger_update_session_activity",
                        "trigger_update_session_summary",
                    ]

                    for func in functions_to_drop:
                        try:
                            cursor.execute(f"DROP FUNCTION IF EXISTS {func} CASCADE")
                            self.log_migration(f"Dropped function: {func}")
                        except Exception as e:
                            self.log_migration(f"Failed to drop function {func}: {e}", "WARNING")

                    # Restore backup tables if they exist
                    for backup_table in self.backup_tables:
                        original_table = backup_table.replace(f"_backup_{int(time.time())}", "")
                        try:
                            cursor.execute(f"DROP TABLE IF EXISTS {original_table}")
                            cursor.execute(f"ALTER TABLE {backup_table} RENAME TO {original_table}")
                            self.log_migration(f"Restored table: {original_table}")
                        except Exception as e:
                            self.log_migration(f"Failed to restore table {original_table}: {e}", "WARNING")

                    conn.commit()
                    self.log_migration("Rollback completed")
                    return True

        except Exception as e:
            self.log_migration(f"Rollback failed: {e}", "ERROR")
            return False

    def save_migration_log(self, filename: Optional[str] = None) -> str:
        """Save migration log to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ltst_migration_log_{timestamp}.json"

        log_file = Path(filename)

        import json

        with open(log_file, "w") as f:
            json.dump(self.migration_log, f, indent=2)

        self.log_migration(f"Migration log saved to: {log_file}")
        return str(log_file)

    def cleanup_backup_tables(self) -> bool:
        """Clean up backup tables."""
        try:
            self.log_migration("Cleaning up backup tables...")

            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    for backup_table in self.backup_tables:
                        try:
                            cursor.execute(f"DROP TABLE IF EXISTS {backup_table}")
                            self.log_migration(f"Dropped backup table: {backup_table}")
                        except Exception as e:
                            self.log_migration(f"Failed to drop backup table {backup_table}: {e}", "WARNING")

                    conn.commit()
                    self.log_migration("Backup cleanup completed")
                    return True

        except Exception as e:
            self.log_migration(f"Backup cleanup failed: {e}", "ERROR")
            return False


def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description="LTST Memory System Database Migration")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    parser.add_argument("--rollback", action="store_true", help="Rollback the migration")
    parser.add_argument("--validate-only", action="store_true", help="Only validate prerequisites")
    parser.add_argument("--cleanup", action="store_true", help="Clean up backup tables")
    parser.add_argument("--log-file", help="Save migration log to specified file")
    parser.add_argument("--db-url", help="Database connection URL")

    args = parser.parse_args()

    # Initialize migration manager
    migration_manager = LTSTMigrationManager(args.db_url)

    try:
        if args.rollback:
            success = migration_manager.rollback()
        elif args.validate_only:
            success = migration_manager.validate_prerequisites()
        elif args.cleanup:
            success = migration_manager.cleanup_backup_tables()
        else:
            # Full migration process
            if not migration_manager.validate_prerequisites():
                sys.exit(1)

            if not args.dry_run:
                if not migration_manager.create_backup():
                    sys.exit(1)

            if not migration_manager.run_migration(dry_run=args.dry_run):
                sys.exit(1)

            if not args.dry_run:
                if not migration_manager.validate_migration():
                    migration_manager.log_migration("Migration validation failed, rolling back...", "ERROR")
                    migration_manager.rollback()
                    sys.exit(1)

                # Clean up backup tables on success
                migration_manager.cleanup_backup_tables()

            success = True

        # Save migration log
        log_file = migration_manager.save_migration_log(args.log_file)

        if success:
            migration_manager.log_migration("Migration process completed successfully")
            print(f"✅ Migration completed successfully. Log saved to: {log_file}")
        else:
            migration_manager.log_migration("Migration process failed")
            print(f"❌ Migration failed. Check log: {log_file}")
            sys.exit(1)

    except KeyboardInterrupt:
        migration_manager.log_migration("Migration interrupted by user", "WARNING")
        print("⚠️ Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        migration_manager.log_migration(f"Unexpected error: {e}", "ERROR")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
