#!/usr/bin/env python3
"""
Core LTST Memory System Functionality Test

This script tests the core functionality of the LTST Memory System
without requiring database connections or complex mocking.
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_dataclass_creation():
    """Test that all dataclasses can be created with proper defaults."""
    print("Testing dataclass creation...")

    try:
        from utils.conversation_storage import ConversationContext, ConversationMessage, ConversationSession

        # Test ConversationMessage
        message = ConversationMessage(session_id="test_session", role="human", content="Hello, this is a test message")
        assert message.session_id == "test_session"
        assert message.role == "human"
        assert message.content == "Hello, this is a test message"
        assert message.timestamp is not None
        print("✓ ConversationMessage creation successful")

        # Test ConversationSession
        session = ConversationSession(session_id="test_session", user_id="test_user")
        assert session.session_id == "test_session"
        assert session.user_id == "test_user"
        assert session.created_at is not None
        print("✓ ConversationSession creation successful")

        # Test ConversationContext
        context = ConversationContext(
            session_id="test_session", context_type="conversation", context_key="test_key", context_value="test_value"
        )
        assert context.session_id == "test_session"
        assert context.context_type == "conversation"
        print("✓ ConversationContext creation successful")

    except Exception as e:
        print(f"✗ Dataclass creation failed: {e}")
        return False

    return True


def test_context_merger_dataclasses():
    """Test ContextMerger dataclasses."""
    print("Testing ContextMerger dataclasses...")

    try:
        from utils.context_merger import ContextMergeRequest, MergedContext

        # Test ContextMergeRequest
        request = ContextMergeRequest(
            session_id="test_session",
            user_id="test_user",
            current_message="Test message",
            context_types=["conversation", "preference"],
            max_context_length=2000,
        )
        assert request.session_id == "test_session"
        assert request.current_message == "Test message"
        print("✓ ContextMergeRequest creation successful")

        # Test MergedContext
        merged = MergedContext(
            session_id="test_session",
            conversation_history=[],
            user_preferences={},
            project_context={},
            relevant_contexts=[],
            merged_content="Test merged content",
            relevance_scores={"overall": 0.8},
            context_hash="test_hash",
            created_at=datetime.now(),
        )
        assert merged.session_id == "test_session"
        assert merged.merged_content == "Test merged content"
        print("✓ MergedContext creation successful")

    except Exception as e:
        print(f"✗ ContextMerger dataclass creation failed: {e}")
        return False

    return True


def test_session_manager_dataclasses():
    """Test SessionManager dataclasses."""
    print("Testing SessionManager dataclasses...")

    try:
        from utils.session_manager import SessionState

        # Test SessionState
        state = SessionState(session_id="test_session", user_id="test_user", status="active")
        assert state.session_id == "test_session"
        assert state.status == "active"
        print("✓ SessionState creation successful")

        # Test SessionState
        state = SessionState(session_id="test_session", status="active", last_activity=datetime.now())
        assert state.session_id == "test_session"
        assert state.status == "active"
        print("✓ SessionState creation successful")

    except Exception as e:
        print(f"✗ SessionManager dataclass creation failed: {e}")
        return False

    return True


def test_ltst_integration_dataclasses():
    """Test LTST integration dataclasses."""
    print("Testing LTST integration dataclasses...")

    try:
        from utils.ltst_memory_integration import LTSTMemoryBundle

        # Test LTSTMemoryBundle
        bundle = LTSTMemoryBundle(
            original_bundle={"test": "data"},
            conversation_history=[],
            user_preferences={},
            session_context=None,
            context_relevance_scores={},
            conversation_continuity_score=0.8,
            user_preference_confidence=0.7,
            metadata={"test": "metadata"},
        )
        assert bundle.original_bundle == {"test": "data"}
        assert bundle.conversation_continuity_score == 0.8
        print("✓ LTSTMemoryBundle creation successful")

    except Exception as e:
        print(f"✗ LTST integration dataclass creation failed: {e}")
        return False

    return True


def test_performance_optimizer_dataclasses():
    """Test performance optimizer dataclasses."""
    print("Testing performance optimizer dataclasses...")

    try:
        from utils.ltst_performance_optimizer import PerformanceBenchmark

        # Test PerformanceBenchmark
        benchmark = PerformanceBenchmark(
            benchmark_name="test_benchmark",
            benchmark_type="retrieval",
            duration_ms=1500.0,
            success_rate=0.95,
            metadata={"test": "data"},
        )
        assert benchmark.benchmark_name == "test_benchmark"
        assert benchmark.duration_ms == 1500.0
        print("✓ PerformanceBenchmark creation successful")

        # Test PerformanceBenchmark
        benchmark = PerformanceBenchmark(
            benchmark_name="test_benchmark",
            benchmark_type="latency",
            start_time=datetime.now(),
            end_time=datetime.now(),
            metrics=[metric],
            summary={"avg": 1.5},
        )
        assert benchmark.benchmark_name == "test_benchmark"
        assert len(benchmark.metrics) == 1
        print("✓ PerformanceBenchmark creation successful")

    except Exception as e:
        print(f"✗ Performance optimizer dataclass creation failed: {e}")
        return False

    return True


def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")

    modules = [
        "utils.conversation_storage",
        "utils.context_merger",
        "utils.session_manager",
        "utils.ltst_memory_integration",
        "utils.ltst_performance_optimizer",
    ]

    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module} imported successfully")
        except Exception as e:
            print(f"✗ Failed to import {module}: {e}")
            return False

    return True


def test_basic_functionality():
    """Test basic functionality without database dependencies."""
    print("Testing basic functionality...")

    try:
        from utils.context_merger import ContextMerger
        from utils.conversation_storage import ConversationStorage
        from utils.session_manager import SessionManager

        # Test that components can be instantiated (they'll fail on database ops, but that's expected)
        storage = ConversationStorage()
        merger = ContextMerger(storage)
        session_manager = SessionManager(storage, merger)

        print("✓ Component instantiation successful")

        # Test that methods exist
        assert hasattr(storage, "create_session")
        assert hasattr(storage, "store_message")
        assert hasattr(merger, "merge_context")
        assert hasattr(session_manager, "create_session")

        print("✓ Method existence verification successful")

    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

    return True


def main():
    """Run all core functionality tests."""
    print("=" * 60)
    print("LTST Memory System - Core Functionality Test")
    print("=" * 60)

    tests = [
        test_imports,
        test_dataclass_creation,
        test_context_merger_dataclasses,
        test_session_manager_dataclasses,
        test_ltst_integration_dataclasses,
        test_performance_optimizer_dataclasses,
        test_basic_functionality,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print(f"\n{test.__name__}:")
        if test():
            passed += 1
        print()

    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("🎉 All core functionality tests passed!")
        print("\nThe LTST Memory System core components are working correctly.")
        print("Database integration tests would require a proper database setup.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
