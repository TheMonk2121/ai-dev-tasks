#!/usr/bin/env python3
# type: ignore
"""
LTST Memory System Database Migration Script (Fixed Version)

This script safely migrates the database to include the LTST memory system schema
with rollback capability, data validation, and audit trail.

Note: Type ignore is used because RealDictCursor returns dictionary-like objects
that the type checker doesn't properly recognize, and database connection objects
are properly handled with null checks at runtime.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor


class LTSTMigrationManager:
    """Manages LTST memory system database migration."""

    def __init__(self, database_url: Optional[str] = None, dry_run: bool = False):
        """Initialize migration manager."""
        self.database_url = database_url or os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")
        self.dry_run = dry_run
        self.connection: Optional[connection] = None
        self.cursor: Optional[cursor] = None
        self.migration_log: List[Dict[str, Any]] = []
        self.rollback_queries: List[str] = []

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("ltst_migration.log"), logging.StreamHandler(sys.stdout)],
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

    def disconnect(self) -> None:
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None
        self.logger.info("Database connection closed")

    def log_migration_step(
        self, step: str, query: Optional[str] = None, success: bool = True, error: Optional[str] = None
    ) -> None:
        """Log migration step for audit trail."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "query": query,
            "success": success,
            "error": error,
            "dry_run": self.dry_run,
        }
        self.migration_log.append(log_entry)

        if success:
            self.logger.info(f"✅ {step}")
        else:
            self.logger.error(f"❌ {step}: {error}")

    def _ensure_cursor(self) -> bool:
        """Ensure cursor is available and connected."""
        if not self.cursor or not self.connection:
            self.logger.error("No database cursor available")
            return False
        if self.connection.closed:
            self.logger.error("Database connection is closed")
            return False
        return True

    def check_prerequisites(self) -> Dict[str, Any]:
        """Check migration prerequisites."""
        self.logger.info("Checking migration prerequisites...")

        prerequisites = {
            "pgvector_extension": False,
            "existing_tables": [],
            "database_version": None,
            "user_permissions": False,
        }

        try:
            if not self._ensure_cursor():
                self.log_migration_step(
                    "Prerequisites check failed", success=False, error="No database cursor available"
                )
                return prerequisites

            # Check pgvector extension
            self.cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
            vector_ext = self.cursor.fetchone()
            prerequisites["pgvector_extension"] = vector_ext is not None

            # Check existing tables
            self.cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('conversation_memory', 'document_chunks', 'documents')
            """
            )
            fetchall_result = self.cursor.fetchall()
            existing_tables = [row["table_name"] for row in fetchall_result] if fetchall_result else []
            prerequisites["existing_tables"] = existing_tables

            # Check database version
            self.cursor.execute("SELECT version();")
            version_result = self.cursor.fetchone()
            prerequisites["database_version"] = version_result["version"] if version_result else None

            # Check user permissions
            self.cursor.execute(
                """
                SELECT has_table_privilege('conversation_memory', 'INSERT') as can_insert,
                       has_schema_privilege('public', 'CREATE') as can_create
            """
            )
            permissions = self.cursor.fetchone()
            prerequisites["user_permissions"] = (
                permissions["can_insert"] and permissions["can_create"] if permissions else False
            )

            self.log_migration_step("Prerequisites check completed", success=True)
            return prerequisites

        except Exception as e:
            self.log_migration_step("Prerequisites check failed", success=False, error=str(e))
            return prerequisites

    def create_backup(self) -> bool:
        """Create backup of existing data."""
        if self.dry_run:
            self.logger.info("DRY RUN: Would create backup")
            return True

        try:
            if not self._ensure_cursor():
                return False

            self.logger.info("Creating backup of existing data...")

            # Backup existing conversation_memory data
            self.cursor.execute("SELECT COUNT(*) FROM conversation_memory;")
            count_result = self.cursor.fetchone()
            row_count = count_result["count"] if count_result else 0

            if row_count > 0:
                backup_table = f"conversation_memory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM conversation_memory;")
                if self.connection:
                    self.connection.commit()

                # Add rollback query
                self.rollback_queries.append(f"DROP TABLE IF EXISTS {backup_table};")

                self.log_migration_step(f"Backup created: {backup_table} with {row_count} rows")
            else:
                self.log_migration_step("No existing data to backup")

            return True

        except Exception as e:
            self.log_migration_step("Backup creation failed", success=False, error=str(e))
            return False

    def execute_schema_migration(self) -> bool:
        """Execute the LTST schema migration."""
        try:
            if not self._ensure_cursor():
                return False

            self.logger.info("Executing LTST schema migration...")

            # Read and execute schema file
            schema_file = "dspy-rag-system/config/database/ltst_memory_schema.sql"

            if not os.path.exists(schema_file):
                raise FileNotFoundError(f"Schema file not found: {schema_file}")

            with open(schema_file, "r") as f:
                sql_content = f.read()

            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

            # Execute statements in batches to handle dependencies
            current_batch = []
            batch_number = 0

            for i, statement in enumerate(statements):
                if statement and not statement.startswith("--"):
                    current_batch.append((i, statement))

                    # Execute batch when we hit a commit point or at the end
                    if (
                        statement.strip().upper().startswith("CREATE TABLE") and "conversation_messages" in statement
                    ) or i == len(statements) - 1:

                        batch_number += 1
                        self.logger.info(f"Executing batch {batch_number} with {len(current_batch)} statements")

                        for batch_i, (stmt_idx, stmt) in enumerate(current_batch):
                            try:
                                if not self.dry_run:
                                    self.cursor.execute(stmt)

                                # Log successful statement
                                step_name = f"Schema statement {stmt_idx+1}/{len(statements)} (batch {batch_number})"
                                self.log_migration_step(
                                    step_name, query=stmt[:100] + "..." if len(stmt) > 100 else stmt
                                )

                            except Exception as e:
                                self.log_migration_step(
                                    f"Schema statement {stmt_idx+1} failed",
                                    query=stmt[:100] + "..." if len(stmt) > 100 else stmt,
                                    success=False,
                                    error=str(e),
                                )
                                raise

                        # Commit after each batch
                        if not self.dry_run and self.connection:
                            self.connection.commit()

                        current_batch = []

            self.log_migration_step("Schema migration completed successfully")
            return True

        except Exception as e:
            self.log_migration_step("Schema migration failed", success=False, error=str(e))
            if not self.dry_run and self.connection:
                self.connection.rollback()
            return False

    def validate_migration(self) -> Dict[str, Any]:
        """Validate the migration results."""
        self.logger.info("Validating migration results...")

        validation_results = {
            "tables_created": [],
            "indexes_created": [],
            "functions_created": [],
            "views_created": [],
            "data_integrity": True,
            "performance_checks": {},
        }

        try:
            if not self._ensure_cursor():
                self.log_migration_step(
                    "Migration validation failed", success=False, error="No database cursor available"
                )
                validation_results["data_integrity"] = False
                return validation_results

            # Check tables were created
            expected_tables = [
                "conversation_sessions",
                "conversation_messages",
                "conversation_context",
                "user_preferences",
                "memory_retrieval_cache",
                "session_relationships",
                "memory_performance_metrics",
            ]

            for table in expected_tables:
                self.cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = %s
                    );
                """,
                    (table,),
                )
                result = self.cursor.fetchone()
                exists = result["exists"] if result else False
                if exists:
                    validation_results["tables_created"].append(table)

            # Check indexes were created
            expected_indexes = [
                "idx_conversation_sessions_user_id",
                "idx_conversation_messages_session_id",
                "idx_conversation_context_session_id",
                "idx_user_preferences_user_id",
            ]

            for index in expected_indexes:
                self.cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM pg_indexes
                        WHERE indexname = %s
                    );
                """,
                    (index,),
                )
                result = self.cursor.fetchone()
                exists = result["exists"] if result else False
                if exists:
                    validation_results["indexes_created"].append(index)

            # Check functions were created
            expected_functions = ["update_session_length", "clean_expired_cache", "clean_expired_context"]

            for func in expected_functions:
                self.cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM pg_proc
                        WHERE proname = %s
                    );
                """,
                    (func,),
                )
                result = self.cursor.fetchone()
                exists = result["exists"] if result else False
                if exists:
                    validation_results["functions_created"].append(func)

            # Check views were created
            expected_views = ["session_summary", "user_preference_summary"]

            for view in expected_views:
                self.cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.views
                        WHERE table_schema = 'public'
                        AND table_name = %s
                    );
                """,
                    (view,),
                )
                result = self.cursor.fetchone()
                exists = result["exists"] if result else False
                if exists:
                    validation_results["views_created"].append(view)

            # Performance checks
            for table in ["conversation_sessions", "conversation_messages"]:
                start_time = datetime.now()
                self.cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count_result = self.cursor.fetchone()
                query_time = (datetime.now() - start_time).total_seconds() * 1000

                validation_results["performance_checks"][table] = {
                    "row_count": count_result["count"] if count_result else 0,
                    "query_time_ms": query_time,
                    "acceptable": query_time < 1000,  # Should complete in under 1 second
                }

            # Data integrity check
            validation_results["data_integrity"] = (
                len(validation_results["tables_created"]) == len(expected_tables)
                and len(validation_results["indexes_created"]) >= len(expected_indexes)
                and len(validation_results["functions_created"]) == len(expected_functions)
                and len(validation_results["views_created"]) == len(expected_views)
            )

            self.log_migration_step("Migration validation completed", success=validation_results["data_integrity"])
            return validation_results

        except Exception as e:
            self.log_migration_step("Migration validation failed", success=False, error=str(e))
            validation_results["data_integrity"] = False
            return validation_results

    def rollback_migration(self) -> bool:
        """Rollback the migration if needed."""
        if self.dry_run:
            self.logger.info("DRY RUN: Would rollback migration")
            return True

        try:
            if not self._ensure_cursor():
                return False

            self.logger.info("Rolling back migration...")

            # Drop new tables in reverse order
            tables_to_drop = [
                "memory_performance_metrics",
                "session_relationships",
                "memory_retrieval_cache",
                "user_preferences",
                "conversation_context",
                "conversation_messages",
                "conversation_sessions",
            ]

            for table in tables_to_drop:
                try:
                    self.cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                    self.log_migration_step(f"Dropped table: {table}")
                except Exception as e:
                    self.log_migration_step(f"Failed to drop table {table}", success=False, error=str(e))

            # Execute rollback queries
            for rollback_query in self.rollback_queries:
                try:
                    self.cursor.execute(rollback_query)
                    self.log_migration_step(f"Executed rollback: {rollback_query}")
                except Exception as e:
                    self.log_migration_step("Failed rollback query", success=False, error=str(e))

            if self.connection:
                self.connection.commit()
            self.log_migration_step("Migration rollback completed")
            return True

        except Exception as e:
            self.log_migration_step("Migration rollback failed", success=False, error=str(e))
            if self.connection:
                self.connection.rollback()
            return False

    def save_migration_log(self, filename: Optional[str] = None) -> None:
        """Save migration log to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ltst_migration_log_{timestamp}.json"

        try:
            with open(filename, "w") as f:
                json.dump(self.migration_log, f, indent=2)
            self.logger.info(f"Migration log saved to: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save migration log: {e}")

    def run_migration(self) -> bool:
        """Run the complete migration process."""
        self.logger.info("Starting LTST Memory System migration...")

        try:
            # Step 1: Check prerequisites
            prerequisites = self.check_prerequisites()
            if not prerequisites["pgvector_extension"]:
                self.logger.error("pgvector extension not found. Please install it first.")
                return False

            # Step 2: Create backup
            if not self.create_backup():
                self.logger.error("Backup creation failed. Aborting migration.")
                return False

            # Step 3: Execute schema migration
            if not self.execute_schema_migration():
                self.logger.error("Schema migration failed. Rolling back...")
                self.rollback_migration()
                return False

            # Step 4: Validate migration
            validation_results = self.validate_migration()
            if not validation_results["data_integrity"]:
                self.logger.error("Migration validation failed. Rolling back...")
                self.rollback_migration()
                return False

            # Step 5: Save migration log
            self.save_migration_log()

            self.logger.info("🎉 LTST Memory System migration completed successfully!")
            return True

        except Exception as e:
            self.logger.error(f"Migration failed with unexpected error: {e}")
            self.rollback_migration()
            return False


def main():
    """Main migration script entry point."""
    parser = argparse.ArgumentParser(description="LTST Memory System Database Migration")
    parser.add_argument("--database-url", help="Database connection URL")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without making changes")
    parser.add_argument("--rollback", action="store_true", help="Rollback previous migration")
    parser.add_argument("--validate-only", action="store_true", help="Only validate existing schema")

    args = parser.parse_args()

    migration_manager = LTSTMigrationManager(database_url=args.database_url, dry_run=args.dry_run)

    if not migration_manager.connect():
        sys.exit(1)

    try:
        if args.rollback:
            success = migration_manager.rollback_migration()
        elif args.validate_only:
            validation_results = migration_manager.validate_migration()
            print(json.dumps(validation_results, indent=2))
            success = validation_results["data_integrity"]
        else:
            success = migration_manager.run_migration()

        if success:
            sys.exit(0)
        else:
            sys.exit(1)

    finally:
        migration_manager.disconnect()


if __name__ == "__main__":
    main()
