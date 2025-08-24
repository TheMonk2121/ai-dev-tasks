"""
Memory Rehydrator for LTST Memory System

This module provides automatic memory rehydration capabilities for the LTST Memory System,
including session continuity detection, intelligent context prioritization, and performance optimization.
"""

import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from psycopg2.extras import RealDictCursor

from .context_merger import ContextMerger, MergedContext
from .conversation_storage import ConversationContext, ConversationMessage
from .database_resilience import DatabaseResilienceManager
from .logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class RehydrationRequest:
    """Request for memory rehydration."""

    session_id: str
    user_id: str
    current_message: Optional[str] = None
    context_types: Optional[List[str]] = None
    max_context_length: int = 10000
    include_conversation_history: bool = True
    history_limit: int = 20
    relevance_threshold: float = 0.7
    similarity_threshold: float = 0.8
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.context_types is None:
            self.context_types = ["conversation", "preference", "project", "user_info"]
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RehydrationResult:
    """Result of memory rehydration operation."""

    session_id: str
    user_id: str
    rehydrated_context: str
    conversation_history: List[ConversationMessage]
    user_preferences: Dict[str, Any]
    project_context: Dict[str, Any]
    relevant_contexts: List[ConversationContext]
    merged_contexts: List[MergedContext]
    session_continuity_score: float
    context_relevance_scores: Dict[str, float]
    rehydration_time_ms: float
    cache_hit: bool
    metadata: Dict[str, Any]

    def __post_init__(self):
        """Initialize computed fields."""
        if self.metadata is None:
            self.metadata = {}


