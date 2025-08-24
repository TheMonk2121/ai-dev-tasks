"""
Session Manager for LTST Memory System

This module provides session management capabilities for maintaining conversation
continuity and session persistence across AI interactions.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .context_merger import ContextMerger, ContextMergeRequest
from .conversation_storage import ConversationMessage, ConversationSession, ConversationStorage
from .logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class SessionState:
    """Represents the current state of a session."""

    session_id: str
    user_id: str
    status: str  # 'active', 'paused', 'archived', 'expired'
    current_context: Optional[Dict[str, Any]] = None
    last_activity: Optional[datetime] = None
    message_count: int = 0
    context_retention_rate: float = 0.95
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.last_activity is None:
            self.last_activity = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SessionPreferences:
    """User preferences for session management."""

    user_id: str
    max_session_length: int = 100
    session_timeout_minutes: int = 60
    context_retention_threshold: float = 0.7
    auto_archive_enabled: bool = True
    preference_learning_enabled: bool = True
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.metadata is None:
            self.metadata = {}


class SessionManager:
    """Handles session management for the LTST Memory System."""

    def __init__(
        self, conversation_storage: Optional[ConversationStorage] = None, context_merger: Optional[ContextMerger] = None
    ):
        """Initialize session manager."""
        self.conversation_storage = conversation_storage or ConversationStorage()
        self.context_merger = context_merger or ContextMerger(self.conversation_storage)
        self.active_sessions: Dict[str, SessionState] = {}
        self.session_preferences: Dict[str, SessionPreferences] = {}
        self.cleanup_interval = timedelta(minutes=30)
        self.last_cleanup = datetime.now()

    def create_session(
        self,
        user_id: str,
        session_name: Optional[str] = None,
        session_type: str = "conversation",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Create a new conversation session."""
        try:
            # Generate unique session ID
            session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

            # Create session
            session = ConversationSession(
                session_id=session_id,
                user_id=user_id,
                session_name=session_name or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                session_type=session_type,
                status="active",
                metadata=metadata or {},
            )

            # Store session
            if self.conversation_storage.create_session(session):
                # Initialize session state
                session_state = SessionState(
                    session_id=session_id, user_id=user_id, status="active", message_count=0, metadata=metadata or {}
                )

                self.active_sessions[session_id] = session_state
                logger.info(f"Session created: {session_id} for user {user_id}")
                return session_id
            else:
                logger.error(f"Failed to create session for user {user_id}")
                return None

        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return None

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get session state."""
        try:
            # Check active sessions first
            if session_id in self.active_sessions:
                return self.active_sessions[session_id]

            # Load from database
            session = self.conversation_storage.get_session(session_id)
            if session:
                # Get message count from database
                messages = self.conversation_storage.get_messages(session_id)
                message_count = len(messages)

                # Create session state
                session_state = SessionState(
                    session_id=session_id,
                    user_id=session.user_id,
                    status=session.status,
                    last_activity=session.last_activity,
                    message_count=message_count,
                    metadata=session.metadata,
                )

                # Add to active sessions if still active
                if session.status == "active":
                    self.active_sessions[session_id] = session_state

                return session_state

            return None

        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        message_type: str = "message",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Add a message to the session."""
        try:
            # Get or create session state
            session_state = self.get_session(session_id)
            if not session_state:
                logger.error(f"Session not found: {session_id}")
                return False

            # Create message
            message = ConversationMessage(
                session_id=session_id, role=role, content=content, message_type=message_type, metadata=metadata or {}
            )

            # Store message
            if self.conversation_storage.store_message(message):
                # Update session state
                session_state.message_count += 1
                session_state.last_activity = datetime.now()

                # Update session activity in database
                self.conversation_storage.update_session_activity(session_id)

                # Learn user preferences if enabled
                if self._should_learn_preferences(session_state.user_id):
                    self._learn_user_preferences(session_state.user_id, role, content)

                logger.info(f"Message added to session {session_id}: {role}")
                return True
            else:
                logger.error(f"Failed to add message to session {session_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to add message to session {session_id}: {e}")
            return False

    def get_context_for_message(
        self, session_id: str, user_id: str, current_message: str, context_types: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get merged context for a message."""
        try:
            # Create merge request
            request = ContextMergeRequest(
                session_id=session_id,
                user_id=user_id,
                current_message=current_message,
                context_types=context_types or ["conversation", "preference", "project", "user_info"],
            )

            # Merge context
            merged_context = self.context_merger.merge_context(request)
            if merged_context:
                # Update session state with current context
                session_state = self.get_session(session_id)
                if session_state:
                    session_state.current_context = {
                        "context_hash": merged_context.context_hash,
                        "relevance_scores": merged_context.relevance_scores,
                        "context_length": len(merged_context.merged_content),
                    }

                return {
                    "merged_content": merged_context.merged_content,
                    "relevance_scores": merged_context.relevance_scores,
                    "context_hash": merged_context.context_hash,
                    "conversation_history": [
                        {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
                        for msg in merged_context.conversation_history
                    ],
                    "user_preferences": merged_context.user_preferences,
                    "project_context": merged_context.project_context,
                }

            return None

        except Exception as e:
            logger.error(f"Failed to get context for session {session_id}: {e}")
            return None

    def pause_session(self, session_id: str) -> bool:
        """Pause a session."""
        try:
            session_state = self.get_session(session_id)
            if not session_state:
                return False

            # Update session state
            session_state.status = "paused"
            session_state.last_activity = datetime.now()

            # Update database
            with self.conversation_storage.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE conversation_sessions
                        SET status = 'paused', last_activity = NOW()
                        WHERE session_id = %s
                    """,
                        (session_id,),
                    )
                    conn.commit()

            logger.info(f"Session paused: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to pause session {session_id}: {e}")
            return False

    def resume_session(self, session_id: str) -> bool:
        """Resume a paused session."""
        try:
            session_state = self.get_session(session_id)
            if not session_state:
                return False

            # Update session state
            session_state.status = "active"
            session_state.last_activity = datetime.now()

            # Update database
            with self.conversation_storage.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE conversation_sessions
                        SET status = 'active', last_activity = NOW()
                        WHERE session_id = %s
                    """,
                        (session_id,),
                    )
                    conn.commit()

            # Add back to active sessions
            self.active_sessions[session_id] = session_state

            logger.info(f"Session resumed: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to resume session {session_id}: {e}")
            return False

    def archive_session(self, session_id: str) -> bool:
        """Archive a session."""
        try:
            session_state = self.get_session(session_id)
            if not session_state:
                return False

            # Update session state
            session_state.status = "archived"
            session_state.last_activity = datetime.now()

            # Update database
            with self.conversation_storage.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE conversation_sessions
                        SET status = 'archived', last_activity = NOW()
                        WHERE session_id = %s
                    """,
                        (session_id,),
                    )
                    conn.commit()

            # Remove from active sessions
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

            logger.info(f"Session archived: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to archive session {session_id}: {e}")
            return False

    def get_user_sessions(self, user_id: str, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get sessions for a user."""
        try:
            sessions = self.conversation_storage.get_user_sessions(user_id, limit)

            # Filter by status if specified
            if status:
                sessions = [s for s in sessions if s.status == status]

            # Convert to dictionary format
            session_data = []
            for session in sessions:
                # Get message count for this session
                messages = self.conversation_storage.get_messages(session.session_id)
                message_count = len(messages)

                session_data.append(
                    {
                        "session_id": session.session_id,
                        "session_name": session.session_name,
                        "session_type": session.session_type,
                        "status": session.status,
                        "created_at": session.created_at,
                        "last_activity": session.last_activity,
                        "message_count": message_count,
                        "relevance_score": session.relevance_score,
                        "metadata": session.metadata,
                    }
                )

            return session_data

        except Exception as e:
            logger.error(f"Failed to get sessions for user {user_id}: {e}")
            return []

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        try:
            cleaned_count = 0
            current_time = datetime.now()

            # Get user preferences for timeout settings
            for user_id in set(session.user_id for session in self.active_sessions.values()):
                preferences = self._get_user_preferences(user_id)
                timeout_minutes = preferences.get("session_timeout_minutes", 60)
                timeout_delta = timedelta(minutes=timeout_minutes)

                # Find expired sessions for this user
                expired_sessions = [
                    session_id
                    for session_id, session_state in self.active_sessions.items()
                    if (
                        session_state.user_id == user_id
                        and session_state.last_activity is not None
                        and current_time - session_state.last_activity > timeout_delta
                    )
                ]

                # Archive expired sessions
                for session_id in expired_sessions:
                    if self.archive_session(session_id):
                        cleaned_count += 1

            self.last_cleanup = current_time
            logger.info(f"Cleaned up {cleaned_count} expired sessions")
            return cleaned_count

        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0

    def get_session_statistics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive session statistics."""
        try:
            session_state = self.get_session(session_id)
            if not session_state:
                return None

            # Get session summary from database
            summary = self.conversation_storage.get_session_summary(session_id)

            # Get context statistics
            context_stats = self.context_merger.get_context_statistics(session_id)

            # Combine statistics
            stats = {
                "session_id": session_id,
                "user_id": session_state.user_id,
                "status": session_state.status,
                "message_count": session_state.message_count,
                "last_activity": session_state.last_activity,
                "context_retention_rate": session_state.context_retention_rate,
                "current_context": session_state.current_context,
                "summary": summary,
                "context_statistics": context_stats,
                "metadata": session_state.metadata,
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get session statistics for {session_id}: {e}")
            return None

    def _should_learn_preferences(self, user_id: str) -> bool:
        """Check if preference learning is enabled for user."""
        try:
            preferences = self._get_user_preferences(user_id)
            return preferences.get("preference_learning_enabled", True)
        except Exception:
            return True

    def _learn_user_preferences(self, user_id: str, role: str, content: str) -> None:
        """Learn user preferences from message content."""
        try:
            # Simple preference learning based on message patterns
            if role == "human":
                # Learn communication style preferences
                if len(content) < 50:
                    self.context_merger.update_user_preference(
                        user_id, "communication_style", "concise", "communication", 0.8
                    )
                elif len(content) > 200:
                    self.context_merger.update_user_preference(
                        user_id, "communication_style", "detailed", "communication", 0.8
                    )

                # Learn technical preferences
                if any(tech_word in content.lower() for tech_word in ["python", "code", "function", "class"]):
                    self.context_merger.update_user_preference(user_id, "technical_focus", "programming", "coding", 0.9)

                # Learn project preferences
                if any(
                    project_word in content.lower() for project_word in ["project", "task", "feature", "implementation"]
                ):
                    self.context_merger.update_user_preference(
                        user_id, "project_focus", "implementation", "project", 0.8
                    )

        except Exception as e:
            logger.error(f"Failed to learn user preferences: {e}")

    def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences for session management."""
        try:
            with self.conversation_storage.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT preference_key, preference_value
                        FROM user_preferences
                        WHERE user_id = %s AND preference_type = 'session'
                    """,
                        (user_id,),
                    )

                    preferences = {}
                    for row in cursor.fetchall():
                        preferences[row["preference_key"]] = row["preference_value"]

                    return preferences

        except Exception as e:
            logger.error(f"Failed to get user preferences for {user_id}: {e}")
            return {}

    def set_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Set user preferences for session management."""
        try:
            for key, value in preferences.items():
                self.context_merger.update_user_preference(user_id, key, str(value), "session", 1.0)

            logger.info(f"User preferences set for {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to set user preferences for {user_id}: {e}")
            return False

    def get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        return len(self.active_sessions)

    def get_session_health(self) -> Dict[str, Any]:
        """Get overall session health metrics."""
        try:
            total_sessions = len(self.active_sessions)
            current_time = datetime.now()

            # Calculate session ages
            session_ages = []
            for session_state in self.active_sessions.values():
                if session_state.last_activity is not None:
                    age_minutes = (current_time - session_state.last_activity).total_seconds() / 60
                    session_ages.append(age_minutes)

            avg_session_age = sum(session_ages) / len(session_ages) if session_ages else 0

            health_metrics = {
                "total_active_sessions": total_sessions,
                "average_session_age_minutes": avg_session_age,
                "last_cleanup": self.last_cleanup,
                "cleanup_interval_minutes": self.cleanup_interval.total_seconds() / 60,
                "session_states": {
                    "active": len([s for s in self.active_sessions.values() if s.status == "active"]),
                    "paused": len([s for s in self.active_sessions.values() if s.status == "paused"]),
                    "archived": 0,  # Archived sessions are not in active_sessions
                },
            }

            return health_metrics

        except Exception as e:
            logger.error(f"Failed to get session health: {e}")
            return {"error": str(e)}
