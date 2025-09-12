from __future__ import annotations
import logging
import os
import sys
from pathlib import Path
from utils.database_resilience import execute_query
from utils.logger import setup_logger
    import argparse
#!/usr/bin/env python3
"""
Query Pattern Knowledge Graph Schema Migration Script

Migrates the database to support query pattern analysis and knowledge graph functionality.
Extends the existing LTST Memory System with advanced query pattern capabilities.
"""

# Add src to path for imports
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system", "src"))  # REMOVED: DSPy venv consolidated into main project

logger = setup_logger(__name__)

def migrate_query_pattern_schema(dry_run: bool = False) -> bool:
    """Migrate database schema for query pattern knowledge graph.

    Args:
        dry_run: If True, only show what would be executed without making changes

    Returns:
        True if migration was successful
    """
    try:
        logger.info("Starting query pattern schema migration")

        # Get schema file path
        schema_file = (
            Path(__file__).parent.parent
            / "dspy-rag-system"
            / "config"
            / "database"
            / "query_pattern_schema_extensions.sql"
        )

        if not schema_file.exists():
            logger.error(f"Schema file not found: {schema_file}")
            return False

        # Read schema
        with open(schema_file) as f:
            schema_sql = f.read()

        logger.info(f"Loaded schema from: {schema_file}")

        # Split into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()]

        logger.info(f"Found {len(statements)} SQL statements to execute")

        if dry_run:
            logger.info("DRY RUN MODE - Statements that would be executed:")
            for i, statement in enumerate(statements, 1):
                print(f"\n--- Statement {i} ---")
                print(statement)
            return True

        # Execute each statement
        success_count = 0
        error_count = 0

        for i, statement in enumerate(statements, 1):
            try:
                logger.info(f"Executing statement {i}/{len(statements)}")
                execute_query(statement)
                success_count += 1
                logger.debug(f"✅ Statement {i} executed successfully")

            except Exception as e:
                error_msg = str(e).lower()

                # Some errors are expected (like "already exists")
                if any(
                    expected in error_msg
                    for expected in [
                        "already exists",
                        "relation already exists",
                        "index already exists",
                        "extension already exists",
                    ]
                ):
                    logger.info(f"⚠️ Statement {i} - Object already exists (OK): {e}")
                    success_count += 1
                else:
                    logger.error(f"❌ Statement {i} failed: {e}")
                    error_count += 1

        # Summary
        logger.info(f"Migration completed: {success_count} successful, {error_count} errors")

        if error_count == 0:
            logger.info("✅ All statements executed successfully!")

            # Verify key tables exist
            if verify_schema_migration():
                logger.info("✅ Schema verification passed!")
                return True
            else:
                logger.error("❌ Schema verification failed!")
                return False
        else:
            logger.warning(f"⚠️ Migration completed with {error_count} errors")
            return False

    except Exception as e:
        logger.error(f"Error during schema migration: {e}")
        return False

def verify_schema_migration() -> bool:
    """Verify that the schema migration was successful.

    Returns:
        True if verification passed
    """
    try:
        logger.info("Verifying schema migration...")

        # Check that key tables exist
        required_tables = [
            "query_patterns",
            "query_relationships",
            "query_intentions",
            "query_clusters",
            "query_predictions",
        ]

        for table in required_tables:
            try:
                result = execute_query(f"SELECT COUNT(*) FROM {table}")
                count = result[0][0] if result else 0
                logger.info(f"✅ Table '{table}' exists with {count} rows")
            except Exception as e:
                logger.error(f"❌ Table '{table}' verification failed: {e}")
                return False

        # Check that key indexes exist
        index_check_query = """
            SELECT indexname
            FROM pg_indexes
            WHERE indexname LIKE 'idx_query_%'
            ORDER BY indexname
        """

        result = execute_query(index_check_query)
        if result:
            index_count = len(result)
            logger.info(f"✅ Found {index_count} query pattern indexes")

            # Log some key indexes
            for row in result[:5]:  # Show first 5
                logger.debug(f"  - {row[0]}")
        else:
            logger.warning("⚠️ No query pattern indexes found")

        # Check vector extension
        try:
            execute_query("SELECT * FROM pg_extension WHERE extname = 'vector'")
            logger.info("✅ Vector extension is available")
        except Exception as e:
            logger.warning(f"⚠️ Vector extension check failed: {e}")

        logger.info("✅ Schema verification completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during schema verification: {e}")
        return False

def show_migration_status() -> None:
    """Show current migration status."""
    try:
        logger.info("Checking current migration status...")

        # Check existing LTST tables
        ltst_tables = ["conversation_sessions", "conversation_messages", "conversation_context", "user_preferences"]

        logger.info("LTST Memory System tables:")
        for table in ltst_tables:
            try:
                result = execute_query(f"SELECT COUNT(*) FROM {table}")
                count = result[0][0] if result else 0
                logger.info(f"  ✅ {table}: {count} rows")
            except Exception:
                logger.info(f"  ❌ {table}: Not found")

        # Check query pattern tables
        qp_tables = ["query_patterns", "query_relationships", "query_intentions", "query_clusters", "query_predictions"]

        logger.info("Query Pattern tables:")
        for table in qp_tables:
            try:
                result = execute_query(f"SELECT COUNT(*) FROM {table}")
                count = result[0][0] if result else 0
                logger.info(f"  ✅ {table}: {count} rows")
            except Exception:
                logger.info(f"  ❌ {table}: Not found - needs migration")

    except Exception as e:
        logger.error(f"Error checking migration status: {e}")

def rollback_migration() -> bool:
    """Rollback the query pattern schema migration.

    Returns:
        True if rollback was successful
    """
    try:
        logger.warning("Rolling back query pattern schema migration...")

        # Tables to drop (in reverse dependency order)
        tables_to_drop = [
            "query_predictions",
            "query_clusters",
            "query_intentions",
            "query_relationships",
            "query_patterns",
        ]

        success_count = 0

        for table in tables_to_drop:
            try:
                execute_query(f"DROP TABLE IF EXISTS {table} CASCADE")
                logger.info(f"✅ Dropped table: {table}")
                success_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to drop table {table}: {e}")

        logger.info(f"Rollback completed: {success_count}/{len(tables_to_drop)} tables dropped")
        return success_count == len(tables_to_drop)

    except Exception as e:
        logger.error(f"Error during rollback: {e}")
        return False

def main():
    """Main function for CLI usage."""

    parser = argparse.ArgumentParser(description="Query Pattern Knowledge Graph Schema Migration")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be executed without making changes")
    parser.add_argument("--status", action="store_true", help="Show current migration status")
    parser.add_argument("--verify", action="store_true", help="Verify existing schema")
    parser.add_argument("--rollback", action="store_true", help="Rollback the migration")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        if args.status:
            show_migration_status()
        elif args.verify:
            if verify_schema_migration():
                logger.info("✅ Schema verification passed")
                sys.exit(0)
            else:
                logger.error("❌ Schema verification failed")
                sys.exit(1)
        elif args.rollback:
            if rollback_migration():
                logger.info("✅ Rollback completed successfully")
                sys.exit(0)
            else:
                logger.error("❌ Rollback failed")
                sys.exit(1)
        else:
            # Default: run migration
            if migrate_query_pattern_schema(dry_run=args.dry_run):
                logger.info("✅ Migration completed successfully")
                sys.exit(0)
            else:
                logger.error("❌ Migration failed")
                sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()