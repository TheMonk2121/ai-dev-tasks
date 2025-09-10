"""
Base MCP Server Infrastructure

Provides the foundational classes and utilities for MCP server implementations.
"""

import asyncio
import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class MCPError(Exception):
    """Base exception for MCP-related errors."""

    def __init__(self, message: str, error_code: str = "MCP_ERROR", details: dict[str, Any] | None = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class MCPConfig(BaseModel):
    """Configuration for MCP servers."""

    server_name: str = Field(..., description="Name of the MCP server")
    server_version: str = Field(default="1.0.0", description="Version of the MCP server")
    max_file_size: int = Field(default=10 * 1024 * 1024, description="Maximum file size in bytes (10MB)")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")
    enable_logging: bool = Field(default=True, description="Enable detailed logging")
    cache_enabled: bool = Field(default=True, description="Enable response caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")

    model_config = {"extra": "forbid"}


@dataclass
class DocumentMetadata:
    """Metadata for processed documents."""

    source: str = field(metadata={"description": "Document source (file path, URL, etc.)"})
    content_type: str = field(metadata={"description": "Content type (txt, pdf, html, etc.)"})
    size: int = field(default=0, metadata={"description": "Document size in bytes"})
    encoding: str = field(default="utf-8", metadata={"description": "Document encoding"})
    created_at: str | None = field(default=None, metadata={"description": "Creation timestamp"})
    modified_at: str | None = field(default=None, metadata={"description": "Modification timestamp"})
    author: str | None = field(default=None, metadata={"description": "Document author"})
    title: str | None = field(default=None, metadata={"description": "Document title"})
    language: str | None = field(default=None, metadata={"description": "Document language"})
    page_count: int | None = field(default=None, metadata={"description": "Number of pages"})
    word_count: int | None = field(default=None, metadata={"description": "Number of words"})
    processing_time: float = field(default=0.0, metadata={"description": "Processing time in seconds"})
    error_count: int = field(default=0, metadata={"description": "Number of processing errors"})

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "source": self.source,
            "content_type": self.content_type,
            "size": self.size,
            "encoding": self.encoding,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "author": self.author,
            "title": self.title,
            "language": self.language,
            "page_count": self.page_count,
            "word_count": self.word_count,
            "processing_time": self.processing_time,
            "error_count": self.error_count,
        }


@dataclass
class ProcessedDocument:
    """Result of document processing."""

    content: str = field(metadata={"description": "Processed document content"})
    metadata: DocumentMetadata = field(metadata={"description": "Document metadata"})
    success: bool = field(default=True, metadata={"description": "Processing success status"})
    error_message: str | None = field(default=None, metadata={"description": "Error message if failed"})
    warnings: list[str] = field(default_factory=list, metadata={"description": "Processing warnings"})

    def to_dict(self) -> dict[str, Any]:
        """Convert processed document to dictionary."""
        return {
            "content": self.content,
            "metadata": self.metadata.to_dict(),
            "success": self.success,
            "error_message": self.error_message,
            "warnings": self.warnings,
        }


