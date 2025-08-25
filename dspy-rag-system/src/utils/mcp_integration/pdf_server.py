"""
PDF MCP Server Implementation

Provides MCP server for PDF document processing, supporting text extraction,
metadata parsing, and content formatting with OCR capabilities.
"""

import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .base_server import DocumentMetadata, MCPConfig, MCPError, MCPProtocolUtils, MCPServer, ProcessedDocument

# Import PyMuPDF (fitz) with fallback
try:
    import fitz  # PyMuPDF - better than PyPDF2
except ImportError:
    fitz = None  # type: ignore


class PDFServerConfig(BaseModel):
    """Configuration specific to PDF MCP server."""

    enable_ocr: bool = Field(default=False, description="Enable OCR for image-based PDFs")
    extract_images: bool = Field(default=False, description="Extract and process images from PDFs")
    max_pages: int = Field(default=100, description="Maximum number of pages to process")
    text_extraction_mode: str = Field(default="text", description="Text extraction mode: 'text', 'layout', 'raw'")
    preserve_formatting: bool = Field(default=True, description="Preserve text formatting and layout")
    extract_tables: bool = Field(default=True, description="Extract and format tables from PDFs")

    model_config = {"extra": "forbid"}


class PDFPageInfo(BaseModel):
    """Information about a PDF page."""

    page_number: int
    text_content: str
    word_count: int
    image_count: int = 0
    table_count: int = 0

    model_config = {"extra": "forbid"}


class PDFDocumentInfo(BaseModel):
    """Information about a PDF document."""

    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    page_count: int = 0
    total_word_count: int = 0
    total_image_count: int = 0
    total_table_count: int = 0
    is_encrypted: bool = False
    is_scanned: bool = False

    model_config = {"extra": "forbid"}


