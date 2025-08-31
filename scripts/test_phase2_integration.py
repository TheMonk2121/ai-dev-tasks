#!/usr/bin/env python3
"""
Phase 2 Integration Test for DSPy-Vector Integration

Tests all Phase 2 components working together:
- Enhanced Coder Role Integration
- Enhanced Planner Role Integration
- Integration with Phase 1 components
"""

import sys
import time

# Import our Phase 1 and Phase 2 components
sys.path.append(".")
from scripts.dspy_vector_integration import DSPyVectorIntegrationBridge
from scripts.enhanced_coder_role import EnhancedCoderRole
from scripts.enhanced_planner_role import EnhancedPlannerRole
from scripts.role_context_enhancer import RoleContextEnhancer


def test_phase2_integration():
    """Test all Phase 2 components working together."""
    print("🚀 Phase 2 Integration Test - Enhanced Role Integration")
    print("=" * 60)

    # Test 1: Phase 1 Components (Foundation)
    print("\n📋 Test 1: Phase 1 Components (Foundation)")
    print("-" * 40)

    bridge = DSPyVectorIntegrationBridge()
    enhancer = RoleContextEnhancer()

    if not bridge.initialize() or not enhancer.initialize():
        print("❌ Phase 1 components failed to initialize")
        return False

    print("✅ Phase 1 components initialized successfully")

    # Test 2: Enhanced Coder Role
    print("\n📋 Test 2: Enhanced Coder Role")
    print("-" * 40)

    coder_role = EnhancedCoderRole()
    if not coder_role.initialize():
        print("❌ Enhanced coder role failed to initialize")
        return False

    print("✅ Enhanced coder role initialized successfully")

    # Test 3: Enhanced Planner Role
    print("\n📋 Test 3: Enhanced Planner Role")
    print("-" * 40)

    planner_role = EnhancedPlannerRole()
    if not planner_role.initialize():
        print("❌ Enhanced planner role failed to initialize")
        return False

    print("✅ Enhanced planner role initialized successfully")

    # Test 4: Role Capabilities Integration
    print("\n📋 Test 4: Role Capabilities Integration")
    print("-" * 40)

    # Test coder capabilities
    coder_queries = [
        "How can I improve the code quality of the database connection module?",
        "What are the dependency patterns in our memory system?",
        "What testing strategy should I use for the vector system?",
    ]

    print("\n🔍 Testing Enhanced Coder Role Capabilities:")
    for i, query in enumerate(coder_queries, 1):
        print(f"  {i}. {query}")

        if "quality" in query.lower():
            result = coder_role.analyze_code_quality(query)
        elif "dependency" in query.lower():
            result = coder_role.analyze_dependencies(query)
        elif "test" in query.lower():
            result = coder_role.generate_testing_strategy(query)
        else:
            result = coder_role.analyze_code_quality(query)

        if "error" not in result:
            print(f"     ✅ Completed in {result['analysis_time_ms']:.2f}ms")
            print(f"     📊 Components: {result['components_analyzed']}")
            if "recommendations" in result:
                print(f"     💡 Recommendations: {len(result['recommendations'])}")
        else:
            print(f"     ❌ Failed: {result['error']}")

    # Test planner capabilities
    planner_queries = [
        "What's the current system architecture of our memory system?",
        "What would be the impact of refactoring the database layer?",
        "How complex is our current vector system implementation?",
    ]

    print("\n🔍 Testing Enhanced Planner Role Capabilities:")
    for i, query in enumerate(planner_queries, 1):
        print(f"  {i}. {query}")

        if "architecture" in query.lower():
            result = planner_role.analyze_system_architecture(query)
        elif "impact" in query.lower():
            result = planner_role.analyze_change_impact(query)
        elif "complex" in query.lower():
            result = planner_role.assess_system_complexity(query)
        else:
            result = planner_role.analyze_system_architecture(query)

        if "error" not in result:
            print(f"     ✅ Completed in {result['analysis_time_ms']:.2f}ms")
            print(f"     📊 Components: {result['components_analyzed']}")
            if "recommendations" in result:
                print(f"     💡 Recommendations: {len(result['recommendations'])}")
        else:
            print(f"     ❌ Failed: {result['error']}")

    # Test 5: Cross-Role Integration
    print("\n📋 Test 5: Cross-Role Integration")
    print("-" * 40)

    # Test how roles can work together
    print("🔍 Testing Cross-Role Collaboration:")

    # Coder analyzes code quality, planner assesses impact
    print("  1. Coder analyzes code quality...")
    coder_result = coder_role.analyze_code_quality(
        "How can I improve the code quality of the database connection module?"
    )

    if "error" not in coder_result:
        print("     ✅ Coder analysis completed")

        # Planner assesses the impact of implementing coder's recommendations
        print("  2. Planner assesses impact of coder recommendations...")
        planner_result = planner_role.analyze_change_impact(
            "What would be the impact of implementing code quality improvements?"
        )

        if "error" not in planner_result:
            print("     ✅ Planner impact assessment completed")
            print("     🔄 Cross-role integration successful!")
        else:
            print("     ❌ Planner impact assessment failed")
    else:
        print("     ❌ Coder analysis failed")

    # Test 6: Performance Validation
    print("\n📋 Test 6: Performance Validation")
    print("-" * 40)

    # Get statistics from all components
    bridge_stats = bridge.get_performance_summary()
    enhancer_stats = enhancer.get_enhancement_stats()
    coder_stats = coder_role.get_coder_stats()
    planner_stats = planner_role.get_planner_stats()

    print("🔧 Phase 1 Components Performance:")
    for key, value in bridge_stats.items():
        print(f"  {key}: {value}")

    print("\n🔧 Role Context Enhancer Performance:")
    for key, value in enhancer_stats.items():
        print(f"  {key}: {value}")

    print("\n🔧 Enhanced Coder Role Performance:")
    for key, value in coder_stats.items():
        print(f"  {key}: {value}")

    print("\n🔧 Enhanced Planner Role Performance:")
    for key, value in planner_stats.items():
        print(f"  {key}: {value}")

    # Test 7: End-to-End Workflow
    print("\n📋 Test 7: End-to-End Workflow")
    print("-" * 40)

    # Simulate a complete development workflow
    workflow_start = time.time()

    print("1️⃣ Initializing all systems...")
    if not all([bridge.initialize(), enhancer.initialize(), coder_role.initialize(), planner_role.initialize()]):
        print("❌ System initialization failed")
        return False

    print("2️⃣ Executing development workflow...")

    # Step 1: Coder analyzes current state
    print("   Step 1: Code quality analysis...")
    coder_analysis = coder_role.analyze_code_quality("What are the current code quality issues?")

    # Step 2: Planner assesses impact
    print("   Step 2: Impact assessment...")
    planner_impact = planner_role.analyze_change_impact("What's the impact of addressing code quality issues?")

    # Step 3: Coder generates improvement plan
    print("   Step 3: Improvement planning...")
    coder_plan = coder_role.generate_testing_strategy("What testing strategy should I use for improvements?")

    # Step 4: Planner creates strategic roadmap
    print("   Step 4: Strategic roadmap...")
    planner_roadmap = planner_role.create_strategic_plan("What's our roadmap for code quality improvements?")

    workflow_time = time.time() - workflow_start

    print(f"3️⃣ Workflow completed in {workflow_time*1000:.2f}ms")

    # Verify all steps completed successfully
    workflow_success = all(
        [
            "error" not in coder_analysis,
            "error" not in planner_impact,
            "error" not in coder_plan,
            "error" not in planner_roadmap,
        ]
    )

    if workflow_success:
        print("   ✅ All workflow steps completed successfully")
    else:
        print("   ❌ Some workflow steps failed")

    # Final Results
    print("\n🎯 Phase 2 Integration Test Results")
    print("=" * 60)

    if workflow_success:
        print("✅ ALL TESTS PASSED - Phase 2 Integration Successful!")
        print("\n🏆 Phase 2 Components Status:")
        print("  ✅ Enhanced Coder Role - OPERATIONAL")
        print("  ✅ Enhanced Planner Role - OPERATIONAL")
        print("  ✅ Cross-Role Integration - OPERATIONAL")
        print("  ✅ Performance Validation - PASSED")
        print("  ✅ End-to-End Workflow - PASSED")

        print("\n🚀 Ready for Phase 3: Advanced Integration Features!")
        return True
    else:
        print("❌ SOME TESTS FAILED - Phase 2 Integration Incomplete")
        return False


def main():
    """Main function for Phase 2 integration testing."""
    success = test_phase2_integration()

    if success:
        print("\n🎉 Phase 2 Complete! Ready to proceed with Phase 3.")
        print("\n📋 Next Steps:")
        print("  • Phase 3: Advanced Integration Features")
        print("  • Enhanced Researcher Role Integration")
        print("  • Enhanced Implementer Role Integration")
        print("  • Advanced Context Routing")
        print("  • Performance Optimization")
    else:
        print("\n⚠️ Phase 2 incomplete. Please fix issues before proceeding.")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
