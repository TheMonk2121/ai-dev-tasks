"""
LTST Database Integration - PostgreSQL Function Integration

This module provides integration between the Python LTST Memory System
and the PostgreSQL functions for context merging and memory rehydration.
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from psycopg2.extras import RealDictCursor

from .database_resilience import DatabaseResilienceManager
from .logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class DatabaseMergeResult:
    """Result from database context merging."""

    merged_content: str
    source_context_count: int
    avg_relevance: float
    merge_quality_score: float
    context_types: List[str]


@dataclass
class DatabaseRehydrationResult:
    """Result from database memory rehydration."""

    session_id: str
    user_id: str
    rehydrated_context: str
    conversation_history: str
    user_preferences: str
    continuity_score: float
    context_count: int
    rehydration_quality_score: float
    cache_hit: bool


class LTSTDatabaseIntegration:
    """Integration layer for PostgreSQL LTST functions."""

    def __init__(self, db_manager: Optional[DatabaseResilienceManager] = None):
        """Initialize database integration."""
        if db_manager is None:
            import os

            connection_string = os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")
            self.db_manager = DatabaseResilienceManager(connection_string)
        else:
            self.db_manager = db_manager

    def merge_contexts_database(
        self,
        session_id: str,
        merge_strategy: str = "relevance",
        max_merged_length: int = 5000,
        relevance_threshold: float = 0.7,
        similarity_threshold: float = 0.8,
    ) -> DatabaseMergeResult:
        """
        Merge contexts using PostgreSQL function.

        Args:
            session_id: Session identifier
            merge_strategy: Merging strategy ('relevance' or 'similarity')
            max_merged_length: Maximum length of merged content
            relevance_threshold: Minimum relevance score
            similarity_threshold: Minimum similarity threshold

        Returns:
            DatabaseMergeResult with merged content and metadata
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM merge_contexts_intelligent(
                            %s, %s, %s, %s, %s
                        )
                    """,
                        (session_id, merge_strategy, max_merged_length, relevance_threshold, similarity_threshold),
                    )

                    result = cursor.fetchone()

                    if result:
                        return DatabaseMergeResult(
                            merged_content=result["merged_content"] or "",
                            source_context_count=result["source_context_count"] or 0,
                            avg_relevance=result["avg_relevance"] or 0.0,
                            merge_quality_score=result["merge_quality_score"] or 0.0,
                            context_types=result["context_types"] or [],
                        )
                    else:
                        return DatabaseMergeResult(
                            merged_content="",
                            source_context_count=0,
                            avg_relevance=0.0,
                            merge_quality_score=0.0,
                            context_types=[],
                        )

        except Exception as e:
            logger.error(f"Error in database context merging: {e}")
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
        Rehydrate memory using PostgreSQL function.

        Args:
            session_id: Session identifier
            user_id: User identifier
            max_context_length: Maximum context length
            include_history: Whether to include conversation history
            history_limit: Maximum number of history messages

        Returns:
            DatabaseRehydrationResult with rehydrated content
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM rehydrate_memory_automatic(
                            %s, %s, %s, %s, %s
                        )
                    """,
                        (session_id, user_id, max_context_length, include_history, history_limit),
                    )

                    result = cursor.fetchone()

                    if result:
                        return DatabaseRehydrationResult(
                            session_id=result["session_id"] or session_id,
                            user_id=result["user_id"] or user_id,
                            rehydrated_context=result["rehydrated_context"] or "",
                            conversation_history=result["conversation_history"] or "",
                            user_preferences=result["user_preferences"] or "{}",
                            continuity_score=result["continuity_score"] or 0.0,
                            context_count=result["context_count"] or 0,
                            rehydration_quality_score=result["rehydration_quality_score"] or 0.0,
                            cache_hit=result["cache_hit"] or False,
                        )
                    else:
                        return DatabaseRehydrationResult(
                            session_id=session_id,
                            user_id=user_id,
                            rehydrated_context="",
                            conversation_history="",
                            user_preferences="{}",
                            continuity_score=0.0,
                            context_count=0,
                            rehydration_quality_score=0.0,
                            cache_hit=False,
                        )

        except Exception as e:
            logger.error(f"Error in database memory rehydration: {e}")
            raise

    def get_session_continuity(self, session_id: str, continuity_window_hours: int = 24) -> Dict[str, Any]:
        """
        Get session continuity information.

        Args:
            session_id: Session identifier
            continuity_window_hours: Continuity window in hours

        Returns:
            Dictionary with continuity information
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM detect_session_continuity(%s, %s)
                    """,
                        (session_id, continuity_window_hours),
                    )

                    result = cursor.fetchone()

                    if result:
                        return dict(result)
                    else:
                        return {
                            "session_id": session_id,
                            "continuity_score": 0.0,
                            "last_activity": None,
                            "hours_since_last_activity": 999,
                            "message_count": 0,
                            "is_continuous": False,
                        }

        except Exception as e:
            logger.error(f"Error getting session continuity: {e}")
            raise

    def get_context_statistics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get context merging statistics.

        Args:
            session_id: Optional session filter

        Returns:
            Dictionary with context statistics
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM get_context_statistics(%s)
                    """,
                        (session_id,),
                    )

                    result = cursor.fetchone()

                    if result:
                        return dict(result)
                    else:
                        return {
                            "total_contexts": 0,
                            "avg_relevance": 0.0,
                            "context_types": [],
                            "recent_activity_hours": 0,
                            "cache_hit_ratio": 0.0,
                            "merge_operations_count": 0,
                        }

        except Exception as e:
            logger.error(f"Error getting context statistics: {e}")
            raise

    def get_rehydration_statistics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get memory rehydration statistics.

        Args:
            session_id: Optional session filter

        Returns:
            Dictionary with rehydration statistics
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM get_rehydration_statistics(%s)
                    """,
                        (session_id,),
                    )

                    result = cursor.fetchone()

                    if result:
                        return dict(result)
                    else:
                        return {
                            "total_sessions": 0,
                            "active_sessions": 0,
                            "avg_continuity_score": 0.0,
                            "avg_context_count": 0,
                            "avg_rehydration_quality": 0.0,
                            "cache_hit_ratio": 0.0,
                            "rehydration_operations_count": 0,
                        }

        except Exception as e:
            logger.error(f"Error getting rehydration statistics: {e}")
            raise

    def optimize_caches(self) -> Dict[str, Any]:
        """
        Optimize both context and rehydration caches.

        Returns:
            Dictionary with optimization results
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Optimize context cache
                    cursor.execute("SELECT * FROM optimize_context_cache()")
                    context_result = cursor.fetchone()

                    # Optimize rehydration cache
                    cursor.execute("SELECT * FROM optimize_rehydration_cache()")
                    rehydration_result = cursor.fetchone()

                    return {
                        "context_cache": dict(context_result) if context_result else {},
                        "rehydration_cache": dict(rehydration_result) if rehydration_result else {},
                    }

        except Exception as e:
            logger.error(f"Error optimizing caches: {e}")
            raise

    def test_database_functions(self) -> Dict[str, bool]:
        """
        Test all database functions.

        Returns:
            Dictionary with test results
        """
        test_results = {}

        try:
            # Test context merging
            test_session = f"test_integration_{int(time.time())}"
            merge_result = self.merge_contexts_database(test_session, relevance_threshold=0.1)
            test_results["context_merging"] = True

            # Test memory rehydration
            rehydration_result = self.rehydrate_memory_database(test_session, "test_user")
            test_results["memory_rehydration"] = True

            # Test session continuity
            continuity_result = self.get_session_continuity(test_session)
            test_results["session_continuity"] = True

            # Test statistics
            context_stats = self.get_context_statistics()
            test_results["context_statistics"] = True

            rehydration_stats = self.get_rehydration_statistics()
            test_results["rehydration_statistics"] = True

            logger.info("All database function tests passed")

        except Exception as e:
            logger.error(f"Database function test failed: {e}")
            test_results["error"] = str(e)

        return test_results
