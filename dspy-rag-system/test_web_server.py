#!/usr/bin/env python3
"""
Test script to validate Web MCP Server is working correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.mcp_integration.base_server import MCPConfig
from utils.mcp_integration.web_server import WebMCPServer


async def test_web_server():
    """Test the Web MCP Server."""
    print("🧪 Testing Web MCP Server...")

    # Create configuration
    config = MCPConfig(server_name="test_web_server")
    server = WebMCPServer(config)

    print("1. Server Configuration:")
    print(f"   ✅ Server name: {server.config.server_name}")
    print(f"   ✅ Supported types: {len(server.get_supported_types())}")
    print(f"   ✅ Web config: {server.web_config.user_agent}")

    print("\n2. Testing URL Validation:")
    print(f"   ✅ Valid URL: {server.validate_source('https://example.com')}")
    print(f"   ✅ Invalid URL: {not server.validate_source('not-a-url')}")

    print("\n3. Testing HTML Content Processing:")
    try:
        # Test with a simple HTML page
        result = await server.process_document("https://httpbin.org/html")
        print(f"   ✅ HTML processing: {result.success}")
        print(f"   ✅ Content type: {result.metadata.content_type}")
        print(f"   ✅ Title: {result.metadata.title}")
        print(f"   ✅ Word count: {result.metadata.word_count}")
        print(f"   ✅ Content preview: {result.content[:100]}...")
    except Exception as e:
        print(f"   ❌ HTML processing failed: {e}")

    print("\n4. Testing JSON API Processing:")
    try:
        # Test with a JSON API endpoint
        result = await server.process_document("https://httpbin.org/json")
        print(f"   ✅ JSON processing: {result.success}")
        print(f"   ✅ Content type: {result.metadata.content_type}")
        print(f"   ✅ Title: {result.metadata.title}")
        print(f"   ✅ Author: {result.metadata.author}")
        print(f"   ✅ Content preview: {result.content[:100]}...")
    except Exception as e:
        print(f"   ❌ JSON processing failed: {e}")

    print("\n5. Testing RSS Feed Processing:")
    try:
        # Test with a simple RSS feed (using a test feed)
        result = await server.process_document("https://feeds.feedburner.com/TechCrunch")
        print(f"   ✅ RSS processing: {result.success}")
        print(f"   ✅ Content type: {result.metadata.content_type}")
        print(f"   ✅ Title: {result.metadata.title}")
        print(f"   ✅ Language: {result.metadata.language}")
        print(f"   ✅ Content preview: {result.content[:100]}...")
    except Exception as e:
        print(f"   ❌ RSS processing failed: {e}")

    print("\n6. Testing Error Handling:")
    try:
        await server.process_document("https://httpbin.org/status/404")
        print("   ❌ Should have raised an error")
    except Exception as e:
        print(f"   ✅ Error caught: {type(e).__name__}")

    try:
        await server.process_document("not-a-url")
        print("   ❌ Should have raised an error")
    except Exception as e:
        print(f"   ✅ Error caught: {type(e).__name__}")

    print("\n7. Testing Configuration Management:")
    web_config = server.get_web_config()
    print(f"   ✅ User agent: {web_config['user_agent']}")
    print(f"   ✅ Rate limit delay: {web_config['rate_limit_delay']}")
    print(f"   ✅ Content size limit: {web_config['content_size_limit']}")

    # Test configuration update
    server.update_web_config(rate_limit_delay=2.0)
    updated_config = server.get_web_config()
    print(f"   ✅ Updated rate limit: {updated_config['rate_limit_delay']}")

    print("\n8. Testing Server Information:")
    info = server.get_server_info()
    print(f"   ✅ Server name: {info['name']}")
    print(f"   ✅ Version: {info['version']}")
    print(f"   ✅ Supported types: {len(info['supported_types'])}")
    print(f"   ✅ Cache size: {info['cache_size']}")

    print("\n9. Testing Cleanup:")
    await server.cleanup()
    print("   ✅ Server cleaned up successfully")

    print("\n🎉 All Web MCP Server tests completed!")


if __name__ == "__main__":
    asyncio.run(test_web_server())
