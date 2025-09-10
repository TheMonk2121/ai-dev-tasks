#!/usr/bin/env python3
"""
Test Session Continuity & Preference Learning System

This module tests the SessionContinuityManager implementation for Task 16 of B-1043.
It validates session persistence, preference learning, and cross-session context restoration.
"""

import json
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock

from src.utils.conversation_storage import ConversationStorage, UserPreference
from src.utils.session_continuity import (
    PreferenceLearningResult,
    SessionContinuityManager,
    SessionContinuityState,
)


class TestSessionContinuityState(unittest.TestCase):
    """Test SessionContinuityState functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_session_id = "test_session_001"
        self.test_user_id = "test_user_001"

    def test_continuity_state_creation(self):
        """Test SessionContinuityState creation and hash generation."""
        continuity_state = SessionContinuityState(
            session_id=self.test_session_id,
            user_id=self.test_user_id,
            last_messages=[{"role": "human", "content": "test message"}],
            last_decisions=[{"decision_key": "test_decision", "head": "test"}],
            active_preferences={"python_version": {"value": "3.12", "confidence": 0.9}},
        )

        self.assertEqual(continuity_state.session_id, self.test_session_id)
        self.assertEqual(continuity_state.user_id, self.test_user_id)
        self.assertEqual(len(continuity_state.last_messages), 1)
        self.assertEqual(len(continuity_state.last_decisions), 1)
        self.assertEqual(len(continuity_state.active_preferences), 1)
        self.assertIsNotNone(continuity_state.continuity_hash)

    def test_continuity_hash_validation(self):
        """Test continuity hash generation and validation."""
        state1 = SessionContinuityState(
            session_id=self.test_session_id,
            user_id=self.test_user_id,
        )

        state2 = SessionContinuityState(
            session_id=self.test_session_id,
            user_id=self.test_user_id,
        )

        # Same state should have same hash
        self.assertEqual(state1.continuity_hash, state2.continuity_hash)

        # Different state should have different hash
        state3 = SessionContinuityState(
            session_id=self.test_session_id,
            user_id=self.test_user_id,
            last_messages=[{"role": "human", "content": "different message"}],
        )

        self.assertNotEqual(state1.continuity_hash, state3.continuity_hash)


class TestSessionContinuityManager(unittest.TestCase):
    """Test SessionContinuityManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_session_id = "test_session_002"
        self.test_user_id = "test_user_002"

        # Mock conversation storage
        self.mock_storage = Mock(spec=ConversationStorage)
        self.continuity_manager = SessionContinuityManager(self.mock_storage)

    def test_persist_session_state(self):
        """Test session state persistence."""
        # Mock session state
        mock_session_state = Mock()
        mock_session_state.user_id = self.test_user_id
        mock_session_state.last_activity = datetime.now()
        mock_session_state.metadata = {"test": "metadata"}

        # Mock storage methods
        self.continuity_manager.session_manager.get_session_state = Mock(return_value=mock_session_state)
        self.mock_storage.retrieve_session_messages = Mock(return_value=[{"role": "human", "content": "test message"}])
        self.mock_storage.retrieve_context = Mock(
            return_value=[{"context_key": "test_decision", "context_value": '{"head": "test"}'}]
        )
        self.mock_storage.retrieve_user_preferences = Mock(
            return_value=[{"preference_key": "python_version", "preference_value": "3.12", "confidence_score": 0.9}]
        )
        self.mock_storage.store_context = Mock(return_value=True)

        # Test persistence
        result = self.continuity_manager.persist_session_state(self.test_session_id)

        self.assertTrue(result)
        self.mock_storage.store_context.assert_called_once()

    def test_restore_session_state(self):
        """Test session state restoration."""
        # Mock continuity state data
        continuity_data = {
            "session_id": self.test_session_id,
            "user_id": self.test_user_id,
            "last_messages": [{"role": "human", "content": "test message"}],
            "last_decisions": [{"decision_key": "test_decision", "head": "test"}],
            "active_preferences": {"python_version": {"value": "3.12", "confidence": 0.9}},
            "session_metadata": {"test": "metadata"},
            "last_activity": datetime.now().isoformat(),
            "continuity_hash": "test_hash",
        }

        # Mock storage methods
        self.continuity_manager.session_manager.get_user_sessions = Mock(
            return_value=[{"session_id": self.test_session_id, "status": "active"}]
        )
        self.mock_storage.retrieve_context = Mock(return_value=[{"context_value": json.dumps(continuity_data)}])

        # Test restoration
        result = self.continuity_manager.restore_session_state(self.test_user_id)

        self.assertIsNotNone(result)
        if result is not None:  # Type guard for linter
            self.assertEqual(result.session_id, self.test_session_id)
            self.assertEqual(result.user_id, self.test_user_id)

    def test_learn_and_apply_preferences(self):
        """Test preference learning and application."""
        # Mock session state
        mock_session_state = Mock()
        mock_session_state.user_id = self.test_user_id

        # Mock messages with preference indicators
        test_messages = [
            {"role": "human", "content": "I prefer to use Python 3.12 for all projects"},
            {"role": "ai", "content": "I understand you prefer Python 3.12"},
            {"role": "human", "content": "Please give me detailed explanations"},
        ]

        # Mock storage methods
        self.continuity_manager.session_manager.get_session_state = Mock(return_value=mock_session_state)
        self.mock_storage.store_user_preference = Mock(return_value=True)
        self.mock_storage.retrieve_user_preferences = Mock(return_value=[])

        # Test preference learning
        result = self.continuity_manager.learn_and_apply_preferences(self.test_session_id, test_messages)

        self.assertIsInstance(result, PreferenceLearningResult)
        self.assertGreater(result.preferences_learned, 0)
        self.assertGreater(result.preferences_applied, 0)

    def test_resume_session_with_context(self):
        """Test session resume with context."""
        # Mock continuity state
        mock_continuity_state = SessionContinuityState(
            session_id=self.test_session_id,
            user_id=self.test_user_id,
            last_messages=[{"role": "human", "content": "test message"}],
            last_decisions=[{"decision_key": "test_decision", "head": "test"}],
            active_preferences={"python_version": {"value": "3.12", "confidence": 0.9}},
        )

        # Mock restoration
        self.continuity_manager.restore_session_state = Mock(return_value=mock_continuity_state)

        # Test resume
        result = self.continuity_manager.resume_session_with_context(self.test_user_id)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["session_id"], self.test_session_id)
        self.assertEqual(result["resume_type"], "continuity_restore")
        self.assertIn("last_messages", result)
        self.assertIn("last_decisions", result)
        self.assertIn("active_preferences", result)

    def test_resume_session_new_session(self):
        """Test session resume when no continuity state exists."""
        # Mock no continuity state
        self.continuity_manager.restore_session_state = Mock(return_value=None)
        self.continuity_manager.session_manager.create_session = Mock(return_value="new_session_001")

        # Test resume with new session
        result = self.continuity_manager.resume_session_with_context(self.test_user_id)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["session_id"], "new_session_001")
        self.assertEqual(result["resume_type"], "new_session")

    def test_preference_extraction(self):
        """Test preference extraction from messages."""
        test_messages = [
            {"role": "human", "content": "I always use Python 3.12 for my projects"},
            {"role": "human", "content": "Please give me detailed technical explanations"},
            {"role": "human", "content": "I prefer functional programming style"},
        ]

        # Test preference extraction
        preferences = self.continuity_manager._extract_preferences_from_messages(test_messages, self.test_user_id)

        self.assertGreater(len(preferences), 0)

        # Check for specific preferences
        preference_keys = [pref.preference_key for pref in preferences]
        self.assertIn("python_version", preference_keys)
        self.assertIn("explanation_detail", preference_keys)
        self.assertIn("coding_style", preference_keys)

    def test_preference_conflict_resolution(self):
        """Test preference conflict resolution."""
        # Mock existing preferences
        existing_preferences = [
            {
                "preference_key": "python_version",
                "preference_value": "3.11",
                "confidence_score": 0.7,
            }
        ]

        # Mock new preferences with higher confidence
        new_preferences = [
            UserPreference(
                user_id=self.test_user_id,
                preference_key="python_version",
                preference_value="3.12",
                preference_type="coding",
                confidence_score=0.9,
                source="learned_from_conversation",
            )
        ]

        # Mock storage methods
        self.mock_storage.retrieve_user_preferences.return_value = existing_preferences
        self.mock_storage.store_user_preference.return_value = True

        # Test conflict resolution
        conflicts_resolved = self.continuity_manager._resolve_preference_conflicts(self.test_user_id, new_preferences)

        self.assertEqual(conflicts_resolved, 1)
        self.mock_storage.store_user_preference.assert_called_once()

    def test_continuity_state_validation(self):
        """Test continuity state validation."""
        # Valid state
        valid_state = SessionContinuityState(
            session_id=self.test_session_id,
            user_id=self.test_user_id,
            last_activity=datetime.now(),
        )

        self.assertTrue(self.continuity_manager._validate_continuity_state(valid_state))

        # Expired state
        expired_state = SessionContinuityState(
            session_id=self.test_session_id,
            user_id=self.test_user_id,
            last_activity=datetime.now() - timedelta(hours=25),  # Beyond timeout
        )

        self.assertFalse(self.continuity_manager._validate_continuity_state(expired_state))

    def test_session_continuity_stats(self):
        """Test session continuity statistics."""
        # Mock session data
        mock_sessions = [
            {"session_id": "session_1", "status": "active"},
            {"session_id": "session_2", "status": "active"},
            {"session_id": "session_3", "status": "inactive"},
        ]

        # Mock storage methods
        self.continuity_manager.session_manager.get_user_sessions = Mock(return_value=mock_sessions)
        self.mock_storage.retrieve_context = Mock(
            side_effect=[
                [{"context_value": "test"}],  # session_1 has continuity state
                [],  # session_2 has no continuity state
                [{"context_value": "test"}],  # session_3 has continuity state
            ]
        )

        # Test stats
        stats = self.continuity_manager.get_session_continuity_stats(self.test_user_id)

        self.assertEqual(stats["total_sessions"], 3)
        self.assertEqual(stats["active_sessions"], 2)
        self.assertEqual(stats["continuity_states"], 2)
        self.assertEqual(stats["continuity_rate"], 2 / 3)


class TestPreferenceLearningResult(unittest.TestCase):
    """Test PreferenceLearningResult functionality."""

    def test_preference_learning_result_creation(self):
        """Test PreferenceLearningResult creation."""
        result = PreferenceLearningResult(
            preferences_learned=3,
            preferences_applied=2,
            confidence_scores={"python_version": 0.9, "coding_style": 0.8},
            learning_insights=["Learned 3 new preferences", "Applied 2 preferences to session"],
            conflicts_resolved=1,
        )

        self.assertEqual(result.preferences_learned, 3)
        self.assertEqual(result.preferences_applied, 2)
        self.assertEqual(len(result.confidence_scores), 2)
        self.assertEqual(len(result.learning_insights), 2)
        self.assertEqual(result.conflicts_resolved, 1)


if __name__ == "__main__":
    unittest.main()
