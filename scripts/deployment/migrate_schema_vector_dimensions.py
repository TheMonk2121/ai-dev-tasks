#!/usr/bin/env python3
"""
Migrate database schema to support 384-dimensional vectors.
"""

import os
import sys
from typing import Any

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.psycopg3_config import Psycopg3Config


def migrate_schema_vector_dimensions() -> Any:
    """Update database schema to support 384-dimensional vectors."""

    print("🔄 Migrating Database Schema: 1024 → 384 dimensions")
    print("=" * 60)

    try:
        with Psycopg3Config.get_cursor("default") as cur:
            # Check current vector dimensions
            print("📊 Checking current vector dimensions...")

            # Check atlas_node table
            cur.execute(
                """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'atlas_node' 
                AND column_name = 'embedding'
            """
            )

            atlas_embedding: dict[str, Any] | None = cur.fetchone()
            print(f"   atlas_node.embedding: {atlas_embedding['data_type'] if atlas_embedding else 'Not found'}")

            # Check conv_chunks table
            cur.execute(
                """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'conv_chunks' 
                AND column_name = 'embedding'
            """
            )

            conv_embedding: dict[str, Any] | None = cur.fetchone()
            print(f"   conv_chunks.embedding: {conv_embedding['data_type'] if conv_embedding else 'Not found'}")

            # Update atlas_node table
            print("\\n🔧 Updating atlas_node table...")
            cur.execute(
                """
                ALTER TABLE atlas_node 
                ALTER COLUMN embedding TYPE vector(384)
            """
            )
            print("   ✅ atlas_node.embedding updated to vector(384)")

            # Update conv_chunks table
            print("\\n🔧 Updating conv_chunks table...")
            cur.execute(
                """
                ALTER TABLE conv_chunks 
                ALTER COLUMN embedding TYPE vector(384)
            """
            )
            print("   ✅ conv_chunks.embedding updated to vector(384)")

            # Recreate indexes
            print("\\n🔧 Recreating vector indexes...")

            # Drop existing indexes
            try:
                cur.execute("DROP INDEX IF EXISTS atlas_node_embedding_idx")
                cur.execute("DROP INDEX IF EXISTS conv_chunks_embedding_idx")
                print("   ✅ Dropped existing vector indexes")
            except Exception as e:
                print(f"   ⚠️  Warning: Could not drop indexes: {e}")

            # Create new indexes
            try:
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS atlas_node_embedding_idx 
                    ON atlas_node USING hnsw (embedding vector_cosine_ops)
                """
                )
                print("   ✅ Created atlas_node vector index")

                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS conv_chunks_embedding_idx 
                    ON conv_chunks USING hnsw (embedding vector_cosine_ops)
                """
                )
                print("   ✅ Created conv_chunks vector index")
            except Exception as e:
                print(f"   ⚠️  Warning: Could not create indexes: {e}")

            print("\\n✅ Schema migration completed successfully!")

            # Verify the changes
            print("\\n📊 Verification:")
            cur.execute(
                """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'atlas_node' 
                AND column_name = 'embedding'
            """
            )

            atlas_embedding: dict[str, Any] | None = cur.fetchone()
            print(f"   atlas_node.embedding: {atlas_embedding['data_type'] if atlas_embedding else 'Not found'}")

            cur.execute(
                """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'conv_chunks' 
                AND column_name = 'embedding'
            """
            )

            conv_embedding: dict[str, Any] | None = cur.fetchone()
            print(f"   conv_chunks.embedding: {conv_embedding['data_type'] if conv_embedding else 'Not found'}")

    except Exception as e:
        print(f"❌ Schema migration failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def main() -> Any:
    """Main schema migration function."""

    # Set database connection
    os.environ["POSTGRES_DSN"] = "postgresql://danieljacobs@localhost:5432/ai_agency"

    print("🚀 Starting Database Schema Migration")
    print("=" * 50)
    print("⚠️  WARNING: This will update the database schema!")
    print("   Make sure you have a database backup before proceeding.")
    print()

    # Ask for confirmation
    response = input("Do you want to proceed? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Migration cancelled")
        return 1

    # Run migration
    success = migrate_schema_vector_dimensions()

    if success:
        print("\\n🎉 Schema migration completed successfully!")
        print("   Database now supports 384-dimensional vectors")
        return 0
    else:
        print("\\n❌ Schema migration failed!")
        return 1


if __name__ == "__main__":
    exit(main())
