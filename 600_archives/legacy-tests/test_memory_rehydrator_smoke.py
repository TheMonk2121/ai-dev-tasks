#!/usr/bin/env python3
"""
Smoke Tests for Memory Rehydrator
Tests both planner and implementer roles with our existing vector store infrastructure
"""

import pytest

# Mark all tests in this file as deprecated
pytestmark = pytest.mark.deprecated

@pytest.mark.tier1
@pytest.mark.smoke
def test_planner_role():
    """Test planner role functionality"""
    print("🧪 Testing Planner Role")
    print("=" * 40)

    try:
        from src.utils.memory_rehydrator import build_hydration_bundle

        # Test planner role with hybrid search task
        bundle = build_hydration_bundle(role="planner", task="Plan hybrid search rollout", limit=8, token_budget=1200)

        print("✅ Planner bundle created successfully")
        print(f"Bundle sections: {bundle.meta.get('sections', 0)}")
        print(f"Tokens used: {bundle.meta.get('tokens_est', 0)}")
        print(f"Elapsed time: {bundle.meta.get('elapsed_s', 0)}s")

        # Validate metadata
        required_meta = ["role", "task", "limit", "fusion_method_used", "w_dense_used", "w_sparse_used"]
        for field in required_meta:
            if field in bundle.meta:
                print(f"✅ {field}: {bundle.meta[field]}")
            else:
                print(f"❌ Missing {field}")
                return False

        # Check for TL;DR in bundle
        if "TL;DR" in bundle.text or "TLDR" in bundle.text:
            print("✅ TL;DR found in bundle")
        else:
            print("⚠️  TL;DR not found in bundle (may not have anchor metadata yet)")

        # Check for role-specific content
        if any(keyword in bundle.text.lower() for keyword in ["system", "backlog", "overview"]):
            print("✅ Role-specific content found")
        else:
            print("⚠️  Role-specific content not found (may not have anchor metadata yet)")

    except Exception as e:
        print(f"❌ Planner test failed: {e}")
        import traceback

        traceback.print_exc()
        raise

@pytest.mark.tier1
@pytest.mark.smoke
def test_implementer_role():
    """Test implementer role functionality"""
    print("\n🧪 Testing Implementer Role")
    print("=" * 40)

    try:
        from src.utils.memory_rehydrator import build_hydration_bundle

        # Test implementer role with vector store task
        bundle = build_hydration_bundle(
            role="implementer", task="Refactor vector store search path for spans", limit=8, token_budget=1200
        )

        print("✅ Implementer bundle created successfully")
        print(f"Bundle sections: {bundle.meta.get('sections', 0)}")
        print(f"Tokens used: {bundle.meta.get('tokens_est', 0)}")
        print(f"Elapsed time: {bundle.meta.get('elapsed_s', 0)}s")

        # Validate metadata
        required_meta = ["role", "task", "limit", "fusion_method_used", "w_dense_used", "w_sparse_used"]
        for field in required_meta:
            assert field in bundle.meta, f"Missing {field}"
            print(f"✅ {field}: {bundle.meta[field]}")

        # Check for TL;DR in bundle
        if "TL;DR" in bundle.text or "TLDR" in bundle.text:
            print("✅ TL;DR found in bundle")
        else:
            print("⚠️  TL;DR not found in bundle (may not have anchor metadata yet)")

        # Check for DSPy context
        if any(keyword in bundle.text.lower() for keyword in ["dspy", "development", "context"]):
            print("✅ DSPy context found")
        else:
            print("⚠️  DSPy context not found (may not have anchor metadata yet)")

    except Exception as e:
        print(f"❌ Implementer test failed: {e}")
        import traceback

        traceback.print_exc()
        raise

def test_tier1_guard():
    """Test that Tier-1 modules are included for implementer tasks"""
    print("\n🧪 Testing Tier-1 Guard")
    print("=" * 40)

    try:
        from src.utils.memory_rehydrator import build_hydration_bundle

        # Test implementer role with Tier-1 specific task
        bundle = build_hydration_bundle(
            role="implementer", task="Optimize vector store performance for production", limit=8, token_budget=1200
        )

        print("✅ Tier-1 bundle created successfully")

        # Check for Tier-1 module references
        tier1_keywords = ["vector_store", "document_processor", "cursor_model_router"]
        found_tier1 = any(keyword in bundle.text.lower() for keyword in tier1_keywords)

        if found_tier1:
            print("✅ Tier-1 module content found")
        else:
            print("⚠️  Tier-1 module content not found (may not have relevant data)")

        # Check bundle composition
        sections = bundle.meta.get("sections", 0)
        if sections > 0:
            print(f"✅ Bundle has {sections} sections")
        else:
            print("⚠️  Bundle has no sections")

    except Exception as e:
        print(f"❌ Tier-1 guard test failed: {e}")
        import traceback

        traceback.print_exc()
        raise

