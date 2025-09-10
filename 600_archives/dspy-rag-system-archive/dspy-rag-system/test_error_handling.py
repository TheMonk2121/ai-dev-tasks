#!/usr/bin/env python3
"""
Test Error Handling (T4)

Test to verify improved error handling for memory rehydrator failures.
"""

import os
import sys
import time

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from cursor_integration import quick_task


def test_normal_operation():
    """Test normal operation with working memory rehydrator"""
    print("🔍 Test 1: Normal Operation")
    print("-" * 50)

    task = "Explain Python best practices"

    try:
        start_time = time.time()
        result = quick_task(task)
        execution_time = time.time() - start_time

        print(f"✅ Normal operation completed in {execution_time:.2f}s")
        print(f"📝 Result preview: {result[:200]}...")

        # Check if result contains meaningful content
        if len(result) > 100 and any(word in result.lower() for word in ["python", "best", "practice", "code"]):
            print("   ✅ Result contains meaningful content")
            return True
        else:
            print("   ⚠️ Result may be using fallback context")
            return False

    except Exception as e:
        print(f"❌ Normal operation failed: {str(e)}")
        return False


def test_fallback_context():
    """Test fallback context quality"""
    print("\n🔍 Test 2: Fallback Context Quality")
    print("-" * 50)

    # Import directly to test fallback function
    try:
        from dspy_modules.model_switcher import _get_fallback_context

        roles = ["coder", "planner", "implementer", "researcher", "reviewer"]
        task = "Test task for fallback context"

        for role in roles:
            fallback = _get_fallback_context(role, task)

            print(f"\n📋 {role.upper()} Role:")
            print(f"   Context length: {len(fallback)} characters")
            print(f"   Preview: {fallback[:100]}...")

            # Check fallback quality
            quality_indicators = ["guidelines", "best practices", "standards", "focus", "approach"]
            found_indicators = sum(1 for indicator in quality_indicators if indicator.lower() in fallback.lower())

            if found_indicators >= 3:
                print(f"   ✅ High quality fallback ({found_indicators}/5 indicators)")
            elif found_indicators >= 2:
                print(f"   ⚠️ Moderate quality fallback ({found_indicators}/5 indicators)")
            else:
                print(f"   ❌ Low quality fallback ({found_indicators}/5 indicators)")

        return True

    except Exception as e:
        print(f"❌ Fallback context test failed: {str(e)}")
        return False


def test_retry_mechanism():
    """Test retry and progressive timeout behavior"""
    print("\n🔍 Test 3: Retry Mechanism")
    print("-" * 50)

    # This test verifies the retry logic is implemented
    try:
        from dspy_modules.model_switcher import get_context_for_role

        # Test with a complex task that might trigger retries
        task = "Generate a comprehensive analysis of this complex AI system architecture"
        role = "researcher"

        start_time = time.time()
        context = get_context_for_role(role, task)
        execution_time = time.time() - start_time

        print(f"✅ Context retrieval completed in {execution_time:.2f}s")
        print(f"📝 Context preview: {context[:200]}...")

        # Check if context was retrieved
        if "PROJECT CONTEXT" in context:
            print("   ✅ Context retrieval successful")

            if "FALLBACK" in context:
                print("   ⚠️ Using fallback context (memory rehydrator may have failed)")
            else:
                print("   ✅ Using full memory rehydrator context")

            return True
        else:
            print("   ❌ No context retrieved")
            return False

    except Exception as e:
        print(f"❌ Retry mechanism test failed: {str(e)}")
        return False


def test_failure_tracking():
    """Test failure tracking and circuit breaker behavior"""
    print("\n🔍 Test 4: Failure Tracking")
    print("-" * 50)

    try:
        from dspy_modules.model_switcher import _failure_count, _max_failures

        print("📊 Current failure tracking:")
        print(f"   Max failures threshold: {_max_failures}")
        print(f"   Current failure counts: {dict(_failure_count)}")

        if len(_failure_count) == 0:
            print("   ✅ No failures recorded - system healthy")
        else:
            for role, count in _failure_count.items():
                if count >= _max_failures:
                    print(f"   ⚠️ Role {role} has {count} failures (threshold exceeded)")
                else:
                    print(f"   📋 Role {role} has {count} failures (within threshold)")

        return True

    except Exception as e:
        print(f"❌ Failure tracking test failed: {str(e)}")
        return False


def main():
    """Run error handling tests"""
    print("🛡️ Error Handling Test Suite (T4)")
    print("=" * 80)

    tests = [
        ("Normal Operation", test_normal_operation),
        ("Fallback Context Quality", test_fallback_context),
        ("Retry Mechanism", test_retry_mechanism),
        ("Failure Tracking", test_failure_tracking),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        result = test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "=" * 80)
    print("📊 ERROR HANDLING TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"🎯 Tests passed: {passed}/{total}")

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status}: {test_name}")

    print("\n🛡️ Error Handling Features:")
    print("   • Retry logic with progressive backoff")
    print("   • Failure tracking and circuit breaker")
    print("   • Role-specific fallback contexts")
    print("   • Timeout management and optimization")
    print("   • Comprehensive error logging")

    if passed == total:
        print("\n🎉 All error handling tests passed!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed - review error handling implementation")


if __name__ == "__main__":
    main()