class MCPServer(ABC):
    """Base class for MCP server implementations."""

    def __init__(self, config: MCPConfig):
        self.config = config
        self.logger = logging.getLogger(f"mcp.{config.server_name}")
        self._cache: dict[str, Any] = {}
        self._start_time = time.time()

        if config.enable_logging:
            self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging for the MCP server."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    @abstractmethod
    async def process_document(self, source: str, **kwargs) -> ProcessedDocument:
        """Process a document from the given source."""
        pass

    @abstractmethod
    def supports_content_type(self, content_type: str) -> bool:
        """Check if this server supports the given content type."""
        pass

    @abstractmethod
    def get_supported_types(self) -> list[str]:
        """Get list of supported content types."""
        pass

    def validate_source(self, source: str) -> bool:
        """Validate if the source is supported by this server."""
        try:
            # Basic validation - subclasses can override
            if not source or not source.strip():
                return False
            return True
        except Exception as e:
            self.logger.error(f"Source validation failed: {e}")
            return False

    def get_cache_key(self, source: str, **kwargs) -> str:
        """Generate cache key for the given source and parameters."""
        params = sorted(kwargs.items())
        return f"{source}:{hash(str(params))}"

    def get_cached_result(self, cache_key: str) -> ProcessedDocument | None:
        """Get cached result if available and not expired."""
        if not self.config.cache_enabled:
            return None

        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.config.cache_ttl:
                self.logger.debug(f"Cache hit for key: {cache_key}")
                return cached_data

        return None

    def cache_result(self, cache_key: str, result: ProcessedDocument) -> None:
        """Cache the processing result."""
        if self.config.cache_enabled:
            self._cache[cache_key] = (result, time.time())
            self.logger.debug(f"Cached result for key: {cache_key}")

    async def process_with_retry(self, source: str, **kwargs) -> ProcessedDocument:
        """Process document with retry logic."""
        last_error = None

        for attempt in range(self.config.retry_attempts):
            try:
                start_time = time.time()
                result = await self.process_document(source, **kwargs)
                result.metadata.processing_time = time.time() - start_time
                return result

            except Exception as e:
                last_error = e
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")

                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay * (2**attempt))

        # All retries failed
        error_msg = f"Processing failed after {self.config.retry_attempts} attempts: {last_error}"
        self.logger.error(error_msg)

        return ProcessedDocument(
            content="",
            metadata=DocumentMetadata(source=source, content_type="unknown", error_count=self.config.retry_attempts),
            success=False,
            error_message=str(last_error),
        )

    def get_server_info(self) -> dict[str, Any]:
        """Get server information and statistics."""
        return {
            "name": self.config.server_name,
            "version": self.config.server_version,
            "supported_types": self.get_supported_types(),
            "uptime": time.time() - self._start_time,
            "cache_size": len(self._cache),
            "config": self.config.model_dump(),
        }

    def cleanup(self) -> None:
        """Cleanup resources."""
        self._cache.clear()
        self.logger.info(f"MCP Server {self.config.server_name} cleaned up")


class MCPProtocolUtils:
    """Utility functions for MCP protocol handling."""

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate if the given string is a valid URL."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def validate_file_path(path: str) -> bool:
        """Validate if the given string is a valid file path."""
        try:
            path_obj = Path(path)
            return path_obj.exists() and path_obj.is_file()
        except Exception:
            return False

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file operations."""

        # Remove or replace unsafe characters
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
        # Limit length
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
        return sanitized

    @staticmethod
    def detect_encoding(content: bytes) -> str:
        """Detect encoding of content."""
        # Try common encodings first
        common_encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]

        for encoding in common_encodings:
            try:
                content.decode(encoding)
                return encoding
            except UnicodeDecodeError:
                continue

        # If chardet is available, use it as a fallback
        try:
            import chardet  # type: ignore[import-untyped]

            result = chardet.detect(content)
            return result["encoding"] or "utf-8"
        except ImportError:
            # Fallback to utf-8 if chardet is not available
            return "utf-8"
        except Exception:
            # Handle any other chardet errors gracefully
            return "utf-8"

    @staticmethod
    def extract_text_from_html(html_content: str) -> str:
        """Extract text content from HTML."""
        try:
            from bs4 import BeautifulSoup  # type: ignore[import-untyped]

            soup = BeautifulSoup(html_content, "html.parser")
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text()
        except ImportError:
            # Fallback to simple regex if BeautifulSoup is not available

            logger = logging.getLogger(__name__)
            logger.warning(
                "BeautifulSoup not available, falling back to regex-based HTML parsing. "
                "Install beautifulsoup4 for better HTML processing."
            )

            # Remove script and style tags first
            text = re.sub(r"<script[^>]*>.*?</script>", "", html_content, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
            # Remove remaining HTML tags
            text = re.sub(r"<[^>]+>", "", text)
            # Remove extra whitespace
            text = re.sub(r"\s+", " ", text).strip()
            return text
        except Exception as e:
            # Handle any other errors gracefully

            logger = logging.getLogger(__name__)
            logger.error(f"Error extracting text from HTML: {e}")
            return html_content  # Return original content if all else fails

    @staticmethod
    def calculate_word_count(text: str) -> int:
        """Calculate word count in text."""
        if not text:
            return 0
        return len(text.split())

    @staticmethod
    def truncate_text(text: str, max_length: int = 1000) -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
