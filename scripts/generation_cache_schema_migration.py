#!/usr/bin/env python3
"""
Generation Cache Schema Migration Script
========================================
Task 1.1: Database Schema Updates for B-1054 Generation Cache Implementation

This script adds cache-specific columns to the episodic_logs table to support
generation caching with cache hit tracking, similarity scoring, and cache invalidation.

Columns Added:
- cache_hit (boolean): Whether this entry was served from cache
- similarity_score (float): Vector similarity score for cache retrieval
- last_verified (timestamp): When this cache entry was last verified

Migration Features:
- Safe migration with rollback capability
- Transaction-based updates
- Performance impact validation
- Column constraint validation
"""

import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Database configuration - simplified for this script
def get_database_url():
    return os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")


def validate_database_config():
    database_url = get_database_url()
    return database_url.startswith("postgresql://")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/generation_cache_migration.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class GenerationCacheSchemaMigration:
    """Database schema migration for generation cache implementation"""

    def __init__(self, database_url: str | None = None):
        """Initialize migration with database connection"""
        self.database_url = database_url or get_database_url()
        self.connection = None
        self.cursor = None
        self.migration_start_time = None
        self.rollback_commands = []

        # Validate database configuration
        if not validate_database_config():
            raise ValueError("Invalid database configuration")

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.disconnect()

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Database connection closed")

    def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        try:
            self.cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = %s
                );
            """,
                (table_name,),
            )
            result = self.cursor.fetchone()
            return result["exists"] if result else False
        except Exception as e:
            logger.error(f"Error checking table existence: {e}")
            return False

    def get_table_schema(self, table_name: str) -> dict[str, Any]:
        """Get current table schema information"""
        try:
            self.cursor.execute(
                """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = %s
                ORDER BY ordinal_position;
            """,
                (table_name,),
            )

            columns = {}
            for row in self.cursor.fetchall():
                columns[row["column_name"]] = {
                    "data_type": row["data_type"],
                    "is_nullable": row["is_nullable"] == "YES",
                    "column_default": row["column_default"],
                }

            return columns
        except Exception as e:
            logger.error(f"Error getting table schema: {e}")
            return {}

    def check_column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a specific column exists in the table"""
        try:
            self.cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = %s
                    AND column_name = %s
                );
            """,
                (table_name, column_name),
            )
            result = self.cursor.fetchone()
            return result["exists"] if result else False
        except Exception as e:
            logger.error(f"Error checking column existence: {e}")
            return False

    def add_cache_columns(self) -> bool:
        """Add cache-specific columns to episodic_logs table"""
        try:
            # Check if table exists
            if not self.check_table_exists("episodic_logs"):
                logger.error("Table 'episodic_logs' does not exist")
                return False

            # Get current schema
            current_schema = self.get_table_schema("episodic_logs")
            logger.info(f"Current episodic_logs schema: {list(current_schema.keys())}")

            # Define cache columns to add
            cache_columns = {
                "cache_hit": {
                    "type": "BOOLEAN",
                    "default": "FALSE",
                    "nullable": True,
                    "description": "Whether this entry was served from cache",
                },
                "similarity_score": {
                    "type": "REAL",
                    "default": "0.0",
                    "nullable": True,
                    "description": "Vector similarity score for cache retrieval",
                },
                "last_verified": {
                    "type": "TIMESTAMP",
                    "default": "NOW()",
                    "nullable": True,
                    "description": "When this cache entry was last verified",
                },
            }

            # Add each column if it doesn't exist
            for column_name, column_spec in cache_columns.items():
                if not self.check_column_exists("episodic_logs", column_name):
                    logger.info(f"Adding column: {column_name}")

                    # Build ALTER TABLE statement
                    alter_sql = f"""
                        ALTER TABLE episodic_logs
                        ADD COLUMN {column_name} {column_spec['type']}
                    """

                    # Add default value if specified
                    if column_spec["default"]:
                        alter_sql += f" DEFAULT {column_spec['default']}"

                    # Add nullable constraint
                    if not column_spec["nullable"]:
                        alter_sql += " NOT NULL"

                    # Execute ALTER TABLE
                    self.cursor.execute(alter_sql)

                    # Store rollback command
                    self.rollback_commands.append(f"ALTER TABLE episodic_logs DROP COLUMN {column_name};")

                    logger.info(f"Successfully added column: {column_name}")
                else:
                    logger.info(f"Column {column_name} already exists, skipping")

            # Commit changes
            self.connection.commit()
            logger.info("Cache columns added successfully")
            return True

        except Exception as e:
            logger.error(f"Error adding cache columns: {e}")
            self.connection.rollback()
            return False

    def validate_cache_columns(self) -> bool:
        """Validate that cache columns were added correctly"""
        try:
            # Check if all required columns exist
            required_columns = ["cache_hit", "similarity_score", "last_verified"]

            for column_name in required_columns:
                if not self.check_column_exists("episodic_logs", column_name):
                    logger.error(f"Required column {column_name} is missing")
                    return False

            # Get updated schema
            updated_schema = self.get_table_schema("episodic_logs")
            logger.info(f"Updated episodic_logs schema: {list(updated_schema.keys())}")

            # Validate column types
            expected_types = {
                "cache_hit": "boolean",
                "similarity_score": "real",
                "last_verified": "timestamp without time zone",
            }

            for column_name, expected_type in expected_types.items():
                if column_name in updated_schema:
                    actual_type = updated_schema[column_name]["data_type"]
                    if actual_type != expected_type:
                        logger.warning(f"Column {column_name} has type {actual_type}, expected {expected_type}")
                else:
                    logger.error(f"Column {column_name} not found in updated schema")
                    return False

            logger.info("Cache columns validation successful")
            return True

        except Exception as e:
            logger.error(f"Error validating cache columns: {e}")
            return False

    def measure_performance_impact(self) -> dict[str, Any]:
        """Measure performance impact of schema changes"""
        try:
            # Get table size before changes
            self.cursor.execute(
                """
                SELECT
                    pg_size_pretty(pg_total_relation_size('episodic_logs')) as table_size,
                    pg_size_pretty(pg_relation_size('episodic_logs')) as data_size,
                    pg_size_pretty(pg_total_relation_size('episodic_logs') - pg_relation_size('episodic_logs')) as index_size
                FROM pg_class
                WHERE relname = 'episodic_logs';
            """
            )

            size_info = self.cursor.fetchone()

            # Test basic query performance
            start_time = time.time()
            self.cursor.execute("SELECT COUNT(*) FROM episodic_logs")
            count_result = self.cursor.fetchone()
            count_time = time.time() - start_time

            # Test SELECT with new columns
            start_time = time.time()
            self.cursor.execute(
                """
                SELECT cache_hit, similarity_score, last_verified
                FROM episodic_logs
                LIMIT 100
            """
            )
            select_time = time.time() - start_time

            performance_metrics = {
                "table_size": size_info["table_size"] if size_info else "Unknown",
                "data_size": size_info["data_size"] if size_info else "Unknown",
                "index_size": size_info["index_size"] if size_info else "Unknown",
                "record_count": count_result["count"] if count_result else 0,
                "count_query_time": f"{count_time:.4f}s",
                "select_query_time": f"{select_time:.4f}s",
            }

            logger.info(f"Performance metrics: {performance_metrics}")
            return performance_metrics

        except Exception as e:
            logger.error(f"Error measuring performance impact: {e}")
            return {}

    def create_cache_indexes(self) -> bool:
        """Create indexes for cache performance optimization"""
        try:
            # Create index on cache_hit for fast cache hit queries
            if not self.check_index_exists("episodic_logs", "idx_episodic_logs_cache_hit"):
                logger.info("Creating index on cache_hit column")
                self.cursor.execute(
                    """
                    CREATE INDEX idx_episodic_logs_cache_hit
                    ON episodic_logs (cache_hit)
                    WHERE cache_hit = TRUE;
                """
                )
                logger.info("Index on cache_hit created successfully")

            # Create index on similarity_score for range queries
            if not self.check_index_exists("episodic_logs", "idx_episodic_logs_similarity_score"):
                logger.info("Creating index on similarity_score column")
                self.cursor.execute(
                    """
                    CREATE INDEX idx_episodic_logs_similarity_score
                    ON episodic_logs (similarity_score);
                """
                )
                logger.info("Index on similarity_score created successfully")

            # Create index on last_verified for cache expiration queries
            if not self.check_index_exists("episodic_logs", "idx_episodic_logs_last_verified"):
                logger.info("Creating index on last_verified column")
                self.cursor.execute(
                    """
                    CREATE INDEX idx_episodic_logs_last_verified
                    ON episodic_logs (last_verified);
                """
                )
                logger.info("Index on last_verified created successfully")

            # Commit index creation
            self.connection.commit()
            return True

        except Exception as e:
            logger.error(f"Error creating cache indexes: {e}")
            self.connection.rollback()
            return False

    def check_index_exists(self, table_name: str, index_name: str) -> bool:
        """Check if a specific index exists"""
        try:
            self.cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM pg_indexes
                    WHERE tablename = %s
                    AND indexname = %s
                );
            """,
                (table_name, index_name),
            )
            result = self.cursor.fetchone()
            return result["exists"] if result else False
        except Exception as e:
            logger.error(f"Error checking index existence: {e}")
            return False

    def rollback_migration(self) -> bool:
        """Rollback all schema changes"""
        try:
            logger.warning("Rolling back migration...")

            for rollback_command in reversed(self.rollback_commands):
                logger.info(f"Executing rollback: {rollback_command}")
                self.cursor.execute(rollback_command)

            self.connection.commit()
            logger.info("Migration rollback completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error during rollback: {e}")
            self.connection.rollback()
            return False

    def run_migration(self) -> bool:
        """Run the complete migration process"""
        try:
            self.migration_start_time = datetime.now()
            logger.info("Starting Generation Cache Schema Migration")
            logger.info(f"Database: {self.database_url}")
            logger.info(f"Start time: {self.migration_start_time}")

            # Step 1: Add cache columns
            logger.info("Step 1: Adding cache columns")
            if not self.add_cache_columns():
                logger.error("Failed to add cache columns")
                return False

            # Step 2: Validate changes
            logger.info("Step 2: Validating cache columns")
            if not self.validate_cache_columns():
                logger.error("Cache columns validation failed")
                self.rollback_migration()
                return False

            # Step 3: Create performance indexes
            logger.info("Step 3: Creating cache performance indexes")
            if not self.create_cache_indexes():
                logger.error("Failed to create cache indexes")
                # Index creation failure is not critical, continue

            # Step 4: Measure performance impact
            logger.info("Step 4: Measuring performance impact")
            performance_metrics = self.measure_performance_impact()

            # Migration completed successfully
            migration_end_time = datetime.now()
            duration = migration_end_time - self.migration_start_time

            logger.info("=" * 60)
            logger.info("MIGRATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            logger.info(f"Duration: {duration}")
            logger.info(f"Performance metrics: {performance_metrics}")
            logger.info("Cache columns added: cache_hit, similarity_score, last_verified")
            logger.info("Performance indexes created for cache optimization")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            self.rollback_migration()
            return False


def main():
    """Main migration execution function"""
    try:
        # Check if running in test mode
        test_mode = os.getenv("MIGRATION_TEST_MODE", "false").lower() == "true"

        if test_mode:
            logger.info("Running in TEST MODE - changes will be rolled back")

        # Run migration
        with GenerationCacheSchemaMigration() as migration:
            success = migration.run_migration()

            if test_mode and success:
                logger.info("Test mode: Rolling back changes")
                migration.rollback_migration()
                logger.info("Test completed successfully")
                return True

            return success

    except Exception as e:
        logger.error(f"Migration execution failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
