#!/usr/bin/env python3

# type: ignore
"""
Session Management System for LTST Memory

This module provides the SessionManager class for managing conversation sessions,
user preference learning, and session continuity across AI interactions.

Note: Type ignore is used because RealDictCursor returns dictionary-like objects
that the type checker doesn't properly recognize, and database connection objects
are properly handled with null checks at runtime.
"""

import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .conversation_storage import ConversationSession, ConversationStorage, UserPreference


@dataclass
class SessionState:
    """Represents the current state of a session."""

    session_id: str
    user_id: str
    is_active: bool
    last_activity: datetime
    message_count: int
    context_count: int
    preference_count: int
    session_duration: timedelta
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SessionSummary:
    """Summary of session activity and learning."""

    session_id: str
    user_id: str
    total_messages: int
    total_contexts: int
    total_preferences: int
    session_duration: timedelta
    learning_insights: List[str]
    preference_updates: List[Dict[str, Any]]
    created_at: datetime
    last_updated: datetime


class SessionManager:
    """Manages conversation sessions and user preference learning."""

    def __init__(self, conversation_storage: Optional[ConversationStorage] = None):
        """Initialize session manager."""
        if conversation_storage is None:
            self.conversation_storage = ConversationStorage()
        else:
            self.conversation_storage = conversation_storage

        self.logger = logging.getLogger(__name__)

        # Session state cache
        self.active_sessions: Dict[str, SessionState] = {}
        self.session_cache_ttl = timedelta(hours=1)

        # Learning configuration
        self.preference_learning_enabled = True
        self.learning_confidence_threshold = 0.7
        self.max_preferences_per_session = 10

        # Performance metrics
        self.session_operations = 0
        self.preference_learnings = 0

    def create_session(
        self,
        user_id: str,
        session_name: Optional[str] = None,
        session_type: str = "conversation",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new conversation session."""
        try:
            # Generate unique session ID
            timestamp = datetime.now().isoformat()
            session_id = hashlib.sha256(f"{user_id}:{timestamp}".encode()).hexdigest()[:16]

            # Create session
            session = ConversationSession(
                session_id=session_id,
                user_id=user_id,
                session_name=session_name or f"Session {session_id[:8]}",
                session_type=session_type,
                status="active",
                metadata=metadata or {},
            )

            # Store session
            success = self.conversation_storage.create_session(session)
            if not success:
                raise Exception("Failed to create session in storage")

            # Initialize session state
            session_state = SessionState(
                session_id=session_id,
                user_id=user_id,
                is_active=True,
                last_activity=datetime.now(),
                message_count=0,
                context_count=0,
                preference_count=0,
                session_duration=timedelta(0),
                metadata=metadata or {},
            )

            # Cache session state
            self.active_sessions[session_id] = session_state
            self.session_operations += 1

            self.logger.info(f"Session created: {session_id} for user {user_id}")
            return session_id

        except Exception as e:
            self.logger.error(f"Failed to create session for user {user_id}: {e}")
            raise

    def get_session_state(self, session_id: str) -> Optional[SessionState]:
        """Get current session state."""
        try:
            # Check cache first
            if session_id in self.active_sessions:
                session_state = self.active_sessions[session_id]

                # Check if session is still active
                if session_state.is_active:
                    return session_state

            # Load from database
            session_summary = self.conversation_storage.get_session_summary(session_id)
            if not session_summary:
                return None

            # Create session state from summary
            last_activity_str = session_summary.get("last_activity")
            if isinstance(last_activity_str, str):
                last_activity = datetime.fromisoformat(last_activity_str)
            else:
                last_activity = datetime.now()

            session_state = SessionState(
                session_id=session_id,
                user_id=session_summary.get("user_id", "unknown"),
                is_active=session_summary.get("status", "inactive") == "active",
                last_activity=last_activity,
                message_count=session_summary.get("message_count", 0),
                context_count=session_summary.get("context_count", 0),
                preference_count=session_summary.get("preference_count", 0),
                session_duration=timedelta(seconds=session_summary.get("session_length", 0)),
                metadata=session_summary.get("metadata", {}),
            )

            # Cache if active
            if session_state.is_active:
                self.active_sessions[session_id] = session_state

            return session_state

        except Exception as e:
            self.logger.error(f"Failed to get session state for {session_id}: {e}")
            return None

    def update_session_activity(self, session_id: str, activity_type: str = "message") -> bool:
        """Update session activity and learning."""
        try:
            # Get current session state
            session_state = self.get_session_state(session_id)
            if not session_state:
                return False

            # Update activity
            session_state.last_activity = datetime.now()
            session_state.is_active = True

            # Update counters based on activity type
            if activity_type == "message":
                session_state.message_count += 1
            elif activity_type == "context":
                session_state.context_count += 1
            elif activity_type == "preference":
                session_state.preference_count += 1

            # Update session duration
            session_state.session_duration = datetime.now() - session_state.last_activity

            # Update cache
            self.active_sessions[session_id] = session_state

            # Learn from activity if enabled
            if self.preference_learning_enabled:
                self._learn_from_activity(session_id, activity_type)

            self.session_operations += 1
            return True

        except Exception as e:
            self.logger.error(f"Failed to update session activity for {session_id}: {e}")
            return False

    def _learn_from_activity(self, session_id: str, activity_type: str):
        """Learn user preferences from session activity."""
        try:
            if activity_type != "message":
                return

            # Get recent messages for learning
            messages = self.conversation_storage.retrieve_session_messages(session_id, limit=10)
            if not messages:
                return

            # Analyze messages for preference patterns
            preferences = self._extract_preferences_from_messages(messages)

            # Store learned preferences
            for preference in preferences:
                success = self.conversation_storage.store_user_preference(preference)
                if success:
                    self.preference_learnings += 1

            self.logger.debug(f"Learned {len(preferences)} preferences from session {session_id}")

        except Exception as e:
            self.logger.error(f"Failed to learn from activity for session {session_id}: {e}")

    def _extract_preferences_from_messages(self, messages: List[Dict[str, Any]]) -> List[UserPreference]:
        """Extract user preferences from conversation messages."""
        preferences = []

        try:
            # Simple preference extraction based on message patterns
            # In a production system, this would use more sophisticated NLP

            for message in messages:
                if message["role"] != "human":
                    continue

                content = message["content"].lower()

                # Extract coding style preferences
                if any(term in content for term in ["functional", "functional programming", "pure functions"]):
                    preferences.append(
                        UserPreference(
                            user_id=message.get("user_id", "unknown"),
                            preference_key="coding_style",
                            preference_value="functional",
                            preference_type="coding",
                            confidence_score=0.8,
                            source="learned_from_conversation",
                        )
                    )

                # Extract explanation detail preferences
                if any(term in content for term in ["detailed", "explain more", "step by step", "thorough"]):
                    preferences.append(
                        UserPreference(
                            user_id=message.get("user_id", "unknown"),
                            preference_key="explanation_detail",
                            preference_value="detailed",
                            preference_type="communication",
                            confidence_score=0.7,
                            source="learned_from_conversation",
                        )
                    )

                # Extract technical depth preferences
                if any(
                    term in content for term in ["technical", "deep dive", "implementation details", "architecture"]
                ):
                    preferences.append(
                        UserPreference(
                            user_id=message.get("user_id", "unknown"),
                            preference_key="technical_depth",
                            preference_value="high",
                            preference_type="communication",
                            confidence_score=0.6,
                            source="learned_from_conversation",
                        )
                    )

                # Limit preferences per session
                if len(preferences) >= self.max_preferences_per_session:
                    break

            return preferences

        except Exception as e:
            self.logger.error(f"Failed to extract preferences from messages: {e}")
            return []

    def get_user_sessions(self, user_id: str, limit: int = 20, active_only: bool = False) -> List[SessionSummary]:
        """Get sessions for a user."""
        try:
            # Get session summaries from storage
            # Note: This would need to be implemented in ConversationStorage
            # For now, we'll return basic session information

            sessions = []

            # Get recent sessions from active sessions cache
            for session_id, session_state in self.active_sessions.items():
                if session_state.user_id == user_id:
                    if active_only and not session_state.is_active:
                        continue

                    summary = SessionSummary(
                        session_id=session_id,
                        user_id=user_id,
                        total_messages=session_state.message_count,
                        total_contexts=session_state.context_count,
                        total_preferences=session_state.preference_count,
                        session_duration=session_state.session_duration,
                        learning_insights=[],
                        preference_updates=[],
                        created_at=session_state.last_activity - session_state.session_duration,
                        last_updated=session_state.last_activity,
                    )
                    sessions.append(summary)

            # Sort by last activity
            sessions.sort(key=lambda x: x.last_updated, reverse=True)

            return sessions[:limit]

        except Exception as e:
            self.logger.error(f"Failed to get sessions for user {user_id}: {e}")
            return []

    def close_session(self, session_id: str, reason: str = "user_requested") -> bool:
        """Close a session and perform cleanup."""
        try:
            # Get session state
            session_state = self.get_session_state(session_id)
            if not session_state:
                return False

            # Update session status
            session_state.is_active = False
            session_state.metadata["close_reason"] = reason
            session_state.metadata["closed_at"] = datetime.now().isoformat()

            # Update session in storage
            session = ConversationSession(
                session_id=session_id,
                user_id=session_state.user_id,
                session_name=session_state.metadata.get("session_name", f"Session {session_id[:8]}"),
                session_type=session_state.metadata.get("session_type", "conversation"),
                status="closed",
                metadata=session_state.metadata,
            )

            success = self.conversation_storage.create_session(session)
            if not success:
                self.logger.warning(f"Failed to update session status in storage for {session_id}")

            # Remove from active sessions cache
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

            self.logger.info(f"Session closed: {session_id} (reason: {reason})")
            return True

        except Exception as e:
            self.logger.error(f"Failed to close session {session_id}: {e}")
            return False

    def cleanup_expired_sessions(self, max_inactive_hours: int = 24) -> int:
        """Clean up expired sessions."""
        try:
            current_time = datetime.now()
            expired_sessions = []

            # Find expired sessions
            for session_id, session_state in self.active_sessions.items():
                if not session_state.is_active:
                    continue

                inactive_duration = current_time - session_state.last_activity
                if inactive_duration > timedelta(hours=max_inactive_hours):
                    expired_sessions.append(session_id)

            # Close expired sessions
            closed_count = 0
            for session_id in expired_sessions:
                if self.close_session(session_id, "expired"):
                    closed_count += 1

            if closed_count > 0:
                self.logger.info(f"Cleaned up {closed_count} expired sessions")

            return closed_count

        except Exception as e:
            self.logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0

    def get_session_insights(self, session_id: str) -> Dict[str, Any]:
        """Get insights and learning from a session."""
        try:
            session_state = self.get_session_state(session_id)
            if not session_state:
                return {"error": "Session not found"}

            # Get user preferences learned during this session
            user_preferences = self.conversation_storage.retrieve_user_preferences(session_state.user_id, limit=20)

            # Get recent messages for analysis
            messages = self.conversation_storage.retrieve_session_messages(session_id, limit=50)

            insights = {
                "session_id": session_id,
                "user_id": session_state.user_id,
                "session_duration": str(session_state.session_duration),
                "message_count": session_state.message_count,
                "context_count": session_state.context_count,
                "preference_count": session_state.preference_count,
                "learned_preferences": len(user_preferences),
                "conversation_topics": self._extract_conversation_topics(messages),
                "user_engagement": self._calculate_engagement_score(session_state),
                "learning_opportunities": self._identify_learning_opportunities(messages),
                "last_updated": session_state.last_activity.isoformat(),
            }

            return insights

        except Exception as e:
            self.logger.error(f"Failed to get session insights for {session_id}: {e}")
            return {"error": str(e)}

    def _extract_conversation_topics(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract main topics from conversation messages."""
        topics = []

        try:
            # Simple topic extraction based on keyword frequency
            # In production, this would use more sophisticated NLP

            keyword_patterns = {
                "database": ["database", "sql", "postgres", "schema", "migration"],
                "ai_ml": ["ai", "machine learning", "model", "training", "inference"],
                "programming": ["code", "programming", "development", "implementation"],
                "architecture": ["architecture", "design", "system", "components"],
                "performance": ["performance", "optimization", "speed", "efficiency"],
            }

            all_content = " ".join([msg["content"].lower() for msg in messages])

            for topic, keywords in keyword_patterns.items():
                if any(keyword in all_content for keyword in keywords):
                    topics.append(topic)

            return topics[:5]  # Limit to top 5 topics

        except Exception as e:
            self.logger.error(f"Failed to extract conversation topics: {e}")
            return []

    def _calculate_engagement_score(self, session_state: SessionState) -> float:
        """Calculate user engagement score for the session."""
        try:
            # Simple engagement scoring based on activity metrics
            base_score = 0.0

            # Message frequency
            if session_state.message_count > 0:
                base_score += min(0.4, session_state.message_count / 20.0)

            # Context creation
            if session_state.context_count > 0:
                base_score += min(0.3, session_state.context_count / 10.0)

            # Session duration
            duration_hours = session_state.session_duration.total_seconds() / 3600
            base_score += min(0.3, duration_hours / 2.0)

            return min(1.0, base_score)

        except Exception as e:
            self.logger.error(f"Failed to calculate engagement score: {e}")
            return 0.0

    def _identify_learning_opportunities(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Identify potential learning opportunities from conversation."""
        opportunities = []

        try:
            # Simple pattern matching for learning opportunities
            # In production, this would use more sophisticated analysis

            all_content = " ".join([msg["content"].lower() for msg in messages])

            if any(term in all_content for term in ["don't understand", "confused", "unclear"]):
                opportunities.append("clarification_needed")

            if any(term in all_content for term in ["how to", "tutorial", "guide", "example"]):
                opportunities.append("tutorial_requested")

            if any(term in all_content for term in ["error", "problem", "issue", "bug"]):
                opportunities.append("troubleshooting_needed")

            if any(term in all_content for term in ["optimize", "improve", "better", "enhance"]):
                opportunities.append("optimization_opportunity")

            return opportunities

        except Exception as e:
            self.logger.error(f"Failed to identify learning opportunities: {e}")
            return []

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the session manager."""
        try:
            return {
                "active_sessions": len(self.active_sessions),
                "session_operations": self.session_operations,
                "preference_learnings": self.preference_learnings,
                "learning_enabled": self.preference_learning_enabled,
                "cache_ttl_hours": self.session_cache_ttl.total_seconds() / 3600,
                "max_preferences_per_session": self.max_preferences_per_session,
                "learning_confidence_threshold": self.learning_confidence_threshold,
            }
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return {"error": str(e)}
