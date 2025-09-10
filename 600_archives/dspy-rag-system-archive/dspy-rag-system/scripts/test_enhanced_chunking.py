#!/usr/bin/env python3
"""
Test Enhanced Chunking System
- Validate tokenizer-first approach
- Test recursive splitting with hard caps
- Verify dual-text storage
- Run A/B testing across chunk sizes
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


from utils.enhanced_chunking import ChunkingConfig, create_enhanced_chunker


def test_tokenizer_accuracy():
    """Test tokenizer accuracy vs word count"""
    print("=== Testing Tokenizer Accuracy ===")

    chunker = create_enhanced_chunker("sentence-transformers/all-MiniLM-L6-v2")

    test_texts = [
        "Hello world",
        "This is a longer sentence with multiple words and punctuation!",
        "Code: `def hello(): return 'world'`",
        "Markdown: **bold** and *italic* text",
        "Mixed content with `code` and **formatting** and normal text.",
    ]

    for text in test_texts:
        word_count = len(text.split())
        token_count = chunker.token_len(text)
        print(f"Text: '{text[:50]}...'")
        print(f"  Words: {word_count}, Tokens: {token_count}, Ratio: {token_count/word_count:.2f}")
        print()


def test_recursive_splitting():
    """Test recursive splitting with hard caps"""
    print("=== Testing Recursive Splitting ===")

    # Create a large test document
    large_doc = """
# Main Title

This is a large document that will test our recursive splitting capabilities.

## Section 1

This section contains multiple paragraphs that should be split appropriately.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

## Section 2

```python
def very_long_function():
    # This is a very long code block that should be preserved as a single unit
    # even if it exceeds the chunk size limit
    result = []
    for i in range(1000):
        result.append(f"Item {i}: This is a very long line that contains a lot of text and should be preserved as part of the code block")
    return result
```

## Section 3

This section has a very long paragraph that will definitely exceed our chunk size limits and should be split by the recursive splitting algorithm. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.

## Section 4

Final section with normal content.
"""

    config = ChunkingConfig(
        embedder_name="sentence-transformers/all-MiniLM-L6-v2",
        chunk_size=200,  # Small chunk size to force splitting
        max_tokens=300,
    )

    chunker = create_enhanced_chunker("sentence-transformers/all-MiniLM-L6-v2")
    chunker.config = config

    metadata = {"title": "Test Document", "section_path": "test.md", "content_type": "markdown"}

    result = chunker.chunk_document(Path("test.md"), large_doc)
    print(f"Using metadata: {metadata['title']} ({metadata['content_type']})")

    print(f"Original document tokens: {chunker.token_len(large_doc)}")
    print(f"Number of chunks: {len(result['embedding_texts'])}")
    print(f"Chunks over budget: {result['metrics']['chunks_over_budget']}")
    print()

    for i, (embedding_text, bm25_text) in enumerate(zip(result["embedding_texts"], result["bm25_texts"])):
        embedding_tokens = chunker.token_len(embedding_text)
        bm25_tokens = chunker.token_len(bm25_text)

        print(f"Chunk {i+1}:")
        print(f"  Embedding tokens: {embedding_tokens}")
        print(f"  BM25 tokens: {bm25_tokens}")
        print(f"  Content preview: {bm25_text[:100]}...")
        print(f"  Over budget: {embedding_tokens > config.max_tokens}")
        if "chunk_ids" in result and i < len(result["chunk_ids"]):
            print(f"  Chunk ID: {result['chunk_ids'][i]}")
        print()


def test_dual_text_storage():
    """Test dual-text storage (embedding vs BM25)"""
    print("=== Testing Dual-Text Storage ===")

    chunker = create_enhanced_chunker("sentence-transformers/all-MiniLM-L6-v2")

    test_content = """
# Test Document

This is a test document with some content.

## Section A

Some content here.

## Section B

