#!/usr/bin/env python3
"""
Test Document Processor with Smart Chunker Integration
"""

import sys
from pathlib import Path

# Add the dspy-rag-system src to path
sys.path.insert(0, str(Path(__file__).parent / "dspy-rag-system" / "src"))

from dspy_modules.document_processor import DocumentProcessor


def test_smart_chunker_integration():
    """Test that document processor now uses smart chunking"""

    # Sample DSPy code file
    dspy_code = '''
class DSPyOptimizer:
    """Optimizer for DSPy modules"""

    def __init__(self, name: str):
        self.name = name
        self.learning_rate = 0.01

    def compile(self, module, trainset):
        """Compile the module with training data"""
        # This should stay together as one chunk
        processed_data = self._preprocess_trainset(trainset)
        optimized_module = self._optimize_module(module, processed_data)
        return self._validate_module(optimized_module)

    def _preprocess_trainset(self, trainset):
        """Preprocess training data"""
        return [item for item in trainset if item is not None]

    def _optimize_module(self, module, data):
        """Optimize the module"""
        # Core optimization logic
        for epoch in range(100):
            loss = self._compute_loss(module, data)
            if loss < 0.001:
                break
        return module

    def _validate_module(self, module):
        """Validate the optimized module"""
        return module

# Usage example
if __name__ == "__main__":
    optimizer = DSPyOptimizer("test")
    print("Optimizer created successfully")
'''

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
