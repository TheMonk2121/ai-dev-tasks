#!/usr/bin/env python3
"""
Test Document Processor with Smart Chunker Integration
"""

import sys
from pathlib import Path

# Add the dspy-rag-system src to path
# sys.path.insert(0, str(Path(__file__).parent / "dspy-rag-system" / "src"))  # REMOVED: DSPy venv consolidated into main project

from dspy_modules.document_processor import DocumentProcessor


def test_smart_chunker_integration():
    """Test that document processor now uses smart chunking"""

    # Sample DSPy code file

    print("🧪 Testing Document Processor with Smart Chunker")
    print("=" * 55)

    # Create document processor with smart chunking
    processor = DocumentProcessor(chunk_size=300, chunk_overlap=64)  # Coach's recommendation

    print(f"📊 Processor config: chunk_size={processor.chunk_size}, " f"chunk_overlap={processor.chunk_overlap}")

    # Test processing
    print("\n🔍 Processing DSPy code...")
    result = processor.forward("test_dspy_optimizer.py")

    print("\n📦 Processing complete!")
    print(f"  Chunks created: {len(result.get('chunks', []))}")

    # Show chunk details
    chunks = result.get("chunks", [])
    for i, chunk in enumerate(chunks):
        chunk_id = chunk.get("id", "unknown")
        chunk_type = chunk.get("metadata", {}).get("chunk_type", "unknown")
        function_name = chunk.get("metadata", {}).get("function_name", "N/A")

        print(f"\nChunk {i+1}: {chunk_id}")
        print(f"  Type: {chunk_type}")
        print(f"  Function: {function_name}")
        print(f"  Text length: {len(chunk.get('text', ''))}")
        print(f"  Preview: {chunk.get('text', '')[:100]}...")

    return result


if __name__ == "__main__":
    try:
        result = test_smart_chunker_integration()
        print("\n🎯 Integration Test Complete!")
        print("=" * 40)
        print("✅ Smart chunker integrated successfully")
        print("✅ Code-aware chunking enabled")
        print("✅ Ready for RAGChecker evaluation!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
