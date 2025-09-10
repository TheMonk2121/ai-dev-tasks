"""
Unit tests for File System MCP Server.
"""

import csv
import json
import tempfile
from pathlib import Path

import pytest

from src.utils.mcp_integration.base_server import MCPConfig, MCPError
from src.utils.mcp_integration.file_system_server import FileSystemMCPServer


class TestFileSystemMCPServer:
    """Test File System MCP Server."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return MCPConfig(server_name="test_file_system_server")

    @pytest.fixture
    def server(self, config):
        """Create test server."""
        return FileSystemMCPServer(config)

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_server_initialization(self, config):
        """Test server initialization."""
        server = FileSystemMCPServer(config)
        assert server.config == config
        assert server.config.server_name == "test_file_system_server"
        assert len(server.supported_extensions) > 0

    def test_supported_extensions(self, server):
        """Test supported extensions."""
        extensions = server.get_supported_extensions()
        assert ".txt" in extensions
        assert ".md" in extensions
        assert ".py" in extensions
        assert ".json" in extensions
        assert ".csv" in extensions

    def test_supported_content_types(self, server):
        """Test supported content types."""
        types = server.get_supported_types()
        assert "text/plain" in types
        assert "text/markdown" in types
        assert "text/python" in types
        assert "application/json" in types
        assert "text/csv" in types

    def test_supports_content_type(self, server):
        """Test content type support checking."""
        assert server.supports_content_type("text/plain") is True
        assert server.supports_content_type("text/markdown") is True
        assert server.supports_content_type("application/json") is True
        assert server.supports_content_type("unsupported/type") is False

    def test_validate_source(self, server):
        """Test source validation."""
        # Valid sources
        assert server.validate_source("/path/to/file.txt") is True
        assert server.validate_source("file.txt") is True

        # Invalid sources
        assert server.validate_source("") is False
        assert server.validate_source("   ") is False
        assert server.validate_source("/path/../file.txt") is False  # Path traversal

    @pytest.mark.asyncio
    async def test_process_text_file(self, server, temp_dir):
        """Test processing a text file."""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_content = "Hello, world!\nThis is a test file."
        test_file.write_text(test_content)

        # Process file
        result = await server.process_document(str(test_file))

        # Verify results
        assert result.success is True
        assert result.content == test_content
        assert result.metadata.source == str(test_file)
        assert result.metadata.content_type == "text/plain"
        assert result.metadata.size == len(test_content.encode("utf-8"))
        assert result.metadata.word_count == 7

    @pytest.mark.asyncio
    async def test_process_json_file(self, server, temp_dir):
        """Test processing a JSON file."""
        # Create test JSON file
        test_data = {
            "title": "Test Document",
            "author": "Test Author",
            "content": "This is test content",
            "tags": ["test", "json"],
        }
        test_file = temp_dir / "test.json"
        test_file.write_text(json.dumps(test_data))

        # Process file
        result = await server.process_document(str(test_file))

        # Verify results
        assert result.success is True
        assert result.metadata.content_type == "application/json"
        assert result.metadata.title == "Test Document"
        assert result.metadata.author == "Test Author"
        # Content should be pretty-printed
        assert '"title": "Test Document"' in result.content

    @pytest.mark.asyncio
    async def test_process_csv_file(self, server, temp_dir):
        """Test processing a CSV file."""
        # Create test CSV file
        test_file = temp_dir / "test.csv"
        csv_data = [
            ["Name", "Age", "City"],
            ["Alice", "25", "New York"],
            ["Bob", "30", "Los Angeles"],
            ["Charlie", "35", "Chicago"],
        ]

        with open(test_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)

        # Process file
        result = await server.process_document(str(test_file))

        # Verify results
        assert result.success is True
        assert result.metadata.content_type == "text/csv"
        assert "CSV with 3 columns, 3 rows" in result.metadata.title
        # Content should be formatted as table
        assert "Alice" in result.content
        assert "Bob" in result.content

    @pytest.mark.asyncio
    async def test_process_markdown_file(self, server, temp_dir):
        """Test processing a Markdown file."""
        # Create test Markdown file
        test_file = temp_dir / "test.md"
        test_content = """# Test Document

This is a test markdown file.

## Section 1

Some content here.

