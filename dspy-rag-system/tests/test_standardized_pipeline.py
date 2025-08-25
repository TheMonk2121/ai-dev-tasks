#!/usr/bin/env python3
import sys
from typing import cast
from unittest.mock import Mock, patch

import pytest

sys.path.append("src")

from dspy_modules.standardized_pipeline import (
    PipelineProgress,
    PipelineResult,
    PipelineStatus,
    StandardizedIngestionPipeline,
)


class TestPipelineProgress:
    """Test PipelineProgress dataclass functionality."""

    def test_progress_percentage_calculation(self):
        """Test progress percentage calculation."""
        progress = PipelineProgress(total_documents=10, processed_documents=5)
        assert progress.progress_percentage == 50.0

    def test_progress_percentage_zero_total(self):
        """Test progress percentage with zero total documents."""
        progress = PipelineProgress(total_documents=0, processed_documents=5)
        assert progress.progress_percentage == 0.0

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        progress = PipelineProgress(processed_documents=10, successful_documents=8, failed_documents=2)
        assert progress.success_rate == 80.0

    def test_success_rate_zero_processed(self):
        """Test success rate with zero processed documents."""
        progress = PipelineProgress(processed_documents=0, successful_documents=5)
        assert progress.success_rate == 0.0

    def test_elapsed_time_calculation(self):
        """Test elapsed time calculation."""
        import time

        start_time = time.time() - 5.0  # 5 seconds ago
        progress = PipelineProgress(start_time=start_time)
        assert abs(progress.elapsed_time - 5.0) < 0.1

    def test_elapsed_time_no_start_time(self):
        """Test elapsed time with no start time."""
        progress = PipelineProgress()
        assert progress.elapsed_time == 0.0

    def test_update_estimated_completion(self):
        """Test estimated completion time update."""
        import time

        start_time = time.time() - 10.0  # 10 seconds ago
        progress = PipelineProgress(
            total_documents=10,
            processed_documents=5,
            start_time=start_time,
        )
        progress.update_estimated_completion()
        assert progress.estimated_completion is not None
        assert progress.estimated_completion > time.time()


class TestPipelineResult:
    """Test PipelineResult dataclass functionality."""

    def test_is_complete_completed(self):
        """Test is_complete property for completed status."""
        progress = PipelineProgress()
        result = PipelineResult(pipeline_id="test", status=PipelineStatus.COMPLETED, progress=progress)
        assert result.is_complete is True

    def test_is_complete_failed(self):
        """Test is_complete property for failed status."""
        progress = PipelineProgress()
        result = PipelineResult(pipeline_id="test", status=PipelineStatus.FAILED, progress=progress)
        assert result.is_complete is True

    def test_is_complete_processing(self):
        """Test is_complete property for processing status."""
        progress = PipelineProgress()
        result = PipelineResult(pipeline_id="test", status=PipelineStatus.PROCESSING, progress=progress)
        assert result.is_complete is False

    def test_total_chunks_calculation(self):
        """Test total chunks calculation."""
        progress = PipelineProgress()
        result = PipelineResult(
            pipeline_id="test",
            status=PipelineStatus.COMPLETED,
            progress=progress,
            results=[
                {"total_chunks": 5},
                {"total_chunks": 3},
                {"total_chunks": 2},
            ],
        )
        assert result.total_chunks == 10

    def test_total_processing_time_calculation(self):
        """Test total processing time calculation."""
        progress = PipelineProgress()
        result = PipelineResult(
            pipeline_id="test",
            status=PipelineStatus.COMPLETED,
            progress=progress,
            results=[
                {"processing_time_ms": 1000},
                {"processing_time_ms": 2000},
                {"processing_time_ms": 3000},
            ],
        )
        assert result.total_processing_time == 6.0

    def test_elapsed_time_property(self):
        """Test elapsed_time property."""
        import time

        start_time = time.time() - 5.0
        progress = PipelineProgress(start_time=start_time)
        result = PipelineResult(
            pipeline_id="test",
            status=PipelineStatus.COMPLETED,
            progress=progress,
        )
        assert abs(result.elapsed_time - 5.0) < 0.1


