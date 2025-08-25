"""
File System MCP Server Implementation

Provides MCP server for file system document processing, supporting common text formats
with metadata extraction and safe file operations.
"""

import csv
import io
import json
from datetime import datetime
from pathlib import Path
from typing import List

from .base_server import DocumentMetadata, MCPConfig, MCPError, MCPProtocolUtils, MCPServer, ProcessedDocument


class FileSystemMCPServer(MCPServer):
    """MCP server for file system document processing."""

    def __init__(self, config: MCPConfig):
        super().__init__(config)
        self.supported_extensions = {
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".py": "text/python",
            ".json": "application/json",
            ".csv": "text/csv",
            ".html": "text/html",
            ".htm": "text/html",
            ".xml": "application/xml",
            ".yaml": "text/yaml",
            ".yml": "text/yaml",
            ".toml": "text/toml",
            ".ini": "text/ini",
            ".cfg": "text/ini",
            ".conf": "text/ini",
        }

    async def process_document(self, source: str, **kwargs) -> ProcessedDocument:
        """Process a document from the file system."""
        try:
            # Validate source
            if not self.validate_source(source):
                raise MCPError(f"Invalid file source: {source}", error_code="INVALID_SOURCE")

            file_path = Path(source)

            # Check if file exists
            if not file_path.exists():
                raise MCPError(f"File not found: {source}", error_code="FILE_NOT_FOUND")

            # Check if it's a file (not directory)
            if not file_path.is_file():
                raise MCPError(f"Source is not a file: {source}", error_code="NOT_A_FILE")

            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.config.max_file_size:
                raise MCPError(
                    f"File too large: {file_size} bytes (max: {self.config.max_file_size})", error_code="FILE_TOO_LARGE"
                )

            # Get file extension and content type
            extension = file_path.suffix.lower()
            content_type = self.supported_extensions.get(extension, "text/plain")

            # Read file content
            content = await self._read_file_content(file_path)

            # Extract metadata
            metadata = await self._extract_metadata(file_path, content, content_type)

            # Process content based on type
            processed_content = await self._process_content(content, content_type, **kwargs)

            return ProcessedDocument(content=processed_content, metadata=metadata, success=True)

        except MCPError:
            raise
        except Exception as e:
            self.logger.error(f"Error processing file {source}: {e}")
            raise MCPError(f"File processing failed: {e}", error_code="PROCESSING_ERROR")

    def supports_content_type(self, content_type: str) -> bool:
        """Check if this server supports the given content type."""
        return content_type in self.supported_extensions.values()

    def get_supported_types(self) -> List[str]:
        """Get list of supported content types."""
        return list(self.supported_extensions.values())

    def validate_source(self, source: str) -> bool:
        """Validate if the source is a valid file path."""
        try:
            if not source or not source.strip():
                return False

            # Basic path validation
            path = Path(source)

            # Check for path traversal attempts
            if ".." in str(path):
                return False

            # Check if path is absolute and within allowed directories
            # For now, allow any readable file path
            return True

        except Exception as e:
            self.logger.error(f"Source validation failed: {e}")
            return False

    async def _read_file_content(self, file_path: Path) -> str:
        """Read file content with proper encoding detection."""
        try:
            # Read file as bytes first for encoding detection
            with open(file_path, "rb") as f:
                content_bytes = f.read()

            # Detect encoding
            encoding = MCPProtocolUtils.detect_encoding(content_bytes)

            # Decode content
            content = content_bytes.decode(encoding, errors="replace")

            return content

        except UnicodeDecodeError as e:
            self.logger.warning(f"Encoding error for {file_path}: {e}")
            # Fallback to utf-8 with error replacement
            return content_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            raise MCPError(f"Failed to read file: {e}", error_code="READ_ERROR")

    async def _extract_metadata(self, file_path: Path, content: str, content_type: str) -> DocumentMetadata:
        """Extract metadata from the file."""
        try:
            stat = file_path.stat()

            metadata = DocumentMetadata(
                source=str(file_path),
                content_type=content_type,
                size=stat.st_size,
                encoding=MCPProtocolUtils.detect_encoding(content.encode("utf-8")),
                created_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                word_count=MCPProtocolUtils.calculate_word_count(content),
            )

            # Extract additional metadata based on content type
            if content_type == "application/json":
                metadata = await self._extract_json_metadata(metadata, content)
            elif content_type == "text/csv":
                metadata = await self._extract_csv_metadata(metadata, content)
            elif content_type == "text/markdown":
                metadata = await self._extract_markdown_metadata(metadata, content)
            elif content_type == "text/python":
                metadata = await self._extract_python_metadata(metadata, content)

            return metadata

        except Exception as e:
            self.logger.warning(f"Metadata extraction failed: {e}")
            # Return basic metadata even if extraction fails
            return DocumentMetadata(
                source=str(file_path),
                content_type=content_type,
                size=file_path.stat().st_size,
                word_count=MCPProtocolUtils.calculate_word_count(content),
            )

    async def _process_content(self, content: str, content_type: str, **kwargs) -> str:
        """Process content based on its type."""
        try:
            if content_type == "application/json":
                return await self._process_json_content(content, **kwargs)
            elif content_type == "text/csv":
                return await self._process_csv_content(content, **kwargs)
            elif content_type == "text/markdown":
                return await self._process_markdown_content(content, **kwargs)
            elif content_type == "text/python":
                return await self._process_python_content(content, **kwargs)
            else:
                # Default processing for plain text
                return await self._process_text_content(content, **kwargs)

        except Exception as e:
            self.logger.warning(f"Content processing failed: {e}")
            # Return original content if processing fails
            return content

    async def _extract_json_metadata(self, metadata: DocumentMetadata, content: str) -> DocumentMetadata:
        """Extract metadata from JSON content."""
        try:
            data = json.loads(content)

            # Extract title if available
            if isinstance(data, dict):
                if "title" in data:
                    metadata.title = str(data["title"])
                if "name" in data:
                    metadata.title = metadata.title or str(data["name"])
                if "author" in data:
                    metadata.author = str(data["author"])

            return metadata

        except json.JSONDecodeError:
            return metadata

    async def _extract_csv_metadata(self, metadata: DocumentMetadata, content: str) -> DocumentMetadata:
        """Extract metadata from CSV content."""
        try:
            # Count rows and columns
            lines = content.strip().split("\n")
            if lines:
                # Count columns from header
                reader = csv.reader(io.StringIO(content))
                header = next(reader, [])
                column_count = len(header)

                # Count rows (excluding header)
                row_count = len(lines) - 1 if len(lines) > 1 else 0

                metadata.title = f"CSV with {column_count} columns, {row_count} rows"

            return metadata

        except Exception:
            return metadata

    async def _extract_markdown_metadata(self, metadata: DocumentMetadata, content: str) -> DocumentMetadata:
        """Extract metadata from Markdown content."""
        try:
            lines = content.split("\n")

            # Extract title from first heading
            for line in lines:
                line = line.strip()
                if line.startswith("# "):
                    metadata.title = line[2:].strip()
                    break
                elif line.startswith("## "):
                    metadata.title = metadata.title or line[3:].strip()
                    break

            # Extract language from code blocks
            if "```python" in content:
                metadata.language = "python"
            elif "```javascript" in content or "```js" in content:
                metadata.language = "javascript"
            elif "```html" in content:
                metadata.language = "html"

            return metadata

        except Exception:
            return metadata

    async def _extract_python_metadata(self, metadata: DocumentMetadata, content: str) -> DocumentMetadata:
        """Extract metadata from Python content."""
        try:
            lines = content.split("\n")

            # Extract docstring as title
            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith('"""') or line.startswith("'''"):
                    # Find end of docstring
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip().endswith('"""') or lines[j].strip().endswith("'''"):
                            docstring = "\n".join(lines[i + 1 : j]).strip()
                            if docstring:
                                metadata.title = docstring.split("\n")[0]
                            break
                    break

            # Check for class or function definitions
            for line in lines:
                line = line.strip()
                if line.startswith("class ") and not metadata.title:
                    class_name = line[6:].split("(")[0].split(":")[0].strip()
                    metadata.title = f"Class: {class_name}"
                elif line.startswith("def ") and not metadata.title:
                    func_name = line[4:].split("(")[0].strip()
                    metadata.title = f"Function: {func_name}"

            metadata.language = "python"
            return metadata

        except Exception:
            return metadata

    async def _process_json_content(self, content: str, **kwargs) -> str:
        """Process JSON content."""
        try:
            data = json.loads(content)
            # Pretty print JSON for better readability
            return json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            return content

    async def _process_csv_content(self, content: str, **kwargs) -> str:
        """Process CSV content."""
        try:
            # Parse and reformat CSV for better readability
            reader = csv.reader(io.StringIO(content))
            rows = list(reader)

            if not rows:
                return content

            # Find maximum column width for each column
            col_widths = []
            for col_idx in range(max(len(row) for row in rows)):
                col_width = max(len(str(row[col_idx])) if col_idx < len(row) else 0 for row in rows)
                col_widths.append(col_width)

            # Format as table
            formatted_lines = []
            for row in rows:
                formatted_row = []
                for col_idx, cell in enumerate(row):
                    if col_idx < len(col_widths):
                        formatted_row.append(str(cell).ljust(col_widths[col_idx]))
                formatted_lines.append(" | ".join(formatted_row))

            return "\n".join(formatted_lines)

        except Exception:
            return content

    async def _process_markdown_content(self, content: str, **kwargs) -> str:
        """Process Markdown content."""
        # For now, return as-is. Could add syntax highlighting or formatting later
        return content

    async def _process_python_content(self, content: str, **kwargs) -> str:
        """Process Python content."""
        # For now, return as-is. Could add syntax highlighting or formatting later
        return content

    async def _process_text_content(self, content: str, **kwargs) -> str:
        """Process plain text content."""
        # Basic text processing
        lines = content.split("\n")

        # Remove excessive blank lines
        processed_lines = []
        prev_blank = False

        for line in lines:
            is_blank = not line.strip()
            if is_blank and prev_blank:
                continue
            processed_lines.append(line)
            prev_blank = is_blank

        return "\n".join(processed_lines)

    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return list(self.supported_extensions.keys())

    def add_supported_extension(self, extension: str, content_type: str) -> None:
        """Add support for a new file extension."""
        if not extension.startswith("."):
            extension = "." + extension
        self.supported_extensions[extension.lower()] = content_type
        self.logger.info(f"Added support for {extension} -> {content_type}")

    def remove_supported_extension(self, extension: str) -> None:
        """Remove support for a file extension."""
        if not extension.startswith("."):
            extension = "." + extension
        if extension.lower() in self.supported_extensions:
            del self.supported_extensions[extension.lower()]
            self.logger.info(f"Removed support for {extension}")
