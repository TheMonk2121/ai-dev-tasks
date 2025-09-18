#!/usr/bin/env python3
"""
Simple test to verify query storage is working.
"""

import hashlib
import os
import sys
from datetime import datetime
from typing import Any

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.psycopg3_config import Psycopg3Config


def get_db_connection() -> Any:
    """Get database connection."""
    # Handle mock database case
    try:
        with Psycopg3Config.get_cursor("default") as cur:
            # Test connection
            cur.execute("SELECT 1")
            return cur
    except Exception as e:
        if "mock" in str(e).lower():
            print("⚠️  Mock database detected - skipping real database operations")
            return None
        raise e


def test_simple_storage() -> Any:
    """Test storing a simple conversation."""
    print("🧪 Testing simple conversation storage...")

    # Test data
    session_id = f"test_session_{int(datetime.now().timestamp())}"
    user_id = "test_user"
    test_query = "How do I implement user authentication in FastAPI with JWT tokens?"
    test_response = "To implement user authentication in FastAPI with JWT tokens, you'll need to use libraries like python-jose and passlib."

    try:
        with Psycopg3Config.get_cursor("default") as cur:
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

            print(f"✅ Stored test conversation for session {session_id}")

            # Verify storage
            cur.execute(
                """
                SELECT COUNT(*) FROM conversation_messages 
                WHERE session_id = %s
            """,
                (session_id,),
            )

            result: dict[str, Any] | None = cur.fetchone()
            count = result["count"] if result else 0
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

            messages: list[dict[str, Any]] = cur.fetchall()
            print("📝 Stored messages:")
            for row in messages:
                print(f"   {row['role']}: {row['preview']}...")

            return True

    except Exception as e:
        print(f"❌ Error storing conversation: {e}")
        return False


def check_current_data() -> Any:
    """Check what's currently in the database."""
    print("🔍 Current database state:")

    try:
        with Psycopg3Config.get_cursor("default") as cur:
            # Check conversation messages
            cur.execute("SELECT COUNT(*) FROM conversation_messages")
            result: dict[str, Any] | None = cur.fetchone()
            msg_count = result["count"] if result else 0
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
            recent: list[dict[str, Any]] = cur.fetchall()
            print("   Recent real messages:")
            for row in recent:
                print(f"     {row['role']}: {row['preview']}... ({row['created_at']})")

            # Check Atlas nodes
            cur.execute("SELECT COUNT(*) FROM atlas_node")
            result: dict[str, Any] | None = cur.fetchone()
            node_count = result["count"] if result else 0
            print(f"   Atlas nodes: {node_count}")

            # Check if there are any real conversation turns
            cur.execute("SELECT COUNT(*) FROM atlas_conversation_turn")
            result: dict[str, Any] | None = cur.fetchone()
            turn_count = result["count"] if result else 0
            print(f"   Atlas conversation turns: {turn_count}")

    except Exception as e:
        print(f"❌ Error checking data: {e}")


def main() -> Any:
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
