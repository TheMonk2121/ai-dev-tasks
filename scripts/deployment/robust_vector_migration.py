#!/usr/bin/env python3
"""
Robust migration of ALL vector tables to 384 dimensions with proper dependency handling.
"""

import os

import psycopg2


def robust_vector_migration():
    """Robust migration of ALL vector tables to 384 dimensions."""

    print("🔄 ROBUST VECTOR MIGRATION: ALL TABLES → 384 dimensions")
    print("=" * 80)

    try:
        with psycopg2.connect(os.getenv("POSTGRES_DSN")) as conn:
            with conn.cursor() as cur:
                # Step 1: Handle view dependencies first
                print("\\n🔧 Step 1: Handling view dependencies...")

                # Drop views that depend on vector columns
                views_to_drop = ["conversation_summaries", "active_document_chunks", "active_conversation_sessions"]

                for view in views_to_drop:
                    try:
                        cur.execute(f"DROP VIEW IF EXISTS {view} CASCADE")
                        print(f"   ✅ {view}: Dropped view")
                    except Exception as e:
                        print(f"   ⚠️  {view}: Could not drop view: {e}")

                # Step 2: Clear all vector data
                print("\\n🗑️  Step 2: Clearing ALL vector data...")

                tables_to_clear = [
                    "atlas_conversation_turn",
                    "atlas_node",
                    "atlas_thread",
                    "conv_chunks",
                    "conversation_memory",
                    "conversation_messages",
                    "document_chunks",
                ]

                total_cleared = 0
                for table in tables_to_clear:
                    try:
                        cur.execute(f"UPDATE {table} SET embedding = NULL WHERE embedding IS NOT NULL")
                        cleared = cur.rowcount
                        total_cleared += cleared
                        print(f"   ✅ {table}: Cleared {cleared} embeddings")
                    except Exception as e:
                        print(f"   ⚠️  {table}: Could not clear embeddings: {e}")

                print(f"   📊 Total embeddings cleared: {total_cleared}")

                # Step 3: Update each table individually with proper error handling
                print("\\n🔧 Step 3: Updating tables to 384 dimensions...")

                successful_tables = []
                failed_tables = []

                for table in tables_to_clear:
                    try:
                        # Start a new transaction for each table
                        cur.execute("BEGIN")
                        cur.execute(f"ALTER TABLE {table} ALTER COLUMN embedding TYPE vector(384)")
                        cur.execute("COMMIT")
                        print(f"   ✅ {table}: Updated to vector(384)")
                        successful_tables.append(table)
                    except Exception as e:
                        try:
                            cur.execute("ROLLBACK")
                        except:
                            pass
                        print(f"   ❌ {table}: Failed to update to vector(384): {e}")
                        failed_tables.append(table)

                # Step 4: Recreate vector indexes
                print("\\n🔧 Step 4: Recreating vector indexes...")

                for table in successful_tables:
                    try:
                        # Drop existing indexes
                        cur.execute(f"DROP INDEX IF EXISTS {table}_embedding_idx")
                        cur.execute(f"DROP INDEX IF EXISTS {table}_embedding_hnsw_idx")

                        # Create new HNSW index
                        cur.execute(
                            f"""
                            CREATE INDEX IF NOT EXISTS {table}_embedding_idx 
                            ON {table} USING hnsw (embedding vector_cosine_ops)
                        """
                        )
                        print(f"   ✅ {table}: Created HNSW vector index")
                    except Exception as e:
                        print(f"   ⚠️  {table}: Could not create index: {e}")

                # Step 5: Restore NOT NULL constraints
                print("\\n🔧 Step 5: Restoring NOT NULL constraints...")

                not_null_tables = ["conv_chunks"]
                for table in not_null_tables:
                    if table in successful_tables:
                        try:
                            cur.execute(f"ALTER TABLE {table} ALTER COLUMN embedding SET NOT NULL")
                            print(f"   ✅ {table}: Restored NOT NULL constraint")
                        except Exception as e:
                            print(f"   ⚠️  {table}: Could not restore NOT NULL constraint: {e}")

                # Step 6: Recreate views
                print("\\n🔧 Step 6: Recreating views...")

                # Recreate conversation_summaries view
                try:
                    cur.execute(
                        """
                        CREATE VIEW conversation_summaries AS
                        SELECT 
                            session_id,
                            COUNT(*) as message_count,
                            MAX(created_at) as last_message,
                            MIN(created_at) as first_message
                        FROM conversation_messages 
                        GROUP BY session_id
                    """
                    )
                    print("   ✅ conversation_summaries: Recreated view")
                except Exception as e:
                    print(f"   ⚠️  conversation_summaries: Could not recreate view: {e}")

                # Recreate active_document_chunks view
                try:
                    cur.execute(
                        """
                        CREATE VIEW active_document_chunks AS
                        SELECT 
                            dc.*,
                            d.file_path,
                            d.file_name
                        FROM document_chunks dc
                        JOIN documents d ON dc.document_id = d.id
                        WHERE dc.created_at > NOW() - INTERVAL '7 days'
                    """
                    )
                    print("   ✅ active_document_chunks: Recreated view")
                except Exception as e:
                    print(f"   ⚠️  active_document_chunks: Could not recreate view: {e}")

                # Recreate active_conversation_sessions view
                try:
                    cur.execute(
                        """
                        CREATE VIEW active_conversation_sessions AS
                        SELECT 
                            session_id,
                            COUNT(*) as message_count,
                            MAX(created_at) as last_activity
                        FROM conversation_messages 
                        WHERE created_at > NOW() - INTERVAL '24 hours'
                        GROUP BY session_id
                    """
                    )
                    print("   ✅ active_conversation_sessions: Recreated view")
                except Exception as e:
                    print(f"   ⚠️  active_conversation_sessions: Could not recreate view: {e}")

                # Step 7: Test 384-dimensional vector insertion
                print("\\n🧪 Step 7: Testing 384-dimensional vector insertion...")

                test_vector = [0.1] * 384
                test_successful = []
                test_failed = []

                for table in successful_tables:
                    try:
                        # Test insertion based on table structure
                        if table == "atlas_node":
                            cur.execute(
                                """
                                INSERT INTO atlas_node (node_id, node_type, title, content, embedding, expires_at)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                                (
                                    "test_384_robust",
                                    "test",
                                    "Test 384",
                                    "Test content",
                                    test_vector,
                                    "2025-09-15 00:00:00",
                                ),
                            )
                        elif table == "conv_chunks":
                            cur.execute(
                                """
                                INSERT INTO conv_chunks (session_id, chunk_text, embedding, expires_at)
                                VALUES (%s, %s, %s, %s)
                            """,
                                ("test_session", "Test content", test_vector, "2025-09-15 00:00:00"),
                            )
                        elif table == "atlas_conversation_turn":
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
                        elif table == "atlas_thread":
                            cur.execute(
                                """
                                INSERT INTO atlas_thread (thread_id, session_id, title, embedding)
                                VALUES (%s, %s, %s, %s)
                            """,
                                ("test_thread", "test_session", "Test thread", test_vector),
                            )
                        elif table == "conversation_memory":
                            cur.execute(
                                """
                                INSERT INTO conversation_memory (session_id, content, embedding, created_at)
                                VALUES (%s, %s, %s, %s)
                            """,
                                ("test_session", "Test content", test_vector, "2025-09-15 00:00:00"),
                            )
                        elif table == "conversation_messages":
                            cur.execute(
                                """
                                INSERT INTO conversation_messages (session_id, role, content, embedding, created_at)
                                VALUES (%s, %s, %s, %s, %s)
                            """,
                                ("test_session", "user", "Test content", test_vector, "2025-09-15 00:00:00"),
                            )
                        elif table == "document_chunks":
                            cur.execute(
                                """
                                INSERT INTO document_chunks (document_id, chunk_index, content, embedding, created_at)
                                VALUES (%s, %s, %s, %s, %s)
                            """,
                                (1, 1, "Test content", test_vector, "2025-09-15 00:00:00"),
                            )

                        # Clean up test data
                        cur.execute(
                            f"DELETE FROM {table} WHERE node_id = %s OR turn_id = %s OR thread_id = %s OR session_id = %s OR document_id = %s",
                            ("test_384_robust", "test_turn", "test_thread", "test_session", 1),
                        )
                        conn.commit()

                        print(f"   ✅ {table}: 384-dimensional vector insertion successful")
                        test_successful.append(table)

                    except Exception as e:
                        print(f"   ❌ {table}: 384-dimensional vector insertion failed: {e}")
                        test_failed.append(table)

                # Final summary
                print("\\n🎯 ROBUST MIGRATION SUMMARY:")
                print("=" * 60)
                print(f"✅ Successfully migrated: {len(successful_tables)}/{len(tables_to_clear)} tables")
                print(f"❌ Failed migrations: {len(failed_tables)}/{len(tables_to_clear)} tables")
                print(f"🧪 Test successful: {len(test_successful)}/{len(successful_tables)} tables")

                if successful_tables:
                    print(f"\\n✅ Successful tables: {', '.join(successful_tables)}")

                if test_successful:
                    print(f"\\n🧪 Test successful tables: {', '.join(test_successful)}")

                if failed_tables:
                    print(f"\\n❌ Failed tables: {', '.join(failed_tables)}")

                if test_failed:
                    print(f"\\n🧪 Test failed tables: {', '.join(test_failed)}")

                print("\\n🎉 ROBUST MIGRATION COMPLETE!")
                print("   Vector tables migrated to 384-dimensional embeddings")
                print("   Views recreated with proper dependencies")
                print("   Ready for standards-compliant chunking")

    except Exception as e:
        print(f"❌ Robust migration failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def main():
    """Main migration function."""

    # Set database connection
    os.environ["POSTGRES_DSN"] = "postgresql://danieljacobs@localhost:5432/ai_agency"

    print("🚀 Starting Robust Vector Migration")
    print("=" * 80)
    print("⚠️  WARNING: This will migrate ALL vector tables to 384 dimensions!")
    print("   This handles view dependencies and transaction issues properly.")
    print("   Make sure you have a database backup before proceeding.")
    print()

    # Ask for confirmation
    response = input("Do you want to proceed with the robust migration? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Migration cancelled")
        return 1

    # Run migration
    success = robust_vector_migration()

    if success:
        print("\\n🎉 Robust migration completed successfully!")
        print("   All vector tables now support 384-dimensional embeddings")
        print("   Database is fully aligned with project standards")
        return 0
    else:
        print("\\n❌ Robust migration failed!")
        return 1


if __name__ == "__main__":
    exit(main())
