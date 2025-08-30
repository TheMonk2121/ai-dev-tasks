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
    """Represents conversation context with decision intelligence support."""

    session_id: str
    context_type: str  # 'conversation', 'preference', 'project', 'user_info', 'decision'
    context_key: str
    context_value: str
    relevance_score: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None

    # Decision intelligence fields
    decision_head: Optional[str] = None  # Normalized decision summary
    decision_status: str = "open"  # 'open', 'closed', 'superseded'
    superseded_by: Optional[str] = None  # ID of superseding decision
    entities: Optional[List[str]] = None  # JSONB array of entity names
    files: Optional[List[str]] = None  # JSONB array of file paths

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.entities is None:
            self.entities = []
        if self.files is None:
            self.files = []


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
        decision_head: Optional[str] = None,
        decision_status: str = "open",
        superseded_by: Optional[str] = None,
        entities: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
    ) -> bool:
        """Store conversation context with decision intelligence support."""
        start_time = datetime.now()

        try:
            context_hash = self._generate_context_hash(session_id, context_type, context_key)

            self.cursor.execute(
                """
                INSERT INTO conversation_context
                (session_id, context_type, context_key, context_value, relevance_score,
                 context_hash, expires_at, decision_head, decision_status, superseded_by, entities, files)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_id, context_type, context_key) DO UPDATE SET
                    context_value = EXCLUDED.context_value,
                    relevance_score = EXCLUDED.relevance_score,
                    context_hash = EXCLUDED.context_hash,
                    expires_at = EXCLUDED.expires_at,
                    decision_head = EXCLUDED.decision_head,
                    decision_status = EXCLUDED.decision_status,
                    superseded_by = EXCLUDED.superseded_by,
                    entities = EXCLUDED.entities,
                    files = EXCLUDED.files,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING context_id
            """,
                (
                    session_id,
                    context_type,
                    context_key,
                    context_value,
                    relevance_score,
                    context_hash,
                    expires_at,
                    decision_head,
                    decision_status,
                    superseded_by,
                    entities,
                    files,
                ),
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
                           relevance_score, metadata, created_at, expires_at,
                           decision_head, decision_status, superseded_by, entities, files
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
                           relevance_score, metadata, created_at, expires_at,
                           decision_head, decision_status, superseded_by, entities, files
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

    # Decision Intelligence Methods

    def _canonicalize_query(self, text: str) -> str:
        """Simple canonicalization for decision queries and heads."""
        if not text:
            return text

        # Convert to lowercase and normalize whitespace
        text = text.lower().strip()

        # Use regex with word boundaries to avoid double replacement
        import re

        VERB_MAP = [
            (r"\bswitch to\b", "use"),
            (r"\bmigrate to\b", "use"),
            (r"\badopt\b", "use"),
            (r"\bdrop\b", "disable"),
            (r"\bturn off\b", "disable"),
            (r"\bdeprecate\b", "disable"),
            (r"\bremove\b", "disable"),
        ]

        ALIAS_MAP = [
            (r"\bpostgres(ql)?\b", "postgresql"),
            (r"\bpg\b", "postgresql"),
            (r"\bdocker compose\b", "docker"),
            (r"\bpy\b", "python"),
        ]

        # Apply verb mappings
        for pattern, replacement in VERB_MAP:
            text = re.sub(pattern, replacement, text)

        # Apply aliases
        for pattern, replacement in ALIAS_MAP:
            text = re.sub(pattern, replacement, text)

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def _generate_decision_key(self, original_head: str, canonical_head: str) -> str:
        """Generate stable decision key in verb.object[=value] format."""
        # Parse the canonical head to extract verb and object
        parts = canonical_head.split("_", 1)
        if len(parts) >= 2:
            verb = parts[0]
            object_part = parts[1]
            # Replace underscores with dots for consistency
            object_part = object_part.replace("_", ".")
            return f"{verb}.{object_part}"
        else:
            # Fallback: use the canonical head as-is, replacing underscores with dots
            return canonical_head.replace("_", ".")

    def store_decision(
        self,
        session_id: str,
        decision_head: str,
        context_value: str,
        decision_status: str = "open",
        entities: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        relevance_score: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None,
        auto_supersede: bool = True,
    ) -> bool:
        """Store a decision context with decision intelligence fields and automatic supersedence."""
        start_time = datetime.now()

        try:
            # Canonicalize the decision head
            canonical_head = self._canonicalize_query(decision_head)

            # Generate stable decision_key: verb.object[=value] format
            decision_key = self._generate_decision_key(decision_head, canonical_head)

            # Use decision_key for decisions
            context_key = decision_key
            context_hash = self._generate_context_hash(session_id, "decision", context_key)

            # Check for conflicting decisions if auto-supersede is enabled
            if auto_supersede:
                self._check_and_mark_superseded(session_id, decision_head, entities)

            # Convert Python lists to JSON for JSONB fields
            import json

            entities_json = json.dumps(entities or [])
            files_json = json.dumps(files or [])

            self.cursor.execute(
                """
                INSERT INTO conversation_context
                (session_id, context_type, context_key, context_value, relevance_score,
                 context_hash, decision_head, decision_status, entities, files, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_id, context_type, context_key) DO UPDATE SET
                    context_value = EXCLUDED.context_value,
                    relevance_score = EXCLUDED.relevance_score,
                    decision_head = EXCLUDED.decision_head,
                    decision_status = EXCLUDED.decision_status,
                    entities = EXCLUDED.entities,
                    files = EXCLUDED.files,
                    metadata = EXCLUDED.metadata,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING context_id
            """,
                (
                    session_id,
                    "decision",
                    context_key,
                    context_value,
                    relevance_score,
                    context_hash,
                    decision_head,
                    decision_status,
                    entities_json,
                    files_json,
                    json.dumps(metadata or {}),
                ),
            )

            self.connection.commit()

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("decision_storage", int(execution_time), 1)

            self.logger.info(f"Decision stored: {decision_head} for session {session_id}")
            return True

        except Exception as e:
            if self.connection:
                self.connection.rollback()
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("decision_storage", int(execution_time), error_message=str(e))
            self.logger.error(f"Failed to store decision: {e}")
            return False

    def _check_and_mark_superseded(
        self, session_id: str, new_decision_head: str, new_entities: Optional[List[str]]
    ) -> None:
        """Check for conflicting decisions and mark them as superseded."""
        try:
            if not new_entities:
                self.logger.debug("No new entities provided, skipping supersedence check")
                return

            self.logger.debug(
                f"Checking for conflicts with new decision: {new_decision_head}, entities: {new_entities}"
            )

            # Get existing open decisions for this session
            self.cursor.execute(
                """
                SELECT decision_head, entities, context_id
                FROM conversation_context
                WHERE session_id = %s
                AND context_type = 'decision'
                AND decision_status = 'open'
                AND decision_head != %s
            """,
                (session_id, new_decision_head),
            )

            existing_decisions = self.cursor.fetchall()
            self.logger.debug(f"Found {len(existing_decisions)} existing open decisions")

            for decision in existing_decisions:
                existing_head = decision.get("decision_head")
                existing_entities = decision.get("entities")
                existing_id = decision.get("context_id")

                self.logger.debug(f"Checking existing decision: {existing_head}, entities: {existing_entities}")

                # Check for conflicts based on entity overlap and decision head similarity
                if self._is_decision_conflicting(new_decision_head, new_entities, existing_head, existing_entities):
                    self.logger.info(f"Conflict detected, marking {existing_head} as superseded by {new_decision_head}")
                    # Mark existing decision as superseded
                    self.cursor.execute(
                        """
                        UPDATE conversation_context
                        SET decision_status = 'superseded',
                            superseded_by = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE context_id = %s
                    """,
                        (new_decision_head, existing_id),
                    )

                    self.logger.info(f"Decision marked as superseded: {existing_head} -> {new_decision_head}")

            # Commit any changes
            if existing_decisions:
                self.connection.commit()

        except Exception as e:
            self.logger.error(f"Failed to check and mark superseded decisions: {e}")
            import traceback

            self.logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't raise the exception - just log it

    def _is_decision_conflicting(
        self, new_head: str, new_entities: List[str], existing_head: str, existing_entities: Optional[List[str]]
    ) -> bool:
        """Determine if two decisions are conflicting."""
        try:
            # Convert existing entities to list if it's a string or handle JSONB
            if existing_entities is None:
                existing_entities = []
            elif isinstance(existing_entities, str):
                import json

                try:
                    existing_entities = json.loads(existing_entities)
                except:
                    existing_entities = []

            if not existing_entities or not new_entities:
                return False

            # Ensure both are lists
            if not isinstance(existing_entities, list):
                existing_entities = []
            if not isinstance(new_entities, list):
                new_entities = []

            # Check for entity overlap (conflicting decisions often involve the same entities)
            entity_overlap = set(new_entities).intersection(set(existing_entities))
            if len(entity_overlap) >= 2:  # At least 2 entities overlap
                # Check for semantic conflicts in decision heads
                if self._has_semantic_conflict(new_head, existing_head):
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to check decision conflict: {e}")
            return False

    def _has_semantic_conflict(self, new_head: str, existing_head: str) -> bool:
        """Check if two decision heads have semantic conflicts."""
        try:
            # Convert to lowercase for comparison
            new_lower = new_head.lower()
            existing_lower = existing_head.lower()

            # Define conflict patterns
            conflict_patterns = [
                # Enable/disable conflicts
                (r"enable_(\w+)", r"disable_(\w+)"),
                (r"use_(\w+)", r"drop_(\w+)"),
                (r"add_(\w+)", r"remove_(\w+)"),
                (r"start_(\w+)", r"stop_(\w+)"),
                # Technology choice conflicts
                (r"use_(\w+)", r"replace_with_(\w+)"),
                (r"(\w+)_first", r"(\w+)_instead"),
                # Version conflicts
                (r"(\w+)_v(\d+)", r"(\w+)_v(\d+)"),
                # Python version conflicts
                (r"use_python_(\d+\.\d+)", r"use_python_(\d+\.\d+)"),
            ]

            import re

            for pattern1, pattern2 in conflict_patterns:
                match1 = re.search(pattern1, new_lower)
                match2 = re.search(pattern2, existing_lower)

                if match1 and match2:
                    # Check if the captured groups are similar (same technology/component)
                    if match1.group(1) == match2.group(1):
                        return True

            # Check for direct contradictions in common words
            contradiction_pairs = [
                ("enable", "disable"),
                ("use", "drop"),
                ("add", "remove"),
                ("start", "stop"),
                ("include", "exclude"),
                ("accept", "reject"),
            ]

            # Check for version conflicts (same technology, different versions)
            if "python" in new_lower and "python" in existing_lower:
                # Extract version numbers (handle both dot and underscore formats)
                import re

                # Try dot format first (e.g., "3.11", "3.12")
                new_version = re.search(r"(\d+\.\d+)", new_lower)
                existing_version = re.search(r"(\d+\.\d+)", existing_lower)

                # If no dot format, try underscore format (e.g., "3_11", "3_12")
                if not new_version:
                    new_version = re.search(r"(\d+_\d+)", new_lower)
                if not existing_version:
                    existing_version = re.search(r"(\d+_\d+)", existing_lower)

                if new_version and existing_version and new_version.group(1) != existing_version.group(1):
                    return True

            for word1, word2 in contradiction_pairs:
                if word1 in new_lower and word2 in existing_lower:
                    return True
                if word2 in new_lower and word1 in existing_lower:
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to check semantic conflict: {e}")
            return False

    def retrieve_decisions(
        self,
        session_id: Optional[str] = None,
        decision_status: Optional[str] = None,
        entities: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Retrieve decisions with filtering options."""
        start_time = datetime.now()

        try:
            # If entities are provided, use query-conditioned retrieval
            if entities:
                # Build entity-based query with scoring
                entity_conditions = []
                entity_params = []
                for entity in entities:
                    entity_conditions.append("entities @> %s")
                    entity_params.append(json.dumps([entity]))

                query = f"""
                    SELECT
                        *,
                        CASE
                            WHEN {' OR '.join(entity_conditions)} THEN 1.0
                            ELSE 0.0
                        END as entity_score
                    FROM conversation_context
                    WHERE context_type = 'decision'
                """
                params = entity_params

                if session_id:
                    query += " AND session_id = %s"
                    params.append(session_id)

                if decision_status:
                    query += " AND decision_status = %s"
                    params.append(decision_status)

                query += " ORDER BY entity_score DESC, relevance_score DESC, created_at DESC LIMIT %s"
                params.append(limit)

            else:
                # Build dynamic query based on filters (time-based for backward compatibility)
                query_parts = ["SELECT * FROM conversation_context WHERE context_type = 'decision'"]
                params = []

                if session_id:
                    query_parts.append("AND session_id = %s")
                    params.append(session_id)

                if decision_status:
                    query_parts.append("AND decision_status = %s")
                    params.append(decision_status)

                query_parts.append("ORDER BY relevance_score DESC, created_at DESC")
                query_parts.append("LIMIT %s")
                params.append(limit)

                query = " ".join(query_parts)

            self.cursor.execute(query, params)
            decisions = [dict(row) for row in self.cursor.fetchall()]

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("decision_retrieval", int(execution_time), len(decisions))

            return decisions

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("decision_retrieval", int(execution_time), error_message=str(e))
            self.logger.error(f"Failed to retrieve decisions: {e}")
            return []

    def update_decision_status(self, session_id: str, decision_head: str, new_status: str) -> bool:
        """Update the status of a decision."""
        start_time = datetime.now()

        try:
            self.cursor.execute(
                """
                UPDATE conversation_context
                SET decision_status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = %s AND context_type = 'decision' AND decision_head = %s
                RETURNING context_id
            """,
                (new_status, session_id, decision_head),
            )

            result = self.cursor.fetchone()
            if not result:
                self.logger.warning(f"No decision found to update: {decision_head}")
                return False

            self.connection.commit()

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("decision_status_update", int(execution_time), 1)

            self.logger.info(f"Decision status updated: {decision_head} -> {new_status}")
            return True

        except Exception as e:
            if self.connection:
                self.connection.rollback()
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("decision_status_update", int(execution_time), error_message=str(e))
            self.logger.error(f"Failed to update decision status: {e}")
            return False

    def mark_decision_superseded(self, session_id: str, decision_head: str, superseded_by: str) -> bool:
        """Mark a decision as superseded by another decision."""
        start_time = datetime.now()

        try:
            # First, verify the superseding decision exists
            self.cursor.execute(
                """
                SELECT context_id FROM conversation_context
                WHERE session_id = %s AND context_type = 'decision' AND decision_head = %s
            """,
                (session_id, superseded_by),
            )

            if not self.cursor.fetchone():
                self.logger.error(f"Superseding decision not found: {superseded_by}")
                return False

            # Update the decision to be superseded
            self.cursor.execute(
                """
                UPDATE conversation_context
                SET decision_status = 'superseded', superseded_by = %s, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = %s AND context_type = 'decision' AND decision_head = %s
                RETURNING context_id
            """,
                (superseded_by, session_id, decision_head),
            )

            result = self.cursor.fetchone()
            if not result:
                self.logger.warning(f"No decision found to supersede: {decision_head}")
                return False

            self.connection.commit()

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("decision_supersedence", int(execution_time), 1)

            self.logger.info(f"Decision marked as superseded: {decision_head} -> {superseded_by}")
            return True

        except Exception as e:
            if self.connection:
                self.connection.rollback()
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("decision_supersedence", int(execution_time), error_message=str(e))
            self.logger.error(f"Failed to mark decision as superseded: {e}")
            return False

    def search_decisions(self, query: str, session_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search decisions using query-conditioned retrieval with BM25 and vector search."""
        start_time = datetime.now()

        try:
            # Canonicalize the query
            canonical_query = self._canonicalize_query(query)

            # Step 1: BM25 K1 on decision_head + context_value
            bm25_query = """
                SELECT
                    context_id,
                    context_key as decision_key,
                    decision_head,
                    context_value,
                    decision_status,
                    entities,
                    files,
                    relevance_score,
                    created_at,
                    ts_rank_cd(
                        to_tsvector('english', COALESCE(decision_head, '') || ' ' || COALESCE(context_value, '')),
                        plainto_tsquery('english', %s)
                    ) as bm25_score
                FROM conversation_context
                WHERE context_type = 'decision'
                AND to_tsvector('english', COALESCE(decision_head, '') || ' ' || COALESCE(context_value, '')) @@ plainto_tsquery('english', %s)
            """
            bm25_params = [canonical_query, canonical_query]

            if session_id:
                bm25_query += " AND session_id = %s"
                bm25_params.append(session_id)

            bm25_query += " AND ts_rank_cd(to_tsvector('english', COALESCE(decision_head, '') || ' ' || COALESCE(context_value, '')), plainto_tsquery('english', %s)) >= 0.05"
            bm25_params.append(canonical_query)
            bm25_query += " ORDER BY bm25_score DESC LIMIT %s"
            bm25_params.append(limit // 2)  # K1 = limit/2

            # Step 2: Vector K2 on head_embedding (placeholder for now since we don't have embeddings)
            # For now, we'll use a simple text similarity approach
            vector_query = """
                SELECT
                    context_id,
                    decision_head,
                    context_value,
                    decision_status,
                    entities,
                    files,
                    relevance_score,
                    created_at,
                    similarity(decision_head, %s) as vector_score
                FROM conversation_context
                WHERE context_type = 'decision'
                AND decision_head ILIKE %s
            """
            vector_params = [query, f"%{query}%"]

            if session_id:
                vector_query += " AND session_id = %s"
                vector_params.append(session_id)

            vector_query += " AND similarity(decision_head, %s) >= 0.6"
            vector_params.append(query)
            vector_query += " ORDER BY vector_score DESC LIMIT %s"
            vector_params.append(limit // 2)  # K2 = limit/2

            # Execute both queries and combine results
            self.cursor.execute(bm25_query, bm25_params)
            bm25_decisions = [dict(row) for row in self.cursor.fetchall()]

            self.cursor.execute(vector_query, vector_params)
            vector_decisions = [dict(row) for row in self.cursor.fetchall()]

            # Combine and deduplicate results
            all_decisions = bm25_decisions + vector_decisions
            seen_ids = set()
            decisions = []

            for decision in all_decisions:
                if decision["context_id"] not in seen_ids:
                    seen_ids.add(decision["context_id"])
                    decisions.append(decision)

            # Sort by combined score and limit
            decisions.sort(key=lambda x: x.get("bm25_score", 0) + x.get("vector_score", 0), reverse=True)
            decisions = decisions[:limit]

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("decision_search", int(execution_time), len(decisions))

            return decisions

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("decision_search", int(execution_time), error_message=str(e))
            self.logger.error(f"Failed to search decisions: {e}")
            return []

    def get_supersedence_chain(self, decision_head: str, session_id: str) -> List[Dict[str, Any]]:
        """Get the chain of supersedence for a decision."""
        start_time = datetime.now()

        try:
            # Find the decision and trace its supersedence chain
            chain = []
            current_decision = decision_head

            while current_decision:
                # Get current decision
                self.cursor.execute(
                    """
                    SELECT decision_head, decision_status, superseded_by, context_value, entities
                    FROM conversation_context
                    WHERE session_id = %s AND context_type = 'decision' AND decision_head = %s
                """,
                    (session_id, current_decision),
                )

                result = self.cursor.fetchone()
                if not result:
                    break

                decision_data = {
                    "decision_head": result[0],
                    "status": result[1],
                    "superseded_by": result[2],
                    "context_value": result[3],
                    "entities": result[4],
                }
                chain.append(decision_data)

                # Move to next decision in chain
                current_decision = result[2]

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("supersedence_chain_retrieval", int(execution_time), 1)

            return chain

        except Exception as e:
            self.logger.error(f"Failed to get supersedence chain: {e}")
            return []

    def resolve_supersedence_conflicts(self, session_id: str) -> Dict[str, Any]:
        """Resolve any supersedence conflicts and return summary."""
        start_time = datetime.now()

        try:
            # Find decisions that might have circular supersedence
            self.cursor.execute(
                """
                WITH RECURSIVE supersedence_chain AS (
                    SELECT decision_head, superseded_by, 1 as depth
                    FROM conversation_context
                    WHERE session_id = %s AND context_type = 'decision' AND superseded_by IS NOT NULL

                    UNION ALL

                    SELECT sc.decision_head, cc.superseded_by, sc.depth + 1
                    FROM supersedence_chain sc
                    JOIN conversation_context cc ON sc.superseded_by = cc.decision_head
                    WHERE cc.session_id = %s AND cc.context_type = 'decision' AND cc.superseded_by IS NOT NULL
                    AND sc.depth < 10  -- Prevent infinite loops
                )
                SELECT decision_head, superseded_by, depth
                FROM supersedence_chain
                WHERE depth > 5  -- Flag chains longer than 5
            """,
                (session_id, session_id),
            )

            long_chains = self.cursor.fetchall()

            # Find orphaned superseded decisions (superseded_by points to non-existent decision)
            self.cursor.execute(
                """
                SELECT cc1.decision_head, cc1.superseded_by
                FROM conversation_context cc1
                LEFT JOIN conversation_context cc2 ON cc1.superseded_by = cc2.decision_head
                WHERE cc1.session_id = %s
                AND cc1.context_type = 'decision'
                AND cc1.decision_status = 'superseded'
                AND cc1.superseded_by IS NOT NULL
                AND cc2.context_id IS NULL
            """,
                (session_id,),
            )

            orphaned_decisions = self.cursor.fetchall()

            # Resolve orphaned decisions by setting them back to 'open'
            resolved_count = 0
            for orphaned in orphaned_decisions:
                self.cursor.execute(
                    """
                    UPDATE conversation_context
                    SET decision_status = 'open', superseded_by = NULL, updated_at = CURRENT_TIMESTAMP
                    WHERE session_id = %s AND context_type = 'decision' AND decision_head = %s
                """,
                    (session_id, orphaned[0]),
                )
                resolved_count += 1

            if resolved_count > 0:
                self.connection.commit()
                self.logger.info(f"Resolved {resolved_count} orphaned superseded decisions")

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("supersedence_conflict_resolution", int(execution_time), 1)

            return {
                "long_chains": len(long_chains),
                "orphaned_decisions": len(orphaned_decisions),
                "resolved_count": resolved_count,
                "execution_time_ms": execution_time,
            }

        except Exception as e:
            self.logger.error(f"Failed to resolve supersedence conflicts: {e}")
            return {"error": str(e)}

    def get_decision_analytics(self, session_id: Optional[str] = None, time_range_days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics for decisions."""
        start_time = datetime.now()

        try:
            # Build base query
            base_query = """
                SELECT
                    decision_head,
                    decision_status,
                    entities,
                    files,
                    relevance_score,
                    created_at,
                    updated_at,
                    superseded_by
                FROM conversation_context
                WHERE context_type = 'decision'
            """
            params = []

            if session_id:
                base_query += " AND session_id = %s"
                params.append(session_id)

            base_query += " AND created_at >= CURRENT_DATE - INTERVAL '%s days'"
            params.append(time_range_days)

            base_query += " ORDER BY created_at DESC"

            self.cursor.execute(base_query, params)
            decisions = self.cursor.fetchall()

            if not decisions:
                return {"total_decisions": 0, "time_range_days": time_range_days, "analytics": {}}

            # Analyze decision patterns
            analytics = self._analyze_decision_patterns(decisions)

            # Analyze decision trends over time
            trends = self._analyze_decision_trends(decisions, time_range_days)

            # Analyze entity relationships
            entity_analysis = self._analyze_entity_relationships(decisions)

            # Analyze decision effectiveness
            effectiveness = self._analyze_decision_effectiveness(decisions)

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("decision_analytics", int(execution_time), 1)

            return {
                "total_decisions": len(decisions),
                "time_range_days": time_range_days,
                "analytics": analytics,
                "trends": trends,
                "entity_analysis": entity_analysis,
                "effectiveness": effectiveness,
                "execution_time_ms": execution_time,
            }

        except Exception as e:
            self.logger.error(f"Failed to get decision analytics: {e}")
            return {"error": str(e)}

    def _analyze_decision_patterns(self, decisions: List) -> Dict[str, Any]:
        """Analyze patterns in decision data."""
        try:
            patterns = {
                "status_distribution": {},
                "relevance_score_distribution": {},
                "entity_frequency": {},
                "file_frequency": {},
                "decision_head_patterns": {},
                "supersedence_patterns": {},
            }

            # Status distribution
            for decision in decisions:
                status = decision.get("decision_status", "unknown")
                patterns["status_distribution"][status] = patterns["status_distribution"].get(status, 0) + 1

            # Relevance score distribution
            score_ranges = {"0.0-0.2": 0, "0.2-0.4": 0, "0.4-0.6": 0, "0.6-0.8": 0, "0.8-1.0": 0}
            for decision in decisions:
                score = decision.get("relevance_score", 0.0)
                if score < 0.2:
                    score_ranges["0.0-0.2"] += 1
                elif score < 0.4:
                    score_ranges["0.2-0.4"] += 1
                elif score < 0.6:
                    score_ranges["0.4-0.6"] += 1
                elif score < 0.8:
                    score_ranges["0.6-0.8"] += 1
                else:
                    score_ranges["0.8-1.0"] += 1
            patterns["relevance_score_distribution"] = score_ranges

            # Entity frequency
            for decision in decisions:
                entities = decision.get("entities", [])
                if isinstance(entities, str):
                    try:
                        import json

                        entities = json.loads(entities)
                    except:
                        entities = []

                if isinstance(entities, list):
                    for entity in entities:
                        patterns["entity_frequency"][entity] = patterns["entity_frequency"].get(entity, 0) + 1

            # File frequency
            for decision in decisions:
                files = decision.get("files", [])
                if isinstance(files, str):
                    try:
                        import json

                        files = json.loads(files)
                    except:
                        files = []

                if isinstance(files, list):
                    for file in files:
                        patterns["file_frequency"][file] = patterns["file_frequency"].get(file, 0) + 1

            # Decision head patterns (extract common prefixes)
            for decision in decisions:
                head = decision.get("decision_head", "")
                if head:
                    # Extract prefix (e.g., "use_" from "use_python_3_12")
                    parts = head.split("_")
                    if len(parts) >= 2:
                        prefix = f"{parts[0]}_{parts[1]}"
                        patterns["decision_head_patterns"][prefix] = (
                            patterns["decision_head_patterns"].get(prefix, 0) + 1
                        )

            # Supersedence patterns
            superseded_count = 0
            superseding_count = 0
            for decision in decisions:
                if decision.get("decision_status") == "superseded":
                    superseded_count += 1
                if decision.get("superseded_by"):
                    superseding_count += 1

            patterns["supersedence_patterns"] = {
                "superseded_count": superseded_count,
                "superseding_count": superseding_count,
                "supersedence_rate": superseded_count / len(decisions) if decisions else 0,
            }

            return patterns

        except Exception as e:
            self.logger.error(f"Failed to analyze decision patterns: {e}")
            return {}

    def _analyze_decision_trends(self, decisions: List, time_range_days: int) -> Dict[str, Any]:
        """Analyze decision trends over time."""
        try:
            trends = {
                "daily_decision_count": {},
                "weekly_decision_count": {},
                "status_trends": {},
                "relevance_trends": {},
            }

            # Group decisions by date
            for decision in decisions:
                created_at = decision.get("created_at")
                if created_at:
                    if isinstance(created_at, str):
                        from datetime import datetime

                        try:
                            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        except:
                            continue

                    date_str = created_at.strftime("%Y-%m-%d")
                    week_str = created_at.strftime("%Y-W%U")

                    # Daily count
                    trends["daily_decision_count"][date_str] = trends["daily_decision_count"].get(date_str, 0) + 1

                    # Weekly count
                    trends["weekly_decision_count"][week_str] = trends["weekly_decision_count"].get(week_str, 0) + 1

                    # Status trends
                    status = decision.get("decision_status", "unknown")
                    if date_str not in trends["status_trends"]:
                        trends["status_trends"][date_str] = {}
                    trends["status_trends"][date_str][status] = trends["status_trends"][date_str].get(status, 0) + 1

                    # Relevance trends
                    relevance = decision.get("relevance_score", 0.0)
                    if date_str not in trends["relevance_trends"]:
                        trends["relevance_trends"][date_str] = {"total": 0, "count": 0}
                    trends["relevance_trends"][date_str]["total"] += relevance
                    trends["relevance_trends"][date_str]["count"] += 1

            # Calculate average relevance per day
            for date_str in trends["relevance_trends"]:
                data = trends["relevance_trends"][date_str]
                if data["count"] > 0:
                    data["average"] = data["total"] / data["count"]
                else:
                    data["average"] = 0.0

            return trends

        except Exception as e:
            self.logger.error(f"Failed to analyze decision trends: {e}")
            return {}

    def _analyze_entity_relationships(self, decisions: List) -> Dict[str, Any]:
        """Analyze relationships between entities in decisions."""
        try:
            relationships = {
                "entity_co_occurrence": {},
                "entity_decision_mapping": {},
                "entity_status_distribution": {},
                "entity_relevance_correlation": {},
            }

            # Build entity co-occurrence matrix
            for decision in decisions:
                entities = decision.get("entities", [])
                if isinstance(entities, str):
                    try:
                        import json

                        entities = json.loads(entities)
                    except:
                        entities = []

                if isinstance(entities, list) and len(entities) > 1:
                    # Count co-occurrences
                    for i, entity1 in enumerate(entities):
                        for entity2 in entities[i + 1 :]:
                            pair = tuple(sorted([entity1, entity2]))
                            relationships["entity_co_occurrence"][pair] = (
                                relationships["entity_co_occurrence"].get(pair, 0) + 1
                            )

                # Map entities to decisions
                for entity in entities:
                    if entity not in relationships["entity_decision_mapping"]:
                        relationships["entity_decision_mapping"][entity] = []
                    relationships["entity_decision_mapping"][entity].append(decision.get("decision_head", ""))

                    # Entity status distribution
                    if entity not in relationships["entity_status_distribution"]:
                        relationships["entity_status_distribution"][entity] = {}
                    status = decision.get("decision_status", "unknown")
                    relationships["entity_status_distribution"][entity][status] = (
                        relationships["entity_status_distribution"][entity].get(status, 0) + 1
                    )

                    # Entity relevance correlation
                    if entity not in relationships["entity_relevance_correlation"]:
                        relationships["entity_relevance_correlation"][entity] = {"total": 0, "count": 0}
                    relevance = decision.get("relevance_score", 0.0)
                    relationships["entity_relevance_correlation"][entity]["total"] += relevance
                    relationships["entity_relevance_correlation"][entity]["count"] += 1

            # Calculate average relevance per entity
            for entity in relationships["entity_relevance_correlation"]:
                data = relationships["entity_relevance_correlation"][entity]
                if data["count"] > 0:
                    data["average"] = data["total"] / data["count"]
                else:
                    data["average"] = 0.0

            return relationships

        except Exception as e:
            self.logger.error(f"Failed to analyze entity relationships: {e}")
            return {}

    def _analyze_decision_effectiveness(self, decisions: List) -> Dict[str, Any]:
        """Analyze decision effectiveness metrics."""
        try:
            effectiveness = {
                "decision_lifespan": {},
                "supersedence_effectiveness": {},
                "relevance_effectiveness": {},
                "entity_effectiveness": {},
            }

            # Decision lifespan analysis
            for decision in decisions:
                created_at = decision.get("created_at")
                updated_at = decision.get("updated_at")

                if created_at and updated_at:
                    if isinstance(created_at, str):
                        from datetime import datetime

                        try:
                            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        except:
                            continue

                    if isinstance(updated_at, str):
                        try:
                            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                        except:
                            continue

                    lifespan = (updated_at - created_at).days
                    lifespan_range = f"{(lifespan // 7) * 7}-{((lifespan // 7) + 1) * 7} days"
                    effectiveness["decision_lifespan"][lifespan_range] = (
                        effectiveness["decision_lifespan"].get(lifespan_range, 0) + 1
                    )

            # Supersedence effectiveness
            total_decisions = len(decisions)
            superseded_count = sum(1 for d in decisions if d.get("decision_status") == "superseded")
            open_count = sum(1 for d in decisions if d.get("decision_status") == "open")
            closed_count = sum(1 for d in decisions if d.get("decision_status") == "closed")

            effectiveness["supersedence_effectiveness"] = {
                "total_decisions": total_decisions,
                "superseded_count": superseded_count,
                "open_count": open_count,
                "closed_count": closed_count,
                "supersedence_rate": superseded_count / total_decisions if total_decisions > 0 else 0,
                "stability_rate": (open_count + closed_count) / total_decisions if total_decisions > 0 else 0,
            }

            # Relevance effectiveness
            relevance_scores = [d.get("relevance_score", 0.0) for d in decisions]
            if relevance_scores:
                effectiveness["relevance_effectiveness"] = {
                    "average_relevance": sum(relevance_scores) / len(relevance_scores),
                    "min_relevance": min(relevance_scores),
                    "max_relevance": max(relevance_scores),
                    "high_relevance_count": sum(1 for score in relevance_scores if score >= 0.8),
                    "low_relevance_count": sum(1 for score in relevance_scores if score < 0.5),
                }

            # Entity effectiveness
            entity_decision_counts = {}
            for decision in decisions:
                entities = decision.get("entities", [])
                if isinstance(entities, str):
                    try:
                        import json

                        entities = json.loads(entities)
                    except:
                        entities = []

                if isinstance(entities, list):
                    for entity in entities:
                        entity_decision_counts[entity] = entity_decision_counts.get(entity, 0) + 1

            effectiveness["entity_effectiveness"] = {
                "total_entities": len(entity_decision_counts),
                "most_common_entities": sorted(entity_decision_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                "entity_decision_ratio": len(entity_decision_counts) / total_decisions if total_decisions > 0 else 0,
            }

            return effectiveness

        except Exception as e:
            self.logger.error(f"Failed to analyze decision effectiveness: {e}")
            return {}

    def get_decision_recommendations(self, session_id: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
        """Get decision recommendations based on analytics and patterns."""
        start_time = datetime.now()

        try:
            # Get analytics for the session
            analytics = self.get_decision_analytics(session_id, time_range_days=90)

            if "error" in analytics:
                return {"error": analytics["error"]}

            recommendations = {
                "decision_quality": {},
                "entity_optimization": {},
                "supersedence_insights": {},
                "trend_recommendations": {},
                "action_items": [],
            }

            # Decision quality recommendations
            if "effectiveness" in analytics and "relevance_effectiveness" in analytics["effectiveness"]:
                relevance_data = analytics["effectiveness"]["relevance_effectiveness"]
                avg_relevance = relevance_data.get("average_relevance", 0.0)
                low_relevance_count = relevance_data.get("low_relevance_count", 0)

                if avg_relevance < 0.6:
                    recommendations["decision_quality"][
                        "relevance_issue"
                    ] = "Average decision relevance is low. Consider improving decision context and entity specificity."
                    recommendations["action_items"].append(
                        "Review decisions with relevance scores < 0.5 for context improvement"
                    )

                if low_relevance_count > 0:
                    recommendations["decision_quality"][
                        "low_relevance_decisions"
                    ] = f"{low_relevance_count} decisions have low relevance scores"

            # Entity optimization recommendations
            if "entity_analysis" in analytics and "entity_relevance_correlation" in analytics["entity_analysis"]:
                entity_correlation = analytics["entity_analysis"]["entity_relevance_correlation"]
                low_relevance_entities = []

                for entity, data in entity_correlation.items():
                    if data.get("average", 0.0) < 0.5:
                        low_relevance_entities.append(entity)

                if low_relevance_entities:
                    recommendations["entity_optimization"][
                        "low_relevance_entities"
                    ] = f"Entities with low average relevance: {', '.join(low_relevance_entities[:3])}"
                    recommendations["action_items"].append(
                        "Review decisions involving low-relevance entities for context improvement"
                    )

            # Supersedence insights
            if "analytics" in analytics and "supersedence_patterns" in analytics["analytics"]:
                supersedence_data = analytics["analytics"]["supersedence_patterns"]
                supersedence_rate = supersedence_data.get("supersedence_rate", 0.0)

                if supersedence_rate > 0.3:
                    recommendations["supersedence_insights"][
                        "high_supersedence"
                    ] = f"High supersedence rate ({supersedence_rate:.1%}). Consider improving initial decision quality."
                    recommendations["action_items"].append("Review decision-making process to reduce supersedence rate")
                elif supersedence_rate < 0.1:
                    recommendations["supersedence_insights"][
                        "low_supersedence"
                    ] = f"Low supersedence rate ({supersedence_rate:.1%}). Decisions appear stable."
                else:
                    recommendations["supersedence_insights"][
                        "balanced_supersedence"
                    ] = f"Balanced supersedence rate ({supersedence_rate:.1%}). Good decision evolution."

            # Trend recommendations
            if "trends" in analytics and "daily_decision_count" in analytics["trends"]:
                daily_counts = analytics["trends"]["daily_decision_count"]
                if daily_counts:
                    recent_days = sorted(daily_counts.keys(), reverse=True)[:7]
                    recent_avg = sum(daily_counts.get(day, 0) for day in recent_days) / len(recent_days)

                    if recent_avg > 5:
                        recommendations["trend_recommendations"][
                            "high_decision_volume"
                        ] = f"High decision volume ({recent_avg:.1f} per day). Consider decision consolidation."
                        recommendations["action_items"].append(
                            "Review if multiple decisions can be consolidated into single comprehensive decisions"
                        )
                    elif recent_avg < 1:
                        recommendations["trend_recommendations"][
                            "low_decision_volume"
                        ] = f"Low decision volume ({recent_avg:.1f} per day). Consider more proactive decision tracking."
                        recommendations["action_items"].append(
                            "Identify areas where decisions should be documented but aren't"
                        )

            # Add general recommendations
            if not recommendations["action_items"]:
                recommendations["action_items"].append(
                    "Decision system is performing well. Continue current practices."
                )

            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_performance_metric("decision_recommendations", int(execution_time), 1)

            return recommendations

        except Exception as e:
            self.logger.error(f"Failed to get decision recommendations: {e}")
            return {"error": str(e)}
