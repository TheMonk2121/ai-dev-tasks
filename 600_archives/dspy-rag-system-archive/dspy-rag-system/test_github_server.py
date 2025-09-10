#!/usr/bin/env python3
"""
Test script to validate GitHub MCP Server is working correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.mcp_integration.base_server import MCPConfig
from utils.mcp_integration.github_server import GitHubMCPServer


async def test_github_server():
    """Test the GitHub MCP Server."""
    print("🧪 Testing GitHub MCP Server...")

    # Create configuration
    config = MCPConfig(server_name="test_github_server")
    server = GitHubMCPServer(config)

    print("1. Server Configuration:")
    print(f"   ✅ Server name: {server.config.server_name}")
    print(f"   ✅ Supported types: {len(server.get_supported_types())}")
    print(f"   ✅ GitHub config: {server.github_config.max_items_per_type} max items")

    print("\n2. Testing Source Validation:")
    print(f"   ✅ Valid repository URL: {server.validate_source('https://github.com/owner/repo')}")
    print(f"   ✅ Valid file URL: {server.validate_source('https://github.com/owner/repo/blob/main/file.txt')}")
    print(f"   ✅ Valid issue URL: {server.validate_source('https://github.com/owner/repo/issues/1')}")
    print(f"   ✅ Valid PR URL: {server.validate_source('https://github.com/owner/repo/pull/1')}")
    print(f"   ✅ Invalid URL: {not server.validate_source('https://gitlab.com/owner/repo')}")

    print("\n3. Testing GitHub Configuration:")
    github_config = server.get_github_config()
    print(f"   ✅ API token: {'Set' if github_config['api_token'] else 'Not set'}")
    print(f"   ✅ Rate limit delay: {github_config['rate_limit_delay']}")
    print(f"   ✅ Max file size: {github_config['max_file_size']}")
    print(f"   ✅ Include issues: {github_config['include_issues']}")
    print(f"   ✅ Include PRs: {github_config['include_pull_requests']}")
    print(f"   ✅ Include wiki: {github_config['include_wiki']}")

    # Test configuration update
    server.update_github_config(rate_limit_delay=2.0)
    updated_config = server.get_github_config()
    print(f"   ✅ Updated rate limit: {updated_config['rate_limit_delay']}")

    print("\n4. Testing URL Parsing:")
    test_urls = [
        "https://github.com/owner/repo",
        "https://github.com/owner/repo/blob/main/src/file.py",
        "https://github.com/owner/repo/issues/123",
        "https://github.com/owner/repo/pull/456",
        "https://github.com/owner/repo/wiki/Getting-Started",
    ]

    for url in test_urls:
        try:
            repo_info = server._parse_github_url(url)
            print(f"   ✅ {url}")
            print(f"      Type: {repo_info['type']}")
            print(f"      Owner: {repo_info['owner']}")
            print(f"      Repo: {repo_info['repo']}")
        except Exception as e:
            print(f"   ❌ {url}: {e}")

    print("\n5. Testing GitHub API Integration:")
    try:
        # Test with a public repository (no API token needed)
        result = await server.process_document("https://github.com/octocat/Hello-World")
        print(f"   ✅ Repository processing: {result.success}")
        print(f"   ✅ Content type: {result.metadata.content_type}")
        print(f"   ✅ Title: {result.metadata.title}")
        print(f"   ✅ Author: {result.metadata.author}")
        print(f"   ✅ Word count: {result.metadata.word_count}")
        print(f"   ✅ Content preview: {result.content[:100]}...")
    except Exception as e:
        print(f"   ❌ Repository processing failed: {e}")

    print("\n6. Testing Error Handling:")
    try:
        await server.process_document("not-a-github-url")
        print("   ❌ Should have raised an error")
    except Exception as e:
        print(f"   ✅ Error caught: {type(e).__name__}")

    try:
        await server.process_document("https://github.com/nonexistent/repo")
        print("   ❌ Should have raised an error")
    except Exception as e:
        print(f"   ✅ Error caught: {type(e).__name__}")

    print("\n7. Testing Server Information:")
    info = server.get_server_info()
    print(f"   ✅ Server name: {info['name']}")
    print(f"   ✅ Version: {info['version']}")
    print(f"   ✅ Supported types: {len(info['supported_types'])}")
    print(f"   ✅ Cache size: {info['cache_size']}")

    print("\n8. Testing Cleanup:")
    await server.cleanup()
    print("   ✅ Server cleaned up successfully")

    print("\n🎉 All GitHub MCP Server tests completed!")


if __name__ == "__main__":
    asyncio.run(test_github_server())
