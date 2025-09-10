#!/usr/bin/env python3
import os
import sys
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import pytest

sys.path.append("src")

from utils.mcp_integration.office_server import (
    MCPConfig,
    MCPError,
    OfficeDocumentInfo,
    OfficeMCPServer,
    OfficeServerConfig,
)


class TestOfficeServerConfig:
    def test_default_config(self):
        config = OfficeServerConfig()
        assert config.max_file_size == 50 * 1024 * 1024  # 50MB
        assert config.extract_images is False
        assert config.preserve_formatting is True
        assert config.include_metadata is True
        assert config.handle_corrupted_files is True
        assert config.password_protection_timeout == 30

    def test_custom_config(self):
        config = OfficeServerConfig(
            max_file_size=10 * 1024 * 1024,  # 10MB
            extract_images=True,
            preserve_formatting=False,
            password_protection_timeout=60,
        )
        assert config.max_file_size == 10 * 1024 * 1024
        assert config.extract_images is True
        assert config.preserve_formatting is False
        assert config.password_protection_timeout == 60


class TestOfficeDocumentInfo:
    def test_document_info_creation(self):
        info = OfficeDocumentInfo()
        assert info.title is None
        assert info.author is None
        assert info.keywords == []
        assert info.page_count is None
        assert info.word_count is None

    def test_document_info_with_data(self):
        info = OfficeDocumentInfo(
            title="Test Document", author="John Doe", keywords=["test", "document"], page_count=5, word_count=100
        )
        assert info.title == "Test Document"
        assert info.author == "John Doe"
        assert info.keywords == ["test", "document"]
        assert info.page_count == 5
        assert info.word_count == 100


