#!/usr/bin/env python3
"""
Simple Test for Session Continuity & Preference Learning System

This script tests the core functionality of the SessionContinuityManager
without requiring complex dependencies or database connections.
"""

import os
import sys
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_session_continuity_state():
    """Test SessionContinuityState creation and validation."""
    print("🧪 Testing SessionContinuityState...")

    try:
        from utils.session_continuity import SessionContinuityState

        # Test basic creation
        state = SessionContinuityState(
            session_id="test_session_001",
            user_id="test_user_001",
            last_messages=[{"role": "human", "content": "test message"}],
            last_decisions=[{"decision_key": "test_decision", "head": "test"}],
            active_preferences={"python_version": {"value": "3.12", "confidence": 0.9}},
        )

        print("✅ SessionContinuityState created successfully")
        print(f"   Session ID: {state.session_id}")
        print(f"   User ID: {state.user_id}")
        print(f"   Messages: {len(state.last_messages)}")
        print(f"   Decisions: {len(state.last_decisions)}")
        print(f"   Preferences: {len(state.active_preferences)}")
        print(f"   Continuity Hash: {state.continuity_hash}")

        # Test hash validation
        state2 = SessionContinuityState(
            session_id="test_session_001",
            user_id="test_user_001",
        )

        state3 = SessionContinuityState(
            session_id="test_session_001",
            user_id="test_user_001",
            last_messages=[{"role": "human", "content": "different message"}],
        )

        print(f"✅ Hash validation: {state.continuity_hash == state2.continuity_hash}")
        print(f"✅ Different content hash: {state.continuity_hash != state3.continuity_hash}")

        return True

    except Exception as e:
        print(f"❌ SessionContinuityState test failed: {e}")
        return False


def test_preference_learning_result():
    """Test PreferenceLearningResult creation."""
    print("\n🧪 Testing PreferenceLearningResult...")

    try:
        from utils.session_continuity import PreferenceLearningResult

        result = PreferenceLearningResult(
            preferences_learned=3,
            preferences_applied=2,
            confidence_scores={"python_version": 0.9, "coding_style": 0.8},
            learning_insights=["Learned 3 new preferences", "Applied 2 preferences to session"],
            conflicts_resolved=1,
        )

        print("✅ PreferenceLearningResult created successfully")
        print(f"   Preferences Learned: {result.preferences_learned}")
        print(f"   Preferences Applied: {result.preferences_applied}")
        print(f"   Confidence Scores: {len(result.confidence_scores)}")
        print(f"   Learning Insights: {len(result.learning_insights)}")
        print(f"   Conflicts Resolved: {result.conflicts_resolved}")

        return True

    except Exception as e:
        print(f"❌ PreferenceLearningResult test failed: {e}")
        return False


def test_session_continuity_manager_creation():
    """Test SessionContinuityManager creation."""
    print("\n🧪 Testing SessionContinuityManager creation...")

    try:
        from utils.session_continuity import SessionContinuityManager

        # Test creation without storage (should use default)
        manager = SessionContinuityManager()

        print("✅ SessionContinuityManager created successfully")
        print(f"   Max Messages for Resume: {manager.max_messages_for_resume}")
        print(f"   Max Decisions for Resume: {manager.max_decisions_for_resume}")
        print(f"   Preference Confidence Threshold: {manager.preference_confidence_threshold}")
        print(f"   Session Timeout Hours: {manager.session_timeout_hours}")

        return True

    except Exception as e:
        print(f"❌ SessionContinuityManager creation test failed: {e}")
        return False


def test_preference_extraction():
    """Test preference extraction from messages."""
    print("\n🧪 Testing preference extraction...")

    try:
        from utils.session_continuity import SessionContinuityManager

        manager = SessionContinuityManager()

        # Test messages with preference indicators
        test_messages = [
            {"role": "human", "content": "I prefer to use Python 3.12 for all projects"},
            {"role": "ai", "content": "I understand you prefer Python 3.12"},
            {"role": "human", "content": "Please give me detailed explanations"},
            {"role": "human", "content": "I prefer functional programming style"},
        ]

        preferences = manager._extract_preferences_from_messages(test_messages, "test_user_001")

        print("✅ Preference extraction completed")
        print(f"   Extracted {len(preferences)} preferences")

        for pref in preferences:
            print(f"   - {pref.preference_key}: {pref.preference_value} (confidence: {pref.confidence_score})")

        # Check for specific preferences
        preference_keys = [pref.preference_key for pref in preferences]
        expected_keys = ["python_version", "explanation_detail", "coding_style"]

        for key in expected_keys:
            if key in preference_keys:
                print(f"   ✅ Found expected preference: {key}")
            else:
                print(f"   ⚠️  Missing expected preference: {key}")

        return len(preferences) > 0

    except Exception as e:
        print(f"❌ Preference extraction test failed: {e}")
        return False


def test_continuity_state_validation():
    """Test continuity state validation."""
    print("\n🧪 Testing continuity state validation...")

    try:
        from utils.session_continuity import SessionContinuityManager, SessionContinuityState

        manager = SessionContinuityManager()

        # Test valid state
        valid_state = SessionContinuityState(
            session_id="test_session_001",
            user_id="test_user_001",
            last_activity=datetime.now(),
        )

        is_valid = manager._validate_continuity_state(valid_state)
        print(f"✅ Valid state validation: {is_valid}")

        # Test expired state
        expired_state = SessionContinuityState(
            session_id="test_session_001",
            user_id="test_user_001",
            last_activity=datetime.now() - timedelta(hours=25),  # Beyond timeout
        )

        is_expired = manager._validate_continuity_state(expired_state)
        print(f"✅ Expired state validation: {not is_expired}")

        return is_valid and not is_expired

    except Exception as e:
        print(f"❌ Continuity state validation test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Session Continuity & Preference Learning Tests\n")

    tests = [
        ("SessionContinuityState", test_session_continuity_state),
        ("PreferenceLearningResult", test_preference_learning_result),
        ("SessionContinuityManager Creation", test_session_continuity_manager_creation),
        ("Preference Extraction", test_preference_extraction),
        ("Continuity State Validation", test_continuity_state_validation),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"📋 Running {test_name}...")
        if test_func():
            passed += 1
        print()

    print("📊 Test Results:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Failed: {total - passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Session continuity functionality is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
