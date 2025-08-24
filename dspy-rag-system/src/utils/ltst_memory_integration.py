"""
LTST Memory Integration with Memory Rehydration System

This module integrates the LTST Memory System with the existing memory rehydration
system to provide conversation history and user preferences in memory bundles.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .context_merger import ContextMerger, ContextMergeRequest
from .conversation_storage import ConversationStorage
from .logger import setup_logger
from .memory_rehydrator import Bundle, rehydrate
from .session_manager import SessionManager

logger = setup_logger(__name__)


@dataclass
class LTSTMemoryBundle:
    """Extended memory bundle with LTST conversation context."""

    original_bundle: Bundle
    conversation_history: List[Dict[str, Any]]
    user_preferences: Dict[str, Any]
    session_context: Optional[Dict[str, Any]] = None
    context_relevance_scores: Optional[Dict[str, float]] = None
    conversation_continuity_score: float = 0.0
    user_preference_confidence: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.context_relevance_scores is None:
            self.context_relevance_scores = {}
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "original_bundle": asdict(self.original_bundle),
            "conversation_history": self.conversation_history,
            "user_preferences": self.user_preferences,
            "session_context": self.session_context,
            "context_relevance_scores": self.context_relevance_scores,
            "conversation_continuity_score": self.conversation_continuity_score,
            "user_preference_confidence": self.user_preference_confidence,
            "metadata": self.metadata,
        }


class LTSTMemoryIntegration:
    """Integrates LTST Memory System with existing memory rehydration."""

    def __init__(
        self,
        conversation_storage: Optional[ConversationStorage] = None,
        context_merger: Optional[ContextMerger] = None,
        session_manager: Optional[SessionManager] = None,
    ):
        """Initialize LTST memory integration."""
        self.conversation_storage = conversation_storage or ConversationStorage()
        self.context_merger = context_merger or ContextMerger(self.conversation_storage)
        self.session_manager = session_manager or SessionManager(self.conversation_storage, self.context_merger)
        # Database manager is handled by individual components
        self.db_manager = self.conversation_storage.db_manager

    def rehydrate_with_conversation_context(
        self,
        query: str,
        user_id: str,
        session_id: Optional[str] = None,
        include_conversation_history: bool = True,
        include_user_preferences: bool = True,
        include_session_context: bool = True,
        conversation_history_limit: int = 10,
        max_context_tokens: int = 2000,
        **rehydrate_kwargs,
    ) -> LTSTMemoryBundle:
        """Rehydrate memory with conversation context."""
        try:
            # Get or create session
            if not session_id:
                session_id = self._get_or_create_session(user_id, query)
                if not session_id:
                    logger.warning("Failed to create session, proceeding without session context")

            # Get original memory bundle
            original_bundle = rehydrate(query, **rehydrate_kwargs)

            # Initialize LTST components
            conversation_history = []
            user_preferences = {}
            session_context = None
            context_relevance_scores = {}
            conversation_continuity_score = 0.0
            user_preference_confidence = 0.0

            # Add conversation history if requested
            if include_conversation_history and session_id:
                conversation_history = self._get_conversation_history(session_id, limit=conversation_history_limit)
                conversation_continuity_score = self._calculate_conversation_continuity(conversation_history, query)

            # Add user preferences if requested
            if include_user_preferences:
                user_preferences = self._get_user_preferences(user_id)
                user_preference_confidence = self._calculate_preference_confidence(user_preferences)

            # Add session context if requested
            if include_session_context and session_id:
                session_context = self._get_session_context(session_id, query)
                context_relevance_scores = self._calculate_context_relevance(session_context, query)

            # Create LTST memory bundle
            ltst_bundle = LTSTMemoryBundle(
                original_bundle=original_bundle,
                conversation_history=conversation_history,
                user_preferences=user_preferences,
                session_context=session_context,
                context_relevance_scores=context_relevance_scores,
                conversation_continuity_score=conversation_continuity_score,
                user_preference_confidence=user_preference_confidence,
                metadata={
                    "session_id": session_id,
                    "user_id": user_id,
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "included_components": {
                        "conversation_history": include_conversation_history,
                        "user_preferences": include_user_preferences,
                        "session_context": include_session_context,
                    },
                },
            )

            # Store the query as a message if session exists
            if session_id:
                self.session_manager.add_message(session_id, "human", query, metadata={"source": "memory_rehydration"})

            logger.info(f"LTST memory bundle created for session {session_id}")
            return ltst_bundle

        except Exception as e:
            logger.error(f"Failed to create LTST memory bundle: {e}")
            # Fallback to original bundle
            return LTSTMemoryBundle(
                original_bundle=rehydrate(query, **rehydrate_kwargs),
                conversation_history=[],
                user_preferences={},
                metadata={"error": str(e)},
            )

    def _get_or_create_session(self, user_id: str, query: str) -> Optional[str]:
        """Get existing session or create new one."""
        try:
            # Try to find recent active session
            sessions = self.session_manager.get_user_sessions(user_id, status="active", limit=1)
            if sessions:
                return sessions[0]["session_id"]

            # Create new session
            session_name = f"Memory Rehydration Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            session_id = self.session_manager.create_session(
                user_id, session_name, metadata={"source": "memory_rehydration"}
            )

            return session_id

        except Exception as e:
            logger.error(f"Failed to get or create session: {e}")
            return None

    def _get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for the session."""
        try:
            messages = self.conversation_storage.get_messages(session_id, limit=limit)

            history = []
            for msg in messages:
                history.append(
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                        "message_type": msg.message_type,
                        "relevance_score": msg.relevance_score,
                        "metadata": msg.metadata,
                    }
                )

            return history

        except Exception as e:
            logger.error(f"Failed to get conversation history for session {session_id}: {e}")
            return []

    def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences for context."""
        try:
            if not self.db_manager:
                logger.warning("Database manager not available")
                return {}

            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT preference_key, preference_value, preference_type, confidence_score
                        FROM user_preferences
                        WHERE user_id = %s AND confidence_score >= 0.7
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

    def _get_session_context(self, session_id: str, query: str) -> Optional[Dict[str, Any]]:
        """Get session context using context merger."""
        try:
            # Create merge request
            session = self.session_manager.get_session(session_id)
            if not session or not hasattr(session, "user_id"):
                logger.warning(f"Session {session_id} not found or missing user_id")
                return None

            request = ContextMergeRequest(
                session_id=session_id,
                user_id=session.user_id,
                current_message=query,
                context_types=["conversation", "preference", "project", "user_info"],
                max_context_length=2000,
                relevance_threshold=0.6,
                include_history=True,
                history_limit=5,
            )

            # Merge context
            merged_context = self.context_merger.merge_context(request)
            if merged_context:
                return {
                    "merged_content": merged_context.merged_content,
                    "relevance_scores": merged_context.relevance_scores,
                    "context_hash": merged_context.context_hash,
                    "conversation_history_count": len(merged_context.conversation_history),
                    "user_preferences_count": sum(len(prefs) for prefs in merged_context.user_preferences.values()),
                    "project_context_count": len(merged_context.project_context),
                    "relevant_contexts_count": len(merged_context.relevant_contexts),
                }

            return None

        except Exception as e:
            logger.error(f"Failed to get session context for session {session_id}: {e}")
            return None

    def _calculate_conversation_continuity(self, conversation_history: List[Dict[str, Any]], query: str) -> float:
        """Calculate conversation continuity score."""
        try:
            if not conversation_history:
                return 0.0

            # Simple continuity calculation based on recent messages
            recent_messages = conversation_history[-3:]  # Last 3 messages

            # Check if query relates to recent conversation
            query_lower = query.lower()
            continuity_score = 0.0

            for msg in recent_messages:
                content_lower = msg["content"].lower()

                # Check for keyword overlap
                query_words = set(query_lower.split())
                content_words = set(content_lower.split())
                overlap = len(query_words.intersection(content_words))

                if overlap > 0:
                    continuity_score += min(overlap / len(query_words), 1.0)

            # Normalize by number of recent messages
            return min(continuity_score / len(recent_messages), 1.0)

        except Exception as e:
            logger.error(f"Failed to calculate conversation continuity: {e}")
            return 0.0

    def _calculate_preference_confidence(self, user_preferences: Dict[str, Any]) -> float:
        """Calculate overall user preference confidence."""
        try:
            if not user_preferences:
                return 0.0

            total_confidence = 0.0
            total_preferences = 0

            for pref_type, prefs in user_preferences.items():
                for key, data in prefs.items():
                    total_confidence += data["confidence"]
                    total_preferences += 1

            return total_confidence / total_preferences if total_preferences > 0 else 0.0

        except Exception as e:
            logger.error(f"Failed to calculate preference confidence: {e}")
            return 0.0

    def _calculate_context_relevance(self, session_context: Optional[Dict[str, Any]], query: str) -> Dict[str, float]:
        """Calculate context relevance scores."""
        try:
            if not session_context:
                return {}

            relevance_scores = session_context.get("relevance_scores", {})

            # Add query-specific relevance
            query_lower = query.lower()
            context_content = session_context.get("merged_content", "").lower()

            # Simple keyword-based relevance
            query_words = set(query_lower.split())
            context_words = set(context_content.split())
            overlap = len(query_words.intersection(context_words))

            if len(query_words) > 0:
                keyword_relevance = min(overlap / len(query_words), 1.0)
                relevance_scores["keyword_overlap"] = keyword_relevance

            return relevance_scores

        except Exception as e:
            logger.error(f"Failed to calculate context relevance: {e}")
            return {}

    def store_conversation_response(
        self, session_id: str, response: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store AI response in conversation history."""
        try:
            if not session_id:
                return False

            # Add response as AI message
            success = self.session_manager.add_message(
                session_id,
                "ai",
                response,
                message_type="message",
                metadata=metadata or {"source": "memory_rehydration"},
            )

            if success:
                logger.info(f"AI response stored for session {session_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to store conversation response: {e}")
            return False

    def get_conversation_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation summary for a session."""
        try:
            if not session_id:
                return None

            # Get session statistics
            stats = self.session_manager.get_session_statistics(session_id)

            # Get recent conversation history
            history = self._get_conversation_history(session_id, limit=20)

            # Get user preferences
            session = self.session_manager.get_session(session_id)
            user_preferences = {}
            if session and hasattr(session, "user_id"):
                user_preferences = self._get_user_preferences(session.user_id)

            summary = {
                "session_id": session_id,
                "statistics": stats,
                "recent_history": history,
                "user_preferences": user_preferences,
                "summary_timestamp": datetime.now().isoformat(),
            }

            return summary

        except Exception as e:
            logger.error(f"Failed to get conversation summary for session {session_id}: {e}")
            return None

    def update_user_preferences_from_conversation(self, user_id: str, conversation_data: Dict[str, Any]) -> bool:
        """Update user preferences based on conversation analysis."""
        try:
            # Extract preferences from conversation
            preferences_to_update = {}

            # Analyze conversation patterns
            messages = conversation_data.get("messages", [])
            for msg in messages:
                if msg.get("role") == "human":
                    content = msg.get("content", "").lower()

                    # Learn communication style
                    if len(content) < 50:
                        preferences_to_update["communication_style"] = "concise"
                    elif len(content) > 200:
                        preferences_to_update["communication_style"] = "detailed"

                    # Learn technical focus
                    if any(tech_word in content for tech_word in ["python", "code", "function", "class"]):
                        preferences_to_update["technical_focus"] = "programming"

                    # Learn project preferences
                    if any(project_word in content for project_word in ["project", "task", "feature"]):
                        preferences_to_update["project_focus"] = "implementation"

            # Update preferences
            for key, value in preferences_to_update.items():
                self.context_merger.update_user_preference(user_id, key, value, "general", 0.8)

            logger.info(f"Updated {len(preferences_to_update)} preferences for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update user preferences: {e}")
            return False

    def cleanup_old_conversations(self, days_old: int = 30) -> int:
        """Clean up old conversation data."""
        try:
            if not self.db_manager:
                logger.warning("Database manager not available for cleanup")
                return 0

            cleaned_count = 0
            cutoff_date = datetime.now() - timedelta(days=days_old)

            # Get old sessions
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT session_id FROM conversation_sessions
                        WHERE last_activity < %s AND status = 'archived'
                    """,
                        (cutoff_date,),
                    )

                    old_sessions = [row[0] for row in cursor.fetchall()]

                    # Delete old sessions
                    for session_id in old_sessions:
                        if self.conversation_storage.delete_session(session_id):
                            cleaned_count += 1

            logger.info(f"Cleaned up {cleaned_count} old conversations")
            return cleaned_count

        except Exception as e:
            logger.error(f"Failed to cleanup old conversations: {e}")
            return 0

    def get_integration_health(self) -> Dict[str, Any]:
        """Get health metrics for the LTST memory integration."""
        try:
            health_metrics = {
                "timestamp": datetime.now().isoformat(),
                "active_sessions": self.session_manager.get_active_sessions_count(),
                "session_health": self.session_manager.get_session_health(),
                "storage_health": {
                    "conversation_storage_available": True,
                    "context_merger_available": True,
                    "session_manager_available": True,
                },
                "database_health": {"connection_available": True},
            }

            # Test database connection
            try:
                if not self.db_manager:
                    health_metrics["database_health"]["connection_available"] = False
                    health_metrics["database_health"]["error"] = "Database manager not available"
                else:
                    with self.db_manager.get_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute("SELECT 1")
                    health_metrics["database_health"]["connection_available"] = True
            except Exception as e:
                health_metrics["database_health"]["connection_available"] = False
                health_metrics["database_health"]["error"] = str(e)

            return health_metrics

        except Exception as e:
            logger.error(f"Failed to get integration health: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
