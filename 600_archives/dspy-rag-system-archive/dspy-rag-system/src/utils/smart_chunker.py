#!/usr/bin/env python3
"""
Smart Code-Aware Chunker for DSPy RAG System
Implements intelligent chunking that preserves code structure and enables stitching.
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from .tokenizer import TokenAwareChunker
except ImportError:
    from tokenizer import TokenAwareChunker

logger = logging.getLogger(__name__)


@dataclass
class ChunkBoundary:
    """Represents a chunk boundary with metadata"""

    start_pos: int
    end_pos: int
    chunk_type: str  # 'code_function', 'code_class', 'markdown_heading', 'prose', 'code_fence'
    content: str
    metadata: dict[str, Any]


class SmartCodeAwareChunker:
    """
    Smart chunker that preserves code structure and enables stitching
    Implements the coach's game plan for code-aware chunking
    """

    def __init__(
        self,
        max_tokens: int = 300,
        overlap_tokens: int = 64,  # Coach's recommendation: 64-token overlap
        preserve_code_units: bool = True,
        enable_stitching: bool = True,
    ):

        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.preserve_code_units = preserve_code_units
        self.enable_stitching = enable_stitching

        # Initialize base tokenizer
        self.base_chunker = TokenAwareChunker(max_tokens=max_tokens, overlap_tokens=overlap_tokens)

        # Compile regex patterns for code detection
        self.patterns = {
            "python_function": re.compile(r"^def\s+\w+\s*\([^)]*\)\s*:", re.MULTILINE),
            "python_class": re.compile(r"^class\s+\w+", re.MULTILINE),
            "markdown_heading": re.compile(r"^#{1,6}\s+.+$", re.MULTILINE),
            "code_fence": re.compile(r"```[\w]*\n.*?```", re.DOTALL),
            "docstring": re.compile(r'""".*?"""', re.DOTALL),
            "comment_block": re.compile(r"#.*$", re.MULTILINE),
        }

        logger.info(
            f"SmartCodeAwareChunker initialized: max_tokens={max_tokens}, "
            f"overlap_tokens={overlap_tokens}, preserve_code={preserve_code_units}"
        )

    def create_smart_chunks(self, text: str, file_path: str | None = None) -> list[dict[str, Any]]:
        """
        Create smart chunks that preserve code structure
        Returns chunks with metadata for stitching
        """
        try:
            file_extension = Path(file_path).suffix.lower() if file_path else None

            if file_extension in [".py", ".js", ".ts", ".java", ".cpp", ".c"]:
                return self._chunk_code_file(text, file_path)
            elif file_extension in [".md", ".rst", ".txt"]:
                return self._chunk_markdown_file(text, file_path)
            else:
                return self._chunk_generic_text(text, file_path)

        except Exception as e:
            logger.error(f"Smart chunking failed: {e}")
            # Fallback to base chunker
            return self._fallback_to_base_chunker(text)

    def _chunk_code_file(self, text: str, file_path: str | None) -> list[dict[str, Any]]:
        """Chunk code files preserving function/class boundaries"""
        chunks = []

        # Find all function and class boundaries
        boundaries = self._find_code_boundaries(text)

        # Group boundaries into logical units
        logical_units = self._group_code_boundaries(boundaries)

        for unit in logical_units:
            unit_chunks = self._chunk_code_logical_unit(unit, text)
            chunks.extend(unit_chunks)

        return chunks

    def _find_code_boundaries(self, text: str) -> list[ChunkBoundary]:
        """Find all code boundaries in the text"""
        boundaries = []

        # Find function definitions
        for match in self.patterns["python_function"].finditer(text):
            boundaries.append(
                ChunkBoundary(
                    start_pos=match.start(),
                    end_pos=match.end(),
                    chunk_type="code_function",
                    content=match.group(),
                    metadata={"function_name": match.group().split("(")[0].split()[-1]},
                )
            )

        # Find class definitions
        for match in self.patterns["python_class"].finditer(text):
            boundaries.append(
                ChunkBoundary(
                    start_pos=match.start(),
                    end_pos=match.end(),
                    chunk_type="code_class",
                    content=match.group(),
                    metadata={"class_name": match.group().split()[-1]},
                )
            )

        # Find docstrings
        for match in self.patterns["docstring"].finditer(text):
            boundaries.append(
                ChunkBoundary(
                    start_pos=match.start(),
                    end_pos=match.end(),
                    chunk_type="docstring",
                    content=match.group(),
                    metadata={"docstring_length": len(match.group())},
                )
            )

        # Sort boundaries by position
        boundaries.sort(key=lambda x: x.start_pos)
        return boundaries

    def _group_code_boundaries(self, boundaries: list[ChunkBoundary]) -> list[dict[str, Any]]:
        """Group boundaries into logical units (function + docstring + body)"""
        units = []

        for i, boundary in enumerate(boundaries):
            if boundary.chunk_type == "code_function":
                # Find the end of this function
                next_boundary = boundaries[i + 1] if i + 1 < len(boundaries) else None

                # Estimate function end (look for next function/class or end of file)
                if next_boundary:
                    end_pos = next_boundary.start_pos
                else:
                    end_pos = len(boundary.content) + 1000  # Conservative estimate

                units.append(
                    {
                        "type": "function_unit",
                        "start_pos": boundary.start_pos,
                        "end_pos": end_pos,
                        "function_name": boundary.metadata["function_name"],
                        "boundaries": [boundary],
                    }
                )

        return units

    def _chunk_code_logical_unit(self, unit: dict[str, Any], text: str) -> list[dict[str, Any]]:
        """Chunk a logical code unit (e.g., function) while preserving structure"""
        unit_text = text[unit["start_pos"] : unit["end_pos"]]

        # If unit is small enough, keep it as one chunk
        if self.base_chunker.count_tokens(unit_text) <= self.max_tokens:
            return [
                {
                    "id": f"unit_{unit['function_name']}_0",
                    "text": unit_text,
                    "chunk_type": "code_function",
                    "function_name": unit["function_name"],
                    "start_pos": unit["start_pos"],
                    "end_pos": unit["end_pos"],
                    "metadata": {"is_complete_function": True, "stitching_key": f"func_{unit['function_name']}"},
                }
            ]

        # If unit is too large, chunk it with overlap
        chunks = []
        unit_chunks = self.base_chunker.create_chunks(unit_text)

        for i, chunk_text in enumerate(unit_chunks):
            chunks.append(
                {
                    "id": f"unit_{unit['function_name']}_{i}",
                    "text": chunk_text,
                    "chunk_type": "code_function",
                    "function_name": unit["function_name"],
                    "start_pos": unit["start_pos"] + (i * len(chunk_text)),
                    "end_pos": unit["start_pos"] + ((i + 1) * len(chunk_text)),
                    "metadata": {
                        "is_complete_function": False,
                        "chunk_index": i,
                        "total_chunks": len(unit_chunks),
                        "stitching_key": f"func_{unit['function_name']}",
                    },
                }
            )

        return chunks

    def _chunk_markdown_file(self, text: str, file_path: str | None) -> list[dict[str, Any]]:
        """Chunk markdown files preserving heading structure"""
        chunks = []

        # Find all heading boundaries
        boundaries = self._find_markdown_boundaries(text)

        # Group boundaries into logical units
        logical_units = self._group_markdown_boundaries(boundaries, text)

        for unit in logical_units:
            unit_chunks = self._chunk_markdown_logical_unit(unit, text)
            chunks.extend(unit_chunks)

        return chunks

    def _find_markdown_boundaries(self, text: str) -> list[ChunkBoundary]:
        """Find all markdown heading boundaries in the text"""
        boundaries = []
        for match in self.patterns["markdown_heading"].finditer(text):
            boundaries.append(
                ChunkBoundary(
                    start_pos=match.start(),
                    end_pos=match.end(),
                    chunk_type="markdown_heading",
                    content=match.group(),
                    metadata={"heading_level": len(match.group().split("#")[0])},
                )
            )
        return boundaries

    def _group_markdown_boundaries(self, boundaries: list[ChunkBoundary], text: str) -> list[dict[str, Any]]:
        """Group markdown boundaries into logical units (heading + content)"""
        units = []
        current_unit = {"heading": "Introduction", "content": [], "boundaries": [], "start_pos": 0}

        for boundary in boundaries:
            if boundary.chunk_type == "markdown_heading":
                # Save previous unit
                if current_unit["content"]:
                    units.append(
                        {
                            "type": "markdown_unit",
                            "start_pos": current_unit["start_pos"],
                            "end_pos": boundary.start_pos,
                            "heading": current_unit["heading"],
                            "content": "\n".join(current_unit["content"]).strip(),
                            "boundaries": current_unit["boundaries"],
                        }
                    )

                # Start new unit
                current_unit = {
                    "heading": boundary.metadata["heading_level"],
                    "content": [],
                    "boundaries": [boundary],
                    "start_pos": boundary.start_pos,
                }
            else:
                current_unit["content"].append(boundary.content)
                current_unit["boundaries"].append(boundary)

        # Add final unit
        if current_unit["content"]:
            units.append(
                {
                    "type": "markdown_unit",
                    "start_pos": current_unit["start_pos"],
                    "end_pos": len(text),  # Now text is properly defined
                    "heading": current_unit["heading"],
                    "content": "\n".join(current_unit["content"]).strip(),
                    "boundaries": current_unit["boundaries"],
                }
            )

        return units

    def _chunk_markdown_logical_unit(self, unit: dict[str, Any], text: str) -> list[dict[str, Any]]:
        """Chunk a logical markdown unit (e.g., heading + content) while preserving structure"""
        unit_text = text[unit["start_pos"] : unit["end_pos"]]

        # If unit is small enough, keep it as one chunk
        if self.base_chunker.count_tokens(unit_text) <= self.max_tokens:
            return [
                {
                    "id": f"markdown_{unit['heading']}_0",
                    "text": unit_text,
                    "chunk_type": "markdown_section",
                    "heading": unit["heading"],
                    "start_pos": unit["start_pos"],
                    "end_pos": unit["end_pos"],
                    "metadata": {"is_complete_section": True, "stitching_key": f"md_{unit['heading']}"},
                }
            ]

        # If unit is too large, chunk it with overlap
        chunks = []
        unit_chunks = self.base_chunker.create_chunks(unit_text)

        for i, chunk_text in enumerate(unit_chunks):
            chunks.append(
                {
                    "id": f"markdown_{unit['heading']}_{i}",
                    "text": chunk_text,
                    "chunk_type": "markdown_section",
                    "heading": unit["heading"],
                    "start_pos": unit["start_pos"] + (i * len(chunk_text)),
                    "end_pos": unit["start_pos"] + ((i + 1) * len(chunk_text)),
                    "metadata": {
                        "is_complete_section": False,
                        "chunk_index": i,
                        "total_chunks": len(unit_chunks),
                        "stitching_key": f"md_{unit['heading']}",
                    },
                }
            )

        return chunks

    def _chunk_generic_text(self, text: str, file_path: str | None) -> list[dict[str, Any]]:
        """Chunk generic text files"""
        chunks = []
        base_chunks = self.base_chunker.create_chunks(text)

        for i, chunk_text in enumerate(base_chunks):
            chunks.append(
                {
                    "id": f"generic_chunk_{i}",
                    "text": chunk_text,
                    "chunk_type": "generic_text",
                    "metadata": {"chunk_index": i, "stitching_key": f"generic_{i}"},
                }
            )

        return chunks

    def stitch_adjacent_chunks(
        self, chunks: list[dict[str, Any]], query_type: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Stitch adjacent chunks when re-ranking
        Implements the coach's stitching strategy
        """
        if not self.enable_stitching:
            return chunks

        stitched_chunks = []
        i = 0

        while i < len(chunks):
            current_chunk = chunks[i]

            # Look for adjacent chunks that can be stitched
            if i + 1 < len(chunks):
                next_chunk = chunks[i + 1]

                # Check if chunks belong to the same logical unit
                if current_chunk["metadata"].get("stitching_key") == next_chunk["metadata"].get("stitching_key"):

                    # Stitch them together
                    stitched_text = current_chunk["text"] + "\n\n" + next_chunk["text"]

                    # Only stitch if the result is within token limits
                    if self.base_chunker.count_tokens(stitched_text) <= self.max_tokens * 1.5:
                        stitched_chunk = {
                            "id": f"{current_chunk['id']}_stitched",
                            "text": stitched_text,
                            "chunk_type": current_chunk["chunk_type"],
                            "metadata": {
                                **current_chunk["metadata"],
                                "stitched": True,
                                "original_chunks": [current_chunk["id"], next_chunk["id"]],
                            },
                        }

                        stitched_chunks.append(stitched_chunk)
                        i += 2  # Skip both chunks
                        continue

            # No stitching possible, keep original chunk
            stitched_chunks.append(current_chunk)
            i += 1

        logger.info(f"Stitched {len(chunks)} chunks into {len(stitched_chunks)} chunks")
        return stitched_chunks

    def _fallback_to_base_chunker(self, text: str) -> list[dict[str, Any]]:
        """Fallback to base chunker if smart chunking fails"""
        logger.warning("Falling back to base chunker")
        base_chunks = self.base_chunker.create_chunks(text)

        chunks = []
        for i, chunk_text in enumerate(base_chunks):
            chunks.append(
                {
                    "id": f"fallback_chunk_{i}",
                    "text": chunk_text,
                    "chunk_type": "fallback",
                    "metadata": {"chunk_index": i, "fallback": True},
                }
            )

        return chunks


def create_smart_chunker(
    max_tokens: int = 300, overlap_tokens: int = 64, preserve_code_units: bool = True, enable_stitching: bool = True
) -> SmartCodeAwareChunker:
    """Factory function to create a smart code-aware chunker"""
    return SmartCodeAwareChunker(
        max_tokens=max_tokens,
        overlap_tokens=overlap_tokens,
        preserve_code_units=preserve_code_units,
        enable_stitching=enable_stitching,
    )
