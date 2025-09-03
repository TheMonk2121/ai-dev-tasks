#!/usr/bin/env python3
"""
Test script for Smart Code-Aware Chunker
Demonstrates the impact on DSPy Implementation queries
"""

import sys
from pathlib import Path

# Add the dspy-rag-system src to path
sys.path.insert(0, str(Path(__file__).parent / "dspy-rag-system" / "src"))

from utils.smart_chunker import create_smart_chunker


def test_code_aware_chunking():
    """Test the smart chunker with DSPy code examples"""

    # Sample DSPy code that would cause chunking issues
    dspy_code = '''
class DSPyModule:
    """A DSPy module for testing chunking"""

    def __init__(self, name: str):
        self.name = name
        self.optimizer = None

    def forward(self, input_data):
        """Forward pass through the module"""
        # This is a complex function that should stay together
        processed = self._preprocess(input_data)
        result = self._core_computation(processed)
        return self._postprocess(result)

    def _preprocess(self, data):
        """Preprocess the input data"""
        return data.reshape(-1, 1)

    def _core_computation(self, data):
        """Core computation logic"""
        # This should stay with the function
        return data * 2 + 1

    def _postprocess(self, data):
        """Postprocess the output"""
        return data.clip(0, 100)

def create_pipeline():
    """Create a DSPy pipeline"""
    # This function should stay intact
    module1 = DSPyModule("input")
    module2 = DSPyModule("hidden")
    module3 = DSPyModule("output")

    return [module1, module2, module3]

# Usage example
if __name__ == "__main__":
    pipeline = create_pipeline()
    print("Pipeline created successfully")
'''

    print("🧪 Testing Smart Code-Aware Chunker")
    print("=" * 50)

    # Create smart chunker with coach's recommended settings
    smart_chunker = create_smart_chunker(
        max_tokens=300, overlap_tokens=64, preserve_code_units=True, enable_stitching=True  # Coach's recommendation
    )

    print(
        f"📊 Chunker config: max_tokens={smart_chunker.max_tokens}, " f"overlap_tokens={smart_chunker.overlap_tokens}"
    )

    # Test with the DSPy code
    print("\n🔍 Creating smart chunks...")
    chunks = smart_chunker.create_smart_chunks(dspy_code, "test_dspy.py")

    print(f"\n📦 Generated {len(chunks)} chunks:")
    print("-" * 30)

    for i, chunk in enumerate(chunks):
        chunk_type = chunk.get("chunk_type", "unknown")
        function_name = chunk.get("function_name", "N/A")
        is_complete = chunk.get("metadata", {}).get("is_complete_function", False)
        stitching_key = chunk.get("metadata", {}).get("stitching_key", "N/A")

        print(f"Chunk {i+1}:")
        print(f"  Type: {chunk_type}")
        print(f"  Function: {function_name}")
        print(f"  Complete: {is_complete}")
        print(f"  Stitching Key: {stitching_key}")
        print(f"  Tokens: ~{len(chunk['text'].split())}")
        print(f"  Preview: {chunk['text'][:100]}...")
        print()

    # Test stitching
    print("🔗 Testing chunk stitching...")
    stitched_chunks = smart_chunker.stitch_adjacent_chunks(chunks)

    print("📊 Stitching results:")
    print(f"  Original chunks: {len(chunks)}")
    print(f"  Stitched chunks: {len(stitched_chunks)}")
    print(f"  Reduction: {len(chunks) - len(stitched_chunks)} chunks")

    # Show what got stitched
    for chunk in stitched_chunks:
        if chunk.get("metadata", {}).get("stitched"):
            print(f"  ✅ Stitched: {chunk['id']}")
            print(f"     Original chunks: {chunk['metadata']['original_chunks']}")

    return chunks, stitched_chunks


def test_markdown_chunking():
    """Test markdown chunking with DSPy documentation"""

    markdown_doc = """
# DSPy Implementation Guide

## Overview
DSPy is a framework for optimizing LLM prompts and pipelines.

## Basic Usage

### Creating Modules
To create a DSPy module, inherit from the base class:

```python
from dspy import Module

class MyModule(Module):
    def forward(self, input_data):
        return processed_data
```

### Training the Module
Training involves optimizing the prompts:

```python
module = MyModule()
optimizer = LabeledFewShot()
optimizer.compile(module, trainset)
```

## Advanced Features

### Custom Optimizers
You can create custom optimizers:

```python
class CustomOptimizer:
    def compile(self, module, trainset):
        # Custom optimization logic
        pass
```

### Pipeline Composition
Build complex pipelines:

```python
pipeline = MyModule() >> AnotherModule() >> OutputModule()
```
"""

    print("\n📝 Testing Markdown Chunking")
    print("=" * 40)

    smart_chunker = create_smart_chunker(max_tokens=300, overlap_tokens=64)
    chunks = smart_chunker.create_smart_chunks(markdown_doc, "dspy_guide.md")

    print(f"📦 Generated {len(chunks)} markdown chunks:")
    for i, chunk in enumerate(chunks):
        heading = chunk.get("heading", "No heading")
        is_complete = chunk.get("metadata", {}).get("is_complete_section", False)
        print(f"  Chunk {i+1}: {heading} (Complete: {is_complete})")


if __name__ == "__main__":
    try:
        # Test code chunking
        code_chunks, stitched_chunks = test_code_aware_chunking()

        # Test markdown chunking
        test_markdown_chunking()

        print("\n🎯 Smart Chunker Test Complete!")
        print("=" * 50)
        print("Expected improvements for DSPy Implementation queries:")
        print("✅ Function boundaries preserved")
        print("✅ Docstrings stay with functions")
        print("✅ Related code chunks can be stitched")
        print("✅ Markdown sections stay intact")
        print("\n🚀 Ready to test with RAGChecker evaluation!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
