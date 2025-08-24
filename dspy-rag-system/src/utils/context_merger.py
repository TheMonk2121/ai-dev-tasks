"""
Context Merger for LTST Memory System

This module provides intelligent context merging capabilities for combining
conversation context, user preferences, and historical data for optimal AI responses.
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from psycopg2.extras import RealDictCursor

from .conversation_storage import ConversationContext, ConversationMessage, ConversationStorage
from .logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class MergedContext:
    """Represents merged context for AI processing."""

    session_id: str
    conversation_history: List[ConversationMessage]
    user_preferences: Dict[str, Any]
    project_context: Dict[str, Any]
    relevant_contexts: List[ConversationContext]
    merged_content: str
    relevance_scores: Dict[str, float]
    context_hash: str
    created_at: datetime
    metadata: Dict[str, Any]

    def __post_init__(self):
        """Initialize computed fields."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ContextMergeRequest:
    """Request for context merging."""

    session_id: str
    user_id: str
    current_message: str
    context_types: Optional[List[str]] = None  # ['conversation', 'preference', 'project', 'user_info']
    max_context_length: int = 10000
    relevance_threshold: float = 0.7
    include_history: bool = True
    history_limit: int = 20
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.context_types is None:
            self.context_types = ["conversation", "preference", "project", "user_info"]
        if self.metadata is None:
            self.metadata = {}


