"""
Conversation Storage System for LTST Memory

This module provides efficient conversation storage and retrieval capabilities
for the LTST Memory System, including metadata management and vector search.
"""

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from psycopg2.extras import RealDictCursor

from .database_resilience import DatabaseResilienceManager as DatabaseManager
from .logger import setup_logger
from .prompt_sanitizer import sanitize_prompt

logger = setup_logger(__name__)


@dataclass
class ConversationMessage:
    """Represents a conversation message with metadata."""

    session_id: str
    role: str  # 'human', 'ai', 'system'
    content: str
    message_type: str = "message"  # 'message', 'system', 'context', 'preference'
    message_index: Optional[int] = None
    parent_message_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    embedding: Optional[List[float]] = None
    relevance_score: float = 0.0
    is_context_message: bool = False
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}
        if self.embedding is None:
            self.embedding = []

    @property
    def content_hash(self) -> str:
        """Generate content hash for deduplication."""
        return hashlib.sha256(self.content.encode()).hexdigest()

    @property
    def context_hash(self) -> str:
        """Generate context hash for relationships."""
        context_data = f"{self.session_id}:{self.role}:{self.content_hash}"
        return hashlib.sha256(context_data.encode()).hexdigest()


@dataclass
class ConversationSession:
    """Represents a conversation session."""

    session_id: str
    user_id: str
    session_name: Optional[str] = None
    session_type: str = "conversation"
    status: str = "active"
    metadata: Optional[Dict[str, Any]] = None
    context_summary: Optional[str] = None
    relevance_score: float = 0.0
    created_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ConversationContext:
    """Represents conversation context."""

    session_id: str
    context_type: str  # 'conversation', 'preference', 'project', 'user_info'
    context_key: str
    context_value: str
    relevance_score: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.metadata is None:
            self.metadata = {}

    @property
    def context_hash(self) -> str:
        """Generate context hash for deduplication."""
        context_data = f"{self.session_id}:{self.context_type}:{self.context_key}:{self.context_value}"
        return hashlib.sha256(context_data.encode()).hexdigest()


