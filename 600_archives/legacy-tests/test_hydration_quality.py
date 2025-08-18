#!/usr/bin/env python3.11
"""
Hydration Quality Tests
Comprehensive test suite for memory rehydrator quality validation
"""

import time

from src.utils.memory_rehydrator import build_hydration_bundle

def test_planner_context_quality():
    """Test planner role context assembly quality"""
    print("🧪 Testing Planner Context Quality")
    print("=" * 40)

    try:
        # Test planning-specific task
        bundle = build_hydration_bundle(
            role="planner", task="strategic planning for Q4 development", limit=8, token_budget=1200
        )

        print(f"✅ Planner bundle created: {bundle.meta.get('sections', 0)} sections")
        print(f"✅ Tokens used: {bundle.meta.get('tokens_est', 0)}")

        # Validate content quality
        text = bundle.text.lower()

        # Check for essential planning content
        planning_keywords = ["backlog", "priority", "system", "overview", "planning"]
        found_keywords = [kw for kw in planning_keywords if kw in text]

        print(f"✅ Found planning keywords: {found_keywords}")

        # Check for anchor content
        anchor_checks = {
            "tldr": "tl;" in text or "tldr" in text,
            "quick_start": "quick-start" in text or "quick start" in text,
            "commands": "commands" in text,
        }

        for anchor, found in anchor_checks.items():
            status = "✅" if found else "❌"
            print(f"{status} {anchor}: {found}")

        # Quality score calculation
        keyword_score = len(found_keywords) / len(planning_keywords)
        anchor_score = sum(anchor_checks.values()) / len(anchor_checks)
        overall_score = (keyword_score + anchor_score) / 2

        print(f"📊 Quality Score: {overall_score:.2f} ({overall_score*100:.0f}%)")

        return overall_score >= 0.7  # 70% quality threshold

    except Exception as e:
        print(f"❌ Planner quality test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

def test_implementer_context_quality():
    """Test implementer role context assembly quality"""
    print("\n🧪 Testing Implementer Context Quality")
    print("=" * 40)

    try:
        # Test implementation-specific task
        bundle = build_hydration_bundle(
            role="implementer", task="implement new DSPy module for context assembly", limit=8, token_budget=1200
        )

        print(f"✅ Implementer bundle created: {bundle.meta.get('sections', 0)} sections")
        print(f"✅ Tokens used: {bundle.meta.get('tokens_est', 0)}")

        # Validate content quality
        text = bundle.text.lower()

        # Check for essential implementation content
        implementation_keywords = ["dspy", "development", "implementation", "code", "technical"]
        found_keywords = [kw for kw in implementation_keywords if kw in text]

        print(f"✅ Found implementation keywords: {found_keywords}")

        # Check for anchor content
        anchor_checks = {
            "tldr": "tl;" in text or "tldr" in text,
            "quick_start": "quick-start" in text or "quick start" in text,
            "commands": "commands" in text,
        }

        for anchor, found in anchor_checks.items():
            status = "✅" if found else "❌"
            print(f"{status} {anchor}: {found}")

        # Quality score calculation
        keyword_score = len(found_keywords) / len(implementation_keywords)
        anchor_score = sum(anchor_checks.values()) / len(anchor_checks)
        overall_score = (keyword_score + anchor_score) / 2

        print(f"📊 Quality Score: {overall_score:.2f} ({overall_score*100:.0f}%)")

        return overall_score >= 0.7  # 70% quality threshold

    except Exception as e:
        print(f"❌ Implementer quality test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

def test_performance_benchmarks():
    """Test performance benchmarks for bundle creation"""
    print("\n🧪 Testing Performance Benchmarks")
    print("=" * 40)

    try:
        test_cases = [
            ("planner", "strategic planning", 1200),
            ("implementer", "code implementation", 1200),
            ("planner", "priority assessment", 800),
            ("implementer", "debugging", 1000),
        ]

        results = {}
        total_time = 0

        for role, task, budget in test_cases:
            start_time = time.time()
            bundle = build_hydration_bundle(role=role, task=task, token_budget=budget)
            end_time = time.time()

            creation_time = end_time - start_time
            total_time += creation_time

            results[f"{role}_{task}"] = {
                "creation_time": creation_time,
                "sections": bundle.meta.get("sections", 0),
                "tokens": bundle.meta.get("tokens_est", 0),
                "budget": budget,
                "efficiency": bundle.meta.get("tokens_est", 0) / budget,
            }

            print(f"✅ {role} - {task}: {creation_time:.3f}s, {bundle.meta.get('sections', 0)} sections")

        avg_time = total_time / len(test_cases)
        print(f"\n📊 Average creation time: {avg_time:.3f}s")
        print(f"📊 Total test time: {total_time:.3f}s")

        # Performance thresholds
        performance_passed = avg_time < 5.0  # 5 second threshold
        print(f"📊 Performance: {'✅ PASSED' if performance_passed else '❌ FAILED'}")

        return performance_passed

    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")
        import traceback

        traceback.print_exc()
        return False

def test_token_budget_efficiency():
    """Test token budget efficiency and adherence"""
    print("\n🧪 Testing Token Budget Efficiency")
    print("=" * 40)

    try:
        test_budgets = [500, 800, 1200, 2000]
        results = {}

        for budget in test_budgets:
            bundle = build_hydration_bundle(role="planner", task="token budget efficiency test", token_budget=budget)

            tokens_used = bundle.meta.get("tokens_est", 0)
            efficiency = tokens_used / budget if budget > 0 else 0

            results[budget] = {
                "tokens_used": tokens_used,
                "budget": budget,
                "efficiency": efficiency,
                "sections": bundle.meta.get("sections", 0),
            }

            print(f"✅ Budget {budget}: {tokens_used} tokens ({efficiency:.1%} efficiency)")

        # Calculate overall efficiency
        avg_efficiency = sum(r["efficiency"] for r in results.values()) / len(results)
        print(f"\n📊 Average efficiency: {avg_efficiency:.1%}")

        # Efficiency threshold
        efficiency_passed = avg_efficiency >= 0.6  # 60% efficiency threshold
        print(f"📊 Efficiency: {'✅ PASSED' if efficiency_passed else '❌ FAILED'}")

        return efficiency_passed

    except Exception as e:
        print(f"❌ Token budget efficiency test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

def test_workflow_integration():
    """Test hydration integration with real workflows"""
    print("\n🧪 Testing Workflow Integration")
    print("=" * 40)

    try:
        # Test planning workflow
        print("📋 Testing Planning Workflow:")

        # Step 1: Initial assessment
        assessment_bundle = build_hydration_bundle(
            role="planner", task="assess current project state", token_budget=1200
        )
        print(f"  ✅ Assessment: {assessment_bundle.meta.get('sections', 0)} sections")

        # Step 2: Priority review
        priority_bundle = build_hydration_bundle(role="planner", task="review backlog priorities", token_budget=1000)
        print(f"  ✅ Priority: {priority_bundle.meta.get('sections', 0)} sections")

        # Step 3: Strategic decision
        decision_bundle = build_hydration_bundle(
            role="planner", task="make strategic architecture decision", token_budget=1200
        )
        print(f"  ✅ Decision: {decision_bundle.meta.get('sections', 0)} sections")

        # Test implementation workflow
        print("\n🔧 Testing Implementation Workflow:")

        # Step 1: Code review
        review_bundle = build_hydration_bundle(role="implementer", task="review code implementation", token_budget=1200)
        print(f"  ✅ Review: {review_bundle.meta.get('sections', 0)} sections")

        # Step 2: Technical design
        design_bundle = build_hydration_bundle(role="implementer", task="design technical solution", token_budget=1000)
        print(f"  ✅ Design: {design_bundle.meta.get('sections', 0)} sections")

        # Step 3: Debugging
        debug_bundle = build_hydration_bundle(role="implementer", task="debug technical issues", token_budget=1200)
        print(f"  ✅ Debug: {debug_bundle.meta.get('sections', 0)} sections")

        # Validate all bundles have content
        all_bundles = [assessment_bundle, priority_bundle, decision_bundle, review_bundle, design_bundle, debug_bundle]

        workflow_passed = all(bundle.meta.get("sections", 0) > 0 for bundle in all_bundles)
        print(f"\n📊 Workflow Integration: {'✅ PASSED' if workflow_passed else '❌ FAILED'}")

        return workflow_passed

    except Exception as e:
        print(f"❌ Workflow integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

def main():
    """Run all hydration quality tests"""
    print("🚀 Hydration Quality Test Suite")
    print("=" * 50)

    tests = [
        ("Planner Context Quality", test_planner_context_quality),
        ("Implementer Context Quality", test_implementer_context_quality),
        ("Performance Benchmarks", test_performance_benchmarks),
        ("Token Budget Efficiency", test_token_budget_efficiency),
        ("Workflow Integration", test_workflow_integration),
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

    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Hydration system quality validated")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())
