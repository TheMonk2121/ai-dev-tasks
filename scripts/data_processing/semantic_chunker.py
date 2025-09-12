#!/usr/bin/env python3
"""
Semantic Chunker for RAG System
Implements intelligent chunking by semantic boundaries with configurable overlap.
"""

import re
from pathlib import Path
from typing import Any, Optional


class SemanticChunker:
    """
    Intelligent chunking that respects semantic boundaries (paragraphs, sections, headers)
    while maintaining consistent chunk sizes and overlap.
    """

    def __init__(
        self,
        chunk_size: int = 450,
        overlap_ratio: float = 0.10,
        min_chunk_size: int = 100,
        max_chunk_size: int = 600,
    ):
        """
        Initialize semantic chunker.

        Args:
            chunk_size: Target chunk size in characters (default: 450)
            overlap_ratio: Overlap ratio between chunks (default: 0.10 = 10%)
            min_chunk_size: Minimum chunk size to avoid tiny fragments (default: 100)
            max_chunk_size: Maximum chunk size to prevent oversized chunks (default: 600)
        """
        self.chunk_size = chunk_size
        self.overlap_ratio = overlap_ratio
        self.overlap_size = int(chunk_size * overlap_ratio)
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

    def chunk_content(
        self, content: str, file_path: str, content_type: str = "markdown", metadata: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Chunk content using semantic boundaries.

        Args:
            content: The text content to chunk
            file_path: Path to the source file
            content_type: Type of content (markdown, python, etc.)
            metadata: Additional metadata to include in chunks

        Returns:
            List of chunk dictionaries with content and metadata
        """
        if not content.strip():
            # Return a single empty chunk instead of empty list
            return [self._create_chunk("", [], file_path, content_type, 0, metadata)]

        # Extract semantic units based on content type
        semantic_units = self._extract_semantic_units(content, content_type)

        # Group units into chunks with overlap
        chunks = self._group_units_into_chunks(semantic_units, file_path, content_type, metadata)

        return chunks

    def _extract_semantic_units(self, content: str, content_type: str) -> list[dict[str, Any]]:
        """Extract semantic units (paragraphs, sections, etc.) from content."""
        units = []

        if content_type.lower() in ["markdown", "md"]:
            units = self._extract_markdown_units(content)
        elif content_type.lower() == "python":
            units = self._extract_python_units(content)
        elif content_type.lower() in ["yaml", "yml"]:
            units = self._extract_yaml_units(content)
        else:
            # Fallback to paragraph-based chunking
            units = self._extract_paragraph_units(content)

        return units

    def _extract_markdown_units(self, content: str) -> list[dict[str, Any]]:
        """Extract semantic units from Markdown content."""
        units: list[dict[str, Any]] = []
        lines = content.split("\n")
        current_unit: list[str] = []
        current_type = "paragraph"
        current_level = 0

        for i, line in enumerate(lines):
            line = line.rstrip()

            # Check for headers
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if header_match:
                # Save previous unit if it exists
                if current_unit:
                    units.append(
                        {
                            "content": "\n".join(current_unit).strip(),
                            "type": current_type,
                            "level": current_level,
                            "line_start": i - len(current_unit),
                            "line_end": i - 1,
                        }
                    )

                # Start new header unit
                level = len(header_match.group(1))
                current_unit = [line]
                current_type = f"header_h{level}"
                current_level = level
                continue

            # Check for code blocks
            if line.startswith("```"):
                if current_unit and current_type != "code_block":
                    # Save previous unit
                    units.append(
                        {
                            "content": "\n".join(current_unit).strip(),
                            "type": current_type,
                            "level": current_level,
                            "line_start": i - len(current_unit),
                            "line_end": i - 1,
                        }
                    )
                    current_unit = []

                current_unit = [line]
                current_type = "code_block"
                current_level = 0
                continue

            # Check for list items
            list_match = re.match(r"^(\s*)([-*+]|\d+\.)\s+", line)
            if list_match:
                if current_unit and current_type != "list":
                    # Save previous unit
                    units.append(
                        {
                            "content": "\n".join(current_unit).strip(),
                            "type": current_type,
                            "level": current_level,
                            "line_start": i - len(current_unit),
                            "line_end": i - 1,
                        }
                    )
                    current_unit = []

                current_unit = [line]
                current_type = "list"
                current_level = len(list_match.group(1)) // 2  # Indentation level
                continue

            # Regular content
            if line.strip():
                current_unit.append(line)
            else:
                # Empty line - end current unit if it exists
                if current_unit:
                    units.append(
                        {
                            "content": "\n".join(current_unit).strip(),
                            "type": current_type,
                            "level": current_level,
                            "line_start": i - len(current_unit),
                            "line_end": i - 1,
                        }
                    )
                    current_unit = []
                    current_type = "paragraph"
                    current_level = 0

        # Add final unit
        if current_unit:
            units.append(
                {
                    "content": "\n".join(current_unit).strip(),
                    "type": current_type,
                    "level": current_level,
                    "line_start": len(lines) - len(current_unit),
                    "line_end": len(lines) - 1,
                }
            )

        return units

    def _extract_python_units(self, content: str) -> list[dict[str, Any]]:
        """Extract semantic units from Python content."""
        units: list[dict[str, Any]] = []
        lines = content.split("\n")
        current_unit: list[str] = []
        current_type = "module"
        current_level = 0

        for i, line in enumerate(lines):
            line = line.rstrip()

            # Check for class definitions
            class_match = re.match(r"^(\s*)class\s+(\w+)", line)
            if class_match:
                if current_unit:
                    units.append(
                        {
                            "content": "\n".join(current_unit).strip(),
                            "type": current_type,
                            "level": current_level,
                            "line_start": i - len(current_unit),
                            "line_end": i - 1,
                        }
                    )

                current_unit = [line]
                current_type = "class"
                current_level = len(class_match.group(1)) // 4
                continue

            # Check for function definitions
            func_match = re.match(r"^(\s*)def\s+(\w+)", line)
            if func_match:
                if current_unit:
                    units.append(
                        {
                            "content": "\n".join(current_unit).strip(),
                            "type": current_type,
                            "level": current_level,
                            "line_start": i - len(current_unit),
                            "line_end": i - 1,
                        }
                    )

                current_unit = [line]
                current_type = "function"
                current_level = len(func_match.group(1)) // 4
                continue

            # Regular content
            if line.strip():
                current_unit.append(line)
            else:
                # Empty line - end current unit if it exists
                if current_unit:
                    units.append(
                        {
                            "content": "\n".join(current_unit).strip(),
                            "type": current_type,
                            "level": current_level,
                            "line_start": i - len(current_unit),
                            "line_end": i - 1,
                        }
                    )
                    current_unit = []
                    current_type = "module"
                    current_level = 0

        # Add final unit
        if current_unit:
            units.append(
                {
                    "content": "\n".join(current_unit).strip(),
                    "type": current_type,
                    "level": current_level,
                    "line_start": len(lines) - len(current_unit),
                    "line_end": len(lines) - 1,
                }
            )

        return units

    def _extract_yaml_units(self, content: str) -> list[dict[str, Any]]:
        """Extract semantic units from YAML content."""
        units: list[dict[str, Any]] = []
        lines = content.split("\n")
        current_unit: list[str] = []
        current_type = "section"
        current_level = 0

        for i, line in enumerate(lines):
            line = line.rstrip()

            # Check for top-level keys
            if line and not line.startswith(" ") and not line.startswith("\t") and ":" in line:
                if current_unit:
                    units.append(
                        {
                            "content": "\n".join(current_unit).strip(),
                            "type": current_type,
                            "level": current_level,
                            "line_start": i - len(current_unit),
                            "line_end": i - 1,
                        }
                    )

                current_unit = [line]
                current_type = "section"
                current_level = 0
                continue

            # Regular content
            if line.strip():
                current_unit.append(line)
            else:
                # Empty line - end current unit if it exists
                if current_unit:
                    units.append(
                        {
                            "content": "\n".join(current_unit).strip(),
                            "type": current_type,
                            "level": current_level,
                            "line_start": i - len(current_unit),
                            "line_end": i - 1,
                        }
                    )
                    current_unit = []
                    current_type = "section"
                    current_level = 0

        # Add final unit
        if current_unit:
            units.append(
                {
                    "content": "\n".join(current_unit).strip(),
                    "type": current_type,
                    "level": current_level,
                    "line_start": len(lines) - len(current_unit),
                    "line_end": len(lines) - 1,
                }
            )

        return units

    def _extract_paragraph_units(self, content: str) -> list[dict[str, Any]]:
        """Fallback: extract units by paragraphs."""
        units: list[dict[str, Any]] = []
        paragraphs = content.split("\n\n")

        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                units.append(
                    {"content": paragraph.strip(), "type": "paragraph", "level": 0, "line_start": i, "line_end": i}
                )

        return units

    def _group_units_into_chunks(
        self, units: list[dict[str, Any]], file_path: str, content_type: str, metadata: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Group semantic units into chunks with overlap."""
        chunks: list[dict[str, Any]] = []
        current_chunk = ""
        current_units: list[dict[str, Any]] = []
        chunk_index = 0

        for i, unit in enumerate(units):
            unit_content = unit["content"]

            # Check if adding this unit would exceed target chunk size
            if current_chunk and len(current_chunk) + len(unit_content) + 2 > self.chunk_size:
                # Save current chunk
                if len(current_chunk.strip()) >= self.min_chunk_size:
                    chunks.append(
                        self._create_chunk(
                            current_chunk.strip(), current_units, file_path, content_type, chunk_index, metadata
                        )
                    )
                    chunk_index += 1

                # Start new chunk with overlap
                current_chunk, current_units = self._create_overlap_chunk(current_chunk, current_units)

            # Add unit to current chunk
            if current_chunk:
                current_chunk += "\n\n" + unit_content
            else:
                current_chunk = unit_content

            current_units.append(unit)

        # Add final chunk
        if current_chunk.strip():
            # If final chunk is too large, split it further
            if len(current_chunk.strip()) > self.max_chunk_size:
                # Split the oversized chunk
                sub_chunks = self._split_oversized_chunk(
                    current_chunk.strip(), current_units, file_path, content_type, chunk_index, metadata
                )
                chunks.extend(sub_chunks)
            elif len(current_chunk.strip()) >= self.min_chunk_size:
                chunks.append(
                    self._create_chunk(
                        current_chunk.strip(), current_units, file_path, content_type, chunk_index, metadata
                    )
                )

        return chunks

    def _split_oversized_chunk(
        self,
        content: str,
        units: list[dict[str, Any]],
        file_path: str,
        content_type: str,
        start_chunk_index: int,
        metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Split an oversized chunk into smaller chunks."""
        chunks: list[dict[str, Any]] = []
        chunk_index = start_chunk_index

        # Split by sentences or words if no semantic boundaries
        sentences = re.split(r"(?<=[.!?])\s+", content)
        current_chunk = ""
        current_units: list[dict[str, Any]] = []

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(
                    self._create_chunk(
                        current_chunk.strip(), current_units, file_path, content_type, chunk_index, metadata
                    )
                )
                chunk_index += 1

                # Start new chunk with overlap
                if self.overlap_size > 0:
                    overlap_text = (
                        current_chunk[-self.overlap_size :] if len(current_chunk) > self.overlap_size else current_chunk
                    )
                    current_chunk = overlap_text + " " + sentence
                else:
                    current_chunk = sentence
                current_units = []  # Simplified for sentence-level splitting
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence

        # Add final chunk
        if current_chunk.strip():
            chunks.append(
                self._create_chunk(current_chunk.strip(), current_units, file_path, content_type, chunk_index, metadata)
            )

        return chunks

    def _create_overlap_chunk(
        self, previous_chunk: str, previous_units: list[dict[str, Any]]
    ) -> tuple[str, list[dict[str, Any]]]:
        """Create overlap chunk from the end of previous chunk."""
        if not previous_chunk or self.overlap_size <= 0:
            return "", []

        # Take the last part of the previous chunk for overlap
        overlap_text = (
            previous_chunk[-self.overlap_size :] if len(previous_chunk) > self.overlap_size else previous_chunk
        )

        # Find which units contribute to the overlap
        overlap_units: list[dict[str, Any]] = []
        current_length = 0

        for unit in reversed(previous_units):
            if current_length + len(unit["content"]) <= self.overlap_size:
                overlap_units.insert(0, unit)
                current_length += len(unit["content"]) + 2  # +2 for \n\n
            else:
                break

        return overlap_text, overlap_units

    def _create_chunk(
        self,
        content: str,
        units: list[dict[str, Any]],
        file_path: str,
        content_type: str,
        chunk_index: int,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a chunk dictionary with metadata."""
        chunk_metadata: dict[str, Any] = {
            "file_path": file_path,
            "chunk_type": "semantic",
            "chunk_size": len(content),
            "chunk_index": chunk_index,
            "content_type": content_type,
            "chunk_variant": f"semantic_{self.chunk_size}_o{int(self.overlap_ratio*100)}",
            "overlap_ratio": self.overlap_ratio,
            "overlap_size": self.overlap_size,
            "unit_count": len(units),
            "unit_types": [unit["type"] for unit in units],
            "semantic_levels": [unit["level"] for unit in units],
        }

        # Add any additional metadata
        if metadata:
            chunk_metadata.update(metadata)

        return {"chunk_index": chunk_index, "content": content, "metadata": chunk_metadata}


def test_semantic_chunker():
    """Test the semantic chunker with sample content."""
    chunker = SemanticChunker(chunk_size=450, overlap_ratio=0.10)

    # Test with sample markdown
    sample_md = """# Introduction

This is a sample markdown document for testing the semantic chunker.

## Section 1

This is the first section with some content that should be chunked properly.

### Subsection 1.1

This is a subsection with more detailed information.

## Section 2

This is the second section with different content.

```python
def example_function():
    return "Hello, World!"
```

## Conclusion

This concludes our sample document.
"""

    chunks = chunker.chunk_content(sample_md, "test.md", "markdown")

    print(f"Created {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(f"  Size: {chunk['metadata']['chunk_size']} chars")
        print(f"  Units: {chunk['metadata']['unit_count']}")
        print(f"  Types: {chunk['metadata']['unit_types']}")
        print(f"  Content: {chunk['content'][:100]}...")


if __name__ == "__main__":
    test_semantic_chunker()
