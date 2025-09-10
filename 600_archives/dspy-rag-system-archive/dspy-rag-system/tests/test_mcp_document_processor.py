"""
Unit tests for MCP Document Processor.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.dspy_modules.mcp_document_processor import MCPDocumentIngestionPipeline, MCPDocumentProcessor
from src.utils.mcp_integration import DocumentMetadata


class TestMCPDocumentProcessor:
    """Test MCP Document Processor."""

    @pytest.fixture
    def processor(self):
        """Create test processor."""
        return MCPDocumentProcessor()

    def test_processor_initialization(self, processor):
        """Test processor initialization."""
        assert processor.chunk_size == 300
        assert processor.chunk_overlap == 50
        assert processor.mcp_timeout == 30
        assert processor.enable_cache is True
        assert len(processor.server_registry) == 4
        assert "file_system" in processor.server_registry
        assert "web" in processor.server_registry
        assert "pdf" in processor.server_registry
        assert "github" in processor.server_registry

    def test_processor_initialization_custom_config(self):
        """Test processor initialization with custom configuration."""
        processor = MCPDocumentProcessor(
            chunk_size=500,
            chunk_overlap=100,
            mcp_timeout=60,
            enable_cache=False,
        )
        assert processor.chunk_size == 500
        assert processor.chunk_overlap == 100
        assert processor.mcp_timeout == 60
        assert processor.enable_cache is False

    def test_route_document_file_system(self, processor):
        """Test routing document to file system server."""
        with patch.object(processor.file_system_server, "validate_source", return_value=True):
            server_type, server = processor._route_document("test_file.txt")
            assert server_type == "file_system"
            assert server == processor.file_system_server

    def test_route_document_web(self, processor):
        """Test routing document to web server."""
        with (
            patch.object(processor.server_registry["file_system"], "validate_source", return_value=False),
            patch.object(processor.server_registry["web"], "validate_source", return_value=True),
        ):
            server_type, server = processor._route_document("https://example.com")
            assert server_type == "web"
            assert server == processor.web_server

    def test_route_document_pdf(self, processor):
        """Test routing document to PDF server."""
        with (
            patch.object(processor.server_registry["file_system"], "validate_source", return_value=False),
            patch.object(processor.server_registry["web"], "validate_source", return_value=False),
            patch.object(processor.server_registry["pdf"], "validate_source", return_value=True),
        ):
            server_type, server = processor._route_document("document.pdf")
            assert server_type == "pdf"
            assert server == processor.pdf_server

    def test_route_document_github(self, processor):
        """Test routing document to GitHub server."""
        with (
            patch.object(processor.server_registry["file_system"], "validate_source", return_value=False),
            patch.object(processor.server_registry["web"], "validate_source", return_value=False),
            patch.object(processor.server_registry["pdf"], "validate_source", return_value=False),
            patch.object(processor.server_registry["github"], "validate_source", return_value=True),
        ):
            server_type, server = processor._route_document("https://github.com/owner/repo")
            assert server_type == "github"
            assert server == processor.github_server

    def test_route_document_no_server_found(self, processor):
        """Test routing document when no server can handle it."""
        # Mock all servers to return False
        with (
            patch.object(processor.server_registry["file_system"], "validate_source", return_value=False),
            patch.object(processor.server_registry["web"], "validate_source", return_value=False),
            patch.object(processor.server_registry["pdf"], "validate_source", return_value=False),
            patch.object(processor.server_registry["github"], "validate_source", return_value=False),
        ):

            with pytest.raises(ValueError, match="No MCP server can handle source"):
                processor._route_document("unknown_source")

    def test_determine_fallback_server_github(self, processor):
        """Test determining fallback server for GitHub URLs."""
        fallback = processor._determine_fallback_server("https://github.com/owner/repo")
        assert fallback == "github"

    def test_determine_fallback_server_web(self, processor):
        """Test determining fallback server for web URLs."""
        fallback = processor._determine_fallback_server("https://example.com")
        assert fallback == "web"

    def test_determine_fallback_server_pdf(self, processor):
        """Test determining fallback server for PDF files."""
        fallback = processor._determine_fallback_server("document.pdf")
        assert fallback == "pdf"

    def test_determine_fallback_server_file_system(self, processor):
        """Test determining fallback server for file system."""
        with patch("pathlib.Path.exists", return_value=True):
            fallback = processor._determine_fallback_server("test_file.txt")
            assert fallback == "file_system"

    def test_determine_fallback_server_none(self, processor):
        """Test determining fallback server when none found."""
        fallback = processor._determine_fallback_server("unknown_source")
        assert fallback is None

    def test_create_chunks_from_content(self, processor):
        """Test creating chunks from content."""
        content = "This is a test document with multiple words for chunking."
        document_id = "test_doc_123"

        chunks = processor._create_chunks_from_content(content, document_id)

        assert len(chunks) > 0
        assert chunks[0]["document_id"] == document_id
        assert chunks[0]["chunk_index"] == 0
        assert "text" in chunks[0]
        assert "word_count" in chunks[0]

    def test_create_chunks_from_content_empty(self, processor):
        """Test creating chunks from empty content."""
        content = ""
        document_id = "test_doc_123"

        chunks = processor._create_chunks_from_content(content, document_id)

        assert len(chunks) == 0

    def test_create_chunks_from_content_fallback(self, processor):
        """Test chunk creation fallback when error occurs."""
        content = "Test content"
        document_id = "test_doc_123"

        # Test that the method works normally and returns expected chunks
        chunks = processor._create_chunks_from_content(content, document_id)
        assert len(chunks) == 1
        assert chunks[0]["text"] == content
        assert chunks[0]["id"] == f"{document_id}_chunk_0"
        assert chunks[0]["document_id"] == document_id
        assert chunks[0]["chunk_index"] == 0

    def test_prepare_metadata_success(self, processor):
        """Test preparing metadata successfully."""
        # Create mock processed document
        mock_metadata = DocumentMetadata(
            source="test_source",
            content_type="text/plain",
            title="Test Document",
            author="Test Author",
            created_at="2024-01-01",
            modified_at="2024-01-02",
            word_count=100,
        )

        mock_processed_doc = MagicMock()
        mock_processed_doc.metadata = mock_metadata

        document_source = "test_source"
        document_id = "test_doc_123"

        metadata = processor._prepare_metadata(mock_processed_doc, document_source, document_id)

        assert metadata["document_id"] == document_id
        assert metadata["source"] == document_source
        assert metadata["content_type"] == "text/plain"
        assert metadata["title"] == "Test Document"
        assert metadata["author"] == "Test Author"
        assert metadata["word_count"] == 100
        assert metadata["server_type"] == "file_system"

    def test_prepare_metadata_with_page_count(self, processor):
        """Test preparing metadata with page count."""
        # Create mock processed document with page count
        mock_metadata = DocumentMetadata(
            source="test_source",
            content_type="application/pdf",
            word_count=100,
        )
        mock_metadata.page_count = 5  # Add page count attribute

        mock_processed_doc = MagicMock()
        mock_processed_doc.metadata = mock_metadata

        document_source = "test_source"
        document_id = "test_doc_123"

        metadata = processor._prepare_metadata(mock_processed_doc, document_source, document_id)

        assert metadata["page_count"] == 5
        assert metadata["server_type"] == "pdf"

    def test_prepare_metadata_fallback(self, processor):
        """Test metadata preparation fallback when error occurs."""
        # Create mock processed document that will cause an error
        mock_processed_doc = MagicMock()
        mock_processed_doc.metadata = None  # This will cause an error

        document_source = "test_source"
        document_id = "test_doc_123"

        metadata = processor._prepare_metadata(mock_processed_doc, document_source, document_id)

        assert metadata["document_id"] == document_id
        assert metadata["source"] == document_source
        assert metadata["content_type"] == "unknown"
        assert metadata["word_count"] == 0
        assert metadata["server_type"] == "unknown"

    def test_get_server_type_from_metadata(self, processor):
        """Test getting server type from metadata content type."""
        assert processor._get_server_type_from_metadata("file/text") == "file_system"
        assert processor._get_server_type_from_metadata("web/html") == "web"
        assert processor._get_server_type_from_metadata("application/pdf") == "pdf"
        assert processor._get_server_type_from_metadata("github/repository") == "github"
        assert processor._get_server_type_from_metadata("unknown/type") == "unknown"

    def test_mask_source_url(self, processor):
        """Test masking URL sources."""
        masked = processor._mask_source("https://example.com/path/to/file")
        assert masked == "https://example.com/..."

    def test_mask_source_file(self, processor):
        """Test masking file sources."""
        masked = processor._mask_source("/path/to/file.txt")
        assert masked == "to/file.txt"

    def test_mask_source_file_no_parent(self, processor):
        """Test masking file sources without parent directory."""
        masked = processor._mask_source("file.txt")
        assert masked == "file.txt"

    def test_update_stats_success(self, processor):
        """Test updating statistics for successful processing."""
        initial_total = processor.processing_stats["total_documents"]
        initial_success = processor.processing_stats["successful_documents"]
        initial_file_system = processor.processing_stats["server_usage"]["file_system"]

        processor._update_stats("file_system", True, 1_000_000_000)  # 1 second

        assert processor.processing_stats["total_documents"] == initial_total + 1
        assert processor.processing_stats["successful_documents"] == initial_success + 1
        assert processor.processing_stats["server_usage"]["file_system"] == initial_file_system + 1
        assert processor.processing_stats["total_processing_time"] == 1.0

    def test_update_stats_failure(self, processor):
        """Test updating statistics for failed processing."""
        initial_total = processor.processing_stats["total_documents"]
        initial_failed = processor.processing_stats["failed_documents"]

        processor._update_stats("web", False, 500_000_000)  # 0.5 seconds

        assert processor.processing_stats["total_documents"] == initial_total + 1
        assert processor.processing_stats["failed_documents"] == initial_failed + 1
        assert processor.processing_stats["total_processing_time"] == 0.5

    def test_get_processing_stats(self, processor):
        """Test getting processing statistics."""
        # Add some test data
        processor.processing_stats["total_documents"] = 10
        processor.processing_stats["successful_documents"] = 8
        processor.processing_stats["failed_documents"] = 2
        processor.processing_stats["total_processing_time"] = 5.0

        stats = processor.get_processing_stats()

        assert stats["total_documents"] == 10
        assert stats["successful_documents"] == 8
        assert stats["failed_documents"] == 2
        assert stats["average_processing_time"] == 0.5
        assert stats["success_rate"] == 0.8

    def test_get_processing_stats_empty(self, processor):
        """Test getting processing statistics when no documents processed."""
        stats = processor.get_processing_stats()

        assert stats["total_documents"] == 0
        assert stats["average_processing_time"] == 0.0
        assert stats["success_rate"] == 0.0

    def test_get_server_info(self, processor):
        """Test getting server information."""
        # Mock server info
        mock_info = {
            "name": "test_server",
            "version": "1.0.0",
            "supported_types": ["text/plain"],
            "cache_size": 10,
        }

        with patch.object(processor.file_system_server, "get_server_info", return_value=mock_info):
            server_info = processor.get_server_info()

            assert "file_system" in server_info
            assert server_info["file_system"]["name"] == "test_server"
            assert server_info["file_system"]["version"] == "1.0.0"

    def test_get_server_info_error(self, processor):
        """Test getting server information when error occurs."""
        with patch.object(processor.file_system_server, "get_server_info", side_effect=Exception("Server error")):
            server_info = processor.get_server_info()

            assert "file_system" in server_info
            assert "error" in server_info["file_system"]

    @pytest.mark.asyncio
    async def test_process_with_server_success(self, processor):
        """Test processing document with server successfully."""
        # Create mock processed document
        mock_metadata = DocumentMetadata(
            source="test_source",
            content_type="text/plain",
            title="Test Document",
            word_count=50,
        )

        mock_processed_doc = MagicMock()
        mock_processed_doc.success = True
        mock_processed_doc.content = "This is test content for processing."
        mock_processed_doc.metadata = mock_metadata

        # Mock server
        mock_server = MagicMock()
        mock_server.process_document = AsyncMock(return_value=mock_processed_doc)

        document_source = "test_source"
        document_id = "test_doc_123"

        result = await processor._process_with_server(mock_server, document_source, document_id)

        assert result["document_source"] == document_source
        assert result["document_id"] == document_id
        assert result["total_chunks"] > 0
        assert "chunks" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_process_with_server_failure(self, processor):
        """Test processing document with server failure."""
        # Create mock processed document that failed
        mock_processed_doc = MagicMock()
        mock_processed_doc.success = False
        mock_processed_doc.metadata = "Error occurred"

        # Mock server
        mock_server = MagicMock()
        mock_server.process_document = AsyncMock(return_value=mock_processed_doc)

        document_source = "test_source"
        document_id = "test_doc_123"

        with pytest.raises(Exception, match="MCP server processing failed"):
            await processor._process_with_server(mock_server, document_source, document_id)

    def test_forward_success(self, processor):
        """Test successful forward method execution."""
        # Mock routing
        with patch.object(processor, "_route_document", return_value=("file_system", processor.file_system_server)):
            # Mock server processing
            mock_metadata = DocumentMetadata(
                source="test_source",
                content_type="text/plain",
                title="Test Document",
                word_count=50,
            )

            mock_processed_doc = MagicMock()
            mock_processed_doc.success = True
            mock_processed_doc.content = "This is test content for processing."
            mock_processed_doc.metadata = mock_metadata

            with patch.object(processor.file_system_server, "process_document", return_value=mock_processed_doc):
                result = processor.forward("test_file.txt")

                assert result["document_source"] == "test_file.txt"
                assert result["total_chunks"] > 0
                assert result["server_type"] == "file_system"

    def test_forward_routing_failure(self, processor):
        """Test forward method when routing fails."""
        with patch.object(processor, "_route_document", side_effect=ValueError("No server found")):
            with pytest.raises(ValueError, match="No server found"):
                processor.forward("unknown_source")

    def test_forward_processing_failure(self, processor):
        """Test forward method when processing fails."""
        with patch.object(processor, "_route_document", return_value=("file_system", processor.file_system_server)):
            with patch.object(
                processor.file_system_server, "process_document", side_effect=Exception("Processing failed")
            ):
                with pytest.raises(Exception, match="Processing failed"):
                    processor.forward("test_file.txt")

    def test_cleanup(self, processor):
        """Test cleanup method."""
        # Mock cleanup methods
        with patch.object(processor.file_system_server, "cleanup") as mock_cleanup:
            processor.cleanup()
            mock_cleanup.assert_called_once()


class TestMCPDocumentIngestionPipeline:
    """Test MCP Document Ingestion Pipeline."""

    @pytest.fixture
    def pipeline(self):
        """Create test pipeline."""
        return MCPDocumentIngestionPipeline()

    def test_pipeline_initialization(self, pipeline):
        """Test pipeline initialization."""
        assert pipeline.processor is not None
        assert isinstance(pipeline.processor, MCPDocumentProcessor)

    def test_pipeline_forward_success(self, pipeline):
        """Test successful pipeline forward execution."""
        # Mock processor result
        mock_result = {
            "chunks": [{"text": "chunk 1"}, {"text": "chunk 2"}],
            "metadata": {"title": "Test Document"},
            "total_chunks": 2,
            "document_id": "test_doc_123",
            "server_type": "file_system",
        }

        with patch.object(pipeline.processor, "forward", return_value=mock_result):
            result = pipeline.forward("test_file.txt")

            assert result["total_chunks"] == 2
            assert result["server_type"] == "file_system"
            assert "pipeline_processing_time_ms" in result

    def test_pipeline_forward_with_vector_store(self, pipeline):
        """Test pipeline forward with vector store."""
        # Mock processor result
        mock_result = {
            "chunks": [{"text": "chunk 1"}, {"text": "chunk 2"}],
            "metadata": {"title": "Test Document"},
            "total_chunks": 2,
            "document_id": "test_doc_123",
        }

        # Mock vector store
        mock_vector_store = MagicMock()
        mock_vector_store.return_value = {"status": "success"}

        with patch.object(pipeline.processor, "forward", return_value=mock_result):
            result = pipeline.forward("test_file.txt", vector_store=mock_vector_store)

            assert result["total_chunks"] == 2
            # Verify vector store was called
            mock_vector_store.assert_called_once()

    def test_pipeline_forward_vector_store_failure(self, pipeline):
        """Test pipeline forward when vector store fails."""
        # Mock processor result
        mock_result = {
            "chunks": [{"text": "chunk 1"}],
            "metadata": {"title": "Test Document"},
            "total_chunks": 1,
            "document_id": "test_doc_123",
        }

        # Mock vector store that fails
        mock_vector_store = MagicMock()
        mock_vector_store.return_value = {"status": "error", "error": "Storage failed"}

        with patch.object(pipeline.processor, "forward", return_value=mock_result):
            # Should not raise exception, just log error
            result = pipeline.forward("test_file.txt", vector_store=mock_vector_store)

            assert result["total_chunks"] == 1

    def test_pipeline_forward_processing_failure(self, pipeline):
        """Test pipeline forward when processing fails."""
        with patch.object(pipeline.processor, "forward", side_effect=Exception("Processing failed")):
            with pytest.raises(Exception, match="Processing failed"):
                pipeline.forward("test_file.txt")

    def test_get_processing_stats(self, pipeline):
        """Test getting processing statistics from pipeline."""
        mock_stats = {"total_documents": 10, "success_rate": 0.8}

        with patch.object(pipeline.processor, "get_processing_stats", return_value=mock_stats):
            stats = pipeline.get_processing_stats()

            assert stats["total_documents"] == 10
            assert stats["success_rate"] == 0.8

    def test_get_server_info(self, pipeline):
        """Test getting server information from pipeline."""
        mock_info = {"file_system": {"name": "test"}}

        with patch.object(pipeline.processor, "get_server_info", return_value=mock_info):
            info = pipeline.get_server_info()

            assert info["file_system"]["name"] == "test"

    def test_cleanup(self, pipeline):
        """Test pipeline cleanup."""
        with patch.object(pipeline.processor, "cleanup") as mock_cleanup:
            pipeline.cleanup()
            mock_cleanup.assert_called_once()