class TestOfficeMCPServer:
    @pytest.fixture
    def server(self):
        config = MCPConfig(server_name="test_office_server")
        return OfficeMCPServer(config)

    def test_server_initialization(self, server):
        assert server.config.server_name == "test_office_server"
        assert isinstance(server.office_config, OfficeServerConfig)
        assert len(server.supported_types) == 6
        assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in server.supported_types
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in server.supported_types
        assert "application/vnd.openxmlformats-officedocument.presentationml.presentation" in server.supported_types

    def test_validate_source_word_files(self, server):
        assert server.validate_source("document.docx") is True
        assert server.validate_source("document.doc") is True
        assert server.validate_source("/path/to/document.docx") is True
        assert server.validate_source("file:///path/to/document.docx") is True

    def test_validate_source_excel_files(self, server):
        assert server.validate_source("spreadsheet.xlsx") is True
        assert server.validate_source("spreadsheet.xls") is True
        assert server.validate_source("/path/to/spreadsheet.xlsx") is True

    def test_validate_source_powerpoint_files(self, server):
        assert server.validate_source("presentation.pptx") is True
        assert server.validate_source("presentation.ppt") is True
        assert server.validate_source("/path/to/presentation.pptx") is True

    def test_validate_source_urls(self, server):
        assert server.validate_source("https://example.com/document.docx") is True
        assert server.validate_source("http://example.com/spreadsheet.xlsx") is True
        assert server.validate_source("https://example.com/presentation.pptx") is True

    def test_validate_source_invalid(self, server):
        assert server.validate_source("document.txt") is False
        assert server.validate_source("image.jpg") is False
        assert server.validate_source("https://example.com/document.txt") is False
        assert server.validate_source("") is False

    def test_get_file_extension(self, server):
        assert server._get_file_extension("document.docx") == ".docx"
        assert server._get_file_extension("spreadsheet.xlsx") == ".xlsx"
        assert server._get_file_extension("presentation.pptx") == ".pptx"
        assert server._get_file_extension("file:///path/document.doc") == ".doc"

    def test_get_document_type(self, server):
        assert server._get_document_type("document.docx") == "word"
        assert server._get_document_type("document.doc") == "word"
        assert server._get_document_type("spreadsheet.xlsx") == "excel"
        assert server._get_document_type("spreadsheet.xls") == "excel"
        assert server._get_document_type("presentation.pptx") == "powerpoint"
        assert server._get_document_type("presentation.ppt") == "powerpoint"
        assert server._get_document_type("unknown.txt") == "unknown"

    def test_supports_content_type(self, server):
        assert (
            server.supports_content_type("application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            is True
        )
        assert server.supports_content_type("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") is True
        assert (
            server.supports_content_type("application/vnd.openxmlformats-officedocument.presentationml.presentation")
            is True
        )
        assert server.supports_content_type("text/plain") is False

    def test_get_supported_types(self, server):
        types = server.get_supported_types()
        assert len(types) == 6
        assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in types
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in types
        assert "application/vnd.openxmlformats-officedocument.presentationml.presentation" in types

    @patch("docx.Document")
    def test_extract_word_content_success(self, mock_document, server):
        # Mock document structure
        mock_doc = Mock()
        mock_doc.paragraphs = [Mock(text="Paragraph 1"), Mock(text="Paragraph 2")]
        mock_doc.tables = []
        mock_doc.core_properties = Mock(
            title="Test Document",
            author="John Doe",
            subject="Test Subject",
            keywords="test, document",
            created=None,
            modified=None,
            version="1.0",
        )
        mock_document.return_value = mock_doc

        result = server._extract_word_content("test.docx")

        assert result["document_type"] == "word"
        assert "Paragraph 1" in result["content"]
        assert "Paragraph 2" in result["content"]
        assert result["metadata"].title == "Test Document"
        assert result["metadata"].author == "John Doe"
        assert result["metadata"].keywords == ["test", "document"]

    @patch("docx.Document")
    def test_extract_word_content_with_tables(self, mock_document, server):
        # Mock document with tables
        mock_doc = Mock()
        mock_doc.paragraphs = [Mock(text="Paragraph 1")]

        # Mock table
        mock_table = Mock()
        mock_row = Mock()
        mock_cell1 = Mock(text="Cell 1")
        mock_cell2 = Mock(text="Cell 2")
        mock_row.cells = [mock_cell1, mock_cell2]
        mock_table.rows = [mock_row]
        mock_doc.tables = [mock_table]
        mock_doc.core_properties = Mock()
        mock_document.return_value = mock_doc

        result = server._extract_word_content("test.docx")

        assert "Cell 1 | Cell 2" in result["content"]

    @patch("docx.Document")
    def test_extract_word_content_import_error(self, mock_document, server):
        mock_document.side_effect = ImportError("No module named 'docx'")

        with pytest.raises(MCPError, match="python-docx library not available"):
            server._extract_word_content("test.docx")

    @patch("docx.Document")
    def test_extract_word_content_corrupted_file(self, mock_document, server):
        mock_document.side_effect = Exception("Corrupted file")

        result = server._extract_word_content("test.docx")

        assert "error" in result
        assert "Corrupted file" in result["content"]

    @patch("openpyxl.load_workbook")
    def test_extract_excel_content_success(self, mock_load_workbook, server):
        # Mock workbook structure
        mock_workbook = Mock()
        mock_sheet = Mock()
        mock_sheet.iter_rows.return_value = [["A1", "B1"], ["A2", "B2"]]
        mock_workbook.sheetnames = ["Sheet1"]
        mock_workbook.__getitem__.return_value = mock_sheet
        mock_workbook.worksheets = [mock_sheet]
        mock_workbook.properties = Mock(
            title="Test Spreadsheet",
            creator="John Doe",
            subject="Test Subject",
            created=None,
            modified=None,
            version="1.0",
        )
        mock_load_workbook.return_value = mock_workbook

        result = server._extract_excel_content("test.xlsx")

        assert result["document_type"] == "excel"
        assert "=== Worksheet: Sheet1 ===" in result["content"]
        assert "A1 | B1" in result["content"]
        assert "A2 | B2" in result["content"]
        assert result["metadata"].title == "Test Spreadsheet"
        assert result["metadata"].author == "John Doe"

    @patch("openpyxl.load_workbook")
    def test_extract_excel_content_import_error(self, mock_load_workbook, server):
        mock_load_workbook.side_effect = ImportError("No module named 'openpyxl'")

        with pytest.raises(MCPError, match="openpyxl library not available"):
            server._extract_excel_content("test.xlsx")

    @patch("pptx.Presentation")
    def test_extract_powerpoint_content_success(self, mock_presentation, server):
        # Mock presentation structure
        mock_prs = Mock()
        mock_slide = Mock()
        mock_shape = Mock()
        mock_shape.text = "Slide Text"
        mock_slide.shapes = [mock_shape]
        mock_prs.slides = [mock_slide]
        mock_prs.core_properties = Mock(
            title="Test Presentation", author="John Doe", subject="Test Subject", created=None, modified=None
        )
        mock_presentation.return_value = mock_prs

        result = server._extract_powerpoint_content("test.pptx")

        assert result["document_type"] == "powerpoint"
        assert "=== Slide 1 ===" in result["content"]
        assert "Slide Text" in result["content"]
        assert result["metadata"].title == "Test Presentation"
        assert result["metadata"].author == "John Doe"
        assert result["metadata"].page_count == 1

    @patch("pptx.Presentation")
    def test_extract_powerpoint_content_import_error(self, mock_presentation, server):
        mock_presentation.side_effect = ImportError("No module named 'pptx'")

        with pytest.raises(MCPError, match="python-pptx library not available"):
            server._extract_powerpoint_content("test.pptx")

    @pytest.mark.asyncio
    async def test_download_file_success(self, server):
        mock_response = Mock()
        mock_response.content = b"test content"
        mock_response.raise_for_status.return_value = None

        mock_session = AsyncMock()
        mock_session.get.return_value = mock_response
        server._session = mock_session

        with patch("tempfile.NamedTemporaryFile") as mock_temp_file:
            mock_temp_file.return_value.__enter__.return_value.name = "/tmp/test.docx"

            result = await server._download_file("https://example.com/test.docx")

            assert result == "/tmp/test.docx"
            mock_session.get.assert_called_once_with("https://example.com/test.docx")

    @pytest.mark.asyncio
    async def test_download_file_too_large(self, server):
        mock_response = Mock()
        mock_response.content = b"x" * (server.office_config.max_file_size + 1)
        mock_response.raise_for_status.return_value = None

        mock_session = AsyncMock()
        mock_session.get.return_value = mock_response
        server._session = mock_session

        with pytest.raises(MCPError, match="File too large"):
            await server._download_file("https://example.com/large.docx")

    @pytest.mark.asyncio
    async def test_process_document_word_file(self, server):
        with patch.object(server, "_extract_word_content") as mock_extract:
            mock_extract.return_value = {
                "content": "Test content",
                "metadata": OfficeDocumentInfo(title="Test Doc", author="John Doe"),
                "document_type": "word",
            }

            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
                f.write(b"test content")
                temp_path = f.name

            try:
                result = await server.process_document(temp_path)

                assert result.metadata.content_type == "application/vnd.openxmlformats-officedocument.word"
                assert result.metadata.title == "Test Doc"
                assert result.metadata.author == "John Doe"
                assert result.content == "Test content"
                assert result.success is True
            finally:
                os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_process_document_excel_file(self, server):
        with patch.object(server, "_extract_excel_content") as mock_extract:
            mock_extract.return_value = {
                "content": "Excel content",
                "metadata": OfficeDocumentInfo(title="Test Sheet", author="Jane Doe"),
                "document_type": "excel",
            }

            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
                f.write(b"test content")
                temp_path = f.name

            try:
                result = await server.process_document(temp_path)

                assert result.metadata.content_type == "application/vnd.openxmlformats-officedocument.excel"
                assert result.metadata.title == "Test Sheet"
                assert result.metadata.author == "Jane Doe"
                assert result.content == "Excel content"
                assert result.success is True
            finally:
                os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_process_document_powerpoint_file(self, server):
        with patch.object(server, "_extract_powerpoint_content") as mock_extract:
            mock_extract.return_value = {
                "content": "PowerPoint content",
                "metadata": OfficeDocumentInfo(title="Test Presentation", author="Bob Smith"),
                "document_type": "powerpoint",
            }

            with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
                f.write(b"test content")
                temp_path = f.name

            try:
                result = await server.process_document(temp_path)

                assert result.metadata.content_type == "application/vnd.openxmlformats-officedocument.powerpoint"
                assert result.metadata.title == "Test Presentation"
                assert result.metadata.author == "Bob Smith"
                assert result.content == "PowerPoint content"
                assert result.success is True
            finally:
                os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_process_document_unsupported_type(self, server):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test content")
            temp_path = f.name

        try:
            with pytest.raises(MCPError, match="Unsupported document type"):
                await server.process_document(temp_path)
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_process_document_file_too_large(self, server):
        # Create a file larger than the limit
        server.office_config.max_file_size = 10  # 10 bytes

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            f.write(b"x" * 20)  # 20 bytes
            temp_path = f.name

        try:
            with pytest.raises(MCPError, match="File too large"):
                await server.process_document(temp_path)
        finally:
            os.unlink(temp_path)

    def test_get_server_info(self, server):
        info = server.get_server_info()
        assert info["name"] == "test_office_server"
        assert info["version"] == "1.0.0"
        assert len(info["supported_types"]) == 6
        assert "word" in info["document_types"]
        assert "excel" in info["document_types"]
        assert "powerpoint" in info["document_types"]
        assert "text_extraction" in info["features"]
        assert "metadata_extraction" in info["features"]
        assert "corrupted_file_handling" in info["features"]
        # Check that dependency availability is included in server info
        assert "dependencies_available" in info
        assert isinstance(info["dependencies_available"], dict)
        assert "python-docx" in info["dependencies_available"]
        assert "openpyxl" in info["dependencies_available"]
        assert "python-pptx" in info["dependencies_available"]

    def test_dependency_checking(self, server):
        """Test that dependency checking works correctly."""
        # The dependency check should run during initialization
        # and not raise any exceptions
        assert hasattr(server, "_check_dependencies")

        # Test that the method exists and can be called
        server._check_dependencies()

        # Verify that the dependency flags are set
        from utils.mcp_integration.office_server import DOCX_AVAILABLE, OPENPYXL_AVAILABLE, PPTX_AVAILABLE

        assert isinstance(DOCX_AVAILABLE, bool)
        assert isinstance(OPENPYXL_AVAILABLE, bool)
        assert isinstance(PPTX_AVAILABLE, bool)

    @pytest.mark.asyncio
    async def test_cleanup(self, server):
        mock_session = AsyncMock()
        server._session = mock_session

        await server.cleanup()

        assert server._session is None
        mock_session.aclose.assert_called_once()
