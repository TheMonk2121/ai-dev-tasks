#!/usr/bin/env python3
"""
Safely migrate vector dimensions from 1024 to 384 by clearing and recreating.
"""

import os
import sys
from typing import Any

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.psycopg3_config import Psycopg3Config


def safe_migrate_vector_dimensions() -> Any:
    """Safely migrate vector dimensions by clearing existing data and recreating schema."""

    print("🔄 Safe Migration: 1024 → 384 dimensions")
    print("=" * 50)
    print("⚠️  This will clear existing vector data and recreate with 384 dimensions")

    try:
        with Psycopg3Config.get_cursor("default") as cur:
            # Step 1: Clear existing vector data
            print("\\n🗑️  Step 1: Clearing existing vector data...")

            cur.execute("UPDATE atlas_node SET embedding = NULL WHERE embedding IS NOT NULL")
            atlas_cleared = cur.rowcount
            print(f"   ✅ Cleared {atlas_cleared} embeddings from atlas_node")

            cur.execute("UPDATE conv_chunks SET embedding = NULL WHERE embedding IS NOT NULL")
            conv_cleared = cur.rowcount
            print(f"   ✅ Cleared {conv_cleared} embeddings from conv_chunks")

            # Step 2: Update schema to 384 dimensions
            print("\\n🔧 Step 2: Updating schema to 384 dimensions...")

            # Update atlas_node
            cur.execute(
                """
                ALTER TABLE atlas_node 
                ALTER COLUMN embedding TYPE vector(384)
            """
            )
            print("   ✅ atlas_node.embedding updated to vector(384)")

            # Update conv_chunks
            cur.execute(
                """
                ALTER TABLE conv_chunks 
                ALTER COLUMN embedding TYPE vector(384)
            """
            )
            print("   ✅ conv_chunks.embedding updated to vector(384)")

            # Step 3: Recreate indexes
            print("\\n🔧 Step 3: Recreating vector indexes...")

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

            # Step 4: Verify the changes
            print("\\n📊 Step 4: Verification...")
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

            print("\\n🎯 Next Steps:")
            print("   1. Run the standards-compliant chunking test")
            print("   2. New conversations will use 384-dimensional embeddings")
            print("   3. Memory consolidation will work with proper chunking")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def main() -> Any:
    """Main migration function."""

    # Set database connection
    os.environ["POSTGRES_DSN"] = "postgresql://danieljacobs@localhost:5432/ai_agency"

    print("🚀 Starting Safe Vector Dimension Migration")
    print("=" * 60)
    print("⚠️  WARNING: This will clear existing vector data!")
    print("   The database schema will be updated to support 384-dimensional vectors.")
    print("   Existing conversations will need to be re-processed with chunking.")
    print()

    # Ask for confirmation
    response = input("Do you want to proceed? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Migration cancelled")
        return 1

    # Run migration
    success = safe_migrate_vector_dimensions()

    if success:
        print("\\n🎉 Safe migration completed successfully!")
        print("   Database now supports 384-dimensional vectors")
        print("   Ready for standards-compliant chunking")
        return 0
    else:
        print("\\n❌ Migration failed!")
        return 1


if __name__ == "__main__":
    exit(main())
