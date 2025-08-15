#!/usr/bin/env python3
"""
Apply Clean Slate Database Schema
=================================
Applies the new clean-slate schema with proper foreign keys, constraints, and optimized indexes.
Based on ChatGPT's recommendations for deterministic, performant storage.

Usage:
    python3 scripts/apply_clean_slate_schema.py [--dry-run] [--backup]
"""

import argparse
import os
import sys
from pathlib import Path

# Add the dspy-rag-system src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.database_resilience import get_database_manager


def apply_clean_slate_schema(dry_run: bool = False, backup: bool = False):
    """Apply the clean-slate schema migration."""

    # Read the schema file
    schema_path = Path(__file__).parent.parent / "config" / "database" / "clean_slate_schema.sql"

    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        return False

    with open(schema_path, "r") as f:
        schema_sql = f.read()

    print("🧠 Applying clean-slate database schema...")
    print(f"   Schema file: {schema_path}")
    print(f"   Dry run: {dry_run}")
    print(f"   Backup: {backup}")
    print()

    if dry_run:
        print("📋 DRY RUN - Schema SQL:")
        print("=" * 80)
        print(schema_sql)
        print("=" * 80)
        print("✅ Dry run completed - no changes made")
        return True

    try:
        db = get_database_manager()

        # Create backup if requested
        if backup:
            print("💾 Creating backup...")
            backup_sql = """
            -- Create backup tables
            CREATE TABLE IF NOT EXISTS document_chunks_backup AS SELECT * FROM document_chunks;
            CREATE TABLE IF NOT EXISTS documents_backup AS SELECT * FROM documents;
            CREATE TABLE IF NOT EXISTS conversation_memory_backup AS SELECT * FROM conversation_memory;
            """
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(backup_sql)
            print("✅ Backup created")

        # Apply the schema
        print("🔧 Applying schema...")
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)

        print("✅ Clean-slate schema applied successfully!")
        print()
        print("📊 Next steps:")
        print("1. Re-ingest your documents: ./start_watch_folder.sh")
        print("2. Test the rehydrator: python3 scripts/cursor_memory_rehydrate.py planner 'test'")
        print("3. Verify deterministic results across multiple runs")

        return True

    except Exception as e:
        print(f"❌ Error applying schema: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check POSTGRES_DSN environment variable")
        print("3. Ensure you have write permissions to the database")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Apply clean-slate database schema")
    parser.add_argument("--dry-run", action="store_true", help="Show SQL without executing")
    parser.add_argument("--backup", action="store_true", help="Create backup tables before migration")

    args = parser.parse_args()

    success = apply_clean_slate_schema(dry_run=args.dry_run, backup=args.backup)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
