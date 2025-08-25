"""
MCP (Model Context Protocol) Integration Module

This module provides MCP server implementations for document processing
and integration with the DSPy RAG system.

Supported MCP servers:
- File System: txt, md, py, json, csv files
- Web: HTML, RSS feeds, web APIs
- PDF: PDF document processing
- GitHub: Repository files, issues, pull requests
- Database: PostgreSQL, SQLite schema and data
- Office: Word, Excel, PowerPoint documents
"""

from .base_server import DocumentMetadata, MCPConfig, MCPError, MCPProtocolUtils, MCPServer, ProcessedDocument
from .database_server import DatabaseMCPServer
from .file_system_server import FileSystemMCPServer
from .github_server import GitHubMCPServer
from .office_server import OfficeMCPServer
from .pdf_server import PDFMCPServer
from .web_server import WebMCPServer

__all__ = [
    "MCPServer",
    "MCPError",
    "MCPConfig",
    "DocumentMetadata",
    "ProcessedDocument",
    "MCPProtocolUtils",
    "FileSystemMCPServer",
    "WebMCPServer",
    "PDFMCPServer",
    "GitHubMCPServer",
    "DatabaseMCPServer",
    "OfficeMCPServer",
]

__version__ = "1.0.0"