class PDFMCPServer(MCPServer):
    """MCP server for PDF document processing."""

    def __init__(self, config: MCPConfig):
        super().__init__(config)
        self.pdf_config = PDFServerConfig()
        self._pdf_processor = None

        # Supported content types
        self.supported_types = {
            "application/pdf": "PDF document",
        }

    async def process_document(self, source: str, **kwargs) -> ProcessedDocument:
        """Process a PDF document."""
        try:
            # Validate source
            if not self.validate_source(source):
                raise MCPError(f"Invalid PDF source: {source}", error_code="INVALID_SOURCE")

            # Read PDF content
            pdf_content = await self._read_pdf_content(source)

            # Extract document information
            doc_info = await self._extract_document_info(pdf_content)

            # Extract text content
            text_content = await self._extract_text_content(pdf_content, **kwargs)

            # Process content
            processed_content = await self._process_pdf_content(text_content, doc_info, **kwargs)

            # Create metadata
            metadata = await self._create_metadata(source, doc_info, text_content)

            return ProcessedDocument(content=processed_content, metadata=metadata, success=True)

        except MCPError:
            raise
        except Exception as e:
            self.logger.error(f"Error processing PDF {source}: {e}")
            raise MCPError(f"PDF processing failed: {e}", error_code="PROCESSING_ERROR")

    def supports_content_type(self, content_type: str) -> bool:
        """Check if this server supports the given content type."""
        return content_type in self.supported_types

    def get_supported_types(self) -> List[str]:
        """Get list of supported content types."""
        return list(self.supported_types.keys())

    def validate_source(self, source: str) -> bool:
        """Validate if the source is a valid PDF file."""
        try:
            if not source or not source.strip():
                return False

            # Check if it's a file path
            if source.endswith(".pdf"):
                return True

            # Check if it's a URL pointing to a PDF
            if source.startswith(("http://", "https://")) and ".pdf" in source.lower():
                return True

            return False

        except Exception as e:
            self.logger.error(f"Source validation failed: {e}")
            return False

    async def _read_pdf_content(self, source: str) -> bytes:
        """Read PDF content from source."""
        try:
            if source.startswith(("http://", "https://")):
                # Download PDF from URL
                return await self._download_pdf_from_url(source)
            else:
                # Read PDF from file
                return await self._read_pdf_from_file(source)

        except Exception as e:
            raise MCPError(f"Failed to read PDF content: {e}", error_code="READ_ERROR")

    async def _download_pdf_from_url(self, url: str) -> bytes:
        """Download PDF content from URL."""
        try:
            import httpx

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()

                content_type = response.headers.get("content-type", "").lower()
                if "pdf" not in content_type and not url.lower().endswith(".pdf"):
                    raise MCPError("URL does not point to a PDF file", error_code="INVALID_CONTENT_TYPE")

                return response.content

        except httpx.HTTPStatusError as e:
            raise MCPError(f"HTTP error {e.response.status_code}: {e}", error_code="HTTP_ERROR")
        except httpx.RequestError as e:
            raise MCPError(f"Request failed: {e}", error_code="REQUEST_ERROR")

    async def _read_pdf_from_file(self, file_path: str) -> bytes:
        """Read PDF content from file."""
        try:
            from pathlib import Path

            path = Path(file_path)
            if not path.exists():
                raise MCPError(f"PDF file not found: {file_path}", error_code="FILE_NOT_FOUND")

            if not path.is_file():
                raise MCPError(f"Source is not a file: {file_path}", error_code="NOT_A_FILE")

            # Check file size
            file_size = path.stat().st_size
            if file_size > self.config.max_file_size:
                raise MCPError(
                    f"PDF file too large: {file_size} bytes (max: {self.config.max_file_size})",
                    error_code="FILE_TOO_LARGE",
                )

            with open(path, "rb") as f:
                return f.read()

        except Exception as e:
            raise MCPError(f"Failed to read PDF file: {e}", error_code="READ_ERROR")

    async def _extract_document_info(self, pdf_content: bytes) -> PDFDocumentInfo:
        """Extract document information from PDF."""
        try:
            if fitz is None:
                raise MCPError("PyMuPDF (fitz) is required for PDF processing", error_code="MISSING_DEPENDENCY")

            # Open PDF from bytes
            doc = fitz.open(stream=pdf_content, filetype="pdf")  # type: ignore[attr-defined]

            # Check if PDF is encrypted
            if doc.needs_pass:  # type: ignore[attr-defined]
                doc.close()
                return PDFDocumentInfo(page_count=len(doc), is_encrypted=True)

            # Extract metadata
            metadata = doc.metadata  # type: ignore[attr-defined]

            doc_info = PDFDocumentInfo(
                title=metadata.get("title"),
                author=metadata.get("author"),
                subject=metadata.get("subject"),
                creator=metadata.get("creator"),
                producer=metadata.get("producer"),
                creation_date=metadata.get("creationDate"),
                modification_date=metadata.get("modDate"),
                page_count=len(doc),
                is_encrypted=False,
            )

            # Detect if PDF is scanned (image-based)
            doc_info.is_scanned = await self._detect_scanned_pdf(doc)

            doc.close()
            return doc_info

        except Exception as e:
            self.logger.warning(f"Document info extraction failed: {e}")
            return PDFDocumentInfo(page_count=0)

    async def _detect_scanned_pdf(self, doc) -> bool:
        """Detect if PDF is scanned (image-based)."""
        try:
            # Simple heuristic: check if first page has very little text
            if len(doc) > 0:
                first_page = doc[0]  # type: ignore[attr-defined]
                text = first_page.get_text()

                # If text is very short or empty, likely scanned
                if len(text.strip()) < 50:
                    return True

            return False

        except Exception:
            return False

    async def _extract_text_content(self, pdf_content: bytes, **kwargs) -> str:
        """Extract text content from PDF."""
        try:
            if fitz is None:
                raise MCPError("PyMuPDF (fitz) is required for PDF processing", error_code="MISSING_DEPENDENCY")

            # Open PDF from bytes
            doc = fitz.open(stream=pdf_content, filetype="pdf")  # type: ignore[attr-defined]

            if doc.needs_pass:  # type: ignore[attr-defined]
                doc.close()
                raise MCPError("PDF is encrypted and cannot be processed", error_code="ENCRYPTED_PDF")

            # Limit pages if configured
            max_pages = min(self.pdf_config.max_pages, len(doc))

            extracted_text = []
            total_word_count = 0

            for page_num in range(max_pages):
                try:
                    page = doc[page_num]  # type: ignore[attr-defined]
                    page_text = page.get_text()

                    if page_text:
                        # Clean up text
                        cleaned_text = await self._clean_page_text(page_text, page_num + 1)
                        extracted_text.append(cleaned_text)
                        total_word_count += len(page_text.split())

                except Exception as e:
                    self.logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue

            doc.close()
            return "\n\n".join(extracted_text)

        except Exception as e:
            raise MCPError(f"Text extraction failed: {e}", error_code="EXTRACTION_ERROR")

    async def _clean_page_text(self, page_text: str, page_num: int) -> str:
        """Clean and format page text."""
        try:
            # Remove excessive whitespace
            cleaned = re.sub(r"\s+", " ", page_text.strip())

            # Add page header
            page_header = f"\n--- Page {page_num} ---\n"

            return page_header + cleaned

        except Exception as e:
            self.logger.warning(f"Text cleaning failed for page {page_num}: {e}")
            return page_text

    async def _process_pdf_content(self, text_content: str, doc_info: PDFDocumentInfo, **kwargs) -> str:
        """Process extracted PDF content."""
        try:
            lines = text_content.split("\n")
            processed_lines = []

            # Add document header
            if doc_info.title:
                processed_lines.append(f"# {doc_info.title}")
                processed_lines.append("")

            if doc_info.author:
                processed_lines.append(f"**Author:** {doc_info.author}")
                processed_lines.append("")

            if doc_info.subject:
                processed_lines.append(f"**Subject:** {doc_info.subject}")
                processed_lines.append("")

            if doc_info.page_count > 0:
                processed_lines.append(f"**Pages:** {doc_info.page_count}")
                processed_lines.append("")

            if doc_info.creation_date:
                processed_lines.append(f"**Created:** {doc_info.creation_date}")
                processed_lines.append("")

            if doc_info.modification_date:
                processed_lines.append(f"**Modified:** {doc_info.modification_date}")
                processed_lines.append("")

            if doc_info.is_scanned:
                processed_lines.append("**Note:** This appears to be a scanned document")
                processed_lines.append("")

            processed_lines.append("---")
            processed_lines.append("")

            # Add content
            processed_lines.extend(lines)

            return "\n".join(processed_lines)

        except Exception as e:
            self.logger.warning(f"Content processing failed: {e}")
            return text_content

    async def _create_metadata(self, source: str, doc_info: PDFDocumentInfo, text_content: str) -> DocumentMetadata:
        """Create metadata for the processed PDF."""
        try:
            return DocumentMetadata(
                source=source,
                content_type="application/pdf",
                title=doc_info.title,
                author=doc_info.author,
                created_at=doc_info.creation_date,
                modified_at=doc_info.modification_date,
                page_count=doc_info.page_count,
                word_count=MCPProtocolUtils.calculate_word_count(text_content),
                processing_time=0.0,  # Could be calculated if needed
            )

        except Exception as e:
            self.logger.warning(f"Metadata creation failed: {e}")
            return DocumentMetadata(
                source=source,
                content_type="application/pdf",
                word_count=MCPProtocolUtils.calculate_word_count(text_content),
            )

    def get_pdf_config(self) -> Dict[str, Any]:
        """Get PDF server configuration."""
        return self.pdf_config.model_dump()

    def update_pdf_config(self, **kwargs) -> None:
        """Update PDF server configuration."""
        for key, value in kwargs.items():
            if hasattr(self.pdf_config, key):
                setattr(self.pdf_config, key, value)

    async def get_page_info(self, source: str, page_num: int) -> Optional[PDFPageInfo]:
        """Get information about a specific page."""
        try:
            if fitz is None:
                raise MCPError("PyMuPDF (fitz) is required for PDF processing", error_code="MISSING_DEPENDENCY")

            pdf_content = await self._read_pdf_content(source)
            doc = fitz.open(stream=pdf_content, filetype="pdf")  # type: ignore[attr-defined]

            if page_num < 1 or page_num > len(doc):
                doc.close()
                return None

            page = doc[page_num - 1]  # type: ignore[attr-defined]
            page_text = page.get_text()

            doc.close()
            return PDFPageInfo(
                page_number=page_num,
                text_content=page_text,
                word_count=len(page_text.split()),
            )

        except Exception as e:
            self.logger.error(f"Failed to get page info: {e}")
            return None

    async def extract_tables(self, source: str) -> List[Dict[str, Any]]:
        """Extract tables from PDF."""
        try:
            # This would require additional libraries like tabula-py or camelot-py
            # For now, return empty list
            self.logger.info("Table extraction not implemented yet")
            return []

        except Exception as e:
            self.logger.error(f"Table extraction failed: {e}")
            return []

    async def extract_images(self, source: str) -> List[Dict[str, Any]]:
        """Extract images from PDF."""
        try:
            # This would require additional libraries like pdf2image
            # For now, return empty list
            self.logger.info("Image extraction not implemented yet")
            return []

        except Exception as e:
            self.logger.error(f"Image extraction failed: {e}")
            return []