class ContextMerger:
    """Handles intelligent context merging for the LTST Memory System."""

    def __init__(self, conversation_storage: Optional[ConversationStorage] = None):
        """Initialize context merger."""
        self.conversation_storage = conversation_storage or ConversationStorage()
        self.cache = {}
        self.cache_ttl = timedelta(minutes=30)

    def merge_context(self, request: ContextMergeRequest) -> Optional[MergedContext]:
        """Merge context for a given request."""
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self.cache:
                cached_result = self.cache[cache_key]
                if datetime.now() - cached_result.created_at < self.cache_ttl:
                    logger.info(f"Using cached context for session {request.session_id}")
                    return cached_result

            # Gather conversation history
            conversation_history = []
            if request.include_history:
                conversation_history = self.conversation_storage.get_messages(
                    request.session_id, limit=request.history_limit
                )

            # Gather user preferences
            user_preferences = self._get_user_preferences(request.user_id)

            # Gather project context
            project_context = self._get_project_context(request.session_id)

            # Gather relevant contexts
            relevant_contexts = self._get_relevant_contexts(request)

            # Merge content
            merged_content = self._merge_content(
                conversation_history, user_preferences, project_context, relevant_contexts, request.current_message
            )

            # Calculate relevance scores
            relevance_scores = self._calculate_relevance_scores(
                conversation_history, user_preferences, project_context, relevant_contexts, request.current_message
            )

            # Create merged context
            merged_context = MergedContext(
                session_id=request.session_id,
                conversation_history=conversation_history,
                user_preferences=user_preferences,
                project_context=project_context,
                relevant_contexts=relevant_contexts,
                merged_content=merged_content,
                relevance_scores=relevance_scores,
                context_hash=self._generate_context_hash(request, merged_content),
                created_at=datetime.now(),
                metadata=request.metadata or {},
            )

            # Cache result
            self.cache[cache_key] = merged_context

            logger.info(f"Context merged for session {request.session_id}")
            return merged_context

        except Exception as e:
            logger.error(f"Failed to merge context for session {request.session_id}: {e}")
            return None

    def _generate_cache_key(self, request: ContextMergeRequest) -> str:
        """Generate cache key for the request."""
        cache_data = {
            "session_id": request.session_id,
            "user_id": request.user_id,
            "current_message_hash": hashlib.sha256(request.current_message.encode()).hexdigest(),
            "context_types": sorted(request.context_types or []),
            "max_context_length": request.max_context_length,
            "relevance_threshold": request.relevance_threshold,
            "include_history": request.include_history,
            "history_limit": request.history_limit,
        }
        return hashlib.sha256(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()

    def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences for context merging."""
        try:
            with self.conversation_storage.db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT preference_key, preference_value, preference_type, confidence_score
                        FROM user_preferences
                        WHERE user_id = %s
                        ORDER BY confidence_score DESC, last_used DESC
                    """,
                        (user_id,),
                    )

                    preferences = {}
                    for row in cursor.fetchall():
                        pref_type = row["preference_type"]
                        if pref_type not in preferences:
                            preferences[pref_type] = {}

                        preferences[pref_type][row["preference_key"]] = {
                            "value": row["preference_value"],
                            "confidence": row["confidence_score"],
                        }

                    return preferences

        except Exception as e:
            logger.error(f"Failed to get user preferences for {user_id}: {e}")
            return {}

    def _get_project_context(self, session_id: str) -> Dict[str, Any]:
        """Get project context for the session."""
        try:
            contexts = self.conversation_storage.get_context(session_id, "project")

            project_context = {}
            for context in contexts:
                project_context[context.context_key] = {
                    "value": context.context_value,
                    "relevance": context.relevance_score,
                    "metadata": context.metadata,
                }

            return project_context

        except Exception as e:
            logger.error(f"Failed to get project context for session {session_id}: {e}")
            return {}

    def _get_relevant_contexts(self, request: ContextMergeRequest) -> List[ConversationContext]:
        """Get relevant contexts based on the request."""
        try:
            relevant_contexts = []

            for context_type in request.context_types or []:
                contexts = self.conversation_storage.get_context(request.session_id, context_type)

                # Filter by relevance threshold
                filtered_contexts = [ctx for ctx in contexts if ctx.relevance_score >= request.relevance_threshold]

                # Sort by relevance and add to results
                filtered_contexts.sort(key=lambda x: x.relevance_score, reverse=True)
                relevant_contexts.extend(filtered_contexts)

            return relevant_contexts

        except Exception as e:
            logger.error(f"Failed to get relevant contexts for session {request.session_id}: {e}")
            return []

    def _merge_content(
        self,
        conversation_history: List[ConversationMessage],
        user_preferences: Dict[str, Any],
        project_context: Dict[str, Any],
        relevant_contexts: List[ConversationContext],
        current_message: str,
    ) -> str:
        """Merge all context into a single content string."""
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
                for pref_type, prefs in user_preferences.items():
                    if prefs:
                        prefs_text += f"{pref_type.title()}:\n"
                        for key, data in prefs.items():
                            if data["confidence"] >= 0.7:  # Only high-confidence preferences
                                prefs_text += f"  {key}: {data['value']}\n"
                merged_parts.append(prefs_text)

            # Add project context
            if project_context:
                project_text = "Project Context:\n"
                for key, data in project_context.items():
                    if data["relevance"] >= 0.7:  # Only high-relevance context
                        project_text += f"  {key}: {data['value']}\n"
                merged_parts.append(project_text)

            # Add relevant contexts
            if relevant_contexts:
                context_text = "Relevant Context:\n"
                for ctx in relevant_contexts[:5]:  # Top 5 contexts
                    context_text += f"  {ctx.context_type}: {ctx.context_value}\n"
                merged_parts.append(context_text)

            # Add current message
            merged_parts.append(f"Current Message: {current_message}")

            # Join all parts
            merged_content = "\n\n".join(merged_parts)

            # Truncate if too long
            if len(merged_content) > 10000:
                merged_content = merged_content[:10000] + "\n\n[Content truncated due to length]"

            return merged_content

        except Exception as e:
            logger.error(f"Failed to merge content: {e}")
            return f"Current Message: {current_message}"

    def _calculate_relevance_scores(
        self,
        conversation_history: List[ConversationMessage],
        user_preferences: Dict[str, Any],
        project_context: Dict[str, Any],
        relevant_contexts: List[ConversationContext],
        current_message: str,
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
                total_confidence = 0
                count = 0
                for pref_type, prefs in user_preferences.items():
                    for key, data in prefs.items():
                        total_confidence += data["confidence"]
                        count += 1
                scores["user_preferences"] = total_confidence / count if count > 0 else 0.0
            else:
                scores["user_preferences"] = 0.0

            # Project context relevance
            if project_context:
                total_relevance = sum(data["relevance"] for data in project_context.values())
                scores["project_context"] = total_relevance / len(project_context)
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

    def _generate_context_hash(self, request: ContextMergeRequest, merged_content: str) -> str:
        """Generate hash for the merged context."""
        context_data = {
            "session_id": request.session_id,
            "user_id": request.user_id,
            "current_message": request.current_message,
            "context_types": request.context_types,
            "merged_content_hash": hashlib.sha256(merged_content.encode()).hexdigest(),
        }
        return hashlib.sha256(json.dumps(context_data, sort_keys=True).encode()).hexdigest()

    def update_user_preference(
        self,
        user_id: str,
        preference_key: str,
        preference_value: str,
        preference_type: str = "general",
        confidence_score: float = 0.8,
    ) -> bool:
        """Update user preference and invalidate cache."""
        try:
            with self.conversation_storage.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO user_preferences
                        (user_id, preference_key, preference_value, preference_type, confidence_score)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (user_id, preference_key) DO UPDATE SET
                            preference_value = EXCLUDED.preference_value,
                            confidence_score = EXCLUDED.confidence_score,
                            last_used = NOW(),
                            usage_count = user_preferences.usage_count + 1
                    """,
                        (user_id, preference_key, preference_value, preference_type, confidence_score),
                    )
                    conn.commit()

            # Invalidate cache for this user
            self._invalidate_user_cache(user_id)

            logger.info(f"User preference updated: {user_id}:{preference_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to update user preference: {e}")
            return False

    def _invalidate_user_cache(self, user_id: str) -> None:
        """Invalidate cache entries for a specific user."""
        keys_to_remove = []
        for key in self.cache.keys():
            # This is a simplified cache invalidation
            # In a production system, you'd want more sophisticated cache management
            if user_id in key:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.cache[key]

    def get_context_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get statistics about context usage."""
        try:
            stats = {
                "session_id": session_id,
                "conversation_messages": 0,
                "user_preferences": 0,
                "project_contexts": 0,
                "relevant_contexts": 0,
                "cache_hits": 0,
                "cache_misses": 0,
            }

            # Get message count
            messages = self.conversation_storage.get_messages(session_id)
            stats["conversation_messages"] = len(messages)

            # Get context counts
            contexts = self.conversation_storage.get_context(session_id)
            for context in contexts:
                if context.context_type == "project":
                    stats["project_contexts"] += 1
                else:
                    stats["relevant_contexts"] += 1

            # Get user preferences count (simplified)
            session = self.conversation_storage.get_session(session_id)
            if session:
                user_prefs = self._get_user_preferences(session.user_id)
                stats["user_preferences"] = sum(len(prefs) for prefs in user_prefs.values())

            return stats

        except Exception as e:
            logger.error(f"Failed to get context statistics for session {session_id}: {e}")
            return {"session_id": session_id, "error": str(e)}

    def cleanup_cache(self) -> None:
        """Clean up expired cache entries."""
        try:
            current_time = datetime.now()
            keys_to_remove = []

            for key, cached_result in self.cache.items():
                if current_time - cached_result.created_at > self.cache_ttl:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self.cache[key]

            logger.info(f"Cleaned up {len(keys_to_remove)} expired cache entries")

        except Exception as e:
            logger.error(f"Failed to cleanup cache: {e}")
