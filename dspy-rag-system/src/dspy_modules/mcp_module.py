#!/usr/bin/env python3
"""
DSPy Module wrapper over MCPDocumentProcessor using MCPDocumentSignature
"""

from typing import Any, Dict, List

from dspy import Module

from .mcp_document_processor import MCPDocumentProcessor


class MCPDocumentModule(Module):
    """Thin DSPy module that delegates to MCPDocumentProcessor and adapts outputs."""

    def __init__(
        self,
        chunk_size: int = 300,
        chunk_overlap: int = 50,
        mcp_timeout: int = 30,
        enable_cache: bool = True,
    ) -> None:
        super().__init__()
        self.processor = MCPDocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            mcp_timeout=mcp_timeout,
            enable_cache=enable_cache,
        )

    def forward(self, document_source: str, **kwargs) -> Dict[str, Any]:
        """Conform to MCPDocumentSignature: returns chunks as list[str] + metadata."""
        result = self.processor(document_source, **kwargs)
        # Adapt chunks to list[str]
        chunk_texts: List[str] = [c["text"] for c in result.get("chunks", [])]
        return {
            "chunks": chunk_texts,
            "metadata": result.get("metadata", {}),
        }

    # Convenience accessors
    def get_processing_stats(self) -> Dict[str, Any]:
        return self.processor.get_processing_stats()

    def get_server_info(self) -> Dict[str, Any]:
        return self.processor.get_server_info()

    def cleanup(self) -> None:
        self.processor.cleanup()
