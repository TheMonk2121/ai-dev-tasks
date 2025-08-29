#!/usr/bin/env python3
# type: ignore
"""
Conversation Storage System for LTST Memory

This module provides the ConversationStorage class for managing conversation data,
session tracking, and user preferences in the LTST memory system.

Note: Type ignore is used because RealDictCursor returns dictionary-like objects
that the type checker doesn't properly recognize, and database connection objects
are properly handled with null checks at runtime.
"""

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor


@dataclass
class ConversationMessage:
    """Represents a conversation message."""

    session_id: str
    role: str  # 'human', 'ai', 'system'
    content: str
    message_type: str = "message"
    metadata: Optional[Dict[str, Any]] = None
    parent_message_id: Optional[int] = None
    is_context_message: bool = False
    relevance_score: float = 0.5

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


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

    def __post_init__(self):
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
        if self.metadata is None:
            self.metadata = {}


@dataclass
class UserPreference:
    """Represents a user preference."""

    user_id: str
    preference_key: str
    preference_value: str
    preference_type: str = "general"
    confidence_score: float = 0.0
    source: str = "learned"


class ConversationStorage:
    """Manages conversation storage and retrieval for the LTST memory system."""

    def __init__(self, database_url: str = None):
        """Initialize conversation storage."""
        self.database_url = database_url or os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")
        self.connection = None
        self.cursor = None
        self.logger = logging.getLogger(__name__)

        # Performance metrics
        self.performance_metrics = {
            "storage_operations": 0,
            "retrieval_operations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(self.database_url)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            return True
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            return False

    def disconnect(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content to detect duplicates."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _generate_context_hash(self, session_id: str, context_type: str, context_key: str) -> str:
        """Generate hash for context entries."""
        content = f"{session_id}:{context_type}:{context_key}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _log_performance_metric(
        self,
        operation_type: str,
        execution_time_ms: int,
        result_count: int = None,
        cache_hit: bool = False,
        error_message: str = None,
    ):
        """Log performance metrics."""
        try:
            self.cursor.execute(
                """
                INSERT INTO memory_performance_metrics
                (operation_type, execution_time_ms, result_count, cache_hit, error_message)
                VALUES (%s, %s, %s, %s, %s)
            """,
                (operation_type, execution_time_ms, result_count, cache_hit, error_message),
            )
            self.connection.commit()
        except Exception as e:
            self.logger.warning(f"Failed to log performance metric: {e}")

    def create_session(self, session: ConversationSession) -> bool:
        """Create a new conversation session."""
        start_time = datetime.now()

        try:
            self.cursor.execute(
                """
                INSERT INTO conversation_sessions
                (session_id, user_id, session_name, session_type, status, metadata, context_summary)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_id) DO UPDATE SET
                    last_activity = CURRENT_TIMESTAMP,
                    status = EXCLUDED.status,
                    metadata = EXCLUDED.metadata,
                    context_summary = EXCLUDED.context_summary
                RETURNING session_id
            """,
                (
                    session.session_id,
                    session.user_id,
                    session.session_name,
                    session.session_type,
                    session.status,
                    json.dumps(session.metadata),
                    session.context_summary,
                ),
            )

            self.connection.commit()

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("session_creation", int(execution_time), 1)

            self.logger.info(f"Session created/updated: {session.session_id}")
            return True

        except Exception as e:
            self.connection.rollback()
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("session_creation", int(execution_time), error_message=str(e))
            self.logger.error(f"Failed to create session: {e}")
            return False

    def store_message(self, message: ConversationMessage, embedding: Optional[List[float]] = None) -> bool:
        """Store a conversation message."""
        start_time = datetime.now()

        try:
            # Get next message index for the session
            self.cursor.execute(
                """
                SELECT COALESCE(MAX(message_index), 0) + 1 as next_index
                FROM conversation_messages
                WHERE session_id = %s
            """,
                (message.session_id,),
            )

            result = self.cursor.fetchone()
            message_index = result["next_index"] if result else 1

            # Generate content hash
            content_hash = self._generate_content_hash(message.content)

            # Convert embedding to vector if provided
            vector_embedding = None
            if embedding:
                vector_embedding = f"[{','.join(map(str, embedding))}]"

            self.cursor.execute(
                """
                INSERT INTO conversation_messages
                (session_id, message_type, role, content, content_hash, timestamp,
                 message_index, metadata, embedding, is_context_message, parent_message_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING message_id
            """,
                (
                    message.session_id,
                    message.message_type,
                    message.role,
                    message.content,
                    content_hash,
                    datetime.now(),
                    message_index,
                    json.dumps(message.metadata),
                    vector_embedding,
                    message.is_context_message,
                    message.parent_message_id,
                ),
            )

            result = self.cursor.fetchone()
            self.connection.commit()

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("message_storage", int(execution_time), 1)

            self.logger.info(f"Message stored: {result['message_id']} in session {message.session_id}")
            return True

        except Exception as e:
            self.connection.rollback()
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("message_storage", int(execution_time), error_message=str(e))
            self.logger.error(f"Failed to store message: {e}")
            return False

    def retrieve_session_messages(self, session_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieve messages for a session."""
        start_time = datetime.now()

        try:
            self.cursor.execute(
                """
                SELECT message_id, session_id, message_type, role, content,
                       content_hash, timestamp, message_index, metadata,
                       is_context_message, parent_message_id, created_at
                FROM conversation_messages
                WHERE session_id = %s
                ORDER BY message_index ASC
                LIMIT %s OFFSET %s
            """,
                (session_id, limit, offset),
            )

            messages = [dict(row) for row in self.cursor.fetchall()]

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("message_retrieval", int(execution_time), len(messages))

            return messages

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("message_retrieval", int(execution_time), error_message=str(e))
            self.logger.error(f"Failed to retrieve messages: {e}")
            return []

    def search_messages_semantic(
        self,
        query_embedding: List[float],
        session_id: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Search messages using semantic similarity."""
        start_time = datetime.now()

        try:
            vector_query = f"[{','.join(map(str, query_embedding))}]"

            if session_id:
                # Search within specific session
                self.cursor.execute(
                    """
                    SELECT message_id, session_id, role, content,
                           metadata, relevance_score,
                           1 - (embedding <=> %s) as similarity_score
                    FROM conversation_messages
                    WHERE session_id = %s
                    AND embedding IS NOT NULL
                    AND 1 - (embedding <=> %s) > %s
                    ORDER BY embedding <=> %s
                    LIMIT %s
                """,
                    (vector_query, session_id, vector_query, similarity_threshold, vector_query, limit),
                )
            else:
                # Search across all sessions
                self.cursor.execute(
                    """
                    SELECT message_id, session_id, role, content,
                           metadata, relevance_score,
                           1 - (embedding <=> %s) as similarity_score
                    FROM conversation_messages
                    WHERE embedding IS NOT NULL
                    AND 1 - (embedding <=> %s) > %s
                    ORDER BY embedding <=> %s
                    LIMIT %s
                """,
                    (vector_query, vector_query, similarity_threshold, vector_query, limit),
                )

            messages = [dict(row) for row in self.cursor.fetchall()]

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("semantic_search", int(execution_time), len(messages))

            return messages

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("semantic_search", int(execution_time), error_message=str(e))
            self.logger.error(f"Failed to search messages semantically: {e}")
            return []

    def store_context(
        self,
        session_id: str,
        context_type: str,
        context_key: str,
        context_value: str,
        relevance_score: float = 0.0,
        expires_at: Optional[datetime] = None,
    ) -> bool:
        """Store conversation context."""
        start_time = datetime.now()

        try:
            context_hash = self._generate_context_hash(session_id, context_type, context_key)

            self.cursor.execute(
                """
                INSERT INTO conversation_context
                (session_id, context_type, context_key, context_value, relevance_score,
                 context_hash, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_id, context_type, context_key) DO UPDATE SET
                    context_value = EXCLUDED.context_value,
                    relevance_score = EXCLUDED.relevance_score,
                    context_hash = EXCLUDED.context_hash,
                    expires_at = EXCLUDED.expires_at,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING context_id
            """,
                (session_id, context_type, context_key, context_value, relevance_score, context_hash, expires_at),
            )

            self.connection.commit()

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("context_storage", int(execution_time), 1)

            return True

        except Exception as e:
            self.connection.rollback()
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("context_storage", int(execution_time), error_message=str(e))
            self.logger.error(f"Failed to store context: {e}")
            return False

    def retrieve_context(
        self, session_id: str, context_type: Optional[str] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Retrieve conversation context."""
        start_time = datetime.now()

        try:
            if context_type:
                self.cursor.execute(
                    """
                    SELECT context_id, session_id, context_type, context_key, context_value,
                           relevance_score, metadata, created_at, expires_at
                    FROM conversation_context
                    WHERE session_id = %s AND context_type = %s
                    AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                    ORDER BY relevance_score DESC, created_at DESC
                    LIMIT %s
                """,
                    (session_id, context_type, limit),
                )
            else:
                self.cursor.execute(
                    """
                    SELECT context_id, session_id, context_type, context_key, context_value,
                           relevance_score, metadata, created_at, expires_at
                    FROM conversation_context
                    WHERE session_id = %s
                    AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                    ORDER BY relevance_score DESC, created_at DESC
                    LIMIT %s
                """,
                    (session_id, limit),
                )

            context_entries = [dict(row) for row in self.cursor.fetchall()]

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("context_retrieval", int(execution_time), len(context_entries))

            return context_entries

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("context_retrieval", int(execution_time), error_message=str(e))
            self.logger.error(f"Failed to retrieve context: {e}")
            return []

    def store_user_preference(self, preference: UserPreference) -> bool:
        """Store user preference."""
        start_time = datetime.now()

        try:
            self.cursor.execute(
                """
                INSERT INTO user_preferences
                (user_id, preference_key, preference_value, preference_type,
                 confidence_score, source)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, preference_key) DO UPDATE SET
                    preference_value = EXCLUDED.preference_value,
                    preference_type = EXCLUDED.preference_type,
                    confidence_score = EXCLUDED.confidence_score,
                    source = EXCLUDED.source,
                    usage_count = user_preferences.usage_count + 1,
                    last_used = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING preference_id
            """,
                (
                    preference.user_id,
                    preference.preference_key,
                    preference.preference_value,
                    preference.preference_type,
                    preference.confidence_score,
                    preference.source,
                ),
            )

            self.connection.commit()

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("preference_storage", int(execution_time), 1)

            return True

        except Exception as e:
            self.connection.rollback()
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("preference_storage", int(execution_time), error_message=str(e))
            self.logger.error(f"Failed to store preference: {e}")
            return False

    def retrieve_user_preferences(
        self, user_id: str, preference_type: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve user preferences."""
        start_time = datetime.now()

        try:
            if preference_type:
                self.cursor.execute(
                    """
                    SELECT preference_id, preference_key, preference_value, preference_type,
                           confidence_score, source, usage_count, last_used, created_at
                    FROM user_preferences
                    WHERE user_id = %s AND preference_type = %s
                    ORDER BY confidence_score DESC, usage_count DESC
                    LIMIT %s
                """,
                    (user_id, preference_type, limit),
                )
            else:
                self.cursor.execute(
                    """
                    SELECT preference_id, preference_key, preference_value, preference_type,
                           confidence_score, source, usage_count, last_used, created_at
                    FROM user_preferences
                    WHERE user_id = %s
                    ORDER BY confidence_score DESC, usage_count DESC
                    LIMIT %s
                """,
                    (user_id, limit),
                )

            preferences = [dict(row) for row in self.cursor.fetchall()]

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("preference_retrieval", int(execution_time), len(preferences))

            return preferences

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("preference_retrieval", int(execution_time), error_message=str(e))
            self.logger.error(f"Failed to retrieve preferences: {e}")
            return []

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session summary information."""
        start_time = datetime.now()

        try:
            self.cursor.execute(
                """
                SELECT * FROM session_summary WHERE session_id = %s
            """,
                (session_id,),
            )

            result = self.cursor.fetchone()

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("session_summary", int(execution_time), 1 if result else 0)

            return dict(result) if result else None

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("session_summary", int(execution_time), error_message=str(e))
            self.logger.error(f"Failed to get session summary: {e}")
            return None

    def cleanup_expired_data(self) -> Tuple[int, int]:
        """Clean up expired context and cache entries."""
        start_time = datetime.now()

        try:
            # Clean expired context
            self.cursor.execute("SELECT clean_expired_context();")
            context_cleaned = self.cursor.fetchone()[0] if self.cursor.fetchone() else 0

            # Clean expired cache
            self.cursor.execute("SELECT clean_expired_cache();")
            cache_cleaned = self.cursor.fetchone()[0] if self.cursor.fetchone() else 0

            self.connection.commit()

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("cleanup", int(execution_time), context_cleaned + cache_cleaned)

            self.logger.info(f"Cleanup completed: {context_cleaned} context entries, {cache_cleaned} cache entries")
            return context_cleaned, cache_cleaned

        except Exception as e:
            self.connection.rollback()
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("cleanup", int(execution_time), error_message=str(e))
            self.logger.error(f"Failed to cleanup expired data: {e}")
            return 0, 0

    def get_performance_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics for the specified time period."""
        try:
            self.cursor.execute(
                """
                SELECT
                    operation_type,
                    COUNT(*) as operation_count,
                    AVG(execution_time_ms) as avg_execution_time,
                    MAX(execution_time_ms) as max_execution_time,
                    SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hits,
                    COUNT(*) - SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_misses
                FROM memory_performance_metrics
                WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '%s hours'
                GROUP BY operation_type
                ORDER BY operation_count DESC
            """,
                (hours,),
            )

            metrics = [dict(row) for row in self.cursor.fetchall()]

            return {
                "time_period_hours": hours,
                "operations": metrics,
                "total_operations": sum(m["operation_count"] for m in metrics),
                "total_cache_hits": sum(m["cache_hits"] for m in metrics),
                "total_cache_misses": sum(m["cache_misses"] for m in metrics),
            }

        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return {}
