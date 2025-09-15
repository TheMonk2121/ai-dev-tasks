#!/usr/bin/env python3
"""
Test script to verify query storage is working properly.
"""

import os
import sys
from datetime import datetime

import psycopg2


def get_db_connection():
    """Get database connection."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
    from src.common.db_dsn import resolve_dsn

    dsn = resolve_dsn()
    return psycopg2.connect(dsn)


def test_conversation_storage():
    """Test storing a conversation turn."""
    print("🧪 Testing conversation storage...")

    conn = get_db_connection()

    # Test data
    session_id = f"test_session_{int(datetime.now().timestamp())}"
    test_query = "How do I implement user authentication in FastAPI with JWT tokens?"
    test_response = "To implement user authentication in FastAPI with JWT tokens, you'll need to..."

    try:
        with conn.cursor() as cur:
            # Store user query
            cur.execute(
                """
                INSERT INTO conversation_messages (session_id, role, content, created_at)
                VALUES (%s, %s, %s, %s)
            """,
                (session_id, "human", test_query, datetime.now()),
            )

            # Store AI response
            cur.execute(
                """
                INSERT INTO conversation_messages (session_id, role, content, created_at)
                VALUES (%s, %s, %s, %s)
            """,
                (session_id, "ai", test_response, datetime.now()),
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
            if result is None:
                print("❌ No results returned from count query")
                return False

            count = result[0]
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
        test_content = "This is a test query for Atlas storage verification"

        result = atlas.store_conversation_turn(
            session_id=session_id, role="user", content=test_content, metadata={"test": True}
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
        # Import memory consolidation
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "memory_graphs"))
        from consolidate import consolidate_memory

        # Test conversation turns
        turns = [
            {
                "role": "user",
                "content": "How do I implement authentication in FastAPI?",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "role": "assistant",
                "content": "To implement authentication in FastAPI, you need to use JWT tokens and bcrypt for password hashing.",
                "timestamp": datetime.now().isoformat(),
            },
        ]

        result = consolidate_memory(turns)

        if result and result.summary:
            print("✅ Memory consolidation successful")
            print(f"   Summary: {result.summary[:100]}...")
            print(f"   Facts extracted: {len(result.facts)}")
            print(f"   Entities found: {len(result.entities)}")
            return True
        else:
            print("❌ Memory consolidation failed")
            return False

    except Exception as e:
        print(f"❌ Error testing memory consolidation: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Testing Query Storage Systems")
    print("=" * 50)

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