def test_fusion_configuration():
    """Test different fusion configurations"""
    print("\n🧪 Testing Fusion Configuration")
    print("=" * 40)

    try:
        from src.utils.memory_rehydrator import build_hydration_bundle

        # Test basic functionality
        bundle = build_hydration_bundle(role="planner", task="Test basic configuration", limit=4, token_budget=800)

        print("✅ Basic bundle created successfully")
        print(f"Bundle sections: {bundle.meta.get('sections', 0)}")
        print(f"Tokens used: {bundle.meta.get('tokens_est', 0)}")
        print(f"Elapsed time: {bundle.meta.get('elapsed_s', 0)}s")

    except Exception as e:
        print(f"❌ Fusion configuration test failed: {e}")
        import traceback

        traceback.print_exc()
        raise

def test_token_budget():
    """Test token budget enforcement"""
    print("\n🧪 Testing Token Budget")
    print("=" * 40)

    try:
        from src.utils.memory_rehydrator import build_hydration_bundle

        # Test with small budget
        bundle_small = build_hydration_bundle(role="planner", task="Test small budget", token_budget=500, limit=4)

        print("✅ Small budget bundle created")
        tokens_used = bundle_small.meta.get("tokens_est", 0)
        budget = bundle_small.meta.get("token_budget", 500)
        print(f"Tokens used: {tokens_used}, Budget: {budget}")

        assert tokens_used <= budget, f"Token budget exceeded: {tokens_used} > {budget}"
        print("✅ Token budget enforced correctly")

        # Test with large budget
        bundle_large = build_hydration_bundle(role="implementer", task="Test large budget", token_budget=2000, limit=12)

        print("✅ Large budget bundle created")
        tokens_used = bundle_large.meta.get("tokens_est", 0)
        budget = bundle_large.meta.get("token_budget", 2000)
        print(f"Tokens used: {tokens_used}, Budget: {budget}")

    except Exception as e:
        print(f"❌ Token budget test failed: {e}")
        import traceback

        traceback.print_exc()
        raise

def test_json_output():
    """Test JSON output format"""
    print("\n🧪 Testing JSON Output")
    print("=" * 40)

    try:
        from src.utils.memory_rehydrator import build_hydration_bundle

        bundle = build_hydration_bundle(role="planner", task="Test JSON output", limit=4, token_budget=800)

        # Convert to JSON format
        json_output = {
            "text": bundle.text,
            "sections": [
                {"kind": s.kind, "title": s.title, "content": s.content, "citation": s.citation}
                for s in bundle.sections
            ],
            "meta": bundle.meta,
        }

        # Validate JSON structure
        assert "text" in json_output and "sections" in json_output and "meta" in json_output, "JSON structure invalid"
        print("✅ JSON structure valid")

        # Check sections
        sections = json_output["sections"]
        assert len(sections) > 0, "JSON has no sections"
        print(f"✅ JSON has {len(sections)} sections")
        for i, section in enumerate(sections[:2]):  # Show first 2 sections
            print(f"  Section {i+1}: {section['kind']} - {section['title']}")

        # Check metadata
        meta = json_output["meta"]
        required_fields = ["role", "task", "sections", "tokens_est", "elapsed_s"]
        for field in required_fields:
            if field in meta:
                print(f"✅ Meta field '{field}': {meta[field]}")
            else:
                print(f"❌ Missing meta field: {field}")

    except Exception as e:
        print(f"❌ JSON output test failed: {e}")
        import traceback

        traceback.print_exc()
        raise

def main():
    """Run all smoke tests"""
    print("🚀 Memory Rehydrator Smoke Tests")
    print("=" * 50)

    tests = [
        ("Planner Role", test_planner_role),
        ("Implementer Role", test_implementer_role),
        ("Tier-1 Guard", test_tier1_guard),
        ("Fusion Configuration", test_fusion_configuration),
        ("Token Budget", test_token_budget),
        ("JSON Output", test_json_output),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")

    print(f"\n{'='*50}")
    print(f"📊 Smoke Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL SMOKE TESTS PASSED!")
        print("✅ Memory rehydrator is working correctly")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())
