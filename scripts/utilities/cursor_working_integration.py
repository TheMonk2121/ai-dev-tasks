#!/usr/bin/env python3
"""
Working Cursor AI integration system.
Handles sequence issues and provides real-time conversation capture.
"""

import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime

# from typing import Any  # Unused import removed
import psycopg2
from sentence_transformers import SentenceTransformer

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.db_dsn import resolve_dsn


class CursorWorkingIntegration:
    """Working integration system for Cursor AI conversations."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn: str = dsn if dsn is not None else resolve_dsn()
        self.embedder: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")
        self.embedding_dim: int = 384
        self.session_id: str = f"cursor_session_{int(time.time())}"
        self.thread_id: str = f"thread_{uuid.uuid4().hex[:8]}"
        self.message_index: int = 0
        self.is_mock: bool = self.dsn.startswith("mock://")

        # Initialize database
        self._init_database()

        print("🚀 Cursor Working Integration initialized")
        print(f"   Session ID: {self.session_id}")
        print(f"   Thread ID: {self.thread_id}")

    def _init_database(self) -> None:
        """Initialize database connection and create session."""
        if self.is_mock:
            print("⚠️  Mock database detected - skipping real database operations")
            return

        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    # Create session
                    cur.execute(
                        """
                        INSERT INTO conversation_sessions 
                        (session_id, user_id, session_name, session_type, status, created_at, last_activity, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (session_id) DO UPDATE SET
                            last_activity = EXCLUDED.last_activity,
                            updated_at = CURRENT_TIMESTAMP
                    """,
                        (
                            self.session_id,
                            "cursor_user",
                            f"Cursor Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                            "cursor_ai",
                            "active",
                            datetime.now(),
                            datetime.now(),
                            json.dumps({"capture_type": "realtime", "thread_id": self.thread_id}),
                        ),
                    )

                    # Create thread
                    cur.execute(
                        """
                        INSERT INTO atlas_thread 
                        (thread_id, session_id, tab_id, title, status, embedding, metadata, created_at, last_activity)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (thread_id) DO UPDATE SET
                            last_activity = EXCLUDED.last_activity
                    """,
                        (
                            self.thread_id,
                            self.session_id,
                            "cursor_tab",
                            f"Cursor Conversation {datetime.now().strftime('%H:%M')}",
                            "active",
                            self.embedder.encode("").tolist(),
                            json.dumps({"capture_type": "realtime", "session_id": self.session_id}),
                            datetime.now(),
                            datetime.now(),
                        ),
                    )

                    conn.commit()
                    print(f"✅ Database initialized for session {self.session_id}")

        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            raise

    def _ensure_thread_exists(self, thread_id: str) -> bool:
        """Ensure a thread exists in the database, creating it if necessary."""
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    # Check if thread exists
                    cur.execute("SELECT thread_id FROM atlas_thread WHERE thread_id = %s", (thread_id,))
                    if cur.fetchone():
                        print(f"✅ Thread {thread_id} already exists")
                        return True

                    # Create thread with ON CONFLICT DO NOTHING for safety
                    cur.execute(
                        """
                        INSERT INTO atlas_thread 
                        (thread_id, session_id, tab_id, title, status, embedding, metadata, created_at, last_activity)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (thread_id) DO NOTHING
                    """,
                        (
                            thread_id,
                            self.session_id,
                            "cursor_tab",
                            f"Cursor Conversation {datetime.now().strftime('%H:%M')}",
                            "active",
                            self.embedder.encode("").tolist(),
                            json.dumps({"capture_type": "realtime", "session_id": self.session_id}),
                            datetime.now(),
                            datetime.now(),
                        ),
                    )

                    conn.commit()
                    print(f"✅ Created thread {thread_id} in database")
                    return True

        except Exception as e:
            print(f"❌ Failed to ensure thread exists: {e}")
            return False

    def capture_user_query(
        self, query: str, metadata: dict[str, str | int | float | bool | None] | None = None
    ) -> str | None:
        """Capture a user query with full processing."""
        print(f"👤 Capturing user query: {query[:50]}...")

        if self.is_mock:
            # Return a mock turn ID for testing
            turn_id = f"mock_turn_{self.thread_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            print(f"🔍 Mock: Captured user query: {query[:50]}... -> {turn_id}")
            return turn_id

        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    # Start transaction for atomicity
                    cur.execute("BEGIN")

                    # Ensure thread exists before inserting conversation turn
                    cur.execute(
                        """
                        INSERT INTO atlas_thread 
                        (thread_id, session_id, tab_id, title, status, embedding, metadata, created_at, last_activity)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (thread_id) DO UPDATE SET
                            last_activity = EXCLUDED.last_activity
                    """,
                        (
                            self.thread_id,
                            self.session_id,
                            "cursor_tab",
                            f"Cursor Conversation {datetime.now().strftime('%H:%M')}",
                            "active",
                            self.embedder.encode("").tolist(),
                            json.dumps({"capture_type": "realtime", "session_id": self.session_id}),
                            datetime.now(),
                            datetime.now(),
                        ),
                    )

                    # Generate turn ID
                    turn_id = f"turn_{self.thread_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"

                    # Create content hash
                    content_hash = hashlib.sha256(query.encode()).hexdigest()

                    # Generate embedding
                    embedding = self.embedder.encode(query).tolist()

                    # Enhanced metadata
                    enhanced_metadata = {
                        "role": "user",
                        "turn_id": turn_id,
                        "thread_id": self.thread_id,
                        "session_id": self.session_id,
                        "timestamp": datetime.now().isoformat(),
                        "content_length": len(query),
                        "word_count": len(query.split()),
                        "capture_type": "realtime",
                        **(metadata or {}),
                    }

                    # Store in conversation_messages (let the sequence handle the ID)
                    cur.execute(
                        """
                        INSERT INTO conversation_messages 
                        (session_id, message_type, role, content, content_hash, message_index, 
                         metadata, embedding, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                        (
                            self.session_id,
                            "message",
                            "human",
                            query,
                            content_hash,
                            self.message_index,
                            json.dumps(enhanced_metadata),
                            embedding,
                            datetime.now(),
                        ),
                    )

                    # Store in atlas_conversation_turn
                    cur.execute(
                        """
                        INSERT INTO atlas_conversation_turn 
                        (turn_id, thread_id, role, content, timestamp, embedding, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (turn_id) DO UPDATE SET
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata
                    """,
                        (
                            turn_id,
                            self.thread_id,
                            "user",
                            query,
                            datetime.now(),
                            embedding,
                            json.dumps(enhanced_metadata),
                        ),
                    )

                    # Store in atlas_node
                    cur.execute(
                        """
                        INSERT INTO atlas_node 
                        (node_id, node_type, title, content, embedding, metadata, created_at, updated_at, session_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (node_id) DO UPDATE SET
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata,
                            updated_at = EXCLUDED.updated_at
                    """,
                        (
                            turn_id,
                            "conversation",
                            f"User Query: {query[:50]}...",
                            query,
                            embedding,
                            json.dumps(enhanced_metadata),
                            datetime.now(),
                            datetime.now(),
                            self.session_id,
                        ),
                    )

                    # Update thread activity
                    cur.execute(
                        """
                        UPDATE atlas_thread 
                        SET last_activity = NOW()
                        WHERE thread_id = %s
                    """,
                        (self.thread_id,),
                    )

                    # Update session activity
                    cur.execute(
                        """
                        UPDATE conversation_sessions 
                        SET last_activity = NOW(), session_length = session_length + 1
                        WHERE session_id = %s
                    """,
                        (self.session_id,),
                    )

                    conn.commit()
                    self.message_index += 1

                    print(f"✅ User query captured: {turn_id}")
                    return turn_id

        except Exception as e:
            print(f"❌ Error capturing user query: {e}")
            return None

    def capture_ai_response(
        self,
        response: str,
        query_turn_id: str | None = None,
        metadata: dict[str, str | int | float | bool | None] | None = None,
    ) -> str | None:
        """Capture an AI response with full processing."""
        print(f"🤖 Capturing AI response: {response[:50]}...")

        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    # Start transaction for atomicity
                    cur.execute("BEGIN")

                    # Ensure thread exists before inserting conversation turn
                    cur.execute(
                        """
                        INSERT INTO atlas_thread 
                        (thread_id, session_id, tab_id, title, status, embedding, metadata, created_at, last_activity)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (thread_id) DO UPDATE SET
                            last_activity = EXCLUDED.last_activity
                    """,
                        (
                            self.thread_id,
                            self.session_id,
                            "cursor_tab",
                            f"Cursor Conversation {datetime.now().strftime('%H:%M')}",
                            "active",
                            self.embedder.encode("").tolist(),
                            json.dumps({"capture_type": "realtime", "session_id": self.session_id}),
                            datetime.now(),
                            datetime.now(),
                        ),
                    )

                    # Generate turn ID
                    turn_id = f"turn_{self.thread_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"

                    # Create content hash
                    content_hash = hashlib.sha256(response.encode()).hexdigest()

                    # Generate embedding
                    embedding = self.embedder.encode(response).tolist()

                    # Enhanced metadata
                    enhanced_metadata = {
                        "role": "assistant",
                        "turn_id": turn_id,
                        "thread_id": self.thread_id,
                        "session_id": self.session_id,
                        "timestamp": datetime.now().isoformat(),
                        "content_length": len(response),
                        "word_count": len(response.split()),
                        "capture_type": "realtime",
                        "parent_turn_id": query_turn_id,
                        **(metadata or {}),
                    }

                    # Store in conversation_messages
                    cur.execute(
                        """
                        INSERT INTO conversation_messages 
                        (session_id, message_type, role, content, content_hash, message_index, 
                         metadata, embedding, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                        (
                            self.session_id,
                            "message",
                            "ai",
                            response,
                            content_hash,
                            self.message_index,
                            json.dumps(enhanced_metadata),
                            embedding,
                            datetime.now(),
                        ),
                    )

                    # Store in atlas_conversation_turn
                    cur.execute(
                        """
                        INSERT INTO atlas_conversation_turn 
                        (turn_id, thread_id, role, content, timestamp, embedding, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (turn_id) DO UPDATE SET
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata
                    """,
                        (
                            turn_id,
                            self.thread_id,
                            "assistant",
                            response,
                            datetime.now(),
                            embedding,
                            json.dumps(enhanced_metadata),
                        ),
                    )

                    # Store in atlas_node
                    cur.execute(
                        """
                        INSERT INTO atlas_node 
                        (node_id, node_type, title, content, embedding, metadata, created_at, updated_at, session_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (node_id) DO UPDATE SET
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata,
                            updated_at = EXCLUDED.updated_at
                    """,
                        (
                            turn_id,
                            "conversation",
                            f"AI Response: {response[:50]}...",
                            response,
                            embedding,
                            json.dumps(enhanced_metadata),
                            datetime.now(),
                            datetime.now(),
                            self.session_id,
                        ),
                    )

                    # Create edge between query and response
                    if query_turn_id:
                        cur.execute(
                            """
                            INSERT INTO atlas_edge 
                            (source_node_id, target_node_id, edge_type, weight, metadata, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (source_node_id, target_node_id, edge_type) DO NOTHING
                        """,
                            (
                                query_turn_id,
                                turn_id,
                                "responds_to",
                                1.0,
                                json.dumps({"relationship": "query_response", "capture_type": "realtime"}),
                                datetime.now(),
                            ),
                        )

                    # Update thread activity
                    cur.execute(
                        """
                        UPDATE atlas_thread 
                        SET last_activity = NOW()
                        WHERE thread_id = %s
                    """,
                        (self.thread_id,),
                    )

                    # Update session activity
                    cur.execute(
                        """
                        UPDATE conversation_sessions 
                        SET last_activity = NOW(), session_length = session_length + 1
                        WHERE session_id = %s
                    """,
                        (self.session_id,),
                    )

                    conn.commit()
                    self.message_index += 1

                    print(f"✅ AI response captured: {turn_id}")
                    return turn_id

        except Exception as e:
            print(f"❌ Error capturing AI response: {e}")
            return None

    def get_session_stats(self) -> dict[str, str | int | float | bool | None]:
        """Get current session statistics."""
        if self.is_mock:
            # Return mock stats for testing
            return {
                "session_id": self.session_id,
                "thread_id": self.thread_id,
                "message_count": 0,  # Mock doesn't track actual counts
                "turn_count": 0,
                "node_count": 0,
                "status": "mock_mode",
                "last_activity": "mock",
            }

        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    # Get message count from atlas_conversation_turn table
                    cur.execute(
                        """
                        SELECT COUNT(*) FROM atlas_conversation_turn 
                        WHERE thread_id = %s
                    """,
                        (self.thread_id,),
                    )
                    result = cur.fetchone()
                    message_count = result[0] if result else 0

                    # Get turn count (same as message count for this table)
                    turn_count = message_count

                    # Get node count
                    cur.execute(
                        """
                        SELECT COUNT(*) FROM atlas_node 
                        WHERE session_id = %s
                    """,
                        (self.session_id,),
                    )
                    result = cur.fetchone()
                    node_count = result[0] if result else 0

                    return {
                        "session_id": self.session_id,
                        "thread_id": self.thread_id,
                        "message_count": message_count,
                        "turn_count": turn_count,
                        "node_count": node_count,
                        "message_index": self.message_index,
                    }

        except Exception as e:
            print(f"❌ Error getting session stats: {e}")
            return {}

    def get_recent_conversation(self, limit: int = 10) -> list[dict[str, object]]:
        """Get recent conversation turns."""
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT role, content, created_at, metadata
                        FROM conversation_messages 
                        WHERE session_id = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                    """,
                        (self.session_id, limit),
                    )

                    turns = []
                    for row in cur.fetchall():
                        # Extract values with proper type handling
                        role = row[0]
                        content = row[1]
                        created_at = row[2]
                        metadata = row[3]

                        # Convert created_at to string if it's a datetime object
                        created_at_str: str | None = None
                        if created_at is not None:
                            if hasattr(created_at, "isoformat"):
                                created_at_str = created_at.isoformat()
                            else:
                                created_at_str = str(created_at)

                        # Parse metadata safely
                        parsed_metadata: dict[str, object] = {}
                        if metadata is not None:
                            if isinstance(metadata, str):
                                try:
                                    parsed_metadata = json.loads(metadata)
                                except (json.JSONDecodeError, TypeError):
                                    parsed_metadata = {}
                            elif isinstance(metadata, dict):
                                parsed_metadata = metadata

                        turns.append(
                            {
                                "role": str(role) if role is not None else "",
                                "content": str(content) if content is not None else "",
                                "created_at": created_at_str,
                                "metadata": parsed_metadata,
                            }
                        )

                    return turns

        except Exception as e:
            print(f"❌ Error getting recent conversation: {e}")
            return []

    def close_session(self) -> None:
        """Close the current session."""
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    # Update session status
                    cur.execute(
                        """
                        UPDATE conversation_sessions 
                        SET status = 'closed', last_activity = NOW()
                        WHERE session_id = %s
                    """,
                        (self.session_id,),
                    )

                    conn.commit()
                    print(f"✅ Session {self.session_id} closed")

        except Exception as e:
            print(f"❌ Error closing session: {e}")


def main() -> None:
    """Test the working integration system."""
    print("🚀 Testing Cursor Working Integration System")
    print("=" * 60)

    # Initialize integration
    integration = CursorWorkingIntegration()

    # Test conversation flow
    print("\n📝 Testing conversation flow...")

    # User query
    query_turn_id = integration.capture_user_query(
        "How do I implement user authentication in FastAPI with JWT tokens?",
        {"topic": "authentication", "complexity": "intermediate"},
    )

    # AI response
    _ = integration.capture_ai_response(
        "To implement user authentication in FastAPI with JWT tokens, you'll need to use libraries like python-jose and passlib. Here's a step-by-step guide:\n\n1. Install required packages\n2. Create user models\n3. Implement password hashing\n4. Create JWT token functions\n5. Add authentication middleware",
        query_turn_id,
        {"response_type": "tutorial", "steps": 5},
    )

    # Another user query
    query2_turn_id = integration.capture_user_query(
        "What about password reset functionality?", {"topic": "authentication", "follow_up": True}
    )

    # Another AI response
    _ = integration.capture_ai_response(
        "For password reset functionality, you'll need to implement email verification and secure token generation. Here's how to add it to your FastAPI authentication system...",
        query2_turn_id,
        {"response_type": "tutorial", "feature": "password_reset"},
    )

    # Get session stats
    print("\n📊 Getting session stats...")
    stats = integration.get_session_stats()
    print(f"Session Stats: {stats}")

    # Get recent conversation
    print("\n💬 Recent conversation:")
    recent = integration.get_recent_conversation(4)
    for turn in recent:
        content = turn.get("content", "")
        if isinstance(content, str):
            print(f"   {turn['role']}: {content[:60]}...")
        else:
            print(f"   {turn['role']}: {content}")

    # Close session
    integration.close_session()

    print("\n🎉 Working integration system test completed!")
    print("\n✅ Your queries are now being stored in real-time!")


if __name__ == "__main__":
    main()
