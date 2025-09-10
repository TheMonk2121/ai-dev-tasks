#!/usr/bin/env python3
"""
Simple script to add LTST Memory System tables to existing database.
"""

import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import after path setup
from src.utils.database_resilience import DatabaseResilienceManager  # noqa: E402


def add_ltst_tables():
    """Add LTST Memory System tables to the database."""

    # Get connection string
    connection_string = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")

    # Initialize database manager
    db_manager = DatabaseResilienceManager(connection_string)

    # Read the schema file
    schema_file = project_root / "config" / "database" / "ltst_memory_schema.sql"

    if not schema_file.exists():
        print(f"Schema file not found: {schema_file}")
        return False

    with open(schema_file) as f:
        schema_sql = f.read()

    print("Adding LTST Memory System tables to database...")

    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Execute the schema
                cursor.execute(schema_sql)
                conn.commit()

        print("✅ LTST Memory System tables added successfully!")
        return True

    except Exception as e:
        print(f"❌ Error adding tables: {e}")
        return False


if __name__ == "__main__":
    success = add_ltst_tables()
    sys.exit(0 if success else 1)
