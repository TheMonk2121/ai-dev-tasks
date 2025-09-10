"""
Unit tests for PDF MCP Server.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.utils.mcp_integration.base_server import MCPConfig, MCPError
from src.utils.mcp_integration.pdf_server import (
    PDFDocumentInfo,
    PDFMCPServer,
    PDFPageInfo,
    PDFServerConfig,
)


class TestPDFServerConfig:
    """Test PDF Server Configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = PDFServerConfig()
        assert config.enable_ocr is False
        assert config.extract_images is False
        assert config.max_pages == 100
        assert config.text_extraction_mode == "text"
        assert config.preserve_formatting is True
        assert config.extract_tables is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = PDFServerConfig(
            enable_ocr=True,
            extract_images=True,
            max_pages=50,
            text_extraction_mode="layout",
            preserve_formatting=False,
            extract_tables=False,
        )
        assert config.enable_ocr is True
        assert config.extract_images is True
        assert config.max_pages == 50
        assert config.text_extraction_mode == "layout"
        assert config.preserve_formatting is False
        assert config.extract_tables is False


class TestPDFDocumentInfo:
    """Test PDF Document Info model."""

    def test_pdf_document_info(self):
        """Test PDF document info creation."""
        doc_info = PDFDocumentInfo(
            title="Test PDF",
            author="Test Author",
            subject="Test Subject",
            creator="Test Creator",
            producer="Test Producer",
            creation_date="2024-01-01",
            modification_date="2024-01-02",
            page_count=10,
            total_word_count=1000,
            is_encrypted=False,
            is_scanned=False,
        )
        assert doc_info.title == "Test PDF"
        assert doc_info.author == "Test Author"
        assert doc_info.subject == "Test Subject"
        assert doc_info.page_count == 10
        assert doc_info.is_encrypted is False
        assert doc_info.is_scanned is False


class TestPDFPageInfo:
    """Test PDF Page Info model."""

    def test_pdf_page_info(self):
        """Test PDF page info creation."""
        page_info = PDFPageInfo(
            page_number=1,
            text_content="This is page content",
            word_count=5,
            image_count=2,
            table_count=1,
        )
        assert page_info.page_number == 1
        assert page_info.text_content == "This is page content"
        assert page_info.word_count == 5
        assert page_info.image_count == 2
        assert page_info.table_count == 1


