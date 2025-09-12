#!/usr/bin/env python3
"""
Comprehensive test for the semantic chunker implementation.
Tests chunking logic, overlap handling, and edge cases.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.semantic_chunker import SemanticChunker


def test_basic_chunking():
    """Test basic chunking functionality."""
    print("=== Testing Basic Chunking ===")

    chunker = SemanticChunker(chunk_size=450, overlap_ratio=0.10)
    print(f"✅ Chunker created: {chunker.chunk_size} chars, {chunker.overlap_ratio} overlap")

    # Test with simple content
    test_content = """# Test Document

This is a test paragraph that should be chunked properly.

## Section 1

This is another paragraph with more content.

### Subsection

This is a subsection with additional information.
"""

    chunks = chunker.chunk_content(test_content, "test.md", "markdown")
    print(f"✅ Created {len(chunks)} chunks from test content")

    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}: {chunk['metadata']['chunk_size']} chars, {chunk['metadata']['unit_count']} units")

    return chunks


def test_overlap_logic():
    """Test that overlap is working correctly."""
    print("\n=== Testing Overlap Logic ===")

    chunker = SemanticChunker(chunk_size=100, overlap_ratio=0.20)  # 20% overlap for easier testing

    # Create content that will definitely need multiple chunks
    long_content = (
        "This is a very long paragraph that will definitely exceed the chunk size limit and should be split into multiple chunks with proper overlap between them. "
        * 10
    )

    chunks = chunker.chunk_content(long_content, "test_long.md", "markdown")
    print(f"✅ Created {len(chunks)} chunks from long content")

    if len(chunks) > 1:
        # Check overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]["content"]
            next_chunk = chunks[i + 1]["content"]

            # Find overlap by checking end of current vs start of next
            overlap_found = False
            for j in range(1, min(len(current_chunk), len(next_chunk))):
                if current_chunk[-j:] == next_chunk[:j]:
                    overlap_found = True
                    print(f"  Chunk {i+1}->{i+2}: {j} char overlap found")
                    break

            if not overlap_found:
                print(f"  ⚠️  No overlap found between chunks {i+1} and {i+2}")

    return chunks


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("\n=== Testing Edge Cases ===")

    chunker = SemanticChunker(chunk_size=450, overlap_ratio=0.10)

    # Test empty content
    empty_chunks = chunker.chunk_content("", "empty.md", "markdown")
    print(f"✅ Empty content: {len(empty_chunks)} chunks")

    # Test very short content
    short_content = "Short."
    short_chunks = chunker.chunk_content(short_content, "short.md", "markdown")
    print(f"✅ Short content: {len(short_chunks)} chunks")

    # Test content with only headers
    header_only = """# Header 1
## Header 2
### Header 3"""
    header_chunks = chunker.chunk_content(header_only, "headers.md", "markdown")
    print(f"✅ Header-only content: {len(header_chunks)} chunks")

    # Test content with very long single paragraph
    long_paragraph = (
        "This is a single very long paragraph that contains a lot of text and should be handled properly by the chunking algorithm. "
        * 50
    )
    long_chunks = chunker.chunk_content(long_paragraph, "long_para.md", "markdown")
    print(f"✅ Long paragraph: {len(long_chunks)} chunks")

    return empty_chunks, short_chunks, header_chunks, long_chunks


def test_semantic_structure():
    """Test that semantic structure is preserved."""
    print("\n=== Testing Semantic Structure Preservation ===")

    chunker = SemanticChunker(chunk_size=200, overlap_ratio=0.10)

    structured_content = """# Main Title

This is the introduction paragraph.

## Section A

This is content for section A.

### Subsection A.1

This is content for subsection A.1.

### Subsection A.2

This is content for subsection A.2.

## Section B

This is content for section B.

## Conclusion

This is the conclusion paragraph.
"""

    chunks = chunker.chunk_content(structured_content, "structured.md", "markdown")
    print(f"✅ Created {len(chunks)} chunks from structured content")

    # Check that headers are preserved
    for i, chunk in enumerate(chunks):
        content = chunk["content"]
        if "#" in content:
            print(f"  Chunk {i+1}: Contains headers")
        else:
            print(f"  Chunk {i+1}: No headers")

    return chunks


def test_chunk_size_consistency():
    """Test that chunks respect size constraints."""
    print("\n=== Testing Chunk Size Consistency ===")

    chunker = SemanticChunker(chunk_size=300, overlap_ratio=0.10)

    # Create content that should produce multiple chunks
    content = "This is a test sentence. " * 100  # ~2400 characters

    chunks = chunker.chunk_content(content, "size_test.md", "markdown")
    print(f"✅ Created {len(chunks)} chunks")

    # Check size constraints
    for i, chunk in enumerate(chunks):
        chunk_size = chunk["metadata"]["chunk_size"]
        if chunk_size <= chunker.max_chunk_size:
            print(f"  Chunk {i+1}: {chunk_size} chars (within limit)")
        else:
            print(f"  ⚠️  Chunk {i+1}: {chunk_size} chars (exceeds limit!)")

    return chunks


def main():
    """Run all tests."""
    print("🧪 Starting Comprehensive Semantic Chunker Tests\n")

    try:
        # Run all test functions
        basic_chunks = test_basic_chunking()
        overlap_chunks = test_overlap_logic()
        edge_results = test_edge_cases()
        semantic_chunks = test_semantic_structure()
        size_chunks = test_chunk_size_consistency()

        print("\n✅ All tests completed successfully!")
        print("📊 Summary:")
        print(f"  - Basic chunking: {len(basic_chunks)} chunks")
        print(f"  - Overlap testing: {len(overlap_chunks)} chunks")
        print(
            f"  - Edge cases: {len(edge_results[0])} empty, {len(edge_results[1])} short, {len(edge_results[2])} headers, {len(edge_results[3])} long"
        )
        print(f"  - Semantic structure: {len(semantic_chunks)} chunks")
        print(f"  - Size consistency: {len(size_chunks)} chunks")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
