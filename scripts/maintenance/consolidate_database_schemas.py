from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.db_dsn import resolve_dsn
from src.common.psycopg3_config import Psycopg3Config

#!/usr/bin/env python3
"""
Phase 2: Schema Consolidation
Adds missing tables and columns from dspy_rag to ai_agency database.
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class SchemaConsolidator:
    """Consolidates database schemas from dspy_rag to ai_agency."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.changes_made = []
        self.errors = []

    def get_table_schema(self, table_name: str, source_dsn: str) -> dict | None:
        """Get table schema from source database."""
        try:
            with psycopg.connect(source_dsn) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get column information
                    cur.execute(
                        """
                        SELECT 
                            column_name, 
                            data_type, 
                            is_nullable, 
                            column_default,
                            character_maximum_length,
                            numeric_precision,
                            numeric_scale
                        FROM information_schema.columns 
                        WHERE table_name = %s AND table_schema = 'public'
                        ORDER BY ordinal_position
                    """,
                        (table_name,),
                    )
                    columns = cur.fetchall()

                    # Get constraints
                    cur.execute(
                        """
                        SELECT 
                            tc.constraint_name,
                            tc.constraint_type,
                            kcu.column_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu 
                            ON tc.constraint_name = kcu.constraint_name
                        WHERE tc.table_name = %s AND tc.table_schema = 'public'
                    """,
                        (table_name,),
                    )
                    constraints = cur.fetchall()

                    # Get indexes
                    cur.execute(
                        """
                        SELECT 
                            indexname,
                            indexdef
                        FROM pg_indexes 
                        WHERE tablename = %s AND schemaname = 'public'
                    """,
                        (table_name,),
                    )
                    indexes = cur.fetchall()

                    return {"columns": columns, "constraints": constraints, "indexes": indexes}
        except Exception as e:
            self.errors.append(f"Error getting schema for {table_name}: {e}")
            return None

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in target database."""
        try:
            with psycopg.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = %s AND table_schema = 'public'
                        )
                    """,
                        (table_name,),
                    )
                    result = cur.fetchone()
                    return result[0] if result else False
        except Exception as e:
            self.errors.append(f"Error checking if table {table_name} exists: {e}")
            return False

    def column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if column exists in table."""
        try:
            with psycopg.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = %s AND column_name = %s AND table_schema = 'public'
                        )
                    """,
                        (table_name, column_name),
                    )
                    result = cur.fetchone()
                    return result[0] if result else False
        except Exception as e:
            self.errors.append(f"Error checking if column {column_name} exists in {table_name}: {e}")
            return False

    def add_missing_columns(self, table_name: str, schema: dict):
        """Add missing columns to existing table."""
        if not schema or not schema["columns"]:
            return

        try:
            with psycopg.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    for column in schema["columns"]:
                        col_name = column["column_name"]
                        if not self.column_exists(table_name, col_name):
                            # Build ALTER TABLE statement
                            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name}"

                            # Add data type
                            data_type = column["data_type"]
                            if column["character_maximum_length"]:
                                data_type += f"({column['character_maximum_length']})"
                            elif column["numeric_precision"] and column["numeric_scale"]:
                                data_type += f"({column['numeric_precision']},{column['numeric_scale']})"

                            alter_sql += f" {data_type}"

                            # Add NOT NULL if needed
                            if column["is_nullable"] == "NO":
                                alter_sql += " NOT NULL"

                            # Add default if exists
                            if column["column_default"]:
                                alter_sql += f" DEFAULT {column['column_default']}"

                            cur.execute(alter_sql)
                            self.changes_made.append(f"  ✅ Added column {col_name} to {table_name}")
                        else:
                            self.changes_made.append(f"  ℹ️  Column {col_name} already exists in {table_name}")
        except Exception as e:
            error_msg = f"Error adding columns to {table_name}: {e}"
            self.errors.append(error_msg)
            self.changes_made.append(f"  ❌ {error_msg}")

    def create_missing_table(self, table_name: str, schema: dict):
        """Create missing table with full schema."""
        if not schema or not schema["columns"]:
            return

        try:
            with psycopg.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    # Build CREATE TABLE statement
                    create_sql = f"CREATE TABLE {table_name} ("

                    column_definitions = []
                    for column in schema["columns"]:
                        col_name = column["column_name"]
                        data_type = column["data_type"]

                        # Add length/precision if needed
                        if column["character_maximum_length"]:
                            data_type += f"({column['character_maximum_length']})"
                        elif column["numeric_precision"] and column["numeric_scale"]:
                            data_type += f"({column['numeric_precision']},{column['numeric_scale']})"

                        col_def = f"{col_name} {data_type}"

                        # Add NOT NULL if needed
                        if column["is_nullable"] == "NO":
                            col_def += " NOT NULL"

                        # Add default if exists
                        if column["column_default"]:
                            col_def += f" DEFAULT {column['column_default']}"

                        column_definitions.append(col_def)

                    create_sql += ",\n".join(column_definitions)
                    create_sql += ")"

                    cur.execute(create_sql)
                    self.changes_made.append(f"  ✅ Created table {table_name}")

                    # Add indexes
                    for index in schema["indexes"]:
                        try:
                            cur.execute(index["indexdef"])
                            self.changes_made.append(f"  ✅ Added index {index['indexname']} to {table_name}")
                        except Exception as e:
                            self.changes_made.append(f"  ⚠️  Could not add index {index['indexname']}: {e}")

        except Exception as e:
            error_msg = f"Error creating table {table_name}: {e}"
            self.errors.append(error_msg)
            self.changes_made.append(f"  ❌ {error_msg}")

    def consolidate_schemas(self):
        """Consolidate schemas from dspy_rag to ai_agency."""
        print("🔧 Phase 2: Schema Consolidation")
        print("=" * 60)

        # Get list of tables from dspy_rag
        dspy_rag_dsn = "postgresql://danieljacobs@localhost:5432/dspy_rag"

        try:
            with psycopg.connect(dspy_rag_dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                        ORDER BY table_name
                    """
                    )
                    dspy_tables = [row[0] for row in cur.fetchall()]
        except Exception as e:
            self.errors.append(f"Error connecting to dspy_rag database: {e}")
            return False

        print(f"📋 Found {len(dspy_tables)} tables in dspy_rag database")

        # Process each table
        for table_name in dspy_tables:
            print(f"\n🔍 Processing table: {table_name}")

            # Get schema from dspy_rag
            schema = self.get_table_schema(table_name, dspy_rag_dsn)
            if not schema:
                continue

            # Check if table exists in ai_agency
            if self.table_exists(table_name):
                print(f"  📝 Table {table_name} exists, checking for missing columns...")
                self.add_missing_columns(table_name, schema)
            else:
                print(f"  🆕 Table {table_name} missing, creating...")
                self.create_missing_table(table_name, schema)

        return True

    def verify_consolidation(self):
        """Verify that consolidation was successful."""
        print("\n🔍 Verifying schema consolidation...")

        try:
            with psycopg.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    # Get table count
                    cur.execute(
                        """
                        SELECT COUNT(*) 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                    """
                    )
                    result = cur.fetchone()
                    table_count = result[0] if result else 0

                    # Get column count
                    cur.execute(
                        """
                        SELECT COUNT(*) 
                        FROM information_schema.columns 
                        WHERE table_schema = 'public'
                    """
                    )
                    result = cur.fetchone()
                    column_count = result[0] if result else 0

                    print(f"  📊 Tables in ai_agency: {table_count}")
                    print(f"  📊 Columns in ai_agency: {column_count}")

                    # Check for specific tables that should exist
                    required_tables = [
                        "conversation_context",
                        "conversation_sessions",
                        "documents",
                        "document_chunks",
                        "memory_performance_metrics",
                        "user_preferences",
                    ]

                    missing_tables = []
                    for table in required_tables:
                        if not self.table_exists(table):
                            missing_tables.append(table)

                    if missing_tables:
                        print(f"  ❌ Missing required tables: {missing_tables}")
                        return False
                    else:
                        print("  ✅ All required tables present")
                        return True

        except Exception as e:
            self.errors.append(f"Error verifying consolidation: {e}")
            return False

    def run(self):
        """Run the schema consolidation process."""
        success = self.consolidate_schemas()

        if success:
            self.verify_consolidation()

        # Summary
        print("\n" + "=" * 60)
        print("📊 PHASE 2 SUMMARY")
        print("=" * 60)

        if self.changes_made:
            print(f"✅ Changes made: {len([c for c in self.changes_made if '✅' in c])}")
            print(f"ℹ️  Items checked: {len([c for c in self.changes_made if 'ℹ️' in c])}")
            print(f"⚠️  Warnings: {len([c for c in self.changes_made if '⚠️' in c])}")

        if self.errors:
            print(f"❌ Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"   {error}")

        print("\n🎉 Phase 2 completed!")
        print("📋 Next steps:")
        print("   1. Review schema changes")
        print("   2. Proceed to Phase 3 (Data Migration)")

        return len(self.errors) == 0

def main():
    """Main entry point."""
    # Force use of ai_agency database
    dsn = "postgresql://danieljacobs@localhost:5432/ai_agency"
    print(f"📡 Using database: {dsn}")

    consolidator = SchemaConsolidator(dsn)
    success = consolidator.run()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())