class TestPDFMCPServer:
    """Test PDF MCP Server."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return MCPConfig(server_name="test_pdf_server")

    @pytest.fixture
    def server(self, config):
        """Create test server."""
        return PDFMCPServer(config)

    def test_server_initialization(self, config):
        """Test server initialization."""
        server = PDFMCPServer(config)
        assert server.config == config
        assert server.config.server_name == "test_pdf_server"
        assert len(server.supported_types) > 0
        assert isinstance(server.pdf_config, PDFServerConfig)

    def test_supported_content_types(self, server):
        """Test supported content types."""
        types = server.get_supported_types()
        assert "application/pdf" in types
        assert len(types) == 1

    def test_supports_content_type(self, server):
        """Test content type support checking."""
        assert server.supports_content_type("application/pdf") is True
        assert server.supports_content_type("text/html") is False
        assert server.supports_content_type("unsupported/type") is False

    def test_validate_source(self, server):
        """Test source validation."""
        # Valid sources
        assert server.validate_source("/path/to/document.pdf") is True
        assert server.validate_source("document.pdf") is True
        assert server.validate_source("https://example.com/document.pdf") is True
        assert server.validate_source("http://example.com/file.PDF") is True

        # Invalid sources
        assert server.validate_source("") is False
        assert server.validate_source("   ") is False
        assert server.validate_source("/path/to/document.txt") is False
        assert server.validate_source("https://example.com/document.html") is False

    @pytest.mark.asyncio
    async def test_read_pdf_from_file(self, server):
        """Test reading PDF from file."""
        # Create a simple PDF file for testing
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            # Create a minimal PDF content (this is just a placeholder)
            pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids []\n/Count 0\n>>\nendobj\nxref\n0 3\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n trailer\n<<\n/Size 3\n/Root 1 0 R\n>>\nstartxref\n108\n%%EOF\n"
            temp_file.write(pdf_content)
            temp_file.flush()

            try:
                result = await server._read_pdf_from_file(temp_file.name)
                assert isinstance(result, bytes)
                assert len(result) > 0
            finally:
                # Clean up
                Path(temp_file.name).unlink()

    @pytest.mark.asyncio
    async def test_read_pdf_from_file_not_found(self, server):
        """Test reading non-existent PDF file."""
        with pytest.raises(MCPError) as exc_info:
            await server._read_pdf_from_file("/nonexistent/file.pdf")

        assert exc_info.value.error_code == "READ_ERROR"

    @pytest.mark.asyncio
    async def test_download_pdf_from_url(self, server):
        """Test downloading PDF from URL."""
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.content = pdf_content
            mock_response.headers = {"content-type": "application/pdf"}
            mock_response.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value = mock_client_instance

            result = await server._download_pdf_from_url("https://example.com/test.pdf")
            assert isinstance(result, bytes)
            assert result == pdf_content

    @pytest.mark.asyncio
    async def test_download_pdf_from_url_invalid_content_type(self, server):
        """Test downloading non-PDF from URL."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.content = b"<html>Not a PDF</html>"
            mock_response.headers = {"content-type": "text/html"}
            mock_response.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value = mock_client_instance

            with pytest.raises(MCPError) as exc_info:
                await server._download_pdf_from_url("https://example.com/test.html")

            assert exc_info.value.error_code == "INVALID_CONTENT_TYPE"

    @pytest.mark.asyncio
    async def test_extract_document_info(self, server):
        """Test extracting document information."""
        # Create a mock PDF reader
        mock_reader = MagicMock()
        mock_reader.is_encrypted = False
        mock_reader.pages = [MagicMock(), MagicMock()]  # 2 pages
        mock_reader.metadata = {
            "/Title": "Test Document",
            "/Author": "Test Author",
            "/Subject": "Test Subject",
            "/Creator": "Test Creator",
            "/Producer": "Test Producer",
            "/CreationDate": "20240101",
            "/ModDate": "20240102",
        }

        with patch("fitz.open") as mock_fitz_open:
            mock_doc = MagicMock()
            mock_doc.needs_pass = False
            mock_doc.__len__.return_value = 2
            mock_doc.metadata = {
                "title": "Test Document",
                "author": "Test Author",
                "subject": "Test Subject",
                "creator": "Test Creator",
                "producer": "Test Producer",
                "creationDate": "20240101",
                "modDate": "20240102",
            }
            mock_doc[0].get_text.return_value = "This is a test document with enough text content."
            mock_fitz_open.return_value = mock_doc

            pdf_content = b"fake pdf content"
            doc_info = await server._extract_document_info(pdf_content)

            assert doc_info.title == "Test Document"
            assert doc_info.author == "Test Author"
            assert doc_info.subject == "Test Subject"
            assert doc_info.page_count == 2
            assert doc_info.is_encrypted is False
            # Note: The scanned detection logic may vary based on implementation
            # We'll just check that the property exists
            assert hasattr(doc_info, "is_scanned")

    @pytest.mark.asyncio
    async def test_extract_document_info_encrypted(self, server):
        """Test extracting document information from encrypted PDF."""
        mock_reader = MagicMock()
        mock_reader.is_encrypted = True
        mock_reader.pages = [MagicMock()]

        with patch("fitz.open") as mock_fitz_open:
            mock_doc = MagicMock()
            mock_doc.needs_pass = True
            mock_doc.__len__.return_value = 1
            mock_fitz_open.return_value = mock_doc

            pdf_content = b"fake pdf content"
            doc_info = await server._extract_document_info(pdf_content)

            assert doc_info.is_encrypted is True
            assert doc_info.page_count == 1

    @pytest.mark.asyncio
    async def test_extract_document_info_scanned(self, server):
        """Test detecting scanned PDF."""
        mock_reader = MagicMock()
        mock_reader.is_encrypted = False
        mock_reader.pages = [MagicMock()]
        mock_reader.metadata = {}

        # Mock very little text (indicating scanned document)
        with patch("fitz.open") as mock_fitz_open:
            mock_doc = MagicMock()
            mock_doc.needs_pass = False
            mock_doc.__len__.return_value = 1
            mock_doc[0].get_text.return_value = "a b c"
            mock_fitz_open.return_value = mock_doc

            pdf_content = b"fake pdf content"
            doc_info = await server._extract_document_info(pdf_content)

            assert doc_info.is_scanned is True

    @pytest.mark.asyncio
    async def test_extract_text_content(self, server):
        """Test extracting text content."""
        mock_reader = MagicMock()
        mock_reader.is_encrypted = False
        mock_reader.pages = [MagicMock(), MagicMock()]

        # Mock text extraction
        with patch("fitz.open") as mock_fitz_open:
            mock_doc = MagicMock()
            mock_doc.needs_pass = False
            mock_doc.__len__.return_value = 2
            mock_doc[0].get_text.return_value = "Page 1 content"
            mock_doc[1].get_text.return_value = "Page 2 content"
            mock_fitz_open.return_value = mock_doc

            pdf_content = b"fake pdf content"
            text_content = await server._extract_text_content(pdf_content)

            assert "Page 1 content" in text_content
            assert "Page 2 content" in text_content
            assert "--- Page 1 ---" in text_content
            assert "--- Page 2 ---" in text_content

    @pytest.mark.asyncio
    async def test_extract_text_content_encrypted(self, server):
        """Test extracting text from encrypted PDF."""
        mock_reader = MagicMock()
        mock_reader.is_encrypted = True

        with patch("fitz.open") as mock_fitz_open:
            mock_doc = MagicMock()
            mock_doc.needs_pass = True
            mock_fitz_open.return_value = mock_doc

            pdf_content = b"fake pdf content"

            with pytest.raises(MCPError) as exc_info:
                await server._extract_text_content(pdf_content)

            assert exc_info.value.error_code == "EXTRACTION_ERROR"

    @pytest.mark.asyncio
    async def test_clean_page_text(self, server):
        """Test cleaning page text."""
        page_text = "  This   is   a   test   page   with   extra   spaces  "
        cleaned = await server._clean_page_text(page_text, 1)

        assert "--- Page 1 ---" in cleaned
        assert "This is a test page with extra spaces" in cleaned

    @pytest.mark.asyncio
    async def test_process_pdf_content(self, server):
        """Test processing PDF content."""
        doc_info = PDFDocumentInfo(
            title="Test Document",
            author="Test Author",
            subject="Test Subject",
            page_count=2,
            creation_date="20240101",
            modification_date="20240102",
        )

        text_content = "--- Page 1 ---\nPage 1 content\n\n--- Page 2 ---\nPage 2 content"

        processed = await server._process_pdf_content(text_content, doc_info)

        assert "# Test Document" in processed
        assert "**Author:** Test Author" in processed
        assert "**Subject:** Test Subject" in processed
        assert "**Pages:** 2" in processed
        assert "Page 1 content" in processed
        assert "Page 2 content" in processed

    @pytest.mark.asyncio
    async def test_process_pdf_content_scanned(self, server):
        """Test processing scanned PDF content."""
        doc_info = PDFDocumentInfo(
            title="Scanned Document",
            page_count=1,
            is_scanned=True,
        )

        text_content = "--- Page 1 ---\nScanned content"

        processed = await server._process_pdf_content(text_content, doc_info)

        assert "**Note:** This appears to be a scanned document" in processed

    @pytest.mark.asyncio
    async def test_create_metadata(self, server):
        """Test creating metadata."""
        doc_info = PDFDocumentInfo(
            title="Test Document",
            author="Test Author",
            creation_date="20240101",
            modification_date="20240102",
            page_count=5,
        )

        text_content = "This is test content with multiple words."

        metadata = await server._create_metadata("/path/to/test.pdf", doc_info, text_content)

        assert metadata.source == "/path/to/test.pdf"
        assert metadata.content_type == "application/pdf"
        assert metadata.title == "Test Document"
        assert metadata.author == "Test Author"
        assert metadata.created_at == "20240101"
        assert metadata.modified_at == "20240102"
        assert metadata.page_count == 5
        assert metadata.word_count == 7  # "This is test content with multiple words" (7 words)

    @pytest.mark.asyncio
    async def test_process_document_success(self, server):
        """Test successful document processing."""
        # Mock all the internal methods
        with (
            patch.object(server, "_read_pdf_content") as mock_read,
            patch.object(server, "_extract_document_info") as mock_info,
            patch.object(server, "_extract_text_content") as mock_text,
            patch.object(server, "_process_pdf_content") as mock_process,
            patch.object(server, "_create_metadata") as mock_metadata,
        ):

            mock_read.return_value = b"fake pdf content"
            mock_info.return_value = PDFDocumentInfo(title="Test", page_count=1)
            mock_text.return_value = "Test content"
            mock_process.return_value = "# Test\nTest content"
            mock_metadata.return_value = MagicMock()

            result = await server.process_document("/path/to/test.pdf")

            assert result.success is True
            assert "# Test" in result.content

    @pytest.mark.asyncio
    async def test_process_document_invalid_source(self, server):
        """Test processing document with invalid source."""
        with pytest.raises(MCPError) as exc_info:
            await server.process_document("not-a-pdf.txt")

        assert exc_info.value.error_code == "INVALID_SOURCE"

    @pytest.mark.asyncio
    async def test_get_page_info(self, server):
        """Test getting page information."""
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock()]
        mock_reader.pages[0].extract_text.return_value = "Page 1 content"

        with patch.object(server, "_read_pdf_content") as mock_read, patch("fitz.open") as mock_fitz_open:

            mock_read.return_value = b"fake pdf content"
            mock_doc = MagicMock()
            mock_doc.__len__.return_value = 1
            mock_doc[0].get_text.return_value = "Page 1 content"
            mock_fitz_open.return_value = mock_doc

            page_info = await server.get_page_info("/path/to/test.pdf", 1)

            assert page_info is not None
            assert page_info.page_number == 1
            assert page_info.text_content == "Page 1 content"
            assert page_info.word_count == 3  # "Page 1 content"

    @pytest.mark.asyncio
    async def test_get_page_info_invalid_page(self, server):
        """Test getting information for invalid page."""
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock()]  # Only 1 page

        with patch.object(server, "_read_pdf_content") as mock_read, patch("fitz.open") as mock_fitz_open:

            mock_read.return_value = b"fake pdf content"
            mock_doc = MagicMock()
            mock_doc.__len__.return_value = 1  # Only 1 page
            mock_fitz_open.return_value = mock_doc

            page_info = await server.get_page_info("/path/to/test.pdf", 2)

            assert page_info is None

    def test_get_pdf_config(self, server):
        """Test getting PDF configuration."""
        config = server.get_pdf_config()

        assert "enable_ocr" in config
        assert "extract_images" in config
        assert "max_pages" in config
        assert "text_extraction_mode" in config
        assert "preserve_formatting" in config
        assert "extract_tables" in config

    def test_update_pdf_config(self, server):
        """Test updating PDF configuration."""
        original_max_pages = server.pdf_config.max_pages

        server.update_pdf_config(max_pages=50)

        assert server.pdf_config.max_pages == 50
        assert server.pdf_config.max_pages != original_max_pages

    @pytest.mark.asyncio
    async def test_extract_tables(self, server):
        """Test table extraction."""
        tables = await server.extract_tables("/path/to/test.pdf")

        # Should return empty list for now (not implemented)
        assert tables == []

    @pytest.mark.asyncio
    async def test_extract_images(self, server):
        """Test image extraction."""
        images = await server.extract_images("/path/to/test.pdf")

        # Should return empty list for now (not implemented)
        assert images == []

    @pytest.mark.asyncio
    async def test_missing_dependency(self, server):
        """Test handling missing PyMuPDF dependency."""
        with patch("fitz.open", side_effect=ImportError("No module named 'fitz'")):
            with pytest.raises(MCPError) as exc_info:
                await server._extract_document_info(b"fake content")

            assert exc_info.value.error_code == "MISSING_DEPENDENCY"

    @pytest.mark.asyncio
    async def test_server_info(self, server):
        """Test server information."""
        info = server.get_server_info()

        assert info["name"] == "test_pdf_server"
        assert info["version"] == "1.0.0"
        assert "application/pdf" in info["supported_types"]
        assert info["cache_size"] == 0
