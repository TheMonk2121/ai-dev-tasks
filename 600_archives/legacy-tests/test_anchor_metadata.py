#!/usr/bin/env python3
"""
Test Anchor Metadata Parser

Tests the HTML comment parsing and metadata extraction functionality.
"""

import pytest

# Mark all tests in this file as deprecated
pytestmark = pytest.mark.deprecated

from utils.anchor_metadata_parser import (
    AnchorMetadata,
    extract_anchor_metadata,
    validate_anchor_metadata,
)


@pytest.mark.tier2
@pytest.mark.unit
def test_canonical_anchor_extraction():
    """Test extraction of canonical anchor keys"""
    print("🧪 Testing Canonical Anchor Extraction")
    print("=" * 40)

    test_cases = [
        {
            "name": "TL;DR anchor",
            "content": "<!-- ANCHOR_KEY: tldr -->\n# Test Document\nContent here",
            "expected_key": "tldr",
            "expected_priority": 0,
        },
        {
            "name": "Quick start anchor",
            "content": "<!-- ANCHOR_KEY: quick-start -->\n<!-- ANCHOR_PRIORITY: 1 -->\n# Test Document",
            "expected_key": "quick-start",
            "expected_priority": 1,
        },
        {
            "name": "Commands anchor",
            "content": "<!-- ANCHOR_KEY: commands -->\n<!-- ANCHOR_PRIORITY: 3 -->\n# Test Document",
            "expected_key": "commands",
            "expected_priority": 3,
        },
    ]

    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        metadata = extract_anchor_metadata(test_case["content"])

        assert (
            metadata.anchor_key == test_case["expected_key"]
        ), f"Expected {test_case['expected_key']}, got {metadata.anchor_key}"
        print(f"✅ Anchor key: {metadata.anchor_key}")

        assert (
            metadata.anchor_priority == test_case["expected_priority"]
        ), f"Expected priority {test_case['expected_priority']}, got {metadata.anchor_priority}"
        print(f"✅ Priority: {metadata.anchor_priority}")


@pytest.mark.tier2
@pytest.mark.unit
def test_role_pin_extraction():
    """Test extraction of role pins"""
    print("\n🧪 Testing Role Pin Extraction")
    print("=" * 35)

    test_cases = [
        {
            "name": "Single role pin",
            "content": '<!-- ROLE_PINS: ["planner"] -->\n# Test Document',
            "expected_roles": ["planner"],
        },
        {
            "name": "Multiple role pins",
            "content": '<!-- ROLE_PINS: ["implementer", "researcher"] -->\n# Test Document',
            "expected_roles": ["implementer", "researcher"],
        },
        {
            "name": "Quoted role pins",
            "content": '<!-- ROLE_PINS: ["planner", "implementer"] -->\n# Test Document',
            "expected_roles": ["planner", "implementer"],
        },
        {
            "name": "Mixed quotes",
            "content": "<!-- ROLE_PINS: [\"planner\", 'implementer'] -->\n# Test Document",
            "expected_roles": ["planner", "implementer"],
        },
    ]

    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        metadata = extract_anchor_metadata(test_case["content"])

        assert (
            metadata.role_pins == test_case["expected_roles"]
        ), f"Expected {test_case['expected_roles']}, got {metadata.role_pins}"
        print(f"✅ Role pins: {metadata.role_pins}")


@pytest.mark.tier2
@pytest.mark.unit
def test_custom_anchor_extraction():
    """Test extraction of custom anchor keys"""
    print("\n🧪 Testing Custom Anchor Extraction")
    print("=" * 35)

    test_cases = [
        {
            "name": "Valid custom anchor",
            "content": "<!-- ANCHOR_KEY: my-custom-anchor -->\n<!-- ANCHOR_PRIORITY: 50 -->\n# Test Document",
            "expected_key": "my-custom-anchor",
            "expected_priority": 50,
        },
        {
            "name": "Custom anchor with role pins",
            "content": '<!-- ANCHOR_KEY: api-docs -->\n<!-- ANCHOR_PRIORITY: 25 -->\n<!-- ROLE_PINS: ["implementer"] -->\n# API Documentation',
            "expected_key": "api-docs",
            "expected_priority": 25,
            "expected_roles": ["implementer"],
        },
    ]

    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        metadata = extract_anchor_metadata(test_case["content"])

        assert (
            metadata.anchor_key == test_case["expected_key"]
        ), f"Expected {test_case['expected_key']}, got {metadata.anchor_key}"
        print(f"✅ Custom anchor key: {metadata.anchor_key}")

        assert (
            metadata.anchor_priority == test_case["expected_priority"]
        ), f"Expected priority {test_case['expected_priority']}, got {metadata.anchor_priority}"
        print(f"✅ Priority: {metadata.anchor_priority}")

        if "expected_roles" in test_case:
            assert (
                metadata.role_pins == test_case["expected_roles"]
            ), f"Expected roles {test_case['expected_roles']}, got {metadata.role_pins}"
            print(f"✅ Role pins: {metadata.role_pins}")


