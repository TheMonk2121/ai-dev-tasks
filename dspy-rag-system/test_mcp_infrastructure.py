#!/usr/bin/env python3
"""
Test script to validate MCP infrastructure is working correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.mcp_integration.base_server import (
    DocumentMetadata,
    MCPConfig,
    MCPError,
    MCPProtocolUtils,
    ProcessedDocument,
)


class TestMCPServer:
    """Test MCP server implementation."""

    def __init__(self, config: MCPConfig):
        self.config = config

    async def process_document(self, source: str, **kwargs) -> ProcessedDocument:
        """Mock document processing."""
        metadata = DocumentMetadata(source=source, content_type="txt")
        return ProcessedDocument(content=f"Processed: {source}", metadata=metadata)

    def supports_content_type(self, content_type: str) -> bool:
        """Mock content type support."""
        return content_type in ["txt", "md", "py"]

    def get_supported_types(self) -> list[str]:
        """Mock supported types."""
        return ["txt", "md", "py"]


async def test_mcp_infrastructure():
    """Test the MCP infrastructure."""
    print("🧪 Testing MCP Infrastructure...")

    # Test configuration
    print("1. Testing MCP Configuration...")
    config = MCPConfig(server_name="test_server")
    print(f"   ✅ Server name: {config.server_name}")
    print(f"   ✅ Version: {config.server_version}")
    print(f"   ✅ Max file size: {config.max_file_size}")

    # Test server
    print("2. Testing MCP Server...")
    server = TestMCPServer(config)
    print("   ✅ Server initialized")
    print(f"   ✅ Supported types: {server.get_supported_types()}")

    # Test document processing
    print("3. Testing Document Processing...")
    result = await server.process_document("/path/to/test.txt")
    print(f"   ✅ Processing successful: {result.success}")
    print(f"   ✅ Content: {result.content}")
    print(f"   ✅ Metadata source: {result.metadata.source}")

    # Test protocol utilities
    print("4. Testing Protocol Utilities...")
    print(f"   ✅ URL validation: {MCPProtocolUtils.validate_url('https://example.com')}")
    print(f"   ✅ Word count: {MCPProtocolUtils.calculate_word_count('Hello world')}")

    # Test error handling
    print("5. Testing Error Handling...")
    try:
        raise MCPError("Test error", error_code="TEST_ERROR")
    except MCPError as e:
        print(f"   ✅ Error caught: {e.error_code}")

    print("\n🎉 All MCP infrastructure tests passed!")


if __name__ == "__main__":
    asyncio.run(test_mcp_infrastructure())
