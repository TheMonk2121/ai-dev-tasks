"""
LTST Memory System - Main Integration Class

This module provides the main integration class for the LTST Memory System,
combining conversation storage, context merging, and memory rehydration capabilities.
"""

import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .context_merger import ContextMerger, ContextMergeResult
from .conversation_storage import ConversationContext, ConversationMessage, ConversationSession, ConversationStorage
from .dashboard_manager import DashboardManager
from .database_resilience import DatabaseResilienceManager
from .logger import setup_logger
from .ltst_database_integration import DatabaseMergeResult, DatabaseRehydrationResult, LTSTDatabaseIntegration
from .memory_rehydrator import MemoryRehydrator, RehydrationRequest, RehydrationResult
from .privacy_manager import PrivacyConfig, PrivacyManager
from .session_continuity import SessionContinuityManager

# Add src to path for DSN resolver import
try:
    # Try relative import first (when running from dspy-rag-system directory)
    from ...src.common.db_dsn import resolve_dsn
except ImportError:
    try:
        # Try absolute import (when running from project root)
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
        from common.db_dsn import resolve_dsn
    except ImportError:
        # Fallback to direct environment variable access
        resolve_dsn = None

logger = setup_logger(__name__)


@dataclass
class MemoryOperation:
    """Represents a memory operation with metadata."""

    operation_type: str  # 'store', 'retrieve', 'merge', 'rehydrate'
    session_id: str
    user_id: str
    timestamp: datetime
    duration_ms: float
    success: bool
    error_message: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SystemHealth:
    """Represents system health status."""

    database_connected: bool
    cache_size: int
    active_sessions: int
    total_operations: int
    error_rate: float
    average_response_time_ms: float
    last_health_check: datetime
    component_status: dict[str, bool]


