#!/usr/bin/env python3
"""
DSPy Signatures for MCP-based document processing
"""

from typing import Any

from dspy import InputField, OutputField, Signature


class MCPDocumentSignature(Signature):
    """Signature describing MCP document processing.

    Inputs:
      - document_source: Path/URL identifying the document to process

    Outputs:
      - chunks: Text chunks extracted from the document
      - metadata: Processing metadata (content_type, server_type, etc.)
    """

    document_source: str = InputField(desc="Path or URL identifying the document to process")
    chunks: list[str] = OutputField(desc="Extracted text chunks from the document")
    metadata: dict[str, Any] = OutputField(desc="Processing metadata such as content_type and server_type")
