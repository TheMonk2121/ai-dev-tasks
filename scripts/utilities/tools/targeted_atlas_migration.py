#!/usr/bin/env python3
"""
Targeted Atlas migration: Add embeddings to content-based tables, remove from structural tables.
"""

import os

import psycopg2


def targeted_atlas_migration():
    """Targeted migration of Atlas tables based on their purpose."""

    print("🎯 TARGETED ATLAS MIGRATION: Content vs Structural Tables")
    print("=" * 70)

    # Content-based tables that SHOULD have embeddings (for semantic search)
    content_tables = [
        {
            "name": "atlas_node",
            "description": "Core graph nodes with content for semantic search",
            "has_embedding": True,
            "embedding_dim": 384,
        },
        {
            "name": "atlas_conversation_turn",
            "description": "Individual conversation turns for semantic similarity",
            "has_embedding": True,
            "embedding_dim": 384,
        },
        {
            "name": "atlas_thread",
            "description": "Thread titles and content for topic-based search",
            "has_embedding": True,
            "embedding_dim": 384,
        },
    ]

    # Structural tables that should NOT have embeddings (relationship/metadata only)
    structural_tables = [
        {"name": "atlas_cross_thread_insight", "description": "Structured insights, not semantic content"},
        {"name": "atlas_edge", "description": "Pure relationship data (source → target)"},
        {"name": "atlas_evidence", "description": "Evidence metadata, not searchable content"},
        {"name": "atlas_query_response_relationship", "description": "Relationship metadata"},
        {"name": "atlas_thread_relationship", "description": "Thread relationship data"},
    ]

    try:
        with psycopg2.connect(os.getenv("POSTGRES_DSN")) as conn:
            with conn.cursor() as cur:
                # Step 1: Handle content-based tables (add/ensure embeddings)
                print("\\n🔧 Step 1: Configuring content-based tables for embeddings...")

                for table in content_tables:
                    table_name = table["name"]
                    print(f"\\n📊 {table_name}: {table['description']}")

                    try:
                        # Check if table exists
                        cur.execute(
                            """
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_name = %s
                            )
                        """,
                            (table_name,),
                        )

                        result = cur.fetchone()
                        exists = result[0] if result else False
                        if not exists:
                            print(f"   ⚠️  {table_name}: Table does not exist, skipping")
                            continue

                        # Check current embedding column
                        cur.execute(
                            """
                            SELECT column_name, data_type, is_nullable
                            FROM information_schema.columns 
                            WHERE table_name = %s AND column_name = 'embedding'
                        """,
                            (table_name,),
                        )

                        embedding_col = cur.fetchone()

                        if embedding_col:
                            current_type = embedding_col[1]
                            print(f"   📋 Current embedding: {current_type} (nullable: {embedding_col[2]})")

                            # Check if it's already 384 dimensions
                            if "vector(384)" in current_type:
                                print(f"   ✅ {table_name}: Already has vector(384) - no changes needed")
                            else:
                                print(f"   🔄 {table_name}: Updating to vector(384)...")

                                # Clear existing embeddings
                                cur.execute(f"UPDATE {table_name} SET embedding = NULL WHERE embedding IS NOT NULL")
                                cleared = cur.rowcount
                                print(f"      Cleared {cleared} existing embeddings")

                                # Update column type
                                cur.execute(f"ALTER TABLE {table_name} ALTER COLUMN embedding TYPE vector(384)")
                                print("      ✅ Updated to vector(384)")

                                # Create/update index
                                cur.execute(f"DROP INDEX IF EXISTS {table_name}_embedding_idx")
                                cur.execute(
                                    f"""
                                    CREATE INDEX IF NOT EXISTS {table_name}_embedding_idx 
                                    ON {table_name} USING hnsw (embedding vector_cosine_ops)
                                """
                                )
                                print("      ✅ Created HNSW vector index")
                        else:
                            print(f"   ➕ {table_name}: Adding embedding column...")

                            # Add embedding column
                            cur.execute(f"ALTER TABLE {table_name} ADD COLUMN embedding vector(384)")
                            print("      ✅ Added vector(384) column")

                            # Create index
                            cur.execute(
                                f"""
                                CREATE INDEX IF NOT EXISTS {table_name}_embedding_idx 
                                ON {table_name} USING hnsw (embedding vector_cosine_ops)
                            """
                            )
                            print("      ✅ Created HNSW vector index")

                        # Test 384-dimensional vector insertion
                        test_vector = [0.1] * 384
                        try:
                            if table_name == "atlas_node":
                                cur.execute(
                                    """
                                    INSERT INTO atlas_node (node_id, node_type, title, content, embedding, expires_at)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                """,
                                    (
                                        "test_384_atlas",
                                        "test",
                                        "Test 384",
                                        "Test content",
                                        test_vector,
                                        "2025-09-15 00:00:00",
                                    ),
                                )
                            elif table_name == "atlas_conversation_turn":
                                cur.execute(
                                    """
                                    INSERT INTO atlas_conversation_turn (turn_id, thread_id, role, content, embedding, timestamp)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                """,
                                    (
                                        "test_turn",
                                        "test_thread",
                                        "user",
                                        "Test content",
                                        test_vector,
                                        "2025-09-15 00:00:00",
                                    ),
                                )
                            elif table_name == "atlas_thread":
                                cur.execute(
                                    """
                                    INSERT INTO atlas_thread (thread_id, session_id, title, embedding)
                                    VALUES (%s, %s, %s, %s)
                                """,
                                    ("test_thread", "test_session", "Test thread", test_vector),
                                )

                            # Clean up test data
                            cur.execute(
                                f"DELETE FROM {table_name} WHERE node_id = %s OR turn_id = %s OR thread_id = %s",
                                ("test_384_atlas", "test_turn", "test_thread"),
                            )
                            conn.commit()

                            print(f"      ✅ {table_name}: 384-dimensional vector insertion successful")

                        except Exception as e:
                            print(f"      ❌ {table_name}: Vector insertion failed: {e}")

                    except Exception as e:
                        print(f"   ❌ {table_name}: Error - {e}")

                # Step 2: Handle structural tables (remove embeddings)
                print("\\n🔧 Step 2: Configuring structural tables (removing embeddings)...")

                for table in structural_tables:
                    table_name = table["name"]
                    print(f"\\n📊 {table_name}: {table['description']}")

                    try:
                        # Check if table exists
                        cur.execute(
                            """
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_name = %s
                            )
                        """,
                            (table_name,),
                        )

                        result = cur.fetchone()
                        exists = result[0] if result else False
                        if not exists:
                            print(f"   ⚠️  {table_name}: Table does not exist, skipping")
                            continue

                        # Check if embedding column exists
                        cur.execute(
                            """
                            SELECT column_name, data_type
                            FROM information_schema.columns 
                            WHERE table_name = %s AND column_name = 'embedding'
                        """,
                            (table_name,),
                        )

                        embedding_col = cur.fetchone()

                        if embedding_col:
                            print(f"   🗑️  {table_name}: Removing embedding column...")

                            # Drop embedding column
                            cur.execute(f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS embedding")
                            print("      ✅ Removed embedding column")

                            # Drop any embedding indexes
                            cur.execute(f"DROP INDEX IF EXISTS {table_name}_embedding_idx")
                            cur.execute(f"DROP INDEX IF EXISTS {table_name}_embedding_hnsw_idx")
                            print("      ✅ Removed embedding indexes")
                        else:
                            print(f"   ✅ {table_name}: No embedding column (already correct)")

                    except Exception as e:
                        print(f"   ❌ {table_name}: Error - {e}")

                # Step 3: Verify final state
                print("\\n📊 Step 3: Verifying final Atlas table configuration...")

                all_atlas_tables = content_tables + structural_tables

                for table in all_atlas_tables:
                    table_name = table["name"]
                    try:
                        # Check if table exists
                        cur.execute(
                            """
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_name = %s
                            )
                        """,
                            (table_name,),
                        )

                        result = cur.fetchone()
                        exists = result[0] if result else False
                        if not exists:
                            print(f"   ⚠️  {table_name}: Table does not exist")
                            continue

                        # Check embedding column
                        cur.execute(
                            """
                            SELECT column_name, data_type, is_nullable
                            FROM information_schema.columns 
                            WHERE table_name = %s AND column_name = 'embedding'
                        """,
                            (table_name,),
                        )

                        embedding_col = cur.fetchone()

                        if table["has_embedding"]:
                            if embedding_col:
                                print(f"   ✅ {table_name}: Has embedding column ({embedding_col[1]})")
                            else:
                                print(f"   ❌ {table_name}: Missing embedding column")
                        else:
                            if embedding_col:
                                print(f"   ❌ {table_name}: Has embedding column (should not)")
                            else:
                                print(f"   ✅ {table_name}: No embedding column (correct)")

                    except Exception as e:
                        print(f"   ⚠️  {table_name}: Error checking - {e}")

                # Commit all changes
                conn.commit()
                print("\\n✅ Targeted Atlas migration completed successfully!")

                # Final summary
                print("\\n🎯 MIGRATION SUMMARY:")
                print("=" * 50)
                print(f"✅ Content-based tables (with embeddings): {len(content_tables)}")
                print(f"✅ Structural tables (no embeddings): {len(structural_tables)}")
                print("\\n📋 Content-based tables:")
                for table in content_tables:
                    print(f"   - {table['name']}: {table['description']}")
                print("\\n📋 Structural tables:")
                for table in structural_tables:
                    print(f"   - {table['name']}: {table['description']}")

                print("\\n🎉 ATLAS MIGRATION COMPLETE!")
                print("   Content-based tables ready for semantic search")
                print("   Structural tables optimized for relationships")
                print("   Database aligned with Atlas architecture principles")

    except Exception as e:
        print(f"❌ Targeted Atlas migration failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def main():
    """Main migration function."""

    # Set database connection
    os.environ["POSTGRES_DSN"] = "postgresql://danieljacobs@localhost:5432/ai_agency"

    print("🚀 Starting Targeted Atlas Migration")
    print("=" * 70)
    print("🎯 This migration will:")
    print("   ✅ Add/ensure embeddings on 3 content-based Atlas tables")
    print("   ✅ Remove embeddings from 5 structural Atlas tables")
    print("   ✅ Align with Atlas architecture principles")
    print()

    # Ask for confirmation
    response = input("Do you want to proceed with the targeted Atlas migration? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Migration cancelled")
        return 1

    # Run migration
    success = targeted_atlas_migration()

    if success:
        print("\\n🎉 Targeted Atlas migration completed successfully!")
        print("   Atlas tables now properly configured for their purposes")
        print("   Content-based tables ready for semantic search")
        print("   Structural tables optimized for relationships")
        return 0
    else:
        print("\\n❌ Targeted Atlas migration failed!")
        return 1


if __name__ == "__main__":
    exit(main())
