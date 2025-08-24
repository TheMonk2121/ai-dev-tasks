"""
Context Merger for LTST Memory System

This module provides intelligent context merging capabilities for the LTST Memory System,
including relevance-based context selection, semantic similarity matching, and performance optimization.
"""

import hashlib
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from psycopg2.extras import RealDictCursor

from .conversation_storage import ConversationContext
from .database_resilience import DatabaseResilienceManager
from .logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class MergedContext:
    """Represents merged context with metadata."""

    session_id: str
    context_type: str
    merged_content: str
    source_contexts: List[ConversationContext]
    relevance_score: float
    semantic_similarity: float
    merge_timestamp: datetime
    metadata: Dict[str, Any]

    def __post_init__(self):
        """Initialize computed fields."""
        if self.merge_timestamp is None:
            self.merge_timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

    @property
    def context_hash(self) -> str:
        """Generate hash for merged context."""
        content = f"{self.session_id}:{self.context_type}:{self.merged_content}"
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class ContextMergeResult:
    """Result of context merging operation."""

    merged_contexts: List[MergedContext]
    total_contexts_processed: int
    contexts_merged: int
    contexts_preserved: int
    merge_time_ms: float
    relevance_threshold: float
    similarity_threshold: float


class ContextMerger:
    """Handles intelligent context merging for the LTST Memory System."""

    def __init__(self, db_manager: Optional[DatabaseResilienceManager] = None):
        """Initialize context merger."""
        if db_manager is None:
            import os

            connection_string = os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")
            self.db_manager = DatabaseResilienceManager(connection_string)
        else:
            self.db_manager = db_manager

        # Cache for performance optimization
        self.context_cache = {}
        self.cache_ttl = timedelta(minutes=30)
        self.cache_timestamps = {}

        # Configuration
        self.default_relevance_threshold = 0.7
        self.default_similarity_threshold = 0.8
        self.max_contexts_per_merge = 10
        self.max_merge_content_length = 5000

    def _get_cached_contexts(self, session_id: str, context_type: str) -> Optional[List[ConversationContext]]:
        """Get contexts from cache if available and fresh."""
        cache_key = f"{session_id}:{context_type}"

        if cache_key in self.context_cache:
            timestamp = self.cache_timestamps.get(cache_key)
            if timestamp and datetime.now() - timestamp < self.cache_ttl:
                return self.context_cache[cache_key]

        return None

    def _cache_contexts(self, session_id: str, context_type: str, contexts: List[ConversationContext]):
        """Cache contexts for future use."""
        cache_key = f"{session_id}:{context_type}"
        self.context_cache[cache_key] = contexts
        self.cache_timestamps[cache_key] = datetime.now()

    def _calculate_semantic_similarity(self, context1: ConversationContext, context2: ConversationContext) -> float:
        """Calculate semantic similarity between two contexts."""
        try:
            # Simple text-based similarity for now
            # In production, this would use embeddings and vector similarity
            text1 = context1.context_value.lower()
            text2 = context2.context_value.lower()

            # Tokenize and calculate Jaccard similarity
            tokens1 = set(text1.split())
            tokens2 = set(text2.split())

            if not tokens1 or not tokens2:
                return 0.0

            intersection = len(tokens1.intersection(tokens2))
            union = len(tokens1.union(tokens2))

            return intersection / union if union > 0 else 0.0

        except Exception as e:
            logger.warning(f"Error calculating semantic similarity: {e}")
            return 0.0

    def _merge_context_content(self, contexts: List[ConversationContext]) -> str:
        """Merge context content intelligently."""
        if not contexts:
            return ""

        if len(contexts) == 1:
            return contexts[0].context_value

        # Sort by relevance score
        sorted_contexts = sorted(contexts, key=lambda x: x.relevance_score, reverse=True)

        # Start with the most relevant context
        merged_content = sorted_contexts[0].context_value

        # Add additional context with deduplication
        for context in sorted_contexts[1:]:
            if len(merged_content) + len(context.context_value) > self.max_merge_content_length:
                break

            # Check for overlap
            if context.context_value not in merged_content:
                merged_content += f"\n\n{context.context_value}"

        return merged_content.strip()

    def _select_relevant_contexts(
        self, contexts: List[ConversationContext], relevance_threshold: float
    ) -> List[ConversationContext]:
        """Select contexts based on relevance threshold."""
        relevant_contexts = [context for context in contexts if context.relevance_score >= relevance_threshold]

        # Sort by relevance score
        relevant_contexts.sort(key=lambda x: x.relevance_score, reverse=True)

        # Limit to max contexts per merge
        return relevant_contexts[: self.max_contexts_per_merge]

    def _group_similar_contexts(
        self, contexts: List[ConversationContext], similarity_threshold: float
    ) -> List[List[ConversationContext]]:
        """Group contexts by semantic similarity."""
        if not contexts:
            return []

        groups = []
        used_indices = set()

        for i, context in enumerate(contexts):
            if i in used_indices:
                continue

            # Start a new group
            group = [context]
            used_indices.add(i)

            # Find similar contexts
            for j, other_context in enumerate(contexts[i + 1 :], i + 1):
                if j in used_indices:
                    continue

                similarity = self._calculate_semantic_similarity(context, other_context)
                if similarity >= similarity_threshold:
                    group.append(other_context)
                    used_indices.add(j)

            groups.append(group)

        return groups

    def merge_contexts(
        self,
        session_id: str,
        context_type: Optional[str] = None,
        relevance_threshold: Optional[float] = None,
        similarity_threshold: Optional[float] = None,
    ) -> ContextMergeResult:
        """
        Merge contexts for a session based on relevance and similarity.

        Args:
            session_id: Session identifier
            context_type: Type of context to merge (optional)
            relevance_threshold: Minimum relevance score (default: 0.7)
            similarity_threshold: Minimum similarity for grouping (default: 0.8)

        Returns:
            ContextMergeResult with merged contexts and statistics
        """
        start_time = time.time()

        relevance_threshold = relevance_threshold or self.default_relevance_threshold
        similarity_threshold = similarity_threshold or self.default_similarity_threshold

        try:
            # Get contexts from cache or database
            cached_contexts = self._get_cached_contexts(session_id, context_type)

            if cached_contexts is not None:
                contexts = cached_contexts
                logger.debug(f"Using cached contexts for {session_id}:{context_type}")
            else:
                # Fetch contexts from database
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

                # Cache the contexts
                self._cache_contexts(session_id, context_type or "all", contexts)

            if not contexts:
                return ContextMergeResult(
                    merged_contexts=[],
                    total_contexts_processed=0,
                    contexts_merged=0,
                    contexts_preserved=0,
                    merge_time_ms=(time.time() - start_time) * 1000,
                    relevance_threshold=relevance_threshold,
                    similarity_threshold=similarity_threshold,
                )

            # Select relevant contexts
            relevant_contexts = self._select_relevant_contexts(contexts, relevance_threshold)

            # Group similar contexts
            context_groups = self._group_similar_contexts(relevant_contexts, similarity_threshold)

            # Merge each group
            merged_contexts = []
            contexts_merged = 0
            contexts_preserved = 0

            for group in context_groups:
                if len(group) == 1:
                    # Single context, preserve as-is
                    context = group[0]
                    merged_context = MergedContext(
                        session_id=context.session_id,
                        context_type=context.context_type,
                        merged_content=context.context_value,
                        source_contexts=[context],
                        relevance_score=context.relevance_score,
                        semantic_similarity=1.0,
                        merge_timestamp=datetime.now(),
                        metadata=context.metadata,
                    )
                    merged_contexts.append(merged_context)
                    contexts_preserved += 1
                else:
                    # Multiple contexts, merge them
                    merged_content = self._merge_context_content(group)
                    avg_relevance = sum(c.relevance_score for c in group) / len(group)

                    # Calculate average similarity within group
                    similarities = []
                    for i, context1 in enumerate(group):
                        for context2 in group[i + 1 :]:
                            similarity = self._calculate_semantic_similarity(context1, context2)
                            similarities.append(similarity)

                    avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0

                    merged_context = MergedContext(
                        session_id=session_id,
                        context_type=group[0].context_type,
                        merged_content=merged_content,
                        source_contexts=group,
                        relevance_score=avg_relevance,
                        semantic_similarity=avg_similarity,
                        merge_timestamp=datetime.now(),
                        metadata={"merged_from": len(group), "source_contexts": [c.context_key for c in group]},
                    )
                    merged_contexts.append(merged_context)
                    contexts_merged += len(group)

            merge_time_ms = (time.time() - start_time) * 1000

            logger.info(
                f"Context merging completed for session {session_id}: "
                f"{len(merged_contexts)} merged contexts, "
                f"{contexts_merged} contexts merged, "
                f"{contexts_preserved} contexts preserved, "
                f"{merge_time_ms:.2f}ms"
            )

            return ContextMergeResult(
                merged_contexts=merged_contexts,
                total_contexts_processed=len(contexts),
                contexts_merged=contexts_merged,
                contexts_preserved=contexts_preserved,
                merge_time_ms=merge_time_ms,
                relevance_threshold=relevance_threshold,
                similarity_threshold=similarity_threshold,
            )

        except Exception as e:
            logger.error(f"Context merging failed for session {session_id}: {e}")
            raise

    def merge_conversation_context(self, session_id: str, max_context_length: Optional[int] = None) -> Optional[str]:
        """
        Merge conversation context into a single string for AI consumption.

        Args:
            session_id: Session identifier
            max_context_length: Maximum length of merged context

        Returns:
            Merged conversation context string
        """
        try:
            # Get conversation messages
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT role, content, timestamp
                        FROM conversation_messages
                        WHERE session_id = %s
                        ORDER BY message_index
                        LIMIT 50
                    """,
                        (session_id,),
                    )

                    messages = []
                    for row in cursor.fetchall():
                        messages.append({"role": row["role"], "content": row["content"], "timestamp": row["timestamp"]})

            if not messages:
                return None

            # Build conversation context
            conversation_parts = []
            for msg in messages:
                role_prefix = "User" if msg["role"] == "human" else "Assistant"
                conversation_parts.append(f"{role_prefix}: {msg['content']}")

            merged_context = "\n\n".join(conversation_parts)

            # Truncate if needed
            if max_context_length and len(merged_context) > max_context_length:
                merged_context = merged_context[:max_context_length] + "..."

            return merged_context

        except Exception as e:
            logger.error(f"Conversation context merging failed for session {session_id}: {e}")
            return None

    def get_context_summary(self, session_id: str, context_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get a summary of contexts for a session.

        Args:
            session_id: Session identifier
            context_types: List of context types to include

        Returns:
            Context summary dictionary
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    if context_types:
                        placeholders = ",".join(["%s"] * len(context_types))
                        cursor.execute(
                            f"""
                            SELECT context_type, COUNT(*) as count,
                                   AVG(relevance_score) as avg_relevance
                            FROM conversation_context
                            WHERE session_id = %s AND context_type IN ({placeholders})
                            AND (expires_at IS NULL OR expires_at > NOW())
                            GROUP BY context_type
                        """,
                            (session_id, *context_types),
                        )
                    else:
                        cursor.execute(
                            """
                            SELECT context_type, COUNT(*) as count,
                                   AVG(relevance_score) as avg_relevance
                            FROM conversation_context
                            WHERE session_id = %s
                            AND (expires_at IS NULL OR expires_at > NOW())
                            GROUP BY context_type
                        """,
                            (session_id,),
                        )

                    summary = {
                        "session_id": session_id,
                        "total_contexts": 0,
                        "context_types": {},
                        "last_updated": datetime.now().isoformat(),
                    }

                    for row in cursor.fetchall():
                        context_type = row["context_type"]
                        count = row["count"]
                        avg_relevance = float(row["avg_relevance"]) if row["avg_relevance"] else 0.0

                        summary["context_types"][context_type] = {"count": count, "avg_relevance": avg_relevance}
                        summary["total_contexts"] += count

                    return summary

        except Exception as e:
            logger.error(f"Context summary failed for session {session_id}: {e}")
            return {
                "session_id": session_id,
                "error": str(e),
                "total_contexts": 0,
                "context_types": {},
                "last_updated": datetime.now().isoformat(),
            }

    def cleanup_expired_cache(self) -> int:
        """Clean up expired cache entries."""
        try:
            current_time = datetime.now()
            expired_keys = []

            for cache_key, timestamp in self.cache_timestamps.items():
                if current_time - timestamp > self.cache_ttl:
                    expired_keys.append(cache_key)

            for key in expired_keys:
                del self.context_cache[key]
                del self.cache_timestamps[key]

            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

            return len(expired_keys)

        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
            return 0

    def get_merge_statistics(self) -> Dict[str, Any]:
        """Get statistics about context merging operations."""
        try:
            return {
                "cache_size": len(self.context_cache),
                "cache_entries": list(self.context_cache.keys()),
                "cache_ttl_seconds": self.cache_ttl.total_seconds(),
                "default_relevance_threshold": self.default_relevance_threshold,
                "default_similarity_threshold": self.default_similarity_threshold,
                "max_contexts_per_merge": self.max_contexts_per_merge,
                "max_merge_content_length": self.max_merge_content_length,
            }
        except Exception as e:
            logger.error(f"Failed to get merge statistics: {e}")
            return {"error": str(e)}