class TestStandardizedIngestionPipeline:
    """Test StandardizedIngestionPipeline functionality."""

    @pytest.fixture
    def pipeline(self):
        """Create a pipeline instance for testing."""
        return StandardizedIngestionPipeline(
            chunk_size=300,
            chunk_overlap=50,
            max_concurrent=3,
            batch_size=5,
        )

    def test_initialization(self, pipeline):
        """Test pipeline initialization."""
        assert pipeline.chunk_size == 300
        assert pipeline.chunk_overlap == 50
        assert pipeline.max_concurrent == 3
        assert pipeline.batch_size == 5
        assert pipeline.enable_progress_tracking is True
        assert len(pipeline.active_pipelines) == 0
        assert len(pipeline.pipeline_history) == 0

    def test_forward_single_document(self, pipeline):
        """Test processing a single document."""
        # Mock the processor's forward method to avoid real processing
        mock_result = {
            "chunks": [{"text": "test chunk"}],
            "total_chunks": 1,
            "processing_time_ms": 100,
            "metadata": {"content_type": "text/plain"},
        }

        with patch.object(pipeline.processor, "forward", return_value=mock_result):
            result = pipeline("test_document.txt")

        assert result.status == PipelineStatus.COMPLETED
        assert result.progress.total_documents == 1
        assert result.progress.processed_documents == 1
        assert result.progress.successful_documents == 1
        assert result.progress.failed_documents == 0
        assert len(result.results) == 1
        assert len(result.errors) == 0

    def test_forward_multiple_documents(self, pipeline):
        """Test processing multiple documents."""
        # Mock the processor's forward method to avoid real processing
        mock_result = {
            "chunks": [{"text": "test chunk"}],
            "total_chunks": 1,
            "processing_time_ms": 100,
            "metadata": {"content_type": "text/plain"},
        }

        with patch.object(pipeline.processor, "forward", return_value=mock_result):
            result = pipeline(["doc1.txt", "doc2.txt", "doc3.txt"])

        assert result.status == PipelineStatus.COMPLETED
        assert result.progress.total_documents == 3
        assert result.progress.processed_documents == 3
        assert result.progress.successful_documents == 3
        assert result.progress.failed_documents == 0
        assert len(result.results) == 3
        assert len(result.errors) == 0

    def test_forward_with_vector_store(self, pipeline):
        """Test processing with vector store integration."""
        # Mock the processor
        mock_result = {
            "chunks": [{"text": "test chunk"}],
            "total_chunks": 1,
            "processing_time_ms": 100,
            "metadata": {"content_type": "text/plain"},
        }

        # Mock vector store
        mock_vector_store = Mock()
        mock_vector_store.return_value = {"status": "success"}

        with patch.object(pipeline.processor, "forward", return_value=mock_result):
            result = pipeline("test_document.txt", vector_store=mock_vector_store)

        assert result.status == PipelineStatus.COMPLETED
        assert len(result.errors) == 0
        # Verify vector store was called
        mock_vector_store.assert_called_once()

    def test_forward_vector_store_error(self, pipeline):
        """Test handling of vector store errors."""
        # Mock the processor
        mock_result = {
            "chunks": [{"text": "test chunk"}],
            "total_chunks": 1,
            "processing_time_ms": 100,
            "metadata": {"content_type": "text/plain"},
        }

        # Mock vector store with error
        mock_vector_store = Mock()
        mock_vector_store.return_value = {"status": "error", "error": "Storage failed"}

        with patch.object(pipeline.processor, "forward", return_value=mock_result):
            result = pipeline("test_document.txt", vector_store=mock_vector_store)

        assert result.status == PipelineStatus.COMPLETED
        assert len(result.errors) == 1
        assert "Storage failed" in result.errors[0]["error"]

    def test_forward_processing_error(self, pipeline):
        """Test handling of document processing errors."""
        # Mock the processor to raise an exception
        with patch.object(pipeline.processor, "forward", side_effect=Exception("Processing failed")):
            result = pipeline("test_document.txt")

        assert result.status == PipelineStatus.COMPLETED  # Pipeline continues despite errors
        assert result.progress.total_documents == 1
        assert result.progress.processed_documents == 1
        assert result.progress.successful_documents == 0
        assert result.progress.failed_documents == 1
        assert len(result.results) == 0
        assert len(result.errors) == 1
        assert "Processing failed" in result.errors[0]["error"]

    def test_forward_with_custom_pipeline_id(self, pipeline):
        """Test processing with custom pipeline ID."""
        mock_result = {
            "chunks": [{"text": "test chunk"}],
            "total_chunks": 1,
            "processing_time_ms": 100,
            "metadata": {"content_type": "text/plain"},
        }

        with patch.object(pipeline.processor, "forward", return_value=mock_result):
            result = pipeline("test_document.txt", pipeline_id="custom_pipeline_123")

        assert result.pipeline_id == "custom_pipeline_123"
        assert result.status == PipelineStatus.COMPLETED

    def test_get_pipeline_status(self, pipeline):
        """Test getting pipeline status."""
        # Process a document to create an active pipeline
        mock_result = {
            "chunks": [{"text": "test chunk"}],
            "total_chunks": 1,
            "processing_time_ms": 100,
            "metadata": {"content_type": "text/plain"},
        }

        with patch.object(pipeline.processor, "forward", return_value=mock_result):
            pipeline("test_document.txt", pipeline_id="test_pipeline")

        # Pipeline should be in history, not active
        status = pipeline.get_pipeline_status("test_pipeline")
        assert status is None

    def test_get_pipeline_history(self, pipeline):
        """Test getting pipeline history."""
        # Process multiple documents
        mock_result = {
            "chunks": [{"text": "test chunk"}],
            "total_chunks": 1,
            "processing_time_ms": 100,
            "metadata": {"content_type": "text/plain"},
        }

        with patch.object(pipeline.processor, "forward", return_value=mock_result):
            pipeline("doc1.txt")
            pipeline("doc2.txt")
            pipeline("doc3.txt")

        history = pipeline.get_pipeline_history()
        assert len(history) == 3

        # Test with limit
        limited_history = pipeline.get_pipeline_history(limit=2)
        assert len(limited_history) == 2

    def test_get_pipeline_stats(self, pipeline):
        """Test getting pipeline statistics."""
        # Process some documents
        mock_result = {
            "chunks": [{"text": "test chunk"}],
            "total_chunks": 1,
            "processing_time_ms": 100,
            "metadata": {"content_type": "text/plain"},
        }

        with patch.object(pipeline.processor, "forward", return_value=mock_result):
            pipeline("doc1.txt")
            pipeline("doc2.txt")

        stats = pipeline.get_pipeline_stats()
        assert stats["total_pipelines"] == 2
        assert stats["successful_pipelines"] == 2
        assert stats["failed_pipelines"] == 0
        assert stats["total_documents_processed"] == 2
        assert stats["total_chunks_generated"] == 2
        assert stats["success_rate"] == 100.0
        assert stats["active_pipelines"] == 0

    def test_cancel_pipeline(self, pipeline):
        """Test canceling a pipeline."""
        # Create a mock active pipeline
        mock_progress = PipelineProgress()
        mock_result = PipelineResult(
            pipeline_id="test_pipeline",
            status=PipelineStatus.PROCESSING,
            progress=mock_progress,
        )
        pipeline.active_pipelines["test_pipeline"] = mock_result

        # Cancel the pipeline
        success = pipeline.cancel_pipeline("test_pipeline")
        assert success is True
        assert "test_pipeline" not in pipeline.active_pipelines
        assert mock_result.status == PipelineStatus.CANCELLED

        # Try to cancel non-existent pipeline
        success = pipeline.cancel_pipeline("non_existent")
        assert success is False

    def test_cleanup(self, pipeline):
        """Test pipeline cleanup."""
        # Create mock active pipelines
        mock_progress = PipelineProgress()
        mock_result = PipelineResult(
            pipeline_id="test_pipeline",
            status=PipelineStatus.PROCESSING,
            progress=mock_progress,
        )
        pipeline.active_pipelines["test_pipeline"] = mock_result

        # Mock processor cleanup
        with patch.object(pipeline.processor, "cleanup") as mock_cleanup:
            pipeline.cleanup()
            mock_cleanup.assert_called_once()

        # Verify active pipelines were cancelled
        assert len(pipeline.active_pipelines) == 0

    def test_batch_processing_edge_cases(self, pipeline):
        """Test batch processing with edge cases."""
        # Test empty document list
        mock_result = {
            "chunks": [{"text": "test chunk"}],
            "total_chunks": 1,
            "processing_time_ms": 100,
            "metadata": {"content_type": "text/plain"},
        }

        with patch.object(pipeline.processor, "forward", return_value=mock_result):
            result = pipeline([])

        assert result.status == PipelineStatus.COMPLETED
        assert result.progress.total_documents == 0
        assert result.progress.processed_documents == 0

    def test_progress_tracking_disabled(self):
        """Test pipeline with progress tracking disabled."""
        pipeline = StandardizedIngestionPipeline(enable_progress_tracking=False)

        mock_result = {
            "chunks": [{"text": "test chunk"}],
            "total_chunks": 1,
            "processing_time_ms": 100,
            "metadata": {"content_type": "text/plain"},
        }

        with patch.object(pipeline.processor, "forward", return_value=mock_result):
            result = cast(PipelineResult, pipeline("test_document.txt"))

        assert result.status == PipelineStatus.COMPLETED
        # Progress tracking should still work, but estimated completion won't be updated
        assert result.progress.estimated_completion is None
