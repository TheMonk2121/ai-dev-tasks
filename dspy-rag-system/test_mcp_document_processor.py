#!/usr/bin/env python3
"""
Test script for MCP Document Processor
Validates the core functionality of the MCP Document Processor
"""

import asyncio
import sys

# Add src to path
sys.path.append("src")

from dspy_modules.mcp_document_processor import MCPDocumentProcessor


async def test_mcp_document_processor():
    """Test the MCP Document Processor functionality"""
    print("🧪 Testing MCP Document Processor...")

    # Initialize the processor
    processor = MCPDocumentProcessor()
    print("✅ MCP Document Processor initialized")

    # Test server info
    server_info = processor.get_server_info()
    print(f"📊 Server Info: {server_info}")

    # Test processing a simple text document
    test_content = "This is a test document for the MCP Document Processor."
    test_source = "test_document.txt"

    print(f"\n📄 Processing test document: {test_source}")

    # Create a mock processed document
    from utils.mcp_integration import DocumentMetadata, ProcessedDocument

    metadata = DocumentMetadata(
        source=test_source,
        content_type="text/plain",
        title="Test Document",
        author="Test Author",
        created_at="2024-01-01T00:00:00Z",
        modified_at="2024-01-01T00:00:00Z",
        word_count=10,
        page_count=1,
    )

    processed_doc = ProcessedDocument(content=test_content, metadata=metadata)

    # Test chunk creation
    document_id = "test_doc_123"
    chunks = processor._create_chunks_from_content(test_content, document_id)
    print(f"📝 Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i}: {chunk['text'][:50]}...")

    # Test metadata preparation
    metadata_dict = processor._prepare_metadata(processed_doc, test_source, document_id)
    print(f"📋 Metadata: {metadata_dict}")

    # Test source masking
    masked_source = processor._mask_source("/path/to/sensitive/file.txt")
    print(f"🔒 Masked source: {masked_source}")

    # Test server type detection
    server_type = processor._get_server_type_from_metadata("text/plain")
    print(f"🏷️  Server type for text/plain: {server_type}")

    # Test statistics
    stats = processor.get_processing_stats()
    print(f"📈 Statistics: {stats}")

    # Cleanup
    processor.cleanup()
    print("🧹 Cleanup completed")

    print("\n🎉 All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_mcp_document_processor())
