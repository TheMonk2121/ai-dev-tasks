#!/usr/bin/env python3
"""
Test script to verify query storage is working with the actual database schema.
"""

import hashlib
import os
import sys
from collections.abc import Sequence
from datetime import datetime
from typing import cast

import psycopg2


def get_db_connection():
    """Get database connection."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
    from src.common.db_dsn import resolve_dsn

    dsn = resolve_dsn()
    return psycopg2.connect(dsn)


def test_conversation_storage():
    """Test storing a conversation turn with proper schema."""
    print("🧪 Testing conversation storage...")

    conn = get_db_connection()

    # Test data
    session_id = f"test_session_{int(datetime.now().timestamp())}"
    test_query = "How do I implement user authentication in FastAPI with JWT tokens?"
    test_response = "To implement user authentication in FastAPI with JWT tokens, you'll need to use libraries like python-jose and passlib for JWT handling and password hashing."

    try:
        with conn.cursor() as cur:
            # First create a session
            cur.execute(
                """
                INSERT INTO conversation_sessions (session_id, created_at, last_accessed, metadata)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (session_id) DO NOTHING
            """,
                (session_id, datetime.now(), datetime.now(), "{}"),
            )

            # Store user query with proper schema
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

            row = cur.fetchone()
            count = int(cast(int, row[0])) if row is not None else 0
            print(f"✅ Verified: {count} messages stored")

            return True

    except Exception as e:
        print(f"❌ Error storing conversation: {e}")
        return False
    finally:
        conn.close()


def test_atlas_storage():
    """Test storing in Atlas system."""
    print("🧪 Testing Atlas storage...")

    try:
        # Import the Atlas integration
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utilities"))
        from cursor_atlas_integration import CursorAtlasIntegration

        atlas = CursorAtlasIntegration()

        # Test conversation turn
        session_id = f"atlas_test_{int(datetime.now().timestamp())}"
        test_content = "This is a test query for Atlas storage verification with FastAPI authentication"

        result = atlas.store_conversation_turn(
            session_id=session_id,
            role="user",
            content=test_content,
            metadata={"test": True, "timestamp": datetime.now().isoformat()},
        )

        if result:
            print(f"✅ Atlas storage successful: {result}")
            return True
        else:
            print("❌ Atlas storage failed")
            return False

    except Exception as e:
        print(f"❌ Error testing Atlas storage: {e}")
        return False


def test_memory_consolidation():
    """Test memory consolidation system."""
    print("🧪 Testing memory consolidation...")

    try:
        # Set environment variable for memory graph
        os.environ["APP_USE_MEMORY_GRAPH"] = "true"

        # Import memory consolidation
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "memory_graphs"))
        from consolidate import consolidate_memory

        # Test conversation turns
        turns = [
            {
                "role": "user",
                "content": "How do I implement authentication in FastAPI with JWT tokens?",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "role": "assistant",
                "content": "To implement authentication in FastAPI, you need to use JWT tokens and bcrypt for password hashing. Install python-jose and passlib libraries.",
                "timestamp": datetime.now().isoformat(),
            },
        ]

        result = consolidate_memory(turns)

        if result and result.summary:
            print("✅ Memory consolidation successful")
            print(f"   Summary: {result.summary[:100]}...")
            print(f"   Facts extracted: {len(result.facts)}")
            print(f"   Entities found: {len(result.entities)}")
            if result.facts:
                print(f"   Sample fact: {result.facts[0].content}")
            if result.entities:
                print(f"   Sample entity: {result.entities[0].name}")
            return True
        else:
            print("❌ Memory consolidation failed")
            return False

    except Exception as e:
        print(f"❌ Error testing memory consolidation: {e}")
        return False


def check_current_storage():
    """Check what's currently stored in the database."""
    print("🔍 Checking current storage...")

    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            # Check conversation messages
            cur.execute("SELECT COUNT(*) FROM conversation_messages")
            row = cur.fetchone()
            msg_count = int(cast(int, row[0])) if row is not None else 0
            print(f"   Conversation messages: {msg_count}")

            # Check recent messages
            cur.execute(
                """
                SELECT role, LEFT(content, 50) as preview, created_at 
                FROM conversation_messages 
                ORDER BY created_at DESC 
                LIMIT 3
            """
            )
            recent = cur.fetchall()
            recent_typed = cast(Sequence[tuple[str, str, object]], recent)
            print("   Recent messages:")
            for role, preview, created_at in recent_typed:
                print(f"     {role}: {preview}... ({created_at})")

            # Check Atlas nodes
            cur.execute("SELECT COUNT(*) FROM atlas_node")
            row = cur.fetchone()
            node_count = int(cast(int, row[0])) if row is not None else 0
            print(f"   Atlas nodes: {node_count}")

            # Check conv_chunks
            cur.execute("SELECT COUNT(*) FROM conv_chunks")
            row = cur.fetchone()
            chunk_count = int(cast(int, row[0])) if row is not None else 0
            print(f"   Conversation chunks: {chunk_count}")

    except Exception as e:
        print(f"❌ Error checking storage: {e}")
    finally:
        conn.close()


def main():
    """Run all tests."""
    print("🚀 Testing Query Storage Systems")
    print("=" * 50)

    # First check current state
    check_current_storage()

    tests = [
        ("Basic Conversation Storage", test_conversation_storage),
        ("Atlas Storage", test_atlas_storage),
        ("Memory Consolidation", test_memory_consolidation),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")

    all_passed = all(success for _, success in results)
    if all_passed:
        print("\n🎉 All tests passed! Query storage is working.")
    else:
        print("\n⚠️  Some tests failed. Query storage needs attention.")


if __name__ == "__main__":
    main()
