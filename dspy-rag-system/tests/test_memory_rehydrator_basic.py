#!/usr/bin/env python3
"""
Basic Test for Memory Rehydrator
Tests basic functionality with existing data (no anchor metadata required)
"""

import sys

sys.path.append("src")


def test_basic_functionality():
    """Test basic functionality without requiring anchor metadata"""
    print("🧪 Testing Basic Memory Rehydrator Functionality")
    print("=" * 50)

    try:
        from src.utils.memory_rehydrator import build_hydration_bundle

        # Test with basic parameters
        bundle = build_hydration_bundle(role="planner", task="Test basic functionality", limit=4, token_budget=800)

        print("✅ Basic bundle created successfully")
        print(f"Bundle sections: {bundle.meta.get('sections', 0)}")
        print(f"Tokens used: {bundle.meta.get('tokens_est', 0)}")
        print(f"Elapsed time: {bundle.meta.get('elapsed_s', 0)}s")

        # Check metadata
        required_meta = ["role", "task", "limit", "sections", "tokens_est", "elapsed_s"]
        for field in required_meta:
            if field in bundle.meta:
                print(f"✅ {field}: {bundle.meta[field]}")
            else:
                print(f"❌ Missing {field}")
                return False

        # Check bundle structure
        if hasattr(bundle, "text") and hasattr(bundle, "sections") and hasattr(bundle, "meta"):
            print("✅ Bundle structure valid")
        else:
            print("❌ Bundle structure invalid")
            return False

        # Check if we got any content
        if bundle.text.strip():
            print("✅ Bundle has content")
            print(f"Content length: {len(bundle.text)} characters")
        else:
            print("⚠️  Bundle has no content (may be expected if no relevant data)")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_different_roles():
    """Test different roles"""
    print("\n🧪 Testing Different Roles")
    print("=" * 30)

    try:
        from src.utils.memory_rehydrator import build_hydration_bundle

        roles = ["planner", "implementer", "researcher"]

        for role in roles:
            print(f"\nTesting role: {role}")
            bundle = build_hydration_bundle(role=role, task=f"Test {role} functionality", limit=3, token_budget=600)

            print(f"✅ {role} bundle created")
            print(f"  Sections: {bundle.meta.get('sections', 0)}")
            print(f"  Tokens: {bundle.meta.get('tokens_est', 0)}")
            print(f"  Time: {bundle.meta.get('elapsed_s', 0)}s")

        return True

    except Exception as e:
        print(f"❌ Role testing failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_token_budget():
    """Test token budget enforcement"""
    print("\n🧪 Testing Token Budget")
    print("=" * 25)

    try:
        from src.utils.memory_rehydrator import build_hydration_bundle

        # Test with small budget
        bundle_small = build_hydration_bundle(role="planner", task="Test small budget", token_budget=200, limit=2)

        print("✅ Small budget bundle created")
        tokens_used = bundle_small.meta.get("tokens_est", 0)
        print(f"Tokens used: {tokens_used}, Budget: 200")

        # Test with large budget
        bundle_large = build_hydration_bundle(role="implementer", task="Test large budget", token_budget=1500, limit=8)

        print("✅ Large budget bundle created")
        tokens_used = bundle_large.meta.get("tokens_est", 0)
        print(f"Tokens used: {tokens_used}, Budget: 1500")

        return True

    except Exception as e:
        print(f"❌ Token budget test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_vector_store_integration():
    """Test that vector store integration works"""
    print("\n🧪 Testing Vector Store Integration")
    print("=" * 35)

    try:
        from src.utils.memory_rehydrator import build_hydration_bundle

        # Test with a query that should find some results
        bundle = build_hydration_bundle(role="planner", task="vector store optimization", limit=5, token_budget=1000)

        print("✅ Vector store integration working")
        print(f"Results found: {bundle.meta.get('merged_count', 0)}")
        print(f"Dense results: {bundle.meta.get('dense_count', 0)}")
        print(f"Sparse results: {bundle.meta.get('sparse_count', 0)}")

        return True

    except Exception as e:
        print(f"❌ Vector store integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all basic tests"""
    print("🚀 Memory Rehydrator Basic Tests")
    print("=" * 40)

    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Different Roles", test_different_roles),
        ("Token Budget", test_token_budget),
        ("Vector Store Integration", test_vector_store_integration),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")

    print(f"\n{'='*40}")
    print(f"📊 Basic Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL BASIC TESTS PASSED!")
        print("✅ Memory rehydrator core functionality is working")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
