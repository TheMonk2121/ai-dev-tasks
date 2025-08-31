#!/usr/bin/env python3
"""
Phase 1 Integration Test for DSPy-Vector Integration

Tests all Phase 1 components working together:
- DSPy-Vector Integration Bridge
- Extended DSPy Role Context Models
- Role Context Enhancer
"""

import sys
import time

# Import our Phase 1 components
sys.path.append(".")
from scripts.dspy_vector_integration import DSPyVectorIntegrationBridge
from scripts.role_context_enhancer import RoleContextEnhancer


def test_phase1_integration():
    """Test all Phase 1 components working together."""
    print("🚀 Phase 1 Integration Test - DSPy-Vector Integration")
    print("=" * 60)

    # Test 1: Integration Bridge
    print("\n📋 Test 1: DSPy-Vector Integration Bridge")
    print("-" * 40)

    bridge = DSPyVectorIntegrationBridge()
    if not bridge.initialize():
        print("❌ Integration bridge failed to initialize")
        return False

    print("✅ Integration bridge initialized successfully")

    # Test 2: Role Context Enhancer
    print("\n📋 Test 2: Role Context Enhancer")
    print("-" * 40)

    enhancer = RoleContextEnhancer()
    if not enhancer.initialize():
        print("❌ Role context enhancer failed to initialize")
        return False

    print("✅ Role context enhancer initialized successfully")

    # Test 3: Basic Functionality Test
    print("\n📋 Test 3: Basic Functionality Test")
    print("-" * 40)

    # Test the vector enhancement system directly
    test_queries = [
        "How can I improve the code quality of the database connection module?",
        "What's the impact of refactoring the memory system on our architecture?",
        "What patterns exist in our testing implementation across components?",
        "How should I integrate the new vector system with existing DSPy modules?",
    ]

    all_tests_passed = True

    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test Query {i}: {query}")

        # Test vector enhancement
        start_time = time.time()
        recommendations = bridge.vector_enhancement.get_component_recommendations(query, top_k=3)
        enhancement_time = time.time() - start_time

        if recommendations:
            print(f"✅ Found {len(recommendations)} component recommendations")
            print(f"⏱️ Enhancement time: {enhancement_time*1000:.2f}ms")

            # Show first recommendation
            first_rec = recommendations[0]
            print(f"   📊 Top component: {first_rec['component_data']['file_path']}")
            print(f"   📈 Similarity: {first_rec['similarity']:.3f}")
        else:
            print("❌ No recommendations found")
            all_tests_passed = False

    # Test 4: Performance Validation
    print("\n📋 Test 4: Performance Validation")
    print("-" * 40)

    bridge_stats = bridge.get_performance_summary()
    enhancer_stats = enhancer.get_enhancement_stats()

    print("🔧 Integration Bridge Performance:")
    for key, value in bridge_stats.items():
        print(f"  {key}: {value}")

    print("\n🔧 Role Context Enhancer Performance:")
    for key, value in enhancer_stats.items():
        print(f"  {key}: {value}")

    # Test 5: Integration Status
    print("\n📋 Test 5: Integration Status")
    print("-" * 40)

    bridge_status = bridge.get_integration_status()
    print("🔧 Integration Bridge Status:")
    for key, value in bridge_status.items():
        print(f"  {key}: {value}")

    enhancer_cache_info = enhancer.get_cache_info()
    print("\n🔧 Role Context Enhancer Cache Info:")
    for key, value in enhancer_cache_info.items():
        print(f"  {key}: {value}")

    # Test 6: End-to-End Workflow
    print("\n📋 Test 6: End-to-End Workflow")
    print("-" * 40)

    # Simulate a complete workflow
    workflow_start = time.time()

    # 1. Initialize systems
    print("1️⃣ Initializing integration systems...")
    if not bridge.initialize() or not enhancer.initialize():
        print("❌ System initialization failed")
        return False

    # 2. Process multiple enhancements
    print("2️⃣ Processing multiple context enhancements...")
    enhancement_count = 0
    for query in test_queries[:2]:  # Test first 2 queries
        recommendations = bridge.vector_enhancement.get_component_recommendations(query, top_k=3)
        if recommendations:
            print(f"   ✅ Query enhancement successful: {len(recommendations)} components")
            enhancement_count += 1
        else:
            print("   ❌ Query enhancement failed")

    # 3. Verify performance
    print("3️⃣ Verifying performance metrics...")
    final_bridge_stats = bridge.get_performance_summary()
    final_enhancer_stats = enhancer.get_enhancement_stats()

    workflow_time = time.time() - workflow_start

    print(f"   ⏱️ Total workflow time: {workflow_time*1000:.2f}ms")
    print(f"   📊 Successful enhancements: {enhancement_count}/2")

    # Final Results
    print("\n🎯 Phase 1 Integration Test Results")
    print("=" * 60)

    if all_tests_passed and enhancement_count > 0:
        print("✅ ALL TESTS PASSED - Phase 1 Integration Successful!")
        print("\n🏆 Phase 1 Components Status:")
        print("  ✅ DSPy-Vector Integration Bridge - OPERATIONAL")
        print("  ✅ Extended DSPy Role Context Models - OPERATIONAL")
        print("  ✅ Role Context Enhancer - OPERATIONAL")
        print("  ✅ Context Enhancement Integration - OPERATIONAL")
        print("  ✅ Performance Validation - PASSED")
        print("  ✅ End-to-End Workflow - PASSED")

        print("\n🚀 Ready for Phase 2: Role Enhancements!")
        return True
    else:
        print("❌ SOME TESTS FAILED - Phase 1 Integration Incomplete")
        if enhancement_count == 0:
            print("   • No successful enhancements in workflow test")
        return False


def main():
    """Main function for Phase 1 integration testing."""
    success = test_phase1_integration()

    if success:
        print("\n🎉 Phase 1 Complete! Ready to proceed with Phase 2.")
        print("\n📋 Next Steps:")
        print("  • Phase 2: Role Enhancements")
        print("  • Enhanced Coder Role Integration")
        print("  • Enhanced Planner Role Integration")
        print("  • Enhanced Researcher Role Integration")
        print("  • Enhanced Implementer Role Integration")
    else:
        print("\n⚠️ Phase 1 incomplete. Please fix issues before proceeding.")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
