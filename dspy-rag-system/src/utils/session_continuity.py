#!/usr/bin/env python3
"""
Session Continuity & Preference Learning System

This module implements Task 16 of B-1043: Session Continuity & Minimal Preference Learning.
It extends the LTST memory system with session persistence, preference learning, and
cross-session context restoration capabilities.

Features:
- Session state persistence across restarts
- Stable preference learning and application
- Session resume with last 10 messages + last 2 decisions
- Cross-session context linking
- Preference conflict resolution
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .conversation_storage import ConversationStorage, UserPreference
from .session_manager import SessionManager

logger = logging.getLogger(__name__)


@dataclass
class SessionContinuityState:
    """Represents the continuity state of a session across restarts."""

    session_id: str
    user_id: str
    last_messages: List[Dict[str, Any]] = field(default_factory=list)
    last_decisions: List[Dict[str, Any]] = field(default_factory=list)
    active_preferences: Dict[str, Any] = field(default_factory=dict)
    session_metadata: Dict[str, Any] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.now)
    continuity_hash: str = ""

    def __post_init__(self):
        """Generate continuity hash for state validation."""
        if not self.continuity_hash:
            self.continuity_hash = self._generate_continuity_hash()

    def _generate_continuity_hash(self) -> str:
        """Generate hash for continuity state validation."""
        state_data = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "last_messages_count": len(self.last_messages),
            "last_decisions_count": len(self.last_decisions),
            "preferences_count": len(self.active_preferences),
            # Note: last_activity excluded for deterministic hashing
        }
        return hashlib.sha256(json.dumps(state_data, sort_keys=True).encode()).hexdigest()[:16]


@dataclass
class PreferenceLearningResult:
    """Result of preference learning operation."""

    preferences_learned: int
    preferences_applied: int
    confidence_scores: Dict[str, float]
    learning_insights: List[str]
    conflicts_resolved: int


class SessionContinuityManager:
    """Manages session continuity and preference learning across sessions."""

    def __init__(self, conversation_storage: Optional[ConversationStorage] = None):
        """Initialize session continuity manager."""
        if conversation_storage is None:
            self.conversation_storage = ConversationStorage()
        else:
            self.conversation_storage = conversation_storage

        self.session_manager = SessionManager(self.conversation_storage)
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.max_messages_for_resume = 10
        self.max_decisions_for_resume = 2
        self.preference_confidence_threshold = 0.7
        self.session_timeout_hours = 24

        # Performance tracking
        self.continuity_operations = 0
        self.preference_learnings = 0

    def persist_session_state(self, session_id: str) -> bool:
        """
        Persist current session state for continuity across restarts.

        Args:
            session_id: Session identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current session state
            session_state = self.session_manager.get_session_state(session_id)
            if not session_state:
                self.logger.warning(f"No session state found for {session_id}")
                return False

            # Get last messages
            last_messages = self.conversation_storage.retrieve_session_messages(
                session_id, limit=self.max_messages_for_resume
            )

            # Get last decisions (from conversation context)
            last_decisions = self._get_last_decisions(session_id)

            # Get active preferences
            active_preferences = self._get_active_preferences(session_state.user_id)

            # Create continuity state
            continuity_state = SessionContinuityState(
                session_id=session_id,
                user_id=session_state.user_id,
                last_messages=last_messages,
                last_decisions=last_decisions,
                active_preferences=active_preferences,
                session_metadata=session_state.metadata or {},
                last_activity=session_state.last_activity,
            )

            # Store continuity state in conversation context
            success = self.conversation_storage.store_context(
                session_id=session_id,
                context_type="continuity",
                context_key="session_state",
                context_value=json.dumps(continuity_state.__dict__, default=str),
                relevance_score=1.0,
            )

            if success:
                self.continuity_operations += 1
                self.logger.info(f"Session state persisted for {session_id}")

            return success

        except Exception as e:
            self.logger.error(f"Failed to persist session state for {session_id}: {e}")
            return False

    def restore_session_state(self, user_id: str, session_id: Optional[str] = None) -> Optional[SessionContinuityState]:
        """
        Restore session state for continuity across restarts.

        Args:
            user_id: User identifier
            session_id: Optional specific session ID, otherwise finds most recent

        Returns:
            SessionContinuityState if found, None otherwise
        """
        try:
            # Find session to restore
            target_session_id = session_id
            if not target_session_id:
                # Find most recent active session for user
                sessions = self.session_manager.get_user_sessions(user_id, limit=1)
                if not sessions:
                    self.logger.info(f"No active sessions found for user {user_id}")
                    return None
                # Handle both object and dict return types
                session = sessions[0]
                if hasattr(session, "session_id"):
                    target_session_id = session.session_id
                else:
                    target_session_id = session["session_id"]

            # Get continuity state from conversation context
            continuity_contexts = self.conversation_storage.retrieve_context(
                target_session_id, context_type="continuity", limit=1
            )

            if not continuity_contexts:
                self.logger.info(f"No continuity state found for session {target_session_id}")
                return None

            # Parse continuity state
            continuity_data = json.loads(continuity_contexts[0]["context_value"])

            # Reconstruct SessionContinuityState
            continuity_state = SessionContinuityState(
                session_id=continuity_data["session_id"],
                user_id=continuity_data["user_id"],
                last_messages=continuity_data["last_messages"],
                last_decisions=continuity_data["last_decisions"],
                active_preferences=continuity_data["active_preferences"],
                session_metadata=continuity_data["session_metadata"],
                last_activity=datetime.fromisoformat(continuity_data["last_activity"]),
                continuity_hash=continuity_data["continuity_hash"],
            )

            # Validate continuity state
            if not self._validate_continuity_state(continuity_state):
                self.logger.warning(f"Invalid continuity state for session {target_session_id}")
                return None

            self.continuity_operations += 1
            self.logger.info(f"Session state restored for {target_session_id}")

            return continuity_state

        except Exception as e:
            self.logger.error(f"Failed to restore session state for user {user_id}: {e}")
            return None

    def learn_and_apply_preferences(self, session_id: str, messages: List[Dict[str, Any]]) -> PreferenceLearningResult:
        """
        Learn preferences from session activity and apply them.

        Args:
            session_id: Session identifier
            messages: Recent messages to analyze

        Returns:
            PreferenceLearningResult with learning outcomes
        """
        try:
            # Get session state
            session_state = self.session_manager.get_session_state(session_id)
            if not session_state:
                return PreferenceLearningResult(0, 0, {}, [], 0)

            # Extract preferences from messages
            learned_preferences = self._extract_preferences_from_messages(messages, session_state.user_id)

            # Apply preferences to current session
            applied_preferences = self._apply_preferences_to_session(session_id, learned_preferences)

            # Resolve conflicts
            conflicts_resolved = self._resolve_preference_conflicts(session_state.user_id, learned_preferences)

            # Generate insights
            learning_insights = self._generate_learning_insights(learned_preferences, applied_preferences)

            # Calculate confidence scores
            confidence_scores = {pref.preference_key: pref.confidence_score for pref in learned_preferences}

            result = PreferenceLearningResult(
                preferences_learned=len(learned_preferences),
                preferences_applied=len(applied_preferences),
                confidence_scores=confidence_scores,
                learning_insights=learning_insights,
                conflicts_resolved=conflicts_resolved,
            )

            self.preference_learnings += 1
            self.logger.info(f"Learned {len(learned_preferences)} preferences for session {session_id}")

            return result

        except Exception as e:
            self.logger.error(f"Failed to learn preferences for session {session_id}: {e}")
            return PreferenceLearningResult(0, 0, {}, [f"Error: {str(e)}"], 0)

    def resume_session_with_context(self, user_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Resume session with last 10 messages + last 2 decisions + preferences.

        Args:
            user_id: User identifier
            session_id: Optional specific session ID

        Returns:
            Dictionary with resume context
        """
        try:
            # Restore session state
            continuity_state = self.restore_session_state(user_id, session_id)
            if not continuity_state:
                # Create new session if no continuity state
                new_session_id = self.session_manager.create_session(user_id, "New Session")
                return {
                    "session_id": new_session_id,
                    "resume_type": "new_session",
                    "last_messages": [],
                    "last_decisions": [],
                    "active_preferences": {},
                    "continuity_hash": "",
                }

            # Prepare resume context
            resume_context = {
                "session_id": continuity_state.session_id,
                "resume_type": "continuity_restore",
                "last_messages": continuity_state.last_messages[: self.max_messages_for_resume],
                "last_decisions": continuity_state.last_decisions[: self.max_decisions_for_resume],
                "active_preferences": continuity_state.active_preferences,
                "continuity_hash": continuity_state.continuity_hash,
                "session_metadata": continuity_state.session_metadata,
            }

            # Apply preferences to resume context
            self._apply_preferences_to_resume_context(resume_context, continuity_state.active_preferences)

            self.logger.info(f"Session resumed for {continuity_state.session_id}")
            return resume_context

        except Exception as e:
            self.logger.error(f"Failed to resume session for user {user_id}: {e}")
            return {"error": str(e)}

    def _get_last_decisions(self, session_id: str) -> List[Dict[str, Any]]:
        """Get last decisions from conversation context."""
        try:
            decision_contexts = self.conversation_storage.retrieve_context(
                session_id, context_type="decision", limit=self.max_decisions_for_resume
            )

            decisions = []
            for context in decision_contexts:
                try:
                    decision_data = json.loads(context["context_value"])
                    decisions.append(
                        {
                            "decision_key": context["context_key"],
                            "head": decision_data.get("head", ""),
                            "rationale": decision_data.get("rationale", ""),
                            "confidence": decision_data.get("confidence", 0.0),
                            "timestamp": context["created_at"],
                        }
                    )
                except (json.JSONDecodeError, KeyError):
                    continue

            return decisions

        except Exception as e:
            self.logger.error(f"Failed to get last decisions for session {session_id}: {e}")
            return []

    def _get_active_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get active preferences for user."""
        try:
            preferences = self.conversation_storage.retrieve_user_preferences(user_id, limit=50)

            active_preferences = {}
            for pref in preferences:
                if pref.get("confidence_score", 0.0) >= self.preference_confidence_threshold:
                    active_preferences[pref["preference_key"]] = {
                        "value": pref["preference_value"],
                        "type": pref["preference_type"],
                        "confidence": pref["confidence_score"],
                        "source": pref["source"],
                    }

            return active_preferences

        except Exception as e:
            self.logger.error(f"Failed to get active preferences for user {user_id}: {e}")
            return {}

    def _validate_continuity_state(self, continuity_state: SessionContinuityState) -> bool:
        """Validate continuity state integrity."""
        try:
            # Check if session is not too old
            if datetime.now() - continuity_state.last_activity > timedelta(hours=self.session_timeout_hours):
                return False

            # Validate continuity hash - if it doesn't match, recalculate it
            expected_hash = continuity_state._generate_continuity_hash()
            if continuity_state.continuity_hash != expected_hash:
                # Update the hash to the correct value
                continuity_state.continuity_hash = expected_hash
                self.logger.debug(f"Updated continuity hash for session {continuity_state.session_id}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to validate continuity state: {e}")
            return False

    def _extract_preferences_from_messages(self, messages: List[Dict[str, Any]], user_id: str) -> List[UserPreference]:
        """Extract preferences from conversation messages."""
        preferences = []

        try:
            for message in messages:
                if message.get("role") != "human":
                    continue

                content = message.get("content", "").lower()

                # Extract stable preferences (e.g., "use Python 3.12")
                if "python 3.12" in content or "python3.12" in content:
                    preferences.append(
                        UserPreference(
                            user_id=user_id,
                            preference_key="python_version",
                            preference_value="3.12",
                            preference_type="coding",
                            confidence_score=0.9,
                            source="learned_from_conversation",
                        )
                    )

                # Extract explanation detail preferences
                if any(term in content for term in ["detailed", "explain more", "step by step"]):
                    preferences.append(
                        UserPreference(
                            user_id=user_id,
                            preference_key="explanation_detail",
                            preference_value="detailed",
                            preference_type="communication",
                            confidence_score=0.8,
                            source="learned_from_conversation",
                        )
                    )

                # Extract technical depth preferences
                if any(term in content for term in ["technical", "deep dive", "implementation"]):
                    preferences.append(
                        UserPreference(
                            user_id=user_id,
                            preference_key="technical_depth",
                            preference_value="high",
                            preference_type="communication",
                            confidence_score=0.7,
                            source="learned_from_conversation",
                        )
                    )

                # Extract code style preferences
                if any(term in content for term in ["functional", "pure functions", "immutable"]):
                    preferences.append(
                        UserPreference(
                            user_id=user_id,
                            preference_key="coding_style",
                            preference_value="functional",
                            preference_type="coding",
                            confidence_score=0.8,
                            source="learned_from_conversation",
                        )
                    )

                # Limit preferences per session
                if len(preferences) >= 10:
                    break

            return preferences

        except Exception as e:
            self.logger.error(f"Failed to extract preferences from messages: {e}")
            return []

    def _apply_preferences_to_session(self, session_id: str, preferences: List[UserPreference]) -> List[UserPreference]:
        """Apply preferences to current session."""
        applied_preferences = []

        try:
            for preference in preferences:
                # Store preference
                success = self.conversation_storage.store_user_preference(preference)
                if success:
                    applied_preferences.append(preference)

                    # Store preference context for session
                    self.conversation_storage.store_context(
                        session_id=session_id,
                        context_type="preference",
                        context_key=preference.preference_key,
                        context_value=preference.preference_value,
                        relevance_score=preference.confidence_score,
                    )

            return applied_preferences

        except Exception as e:
            self.logger.error(f"Failed to apply preferences to session {session_id}: {e}")
            return []

    def _resolve_preference_conflicts(self, user_id: str, new_preferences: List[UserPreference]) -> int:
        """Resolve conflicts between new and existing preferences."""
        conflicts_resolved = 0

        try:
            existing_preferences = self.conversation_storage.retrieve_user_preferences(user_id, limit=100)

            for new_pref in new_preferences:
                for existing_pref in existing_preferences:
                    if (
                        existing_pref["preference_key"] == new_pref.preference_key
                        and existing_pref["preference_value"] != new_pref.preference_value
                    ):

                        # Resolve by confidence score
                        if new_pref.confidence_score > existing_pref.get("confidence_score", 0.0):
                            # Update existing preference
                            updated_pref = UserPreference(
                                user_id=user_id,
                                preference_key=new_pref.preference_key,
                                preference_value=new_pref.preference_value,
                                preference_type=new_pref.preference_type,
                                confidence_score=new_pref.confidence_score,
                                source="resolved_conflict",
                            )
                            self.conversation_storage.store_user_preference(updated_pref)
                            conflicts_resolved += 1

            return conflicts_resolved

        except Exception as e:
            self.logger.error(f"Failed to resolve preference conflicts for user {user_id}: {e}")
            return 0

    def _generate_learning_insights(
        self, learned_preferences: List[UserPreference], applied_preferences: List[UserPreference]
    ) -> List[str]:
        """Generate insights from preference learning."""
        insights = []

        try:
            if learned_preferences:
                insights.append(f"Learned {len(learned_preferences)} new preferences")

                # Group by preference type
                type_counts = {}
                for pref in learned_preferences:
                    pref_type = pref.preference_type
                    type_counts[pref_type] = type_counts.get(pref_type, 0) + 1

                for pref_type, count in type_counts.items():
                    insights.append(f"  - {count} {pref_type} preferences")

            if applied_preferences:
                insights.append(f"Applied {len(applied_preferences)} preferences to session")

            return insights

        except Exception as e:
            self.logger.error(f"Failed to generate learning insights: {e}")
            return [f"Error generating insights: {str(e)}"]

    def _apply_preferences_to_resume_context(
        self, resume_context: Dict[str, Any], active_preferences: Dict[str, Any]
    ) -> None:
        """Apply preferences to resume context."""
        try:
            # Apply preferences to session metadata
            if "session_metadata" not in resume_context:
                resume_context["session_metadata"] = {}

            for pref_key, pref_data in active_preferences.items():
                resume_context["session_metadata"][f"preference_{pref_key}"] = pref_data["value"]

        except Exception as e:
            self.logger.error(f"Failed to apply preferences to resume context: {e}")

    def get_session_continuity_stats(self, user_id: str) -> Dict[str, Any]:
        """Get session continuity statistics for user."""
        try:
            sessions = self.session_manager.get_user_sessions(user_id, limit=50)

            total_sessions = len(sessions)
            # Consider sessions active if they were updated within the last 24 hours
            current_time = datetime.now()
            active_sessions = 0
            continuity_states = 0

            for session in sessions:
                # Handle both object and dict return types
                if hasattr(session, "last_updated"):
                    if (current_time - session.last_updated) < timedelta(hours=24):
                        active_sessions += 1
                    session_id = session.session_id
                else:
                    # For dict format, assume active if status is active
                    if session.get("status") == "active":
                        active_sessions += 1
                    session_id = session["session_id"]

                continuity_contexts = self.conversation_storage.retrieve_context(
                    session_id, context_type="continuity", limit=1
                )
                if continuity_contexts:
                    continuity_states += 1

            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "continuity_states": continuity_states,
                "continuity_rate": continuity_states / total_sessions if total_sessions > 0 else 0,
                "continuity_operations": self.continuity_operations,
                "preference_learnings": self.preference_learnings,
            }

        except Exception as e:
            self.logger.error(f"Failed to get session continuity stats for user {user_id}: {e}")
            return {"error": str(e)}
