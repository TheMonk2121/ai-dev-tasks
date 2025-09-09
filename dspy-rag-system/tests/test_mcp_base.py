"""
Unit tests for base MCP server infrastructure.
"""

import tempfile


import pytest
from pydantic import ValidationError

from src.utils.mcp_integration.base_server import (
    DocumentMetadata,
    MCPConfig,
    MCPError,
    MCPProtocolUtils,
    MCPServer,
    ProcessedDocument,
)


class TestMCPConfig:
    """Test MCP configuration."""

    def test_valid_config(self):
        """Test creating valid MCP configuration."""
        config = MCPConfig(server_name="test_server")
        assert config.server_name == "test_server"
        assert config.server_version == "1.0.0"
        assert config.max_file_size == 10 * 1024 * 1024
        assert config.timeout == 30
        assert config.retry_attempts == 3
        assert config.enable_logging is True
        assert config.cache_enabled is True

    def test_invalid_config(self):
        """Test creating invalid MCP configuration."""
        with pytest.raises(ValidationError):
            MCPConfig()  # type: ignore[call-arg] # Missing required server_name

    def test_custom_config(self):
        """Test creating custom MCP configuration."""
        config = MCPConfig(
            server_name="custom_server",
            server_version="2.0.0",
            max_file_size=5 * 1024 * 1024,
            timeout=60,
            retry_attempts=5,
            enable_logging=False,
            cache_enabled=False,
        )
        assert config.server_name == "custom_server"
        assert config.server_version == "2.0.0"
        assert config.max_file_size == 5 * 1024 * 1024
        assert config.timeout == 60
        assert config.retry_attempts == 5
        assert config.enable_logging is False
        assert config.cache_enabled is False


class TestDocumentMetadata:
    """Test document metadata."""

    def test_basic_metadata(self):
        """Test creating basic document metadata."""
        metadata = DocumentMetadata(source="/path/to/file.txt", content_type="txt")
        assert metadata.source == "/path/to/file.txt"
        assert metadata.content_type == "txt"
        assert metadata.size == 0
        assert metadata.encoding == "utf-8"

    def test_full_metadata(self):
        """Test creating full document metadata."""
        metadata = DocumentMetadata(
            source="/path/to/file.pdf",
            content_type="pdf",
            size=1024,
            encoding="utf-8",
            created_at="2024-01-01T00:00:00Z",
            modified_at="2024-01-02T00:00:00Z",
            author="Test Author",
            title="Test Document",
            language="en",
            page_count=10,
            word_count=1000,
            processing_time=1.5,
            error_count=0,
        )
        assert metadata.source == "/path/to/file.pdf"
        assert metadata.content_type == "pdf"
        assert metadata.size == 1024
        assert metadata.author == "Test Author"
        assert metadata.title == "Test Document"
        assert metadata.page_count == 10
        assert metadata.word_count == 1000
        assert metadata.processing_time == 1.5

    def test_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = DocumentMetadata(source="/path/to/file.txt", content_type="txt", size=512, author="Test Author")
        metadata_dict = metadata.to_dict()
        assert metadata_dict["source"] == "/path/to/file.txt"
        assert metadata_dict["content_type"] == "txt"
        assert metadata_dict["size"] == 512
        assert metadata_dict["author"] == "Test Author"


class TestProcessedDocument:
    """Test processed document."""

    def test_successful_document(self):
        """Test creating successful processed document."""
        metadata = DocumentMetadata(source="/path/to/file.txt", content_type="txt")
        doc = ProcessedDocument(content="This is test content", metadata=metadata, success=True)
        assert doc.content == "This is test content"
        assert doc.metadata == metadata
        assert doc.success is True
        assert doc.error_message is None
        assert doc.warnings == []

    def test_failed_document(self):
        """Test creating failed processed document."""
        metadata = DocumentMetadata(source="/path/to/file.txt", content_type="txt")
        doc = ProcessedDocument(
            content="",
            metadata=metadata,
            success=False,
            error_message="File not found",
            warnings=["File was corrupted"],
        )
        assert doc.content == ""
        assert doc.success is False
        assert doc.error_message == "File not found"
        assert doc.warnings == ["File was corrupted"]

    def test_document_to_dict(self):
        """Test converting document to dictionary."""
        metadata = DocumentMetadata(source="/path/to/file.txt", content_type="txt")
        doc = ProcessedDocument(content="Test content", metadata=metadata, success=True)
        doc_dict = doc.to_dict()
        assert doc_dict["content"] == "Test content"
        assert doc_dict["success"] is True
        assert "metadata" in doc_dict


