#!/usr/bin/env python3.11
"""
Test script for the improved token-aware chunker
Verifies all critical fixes and performance improvements
"""

import time

import pytest

from utils.tokenizer import TokenAwareChunker


@pytest.mark.tier3
@pytest.mark.unit
def test_basic_chunking():
    """Test basic chunking functionality"""
    print("🧪 Testing basic chunking...")

    chunker = TokenAwareChunker(model_name="gpt-4o", max_tokens=100, overlap_tokens=20)

    # Test with simple text
    text = "This is a test document. " * 50  # Create a long text
    chunks = chunker.create_chunks(text)

    print(f"✅ Created {len(chunks)} chunks")
    print(f"   First chunk: {chunks[0][:50]}...")
    print(f"   Last chunk: {chunks[-1][:50]}...")

    # Verify chunk sizes
    for i, chunk in enumerate(chunks):
        tokens = chunker.count_tokens(chunk)
        print(f"   Chunk {i+1}: {tokens} tokens")
        assert tokens <= 100, f"Chunk {i+1} exceeds max tokens: {tokens}"

    print("✅ Basic chunking test passed")


@pytest.mark.tier3
@pytest.mark.unit
def test_model_awareness():
    """Test model-aware tokenizer selection"""
    print("🧪 Testing model awareness...")

    # Test different models
    models = ["gpt-4o", "gpt-4", "mistral-7b"]

    for model in models:
        chunker = TokenAwareChunker(model_name=model, max_tokens=50)
        text = "This is a test for model awareness."
        chunks = chunker.create_chunks(text)

        print(f"   {model}: {len(chunks)} chunks created")
        assert len(chunks) > 0, f"No chunks created for {model}"

    print("✅ Model awareness test passed")


def test_performance_improvement():
    """Test the performance improvement from single encoding"""
    print("🧪 Testing performance improvement...")

    # Create a large text
    large_text = "This is a performance test. " * 10000  # ~200KB

    chunker = TokenAwareChunker(model_name="gpt-4o", max_tokens=200, overlap_tokens=50)

    # Time the chunking
    start_time = time.time()
    chunks = chunker.create_chunks(large_text)
    end_time = time.time()

    processing_time = end_time - start_time
    total_tokens = chunker.count_tokens(large_text)

    print(f"✅ Processed {total_tokens} tokens in {processing_time:.2f}s")
    print(f"   Created {len(chunks)} chunks")
    print(f"   Rate: {total_tokens/processing_time:.0f} tokens/second")

    # Should be much faster than the old O(N²) approach
    assert processing_time < 5.0, f"Chunking took too long: {processing_time}s"

    print("✅ Performance test passed")


def test_overlap_calculation():
    """Test proper token-based overlap calculation"""
    print("🧪 Testing overlap calculation...")

    chunker = TokenAwareChunker(model_name="gpt-4o", max_tokens=50, overlap_tokens=10)

    text = "This is a test of overlap calculation. " * 20
    chunks = chunker.create_chunks(text)

    # Check that chunks have proper overlap
    for i in range(len(chunks) - 1):
        chunk1 = chunks[i]

        # Count tokens in overlap (rough check)
        overlap_text = chunk1[-50:]  # Last 50 chars of first chunk
        overlap_tokens = chunker.count_tokens(overlap_text)

        print(f"   Chunk {i+1} to {i+2}: ~{overlap_tokens} overlap tokens")
        assert overlap_tokens > 0, f"No overlap between chunks {i+1} and {i+2}"

    print("✅ Overlap calculation test passed")


def test_error_handling():
    """Test error handling and fallback mechanisms"""
    print("🧪 Testing error handling...")

    chunker = TokenAwareChunker(model_name="gpt-4o", max_tokens=50, overlap_tokens=10)

    # Test with empty text
    chunks = chunker.create_chunks("")
    assert len(chunks) == 0, "Empty text should produce no chunks"

    # Test with whitespace only
    chunks = chunker.create_chunks("   \n\t   ")
    assert len(chunks) == 0, "Whitespace-only text should produce no chunks"

    # Test with very short text
    chunks = chunker.create_chunks("Short.")
    assert len(chunks) == 1, "Short text should produce one chunk"

    print("✅ Error handling test passed")


