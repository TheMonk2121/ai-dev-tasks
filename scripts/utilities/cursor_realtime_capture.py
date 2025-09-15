#!/usr/bin/env python3
"""
Real-time conversation capture system for Cursor AI sessions.
Integrates with Atlas graph system and memory consolidation.
"""

import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime

import psycopg2
from sentence_transformers import SentenceTransformer

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.db_dsn import resolve_dsn

# JSON-like typing that avoids Any
JSONScalar = str | int | float | bool | None
JSONValue = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]


class CursorRealtimeCapture:
    """Real-time conversation capture system for Cursor AI."""

    def __init__(self, dsn: str | None = None):
        self.dsn: str = dsn if dsn is not None else resolve_dsn()
        self.embedder: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")
        self.embedding_dim: int = 384
        self.session_id: str = f"cursor_session_{int(time.time())}"
        self.thread_id: str = f"thread_{uuid.uuid4().hex[:8]}"
        self.message_index: int = 0

        # Initialize database
        self._init_database()

        print("🚀 Cursor Realtime Capture initialized")
        print(f"   Session ID: {self.session_id}")
        print(f"   Thread ID: {self.thread_id}")

    def _init_database(self) -> None:
        """Initialize database connection and create session."""
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

    def capture_user_query(self, query: str, metadata: dict[str, JSONValue] | None = None) -> str | None:
        """Capture a user query with full processing."""
        print(f"📝 Capturing user query: {query[:50]}...")

        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
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
        metadata: dict[str, JSONValue] | None = None,
    ) -> str | None:
        """Capture an AI response with full processing."""
        print(f"🤖 Capturing AI response: {response[:50]}...")

        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
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
                            (edge_id, source_node_id, target_node_id, edge_type, weight, metadata, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (edge_id) DO NOTHING
                        """,
                            (
                                f"edge_{query_turn_id}_{turn_id}",
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

    def process_conversation_turn(
        self, role: str, content: str, metadata: dict[str, JSONValue] | None = None
    ) -> str | None:
        """Process a conversation turn (user query or AI response)."""
        if role.lower() in ["user", "human"]:
            return self.capture_user_query(content, metadata)
        elif role.lower() in ["ai", "assistant", "assistant"]:
            return self.capture_ai_response(content, metadata=metadata)
        else:
            print(f"⚠️  Unknown role: {role}")
            return None

    def get_session_stats(self) -> dict[str, JSONValue]:
        """Get current session statistics."""
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    # Get message count
                    cur.execute(
                        """
                        SELECT COUNT(*) FROM conversation_messages 
                        WHERE session_id = %s
                    """,
                        (self.session_id,),
                    )
                    row = cur.fetchone()
                    message_count = row[0] if row is not None else 0

                    # Get turn count
                    cur.execute(
                        """
                        SELECT COUNT(*) FROM atlas_conversation_turn 
                        WHERE thread_id = %s
                    """,
                        (self.thread_id,),
                    )
                    row = cur.fetchone()
                    turn_count = row[0] if row is not None else 0

                    # Get node count
                    cur.execute(
                        """
                        SELECT COUNT(*) FROM atlas_node 
                        WHERE session_id = %s
                    """,
                        (self.session_id,),
                    )
                    row = cur.fetchone()
                    node_count = row[0] if row is not None else 0

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

    def close_session(self):
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


def main():
    """Test the real-time capture system."""
    print("🚀 Testing Cursor Realtime Capture System")
    print("=" * 50)

    # Initialize capture system
    capture = CursorRealtimeCapture()

    # Test conversation
    print("\n📝 Testing conversation capture...")

    # Capture user query
    query_turn_id = capture.capture_user_query(
        "How do I implement user authentication in FastAPI with JWT tokens?", {"test": True, "topic": "authentication"}
    )

    # Capture AI response
    _response_turn_id = capture.capture_ai_response(
        "To implement user authentication in FastAPI with JWT tokens, you'll need to use libraries like python-jose and passlib for JWT handling and password hashing. Here's a step-by-step guide...",
        query_turn_id,
        {"test": True, "response_type": "tutorial"},
    )

    # Get session stats
    stats = capture.get_session_stats()
    print("\n📊 Session Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Close session
    capture.close_session()

    print("\n🎉 Real-time capture system test completed!")


if __name__ == "__main__":
    main()
