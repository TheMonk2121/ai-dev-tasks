#!/usr/bin/env python3
"""
Enhanced Atlas Chunking Strategy
Implements semantic chunking with overlap and context preservation
"""

import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime

import psycopg2
from sentence_transformers import SentenceTransformer


@dataclass
class ChunkMetadata:
    """Metadata for a semantic chunk."""

    chunk_type: str  # 'conversation', 'decision', 'suggestion', 'code', 'error', 'context'
    source_turn_id: str
    chunk_index: int
    total_chunks: int
    overlap_start: int
    overlap_end: int
    entities: list[str]
    topics: list[str]
    confidence: float


class AtlasEnhancedChunking:
    """Enhanced chunking strategy for Atlas graph storage."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn: str = dsn or os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
        self.embedder: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")
        self.embedding_dim: int = 384

        # Chunking parameters (standards compliant)
        self.max_chunk_size: int = 500  # tokens (350-600 range)
        self.overlap_size: int = 100  # tokens (20-25% of 500 = 100-125)
        self.min_chunk_size: int = 100  # tokens

    def chunk_conversation_turn(
        self, session_id: str, role: str, content: str, metadata: dict[str, str | bool] | None = None
    ) -> list[str]:
        """Chunk a conversation turn into semantic pieces."""
        chunks = []

        # 1. Extract structured content first
        structured_chunks = self._extract_structured_content(content, role)

        # 2. Create semantic chunks from remaining content
        if structured_chunks:
            remaining_content = self._remove_structured_content(content, structured_chunks)
            semantic_chunks = self._create_semantic_chunks(remaining_content)
        else:
            semantic_chunks = self._create_semantic_chunks(content)

        # 3. Combine and create nodes
        all_chunks = structured_chunks + semantic_chunks

        for i, chunk_data in enumerate(all_chunks):
            chunk_id = f"chunk_{session_id}_{int(time.time())}_{i}"

            # Create chunk node
            raw_metadata = chunk_data.get("metadata", {})
            if not isinstance(raw_metadata, dict):
                final_metadata: dict[str, str | int | float | bool | None] = {}
            else:
                # Convert to the expected type
                final_metadata: dict[str, str | int | float | bool | None] = {}
                for k, v in raw_metadata.items():
                    if isinstance(v, (str, int, float, bool)) or v is None:
                        final_metadata[k] = v
                    else:
                        final_metadata[k] = str(v)

            parent_turn_id = chunk_data.get("parent_turn_id")
            if not isinstance(parent_turn_id, str):
                parent_turn_id = None

            self._create_chunk_node(
                chunk_id=chunk_id,
                session_id=session_id,
                role=role,
                content=str(chunk_data["content"]),
                chunk_type=str(chunk_data["type"]),
                metadata=final_metadata,
                parent_turn_id=parent_turn_id,
                chunk_index=i,
                total_chunks=len(all_chunks),
            )

            chunks.append(chunk_id)

        return chunks

    def _extract_structured_content(
        self, content: str, role: str
    ) -> list[dict[str, str | dict[str, str | float] | None]]:
        """Extract structured content like decisions, suggestions, code blocks."""
        structured_chunks = []

        # Extract decisions
        decisions = self._extract_decisions(content)
        for decision in decisions:
            structured_chunks.append(
                {"content": decision, "type": "decision", "metadata": {"extracted_from": role, "confidence": 0.9}}
            )

        # Extract suggestions
        suggestions = self._extract_suggestions(content)
        for suggestion in suggestions:
            structured_chunks.append(
                {"content": suggestion, "type": "suggestion", "metadata": {"extracted_from": role, "confidence": 0.9}}
            )

        # Extract code blocks
        code_blocks = self._extract_code_blocks(content)
        for code in code_blocks:
            structured_chunks.append(
                {
                    "content": code["code"],
                    "type": "code",
                    "metadata": {"language": code["language"], "extracted_from": role, "confidence": 0.95},
                }
            )

        # Extract error messages
        errors = self._extract_error_messages(content)
        for error in errors:
            structured_chunks.append(
                {"content": error, "type": "error", "metadata": {"extracted_from": role, "confidence": 0.9}}
            )

        return structured_chunks

    def _create_semantic_chunks(self, content: str) -> list[dict[str, str | dict[str, int] | None]]:
        """Create semantic chunks with overlap from remaining content."""
        if len(content) < self.min_chunk_size:
            return [{"content": content, "type": "conversation", "metadata": {}}]

        # Simple sentence-based chunking with overlap
        sentences = self._split_into_sentences(content)
        chunks = []

        current_chunk = ""
        chunk_start = 0

        for i, sentence in enumerate(sentences):
            # Check if adding this sentence would exceed max size
            if len(current_chunk + sentence) > self.max_chunk_size and current_chunk:
                # Create chunk
                chunks.append(
                    {
                        "content": current_chunk.strip(),
                        "type": "conversation",
                        "metadata": {
                            "chunk_start": chunk_start,
                            "chunk_end": chunk_start + len(current_chunk),
                            "sentence_count": current_chunk.count("."),
                        },
                    }
                )

                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(sentences, i, self.overlap_size)
                current_chunk = " ".join(overlap_sentences) + " " + sentence
                chunk_start = chunk_start + len(current_chunk) - len(sentence)
            else:
                current_chunk += " " + sentence

        # Add final chunk
        if current_chunk.strip():
            chunks.append(
                {
                    "content": current_chunk.strip(),
                    "type": "conversation",
                    "metadata": {
                        "chunk_start": chunk_start,
                        "chunk_end": chunk_start + len(current_chunk),
                        "sentence_count": current_chunk.count("."),
                    },
                }
            )

        return chunks

    def _extract_decisions(self, content: str) -> list[str]:
        """Extract decisions from content."""
        decisions = []
        decision_patterns = [
            r"we should (.+?)(?:\.|$)",
            r"let's (.+?)(?:\.|$)",
            r"i'll (.+?)(?:\.|$)",
            r"we'll (.+?)(?:\.|$)",
            r"decision: (.+?)(?:\.|$)",
            r"decided to (.+?)(?:\.|$)",
            r"i think we should (.+?)(?:\.|$)",
        ]

        for pattern in decision_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            decisions.extend(matches)

        return decisions

    def _extract_suggestions(self, content: str) -> list[str]:
        """Extract suggestions from content."""
        suggestions = []
        suggestion_patterns = [
            r"you should (.+?)(?:\.|$)",
            r"try (.+?)(?:\.|$)",
            r"consider (.+?)(?:\.|$)",
            r"suggest (.+?)(?:\.|$)",
            r"recommend (.+?)(?:\.|$)",
            r"maybe (.+?)(?:\.|$)",
            r"i suggest (.+?)(?:\.|$)",
        ]

        for pattern in suggestion_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            suggestions.extend(matches)

        return suggestions

    def _extract_code_blocks(self, content: str) -> list[dict[str, str]]:
        """Extract code blocks from content."""
        code_blocks = []

        # Match code blocks with language specification
        code_pattern = r"```(\w+)?\n(.*?)\n```"
        matches = re.findall(code_pattern, content, re.DOTALL)

        for match in matches:
            language: str | None = match[0] if match[0] else None
            code: str = match[1] if match[1] else ""
            code_blocks.append({"language": str(language) if language else "text", "code": str(code).strip()})

        return code_blocks

    def _extract_error_messages(self, content: str) -> list[str]:
        """Extract error messages from content."""
        errors = []
        error_patterns = [
            r"error: (.+?)(?:\n|$)",
            r"exception: (.+?)(?:\n|$)",
            r"failed: (.+?)(?:\n|$)",
            r"traceback: (.+?)(?:\n|$)",
        ]

        for pattern in error_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            errors.extend(matches)

        return errors

    def _split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _get_overlap_sentences(self, sentences: list[str], current_index: int, overlap_size: int) -> list[str]:
        """Get overlap sentences for chunk continuity."""
        overlap_sentences = []
        current_length = 0

        # Go backwards from current position
        for i in range(current_index - 1, -1, -1):
            if current_length + len(sentences[i]) > overlap_size:
                break
            overlap_sentences.insert(0, sentences[i])
            current_length += len(sentences[i])

        return overlap_sentences

    def _remove_structured_content(
        self, content: str, structured_chunks: list[dict[str, str | dict[str, str | float] | None]]
    ) -> str:
        """Remove already extracted structured content from text."""
        remaining = content

        for chunk in structured_chunks:
            # Simple removal - could be more sophisticated
            remaining = remaining.replace(str(chunk["content"]), "")

        return remaining.strip()

    def _create_chunk_node(
        self,
        chunk_id: str,
        session_id: str,
        role: str,
        content: str,
        chunk_type: str,
        metadata: dict[str, str | int | float | bool | None],
        parent_turn_id: str | None = None,
        chunk_index: int = 0,
        total_chunks: int = 1,
    ) -> None:
        """Create a chunk node in the Atlas graph."""
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                # Get embedding for chunk
                embedding = self.embedder.encode(content)

                # Enhanced metadata
                enhanced_metadata = {
                    **metadata,
                    "role": role,
                    "session_id": session_id,
                    "chunk_type": chunk_type,
                    "chunk_index": chunk_index,
                    "total_chunks": total_chunks,
                    "parent_turn_id": parent_turn_id,
                    "chunk_size": len(content),
                    "created_at": datetime.now().isoformat(),
                }

                # Create chunk node
                cur.execute(
                    """
                    INSERT INTO atlas_node (node_id, node_type, title, content, metadata, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (node_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding,
                        updated_at = CURRENT_TIMESTAMP
                """,
                    (
                        chunk_id,
                        f"chunk_{chunk_type}",
                        f"{chunk_type}: {content[:100]}...",
                        content,
                        json.dumps(enhanced_metadata),
                        embedding.tolist(),
                    ),
                )

                # Create edges to parent turn if exists
                if parent_turn_id is not None:
                    cur.execute(
                        """
                        INSERT INTO atlas_edge (source_node_id, target_node_id, edge_type, evidence, weight)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (source_node_id, target_node_id, edge_type) DO NOTHING
                    """,
                        (parent_turn_id, chunk_id, "contains", f"Parent turn contains {chunk_type} chunk", 1.0),
                    )

                # Create sequential edges between chunks
                if chunk_index > 0:
                    prev_chunk_id = f"chunk_{session_id}_{int(time.time())}_{chunk_index - 1}"
                    cur.execute(
                        """
                        INSERT INTO atlas_edge (source_node_id, target_node_id, edge_type, evidence, weight)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (source_node_id, target_node_id, edge_type) DO NOTHING
                    """,
                        (
                            prev_chunk_id,
                            chunk_id,
                            "follows",
                            f"Sequential chunk {chunk_index - 1} -> {chunk_index}",
                            0.8,
                        ),
                    )

                conn.commit()


def main() -> None:
    """Test enhanced chunking strategy."""
    print("🧩 Testing Enhanced Atlas Chunking")

    chunker = AtlasEnhancedChunking()

    # Test conversation with mixed content
    test_content = """
    I think we should implement the Atlas graph storage system. It would preserve connections between conversations and decisions much better than the current vector-only approach.
    
    Here's some code to get started:
    ```python
    def store_conversation_turn(session_id, content):
        embedding = embedder.encode(content)
        # Store in graph
    ```
    
    We could also consider using semantic chunking with overlap. This would help maintain context across chunk boundaries.
    
    Error: The current implementation doesn't handle long conversations well.
    
    Let me suggest we add a chunking strategy that:
    1. Extracts structured content (decisions, code, errors)
    2. Creates semantic chunks with overlap
    3. Maintains relationships between chunks
    """

    chunks = chunker.chunk_conversation_turn(
        session_id="test_enhanced_chunking", role="user", content=test_content, metadata={"test": True}
    )

    print(f"✅ Created {len(chunks)} chunks:")
    for i, chunk_id in enumerate(chunks):
        print(f"  {i+1}. {chunk_id}")

    print("🎯 Enhanced chunking is working!")


if __name__ == "__main__":
    main()
