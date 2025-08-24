"""
LTST Memory System - Main Integration Class

This module provides the main integration class for the LTST Memory System,
combining conversation storage, context merging, and memory rehydration capabilities.
"""

import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .context_merger import ContextMerger, ContextMergeResult
from .conversation_storage import ConversationContext, ConversationMessage, ConversationSession, ConversationStorage
from .database_resilience import DatabaseResilienceManager
from .logger import setup_logger
from .memory_rehydrator import MemoryRehydrator, RehydrationRequest, RehydrationResult

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
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

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
    component_status: Dict[str, bool]


class LTSTMemorySystem:
    """Main integration class for the LTST Memory System."""

    def __init__(self, db_manager: Optional[DatabaseResilienceManager] = None):
        """Initialize the LTST Memory System."""
        if db_manager is None:
            import os

            connection_string = os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")
            self.db_manager = DatabaseResilienceManager(connection_string)
        else:
            self.db_manager = db_manager

        # Initialize components
        self.conversation_storage = ConversationStorage(self.db_manager)
        self.context_merger = ContextMerger(self.db_manager)
        self.memory_rehydrator = MemoryRehydrator(self.db_manager)

        # Performance monitoring
        self.operation_history: List[MemoryOperation] = []
        self.max_operation_history = 1000
        self.health_check_interval = timedelta(minutes=5)
        self.last_health_check = datetime.now()

        # System configuration
        self.enable_caching = True
        self.enable_monitoring = True
        self.default_session_timeout = timedelta(hours=24)

        logger.info("LTST Memory System initialized successfully")

    def store_conversation_message(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        message_type: str = "message",
        metadata: Optional[Dict[str, Any]] = None,
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
        metadata: Optional[Dict[str, Any]] = None,
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

            success = self.conversation_storage.store_context(context)

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
    ) -> List[ConversationMessage]:
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
            messages = self.conversation_storage.get_messages(session_id, limit, offset)

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
        context_type: Optional[str] = None,
        relevance_threshold: Optional[float] = None,
        similarity_threshold: Optional[float] = None,
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

    def rehydrate_memory(
        self,
        session_id: str,
        user_id: str,
        current_message: Optional[str] = None,
        context_types: Optional[List[str]] = None,
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

    def search_conversations(
        self, query: str, session_id: Optional[str] = None, limit: int = 10, threshold: float = 0.7
    ) -> List[Tuple[ConversationMessage, float]]:
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
            results = self.conversation_storage.search_messages(query, session_id, limit, threshold)

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

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
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

    def cleanup_expired_data(self) -> Dict[str, int]:
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
                component_status={"error": str(e)},
            )

    def _record_operation(
        self,
        operation_type: str,
        session_id: str,
        user_id: str,
        duration_ms: float,
        success: bool,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
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

    def get_system_statistics(self) -> Dict[str, Any]:
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
