#!/usr/bin/env python3
"""
Test Anchor Metadata Parser

Tests the HTML comment parsing and metadata extraction functionality.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.anchor_metadata_parser import AnchorMetadata, extract_anchor_metadata, validate_anchor_metadata


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

        if metadata.anchor_key == test_case["expected_key"]:
            print(f"✅ Anchor key: {metadata.anchor_key}")
        else:
            print(f"❌ Expected {test_case['expected_key']}, got {metadata.anchor_key}")
            return False

        if metadata.anchor_priority == test_case["expected_priority"]:
            print(f"✅ Priority: {metadata.anchor_priority}")
        else:
            print(f"❌ Expected priority {test_case['expected_priority']}, got {metadata.anchor_priority}")
            return False

    return True


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

        if metadata.role_pins == test_case["expected_roles"]:
            print(f"✅ Role pins: {metadata.role_pins}")
        else:
            print(f"❌ Expected {test_case['expected_roles']}, got {metadata.role_pins}")
            return False

    return True


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

        if metadata.anchor_key == test_case["expected_key"]:
            print(f"✅ Custom anchor key: {metadata.anchor_key}")
        else:
            print(f"❌ Expected {test_case['expected_key']}, got {metadata.anchor_key}")
            return False

        if metadata.anchor_priority == test_case["expected_priority"]:
            print(f"✅ Priority: {metadata.anchor_priority}")
        else:
            print(f"❌ Expected priority {test_case['expected_priority']}, got {metadata.anchor_priority}")
            return False

        if "expected_roles" in test_case:
            if metadata.role_pins == test_case["expected_roles"]:
                print(f"✅ Role pins: {metadata.role_pins}")
            else:
                print(f"❌ Expected roles {test_case['expected_roles']}, got {metadata.role_pins}")
                return False

    return True


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
            if not errors:
                print("✅ Valid (no errors)")
            else:
                print(f"❌ Expected valid, got errors: {errors}")
                return False
        else:
            if errors:
                print(f"✅ Invalid (expected): {errors}")
            else:
                print("❌ Expected invalid, but no errors found")
                return False

    return True


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
    if metadata.anchor_key == "tldr":
        print("✅ First anchor key extracted: tldr")
    else:
        print(f"❌ Expected 'tldr', got '{metadata.anchor_key}'")
        return False

    # Should get the first priority found
    if metadata.anchor_priority == 0:
        print("✅ First priority extracted: 0")
    else:
        print(f"❌ Expected 0, got {metadata.anchor_priority}")
        return False

    # Should get the first role_pins found
    if metadata.role_pins == ["planner", "implementer"]:
        print("✅ First role pins extracted: ['planner', 'implementer']")
    else:
        print(f"❌ Expected ['planner', 'implementer'], got {metadata.role_pins}")
        return False

    return True


def test_to_dict_conversion():
    """Test conversion to dictionary for JSONB storage"""
    print("\n🧪 Testing Dictionary Conversion")
    print("=" * 35)

    metadata = AnchorMetadata(anchor_key="tldr", anchor_priority=0, role_pins=["planner", "implementer"])

    result = metadata.to_dict()
    expected = {"anchor_key": "tldr", "anchor_priority": 0, "role_pins": ["planner", "implementer"]}

    if result == expected:
        print("✅ Dictionary conversion correct")
        print(f"Result: {result}")
    else:
        print(f"❌ Expected {expected}, got {result}")
        return False

    # Test with partial metadata
    partial_metadata = AnchorMetadata(anchor_key="quick-start")
    partial_result = partial_metadata.to_dict()
    partial_expected = {"anchor_key": "quick-start"}

    if partial_result == partial_expected:
        print("✅ Partial dictionary conversion correct")
        print(f"Result: {partial_result}")
    else:
        print(f"❌ Expected {partial_expected}, got {partial_result}")
        return False

    return True


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
