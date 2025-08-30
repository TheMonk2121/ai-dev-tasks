#!/usr/bin/env python3
# type: ignore
"""
Decision Intelligence Schema Migration Script

This script extends the existing LTST memory system schema with decision intelligence
features including decision tracking, supersedence logic, and entity relationships.

Note: Type ignore is used because RealDictCursor returns dictionary-like objects
that the type checker doesn't properly recognize, and database connection objects
are properly handled with null checks at runtime.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.conversation_storage import ConversationStorage


class DecisionIntelligenceMigration:
    """Manages the migration to add decision intelligence features."""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize migration manager."""
        self.database_url = database_url
        self.storage = ConversationStorage(database_url)
        self.logger = logging.getLogger(__name__)

        # Migration configuration
        self.migration_version = "2024.12.001"
        self.migration_name = "decision_intelligence_schema_extension"

        # New columns to add
        self.new_columns = [
            "decision_head TEXT",
            "decision_status TEXT CHECK (decision_status IN ('open', 'closed', 'superseded')) DEFAULT 'open'",
            "superseded_by TEXT",
            "entities JSONB",
            "files JSONB",
        ]

        # New indexes to create
        self.new_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_conversation_context_decision_head ON conversation_context USING GIN (to_tsvector('english', decision_head))",
            "CREATE INDEX IF NOT EXISTS idx_conversation_context_decision_status ON conversation_context (decision_status, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_conversation_context_entities ON conversation_context USING GIN (entities jsonb_path_ops)",
            "CREATE INDEX IF NOT EXISTS idx_conversation_context_superseded_by ON conversation_context (superseded_by) WHERE superseded_by IS NOT NULL",
        ]

    def _ensure_cursor(self):
        """Ensure cursor is available."""
        if not self.storage.cursor:
            if not self.storage.connect():
                raise Exception("Failed to connect to database")

    def check_prerequisites(self) -> bool:
        """Check if migration prerequisites are met."""
        try:
            self._ensure_cursor()

            # Check if conversation_context table exists
            self.storage.cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'conversation_context'
                )
            """
            )

            result = self.storage.cursor.fetchone()
            table_exists = result[0] if isinstance(result, (list, tuple)) else result.get("exists") if result else False
            if not table_exists:
                self.logger.error("Prerequisites check failed: conversation_context table does not exist")
                return False

            # Check if we can alter the table
            self.storage.cursor.execute(
                """
                SELECT has_table_privilege(current_user, 'conversation_context', 'UPDATE')
            """
            )

            result = self.storage.cursor.fetchone()
            can_alter = (
                result[0]
                if isinstance(result, (list, tuple))
                else result.get("has_table_privilege") if result else False
            )
            if not can_alter:
                self.logger.error(
                    "Prerequisites check failed: insufficient privileges to alter conversation_context table"
                )
                return False

            self.logger.info("Prerequisites check passed")
            return True

        except Exception as e:
            self.logger.error(f"Prerequisites check failed: {e}")
            return False

    def backup_existing_data(self) -> bool:
        """Create backup of existing conversation_context data."""
        try:
            self._ensure_cursor()

            # Create backup table
            backup_table = f"conversation_context_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            self.storage.cursor.execute(
                f"""
                CREATE TABLE {backup_table} AS
                SELECT * FROM conversation_context
            """
            )

            # Get row count
            self.storage.cursor.execute(f"SELECT COUNT(*) FROM {backup_table}")
            result = self.storage.cursor.fetchone()
            row_count = result[0] if isinstance(result, (list, tuple)) else result.get("count") if result else 0

            self.storage.connection.commit()
            self.logger.info(f"Backup created: {backup_table} with {row_count} rows")
            return True

        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            if self.storage.connection:
                self.storage.connection.rollback()
            return False

    def add_decision_columns(self) -> bool:
        """Add new decision intelligence columns to conversation_context table."""
        try:
            self._ensure_cursor()

            for column_def in self.new_columns:
                column_name = column_def.split()[0]

                # Check if column already exists
                self.storage.cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns
                        WHERE table_name = 'conversation_context'
                        AND column_name = %s
                    )
                """,
                    (column_name,),
                )

                result = self.storage.cursor.fetchone()
                column_exists = (
                    result[0] if isinstance(result, (list, tuple)) else result.get("exists") if result else False
                )
                if not column_exists:
                    self.storage.cursor.execute(
                        f"""
                        ALTER TABLE conversation_context
                        ADD COLUMN {column_def}
                    """
                    )
                    self.logger.info(f"Added column: {column_name}")
                else:
                    self.logger.info(f"Column already exists: {column_name}")

            self.storage.connection.commit()
            self.logger.info("All decision intelligence columns added successfully")
            return True

        except Exception as e:
            self.logger.error(f"Column addition failed: {e}")
            if self.storage.connection:
                self.storage.connection.rollback()
            return False

    def create_decision_indexes(self) -> bool:
        """Create new indexes for decision intelligence features."""
        try:
            self._ensure_cursor()

            for index_sql in self.new_indexes:
                self.storage.cursor.execute(index_sql)
                self.logger.info(f"Created index: {index_sql.split('idx_')[1].split()[0]}")

            self.storage.connection.commit()
            self.logger.info("All decision intelligence indexes created successfully")
            return True

        except Exception as e:
            self.logger.error(f"Index creation failed: {e}")
            if self.storage.connection:
                self.storage.connection.rollback()
            return False

    def update_existing_data(self) -> bool:
        """Update existing data to set default values for new columns."""
        try:
            self._ensure_cursor()

            # Update existing rows to have default decision_status
            self.storage.cursor.execute(
                """
                UPDATE conversation_context
                SET decision_status = 'open'
                WHERE decision_status IS NULL
            """
            )

            updated_rows = self.storage.cursor.rowcount
            self.logger.info(f"Updated {updated_rows} existing rows with default decision_status")

            # Initialize entities and files as empty JSONB arrays for existing rows
            self.storage.cursor.execute(
                """
                UPDATE conversation_context
                SET entities = '[]'::jsonb, files = '[]'::jsonb
                WHERE entities IS NULL OR files IS NULL
            """
            )

            updated_rows = self.storage.cursor.rowcount
            self.logger.info(f"Updated {updated_rows} existing rows with empty JSONB arrays")

            self.storage.connection.commit()
            return True

        except Exception as e:
            self.logger.error(f"Data update failed: {e}")
            if self.storage.connection:
                self.storage.connection.rollback()
            return False

    def validate_migration(self) -> bool:
        """Validate that the migration was successful."""
        try:
            self._ensure_cursor()

            # Check all new columns exist
            expected_columns = ["decision_head", "decision_status", "superseded_by", "entities", "files"]

            for column in expected_columns:
                self.storage.cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns
                        WHERE table_name = 'conversation_context'
                        AND column_name = %s
                    )
                """,
                    (column,),
                )

                result = self.storage.cursor.fetchone()
                column_exists = (
                    result[0] if isinstance(result, (list, tuple)) else result.get("exists") if result else False
                )
                if not column_exists:
                    self.logger.error(f"Validation failed: column {column} does not exist")
                    return False

            # Check indexes exist
            expected_indexes = [
                "idx_conversation_context_decision_head",
                "idx_conversation_context_decision_status",
                "idx_conversation_context_entities",
                "idx_conversation_context_superseded_by",
            ]

            for index in expected_indexes:
                self.storage.cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM pg_indexes
                        WHERE indexname = %s
                    )
                """,
                    (index,),
                )

                result = self.storage.cursor.fetchone()
                index_exists = (
                    result[0] if isinstance(result, (list, tuple)) else result.get("exists") if result else False
                )
                if not index_exists:
                    self.logger.error(f"Validation failed: index {index} does not exist")
                    return False

            # Create test session first
            self.storage.cursor.execute(
                """
                INSERT INTO conversation_sessions (session_id, user_id, session_name, session_type, status)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (session_id) DO NOTHING
            """,
                ("migration_test_session", "migration_test_user", "Migration Test Session", "test", "active"),
            )

            # Test data insertion
            test_context = {
                "session_id": "migration_test_session",
                "context_type": "decision",
                "context_key": "migration_test",
                "context_value": "Test decision context",
                "relevance_score": 0.9,
                "decision_head": "test_decision",
                "decision_status": "open",
                "entities": ["test_entity"],
                "files": ["test_file.py"],
            }

            # Convert Python lists to JSON for JSONB fields
            import json

            test_context["entities"] = json.dumps(test_context["entities"])
            test_context["files"] = json.dumps(test_context["files"])

            success = self.storage.store_context(**test_context)
            if not success:
                self.logger.error("Validation failed: cannot insert test data")
                return False

            # Clean up test data
            self.storage.cursor.execute(
                """
                DELETE FROM conversation_context
                WHERE session_id = 'migration_test_session'
            """
            )
            self.storage.connection.commit()

            self.logger.info("Migration validation successful")
            return True

        except Exception as e:
            self.logger.error(f"Migration validation failed: {e}")
            return False

    def run_migration(self, dry_run: bool = False) -> bool:
        """Run the complete migration process."""
        start_time = datetime.now()
        self.logger.info(f"Starting decision intelligence migration (dry_run: {dry_run})")

        try:
            # Check prerequisites
            if not self.check_prerequisites():
                return False

            if dry_run:
                self.logger.info("DRY RUN: Prerequisites check passed")
                return True

            # Create backup
            if not self.backup_existing_data():
                return False

            # Add new columns
            if not self.add_decision_columns():
                return False

            # Create indexes
            if not self.create_decision_indexes():
                return False

            # Update existing data
            if not self.update_existing_data():
                return False

            # Validate migration
            if not self.validate_migration():
                return False

            migration_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Migration completed successfully in {migration_time:.2f} seconds")
            return True

        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            return False
        finally:
            if self.storage.connection:
                self.storage.disconnect()

    def rollback_migration(self) -> bool:
        """Rollback the migration by removing new columns and indexes."""
        try:
            self._ensure_cursor()

            # Drop new indexes
            index_names = [
                "idx_conversation_context_decision_head",
                "idx_conversation_context_decision_status",
                "idx_conversation_context_entities",
                "idx_conversation_context_superseded_by",
            ]

            for index in index_names:
                self.storage.cursor.execute(f"DROP INDEX IF EXISTS {index}")
                self.logger.info(f"Dropped index: {index}")

            # Drop new columns
            column_names = ["decision_head", "decision_status", "superseded_by", "entities", "files"]

            for column in column_names:
                self.storage.cursor.execute(f"ALTER TABLE conversation_context DROP COLUMN IF EXISTS {column}")
                self.logger.info(f"Dropped column: {column}")

            self.storage.connection.commit()
            self.logger.info("Rollback completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            if self.storage.connection:
                self.storage.connection.rollback()
            return False
        finally:
            if self.storage.connection:
                self.storage.disconnect()


def main():
    """Main migration execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Decision Intelligence Schema Migration")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without making changes")
    parser.add_argument("--rollback", action="store_true", help="Rollback the migration")
    parser.add_argument("--database-url", help="Database connection URL")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Run migration
    migration = DecisionIntelligenceMigration(args.database_url)

    if args.rollback:
        success = migration.rollback_migration()
    else:
        success = migration.run_migration(dry_run=args.dry_run)

    if success:
        print("✅ Migration completed successfully")
        sys.exit(0)
    else:
        print("❌ Migration failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
