"""
Document windowing for precise cross-encoder reranking.

Segments candidate documents into overlapping windows (120-180 tokens)
before reranking to improve relevance scoring granularity while maintaining
document context and traceability for citation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

try:
    import tiktoken

    ENCODER = tiktoken.get_encoding("cl100k_base")

    def count_tokens(text: str) -> int:
        return len(ENCODER.encode(text))

    def decode_tokens(tokens: list[int]) -> str:
        return ENCODER.decode(tokens)

except ImportError:
    # Fallback to word-based approximation
    def count_tokens(text: str) -> int:
        return len(text.split()) * 1.3  # rough token approximation

    def decode_tokens(tokens: list[int]) -> str:
        return ""  # not implemented for fallback


@dataclass
class DocumentWindow:
    """A windowed segment of a document for reranking."""

    window_id: str  # unique identifier for this window
    document_id: str  # original document ID
    text: str  # window content
    start_token: int  # start position in original document (token offset)
    end_token: int  # end position in original document (token offset)
    window_index: int  # sequential window number within document
    original_score: float  # score from fusion/previous stage

    # Citation support
    start_char: int | None = None  # character offset for citation
    end_char: int | None = None  # character offset for citation

    # Context preservation
    doc_title: str | None = None
    doc_metadata: dict[str, Any] | None = None


class DocumentWindower:
    """Creates overlapping windows from candidate documents for reranking."""

    def __init__(
        self,
        window_size_tokens: int = 150,
        overlap_pct: int = 33,
        min_window_tokens: int = 50,
        preserve_doc_boundaries: bool = True,
        preserve_paragraph_boundaries: bool = True,
    ):
        self.window_size_tokens = window_size_tokens
        self.overlap_tokens = max(1, int(window_size_tokens * overlap_pct / 100))
        self.min_window_tokens = min_window_tokens
        self.preserve_doc_boundaries = preserve_doc_boundaries
        self.preserve_paragraph_boundaries = preserve_paragraph_boundaries

        # Stride for non-overlapping portion
        self.stride_tokens = self.window_size_tokens - self.overlap_tokens

    def create_windows(self, candidates: list[dict[str, Any]], max_windows_per_doc: int = 3) -> list[DocumentWindow]:
        """
        Create windows from a list of candidate documents.

        Args:
            candidates: List of dicts with keys: document_id, text, score, metadata
            max_windows_per_doc: Maximum windows to create per document

        Returns:
            List of DocumentWindow objects ready for reranking
        """
        windows = []

        for candidate in candidates:
            doc_id = candidate.get("document_id") or candidate.get("id", "unknown")
            text = candidate.get("text") or candidate.get("content", "")
            score = candidate.get("score", 0.0)
            metadata = candidate.get("metadata", {})

            if not text.strip():
                continue

            # Create windows for this document
            doc_windows = self._create_windows_for_document(
                document_id=doc_id, text=text, original_score=score, metadata=metadata, max_windows=max_windows_per_doc
            )

            windows.extend(doc_windows)

        return windows

    def _create_windows_for_document(
        self,
        document_id: str,
        text: str,
        original_score: float,
        metadata: dict[str, Any] | None = None,
        max_windows: int = 3,
    ) -> list[DocumentWindow]:
        """Create overlapping windows for a single document."""

        if not text.strip():
            return []

        # Handle short documents
        token_count = count_tokens(text)
        if token_count <= self.window_size_tokens:
            return [
                DocumentWindow(
                    window_id=f"{document_id}_w0",
                    document_id=document_id,
                    text=text,
                    start_token=0,
                    end_token=token_count,
                    window_index=0,
                    original_score=original_score,
                    start_char=0,
                    end_char=len(text),
                    doc_metadata=metadata,
                )
            ]

        # Split into segments for windowing
        if self.preserve_paragraph_boundaries:
            segments = self._split_by_paragraphs(text)
        else:
            segments = [text]  # Single segment

        windows = []
        current_token_pos = 0
        window_index = 0

        for segment in segments:
            segment_windows = self._create_windows_for_segment(
                segment=segment,
                document_id=document_id,
                original_score=original_score,
                metadata=metadata,
                start_token_offset=current_token_pos,
                start_window_index=window_index,
            )

            windows.extend(segment_windows)
            window_index += len(segment_windows)
            current_token_pos += count_tokens(segment)

            # Respect max windows limit
            if len(windows) >= max_windows:
                break

        return windows[:max_windows]

    def _create_windows_for_segment(
        self,
        segment: str,
        document_id: str,
        original_score: float,
        metadata: dict[str, Any] | None,
        start_token_offset: int = 0,
        start_window_index: int = 0,
    ) -> list[DocumentWindow]:
        """Create overlapping windows for a text segment."""

        segment_tokens = count_tokens(segment)

        # Handle short segments
        if segment_tokens <= self.window_size_tokens:
            return [
                DocumentWindow(
                    window_id=f"{document_id}_w{start_window_index}",
                    document_id=document_id,
                    text=segment,
                    start_token=start_token_offset,
                    end_token=start_token_offset + segment_tokens,
                    window_index=start_window_index,
                    original_score=original_score,
                    doc_metadata=metadata,
                )
            ]

        windows = []
        words = segment.split()

        # Approximate token positions using word boundaries
        current_pos = 0
        current_tokens = 0
        window_index = start_window_index

        while current_pos < len(words):
            # Collect words for this window
            window_words = []
            window_token_count = 0
            word_pos = current_pos

            while word_pos < len(words) and window_token_count < self.window_size_tokens:
                word = words[word_pos]
                word_tokens = count_tokens(word + " ")  # approximate

                if window_token_count + word_tokens > self.window_size_tokens and window_words:
                    break

                window_words.append(word)
                window_token_count += word_tokens
                word_pos += 1

            if not window_words:
                break

            # Create window
            window_text = " ".join(window_words)
            if len(window_text.strip()) >= self.min_window_tokens:
                window = DocumentWindow(
                    window_id=f"{document_id}_w{window_index}",
                    document_id=document_id,
                    text=window_text,
                    start_token=start_token_offset + current_tokens,
                    end_token=start_token_offset + current_tokens + window_token_count,
                    window_index=window_index,
                    original_score=original_score,
                    doc_metadata=metadata,
                )
                windows.append(window)
                window_index += 1

            # Move to next window position (with overlap)
            stride_words = max(1, len(window_words) - int(len(window_words) * self.overlap_pct / 100))
            current_pos += stride_words
            current_tokens += count_tokens(" ".join(window_words[:stride_words]))

        return windows

    def _split_by_paragraphs(self, text: str) -> list[str]:
        """Split text into paragraphs while preserving structure."""

        # Split on double newlines (paragraph boundaries)
        paragraphs = re.split(r"\n\s*\n", text)

        # Filter empty paragraphs
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        # Merge very short paragraphs with next one
        merged = []
        i = 0
        while i < len(paragraphs):
            current = paragraphs[i]

            # If current paragraph is very short, try to merge with next
            if i + 1 < len(paragraphs) and count_tokens(current) < self.min_window_tokens:
                next_para = paragraphs[i + 1]
                if count_tokens(current + "\n\n" + next_para) <= self.window_size_tokens:
                    merged.append(current + "\n\n" + next_para)
                    i += 2
                    continue

            merged.append(current)
            i += 1

        return merged or [text]  # fallback to original text

    def restore_document_context(
        self, ranked_windows: list[tuple[DocumentWindow, float]]
    ) -> dict[str, list[tuple[DocumentWindow, float]]]:
        """Group ranked windows back by document for context assembly."""

        doc_groups: dict[str, list[tuple[DocumentWindow, float]]] = {}

        for window, score in ranked_windows:
            doc_id = window.document_id
            if doc_id not in doc_groups:
                doc_groups[doc_id] = []
            doc_groups[doc_id].append((window, score))

        # Sort windows within each document by score (desc)
        for doc_id in doc_groups:
            doc_groups[doc_id].sort(key=lambda x: x[1], reverse=True)

        return doc_groups


def create_windower(config: dict[str, Any] | None = None) -> DocumentWindower:
    """Factory function to create a DocumentWindower from config."""

    if not config:
        return DocumentWindower()

    return DocumentWindower(
        window_size_tokens=config.get("window_size_tokens", 150),
        overlap_pct=config.get("overlap_pct", 33),
        min_window_tokens=config.get("min_window_tokens", 50),
        preserve_doc_boundaries=config.get("preserve_doc_boundaries", True),
        preserve_paragraph_boundaries=config.get("preserve_paragraph_boundaries", True),
    )
