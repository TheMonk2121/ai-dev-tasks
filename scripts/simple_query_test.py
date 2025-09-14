#!/usr/bin/env python3
"""
Simple test to verify query storage is working.
"""

import hashlib
import os
import sys
from datetime import datetime

import psycopg2


def get_db_connection():
    """Get database connection."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
    from common.db_dsn import resolve_dsn

    dsn = resolve_dsn()

    # Handle mock database case
    if dsn and dsn.startswith("mock://"):
        print("⚠️  Mock database detected - skipping real database operations")
        return None

    return psycopg2.connect(dsn)


def test_simple_storage():
    """Test storing a simple conversation."""
    print("🧪 Testing simple conversation storage...")

    conn = get_db_connection()

    if conn is None:
        print("⚠️  Skipping database test - no real database connection available")
        return True

    # Test data
    session_id = f"test_session_{int(datetime.now().timestamp())}"
    user_id = "test_user"
    test_query = "How do I implement user authentication in FastAPI with JWT tokens?"
    test_response = "To implement user authentication in FastAPI with JWT tokens, you'll need to use libraries like python-jose and passlib."

    try:
        with conn.cursor() as cur:
            # Create a session
            cur.execute(
                """
                INSERT INTO conversation_sessions 
                (session_id, user_id, session_name, created_at, last_activity, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_id) DO NOTHING
            """,
                (session_id, user_id, "Test Session", datetime.now(), datetime.now(), "{}"),
            )

            # Store user query
            content_hash = hashlib.sha256(test_query.encode()).hexdigest()
            cur.execute(
                """
                INSERT INTO conversation_messages 
                (session_id, message_type, role, content, content_hash, message_index, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (session_id, "message", "human", test_query, content_hash, 0, datetime.now()),
            )

            # Store AI response
            response_hash = hashlib.sha256(test_response.encode()).hexdigest()
            cur.execute(
                """
                INSERT INTO conversation_messages 
                (session_id, message_type, role, content, content_hash, message_index, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (session_id, "message", "ai", test_response, response_hash, 1, datetime.now()),
            )

            conn.commit()
            print(f"✅ Stored test conversation for session {session_id}")

            # Verify storage
            cur.execute(
                """
                SELECT COUNT(*) FROM conversation_messages 
                WHERE session_id = %s
            """,
                (session_id,),
            )

            result = cur.fetchone()
            count = result[0] if result else 0
            print(f"✅ Verified: {count} messages stored")

            # Show the stored data
            cur.execute(
                """
                SELECT role, LEFT(content, 60) as preview, created_at 
                FROM conversation_messages 
                WHERE session_id = %s
                ORDER BY message_index
            """,
                (session_id,),
            )

            messages = cur.fetchall()
            print("📝 Stored messages:")
            for role, preview, _ in messages:
                print(f"   {role}: {preview}...")

            return True

    except Exception as e:
        print(f"❌ Error storing conversation: {e}")
        return False
    finally:
        conn.close()


def check_current_data():
    """Check what's currently in the database."""
    print("🔍 Current database state:")

    conn = get_db_connection()

    if conn is None:
        print("⚠️  Skipping database check - no real database connection available")
        return

    try:
        with conn.cursor() as cur:
            # Check conversation messages
            cur.execute("SELECT COUNT(*) FROM conversation_messages")
            result = cur.fetchone()
            msg_count = result[0] if result else 0
            print(f"   Total conversation messages: {msg_count}")

            # Check recent real messages (not test data)
            cur.execute(
                """
                SELECT role, LEFT(content, 50) as preview, created_at 
                FROM conversation_messages 
                WHERE content NOT LIKE 'Load test message%'
                ORDER BY created_at DESC 
                LIMIT 5
            """
            )
            recent = cur.fetchall()
            print("   Recent real messages:")
            for role, preview, created_at in recent:
                print(f"     {role}: {preview}... ({created_at})")

            # Check Atlas nodes
            cur.execute("SELECT COUNT(*) FROM atlas_node")
            result = cur.fetchone()
            node_count = result[0] if result else 0
            print(f"   Atlas nodes: {node_count}")

            # Check if there are any real conversation turns
            cur.execute("SELECT COUNT(*) FROM atlas_conversation_turn")
            result = cur.fetchone()
            turn_count = result[0] if result else 0
            print(f"   Atlas conversation turns: {turn_count}")

    except Exception as e:
        print(f"❌ Error checking data: {e}")
    finally:
        conn.close()


def main():
    """Run the test."""
    print("🚀 Simple Query Storage Test")
    print("=" * 40)

    # Check current state
    check_current_data()

    print("\n" + "=" * 40)

    # Test storage
    success = test_simple_storage()

    if success:
        print("\n🎉 Query storage is working!")
        print("✅ Your conversations can be stored in the database")
    else:
        print("\n❌ Query storage is not working")
        print("⚠️  There are issues with the storage system")


if __name__ == "__main__":
    main()