class ConversationStorage:
    """Handles conversation storage and retrieval for the LTST Memory System."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize conversation storage."""
        if db_manager is None:
            # Get connection string from environment
            connection_string = os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")
            self.db_manager = DatabaseManager(connection_string)
        else:
            self.db_manager = db_manager
        self.cache = {}
        self.cache_ttl = timedelta(hours=1)

    def create_session(self, session: ConversationSession) -> bool:
        """Create a new conversation session."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO conversation_sessions
                        (session_id, user_id, session_name, session_type, status,
                         metadata, context_summary, relevance_score, created_at, last_activity)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (session_id) DO UPDATE SET
                            last_activity = EXCLUDED.last_activity,
                            status = EXCLUDED.status,
                            metadata = EXCLUDED.metadata
                    """,
                        (
                            session.session_id,
                            session.user_id,
                            session.session_name,
                            session.session_type,
                            session.status,
                            json.dumps(session.metadata),
                            session.context_summary,
                            session.relevance_score,
                            session.created_at,
                            session.last_activity,
                        ),
                    )
                    conn.commit()
                    logger.info(f"Session created/updated: {session.session_id}")
                    return True

        except Exception as e:
            logger.error(f"Failed to create session {session.session_id}: {e}")
            return False

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Retrieve a conversation session."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM conversation_sessions
                        WHERE session_id = %s
                    """,
                        (session_id,),
                    )
                    row = cursor.fetchone()

                    if row:
                        return ConversationSession(
                            session_id=row["session_id"],
                            user_id=row["user_id"],
                            session_name=row["session_name"],
                            session_type=row["session_type"],
                            status=row["status"],
                            metadata=row["metadata"],
                            context_summary=row["context_summary"],
                            relevance_score=row["relevance_score"],
                            created_at=row["created_at"],
                            last_activity=row["last_activity"],
                        )
                    return None

        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    def store_message(self, message: ConversationMessage) -> bool:
        """Store a conversation message."""
        try:
            # Sanitize content
            sanitized_content = sanitize_prompt(message.content)

            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get next message index if not provided
                    if message.message_index is None:
                        cursor.execute(
                            """
                            SELECT COALESCE(MAX(message_index), 0) + 1
                            FROM conversation_messages
                            WHERE session_id = %s
                        """,
                            (message.session_id,),
                        )
                        message.message_index = cursor.fetchone()[0]

                    cursor.execute(
                        """
                        INSERT INTO conversation_messages
                        (session_id, message_type, role, content, content_hash, context_hash,
                         timestamp, message_index, metadata, embedding, relevance_score,
                         is_context_message, parent_message_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (session_id, message_index) DO UPDATE SET
                            content = EXCLUDED.content,
                            content_hash = EXCLUDED.content_hash,
                            context_hash = EXCLUDED.context_hash,
                            metadata = EXCLUDED.metadata,
                            embedding = EXCLUDED.embedding,
                            relevance_score = EXCLUDED.relevance_score
                    """,
                        (
                            message.session_id,
                            message.message_type,
                            message.role,
                            sanitized_content,
                            message.content_hash,
                            message.context_hash,
                            message.timestamp,
                            message.message_index,
                            json.dumps(message.metadata),
                            message.embedding,
                            message.relevance_score,
                            message.is_context_message,
                            message.parent_message_id,
                        ),
                    )
                    conn.commit()
                    logger.info(f"Message stored: {message.session_id}:{message.message_index}")
                    return True

        except Exception as e:
            logger.error(f"Failed to store message: {e}")
            return False

    def get_messages(self, session_id: str, limit: int = 100, offset: int = 0) -> List[ConversationMessage]:
        """Retrieve messages for a session."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM conversation_messages
                        WHERE session_id = %s
                        ORDER BY message_index
                        LIMIT %s OFFSET %s
                    """,
                        (session_id, limit, offset),
                    )

                    messages = []
                    for row in cursor.fetchall():
                        message = ConversationMessage(
                            session_id=row["session_id"],
                            role=row["role"],
                            content=row["content"],
                            message_type=row["message_type"],
                            message_index=row["message_index"],
                            parent_message_id=row["parent_message_id"],
                            metadata=row["metadata"],
                            embedding=row["embedding"],
                            relevance_score=row["relevance_score"],
                            is_context_message=row["is_context_message"],
                            timestamp=row["timestamp"],
                        )
                        messages.append(message)

                    return messages

        except Exception as e:
            logger.error(f"Failed to get messages for session {session_id}: {e}")
            return []

    def search_messages(
        self, query: str, session_id: Optional[str] = None, limit: int = 10, threshold: float = 0.7
    ) -> List[Tuple[ConversationMessage, float]]:
        """Search messages using semantic similarity."""
        try:
            # TODO: Implement embedding generation for query
            # For now, use text-based search
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    if session_id:
                        cursor.execute(
                            """
                            SELECT *,
                                   CASE
                                       WHEN content ILIKE %s THEN 1.0
                                       WHEN content ILIKE %s THEN 0.8
                                       ELSE 0.5
                                   END as similarity
                            FROM conversation_messages
                            WHERE session_id = %s
                            AND (content ILIKE %s OR content ILIKE %s)
                            ORDER BY similarity DESC, timestamp DESC
                            LIMIT %s
                        """,
                            (
                                f"%{query}%",
                                f"%{query.split()[0]}%",
                                session_id,
                                f"%{query}%",
                                f"%{query.split()[0]}%",
                                limit,
                            ),
                        )
                    else:
                        cursor.execute(
                            """
                            SELECT *,
                                   CASE
                                       WHEN content ILIKE %s THEN 1.0
                                       WHEN content ILIKE %s THEN 0.8
                                       ELSE 0.5
                                   END as similarity
                            FROM conversation_messages
                            WHERE content ILIKE %s OR content ILIKE %s
                            ORDER BY similarity DESC, timestamp DESC
                            LIMIT %s
                        """,
                            (f"%{query}%", f"%{query.split()[0]}%", f"%{query}%", f"%{query.split()[0]}%", limit),
                        )

                    results = []
                    for row in cursor.fetchall():
                        if row["similarity"] >= threshold:
                            message = ConversationMessage(
                                session_id=row["session_id"],
                                role=row["role"],
                                content=row["content"],
                                message_type=row["message_type"],
                                message_index=row["message_index"],
                                parent_message_id=row["parent_message_id"],
                                metadata=row["metadata"],
                                embedding=row["embedding"],
                                relevance_score=row["relevance_score"],
                                is_context_message=row["is_context_message"],
                                timestamp=row["timestamp"],
                            )
                            results.append((message, row["similarity"]))

                    return results

        except Exception as e:
            logger.error(f"Failed to search messages: {e}")
            return []

    def store_context(self, context: ConversationContext) -> bool:
        """Store conversation context."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO conversation_context
                        (session_id, context_type, context_key, context_value,
                         relevance_score, context_hash, metadata, expires_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (session_id, context_type, context_key) DO UPDATE SET
                            context_value = EXCLUDED.context_value,
                            relevance_score = EXCLUDED.relevance_score,
                            context_hash = EXCLUDED.context_hash,
                            metadata = EXCLUDED.metadata,
                            expires_at = EXCLUDED.expires_at
                    """,
                        (
                            context.session_id,
                            context.context_type,
                            context.context_key,
                            context.context_value,
                            context.relevance_score,
                            context.context_hash,
                            json.dumps(context.metadata),
                            context.expires_at,
                        ),
                    )
                    conn.commit()
                    logger.info(f"Context stored: {context.session_id}:{context.context_type}:{context.context_key}")
                    return True

        except Exception as e:
            logger.error(f"Failed to store context: {e}")
            return False

    def get_context(self, session_id: str, context_type: Optional[str] = None) -> List[ConversationContext]:
        """Retrieve conversation context."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    if context_type:
                        cursor.execute(
                            """
                            SELECT * FROM conversation_context
                            WHERE session_id = %s AND context_type = %s
                            AND (expires_at IS NULL OR expires_at > NOW())
                            ORDER BY relevance_score DESC
                        """,
                            (session_id, context_type),
                        )
                    else:
                        cursor.execute(
                            """
                            SELECT * FROM conversation_context
                            WHERE session_id = %s
                            AND (expires_at IS NULL OR expires_at > NOW())
                            ORDER BY relevance_score DESC
                        """,
                            (session_id,),
                        )

                    contexts = []
                    for row in cursor.fetchall():
                        context = ConversationContext(
                            session_id=row["session_id"],
                            context_type=row["context_type"],
                            context_key=row["context_key"],
                            context_value=row["context_value"],
                            relevance_score=row["relevance_score"],
                            metadata=row["metadata"],
                            expires_at=row["expires_at"],
                        )
                        contexts.append(context)

                    return contexts

        except Exception as e:
            logger.error(f"Failed to get context for session {session_id}: {e}")
            return []

    def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity timestamp."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE conversation_sessions
                        SET last_activity = NOW()
                        WHERE session_id = %s
                    """,
                        (session_id,),
                    )
                    conn.commit()
                    return True

        except Exception as e:
            logger.error(f"Failed to update session activity {session_id}: {e}")
            return False

    def get_user_sessions(self, user_id: str, limit: int = 50) -> List[ConversationSession]:
        """Get sessions for a user."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM conversation_sessions
                        WHERE user_id = %s
                        ORDER BY last_activity DESC
                        LIMIT %s
                    """,
                        (user_id, limit),
                    )

                    sessions = []
                    for row in cursor.fetchall():
                        session = ConversationSession(
                            session_id=row["session_id"],
                            user_id=row["user_id"],
                            session_name=row["session_name"],
                            session_type=row["session_type"],
                            status=row["status"],
                            metadata=row["metadata"],
                            context_summary=row["context_summary"],
                            relevance_score=row["relevance_score"],
                            created_at=row["created_at"],
                            last_activity=row["last_activity"],
                        )
                        sessions.append(session)

                    return sessions

        except Exception as e:
            logger.error(f"Failed to get sessions for user {user_id}: {e}")
            return []

    def delete_session(self, session_id: str) -> bool:
        """Delete a conversation session and all associated data."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Delete in order due to foreign key constraints
                    cursor.execute("DELETE FROM conversation_messages WHERE session_id = %s", (session_id,))
                    cursor.execute("DELETE FROM conversation_context WHERE session_id = %s", (session_id,))
                    cursor.execute(
                        "DELETE FROM session_relationships WHERE source_session_id = %s OR target_session_id = %s",
                        (session_id, session_id),
                    )
                    cursor.execute("DELETE FROM conversation_sessions WHERE session_id = %s", (session_id,))
                    conn.commit()
                    logger.info(f"Session deleted: {session_id}")
                    return True

        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session summary statistics."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM session_summary
                        WHERE session_id = %s
                    """,
                        (session_id,),
                    )
                    row = cursor.fetchone()

                    if row:
                        return dict(row)
                    return None

        except Exception as e:
            logger.error(f"Failed to get session summary {session_id}: {e}")
            return None

    def cleanup_expired_data(self) -> bool:
        """Clean up expired context and cache entries."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Clean expired context
                    cursor.execute("SELECT clean_expired_context()")

                    # Clean expired cache
                    cursor.execute("SELECT clean_expired_cache()")

                    conn.commit()
                    logger.info("Expired data cleanup completed")
                    return True

        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {e}")
            return False
