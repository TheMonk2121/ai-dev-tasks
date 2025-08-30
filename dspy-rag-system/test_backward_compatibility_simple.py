#!/usr/bin/env python3
"""
Simple Test for Backward Compatibility Flag System

This script tests the core functionality of the BackwardCompatibilityManager
without requiring complex dependencies or database connections.
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_compatibility_config():
    """Test CompatibilityConfig creation and persistence."""
    print("🧪 Testing CompatibilityConfig...")

    try:
        from utils.backward_compatibility import CompatibilityConfig

        # Test basic creation
        config = CompatibilityConfig(
            use_ltst_memory=True,
            fallback_to_static=True,
            log_path_usage=True,
            static_files_path="100_memory",
            ltst_memory_path="dspy-rag-system/src/utils",
        )

        print("✅ CompatibilityConfig created successfully")
        print(f"   Use LTST Memory: {config.use_ltst_memory}")
        print(f"   Fallback to Static: {config.fallback_to_static}")
        print(f"   Log Path Usage: {config.log_path_usage}")
        print(f"   Static Files Path: {config.static_files_path}")
        print(f"   LTST Memory Path: {config.ltst_memory_path}")

        # Test config persistence
        config.save_config()
        print(f"   ✅ Config saved to {config.config_file}")

        return True

    except Exception as e:
        print(f"❌ CompatibilityConfig test failed: {e}")
        return False


def test_backward_compatibility_manager():
    """Test BackwardCompatibilityManager functionality."""
    print("\n🧪 Testing BackwardCompatibilityManager...")

    try:
        from utils.backward_compatibility import BackwardCompatibilityManager, CompatibilityConfig

        # Create manager
        config = CompatibilityConfig(
            use_ltst_memory=True,
            fallback_to_static=True,
            log_path_usage=True,
        )
        manager = BackwardCompatibilityManager(config)

        print("✅ BackwardCompatibilityManager created successfully")
        print(f"   Static path usage: {manager.static_path_usage}")
        print(f"   LTST path usage: {manager.ltst_path_usage}")
        print(f"   Fallback usage: {manager.fallback_usage}")
        print(f"   Errors: {manager.errors}")

        return True

    except Exception as e:
        print(f"❌ BackwardCompatibilityManager test failed: {e}")
        return False


def test_memory_content_retrieval():
    """Test memory content retrieval functionality."""
    print("\n🧪 Testing memory content retrieval...")

    try:
        from utils.backward_compatibility import BackwardCompatibilityManager, CompatibilityConfig

        # Create manager
        config = CompatibilityConfig(
            use_ltst_memory=False,  # Disable LTST to test static fallback
            fallback_to_static=True,
            log_path_usage=True,
        )
        manager = BackwardCompatibilityManager(config)

        # Test memory content retrieval
        result = manager.get_memory_content("test query", "test_user")

        print("✅ Memory content retrieval completed")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Path used: {result.get('path_used', 'unknown')}")
        print(f"   Timestamp: {result.get('timestamp', 'unknown')}")

        if result.get("success", False):
            print(f"   Content keys: {list(result.get('content', {}).keys())}")

        return result.get("success", False)

    except Exception as e:
        print(f"❌ Memory content retrieval test failed: {e}")
        return False


def test_toggle_functionality():
    """Test toggle functionality."""
    print("\n🧪 Testing toggle functionality...")

    try:
        from utils.backward_compatibility import BackwardCompatibilityManager, CompatibilityConfig

        # Create manager
        config = CompatibilityConfig(
            use_ltst_memory=True,
            fallback_to_static=True,
            log_path_usage=True,
        )
        manager = BackwardCompatibilityManager(config)

        # Test initial state
        initial_state = manager.config.use_ltst_memory
        print(f"   Initial LTST state: {initial_state}")

        # Test toggle off
        success = manager.toggle_ltst_memory(False)
        print(f"   Toggle off success: {success}")
        print(f"   LTST state after toggle: {manager.config.use_ltst_memory}")

        # Test toggle on
        success = manager.toggle_ltst_memory(True)
        print(f"   Toggle on success: {success}")
        print(f"   LTST state after toggle: {manager.config.use_ltst_memory}")

        return success

    except Exception as e:
        print(f"❌ Toggle functionality test failed: {e}")
        return False


def test_agent_compatibility_validation():
    """Test agent compatibility validation."""
    print("\n🧪 Testing agent compatibility validation...")

    try:
        from utils.backward_compatibility import BackwardCompatibilityManager, CompatibilityConfig

        # Create manager
        config = CompatibilityConfig(
            use_ltst_memory=True,
            fallback_to_static=True,
            log_path_usage=True,
        )
        manager = BackwardCompatibilityManager(config)

        # Test validation
        validation = manager.validate_agent_compatibility()

        print("✅ Agent compatibility validation completed")
        print(f"   LTST Memory Available: {validation['ltst_memory_available']}")
        print(f"   Static Files Available: {validation['static_files_available']}")
        print(f"   Overall Status: {validation['overall_status']}")
        print(f"   Agent Regressions: {len(validation['agent_regressions'])}")

        if validation["agent_regressions"]:
            for regression in validation["agent_regressions"]:
                print(f"     - {regression}")

        return validation["overall_status"] != "error"

    except Exception as e:
        print(f"❌ Agent compatibility validation test failed: {e}")
        return False


def test_usage_statistics():
    """Test usage statistics functionality."""
    print("\n🧪 Testing usage statistics...")

    try:
        from utils.backward_compatibility import BackwardCompatibilityManager, CompatibilityConfig

        # Create manager
        config = CompatibilityConfig(
            use_ltst_memory=True,
            fallback_to_static=True,
            log_path_usage=True,
        )
        manager = BackwardCompatibilityManager(config)

        # Generate some usage
        manager.get_memory_content("test query 1", "test_user")
        manager.get_memory_content("test query 2", "test_user")

        # Get statistics
        stats = manager.get_usage_statistics()

        print("✅ Usage statistics retrieved")
        print(f"   LTST Path Usage: {stats['ltst_path_usage']}")
        print(f"   Static Path Usage: {stats['static_path_usage']}")
        print(f"   Fallback Usage: {stats['fallback_usage']}")
        print(f"   Errors: {stats['errors']}")
        print(f"   Total Requests: {stats['total_requests']}")
        print(f"   Success Rate: {stats['success_rate']}%")
        print(f"   Current Config: {stats['current_config']}")

        return True

    except Exception as e:
        print(f"❌ Usage statistics test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Backward Compatibility Flag Tests\n")

    tests = [
        ("CompatibilityConfig", test_compatibility_config),
        ("BackwardCompatibilityManager", test_backward_compatibility_manager),
        ("Memory Content Retrieval", test_memory_content_retrieval),
        ("Toggle Functionality", test_toggle_functionality),
        ("Agent Compatibility Validation", test_agent_compatibility_validation),
        ("Usage Statistics", test_usage_statistics),
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
        print("🎉 All tests passed! Backward compatibility functionality is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
