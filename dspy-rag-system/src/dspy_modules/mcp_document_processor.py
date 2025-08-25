#!/usr/bin/env python3
# ANCHOR_KEY: mcp-document-processor
# ANCHOR_PRIORITY: 35
# ROLE_PINS: ["implementer", "coder"]
"""
MCP Document Processor DSPy Module
Extends DocumentProcessor with MCP integration layer for unified document processing.
"""

import asyncio
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from dspy import Module

sys.path.append("src")
from utils.logger import get_logger
from utils.mcp_integration import (
    FileSystemMCPServer,
    GitHubMCPServer,
    MCPConfig,
    PDFMCPServer,
    WebMCPServer,
)


class MCPDocumentProcessor(Module):
    """DSPy module for MCP-based document processing with unified interface"""

    def __init__(
        self,
        chunk_size: int = 300,
        chunk_overlap: int = 50,
        config_path: str = "config/metadata_rules.yaml",
        allowed_paths: Optional[List[str]] = None,
        mcp_timeout: int = 30,
        enable_cache: bool = True,
    ):
        super().__init__()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.allowed_paths = allowed_paths or ["."]
        self.mcp_timeout = mcp_timeout
        self.enable_cache = enable_cache

        # Initialize structured logging
        self.logger = get_logger("mcp_document_processor")

        # Initialize MCP servers
        self._initialize_mcp_servers()

        # Performance monitoring
        self.processing_stats = {
            "total_documents": 0,
            "successful_documents": 0,
            "failed_documents": 0,
            "total_processing_time": 0.0,
            "server_usage": {
                "file_system": 0,
                "web": 0,
                "pdf": 0,
                "github": 0,
            },
        }

        self.logger.info("MCPDocumentProcessor initialized with MCP integration layer")

    def _initialize_mcp_servers(self) -> None:
        """Initialize all MCP servers with appropriate configuration"""
        try:
            # Base configuration for all servers
            base_config = MCPConfig(
                server_name="mcp_document_processor",
                timeout=self.mcp_timeout,
                max_file_size=100 * 1024 * 1024,  # 100MB
                cache_enabled=self.enable_cache,
            )

            # Initialize individual servers
            self.file_system_server = FileSystemMCPServer(base_config)
            self.web_server = WebMCPServer(base_config)
            self.pdf_server = PDFMCPServer(base_config)
            self.github_server = GitHubMCPServer(base_config)

            # Create server registry for routing
            self.server_registry = {
                "file_system": self.file_system_server,
                "web": self.web_server,
                "pdf": self.pdf_server,
                "github": self.github_server,
            }

            self.logger.info("MCP servers initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize MCP servers: {e}")
            raise

    def forward(self, document_source: str, **kwargs) -> Dict[str, Any]:
        """Process a document using appropriate MCP server based on source type"""
        start_time = time.perf_counter_ns()
        document_id = f"mcp_doc_{uuid.uuid4().hex}"

        try:
            self.logger.info(
                "Starting MCP document processing",
                extra={
                    "document_id": document_id,
                    "stage": "start",
                    "source": self._mask_source(document_source),
                },
            )

            # Determine appropriate server and route document
            server_type, server = self._route_document(document_source)

            self.logger.info(
                "Document routed to MCP server",
                extra={
                    "document_id": document_id,
                    "stage": "routing",
                    "server_type": server_type,
                    "source": self._mask_source(document_source),
                },
            )

            # Process document using selected server
            result = asyncio.run(self._process_with_server(server, document_source, document_id, **kwargs))

            # Update processing statistics
            self._update_stats(server_type, True, time.perf_counter_ns() - start_time)

            self.logger.info(
                "MCP document processing completed successfully",
                extra={
                    "document_id": document_id,
                    "stage": "complete",
                    "server_type": server_type,
                    "chunk_count": result.get("total_chunks", 0),
                    "elapsed_ms": result.get("processing_time_ms", 0),
                },
            )

            return result

        except Exception as e:
            # Update processing statistics
            server_type = self._determine_server_type(document_source)
            self._update_stats(server_type, False, time.perf_counter_ns() - start_time)

            self.logger.exception(
                "MCP document processing failed",
                extra={
                    "document_id": document_id,
                    "stage": "error",
                    "error": str(e),
                    "source": self._mask_source(document_source),
                },
            )
            raise

    def _route_document(self, document_source: str) -> tuple[str, Any]:
        """Route document to appropriate MCP server based on source type"""
        try:
            # Check each server to see which one can handle this source
            for server_type, server in self.server_registry.items():
                if server.validate_source(document_source):
                    return server_type, server

            # If no server can handle it, try to determine the best fallback
            fallback_server = self._determine_fallback_server(document_source)
            if fallback_server:
                return fallback_server, self.server_registry[fallback_server]

            raise ValueError(f"No MCP server can handle source: {document_source}")

        except Exception as e:
            self.logger.error(f"Document routing failed: {e}")
            raise

    def _determine_server_type(self, document_source: str) -> str:
        """Determine server type for statistics tracking"""
        try:
            for server_type, server in self.server_registry.items():
                if server.validate_source(document_source):
                    return server_type
        except Exception:
            pass
        return "unknown"

    def _determine_fallback_server(self, document_source: str) -> Optional[str]:
        """Determine fallback server based on source characteristics"""
        source_lower = document_source.lower()

        if source_lower.startswith(("http://", "https://")):
            if "github.com" in source_lower:
                return "github"
            else:
                return "web"
        elif source_lower.endswith(".pdf"):
            return "pdf"
        elif Path(document_source).exists():
            return "file_system"

        return None

    async def _process_with_server(
        self, server: Any, document_source: str, document_id: str, **kwargs
    ) -> Dict[str, Any]:
        """Process document using the selected MCP server"""
        try:
            # Process document with MCP server
            processed_doc = await server.process_document(document_source, **kwargs)

            if not processed_doc.success:
                raise Exception(f"MCP server processing failed: {processed_doc.metadata}")

            # Create chunks from processed content
            chunks = self._create_chunks_from_content(processed_doc.content, document_id)

            # Prepare metadata
            metadata = self._prepare_metadata(processed_doc, document_source, document_id)

            return {
                "chunks": chunks,
                "metadata": metadata,
                "document_source": document_source,
                "total_chunks": len(chunks),
                "document_id": document_id,
                "server_type": self._get_server_type(server),
                "processing_time_ms": metadata.get("processing_time_ms", 0),
            }

        except Exception as e:
            self.logger.error(f"Server processing failed: {e}")
            raise

    def _create_chunks_from_content(self, content: str, document_id: str) -> List[Dict[str, Any]]:
        """Create chunks from processed content using token-aware chunking"""
        try:
            # Simple chunking for now - could be enhanced with token-aware chunking
            chunk_size = self.chunk_size
            chunk_overlap = self.chunk_overlap

            chunks = []
            words = content.split()

            for i in range(0, len(words), chunk_size - chunk_overlap):
                chunk_words = words[i : i + chunk_size]
                chunk_text = " ".join(chunk_words)

                if chunk_text.strip():
                    chunk = {
                        "id": f"{document_id}_chunk_{len(chunks)}",
                        "text": chunk_text,
                        "chunk_index": len(chunks),
                        "document_id": document_id,
                        "word_count": len(chunk_words),
                    }
                    chunks.append(chunk)

            return chunks

        except Exception as e:
            self.logger.error(f"Chunk creation failed: {e}")
            # Return single chunk with full content as fallback
            return [
                {
                    "id": f"{document_id}_chunk_0",
                    "text": content,
                    "chunk_index": 0,
                    "document_id": document_id,
                    "word_count": len(content.split()),
                }
            ]

    def _prepare_metadata(self, processed_doc: Any, document_source: str, document_id: str) -> Dict[str, Any]:
        """Prepare metadata from processed document"""
        try:
            metadata = {
                "document_id": document_id,
                "source": document_source,
                "content_type": processed_doc.metadata.content_type,
                "title": processed_doc.metadata.title,
                "author": processed_doc.metadata.author,
                "created_at": processed_doc.metadata.created_at,
                "modified_at": processed_doc.metadata.modified_at,
                "word_count": processed_doc.metadata.word_count,
                "processing_time_ms": 0,  # Will be updated by caller
                "server_type": self._get_server_type_from_metadata(processed_doc.metadata.content_type),
            }

            # Add any additional metadata from the processed document
            if hasattr(processed_doc.metadata, "page_count"):
                metadata["page_count"] = processed_doc.metadata.page_count

            return metadata

        except Exception as e:
            self.logger.error(f"Metadata preparation failed: {e}")
            return {
                "document_id": document_id,
                "source": document_source,
                "content_type": "unknown",
                "word_count": 0,
                "processing_time_ms": 0,
                "server_type": "unknown",
            }

    def _get_server_type(self, server: Any) -> str:
        """Get server type from server instance"""
        if isinstance(server, FileSystemMCPServer):
            return "file_system"
        elif isinstance(server, WebMCPServer):
            return "web"
        elif isinstance(server, PDFMCPServer):
            return "pdf"
        elif isinstance(server, GitHubMCPServer):
            return "github"
        else:
            return "unknown"

    def _get_server_type_from_metadata(self, content_type: str) -> str:
        """Get server type from content type"""
        if content_type.startswith("file/") or content_type.startswith("text/"):
            return "file_system"
        elif content_type.startswith("web/") or content_type.startswith("http"):
            return "web"
        elif content_type.startswith("application/pdf"):
            return "pdf"
        elif content_type.startswith("github/"):
            return "github"
        else:
            return "unknown"

    def _mask_source(self, source: str) -> str:
        """Mask source for logging to prevent information leakage"""
        if source.startswith(("http://", "https://")):
            # Mask URLs
            try:
                from urllib.parse import urlparse

                parsed = urlparse(source)
                return f"{parsed.scheme}://{parsed.netloc}/..."
            except Exception:
                return "http://..."
        else:
            # Mask file paths
            path = Path(source)
            parts = path.parts
            # Filter out root directory and get the last two meaningful parts
            meaningful_parts = [p for p in parts if p != "/"]
            if len(meaningful_parts) >= 2:
                return f"{meaningful_parts[-2]}/{meaningful_parts[-1]}"
            else:
                return path.name

    def _update_stats(self, server_type: str, success: bool, processing_time_ns: int) -> None:
        """Update processing statistics"""
        self.processing_stats["total_documents"] += 1

        if success:
            self.processing_stats["successful_documents"] += 1
        else:
            self.processing_stats["failed_documents"] += 1

        self.processing_stats["total_processing_time"] += processing_time_ns / 1_000_000_000  # Convert to seconds

        if server_type in self.processing_stats["server_usage"]:
            self.processing_stats["server_usage"][server_type] += 1

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        stats = self.processing_stats.copy()

        # Calculate averages
        if stats["total_documents"] > 0:
            stats["average_processing_time"] = stats["total_processing_time"] / stats["total_documents"]
            stats["success_rate"] = stats["successful_documents"] / stats["total_documents"]
        else:
            stats["average_processing_time"] = 0.0
            stats["success_rate"] = 0.0

        return stats

    def get_server_info(self) -> Dict[str, Any]:
        """Get information about all MCP servers"""
        server_info = {}

        for server_type, server in self.server_registry.items():
            try:
                info = server.get_server_info()
                server_info[server_type] = {
                    "name": info.get("name", "Unknown"),
                    "version": info.get("version", "Unknown"),
                    "supported_types": info.get("supported_types", []),
                    "cache_size": info.get("cache_size", 0),
                }
            except Exception as e:
                self.logger.error(f"Failed to get info for {server_type} server: {e}")
                server_info[server_type] = {"error": str(e)}

        return server_info

    def cleanup(self) -> None:
        """Cleanup all MCP servers"""
        try:
            if hasattr(self, "server_registry"):
                for server_type, server in self.server_registry.items():
                    try:
                        if hasattr(server, "cleanup"):
                            asyncio.run(server.cleanup())
                        self.logger.info(f"Cleaned up {server_type} server")
                    except Exception as e:
                        self.logger.error(f"Failed to cleanup {server_type} server: {e}")

            self.logger.info("MCPDocumentProcessor cleanup completed")

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup()
        except Exception:
            pass  # Ignore cleanup errors in destructor


