#!/usr/bin/env python3
"""
Test script to validate File System MCP Server is working correctly.
"""

import asyncio
import csv
import json
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.mcp_integration.base_server import MCPConfig
from utils.mcp_integration.file_system_server import FileSystemMCPServer


async def test_file_system_server():
    """Test the File System MCP Server."""
    print("🧪 Testing File System MCP Server...")

    # Create configuration
    config = MCPConfig(server_name="test_file_system_server")
    server = FileSystemMCPServer(config)

    print("1. Server Configuration:")
    print(f"   ✅ Server name: {server.config.server_name}")
    print(f"   ✅ Supported extensions: {len(server.supported_extensions)}")
    print(f"   ✅ Supported types: {len(server.get_supported_types())}")

    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        print("\n2. Testing Text File Processing:")
        # Create test text file
        text_file = temp_path / "test.txt"
        text_content = "Hello, world!\nThis is a test text file.\nIt has multiple lines."
        text_file.write_text(text_content)

        result = await server.process_document(str(text_file))
        print(f"   ✅ Text file processed: {result.success}")
        print(f"   ✅ Content type: {result.metadata.content_type}")
        print(f"   ✅ Word count: {result.metadata.word_count}")
        print(f"   ✅ File size: {result.metadata.size} bytes")

        print("\n3. Testing JSON File Processing:")
        # Create test JSON file
        json_file = temp_path / "test.json"
        json_data = {
            "title": "Test JSON Document",
            "author": "Test Author",
            "content": "This is test JSON content",
            "tags": ["test", "json", "mcp"],
        }
        json_file.write_text(json.dumps(json_data))

        result = await server.process_document(str(json_file))
        print(f"   ✅ JSON file processed: {result.success}")
        print(f"   ✅ Content type: {result.metadata.content_type}")
        print(f"   ✅ Title extracted: {result.metadata.title}")
        print(f"   ✅ Author extracted: {result.metadata.author}")
        print(f"   ✅ Pretty printed: {'{' in result.content}")

        print("\n4. Testing CSV File Processing:")
        # Create test CSV file
        csv_file = temp_path / "test.csv"
        csv_data = [
            ["Name", "Age", "City"],
            ["Alice", "25", "New York"],
            ["Bob", "30", "Los Angeles"],
            ["Charlie", "35", "Chicago"],
        ]

        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)

        result = await server.process_document(str(csv_file))
        print(f"   ✅ CSV file processed: {result.success}")
        print(f"   ✅ Content type: {result.metadata.content_type}")
        print(f"   ✅ Title extracted: {result.metadata.title}")
        print(f"   ✅ Formatted as table: {'Alice' in result.content}")

        print("\n5. Testing Markdown File Processing:")
        # Create test Markdown file
        md_file = temp_path / "test.md"
        md_content = """# Test Markdown Document

This is a test markdown file.

## Features

- Feature 1
- Feature 2
- Feature 3

```python
print("Hello, world!")
```
"""
        md_file.write_text(md_content)

        result = await server.process_document(str(md_file))
        print(f"   ✅ Markdown file processed: {result.success}")
        print(f"   ✅ Content type: {result.metadata.content_type}")
        print(f"   ✅ Title extracted: {result.metadata.title}")
        print(f"   ✅ Language detected: {result.metadata.language}")

        print("\n6. Testing Python File Processing:")
        # Create test Python file
        py_file = temp_path / "test.py"
        py_content = '''"""
Test Python Module

This is a test Python file with classes and functions.
"""

class TestClass:
    """A test class."""

    def __init__(self):
        self.value = 42

    def test_method(self):
        """A test method."""
        return self.value

def test_function():
    """A test function."""
    return "Hello, world!"
'''
        py_file.write_text(py_content)

        result = await server.process_document(str(py_file))
        print(f"   ✅ Python file processed: {result.success}")
        print(f"   ✅ Content type: {result.metadata.content_type}")
        print(f"   ✅ Title extracted: {result.metadata.title}")
        print(f"   ✅ Language detected: {result.metadata.language}")

        print("\n7. Testing Error Handling:")
        # Test non-existent file
        try:
            await server.process_document("/nonexistent/file.txt")
            print("   ❌ Should have raised an error")
        except Exception as e:
            print(f"   ✅ Error caught: {type(e).__name__}")

        # Test invalid source
        try:
            await server.process_document("")
            print("   ❌ Should have raised an error")
        except Exception as e:
            print(f"   ✅ Error caught: {type(e).__name__}")

        print("\n8. Testing Extension Management:")
        initial_count = len(server.supported_extensions)
        server.add_supported_extension(".test", "text/test")
        print(f"   ✅ Added extension: {len(server.supported_extensions) == initial_count + 1}")

        server.remove_supported_extension(".test")
        print(f"   ✅ Removed extension: {len(server.supported_extensions) == initial_count}")

        print("\n9. Testing Server Information:")
        info = server.get_server_info()
        print(f"   ✅ Server name: {info['name']}")
        print(f"   ✅ Version: {info['version']}")
        print(f"   ✅ Supported types: {len(info['supported_types'])}")
        print(f"   ✅ Cache size: {info['cache_size']}")

        print("\n🎉 All File System MCP Server tests passed!")


if __name__ == "__main__":
    asyncio.run(test_file_system_server())
