#!/usr/bin/env python3
"""
Standardized Document Ingestion Pipeline
Provides consistent processing workflow across all document sources and types.
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from dspy import Module

from .mcp_document_processor import MCPDocumentProcessor


class PipelineStatus(Enum):
    """Pipeline processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PipelineProgress:
    """Progress tracking for pipeline operations."""

    total_documents: int = 0
    processed_documents: int = 0
    successful_documents: int = 0
    failed_documents: int = 0
    current_document: Optional[str] = None
    start_time: Optional[float] = None
    estimated_completion: Optional[float] = None
    status: PipelineStatus = PipelineStatus.PENDING

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_documents == 0:
            return 0.0
        return (self.processed_documents / self.total_documents) * 100

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.processed_documents == 0:
            return 0.0
        return (self.successful_documents / self.processed_documents) * 100

    @property
    def elapsed_time(self) -> float:
        """Calculate elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time

    def update_estimated_completion(self) -> None:
        """Update estimated completion time based on current progress."""
        if self.processed_documents > 0 and self.start_time is not None:
            avg_time_per_doc = self.elapsed_time / self.processed_documents
            remaining_docs = self.total_documents - self.processed_documents
            self.estimated_completion = time.time() + (avg_time_per_doc * remaining_docs)


@dataclass
class PipelineResult:
    """Result of pipeline processing."""

    pipeline_id: str
    status: PipelineStatus
    progress: PipelineProgress
    results: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_complete(self) -> bool:
        """Check if pipeline processing is complete."""
        return self.status in [PipelineStatus.COMPLETED, PipelineStatus.FAILED, PipelineStatus.CANCELLED]

    @property
    def total_chunks(self) -> int:
        """Get total number of chunks processed."""
        return sum(result.get("total_chunks", 0) for result in self.results)

    @property
    def total_processing_time(self) -> float:
        """Get total processing time in seconds."""
        return sum(result.get("processing_time_ms", 0) for result in self.results) / 1000.0

    @property
    def elapsed_time(self) -> float:
        """Get elapsed time from progress."""
        return self.progress.elapsed_time


class StandardizedIngestionPipeline(Module):
    """Standardized document ingestion pipeline with progress tracking and batch processing."""

    def __init__(
        self,
        chunk_size: int = 300,
        chunk_overlap: int = 50,
        mcp_timeout: int = 30,
        enable_cache: bool = True,
        max_concurrent: int = 5,
        batch_size: int = 10,
        enable_progress_tracking: bool = True,
    ):
        super().__init__()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.mcp_timeout = mcp_timeout
        self.enable_cache = enable_cache
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.enable_progress_tracking = enable_progress_tracking

        # Initialize MCP processor
        self.processor = MCPDocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            mcp_timeout=mcp_timeout,
            enable_cache=enable_cache,
        )

        # Pipeline state
        self.active_pipelines: Dict[str, PipelineResult] = {}
        self.pipeline_history: List[PipelineResult] = []

        # Performance monitoring
        self.pipeline_stats = {
            "total_pipelines": 0,
            "successful_pipelines": 0,
            "failed_pipelines": 0,
            "total_documents_processed": 0,
            "total_chunks_generated": 0,
            "average_processing_time": 0.0,
        }

    def forward(
        self,
        document_sources: Union[str, List[str]],
        vector_store: Optional[Any] = None,
        pipeline_id: Optional[str] = None,
        **kwargs,
    ) -> PipelineResult:
        """Process documents through standardized pipeline."""

        # Normalize input to list
        if isinstance(document_sources, str):
            document_sources = [document_sources]

        # Generate pipeline ID if not provided
        if pipeline_id is None:
            pipeline_id = f"pipeline_{uuid.uuid4().hex}"

        # Initialize pipeline result
        progress = PipelineProgress(
            total_documents=len(document_sources),
            start_time=time.time(),
            status=PipelineStatus.PROCESSING,
        )

        pipeline_result = PipelineResult(
            pipeline_id=pipeline_id,
            status=PipelineStatus.PROCESSING,
            progress=progress,
            metadata={
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "max_concurrent": self.max_concurrent,
                "batch_size": self.batch_size,
                "enable_cache": self.enable_cache,
            },
        )

        # Track active pipeline
        self.active_pipelines[pipeline_id] = pipeline_result

        try:
            # Process documents
            if len(document_sources) == 1:
                # Single document processing
                self._process_single_document(document_sources[0], vector_store, pipeline_result, **kwargs)
            else:
                # Batch processing
                self._process_batch_documents(document_sources, vector_store, pipeline_result, **kwargs)

            # Update final status
            pipeline_result.status = PipelineStatus.COMPLETED
            pipeline_result.progress.status = PipelineStatus.COMPLETED

            # Update pipeline statistics
            self._update_pipeline_stats(pipeline_result, success=True)

            return pipeline_result

        except Exception as e:
            # Handle pipeline failure
            pipeline_result.status = PipelineStatus.FAILED
            pipeline_result.progress.status = PipelineStatus.FAILED
            pipeline_result.errors.append(
                {
                    "error": str(e),
                    "document_source": "pipeline",
                    "timestamp": time.time(),
                }
            )

            # Update pipeline statistics
            self._update_pipeline_stats(pipeline_result, success=False)

            raise

        finally:
            # Cleanup and archive
            if pipeline_id in self.active_pipelines:
                del self.active_pipelines[pipeline_id]
            self.pipeline_history.append(pipeline_result)

    def _process_single_document(
        self, document_source: str, vector_store: Optional[Any], pipeline_result: PipelineResult, **kwargs
    ) -> None:
        """Process a single document."""
        try:
            # Update progress
            pipeline_result.progress.current_document = document_source
            pipeline_result.progress.processed_documents += 1

            # Process document
            result = self.processor(document_source, **kwargs)

            # Store in vector database if provided
            if vector_store and hasattr(vector_store, "store_chunks"):
                try:
                    chunk_texts = [chunk["text"] for chunk in result["chunks"]]
                    store_result = vector_store("store_chunks", chunks=chunk_texts, metadata=result["metadata"])
                    if store_result.get("status") != "success":
                        raise Exception(f"Vector store error: {store_result.get('error', 'Unknown error')}")
                except Exception as e:
                    pipeline_result.errors.append(
                        {
                            "error": str(e),
                            "document_source": document_source,
                            "stage": "vector_store",
                            "timestamp": time.time(),
                        }
                    )

            # Add to results
            pipeline_result.results.append(result)
            pipeline_result.progress.successful_documents += 1

        except Exception as e:
            # Handle document processing failure
            pipeline_result.progress.failed_documents += 1
            pipeline_result.errors.append(
                {
                    "error": str(e),
                    "document_source": document_source,
                    "stage": "processing",
                    "timestamp": time.time(),
                }
            )

            # Continue processing other documents
            if self.enable_progress_tracking:
                pipeline_result.progress.update_estimated_completion()

    def _process_batch_documents(
        self, document_sources: List[str], vector_store: Optional[Any], pipeline_result: PipelineResult, **kwargs
    ) -> None:
        """Process multiple documents in batches."""

        # Process in batches
        for i in range(0, len(document_sources), self.batch_size):
            batch = document_sources[i : i + self.batch_size]

            # Process batch sequentially for now (can be enhanced with threading later)
            for doc_source in batch:
                self._process_single_document(doc_source, vector_store, pipeline_result, **kwargs)

            # Update progress
            if self.enable_progress_tracking:
                pipeline_result.progress.update_estimated_completion()

    def _update_pipeline_stats(self, pipeline_result: PipelineResult, success: bool) -> None:
        """Update pipeline statistics."""
        self.pipeline_stats["total_pipelines"] += 1

        if success:
            self.pipeline_stats["successful_pipelines"] += 1
        else:
            self.pipeline_stats["failed_pipelines"] += 1

        self.pipeline_stats["total_documents_processed"] += pipeline_result.progress.processed_documents
        self.pipeline_stats["total_chunks_generated"] += pipeline_result.total_chunks

        # Update average processing time
        if self.pipeline_stats["total_pipelines"] > 0:
            total_time = sum(p.elapsed_time for p in self.pipeline_history)
            self.pipeline_stats["average_processing_time"] = total_time / self.pipeline_stats["total_pipelines"]

    def get_pipeline_status(self, pipeline_id: str) -> Optional[PipelineResult]:
        """Get status of a specific pipeline."""
        return self.active_pipelines.get(pipeline_id)

    def get_pipeline_history(self, limit: Optional[int] = None) -> List[PipelineResult]:
        """Get pipeline history."""
        history = self.pipeline_history.copy()
        if limit:
            history = history[-limit:]
        return history

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        stats = self.pipeline_stats.copy()

        # Calculate success rate
        if stats["total_pipelines"] > 0:
            stats["success_rate"] = (stats["successful_pipelines"] / stats["total_pipelines"]) * 100
        else:
            stats["success_rate"] = 0.0

        # Add active pipeline count
        stats["active_pipelines"] = len(self.active_pipelines)

        return stats

    def cancel_pipeline(self, pipeline_id: str) -> bool:
        """Cancel an active pipeline."""
        if pipeline_id in self.active_pipelines:
            pipeline_result = self.active_pipelines[pipeline_id]
            pipeline_result.status = PipelineStatus.CANCELLED
            pipeline_result.progress.status = PipelineStatus.CANCELLED
            del self.active_pipelines[pipeline_id]
            return True
        return False

    def cleanup(self) -> None:
        """Cleanup pipeline resources."""
        # Cancel all active pipelines
        for pipeline_id in list(self.active_pipelines.keys()):
            self.cancel_pipeline(pipeline_id)

        # Cleanup processor
        self.processor.cleanup()