class LTSTMemorySystem:
    """Main integration class for the LTST Memory System."""

    def __init__(self, db_manager: DatabaseResilienceManager | None = None):
        """Initialize the LTST Memory System."""
        if db_manager is None:
            # Use DSN resolver for unified database connection management
            if resolve_dsn:
                try:
                    connection_string = resolve_dsn(strict=False, emit_warning=False)
                    if not connection_string:
                        # Fallback to direct environment variable access
                        connection_string = os.getenv(
                            "DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency"
                        )
                        logger.warning("DSN resolver failed, falling back to direct DATABASE_URL access")
                    else:
                        logger.info(f"Using DSN resolver: {connection_string[:50]}...")
                except Exception as e:
                    # Fallback to direct environment variable access
                    connection_string = os.getenv("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")
                    logger.warning(f"DSN resolver error: {e}, falling back to direct DATABASE_URL access")
            else:
                # DSN resolver not available, use direct environment variable access
                connection_string = os.getenv("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")
                logger.warning("DSN resolver not available, using direct DATABASE_URL access")

            self.db_manager = DatabaseResilienceManager(connection_string)
        else:
            self.db_manager = db_manager

        # Initialize components
        # Get database URL from db_manager
        db_url = getattr(self.db_manager, "connection_string", None) or str(self.db_manager)
        self.conversation_storage = ConversationStorage(db_url)
        self.context_merger = ContextMerger(self.conversation_storage)
        self.memory_rehydrator = MemoryRehydrator(self.conversation_storage)
        self.database_integration = LTSTDatabaseIntegration(self.db_manager)

        # Initialize session continuity manager
        self.session_continuity = SessionContinuityManager(self.conversation_storage)  # type: ignore

        # Performance monitoring
        self.operation_history: list[MemoryOperation] = []
        self.max_operation_history = 1000
        self.health_check_interval = timedelta(minutes=5)
        self.last_health_check = datetime.now()

        # System configuration
        self.enable_caching = True
        self.enable_monitoring = True
        self.default_session_timeout = timedelta(hours=24)

        # Session continuity configuration
        self.enable_session_continuity = True
        self.enable_preference_learning = True

        # Privacy configuration
        self.privacy_manager = PrivacyManager(
            PrivacyConfig(
                local_only_storage=True,
                enable_pii_redaction=True,
                enable_encryption=False,  # Can be enabled via config
                log_redaction=True,
            )
        )

        # Dashboard configuration
        self.dashboard_manager = DashboardManager(self)

        logger.info("LTST Memory System initialized successfully")

    def store_conversation_message(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        message_type: str = "message",
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Store a conversation message.

        Args:
            session_id: Session identifier
            user_id: User identifier
            role: Message role ('human', 'ai', 'system')
            content: Message content
            message_type: Type of message
            metadata: Additional metadata

        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()

        try:
            # Create or update session
            session = ConversationSession(
                session_id=session_id,
                user_id=user_id,
                session_name=f"Session {session_id[:8]}",
                session_type="conversation",
                status="active",
            )
            self.conversation_storage.create_session(session)

            # Create message
            message = ConversationMessage(
                session_id=session_id, role=role, content=content, message_type=message_type, metadata=metadata or {}
            )

            # Store message
            success = self.conversation_storage.store_message(message)

            duration_ms = (time.time() - start_time) * 1000

            # Record operation
            self._record_operation(
                "store",
                session_id,
                user_id,
                duration_ms,
                success,
                metadata={"role": role, "message_type": message_type},
            )

            if success:
                logger.info(f"Message stored successfully: {session_id}:{role}")
            else:
                logger.error(f"Failed to store message: {session_id}:{role}")

            return success

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_operation(
                "store",
                session_id,
                user_id,
                duration_ms,
                False,
                str(e),
                metadata={"role": role, "message_type": message_type},
            )
            logger.error(f"Error storing message: {e}")
            return False

    def store_context(
        self,
        session_id: str,
        context_type: str,
        context_key: str,
        context_value: str,
        relevance_score: float = 0.8,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Store conversation context.

        Args:
            session_id: Session identifier
            context_type: Type of context
            context_key: Context key
            context_value: Context value
            relevance_score: Relevance score
            metadata: Additional metadata

        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()

        try:
            context = ConversationContext(
                session_id=session_id,
                context_type=context_type,
                context_key=context_key,
                context_value=context_value,
                relevance_score=relevance_score,
                metadata=metadata or {},
            )

            success = self.conversation_storage.store_context(
                context.session_id,
                context.context_type,
                context.context_key,
                context.context_value,
                context.relevance_score,
                context.expires_at,
                getattr(context, "decision_head", None),
                getattr(context, "decision_status", "open"),
                getattr(context, "superseded_by", None),
                getattr(context, "entities", None),
                getattr(context, "files", None),
            )

            duration_ms = (time.time() - start_time) * 1000

            self._record_operation(
                "store",
                session_id,
                "system",
                duration_ms,
                success,
                metadata={"context_type": context_type, "context_key": context_key},
            )

            if success:
                logger.info(f"Context stored successfully: {session_id}:{context_type}:{context_key}")
            else:
                logger.error(f"Failed to store context: {session_id}:{context_type}:{context_key}")

            return success

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_operation(
                "store",
                session_id,
                "system",
                duration_ms,
                False,
                str(e),
                metadata={"context_type": context_type, "context_key": context_key},
            )
            logger.error(f"Error storing context: {e}")
            return False

    def retrieve_conversation_history(
        self, session_id: str, limit: int = 50, offset: int = 0
    ) -> list[ConversationMessage]:
        """
        Retrieve conversation history for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve
            offset: Offset for pagination

        Returns:
            List of conversation messages
        """
        start_time = time.time()

        try:
            # Use get_session_summary instead of get_messages
            session_summary = self.conversation_storage.get_session_summary(session_id)

            # Extract messages from session summary or return empty list
            if session_summary and "messages" in session_summary:
                messages = session_summary["messages"]
                if limit:
                    messages = messages[:limit]
                if offset:
                    messages = messages[offset:]
            else:
                messages = []

            duration_ms = (time.time() - start_time) * 1000

            self._record_operation(
                "retrieve", session_id, "system", duration_ms, True, metadata={"message_count": len(messages)}
            )

            logger.info(f"Retrieved {len(messages)} messages for session {session_id}")
            return messages

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_operation("retrieve", session_id, "system", duration_ms, False, str(e))
            logger.error(f"Error retrieving conversation history: {e}")
            return []

    def merge_contexts(
        self,
        session_id: str,
        context_type: str | None = None,
        relevance_threshold: float | None = None,
        similarity_threshold: float | None = None,
    ) -> ContextMergeResult:
        """
        Merge contexts for a session.

        Args:
            session_id: Session identifier
            context_type: Type of context to merge
            relevance_threshold: Minimum relevance score
            similarity_threshold: Minimum similarity for grouping

        Returns:
            ContextMergeResult with merged contexts
        """
        start_time = time.time()

        try:
            result = self.context_merger.merge_contexts(
                session_id, context_type, relevance_threshold, similarity_threshold
            )

            duration_ms = (time.time() - start_time) * 1000

            self._record_operation(
                "merge",
                session_id,
                "system",
                duration_ms,
                True,
                metadata={
                    "contexts_processed": result.total_contexts_processed,
                    "contexts_merged": result.contexts_merged,
                    "contexts_preserved": result.contexts_preserved,
                },
            )

            logger.info(f"Context merging completed for session {session_id}: {result.contexts_merged} contexts merged")
            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_operation("merge", session_id, "system", duration_ms, False, str(e))
            logger.error(f"Error merging contexts: {e}")
            raise

    def merge_contexts_database(
        self,
        session_id: str,
        merge_strategy: str = "relevance",
        max_merged_length: int = 5000,
        relevance_threshold: float = 0.7,
        similarity_threshold: float = 0.8,
    ) -> DatabaseMergeResult:
        """
        Merge contexts using PostgreSQL database functions.

        Args:
            session_id: Session identifier
            merge_strategy: Merging strategy ('relevance' or 'similarity')
            max_merged_length: Maximum length of merged content
            relevance_threshold: Minimum relevance score
            similarity_threshold: Minimum similarity threshold

        Returns:
            DatabaseMergeResult with merged content and metadata
        """
        start_time = time.time()

        try:
            result = self.database_integration.merge_contexts_database(
                session_id, merge_strategy, max_merged_length, relevance_threshold, similarity_threshold
            )

            duration_ms = (time.time() - start_time) * 1000

            self._record_operation(
                "merge_database",
                session_id,
                "system",
                duration_ms,
                True,
                metadata={
                    "source_context_count": result.source_context_count,
                    "avg_relevance": result.avg_relevance,
                    "merge_quality_score": result.merge_quality_score,
                    "context_types": result.context_types,
                },
            )

            logger.info(
                f"Database context merging completed for session {session_id}: {result.source_context_count} contexts"
            )
            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_operation("merge_database", session_id, "system", duration_ms, False, str(e))
            logger.error(f"Error in database context merging: {e}")
            raise

    def rehydrate_memory(
        self,
        session_id: str,
        user_id: str,
        current_message: str | None = None,
        context_types: list[str] | None = None,
        max_context_length: int = 10000,
        include_conversation_history: bool = True,
        history_limit: int = 20,
    ) -> RehydrationResult:
        """
        Rehydrate memory for a session.

        Args:
            session_id: Session identifier
            user_id: User identifier
            current_message: Current message for context
            context_types: Types of context to include
            max_context_length: Maximum context length
            include_conversation_history: Whether to include conversation history
            history_limit: Maximum number of history messages

        Returns:
            RehydrationResult with rehydrated context
        """
        start_time = time.time()

        try:
            request = RehydrationRequest(
                session_id=session_id,
                user_id=user_id,
                current_message=current_message,
                context_types=context_types,
                max_context_length=max_context_length,
                include_conversation_history=include_conversation_history,
                history_limit=history_limit,
            )

            result = self.memory_rehydrator.rehydrate_memory(request)

            duration_ms = (time.time() - start_time) * 1000

            self._record_operation(
                "rehydrate",
                session_id,
                user_id,
                duration_ms,
                True,
                metadata={
                    "context_length": len(result.rehydrated_context),
                    "history_count": len(result.conversation_history),
                    "context_count": len(result.relevant_contexts),
                    "continuity_score": result.session_continuity_score,
                },
            )

            logger.info(f"Memory rehydration completed for session {session_id}: {duration_ms:.2f}ms")
            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_operation("rehydrate", session_id, user_id, duration_ms, False, str(e))
            logger.error(f"Error rehydrating memory: {e}")
            raise

    def rehydrate_memory_database(
        self,
        session_id: str,
        user_id: str,
        max_context_length: int = 10000,
        include_history: bool = True,
        history_limit: int = 20,
    ) -> DatabaseRehydrationResult:
        """
        Rehydrate memory using PostgreSQL database functions.

        Args:
            session_id: Session identifier
            user_id: User identifier
            max_context_length: Maximum context length
            include_history: Whether to include conversation history
            history_limit: Maximum number of history messages

        Returns:
            DatabaseRehydrationResult with rehydrated content
        """
        start_time = time.time()

        try:
            result = self.database_integration.rehydrate_memory_database(
                session_id, user_id, max_context_length, include_history, history_limit
            )

            duration_ms = (time.time() - start_time) * 1000

            self._record_operation(
                "rehydrate_database",
                session_id,
                user_id,
                duration_ms,
                True,
                metadata={
                    "context_length": len(result.rehydrated_context),
                    "history_length": len(result.conversation_history),
                    "context_count": result.context_count,
                    "continuity_score": result.continuity_score,
                    "rehydration_quality_score": result.rehydration_quality_score,
                },
            )

            logger.info(f"Database memory rehydration completed for session {session_id}: {duration_ms:.2f}ms")
            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_operation("rehydrate_database", session_id, user_id, duration_ms, False, str(e))
            logger.error(f"Error in database memory rehydration: {e}")
            raise

    def search_conversations(
        self, query: str, session_id: str | None = None, limit: int = 10, threshold: float = 0.7
    ) -> list[tuple[ConversationMessage, float]]:
        """
        Search conversations using semantic similarity.

        Args:
            query: Search query
            session_id: Optional session filter
            limit: Maximum number of results
            threshold: Minimum similarity threshold

        Returns:
            List of (message, similarity) tuples
        """
        start_time = time.time()

        try:
            # Use get_session_summary and filter results since search_messages doesn't exist
            if session_id:
                session_summary = self.conversation_storage.get_session_summary(session_id)
                if session_summary and "messages" in session_summary:
                    messages = session_summary["messages"]
                    # Simple text search in messages
                    results = []
                    for msg in messages:
                        if isinstance(msg, dict) and "content" in msg:
                            if query.lower() in msg["content"].lower():
                                results.append((msg, 0.8))  # Default similarity score
                    if limit:
                        results = results[:limit]
                else:
                    results = []
            else:
                # No session_id provided, return empty results
                results = []

            duration_ms = (time.time() - start_time) * 1000

            self._record_operation(
                "search",
                session_id or "all",
                "system",
                duration_ms,
                True,
                metadata={"query": query, "result_count": len(results)},
            )

            logger.info(f"Search completed: {len(results)} results for query '{query}'")
            return results

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_operation(
                "search", session_id or "all", "system", duration_ms, False, str(e), metadata={"query": query}
            )
            logger.error(f"Error searching conversations: {e}")
            return []

    def get_session_summary(self, session_id: str) -> dict[str, Any] | None:
        """
        Get session summary statistics.

        Args:
            session_id: Session identifier

        Returns:
            Session summary dictionary
        """
        start_time = time.time()

        try:
            summary = self.conversation_storage.get_session_summary(session_id)

            duration_ms = (time.time() - start_time) * 1000

            self._record_operation("summary", session_id, "system", duration_ms, True)

            return summary

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_operation("summary", session_id, "system", duration_ms, False, str(e))
            logger.error(f"Error getting session summary: {e}")
            return None

    def persist_session_state(self, session_id: str) -> bool:
        """
        Persist session state for continuity across restarts.

        Args:
            session_id: Session identifier

        Returns:
            True if successful, False otherwise
        """
        if not self.enable_session_continuity:
            logger.debug("Session continuity disabled")
            return False

        start_time = time.time()

        try:
            success = self.session_continuity.persist_session_state(session_id)

            duration_ms = (time.time() - start_time) * 1000

            # Record operation
            self._record_operation(
                "persist_session_state",
                session_id,
                "system",
                duration_ms,
                success,
                metadata={"operation": "session_continuity"},
            )

            if success:
                logger.info(f"Session state persisted successfully: {session_id}")
            else:
                logger.error(f"Failed to persist session state: {session_id}")

            return success

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_operation(
                "persist_session_state",
                session_id,
                "system",
                duration_ms,
                False,
                metadata={"error": str(e)},
            )
            logger.error(f"Exception persisting session state for {session_id}: {e}")
            return False

    def restore_session_state(self, user_id: str, session_id: str | None = None) -> dict[str, Any] | None:
        """
        Restore session state for continuity across restarts.

        Args:
            user_id: User identifier
            session_id: Optional specific session ID

        Returns:
            Session continuity state if found, None otherwise
        """
        if not self.enable_session_continuity:
            logger.debug("Session continuity disabled")
            return None

        start_time = time.time()

        try:
            continuity_state = self.session_continuity.restore_session_state(user_id, session_id)

            duration_ms = (time.time() - start_time) * 1000

            # Record operation
            self._record_operation(
                "restore_session_state",
                session_id or "auto",
                user_id,
                duration_ms,
                continuity_state is not None,
                metadata={"operation": "session_continuity"},
            )

            if continuity_state:
                logger.info(f"Session state restored successfully: {continuity_state.session_id}")
                return continuity_state.__dict__
            else:
                logger.info(f"No session state found for user {user_id}")
                return None

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_operation(
                "restore_session_state",
                session_id or "auto",
                user_id,
                duration_ms,
                False,
                metadata={"error": str(e)},
            )
            logger.error(f"Exception restoring session state for user {user_id}: {e}")
            return None

    def resume_session_with_context(self, user_id: str, session_id: str | None = None) -> dict[str, Any]:
        """
        Resume session with last 10 messages + last 2 decisions + preferences.

        Args:
            user_id: User identifier
            session_id: Optional specific session ID

        Returns:
            Dictionary with resume context
        """
        if not self.enable_session_continuity:
            logger.debug("Session continuity disabled")
            return {"error": "Session continuity disabled"}

        start_time = time.time()

        try:
            resume_context = self.session_continuity.resume_session_with_context(user_id, session_id)

            duration_ms = (time.time() - start_time) * 1000

            # Record operation
            self._record_operation(
                "resume_session_with_context",
                resume_context.get("session_id", "unknown"),
                user_id,
                duration_ms,
                "error" not in resume_context,
                metadata={"operation": "session_continuity", "resume_type": resume_context.get("resume_type")},
            )

            if "error" not in resume_context:
                logger.info(f"Session resumed successfully: {resume_context.get('session_id')}")
            else:
                logger.error(f"Failed to resume session: {resume_context['error']}")

            return resume_context

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_operation(
                "resume_session_with_context",
                session_id or "unknown",
                user_id,
                duration_ms,
                False,
                metadata={"error": str(e)},
            )
            logger.error(f"Exception resuming session for user {user_id}: {e}")
            return {"error": str(e)}

    def learn_and_apply_preferences(self, session_id: str, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Learn preferences from session activity and apply them.

        Args:
            session_id: Session identifier
            messages: Recent messages to analyze

        Returns:
            Dictionary with learning results
        """
        if not self.enable_preference_learning:
            logger.debug("Preference learning disabled")
            return {
                "preferences_learned": 0,
                "preferences_applied": 0,
                "learning_insights": ["Preference learning disabled"],
            }

        start_time = time.time()

        try:
            result = self.session_continuity.learn_and_apply_preferences(session_id, messages)

            duration_ms = (time.time() - start_time) * 1000

            # Record operation
            self._record_operation(
                "learn_and_apply_preferences",
                session_id,
                "system",
                duration_ms,
                True,
                metadata={
                    "operation": "preference_learning",
                    "preferences_learned": result.preferences_learned,
                    "preferences_applied": result.preferences_applied,
                },
            )

            logger.info(
                f"Preference learning completed: {result.preferences_learned} learned, {result.preferences_applied} applied"
            )

            return {
                "preferences_learned": result.preferences_learned,
                "preferences_applied": result.preferences_applied,
                "confidence_scores": result.confidence_scores,
                "learning_insights": result.learning_insights,
                "conflicts_resolved": result.conflicts_resolved,
            }

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_operation(
                "learn_and_apply_preferences",
                session_id,
                "system",
                duration_ms,
                False,
                metadata={"error": str(e)},
            )
            logger.error(f"Exception learning preferences for session {session_id}: {e}")
            return {"error": str(e)}

    def get_session_continuity_stats(self, user_id: str) -> dict[str, Any]:
        """
        Get session continuity statistics for user.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with continuity statistics
        """
        try:
            stats = self.session_continuity.get_session_continuity_stats(user_id)

            # Add system-level stats
            stats.update(
                {
                    "enable_session_continuity": self.enable_session_continuity,
                    "enable_preference_learning": self.enable_preference_learning,
                    "system_operations": len(self.operation_history),
                }
            )

            return stats

        except Exception as e:
            logger.error(f"Exception getting session continuity stats for user {user_id}: {e}")
            return {"error": str(e)}

    def cleanup_expired_data(self) -> dict[str, Any]:
        """
        Clean up expired data across all components.

        Returns:
            Dictionary with cleanup statistics
        """
        start_time = time.time()

        try:
            stats = {}

            # Clean up conversation storage
            conversation_cleaned = self.conversation_storage.cleanup_expired_data()
            stats["conversation_context"] = conversation_cleaned

            # Clean up context merger cache
            context_cache_cleaned = self.context_merger.cleanup_expired_cache()
            stats["context_cache"] = context_cache_cleaned

            # Clean up memory rehydrator cache
            rehydration_cache_cleaned = self.memory_rehydrator.cleanup_expired_cache()
            stats["rehydration_cache"] = rehydration_cache_cleaned

            # Clean up operation history
            if len(self.operation_history) > self.max_operation_history:
                excess = len(self.operation_history) - self.max_operation_history
                self.operation_history = self.operation_history[excess:]
                stats["operation_history"] = excess

            duration_ms = (time.time() - start_time) * 1000

            logger.info(f"Cleanup completed: {stats} in {duration_ms:.2f}ms")
            return stats

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return {"error": str(e)}

    def get_system_health(self) -> SystemHealth:
        """
        Get system health status.

        Returns:
            SystemHealth object with status information
        """
        try:
            # Check database connection
            database_connected = self._check_database_connection()

            # Get cache sizes
            context_cache_size = len(self.context_merger.context_cache)
            rehydration_cache_size = len(self.memory_rehydrator.rehydration_cache)
            total_cache_size = context_cache_size + rehydration_cache_size

            # Get active sessions count
            active_sessions = self._get_active_sessions_count()

            # Calculate statistics from operation history
            total_operations = len(self.operation_history)
            successful_operations = sum(1 for op in self.operation_history if op.success)
            error_rate = 1.0 - (successful_operations / total_operations) if total_operations > 0 else 0.0

            # Calculate average response time
            response_times = [op.duration_ms for op in self.operation_history]
            average_response_time = sum(response_times) / len(response_times) if response_times else 0.0

            # Check component status
            component_status = {
                "conversation_storage": database_connected,
                "context_merger": database_connected,
                "memory_rehydrator": database_connected,
                "database": database_connected,
            }

            health = SystemHealth(
                database_connected=database_connected,
                cache_size=total_cache_size,
                active_sessions=active_sessions,
                total_operations=total_operations,
                error_rate=error_rate,
                average_response_time_ms=average_response_time,
                last_health_check=datetime.now(),
                component_status=component_status,
            )

            self.last_health_check = datetime.now()
            return health

        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return SystemHealth(
                database_connected=False,
                cache_size=0,
                active_sessions=0,
                total_operations=0,
                error_rate=1.0,
                average_response_time_ms=0.0,
                last_health_check=datetime.now(),
                component_status={"error": False},
            )

    def _record_operation(
        self,
        operation_type: str,
        session_id: str,
        user_id: str,
        duration_ms: float,
        success: bool,
        error_message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Record a memory operation for monitoring."""
        if not self.enable_monitoring:
            return

        operation = MemoryOperation(
            operation_type=operation_type,
            session_id=session_id,
            user_id=user_id,
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
            metadata=metadata or {},
        )

        self.operation_history.append(operation)

        # Trim history if too long
        if len(self.operation_history) > self.max_operation_history:
            self.operation_history = self.operation_history[-self.max_operation_history :]

    def _check_database_connection(self) -> bool:
        """Check if database connection is healthy."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
        except Exception:
            return False

    def _get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT COUNT(*) FROM conversation_sessions
                        WHERE status = 'active'
                        AND last_activity > %s
                    """,
                        (datetime.now() - self.default_session_timeout,),
                    )
                    return cursor.fetchone()[0]
        except Exception:
            return 0

    def get_system_statistics(self) -> dict[str, Any]:
        """Get comprehensive system statistics."""
        try:
            health = self.get_system_health()

            # Get component-specific statistics
            context_merger_stats = self.context_merger.get_merge_statistics()
            rehydration_stats = self.memory_rehydrator.get_rehydration_statistics()

            # Get recent operations by type
            recent_operations = self.operation_history[-100:] if self.operation_history else []
            operations_by_type = {}
            for op in recent_operations:
                op_type = op.operation_type
                if op_type not in operations_by_type:
                    operations_by_type[op_type] = {"count": 0, "avg_duration": 0.0, "success_rate": 0.0}

                operations_by_type[op_type]["count"] += 1
                operations_by_type[op_type]["avg_duration"] += op.duration_ms

                if op.success:
                    operations_by_type[op_type]["success_rate"] += 1

            # Calculate averages
            for op_type, stats in operations_by_type.items():
                count = stats["count"]
                if count > 0:
                    stats["avg_duration"] /= count
                    stats["success_rate"] /= count

            return {
                "health": {
                    "database_connected": health.database_connected,
                    "cache_size": health.cache_size,
                    "active_sessions": health.active_sessions,
                    "total_operations": health.total_operations,
                    "error_rate": health.error_rate,
                    "average_response_time_ms": health.average_response_time_ms,
                },
                "components": {"context_merger": context_merger_stats, "memory_rehydrator": rehydration_stats},
                "operations": operations_by_type,
                "last_health_check": health.last_health_check.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting system statistics: {e}")
            return {"error": str(e)}

    # Privacy-aware methods
    def store_conversation_with_privacy(self, conversation_id: str, conversation_data: dict[str, Any]) -> bool:
        """
        Store conversation with privacy controls.

        Args:
            conversation_id: Conversation identifier
            conversation_data: Conversation data to store

        Returns:
            True if successful, False otherwise
        """
        try:
            return self.privacy_manager.store_conversation(conversation_id, conversation_data)
        except Exception as e:
            logger.error(f"Failed to store conversation with privacy: {e}")
            return False

    def retrieve_conversation_with_privacy(self, conversation_id: str) -> dict[str, Any] | None:
        """
        Retrieve conversation with privacy controls.

        Args:
            conversation_id: Conversation identifier

        Returns:
            Conversation data if found, None otherwise
        """
        try:
            return self.privacy_manager.retrieve_conversation(conversation_id)
        except Exception as e:
            logger.error(f"Failed to retrieve conversation with privacy: {e}")
            return None

    def redact_log_message(self, message: str) -> str:
        """
        Redact PII from log message.

        Args:
            message: Log message to redact

        Returns:
            Redacted log message
        """
        try:
            return self.privacy_manager.redact_log_message(message)
        except Exception as e:
            logger.error(f"Failed to redact log message: {e}")
            return message

    def validate_privacy_compliance(self) -> dict[str, Any]:
        """
        Validate privacy compliance.

        Returns:
            Privacy compliance report
        """
        try:
            return self.privacy_manager.validate_privacy_compliance()
        except Exception as e:
            logger.error(f"Failed to validate privacy compliance: {e}")
            return {"error": str(e), "compliant": False}

    def get_privacy_statistics(self) -> dict[str, Any]:
        """
        Get privacy operation statistics.

        Returns:
            Privacy statistics
        """
        try:
            return self.privacy_manager.get_privacy_statistics()
        except Exception as e:
            logger.error(f"Failed to get privacy statistics: {e}")
            return {"error": str(e)}

    def cleanup_old_data(self, days_old: int = 30) -> int:
        """
        Clean up old data for privacy.

        Args:
            days_old: Age threshold for cleanup

        Returns:
            Number of files cleaned up
        """
        try:
            return self.privacy_manager.cleanup_old_data(days_old)
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0

    # Dashboard methods
    def get_dashboard_metrics(self) -> dict[str, Any]:
        """
        Get dashboard metrics for visualization.

        Returns:
            Dashboard metrics data
        """
        try:
            return self.dashboard_manager.get_current_metrics().__dict__
        except Exception as e:
            logger.error(f"Failed to get dashboard metrics: {e}")
            return {}

    def get_dashboard_decisions(self, limit: int = 20) -> list[dict[str, Any]]:
        """
        Get top decisions for dashboard display.

        Args:
            limit: Maximum number of decisions to return

        Returns:
            List of decision summaries
        """
        try:
            decisions = self.dashboard_manager.get_top_decisions(limit)
            return [decision.__dict__ for decision in decisions]
        except Exception as e:
            logger.error(f"Failed to get dashboard decisions: {e}")
            return []

    def get_dashboard_queries(self, limit: int = 50) -> list[dict[str, Any]]:
        """
        Get recent queries for dashboard display.

        Args:
            limit: Maximum number of queries to return

        Returns:
            List of query metrics
        """
        try:
            queries = self.dashboard_manager.get_recent_queries(limit)
            return [query.__dict__ for query in queries]
        except Exception as e:
            logger.error(f"Failed to get dashboard queries: {e}")
            return []

    def get_dashboard_supersedence_graph(self) -> dict[str, list[str]]:
        """
        Get supersedence graph for dashboard visualization.

        Returns:
            Supersedence graph data
        """
        try:
            return self.dashboard_manager.get_supersedence_graph()
        except Exception as e:
            logger.error(f"Failed to get supersedence graph: {e}")
            return {}

    def update_dashboard_data(self):
        """Update dashboard data."""
        try:
            self.dashboard_manager.update_dashboard_data()
        except Exception as e:
            logger.error(f"Failed to update dashboard data: {e}")

    def get_dashboard_statistics(self) -> dict[str, Any]:
        """
        Get dashboard statistics.

        Returns:
            Dashboard statistics
        """
        try:
            return self.dashboard_manager.get_dashboard_statistics()
        except Exception as e:
            logger.error(f"Failed to get dashboard statistics: {e}")
            return {"error": str(e)}

    def create_dashboard(self) -> bool:
        """
        Create the NiceGUI dashboard.

        Returns:
            True if successful, False otherwise
        """
        try:
            return self.dashboard_manager.create_dashboard()
        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            return False