class MCPDocumentIngestionPipeline(Module):
    """DSPy module for complete MCP-based document ingestion pipeline"""

    def __init__(
        self,
        chunk_size: int = 300,
        chunk_overlap: int = 50,
        config_path: str = "config/metadata_rules.yaml",
        allowed_paths: Optional[List[str]] = None,
        mcp_timeout: int = 30,
        enable_cache: bool = True,
    ):
        super().__init__()
        self.processor = MCPDocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            config_path=config_path,
            allowed_paths=allowed_paths,
            mcp_timeout=mcp_timeout,
            enable_cache=enable_cache,
        )
        self.logger = get_logger("mcp_document_pipeline")

    def forward(self, document_source: str, vector_store: Any = None, **kwargs) -> Dict[str, Any]:
        """Complete MCP-based document ingestion pipeline"""
        start_time = time.perf_counter_ns()

        try:
            self.logger.info(
                "Starting MCP document ingestion pipeline",
                extra={
                    "source": self.processor._mask_source(document_source),
                    "stage": "pipeline_start",
                },
            )

            # Process document using MCP processor
            result: Dict[str, Any] = self.processor.forward(document_source, **kwargs)

            # Store in vector database (if provided)
            if vector_store and hasattr(vector_store, "store_chunks"):
                try:
                    # Extract text from chunk dictionaries
                    chunk_texts = [chunk["text"] for chunk in result["chunks"]]

                    # Store chunks
                    store_result = vector_store("store_chunks", chunks=chunk_texts, metadata=result["metadata"])

                    if store_result.get("status") == "success":
                        self.logger.info(
                            "Chunks stored in vector database",
                            extra={
                                "document_id": result.get("document_id", "unknown"),
                                "chunks_stored": result["total_chunks"],
                            },
                        )
                    else:
                        self.logger.error(
                            "Failed to store chunks in vector database",
                            extra={
                                "document_id": result.get("document_id", "unknown"),
                                "error": store_result.get("error", "Unknown error"),
                            },
                        )

                except Exception as e:
                    self.logger.error(
                        "Failed to store chunks in vector database",
                        extra={
                            "document_id": result.get("document_id", "unknown"),
                            "error": str(e),
                        },
                    )
                    # Continue processing even if vector storage fails

            processing_time = int((time.perf_counter_ns() - start_time) // 1_000_000)

            self.logger.info(
                "MCP document ingestion pipeline completed",
                extra={
                    "document_id": result.get("document_id", "unknown"),
                    "stage": "pipeline_complete",
                    "chunks_processed": result["total_chunks"],
                    "server_type": result.get("server_type", "unknown"),
                    "processing_time_ms": processing_time,
                },
            )

            # Add pipeline processing time to result
            result["pipeline_processing_time_ms"] = processing_time

            return result

        except Exception as e:
            self.logger.exception(
                "MCP document ingestion pipeline failed",
                extra={
                    "source": self.processor._mask_source(document_source),
                    "stage": "pipeline_error",
                    "error": str(e),
                },
            )
            raise

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics from the MCP processor"""
        return self.processor.get_processing_stats()

    def get_server_info(self) -> Dict[str, Any]:
        """Get server information from the MCP processor"""
        return self.processor.get_server_info()

    def cleanup(self) -> None:
        """Cleanup the MCP processor"""
        self.processor.cleanup()


# Example usage and testing
if __name__ == "__main__":
    # Test the MCP document processor
    processor = MCPDocumentProcessor()

    # Test with different source types
    test_sources = [
        "test_document.txt",  # File system
        "https://example.com",  # Web
        "test_document.pdf",  # PDF
        "https://github.com/octocat/Hello-World",  # GitHub
    ]

    for source in test_sources:
        try:
            print(f"\nTesting source: {source}")
            result: Dict[str, Any] = processor.forward(source)
            print(f"✅ Success: {result['total_chunks']} chunks created")
            print(f"Server type: {result.get('server_type', 'unknown')}")
        except Exception as e:
            print(f"❌ Failed: {e}")

    # Print statistics
    print("\nProcessing Statistics:")
    stats = processor.get_processing_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Print server information
    print("\nServer Information:")
    server_info = processor.get_server_info()
    for server_type, info in server_info.items():
        print(f"  {server_type}: {info}")

    # Cleanup
    processor.cleanup()
