#!/usr/bin/env python3
"""
Test Document Processor with Anchor Metadata

Tests the integration of anchor metadata extraction in the document processor.
"""

import os
import sys
import tempfile

# Add the parent directory to the path to find src
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from src.dspy_modules.document_processor import DocumentProcessor


def test_anchor_metadata_in_chunks():
    """Test that anchor metadata is extracted and included in chunks"""
    print("🧪 Testing Document Processor with Anchor Metadata")
    print("=" * 55)

    # Create a test document with anchor metadata
    test_content = """# Test Document

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["planner", "implementer"] -->

## TL;DR

This is a test document with anchor metadata.

<!-- ANCHOR_KEY: quick-start -->
<!-- ANCHOR_PRIORITY: 1 -->

## Quick Start

Here are the quick start steps.

## Regular Content

This is regular content without anchor metadata.

<!-- ANCHOR_KEY: api-docs -->
<!-- ANCHOR_PRIORITY: 50 -->
<!-- ROLE_PINS: ["implementer"] -->

## API Documentation

This section has custom anchor metadata.
"""

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(test_content)
        temp_file = f.name

    try:
        # Initialize document processor
        processor = DocumentProcessor(chunk_size=200, chunk_overlap=20)

        # Process the document
        result = processor.forward(temp_file)

        print("✅ Document processed successfully")
        print(f"📄 Total chunks: {result['total_chunks']}")
        print(f"📁 Document ID: {result['document_id']}")

        # Check chunks for anchor metadata
        chunks_with_metadata = 0
        anchor_keys_found = set()
        role_pins_found = set()

        for chunk in result["chunks"]:
            print(f"\n📝 Chunk {chunk['chunk_index']}:")
            print(f"   Text preview: {chunk['text'][:100]}...")

            if "metadata" in chunk:
                chunks_with_metadata += 1
                metadata = chunk["metadata"]
                print(f"   ✅ Has metadata: {metadata}")

                if "anchor_key" in metadata:
                    anchor_keys_found.add(metadata["anchor_key"])

                if "role_pins" in metadata:
                    role_pins_found.update(metadata["role_pins"])
            else:
                print("   ❌ No metadata")

        print("\n📊 Metadata Summary:")
        print(f"   Chunks with metadata: {chunks_with_metadata}/{len(result['chunks'])}")
        print(f"   Anchor keys found: {anchor_keys_found}")
        print(f"   Role pins found: {role_pins_found}")

        # Validate results
        if chunks_with_metadata > 0:
            print("✅ Anchor metadata extraction working")
        else:
            print("❌ No anchor metadata found")
            return False

        if "tldr" in anchor_keys_found:
            print("✅ TL;DR anchor detected")
        else:
            print("❌ TL;DR anchor not found")
            return False

        if "quick-start" in anchor_keys_found:
            print("✅ Quick-start anchor detected")
        else:
            print("❌ Quick-start anchor not found")
            return False

        if "api-docs" in anchor_keys_found:
            print("✅ Custom anchor detected")
        else:
            print("❌ Custom anchor not found")
            return False

        if "planner" in role_pins_found and "implementer" in role_pins_found:
            print("✅ Role pins detected")
        else:
            print("❌ Role pins not found")
            return False

        return True

    except Exception as e:
        print(f"❌ Error processing document: {e}")
        return False

    finally:
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_no_anchor_metadata():
    """Test document without anchor metadata"""
    print("\n🧪 Testing Document Without Anchor Metadata")
    print("=" * 45)

    # Create a test document without anchor metadata
    test_content = """# Test Document

## Introduction

This is a test document without any anchor metadata.

## Content

Regular content here.

## Conclusion

End of document.
"""

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(test_content)
        temp_file = f.name

    try:
        # Initialize document processor
        processor = DocumentProcessor(chunk_size=200, chunk_overlap=20)

        # Process the document
        result = processor.forward(temp_file)

        print("✅ Document processed successfully")
        print(f"📄 Total chunks: {result['total_chunks']}")

        # Check that no chunks have metadata
        chunks_with_metadata = 0

        for chunk in result["chunks"]:
            if "metadata" in chunk:
                chunks_with_metadata += 1
                print(f"❌ Unexpected metadata in chunk {chunk['chunk_index']}: {chunk['metadata']}")

        if chunks_with_metadata == 0:
            print("✅ No unexpected metadata found")
            return True
        else:
            print(f"❌ Found {chunks_with_metadata} chunks with unexpected metadata")
            return False

    except Exception as e:
        print(f"❌ Error processing document: {e}")
        return False

    finally:
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def main():
    """Run all tests"""
    print("🚀 Document Processor Anchor Metadata Tests")
    print("=" * 50)

    tests = [
        ("Anchor Metadata in Chunks", test_anchor_metadata_in_chunks),
        ("No Anchor Metadata", test_no_anchor_metadata),
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
        print("✅ Document processor anchor metadata integration working")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