class MemoryRehydrator:
    """Handles automatic memory rehydration for the LTST Memory System."""

    def __init__(self, db_manager: Optional[DatabaseResilienceManager] = None):
        """Initialize memory rehydrator."""
        if db_manager is None:
            import os

            connection_string = os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")
            self.db_manager = DatabaseResilienceManager(connection_string)
        else:
            self.db_manager = db_manager

        self.context_merger = ContextMerger(db_manager)

        # Cache for performance optimization
        self.rehydration_cache = {}
        self.cache_ttl = timedelta(minutes=15)
        self.cache_timestamps = {}

        # Configuration
        self.default_relevance_threshold = 0.7
        self.default_similarity_threshold = 0.8
        self.max_conversation_history = 50
        self.max_context_length = 10000
        self.session_continuity_window = timedelta(hours=24)

    def _get_cached_rehydration(self, request: RehydrationRequest) -> Optional[RehydrationResult]:
        """Get rehydration result from cache if available and fresh."""
        cache_key = self._generate_cache_key(request)

        if cache_key in self.rehydration_cache:
            timestamp = self.cache_timestamps.get(cache_key)
            if timestamp and datetime.now() - timestamp < self.cache_ttl:
                return self.rehydration_cache[cache_key]

        return None

    def _cache_rehydration(self, request: RehydrationRequest, result: RehydrationResult):
        """Cache rehydration result for future use."""
        cache_key = self._generate_cache_key(request)
        self.rehydration_cache[cache_key] = result
        self.cache_timestamps[cache_key] = datetime.now()

    def _generate_cache_key(self, request: RehydrationRequest) -> str:
        """Generate cache key for the rehydration request."""
        cache_data = {
            "session_id": request.session_id,
            "user_id": request.user_id,
            "current_message_hash": hashlib.sha256((request.current_message or "").encode()).hexdigest()[:16],
            "context_types": sorted(request.context_types or []),
            "max_context_length": request.max_context_length,
            "include_conversation_history": request.include_conversation_history,
            "history_limit": request.history_limit,
            "relevance_threshold": request.relevance_threshold,
            "similarity_threshold": request.similarity_threshold,
        }
        return hashlib.sha256(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()

    def _detect_session_continuity(self, session_id: str, user_id: str) -> float:
        """Detect session continuity based on recent activity."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Get recent sessions for the user
                    cursor.execute(
                        """
                        SELECT session_id, last_activity, session_name, context_summary
                        FROM conversation_sessions
                        WHERE user_id = %s
                        AND last_activity > %s
                        ORDER BY last_activity DESC
                        LIMIT 5
                    """,
                        (user_id, datetime.now() - self.session_continuity_window),
                    )

                    recent_sessions = cursor.fetchall()

                    if not recent_sessions:
                        return 0.0

                    # Check if current session is in recent sessions
                    current_session_found = any(s["session_id"] == session_id for s in recent_sessions)

                    if current_session_found:
                        # High continuity for current session
                        return 0.9

                    # Check for similar session names or context
                    current_session = self._get_session_info(session_id)
                    if not current_session:
                        return 0.0

                    # Calculate similarity with recent sessions
                    max_similarity = 0.0
                    for recent_session in recent_sessions:
                        similarity = self._calculate_session_similarity(current_session, recent_session)
                        max_similarity = max(max_similarity, similarity)

                    return max_similarity

        except Exception as e:
            logger.error(f"Session continuity detection failed: {e}")
            return 0.0

    def _get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT session_id, session_name, context_summary, metadata
                        FROM conversation_sessions
                        WHERE session_id = %s
                    """,
                        (session_id,),
                    )

                    row = cursor.fetchone()
                    return dict(row) if row else None

        except Exception as e:
            logger.error(f"Failed to get session info: {e}")
            return None

    def _calculate_session_similarity(self, session1: Dict[str, Any], session2: Dict[str, Any]) -> float:
        """Calculate similarity between two sessions."""
        try:
            # Simple text-based similarity for session names and context
            name1 = (session1.get("session_name") or "").lower()
            name2 = (session2.get("session_name") or "").lower()

            context1 = (session1.get("context_summary") or "").lower()
            context2 = (session2.get("context_summary") or "").lower()

            # Calculate name similarity
            name_tokens1 = set(name1.split())
            name_tokens2 = set(name2.split())

            name_similarity = 0.0
            if name_tokens1 and name_tokens2:
                intersection = len(name_tokens1.intersection(name_tokens2))
                union = len(name_tokens1.union(name_tokens2))
                name_similarity = intersection / union if union > 0 else 0.0

            # Calculate context similarity
            context_tokens1 = set(context1.split())
            context_tokens2 = set(context2.split())

            context_similarity = 0.0
            if context_tokens1 and context_tokens2:
                intersection = len(context_tokens1.intersection(context_tokens2))
                union = len(context_tokens1.union(context_tokens2))
                context_similarity = intersection / union if union > 0 else 0.0

            # Weighted average
            return (name_similarity * 0.4) + (context_similarity * 0.6)

        except Exception as e:
            logger.error(f"Session similarity calculation failed: {e}")
            return 0.0

    def _get_conversation_history(self, session_id: str, limit: int) -> List[ConversationMessage]:
        """Get conversation history for a session."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM conversation_messages
                        WHERE session_id = %s
                        ORDER BY message_index DESC
                        LIMIT %s
                    """,
                        (session_id, limit),
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

                    # Reverse to get chronological order
                    return list(reversed(messages))

        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []

    def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences for context rehydration."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT preference_key, preference_value, metadata
                        FROM user_preferences
                        WHERE user_id = %s
                        ORDER BY updated_at DESC
                    """,
                        (user_id,),
                    )

                    preferences = {}
                    for row in cursor.fetchall():
                        preferences[row["preference_key"]] = {
                            "value": row["preference_value"],
                            "metadata": row["metadata"],
                        }

                    return preferences

        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            return {}

    def _get_project_context(self, session_id: str) -> Dict[str, Any]:
        """Get project context for the session."""
        try:
            contexts = self.context_merger.merge_contexts(
                session_id, context_type="project", relevance_threshold=self.default_relevance_threshold
            )

            project_context = {}
            for merged_context in contexts.merged_contexts:
                project_context[merged_context.context_type] = {
                    "content": merged_context.merged_content,
                    "relevance": merged_context.relevance_score,
                    "metadata": merged_context.metadata,
                }

            return project_context

        except Exception as e:
            logger.error(f"Failed to get project context: {e}")
            return {}

    def _get_relevant_contexts(self, request: RehydrationRequest) -> List[ConversationContext]:
        """Get relevant contexts based on the request."""
        try:
            relevant_contexts = []

            for context_type in request.context_types or []:
                contexts = self.context_merger.merge_contexts(
                    request.session_id,
                    context_type=context_type,
                    relevance_threshold=request.relevance_threshold,
                    similarity_threshold=request.similarity_threshold,
                )

                # Convert merged contexts back to conversation contexts
                for merged_context in contexts.merged_contexts:
                    for source_context in merged_context.source_contexts:
                        if source_context not in relevant_contexts:
                            relevant_contexts.append(source_context)

            return relevant_contexts

        except Exception as e:
            logger.error(f"Failed to get relevant contexts: {e}")
            return []

    def _calculate_context_relevance_scores(
        self,
        conversation_history: List[ConversationMessage],
        user_preferences: Dict[str, Any],
        project_context: Dict[str, Any],
        relevant_contexts: List[ConversationContext],
        current_message: Optional[str],
    ) -> Dict[str, float]:
        """Calculate relevance scores for different context types."""
        try:
            scores = {}

            # Conversation history relevance
            if conversation_history:
                recent_messages = conversation_history[-5:]  # Last 5 messages
                avg_relevance = sum(msg.relevance_score for msg in recent_messages) / len(recent_messages)
                scores["conversation_history"] = min(avg_relevance, 1.0)
            else:
                scores["conversation_history"] = 0.0

            # User preferences relevance
            if user_preferences:
                scores["user_preferences"] = 0.8  # High relevance for user preferences
            else:
                scores["user_preferences"] = 0.0

            # Project context relevance
            if project_context:
                total_relevance = sum(data["relevance"] for data in project_context.values())
                scores["project_context"] = total_relevance / len(project_context) if project_context else 0.0
            else:
                scores["project_context"] = 0.0

            # Relevant contexts relevance
            if relevant_contexts:
                total_relevance = sum(ctx.relevance_score for ctx in relevant_contexts)
                scores["relevant_contexts"] = total_relevance / len(relevant_contexts)
            else:
                scores["relevant_contexts"] = 0.0

            # Overall relevance
            scores["overall"] = sum(scores.values()) / len(scores)

            return scores

        except Exception as e:
            logger.error(f"Failed to calculate relevance scores: {e}")
            return {"overall": 0.0}

    def _merge_rehydrated_context(
        self,
        conversation_history: List[ConversationMessage],
        user_preferences: Dict[str, Any],
        project_context: Dict[str, Any],
        relevant_contexts: List[ConversationContext],
        current_message: Optional[str],
        max_length: int,
    ) -> str:
        """Merge all rehydrated context into a single string."""
        try:
            merged_parts = []

            # Add conversation history
            if conversation_history:
                history_text = "Conversation History:\n"
                for msg in conversation_history[-10:]:  # Last 10 messages
                    role_label = "User" if msg.role == "human" else "Assistant"
                    history_text += f"{role_label}: {msg.content}\n"
                merged_parts.append(history_text)

            # Add user preferences
            if user_preferences:
                prefs_text = "User Preferences:\n"
                for key, data in user_preferences.items():
                    prefs_text += f"  {key}: {data['value']}\n"
                merged_parts.append(prefs_text)

            # Add project context
            if project_context:
                project_text = "Project Context:\n"
                for context_type, data in project_context.items():
                    project_text += f"  {context_type}: {data['content']}\n"
                merged_parts.append(project_text)

            # Add relevant contexts
            if relevant_contexts:
                context_text = "Relevant Context:\n"
                for ctx in relevant_contexts[:5]:  # Top 5 contexts
                    context_text += f"  {ctx.context_type}: {ctx.context_value}\n"
                merged_parts.append(context_text)

            # Add current message if provided
            if current_message:
                merged_parts.append(f"Current Message: {current_message}")

            # Join all parts
            merged_content = "\n\n".join(merged_parts)

            # Truncate if too long
            if len(merged_content) > max_length:
                merged_content = merged_content[:max_length] + "\n\n[Content truncated due to length]"

            return merged_content

        except Exception as e:
            logger.error(f"Failed to merge rehydrated context: {e}")
            return f"Current Message: {current_message}" if current_message else ""

    def rehydrate_memory(self, request: RehydrationRequest) -> RehydrationResult:
        """
        Rehydrate memory for a session.

        Args:
            request: Rehydration request with parameters

        Returns:
            RehydrationResult with all rehydrated context
        """
        start_time = time.time()

        try:
            # Check cache first
            cached_result = self._get_cached_rehydration(request)
            if cached_result:
                logger.info(f"Using cached rehydration for session {request.session_id}")
                return cached_result

            # Detect session continuity
            session_continuity_score = self._detect_session_continuity(request.session_id, request.user_id)

            # Get conversation history
            conversation_history = []
            if request.include_conversation_history:
                conversation_history = self._get_conversation_history(request.session_id, request.history_limit)

            # Get user preferences
            user_preferences = self._get_user_preferences(request.user_id)

            # Get project context
            project_context = self._get_project_context(request.session_id)

            # Get relevant contexts
            relevant_contexts = self._get_relevant_contexts(request)

            # Get merged contexts for detailed analysis
            merged_contexts = []
            for context_type in request.context_types or []:
                merge_result = self.context_merger.merge_contexts(
                    request.session_id,
                    context_type=context_type,
                    relevance_threshold=request.relevance_threshold,
                    similarity_threshold=request.similarity_threshold,
                )
                merged_contexts.extend(merge_result.merged_contexts)

            # Calculate relevance scores
            context_relevance_scores = self._calculate_context_relevance_scores(
                conversation_history, user_preferences, project_context, relevant_contexts, request.current_message
            )

            # Merge all context
            rehydrated_context = self._merge_rehydrated_context(
                conversation_history,
                user_preferences,
                project_context,
                relevant_contexts,
                request.current_message,
                request.max_context_length,
            )

            rehydration_time_ms = (time.time() - start_time) * 1000

            # Create result
            result = RehydrationResult(
                session_id=request.session_id,
                user_id=request.user_id,
                rehydrated_context=rehydrated_context,
                conversation_history=conversation_history,
                user_preferences=user_preferences,
                project_context=project_context,
                relevant_contexts=relevant_contexts,
                merged_contexts=merged_contexts,
                session_continuity_score=session_continuity_score,
                context_relevance_scores=context_relevance_scores,
                rehydration_time_ms=rehydration_time_ms,
                cache_hit=False,
                metadata=request.metadata or {},
            )

            # Cache the result
            self._cache_rehydration(request, result)

            logger.info(
                f"Memory rehydration completed for session {request.session_id}: "
                f"{rehydration_time_ms:.2f}ms, "
                f"{len(conversation_history)} messages, "
                f"{len(relevant_contexts)} contexts, "
                f"continuity: {session_continuity_score:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"Memory rehydration failed for session {request.session_id}: {e}")
            raise

    def get_rehydration_statistics(self) -> Dict[str, Any]:
        """Get statistics about rehydration operations."""
        try:
            return {
                "cache_size": len(self.rehydration_cache),
                "cache_entries": list(self.rehydration_cache.keys()),
                "cache_ttl_seconds": self.cache_ttl.total_seconds(),
                "default_relevance_threshold": self.default_relevance_threshold,
                "default_similarity_threshold": self.default_similarity_threshold,
                "max_conversation_history": self.max_conversation_history,
                "max_context_length": self.max_context_length,
                "session_continuity_window_hours": self.session_continuity_window.total_seconds() / 3600,
            }
        except Exception as e:
            logger.error(f"Failed to get rehydration statistics: {e}")
            return {"error": str(e)}

    def cleanup_expired_cache(self) -> int:
        """Clean up expired cache entries."""
        try:
            current_time = datetime.now()
            expired_keys = []

            for cache_key, timestamp in self.cache_timestamps.items():
                if current_time - timestamp > self.cache_ttl:
                    expired_keys.append(cache_key)

            for key in expired_keys:
                del self.rehydration_cache[key]
                del self.cache_timestamps[key]

            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired rehydration cache entries")

            return len(expired_keys)

        except Exception as e:
            logger.error(f"Rehydration cache cleanup failed: {e}")
            return 0