class TestMCPServer:
    """Test base MCP server."""

    class MockMCPServer(MCPServer):
        """Mock MCP server for testing."""

        def __init__(self, config: MCPConfig):
            super().__init__(config)

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

    def test_server_initialization(self):
        """Test MCP server initialization."""
        config = MCPConfig(server_name="test_server")
        server = self.MockMCPServer(config)
        assert server.config == config
        assert server.config.server_name == "test_server"

    def test_validate_source(self):
        """Test source validation."""
        config = MCPConfig(server_name="test_server")
        server = self.MockMCPServer(config)

        assert server.validate_source("/path/to/file.txt") is True
        assert server.validate_source("") is False
        assert server.validate_source("   ") is False

    def test_cache_operations(self):
        """Test cache operations."""
        config = MCPConfig(server_name="test_server", cache_enabled=True)
        server = self.MockMCPServer(config)

        # Test cache key generation
        cache_key = server.get_cache_key("/path/to/file.txt", param1="value1")
        assert isinstance(cache_key, str)
        assert "/path/to/file.txt" in cache_key

        # Test cache miss
        result = server.get_cached_result(cache_key)
        assert result is None

        # Test cache hit
        metadata = DocumentMetadata(source="/path/to/file.txt", content_type="txt")
        doc = ProcessedDocument(content="test", metadata=metadata)
        server.cache_result(cache_key, doc)

        cached_result = server.get_cached_result(cache_key)
        assert cached_result is not None
        assert cached_result.content == "test"

    def test_cache_disabled(self):
        """Test cache operations when disabled."""
        config = MCPConfig(server_name="test_server", cache_enabled=False)
        server = self.MockMCPServer(config)

        cache_key = server.get_cache_key("/path/to/file.txt")
        metadata = DocumentMetadata(source="/path/to/file.txt", content_type="txt")
        doc = ProcessedDocument(content="test", metadata=metadata)

        server.cache_result(cache_key, doc)
        result = server.get_cached_result(cache_key)
        assert result is None

    @pytest.mark.asyncio
    async def test_process_with_retry_success(self):
        """Test successful processing with retry."""
        config = MCPConfig(server_name="test_server", retry_attempts=3)
        server = self.MockMCPServer(config)

        result = await server.process_with_retry("/path/to/file.txt")
        assert result.success is True
        assert result.content == "Processed: /path/to/file.txt"
        assert result.metadata.processing_time > 0

    @pytest.mark.asyncio
    async def test_process_with_retry_failure(self):
        """Test failed processing with retry."""
        config = MCPConfig(server_name="test_server", retry_attempts=2)

        class FailingMCPServer(self.MockMCPServer):
            async def process_document(self, source: str, **kwargs) -> ProcessedDocument:
                raise Exception("Processing failed")

        server = FailingMCPServer(config)

        result = await server.process_with_retry("/path/to/file.txt")
        assert result.success is False
        assert result.error_message == "Processing failed"
        assert result.metadata.error_count == 2

    def test_get_server_info(self):
        """Test getting server information."""
        config = MCPConfig(server_name="test_server")
        server = self.MockMCPServer(config)

        info = server.get_server_info()
        assert info["name"] == "test_server"
        assert info["version"] == "1.0.0"
        assert info["supported_types"] == ["txt", "md", "py"]
        assert info["uptime"] > 0
        assert info["cache_size"] == 0
        assert "config" in info

    def test_cleanup(self):
        """Test server cleanup."""
        config = MCPConfig(server_name="test_server")
        server = self.MockMCPServer(config)

        # Add some cache entries
        cache_key = server.get_cache_key("/path/to/file.txt")
        metadata = DocumentMetadata(source="/path/to/file.txt", content_type="txt")
        doc = ProcessedDocument(content="test", metadata=metadata)
        server.cache_result(cache_key, doc)

        assert len(server._cache) > 0
        server.cleanup()
        assert len(server._cache) == 0


