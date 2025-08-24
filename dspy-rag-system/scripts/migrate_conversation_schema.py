#!/usr/bin/env python3
"""
LTST Memory System Database Migration Script

This script safely migrates the database to include the LTST Memory System schema
with rollback capability and comprehensive validation.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup
from src.utils.database_resilience import DatabaseResilienceManager as DatabaseManager  # noqa: E402
from src.utils.logger import setup_logger  # noqa: E402

# Setup logging
logger = setup_logger(__name__)


class LTSTMemoryMigration:
    """Handles LTST Memory System database migration with safety features."""

    def __init__(self, db_config: Optional[Dict[str, Any]] = None):
        """Initialize migration with database configuration."""
        self.db_config = db_config or {}
        # Get connection string from environment or config
        connection_string = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
        self.db_manager = DatabaseManager(connection_string)
        self.migration_log = []
        self.backup_created = False
        self.migration_started = False

        # Migration metadata
        self.migration_id = f"ltst_memory_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.schema_file = project_root / "config" / "database" / "ltst_memory_schema.sql"
        self.backup_file = project_root / "config" / "database" / f"backup_{self.migration_id}.sql"

    def validate_prerequisites(self) -> bool:
        """Validate that all prerequisites are met for migration."""
        logger.info("Validating migration prerequisites...")

        try:
            # Check if schema file exists
            if not self.schema_file.exists():
                logger.error(f"Schema file not found: {self.schema_file}")
                return False

            # Check database connection
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if pgvector extension is available
                    cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                    if not cursor.fetchone():
                        logger.error("pgvector extension is not installed")
                        return False

                    # Check if we're in a transaction
                    cursor.execute("SELECT txid_current()")
                    tx_id = cursor.fetchone()[0]
                    logger.info(f"Current transaction ID: {tx_id}")

            logger.info("Prerequisites validation passed")
            return True

        except Exception as e:
            logger.error(f"Prerequisites validation failed: {e}")
            return False

    def create_backup(self) -> bool:
        """Create a backup of the current database state."""
        logger.info("Creating database backup...")

        try:
            with self.db_manager.get_connection():
                # Create backup using pg_dump
                backup_command = f"""
                pg_dump -h {self.db_config.get('host', 'localhost')} \
                        -U {self.db_config.get('user', 'postgres')} \
                        -d {self.db_config.get('database', 'dspy_rag')} \
                        --schema-only --no-owner --no-privileges \
                        -f {self.backup_file}
                """

                # Set password environment variable if provided
                if "password" in self.db_config:
                    os.environ["PGPASSWORD"] = self.db_config["password"]

                result = os.system(backup_command)

                if result == 0:
                    self.backup_created = True
                    logger.info(f"Backup created successfully: {self.backup_file}")
                    self.migration_log.append(
                        {
                            "timestamp": datetime.now().isoformat(),
                            "action": "backup_created",
                            "file": str(self.backup_file),
                        }
                    )
                    return True
                else:
                    logger.error("Backup creation failed")
                    return False

        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return False

    def validate_schema_sql(self) -> bool:
        """Validate the schema SQL file for syntax and safety."""
        logger.info("Validating schema SQL file...")

        try:
            with open(self.schema_file, "r") as f:
                schema_sql = f.read()

            # Basic validation checks
            validation_checks = [
                ("CREATE TABLE IF NOT EXISTS", "Uses IF NOT EXISTS for safety"),
                ("CREATE INDEX IF NOT EXISTS", "Uses IF NOT EXISTS for indexes"),
                ("CREATE OR REPLACE FUNCTION", "Uses OR REPLACE for functions"),
                ("CREATE OR REPLACE VIEW", "Uses OR REPLACE for views"),
                ("--", "Contains comments for documentation"),
                ("conversation_sessions", "Contains conversation_sessions table"),
                ("conversation_messages", "Contains conversation_messages table"),
                ("user_preferences", "Contains user_preferences table"),
            ]

            for check, description in validation_checks:
                if check not in schema_sql:
                    logger.error(f"Schema validation failed: {description}")
                    return False

            # Check for potentially dangerous operations
            dangerous_patterns = ["DROP TABLE", "TRUNCATE", "DELETE FROM", "ALTER TABLE DROP"]

            for pattern in dangerous_patterns:
                if pattern in schema_sql.upper():
                    logger.warning(f"Potentially dangerous pattern found: {pattern}")

            logger.info("Schema SQL validation passed")
            return True

        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False

    def execute_migration(self, dry_run: bool = False) -> bool:
        """Execute the database migration."""
        logger.info(f"Executing migration (dry_run={dry_run})...")

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Start transaction
                    if not dry_run:
                        cursor.execute("BEGIN")
                        self.migration_started = True

                    # Read and execute schema
                    with open(self.schema_file, "r") as f:
                        schema_sql = f.read()

                    # Split SQL into individual statements
                    statements = [stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()]

                    for i, statement in enumerate(statements):
                        if not statement or statement.startswith("--"):
                            continue

                        try:
                            logger.debug(f"Executing statement {i+1}/{len(statements)}")
                            cursor.execute(statement)

                            if not dry_run:
                                self.migration_log.append(
                                    {
                                        "timestamp": datetime.now().isoformat(),
                                        "action": "statement_executed",
                                        "statement_index": i,
                                        "statement_preview": (
                                            statement[:100] + "..." if len(statement) > 100 else statement
                                        ),
                                    }
                                )

                        except Exception as e:
                            logger.error(f"Statement {i+1} failed: {e}")
                            logger.error(f"Statement: {statement}")
                            if not dry_run:
                                cursor.execute("ROLLBACK")
                            return False

                    # Commit transaction
                    if not dry_run:
                        cursor.execute("COMMIT")
                        logger.info("Migration executed successfully")
                    else:
                        logger.info("Dry run completed successfully")

                    return True

        except Exception as e:
            logger.error(f"Migration execution failed: {e}")
            if self.migration_started:
                try:
                    with self.db_manager.get_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute("ROLLBACK")
                except Exception:
                    pass
            return False

    def validate_migration(self) -> bool:
        """Validate that the migration was successful."""
        logger.info("Validating migration results...")

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Check that all tables were created
                    expected_tables = [
                        "conversation_sessions",
                        "conversation_messages",
                        "conversation_context",
                        "user_preferences",
                        "memory_retrieval_cache",
                        "session_relationships",
                        "memory_performance_metrics",
                    ]

                    for table_name in expected_tables:
                        cursor.execute(
                            """
                            SELECT table_name
                            FROM information_schema.tables
                            WHERE table_name = %s
                        """,
                            (table_name,),
                        )
                        if not cursor.fetchone():
                            logger.error(f"Table {table_name} was not created")
                            return False

                    # Check that all indexes were created
                    expected_indexes = [
                        "idx_conversation_sessions_user_id",
                        "idx_conversation_messages_session_id",
                        "idx_user_preferences_user_id",
                    ]

                    for index_name in expected_indexes:
                        cursor.execute(
                            """
                            SELECT indexname
                            FROM pg_indexes
                            WHERE indexname = %s
                        """,
                            (index_name,),
                        )
                        if not cursor.fetchone():
                            logger.error(f"Index {index_name} was not created")
                            return False

                    # Check that default system preferences were inserted
                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM user_preferences
                        WHERE user_id = 'system'
                    """
                    )
                    system_pref_count = cursor.fetchone()[0]
                    if system_pref_count < 4:  # Should have at least 4 default preferences
                        logger.error(f"Expected at least 4 system preferences, found {system_pref_count}")
                        return False

                    # Check that views were created
                    expected_views = ["session_summary", "user_preference_summary"]
                    for view_name in expected_views:
                        cursor.execute(
                            """
                            SELECT table_name
                            FROM information_schema.views
                            WHERE table_name = %s
                        """,
                            (view_name,),
                        )
                        if not cursor.fetchone():
                            logger.error(f"View {view_name} was not created")
                            return False

                    logger.info("Migration validation passed")
                    return True

        except Exception as e:
            logger.error(f"Migration validation failed: {e}")
            return False

    def rollback_migration(self) -> bool:
        """Rollback the migration if needed."""
        logger.info("Rolling back migration...")

        try:
            if not self.backup_created:
                logger.error("No backup available for rollback")
                return False

            # Restore from backup
            restore_command = f"""
            psql -h {self.db_config.get('host', 'localhost')} \
                 -U {self.db_config.get('user', 'postgres')} \
                 -d {self.db_config.get('database', 'dspy_rag')} \
                 -f {self.backup_file}
            """

            if "password" in self.db_config:
                os.environ["PGPASSWORD"] = self.db_config["password"]

            result = os.system(restore_command)

            if result == 0:
                logger.info("Migration rollback completed successfully")
                self.migration_log.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "action": "rollback_completed",
                        "backup_file": str(self.backup_file),
                    }
                )
                return True
            else:
                logger.error("Migration rollback failed")
                return False

        except Exception as e:
            logger.error(f"Migration rollback failed: {e}")
            return False

    def generate_migration_report(self) -> Dict[str, Any]:
        """Generate a comprehensive migration report."""
        report = {
            "migration_id": self.migration_id,
            "timestamp": datetime.now().isoformat(),
            "backup_created": self.backup_created,
            "migration_started": self.migration_started,
            "backup_file": str(self.backup_file) if self.backup_created else None,
            "schema_file": str(self.schema_file),
            "migration_log": self.migration_log,
            "status": "completed" if self.migration_started else "failed",
        }

        # Save report to file
        report_file = project_root / "config" / "database" / f"migration_report_{self.migration_id}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Migration report saved to: {report_file}")
        return report

    def run_migration(self, dry_run: bool = False, skip_backup: bool = False) -> bool:
        """Run the complete migration process."""
        logger.info(f"Starting LTST Memory System migration (dry_run={dry_run})")

        try:
            # Step 1: Validate prerequisites
            if not self.validate_prerequisites():
                return False

            # Step 2: Validate schema SQL
            if not self.validate_schema_sql():
                return False

            # Step 3: Create backup (unless skipped)
            if not skip_backup and not dry_run:
                if not self.create_backup():
                    logger.warning("Backup creation failed, but continuing with migration")

            # Step 4: Execute migration
            if not self.execute_migration(dry_run):
                return False

            # Step 5: Validate migration (only for real migrations)
            if not dry_run:
                if not self.validate_migration():
                    logger.error("Migration validation failed, attempting rollback...")
                    self.rollback_migration()
                    return False

            # Step 6: Generate report
            _ = self.generate_migration_report()

            if dry_run:
                logger.info("Dry run completed successfully")
            else:
                logger.info("Migration completed successfully")
                logger.info(f"Migration ID: {self.migration_id}")
                logger.info(f"Backup file: {self.backup_file if self.backup_created else 'None'}")

            return True

        except Exception as e:
            logger.error(f"Migration process failed: {e}")
            if self.migration_started and not dry_run:
                self.rollback_migration()
            return False


def main():
    """Main entry point for the migration script."""
    import argparse

    parser = argparse.ArgumentParser(description="LTST Memory System Database Migration")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making changes")
    parser.add_argument("--skip-backup", action="store_true", help="Skip backup creation")
    parser.add_argument("--rollback", action="store_true", help="Rollback the last migration")
    parser.add_argument("--validate-only", action="store_true", help="Only validate prerequisites and schema")
    parser.add_argument("--config", type=str, help="Database configuration file")

    args = parser.parse_args()

    # Load database configuration
    db_config = {}
    if args.config:
        with open(args.config, "r") as f:
            db_config = json.load(f)

    # Create migration instance
    migration = LTSTMemoryMigration(db_config)

    if args.rollback:
        success = migration.rollback_migration()
        sys.exit(0 if success else 1)

    elif args.validate_only:
        success = migration.validate_prerequisites() and migration.validate_schema_sql()
        sys.exit(0 if success else 1)

    else:
        success = migration.run_migration(dry_run=args.dry_run, skip_backup=args.skip_backup)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
