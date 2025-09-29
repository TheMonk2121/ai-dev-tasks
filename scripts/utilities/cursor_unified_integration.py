#!/usr/bin/env python3
"""
Unified Cursor AI integration system.
Combines real-time capture, memory consolidation, and Atlas graph storage.
"""

import json
import os
import sys
from typing import Any, cast

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from psycopg.rows import dict_row

from src.common.db_dsn import resolve_dsn
from src.common.psycopg3_config import Psycopg3Config

from .cursor_memory_integration import CursorMemoryIntegration
from .cursor_realtime_capture import CursorRealtimeCapture


class CursorUnifiedIntegration:
    """Unified integration system for Cursor AI conversations."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn: str = dsn or resolve_dsn()
        self.capture: CursorRealtimeCapture = CursorRealtimeCapture(self.dsn)
        self.memory: CursorMemoryIntegration = CursorMemoryIntegration(self.dsn)
        self.auto_consolidate: bool = True
        self.consolidation_threshold: int = 3  # Process after 3 turns

        print("🚀 Cursor Unified Integration initialized")
        print(f"   Session ID: {self.capture.session_id}")
        print(f"   Thread ID: {self.capture.thread_id}")
        print(f"   Auto-consolidation: {'ON' if self.auto_consolidate else 'OFF'}")

    def capture_user_query(self, query: str, metadata: dict[str, Any] | None = None) -> str | None:
        """Capture a user query with full processing."""
        print("👤 Capturing user query...")

        # Capture the query
        turn_id = self.capture.capture_user_query(query, metadata)

        if turn_id and self.auto_consolidate:
            # Check if we should run consolidation
            stats = self.capture.get_session_stats()
            turn_count = stats.get("turn_count", 0)
            if isinstance(turn_count, int | float) and turn_count >= self.consolidation_threshold:
                print("🧠 Running memory consolidation...")
                _ = self.memory.process_conversation_turns(self.capture.thread_id, self.capture.session_id)

        return turn_id

    def capture_ai_response(
        self,
        response: str,
        query_turn_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str | None:
        """Capture an AI response with full processing."""
        print("🤖 Capturing AI response...")

        # Capture the response
        turn_id = self.capture.capture_ai_response(response, query_turn_id, metadata)

        if turn_id and self.auto_consolidate:
            # Check if we should run consolidation
            stats = self.capture.get_session_stats()
            turn_count = stats.get("turn_count", 0)
            if isinstance(turn_count, int | float) and turn_count >= self.consolidation_threshold:
                print("🧠 Running memory consolidation...")
                _ = self.memory.process_conversation_turns(self.capture.thread_id, self.capture.session_id)

        return turn_id

    def process_conversation_turn(self, role: str, content: str, metadata: dict[str, Any] | None = None) -> str | None:
        """Process a conversation turn with full integration."""
        if role.lower() in ["user", "human"]:
            return self.capture_user_query(content, metadata)
        elif role.lower() in ["ai", "assistant"]:
            return self.capture_ai_response(content, None, metadata)
        else:
            print(f"⚠️  Unknown role: {role}")
            return None

    def force_consolidation(self) -> dict[str, object]:
        """Force memory consolidation for current thread."""
        print("🧠 Forcing memory consolidation...")
        return self.memory.process_conversation_turns(self.capture.thread_id, self.capture.session_id)

    def get_session_insights(self) -> dict[str, object]:
        """Get comprehensive session insights."""
        # Get basic stats
        stats = self.capture.get_session_stats()

        # Get thread insights
        thread_insights = self.memory.get_thread_insights(self.capture.thread_id)

        # Combine insights
        insights: dict[str, object] = {
            "session": stats,
            "thread": thread_insights,
            "consolidation_enabled": self.auto_consolidate,
            "consolidation_threshold": self.consolidation_threshold,
        }

        return insights

    def get_recent_conversation(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent conversation turns."""
        try:
            config = Psycopg3Config()
            with config.get_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(
                        """
                        SELECT role, content, created_at, metadata
                        FROM conversation_messages 
                        WHERE session_id = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                    """,
                        (self.capture.session_id, limit),
                    )

                    turns = []
                    for row in cur.fetchall():
                        role = row.get("role")
                        content = row.get("content")
                        created_at = row.get("created_at")
                        metadata = row.get("metadata")
                        
                        role_str = cast(str, role) if role is not None else ""
                        content_str = cast(str, content) if content is not None else ""

                        created_at_str: str | None = None
                        if created_at and hasattr(created_at, "isoformat"):
                            created_at_str = str(created_at.isoformat())

                        metadata_dict: dict[str, object] = {}
                        if metadata and isinstance(metadata, str):
                            try:
                                metadata_dict = json.loads(metadata)
                            except (json.JSONDecodeError, TypeError):
                                metadata_dict = {}

                        turns.append(
                            {
                                "role": role_str,
                                "content": content_str,
                                "created_at": created_at_str,
                                "metadata": metadata_dict,
                            }
                        )

                    return turns

        except Exception as e:
            print(f"❌ Error getting recent conversation: {e}")
            return []

    def search_conversation(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search conversation history using vector similarity."""
        try:
            from sentence_transformers import SentenceTransformer

            embedder = SentenceTransformer("all-MiniLM-L6-v2")
            query_embedding = embedder.encode(query).tolist()

            config = Psycopg3Config()
            with config.get_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(
                        """
                        SELECT role, content, created_at, 
                               1 - (embedding <=> %s) as similarity
                        FROM conversation_messages 
                        WHERE session_id = %s
                        ORDER BY embedding <=> %s
                        LIMIT %s
                    """,
                        (query_embedding, self.capture.session_id, query_embedding, limit),
                    )

                    results = []
                    for row in cur.fetchall():
                        role = row.get("role")
                        content = row.get("content")
                        created_at = row.get("created_at")
                        similarity = row.get("similarity")
                        
                        role_str = cast(str, role) if role is not None else ""
                        content_str = cast(str, content) if content is not None else ""

                        created_at_str: str | None = None
                        if created_at and hasattr(created_at, "isoformat"):
                            created_at_str = str(created_at.isoformat())

                        similarity_float = 0.0
                        if similarity is not None:
                            try:
                                similarity_float = float(similarity)
                            except (ValueError, TypeError):
                                similarity_float = 0.0

                        results.append(
                            {
                                "role": role_str,
                                "content": content_str,
                                "created_at": created_at_str,
                                "similarity": similarity_float,
                            }
                        )

                    return results

        except Exception as e:
            print(f"❌ Error searching conversation: {e}")
            return []

    def close_session(self) -> None:
        """Close the current session."""
        self.capture.close_session()
        print("✅ Session closed")


def main() -> None:
    """Test the unified integration system."""
    print("🚀 Testing Cursor Unified Integration System")
    print("=" * 60)

    # Initialize unified integration
    integration = CursorUnifiedIntegration()

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

    # Force consolidation
    print("\n🧠 Forcing memory consolidation...")
    _ = integration.force_consolidation()

    # Get session insights
    print("\n📊 Getting session insights...")
    insights = integration.get_session_insights()
    session_stats = insights.get("session", {})
    thread_insights = insights.get("thread", {})
    print(f"Session Stats: {session_stats}")
    print(f"Thread Insights: {thread_insights}")

    # Get recent conversation
    print("\n💬 Recent conversation:")
    recent = integration.get_recent_conversation(3)
    for turn in recent:
        role = turn.get("role", "")
        content = turn.get("content", "")
        if isinstance(role, str) and isinstance(content, str):
            print(f"   {role}: {content[:60]}...")
        else:
            print(f"   {role}: {content}")

    # Search conversation
    print("\n🔍 Searching conversation for 'JWT':")
    search_results = integration.search_conversation("JWT", 2)
    for result in search_results:
        role = result.get("role", "")
        content = result.get("content", "")
        similarity = result.get("similarity", 0.0)
        if isinstance(role, str) and isinstance(content, str) and isinstance(similarity, int | float):
            print(f"   {role}: {content[:60]}... (similarity: {similarity:.3f})")
        else:
            print(f"   {role}: {content} (similarity: {similarity})")

    # Close session
    integration.close_session()

    print("\n🎉 Unified integration system test completed!")


if __name__ == "__main__":
    main()