```python
print("Hello, world!")
```
"""
        test_file.write_text(test_content)

        # Process file
        result = await server.process_document(str(test_file))

        # Verify results
        assert result.success is True
        assert result.metadata.content_type == "text/markdown"
        assert result.metadata.title == "Test Document"
        assert result.metadata.language == "python"

    @pytest.mark.asyncio
    async def test_process_python_file(self, server, temp_dir):
        """Test processing a Python file."""
        # Create test Python file
        test_file = temp_dir / "test.py"
        test_content = '''"""
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
        test_file.write_text(test_content)

        # Process file
        result = await server.process_document(str(test_file))

        # Verify results
        assert result.success is True
        assert result.metadata.content_type == "text/python"
        assert result.metadata.title == "Test Python Module"
        assert result.metadata.language == "python"

    @pytest.mark.asyncio
    async def test_file_not_found(self, server):
        """Test processing non-existent file."""
        with pytest.raises(MCPError) as exc_info:
            await server.process_document("/nonexistent/file.txt")

        assert exc_info.value.error_code == "FILE_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_file_too_large(self, server, temp_dir):
        """Test processing file that exceeds size limit."""
        # Create a large file
        test_file = temp_dir / "large.txt"
        large_content = "x" * (server.config.max_file_size + 1000)
        test_file.write_text(large_content)

        with pytest.raises(MCPError) as exc_info:
            await server.process_document(str(test_file))

        assert exc_info.value.error_code == "FILE_TOO_LARGE"

    @pytest.mark.asyncio
    async def test_directory_as_source(self, server, temp_dir):
        """Test processing a directory instead of a file."""
        with pytest.raises(MCPError) as exc_info:
            await server.process_document(str(temp_dir))

        assert exc_info.value.error_code == "NOT_A_FILE"

    @pytest.mark.asyncio
    async def test_invalid_source(self, server):
        """Test processing invalid source."""
        with pytest.raises(MCPError) as exc_info:
            await server.process_document("")

        assert exc_info.value.error_code == "INVALID_SOURCE"

    @pytest.mark.asyncio
    async def test_encoding_detection(self, server, temp_dir):
        """Test encoding detection for different file encodings."""
        # Test UTF-8 file
        test_file = temp_dir / "utf8.txt"
        test_content = "Hello, 世界!"
        test_file.write_text(test_content, encoding="utf-8")

        result = await server.process_document(str(test_file))
        assert result.success is True
        assert result.content == test_content

    @pytest.mark.asyncio
    async def test_metadata_extraction(self, server, temp_dir):
        """Test metadata extraction."""
        test_file = temp_dir / "metadata_test.txt"
        test_content = "This is a test file for metadata extraction."
        test_file.write_text(test_content)

        result = await server.process_document(str(test_file))

        # Verify metadata
        metadata = result.metadata
        assert metadata.source == str(test_file)
        assert metadata.content_type == "text/plain"
        assert metadata.size > 0
        assert metadata.word_count == 8
        assert metadata.created_at is not None
        assert metadata.modified_at is not None
        assert metadata.encoding is not None

    def test_add_supported_extension(self, server):
        """Test adding supported extension."""
        initial_count = len(server.supported_extensions)

        server.add_supported_extension(".test", "text/test")

        assert len(server.supported_extensions) == initial_count + 1
        assert ".test" in server.supported_extensions
        assert server.supported_extensions[".test"] == "text/test"

    def test_remove_supported_extension(self, server):
        """Test removing supported extension."""
        # Add an extension first
        server.add_supported_extension(".test", "text/test")
        initial_count = len(server.supported_extensions)

        server.remove_supported_extension(".test")

        assert len(server.supported_extensions) == initial_count - 1
        assert ".test" not in server.supported_extensions

    @pytest.mark.asyncio
    async def test_cache_functionality(self, server, temp_dir):
        """Test caching functionality."""
        test_file = temp_dir / "cache_test.txt"
        test_content = "Cache test content"
        test_file.write_text(test_content)

        # First processing
        result1 = await server.process_document(str(test_file))
        assert result1.success is True

        # Second processing (should use cache)
        result2 = await server.process_document(str(test_file))
        assert result2.success is True

        # Results should be identical
        assert result1.content == result2.content
        assert result1.metadata.source == result2.metadata.source

    @pytest.mark.asyncio
    async def test_retry_functionality(self, server):
        """Test retry functionality."""
        # This would require mocking file operations to simulate failures
        # For now, just test that retry logic exists
        assert hasattr(server, "process_with_retry")
        assert server.config.retry_attempts > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, server):
        """Test error handling."""
        # Test with invalid file path
        with pytest.raises(MCPError):
            await server.process_document("/invalid/path/with/../traversal.txt")

    @pytest.mark.asyncio
    async def test_content_processing(self, server, temp_dir):
        """Test content processing for different types."""
        # Test JSON pretty printing
        test_json = {"key": "value", "nested": {"data": "test"}}
        json_file = temp_dir / "test.json"
        json_file.write_text(json.dumps(test_json, separators=(",", ":")))

        result = await server.process_document(str(json_file))
        assert '"key": "value"' in result.content
        assert '"nested": {' in result.content  # Pretty printed

    @pytest.mark.asyncio
    async def test_text_processing(self, server, temp_dir):
        """Test text processing."""
        # Create text with excessive blank lines
        test_file = temp_dir / "text_test.txt"
        test_content = "Line 1\n\n\n\nLine 2\n\nLine 3"
        test_file.write_text(test_content)

        result = await server.process_document(str(test_file))

        # Should remove excessive blank lines
        lines = result.content.split("\n")
        blank_line_count = sum(1 for line in lines if not line.strip())
        assert blank_line_count < 3  # Should have fewer blank lines