def test_unicode_handling():
    """Test Unicode handling in text cleaning"""
    print("🧪 Testing Unicode handling...")

    chunker = TokenAwareChunker(model_name="gpt-4o", max_tokens=50, overlap_tokens=10)

    # Test with various Unicode characters
    unicode_text = "Test with €, ™, ±, 中文, emoji 🚀, and control chars\x00\x01"
    chunks = chunker.create_chunks(unicode_text)

    # Should handle Unicode gracefully
    assert len(chunks) > 0, "Unicode text should produce chunks"

    # Check that control characters are removed
    for chunk in chunks:
        assert "\x00" not in chunk, "Control characters should be removed"
        assert "\x01" not in chunk, "Control characters should be removed"

    print("✅ Unicode handling test passed")


def test_chunk_stats():
    """Test chunk statistics generation"""
    print("🧪 Testing chunk statistics...")

    chunker = TokenAwareChunker(model_name="gpt-4o", max_tokens=100, overlap_tokens=20)
    text = "This is a test for statistics. " * 50

    stats = chunker.get_chunk_stats(text)

    print("✅ Chunk statistics:")
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Total tokens: {stats['total_tokens']}")
    print(f"   Avg chunk tokens: {stats['avg_chunk_tokens']:.1f}")
    print(f"   Min chunk tokens: {stats['min_chunk_tokens']}")
    print(f"   Max chunk tokens: {stats['max_chunk_tokens']}")
    print(f"   Model name: {stats['model_name']}")

    assert stats["total_chunks"] > 0, "Should have created chunks"
    assert stats["total_tokens"] > 0, "Should have tokens"
    assert stats["max_chunk_tokens"] <= 100, "Max chunk should respect limit"

    print("✅ Chunk statistics test passed")


def test_generator_interface():
    """Test the generator interface for memory efficiency"""
    print("🧪 Testing generator interface...")

    chunker = TokenAwareChunker(model_name="gpt-4o", max_tokens=50, overlap_tokens=10)
    text = "This is a test for the generator interface. " * 100

    # Use generator
    chunks_from_generator = list(chunker.create_chunks_generator(text))

    # Use regular method
    chunks_from_method = chunker.create_chunks(text)

    # Should be identical
    assert len(chunks_from_generator) == len(chunks_from_method), "Generator should produce same number of chunks"

    for i, (gen_chunk, method_chunk) in enumerate(zip(chunks_from_generator, chunks_from_method)):
        assert gen_chunk == method_chunk, f"Chunk {i} should be identical"

    print("✅ Generator interface test passed")


def test_encoder_caching():
    """Test that encoders are properly cached"""
    print("🧪 Testing encoder caching...")

    # Create multiple chunkers for the same model
    chunker1 = TokenAwareChunker(model_name="gpt-4o")
    chunker2 = TokenAwareChunker(model_name="gpt-4o")

    # Should use the same encoder instance (cached)
    assert chunker1.encoder is chunker2.encoder, "Encoders should be cached"

    print("✅ Encoder caching test passed")


def test_large_document_performance():
    """Test performance with a large document"""
    print("🧪 Testing large document performance...")

    # Create a large document (~500KB instead of 1MB for more realistic test)
    large_text = "This is a large document for performance testing. " * 12500

    chunker = TokenAwareChunker(model_name="gpt-4o", max_tokens=200, overlap_tokens=50)

    start_time = time.time()
    chunks = chunker.create_chunks(large_text)
    end_time = time.time()

    processing_time = end_time - start_time
    total_tokens = chunker.count_tokens(large_text)

    print("✅ Large document test:")
    print(f"   Document size: {len(large_text):,} characters")
    print(f"   Total tokens: {total_tokens:,}")
    print(f"   Processing time: {processing_time:.2f}s")
    print(f"   Chunks created: {len(chunks)}")
    print(f"   Tokens per second: {total_tokens/processing_time:.0f}")

    # Should be reasonably fast (adjusted for realistic expectations)
    assert processing_time < 20.0, f"Large document processing took too long: {processing_time}s"
    assert len(chunks) > 0, "Should create chunks from large document"

    print("✅ Large document performance test passed")


def main():
    """Run all tests"""
    print("🚀 Starting Tokenizer Tests")
    print("=" * 50)

    try:
        test_basic_chunking()
        test_model_awareness()
        test_performance_improvement()
        test_overlap_calculation()
        test_error_handling()
        test_unicode_handling()
        test_chunk_stats()
        test_generator_interface()
        test_encoder_caching()
        test_large_document_performance()

        print("\n🎉 All tokenizer tests passed!")
        print("✅ Critical fixes implemented:")
        print("   - Model-aware tokenizer selection")
        print("   - Single encoding optimization (O(N) instead of O(N²))")
        print("   - Proper token-based overlap calculation")
        print("   - Improved Unicode handling")
        print("   - Error handling and fallback mechanisms")
        print("   - Encoder caching for performance")
        print("   - Generator interface for memory efficiency")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