class TestMCPProtocolUtils:
    """Test MCP protocol utilities."""

    def test_validate_url(self):
        """Test URL validation."""
        assert MCPProtocolUtils.validate_url("https://example.com") is True
        assert MCPProtocolUtils.validate_url("http://localhost:8080") is True
        assert MCPProtocolUtils.validate_url("ftp://files.example.com") is True
        assert MCPProtocolUtils.validate_url("not-a-url") is False
        assert MCPProtocolUtils.validate_url("") is False

    def test_validate_file_path(self):
        """Test file path validation."""
        with tempfile.NamedTemporaryFile() as temp_file:
            assert MCPProtocolUtils.validate_file_path(temp_file.name) is True

        assert MCPProtocolUtils.validate_file_path("/nonexistent/file.txt") is False
        assert MCPProtocolUtils.validate_file_path("") is False

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert MCPProtocolUtils.sanitize_filename("normal.txt") == "normal.txt"
        assert MCPProtocolUtils.sanitize_filename("file<with>invalid:chars") == "file_with_invalid_chars"
        assert MCPProtocolUtils.sanitize_filename("file/with\\path|separators") == "file_with_path_separators"

        # Test length limit
        long_filename = "a" * 300
        sanitized = MCPProtocolUtils.sanitize_filename(long_filename)
        assert len(sanitized) == 255

    def test_detect_encoding(self):
        """Test encoding detection."""
        # Test with UTF-8 content
        utf8_content = b"Hello, world!"
        encoding = MCPProtocolUtils.detect_encoding(utf8_content)
        assert encoding in ["utf-8", "ascii"]  # chardet might detect ascii for simple text

    def test_extract_text_from_html(self):
        """Test HTML text extraction."""
        html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Hello World</h1>
                <p>This is a <strong>test</strong> paragraph.</p>
                <script>alert('test');</script>
                <style>body { color: red; }</style>
            </body>
        </html>
        """

        text = MCPProtocolUtils.extract_text_from_html(html_content)
        assert "Hello World" in text
        assert "This is a test paragraph" in text
        assert "alert('test')" not in text  # Script should be removed
        assert "color: red" not in text  # Style should be removed

    def test_calculate_word_count(self):
        """Test word count calculation."""
        assert MCPProtocolUtils.calculate_word_count("") == 0
        assert MCPProtocolUtils.calculate_word_count("Hello") == 1
        assert MCPProtocolUtils.calculate_word_count("Hello world") == 2
        assert MCPProtocolUtils.calculate_word_count("Hello, world!") == 2
        assert MCPProtocolUtils.calculate_word_count("  Hello   world  ") == 2

    def test_truncate_text(self):
        """Test text truncation."""
        short_text = "Short text"
        assert MCPProtocolUtils.truncate_text(short_text, max_length=5) == "Short..."
        assert MCPProtocolUtils.truncate_text(short_text, max_length=20) == short_text

        long_text = "This is a very long text that needs to be truncated"
        truncated = MCPProtocolUtils.truncate_text(long_text, max_length=20)
        assert len(truncated) == 23  # 20 + "..."
        assert truncated.endswith("...")


class TestMCPError:
    """Test MCP error handling."""

    def test_basic_error(self):
        """Test basic MCP error."""
        error = MCPError("Test error message")
        assert str(error) == "Test error message"
        assert error.error_code == "MCP_ERROR"
        assert error.details == {}

    def test_error_with_code(self):
        """Test MCP error with custom error code."""
        error = MCPError("File not found", error_code="FILE_NOT_FOUND")
        assert str(error) == "File not found"
        assert error.error_code == "FILE_NOT_FOUND"

    def test_error_with_details(self):
        """Test MCP error with details."""
        details = {"file_path": "/path/to/file.txt", "reason": "Permission denied"}
        error = MCPError("Access denied", error_code="ACCESS_DENIED", details=details)
        assert error.details == details
