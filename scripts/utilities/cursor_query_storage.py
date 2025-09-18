#!/usr/bin/env python3
"""
Cursor Query Storage Integration
Stores Cursor conversations in the 48-hour conv_chunks table
"""

import os

# Add project paths
import sys
import time
from datetime import datetime, timedelta
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from sentence_transformers import SentenceTransformer

from src.common.psycopg3_config import Psycopg3Config


class CursorQueryStorage:
    """Stores and retrieves Cursor conversation queries with 48-hour retention."""

    dsn: str
    embedder: SentenceTransformer
    embedding_dim: int

    def __init__(self, dsn: str | None = None) -> None:
        resolved_dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
        if dsn is not None:
            self.dsn = dsn
        else:
            self.dsn = resolved_dsn
        # Follow project embedding rules: BAAI/bge-large-en-v1.5 with 1024 dimensions
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.embedding_dim = 384  # Project standard

    def store_conversation_turn(
        self,
        session_id: str,
        _role: str,
        content: str,
        _metadata: dict[str, str | int | float | bool | None] | None = None,
    ) -> str | None:
        """Store a single conversation turn in conv_chunks."""
        try:
            # Generate embedding
            embedding = self.embedder.encode(content).tolist()

            # Extract entities (simple keyword extraction)
            entities: Any = self._extract_entities(content)

            # Calculate salience score (simple length-based for now)
            salience_score = min(len(content) / 1000.0, 1.0)

            # Set expiration to 48 hours from now
            expires_at = datetime.now() + timedelta(hours=48)

            with Psycopg3Config.get_cursor("default") as _:
                _.execute(
                    """
                    INSERT INTO conv_chunks 
                    (session_id, chunk_text, embedding, entities, salience_score, 
                     source_turn_id, expires_at, is_pinned)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """,
                    (
                        session_id,
                        content,
                        embedding,
                        entities,
                        salience_score,
                        int(time.time() * 1000),  # source_turn_id
                        expires_at,
                        False,
                    ),
                )

                result: Any = _.fetchone()
                if result is None:
                    raise ValueError("Failed to get chunk ID from database")
                chunk_id: int = result[0]  # type: ignore[assignment, misc]

            print(f"✅ Stored conversation turn {chunk_id} for session {session_id}")
            return str(chunk_id)

        except Exception as e:
            print(f"❌ Error storing conversation turn: {e}")
            return None

    def retrieve_recent_queries(
        self, session_id: str | None = None, limit: int = 10
    ) -> list[dict[str, str | int | float | bool | None]]:
        """Retrieve recent queries from conv_chunks."""
        try:
            with Psycopg3Config.get_cursor("default") as _:
                    if session_id:
                        _.execute(
                            """
                            SELECT id, session_id, chunk_text, salience_score, 
                                   created_at, expires_at, is_pinned
                            FROM conv_chunks 
                            WHERE session_id = %s AND expires_at > NOW()
                            ORDER BY created_at DESC 
                            LIMIT %s
                        """,
                            (session_id, limit),
                        )
                    else:
                        _.execute(
                            """
                            SELECT id, session_id, chunk_text, salience_score, 
                                   created_at, expires_at, is_pinned
                            FROM conv_chunks 
                            WHERE expires_at > NOW()
                            ORDER BY created_at DESC 
                            LIMIT %s
                        """,
                            (limit,),
                        )

                    results: Any = _.fetchall()
                    return [dict(row) for row in results]

        except Exception as e:
            print(f"❌ Error retrieving queries: {e}")
            return []

    def cleanup_expired_chunks(self) -> int:
        """Clean up expired chunks and return count deleted."""
        try:
            with Psycopg3Config.get_cursor("default") as _:
                _.execute("SELECT cleanup_expired_chunks()")
                result: Any = _.fetchone()
                if result is None:
                    raise ValueError("Failed to get cleanup count from database")
                deleted_count: int = result[0]  # type: ignore[assignment, misc]

            print(f"🧹 Cleaned up {deleted_count} expired chunks")
            return deleted_count

        except Exception as e:
            print(f"❌ Error cleaning up expired chunks: {e}")
            return 0

    def _extract_entities(self, text: str) -> list[str]:
        """Simple entity extraction - look for CamelCase, file paths, etc."""
        import re

        entities = []

        # CamelCase words
        camel_case = re.findall(r"[A-Z][a-z]+(?:[A-Z][a-z]+)*", text)
        entities.extend(camel_case)

        # File paths
        file_paths = re.findall(r"[a-zA-Z0-9_/.-]+\.(?:py|md|json|yaml|yml|sql|sh)", text)
        entities.extend(file_paths)

        # Function names (snake_case)
        functions: Any = re.findall(r"[a-z_]+\(", text)
        entities.extend([str(f).rstrip("(") for f in functions])  # type: ignore[misc]

        return list(set(entities))  # Remove duplicates

    def get_storage_stats(self) -> dict[str, str | int | None]:
        """Get statistics about stored conversations."""
        try:
            with Psycopg3Config.get_cursor("default") as _:
                # Total chunks
                _.execute("SELECT COUNT(*) FROM conv_chunks")
                result: Any = _.fetchone()
                if result is None:
                    raise ValueError("Failed to get total chunks count")
                total_chunks: int = result[0]  # type: ignore[assignment, misc]

                # Active chunks (not expired)
                _.execute("SELECT COUNT(*) FROM conv_chunks WHERE expires_at > NOW()")
                active_result: Any = _.fetchone()
                if active_result is None:
                    raise ValueError("Failed to get active chunks count")
                active_chunks: int = active_result[0]  # type: ignore[assignment, misc]

                # Sessions
                _.execute("SELECT COUNT(DISTINCT session_id) FROM conv_chunks")
                sessions_result: Any = _.fetchone()
                if sessions_result is None:
                    raise ValueError("Failed to get unique sessions count")
                unique_sessions: int = sessions_result[0]  # type: ignore[assignment, misc]

                # Oldest and newest
                _.execute(
                    """
                    SELECT MIN(created_at), MAX(created_at) 
                    FROM conv_chunks WHERE expires_at > NOW()
                """
                )
                date_result: Any = _.fetchone()
                if date_result is None:
                    oldest: datetime | None = None
                    newest: datetime | None = None
                else:
                    oldest, newest = date_result  # type: ignore[assignment, misc]

                return {
                    "total_chunks": total_chunks,
                    "active_chunks": active_chunks,
                    "unique_sessions": unique_sessions,
                    "oldest_chunk": oldest.isoformat() if oldest is not None else None,
                    "newest_chunk": newest.isoformat() if newest is not None else None,
                }

        except Exception as e:
            print(f"❌ Error getting storage stats: {e}")
            return {}


def main() -> Any:
    """Test the Cursor query storage system."""
    storage = CursorQueryStorage()

    # Test storing a conversation
    test_session = f"test_session_{int(time.time())}"
    test_content = "This is a test query to verify the 48-hour storage system is working."

    print("🧪 Testing Cursor Query Storage...")

    # Store test conversation
    chunk_id = storage.store_conversation_turn(
        session_id=test_session, _role="human", content=test_content, _metadata={"test": True}
    )

    if chunk_id:
        print(f"✅ Test conversation stored with ID: {chunk_id}")

        # Retrieve recent queries
        recent: Any = storage.retrieve_recent_queries(limit=5)
        print(f"📊 Retrieved {len(recent)} recent queries")

        # Get storage stats
        stats: Any = storage.get_storage_stats()
        print(f"📈 Storage stats: {stats}")

        # Clean up expired chunks
        cleaned: Any = storage.cleanup_expired_chunks()
        print(f"🧹 Cleaned up {cleaned} expired chunks")

    else:
        print("❌ Failed to store test conversation")


if __name__ == "__main__":
    main()
