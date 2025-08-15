#!/usr/bin/env python3
"""
Test Few-Shot Integration

Simple test script to verify that few-shot integration is working correctly
across both the documentation validator and memory update script.
"""

import sys


def test_few_shot_framework():
    """Test the few-shot integration framework."""
    print("🧪 Testing Few-Shot Integration Framework...")

    try:
        from few_shot_integration import FewShotExampleLoader

        # Test loading examples
        loader = FewShotExampleLoader()
        examples = loader.load_examples()

        print(f"✅ Loaded {len(examples)} example categories:")
        for category, example_list in examples.items():
            print(f"   - {category}: {len(example_list)} examples")

        # Test pattern extraction
        doc_examples = loader.load_examples_by_category("documentation_coherence")
        patterns = loader.extract_patterns(doc_examples)

        print(f"✅ Extracted {len(patterns)} patterns from documentation examples")

        # Test pattern application
        test_content = """
        # Test Document

        <!-- MODULE_REFERENCE: 400_guides/400_system-overview.md -->
        <!-- MEMORY_CONTEXT: HIGH - Essential documentation -->

        | B‑074 | Few-Shot Integration | 🔥 | 0.5 | todo | Test integration |
        """

        results = loader.apply_patterns_to_content(test_content, patterns)

        print("✅ Applied patterns to test content:")
        print(f"   - Matched patterns: {len(results.get('matched_patterns', []))}")
        print(f"   - Validation suggestions: {len(results.get('validation_suggestions', []))}")

        return True

    except Exception as e:
        print(f"❌ Few-shot framework test failed: {e}")
        return False


def test_doc_validator_integration():
    """Test few-shot integration in documentation validator."""
    print("\n🧪 Testing Documentation Validator Integration...")

    try:
        from doc_coherence_validator import OptimizedDocCoherenceValidator

        # Test with few-shot enabled
        validator = OptimizedDocCoherenceValidator(dry_run=True, only_changed=True, enable_few_shot=True)
        # Verify the validator has the expected attributes
        assert hasattr(validator, "enable_few_shot"), "Validator should have few-shot attribute"
        print("✅ Documentation validator with few-shot integration initialized")

        # Test with few-shot disabled
        validator_no_fs = OptimizedDocCoherenceValidator(dry_run=True, only_changed=True, enable_few_shot=False)
        # Verify the validator has the expected attributes
        assert hasattr(validator_no_fs, "enable_few_shot"), "Validator should have few-shot attribute"
        print("✅ Documentation validator without few-shot integration initialized")

        return True

    except Exception as e:
        print(f"❌ Documentation validator integration test failed: {e}")
        return False


def test_memory_update_integration():
    """Test few-shot integration in memory update script."""
    print("\n🧪 Testing Memory Update Integration...")

    try:
        from update_cursor_memory import extract_backlog_priorities

        # Test with few-shot enabled
        priorities_fs = extract_backlog_priorities(enable_few_shot=True)
        print(f"✅ Memory update with few-shot: {len(priorities_fs)} priorities extracted")

        # Test with few-shot disabled
        priorities_no_fs = extract_backlog_priorities(enable_few_shot=False)
        print(f"✅ Memory update without few-shot: {len(priorities_no_fs)} priorities extracted")

        return True

    except Exception as e:
        print(f"❌ Memory update integration test failed: {e}")
        return False


def main():
    """Run all few-shot integration tests."""
    print("🎯 Few-Shot Integration Test Suite")
    print("=" * 50)

    tests = [test_few_shot_framework, test_doc_validator_integration, test_memory_update_integration]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("✅ All few-shot integration tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