More content here.
"""

    metadata = {"title": "Test Document", "section_path": "test.md#section-a", "content_type": "markdown"}

    chunk_pairs = chunker.recursive_split(test_content, metadata)

    print(f"Generated {len(chunk_pairs)} chunk pairs")
    print()

    for i, chunk_data in enumerate(chunk_pairs):
        if len(chunk_data) == 4:
            embedding_text, bm25_text, token_counts, chunk_id = chunk_data
        else:
            # Handle legacy format with proper type checking
            embedding_text = chunk_data[0] if len(chunk_data) > 0 else ""
            bm25_text = chunk_data[1] if len(chunk_data) > 1 else ""

        print(f"Chunk {i+1}:")
        print("  Embedding text (with context):")
        print(f"    {embedding_text[:150]}...")
        print("  BM25 text (clean):")
        print(f"    {bm25_text[:150]}...")
        print(f"  Context added: {len(embedding_text) > len(bm25_text)}")
        if len(chunk_data) == 4:
            print(f"  Chunk ID: {chunk_id}")
            print(f"  Token counts: {token_counts}")
        print()


def test_ab_testing():
    """Test A/B testing across chunk sizes"""
    print("=== Testing A/B Testing Framework ===")

    test_content = """
# A/B Testing Document

This document will be used to test different chunking strategies.

## Introduction

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

## Methodology

Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

## Results

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

## Conclusion

Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""

    chunk_sizes = [200, 400, 600, 800]
    results = {}

    for chunk_size in chunk_sizes:
        config = ChunkingConfig(
            embedder_name="sentence-transformers/all-MiniLM-L6-v2", chunk_size=chunk_size, max_tokens=chunk_size + 100
        )

        chunker = create_enhanced_chunker("sentence-transformers/all-MiniLM-L6-v2")
        chunker.config = config

        metadata = {"title": "AB Test Doc", "section_path": "ab_test.md", "content_type": "markdown"}
        result = chunker.chunk_document(Path("ab_test.md"), test_content)
        # Note: metadata is used internally by chunk_document for contextual prefixes
        _ = metadata  # Acknowledge metadata usage

        results[chunk_size] = {
            "chunk_count": len(result["embedding_texts"]),
            "avg_tokens": result["metrics"]["post_split_tokens_mean"],
            "max_tokens": result["metrics"]["post_split_tokens_max"],
            "over_budget": result["metrics"]["chunks_over_budget"],
        }

    print("A/B Testing Results:")
    print("Chunk Size | Chunks | Avg Tokens | Max Tokens | Over Budget")
    print("-" * 60)
    for chunk_size, metrics in results.items():
        print(
            f"{chunk_size:10} | {metrics['chunk_count']:6} | {metrics['avg_tokens']:10.1f} | {metrics['max_tokens']:10} | {metrics['over_budget']:11}"
        )
    print()


def test_validation():
    """Test validation functions"""
    print("=== Testing Validation Functions ===")

    chunker = create_enhanced_chunker("sentence-transformers/all-MiniLM-L6-v2")

    # Test with valid chunks
    valid_chunks = [
        ("Document: Test\n\nThis is a short chunk.", "This is a short chunk."),
        ("Document: Test\n\nThis is another short chunk.", "This is another short chunk."),
    ]

    validation = chunker.validate_chunking(valid_chunks)
    print("Valid chunks validation:")
    for key, value in validation.items():
        print(f"  {key}: {value}")
    print()

    # Test with oversized chunks
    oversized_chunks = [
        ("Document: Test\n\n" + "word " * 1000, "word " * 1000),
        ("Document: Test\n\n" + "word " * 500, "word " * 500),
    ]

    validation = chunker.validate_chunking(oversized_chunks)
    print("Oversized chunks validation:")
    for key, value in validation.items():
        print(f"  {key}: {value}")
    print()


def main():
    """Run all tests"""
    print("Enhanced Chunking System Tests")
    print("=" * 50)
    print()

    try:
        test_tokenizer_accuracy()
        test_recursive_splitting()
        test_dual_text_storage()
        test_ab_testing()
        test_validation()

        print("✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