def test_validation():
    """Test metadata validation"""
    print("\n🧪 Testing Metadata Validation")
    print("=" * 30)

    test_cases = [
        {
            "name": "Valid canonical anchor",
            "metadata": AnchorMetadata(anchor_key="tldr", anchor_priority=0),
            "should_be_valid": True,
        },
        {
            "name": "Invalid priority range",
            "metadata": AnchorMetadata(anchor_key="tldr", anchor_priority=1000),
            "should_be_valid": False,
        },
        {"name": "Invalid role", "metadata": AnchorMetadata(role_pins=["invalid-role"]), "should_be_valid": False},
        {
            "name": "Valid custom anchor",
            "metadata": AnchorMetadata(anchor_key="my-custom-anchor", anchor_priority=50),
            "should_be_valid": True,
        },
        {
            "name": "Invalid custom anchor format",
            "metadata": AnchorMetadata(anchor_key="invalid@anchor"),
            "should_be_valid": False,
        },
        {
            "name": "Canonical anchor with wrong priority",
            "metadata": AnchorMetadata(anchor_key="quick-start", anchor_priority=5),
            "should_be_valid": False,
        },
    ]

    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        errors = validate_anchor_metadata(test_case["metadata"])

        if test_case["should_be_valid"]:
            assert not errors, f"Expected valid, got errors: {errors}"
            print("✅ Valid (no errors)")
        else:
            assert errors, "Expected invalid, but no errors found"
            print(f"✅ Invalid (expected): {errors}")


def test_complex_extraction():
    """Test complex metadata extraction scenarios"""
    print("\n🧪 Testing Complex Extraction")
    print("=" * 30)

    complex_content = """
# Test Document

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["planner", "implementer"] -->

## TL;DR

This is a test document with complex metadata.

<!-- ANCHOR_KEY: quick-start -->
<!-- ANCHOR_PRIORITY: 1 -->

## Quick Start

Here are the quick start steps.

<!-- ROLE_PINS: ["researcher"] -->

## Research Section

This section is pinned for researchers.
"""

    print("Testing complex document with multiple metadata blocks")
    metadata = extract_anchor_metadata(complex_content)

    # Should get the first anchor_key found
    assert metadata.anchor_key == "tldr", f"Expected 'tldr', got '{metadata.anchor_key}'"
    print("✅ First anchor key extracted: tldr")

    # Should get the first priority found
    assert metadata.anchor_priority == 0, f"Expected 0, got {metadata.anchor_priority}"
    print("✅ First priority extracted: 0")

    # Should get the first role_pins found
    assert metadata.role_pins == [
        "planner",
        "implementer",
    ], f"Expected ['planner', 'implementer'], got {metadata.role_pins}"
    print("✅ First role pins extracted: ['planner', 'implementer']")


def test_to_dict_conversion():
    """Test conversion to dictionary for JSONB storage"""
    print("\n🧪 Testing Dictionary Conversion")
    print("=" * 35)

    metadata = AnchorMetadata(anchor_key="tldr", anchor_priority=0, role_pins=["planner", "implementer"])

    result = metadata.to_dict()
    expected = {"anchor_key": "tldr", "anchor_priority": 0, "role_pins": ["planner", "implementer"]}

    assert result == expected, f"Expected {expected}, got {result}"
    print("✅ Dictionary conversion correct")
    print(f"Result: {result}")

    # Test with partial metadata
    partial_metadata = AnchorMetadata(anchor_key="quick-start")
    partial_result = partial_metadata.to_dict()
    partial_expected = {"anchor_key": "quick-start"}

    assert partial_result == partial_expected, f"Expected {partial_expected}, got {partial_result}"
    print("✅ Partial dictionary conversion correct")
    print(f"Result: {partial_result}")


def main():
    """Run all tests"""
    print("🚀 Anchor Metadata Parser Tests")
    print("=" * 40)

    tests = [
        ("Canonical Anchor Extraction", test_canonical_anchor_extraction),
        ("Role Pin Extraction", test_role_pin_extraction),
        ("Custom Anchor Extraction", test_custom_anchor_extraction),
        ("Validation", test_validation),
        ("Complex Extraction", test_complex_extraction),
        ("Dictionary Conversion", test_to_dict_conversion),
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
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Anchor metadata parser is working correctly")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
