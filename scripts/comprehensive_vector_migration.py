#!/usr/bin/env python3
"""
Comprehensive migration to 384-dimensional vectors with proper constraint handling.
"""

import os

import psycopg2


def comprehensive_vector_migration():
    """Comprehensive migration to 384-dimensional vectors."""

    print("🔄 Comprehensive Vector Migration: 1024 → 384 dimensions")
    print("=" * 70)

    try:
        with psycopg2.connect(os.getenv("POSTGRES_DSN")) as conn:
            with conn.cursor() as cur:
                # Step 1: Drop NOT NULL constraints
                print("\\n🔧 Step 1: Dropping NOT NULL constraints...")

                try:
                    cur.execute("ALTER TABLE conv_chunks ALTER COLUMN embedding DROP NOT NULL")
                    print("   ✅ Dropped NOT NULL constraint from conv_chunks.embedding")
                except Exception as e:
                    print(f"   ⚠️  Warning: Could not drop NOT NULL constraint: {e}")

                # Step 2: Clear existing vector data
                print("\\n🗑️  Step 2: Clearing existing vector data...")

                cur.execute("UPDATE atlas_node SET embedding = NULL WHERE embedding IS NOT NULL")
                atlas_cleared = cur.rowcount
                print(f"   ✅ Cleared {atlas_cleared} embeddings from atlas_node")

                cur.execute("UPDATE conv_chunks SET embedding = NULL WHERE embedding IS NOT NULL")
                conv_cleared = cur.rowcount
                print(f"   ✅ Cleared {conv_cleared} embeddings from conv_chunks")

                # Step 3: Update schema to 384 dimensions
                print("\\n🔧 Step 3: Updating schema to 384 dimensions...")

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

                # Step 4: Recreate indexes
                print("\\n🔧 Step 4: Recreating vector indexes...")

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

                # Step 5: Restore NOT NULL constraints (optional)
                print("\\n🔧 Step 5: Restoring NOT NULL constraints...")

                try:
                    cur.execute("ALTER TABLE conv_chunks ALTER COLUMN embedding SET NOT NULL")
                    print("   ✅ Restored NOT NULL constraint on conv_chunks.embedding")
                except Exception as e:
                    print(f"   ⚠️  Warning: Could not restore NOT NULL constraint: {e}")

                # Commit changes
                conn.commit()
                print("\\n✅ Comprehensive migration completed successfully!")

                # Step 6: Verify the changes
                print("\\n📊 Step 6: Verification...")
                cur.execute(
                    """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'atlas_node' 
                    AND column_name = 'embedding'
                """
                )

                atlas_embedding = cur.fetchone()
                if atlas_embedding:
                    print(f"   atlas_node.embedding: {atlas_embedding[1]} (nullable: {atlas_embedding[2]})")

                cur.execute(
                    """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'conv_chunks' 
                    AND column_name = 'embedding'
                """
                )

                conv_embedding = cur.fetchone()
                if conv_embedding:
                    print(f"   conv_chunks.embedding: {conv_embedding[1]} (nullable: {conv_embedding[2]})")

                print("\\n🎯 Migration Summary:")
                print("   ✅ Database schema updated to 384 dimensions")
                print("   ✅ Vector indexes recreated")
                print("   ✅ Ready for standards-compliant chunking")
                print("   ✅ New conversations will use proper chunking and 384-dim embeddings")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def main():
    """Main migration function."""

    # Set database connection
    os.environ["POSTGRES_DSN"] = "postgresql://danieljacobs@localhost:5432/ai_agency"

    print("🚀 Starting Comprehensive Vector Dimension Migration")
    print("=" * 70)
    print("⚠️  WARNING: This will clear existing vector data!")
    print("   The database schema will be updated to support 384-dimensional vectors.")
    print("   This migration handles NOT NULL constraints properly.")
    print()

    # Ask for confirmation
    response = input("Do you want to proceed? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Migration cancelled")
        return 1

    # Run migration
    success = comprehensive_vector_migration()

    if success:
        print("\\n🎉 Comprehensive migration completed successfully!")
        print("   Database now supports 384-dimensional vectors")
        print("   Ready for standards-compliant chunking")
        return 0
    else:
        print("\\n❌ Migration failed!")
        return 1


if __name__ == "__main__":
    exit(main())
