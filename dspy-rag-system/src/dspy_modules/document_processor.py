#!/usr/bin/env python3
# ANCHOR_KEY: document-processor
# ANCHOR_PRIORITY: 30
# ROLE_PINS: ["implementer", "coder"]
"""
DocumentProcessor DSPy Module
Handles document ingestion, text extraction, and chunking for the RAG system.
"""

import csv
import json
import os

# Import our new utilities
import sys
import time
import uuid
from pathlib import Path
from typing import Any

try:
    import fitz  # PyMuPDF - better than PyPDF2
except ImportError:
    fitz = None  # type: ignore
import pandas as pd
from dspy import Module

sys.path.append("src")
from utils.anchor_metadata_parser import extract_anchor_metadata
from utils.logger import get_logger
from utils.metadata_extractor import ConfigDrivenMetadataExtractor
from utils.smart_chunker import create_smart_chunker


class DocumentProcessor(Module):
    """DSPy module for processing documents and creating chunks"""

    def __init__(
        self,
        chunk_size: int = 300,
        chunk_overlap: int = 50,
        config_path: str = "config/metadata_rules.yaml",
        allowed_paths: list[str] | None = None,
    ):
        super().__init__()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.allowed_paths = allowed_paths or ["."]  # Default to current directory

        # Initialize structured logging (use singleton factory)
        self.logger = get_logger("document_processor")

        # Initialize smart code-aware chunker
        self.chunker = create_smart_chunker(
            max_tokens=chunk_size, overlap_tokens=chunk_overlap, preserve_code_units=True, enable_stitching=True
        )

        # Initialize config-driven metadata extractor
        self.metadata_extractor = ConfigDrivenMetadataExtractor(config_path)

        self.logger.info("DocumentProcessor initialized with token-aware chunking and config-driven metadata")

    def forward(self, document_path: str) -> dict[str, Any]:
        """Process a document and return chunks with metadata"""

        start_time = time.perf_counter_ns()
        document_id = f"doc_{uuid.uuid4().hex}"  # Use UUID to prevent collisions

        try:
            # Security check: validate file path
            self._validate_file_path(document_path)

            self.logger.info(
                "Starting document processing",
                extra={"document_id": document_id, "stage": "start", "file_path": self._mask_file_path(document_path)},
            )

            # Extract text from document
            self.logger.info(
                "Extracting text from document", extra={"document_id": document_id, "stage": "text_extraction"}
            )

            text = self._extract_text(document_path)

            # Create chunks using token-aware chunking
            self.logger.info(
                "Creating chunks using token-aware chunking", extra={"document_id": document_id, "stage": "chunking"}
            )

            chunks, chunk_stats = self._create_structured_chunks(text, document_id)

            # Extract enhanced metadata using config-driven approach
            self.logger.info(
                "Extracting metadata using config-driven rules",
                extra={"document_id": document_id, "stage": "metadata_extraction"},
            )

            metadata = self.metadata_extractor.extract_metadata(document_path, text)

            # Add chunk statistics to metadata
            metadata.update(
                {
                    "total_chunks": len(chunks),
                    "chunk_stats": chunk_stats,
                    "processing_time_ms": int((time.perf_counter_ns() - start_time) // 1_000_000),
                }
            )

            self.logger.info(
                "Document processing completed successfully",
                extra={
                    "document_id": document_id,
                    "stage": "complete",
                    "chunk_count": len(chunks),
                    "file_size": metadata.get("file_size", 0),
                    "elapsed_ms": metadata["processing_time_ms"],
                },
            )

            return {
                "chunks": chunks,
                "metadata": metadata,
                "document_path": document_path,
                "total_chunks": len(chunks),
                "document_id": document_id,
            }

        except Exception as e:
            self.logger.exception(
                "Document processing failed",
                extra={
                    "document_id": document_id,
                    "stage": "error",
                    "error": str(e),
                    "file_path": self._mask_file_path(document_path),
                },
            )
            raise

    def _validate_file_path(self, document_path: str) -> None:
        """Validate file path for security and accessibility"""
        path = Path(document_path).resolve()

        # Check if path is within allowed directories
        is_allowed = False
        for allowed_path in self.allowed_paths:
            try:
                if path.is_relative_to(Path(allowed_path).resolve()):
                    is_allowed = True
                    break
            except ValueError:
                continue

        if not is_allowed:
            raise ValueError(f"File path {document_path} is not within allowed directories")

        # Check if file exists and is accessible
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {document_path}")

        # Check file size (prevent processing extremely large files)
        try:
            file_size = path.stat().st_size
            if file_size > 500 * 1024 * 1024:  # 500MB limit
                raise ValueError(f"File too large: {file_size} bytes")
        except OSError as e:
            raise OSError(f"Cannot access file {document_path}: {e}")

    def _mask_file_path(self, file_path: str) -> str:
        """Mask file path for logging to prevent information leakage"""
        path = Path(file_path)
        return f"{path.parent.name}/{path.name}" if path.parent.name else path.name

    def _create_structured_chunks(self, text: str, document_id: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Create structured chunks with IDs and token offsets"""
        chunks = []
        # Use smart chunking with file path for context
        chunk_data = self.chunker.create_smart_chunks(text, document_id)
        chunk_texts = [chunk["text"] for chunk in chunk_data]

        # Get token statistics efficiently from base chunker
        chunk_stats = self.chunker.base_chunker.get_chunk_stats(text)

        for idx, chunk_text in enumerate(chunk_texts):
            chunk_id = f"{document_id}_chunk_{idx}"

            # Calculate approximate token offsets (this is an estimate)
            start_token = idx * self.chunk_size
            end_token = start_token + len(self.chunker.base_chunker.encoder.encode(chunk_text))

            # Extract anchor metadata from chunk content
            anchor_metadata = extract_anchor_metadata(chunk_text)

            # Create chunk with anchor metadata
            chunk = {
                "id": chunk_id,
                "text": chunk_text,
                "start_token": start_token,
                "end_token": end_token,
                "chunk_index": idx,
                "document_id": document_id,
            }

            # Add anchor metadata if present
            if anchor_metadata.anchor_key or anchor_metadata.anchor_priority is not None or anchor_metadata.role_pins:
                chunk["metadata"] = anchor_metadata.to_dict()

            chunks.append(chunk)

        return chunks, chunk_stats

    def _extract_text(self, document_path: str) -> str:
        """Extract text from different document types"""
        path = Path(document_path)
        file_extension = path.suffix.lower()

        if file_extension == ".pdf":
            return self._extract_pdf_text(document_path)
        elif file_extension in [".txt", ".md"]:
            return self._extract_text_file(document_path)
        elif file_extension == ".csv":
            return self._extract_csv_text(document_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF file using PyMuPDF (fitz)"""
        if fitz is None:
            raise ImportError("PyMuPDF (fitz) is not installed. Please install it with: pip install PyMuPDF")

        try:
            doc = fitz.open(pdf_path)  # type: ignore[attr-defined]
            text_parts = []

            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                if page_text:
                    text_parts.append(page_text)
                else:
                    # Log empty pages but continue processing
                    self.logger.warning(
                        f"Page {page_num + 1} has no extractable text",
                        extra={"file_path": self._mask_file_path(pdf_path), "page_num": page_num + 1},
                    )

            doc.close()

            text = "\n".join(text_parts)

            if not text.strip():
                raise ValueError("No extractable text found in PDF; consider OCR for scanned documents")

            return text

        except Exception as e:
            self.logger.error(
                f"Error reading PDF file: {e}",
                extra={"file_path": self._mask_file_path(pdf_path), "error_type": type(e).__name__},
            )
            raise Exception(f"Error reading PDF file: {e}")

    def _extract_text_file(self, file_path: str) -> str:
        """Extract text from text files with encoding handling"""
        try:
            # Try UTF-8 first
            with open(file_path, encoding="utf-8") as file:
                return file.read()
        except UnicodeDecodeError:
            # Fallback to other encodings
            for encoding in ["latin-1", "cp1252", "iso-8859-1"]:
                try:
                    with open(file_path, encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue

            # Last resort: read with error replacement
            try:
                with open(file_path, encoding="utf-8", errors="replace") as file:
                    return file.read()
            except Exception as e:
                self.logger.error(f"Error reading text file: {e}", extra={"file_path": self._mask_file_path(file_path)})
                raise Exception(f"Error reading text file: {e}")

    def _extract_csv_text(self, csv_path: str) -> str:
        """Extract text from CSV file with streaming for large files"""
        try:
            # First, try to determine file size
            file_size = Path(csv_path).stat().st_size

            # For large files (>10MB), use streaming approach
            if file_size > 10 * 1024 * 1024:
                return self._extract_csv_text_streaming(csv_path)
            else:
                return self._extract_csv_text_pandas(csv_path)

        except Exception:
            # Fallback to basic CSV reading
            return self._extract_csv_text_basic(csv_path)

    def _extract_csv_text_pandas(self, csv_path: str) -> str:
        """Extract CSV text using pandas (for smaller files)"""
        try:
            df = pd.read_csv(csv_path)

            text_parts = []

            # Add column headers
            text_parts.append("Columns: " + ", ".join(df.columns.tolist()))
            text_parts.append(f"Total rows: {len(df)}")
            text_parts.append("")

            # Add first few rows as examples
            text_parts.append("Sample data:")
            for idx, (i, row) in enumerate(df.head(10).iterrows(), 1):
                row_text = f"Row {idx}: " + ", ".join([f"{col}={val}" for col, val in row.items()])
                text_parts.append(row_text)

            # Add summary statistics for numeric columns
            numeric_cols = df.select_dtypes(include=["number"]).columns
            if len(numeric_cols) > 0:
                text_parts.append("")
                text_parts.append("Summary statistics:")
                for col in numeric_cols:
                    text_parts.append(f"{col}: min={df[col].min()}, max={df[col].max()}, mean={df[col].mean():.2f}")

            return "\n".join(text_parts)

        except Exception as e:
            self.logger.warning(
                f"Pandas CSV extraction failed: {e}", extra={"file_path": self._mask_file_path(csv_path)}
            )
            raise

    def _extract_csv_text_streaming(self, csv_path: str) -> str:
        """Extract CSV text using streaming approach for large files"""
        try:
            text_parts = []

            # Read CSV in chunks
            chunk_iter = pd.read_csv(csv_path, chunksize=50000)

            # Get first chunk for headers and sample
            first_chunk = next(chunk_iter)
            text_parts.append("Columns: " + ", ".join(first_chunk.columns.tolist()))

            # Count total rows (approximate)
            row_count = len(first_chunk)
            for chunk in chunk_iter:
                row_count += len(chunk)

            text_parts.append(f"Total rows: {row_count}")
            text_parts.append("")

            # Add sample from first chunk
            text_parts.append("Sample data:")
            for idx, (i, row) in enumerate(first_chunk.head(10).iterrows(), 1):
                row_text = f"Row {idx}: " + ", ".join([f"{col}={val}" for col, val in row.items()])
                text_parts.append(row_text)

            # Add summary statistics for numeric columns
            numeric_cols = first_chunk.select_dtypes(include=["number"]).columns
            if len(numeric_cols) > 0:
                text_parts.append("")
                text_parts.append("Summary statistics (from first chunk):")
                for col in numeric_cols:
                    min_val = first_chunk[col].min()
                    max_val = first_chunk[col].max()
                    mean_val = first_chunk[col].mean()
                    text_parts.append(f"{col}: min={min_val}, max={max_val}, mean={mean_val:.2f}")

            return "\n".join(text_parts)

        except Exception as e:
            self.logger.warning(
                f"Streaming CSV extraction failed: {e}", extra={"file_path": self._mask_file_path(csv_path)}
            )
            raise

    def _extract_csv_text_basic(self, csv_path: str) -> str:
        """Fallback CSV extraction using basic csv module"""
        try:
            with open(csv_path, encoding="utf-8") as file:
                csv_reader = csv.reader(file)
                rows = list(csv_reader)

                text_parts = []
                if rows:
                    text_parts.append("Headers: " + ", ".join(rows[0]))
                    text_parts.append(f"Total rows: {len(rows)}")
                    text_parts.append("")
                    text_parts.append("Sample data:")
                    for i, row in enumerate(rows[1:11]):  # First 10 data rows
                        text_parts.append(f"Row {i+1}: " + ", ".join(row))

                return "\n".join(text_parts)

        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}", extra={"file_path": self._mask_file_path(csv_path)})
            raise Exception(f"Error reading CSV file: {e}")


class DocumentIngestionPipeline(Module):
    """DSPy module for complete document ingestion pipeline"""

    def __init__(self, config_path: str = "config/metadata_rules.yaml", allowed_paths: list[str] | None = None):
        super().__init__()
        self.processor = DocumentProcessor(config_path=config_path, allowed_paths=allowed_paths)
        self.logger = get_logger("document_pipeline")

    def forward(self, document_path: str, vector_store: Any = None) -> dict[str, Any]:
        """Complete document ingestion pipeline"""

        start_time = time.perf_counter_ns()

        try:
            self.logger.info(
                "Starting document ingestion pipeline",
                extra={"file_path": self.processor._mask_file_path(document_path), "stage": "pipeline_start"},
            )

            # Process document
            result: Any = self.processor(document_path)

            # Store in vector database (if provided)
            if vector_store and hasattr(vector_store, "forward"):
                try:
                    # Extract chunk texts for storage
                    chunks = result.get("chunks", [])
                    chunk_texts = [chunk.get("text", "") for chunk in chunks if isinstance(chunk, dict)]
                    metadata = result.get("metadata", {})
                    vector_store.forward("store_chunks", chunks=chunk_texts, metadata=metadata)
                    self.logger.info(
                        "Chunks stored in vector database",
                        extra={
                            "document_id": result.get("document_id", "unknown"),
                            "chunks_stored": result.get("total_chunks", 0),
                        },
                    )
                except Exception as e:
                    self.logger.error(
                        "Failed to store chunks in vector database",
                        extra={"document_id": result.get("document_id", "unknown"), "error": str(e)},
                    )
                    # Continue processing even if vector storage fails

            processing_time = int((time.perf_counter_ns() - start_time) // 1_000_000)

            self.logger.info(
                "Document ingestion pipeline completed",
                extra={
                    "document_id": result.get("document_id", "unknown"),
                    "stage": "pipeline_complete",
                    "chunks_created": result.get("total_chunks", 0),
                    "elapsed_ms": processing_time,
                },
            )

            return {
                "status": "success",
                "document_path": document_path,
                "chunks_created": result.get("total_chunks", 0),
                "metadata": result.get("metadata", {}),
                "processing_time_ms": processing_time,
                "document_id": result.get("document_id", "unknown"),
            }

        except Exception as e:
            self.logger.exception(
                "Document ingestion pipeline failed",
                extra={
                    "file_path": self.processor._mask_file_path(document_path),
                    "stage": "pipeline_error",
                    "error": str(e),
                },
            )
            raise


# Example usage and testing
if __name__ == "__main__":
    # Test the document processor
    processor = DocumentProcessor()

    # Test with a sample text file
    test_file = "test_document.txt"
    with open(test_file, "w") as f:
        f.write("This is a test document. " * 100)  # Create a test document

    try:
        result: Any = processor(test_file)
        print(f"Processed document: {result.get('total_chunks', 0)} chunks created")
        chunks = result.get("chunks", [])
        if chunks and isinstance(chunks[0], dict):
            print(f"First chunk: {chunks[0].get('text', '')[:100]}...")
        print(f"Enhanced metadata: {json.dumps(result.get('metadata', {}), indent=2)}")
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
