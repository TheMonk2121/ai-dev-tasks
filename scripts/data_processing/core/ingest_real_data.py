from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

import psycopg
from psycopg.rows import RealDictCursor

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, PreTrainedTokenizerBase

# Add project root (so `src` package is importable)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.common.db_dsn import resolve_dsn

# Embedding configuration
EMBEDDER_NAME = "BAAI/bge-small-en-v1.5"


def chunk_by_tokens(text: str, max_tokens: int = 220, overlap: int = 48, tokenizer: Any | None = None) -> Iterator[str]:
    """
    Chunk text by tokens with overlap, preserving context.

    Args:
        text: Input text to chunk
        max_tokens: Maximum tokens per chunk
        overlap: Number of tokens to overlap between chunks
        tokenizer: Tokenizer to use (defaults to BGE small tokenizer)

    Yields:
        Decoded text chunks
    """
    if tokenizer is None:
        tokenizer = AutoTokenizer.from_pretrained(EMBEDDER_NAME)

    # Tokenize without special tokens
    ids = tokenizer.encode(text, add_special_tokens=False)

    # Compute step size
    step = max_tokens - overlap

    # Chunk and decode
    for start in range(0, len(ids), step):
        piece = ids[start : start + max_tokens]
        if not piece:
            break

        # Decode the chunk
        chunk = tokenizer.decode(piece)

        # Optional: Attach headings/short lines to the chunk
        if start > 0:
            # Look back for potential headings or short lines to attach
            prev_lines = text[: text.find(chunk)].splitlines()
            if prev_lines:
                # Attach last line if it looks like a heading or is short
                last_line = prev_lines[-1].strip()
                if len(last_line) < 40 or last_line.startswith(("#", "##", "###")):
                    chunk = last_line + "\n" + chunk

        yield chunk


class RealDataIngester:
    """Ingests real project data into the database for evaluation."""

    dsn: str
    embedding_model: SentenceTransformer
    embedding_dim: int
    tokenizer: PreTrainedTokenizerBase
    ingest_run_id: str
    chunk_variant: str
    chunk_size_tokens: int
    chunk_overlap_tokens: int
    source_commit: str
    include_patterns: list[str]
    exclude_dirs: set[str]
    exclude_extensions: set[str]

    def __init__(self, dsn: str):
        self.dsn = dsn

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(EMBEDDER_NAME, device="cuda" if torch.cuda.is_available() else "cpu")
        self.embedding_model.max_seq_length = 512  # Safe for BGE small
        self.embedding_dim = 384

        # Initialize tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(EMBEDDER_NAME)

        # Ingest metadata controls
        self.ingest_run_id = os.getenv("INGEST_RUN_ID") or f"ing-{os.getpid()}"
        self.chunk_variant = os.getenv("CHUNK_VARIANT", "md_t220_o48_v3")
        self.chunk_size_tokens = int(os.getenv("CHUNK_SIZE_TOKENS", "220"))
        self.chunk_overlap_tokens = int(os.getenv("CHUNK_OVERLAP_TOKENS", "48"))

        # Best-effort source commit
        try:
            self.source_commit = (
                os.getenv("SOURCE_COMMIT")
                or subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(project_root)).decode().strip()
            )
        except Exception:
            self.source_commit = "unknown"

        # File patterns to include
        self.include_patterns = [
            "*.md",
            "*.py",
            "*.sh",
            "*.yaml",
            "*.yml",
            "*.json",
            "*.txt",
            "*.sql",
            "Dockerfile",
            "Makefile",
            "pyproject.toml",
            "requirements*.txt",
        ]

        # Directories to exclude
        self.exclude_dirs = {
            "node_modules",
            "venv",
            ".venv",
            ".git",
            "__pycache__",
            ".pytest_cache",
            "build",
            "dist",
            ".mypy_cache",
            ".ruff_cache",
            "logs",
            "metrics",
            "artifacts",
        }

        # File extensions to exclude
        self.exclude_extensions = {
            ".pyc",
            ".pyo",
            ".pyd",
            ".log",
            ".tmp",
            ".bak",
            ".swp",
            ".DS_Store",
        }

    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included based on patterns."""
        for pattern in self.include_patterns:
            if file_path.match(pattern):
                return True
        return False

    def _get_content_type(self, file_path: Path) -> str:
        """Determine content type based on file extension."""
        ext = file_path.suffix.lower()
        type_map = {
            ".md": "markdown",
            ".py": "python",
            ".sh": "shell",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".txt": "text",
            ".sql": "sql",
            ".toml": "toml",
            ".ini": "ini",
        }
        return type_map.get(ext, "text")

    def read_file_content(self, file_path: Path) -> str:
        """Read file content with proper encoding handling."""
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, encoding="latin-1") as f:
                    return f.read()
            except Exception:
                return f"[Binary file: {file_path.name}]"
        except Exception as e:
            return f"[Error reading file: {e}]"

    @staticmethod
    def _is_noise_line(raw_line: str) -> bool:
        """Return True when a line is safe to drop without harming retrieval."""

        stripped = raw_line.strip()
        if not stripped:
            return True

        lowered = stripped.lower()
        if lowered in {"table of contents", "toc", "contents"}:
            return True

        if stripped.startswith("<!--") and stripped.endswith("-->"):
            return True

        # Navigation bullets with no alphanumeric characters add little value
        if len(stripped) <= 4 and not any(ch.isalnum() for ch in stripped):
            return True

        return False

    def chunk_content(self, content: str, file_path: str, content_type: str) -> list[dict[str, Any]]:
        """Chunk content using token-based strategy."""

        filtered_lines = [line for line in content.splitlines() if not self._is_noise_line(line)]
        content = "\n".join(filtered_lines)

        # Chunk by tokens
        chunks = list(
            chunk_by_tokens(
                content, max_tokens=self.chunk_size_tokens, overlap=self.chunk_overlap_tokens, tokenizer=self.tokenizer
            )
        )

        # Post-filter chunks
        chunks = [chunk for chunk in chunks if len(chunk.strip()) >= 140]  # Matches retrieval guard

        # Prepare chunk metadata
        processed_chunks = []
        for chunk_index, chunk_content in enumerate(chunks):
            processed_chunks.append(
                {
                    "chunk_index": chunk_index,
                    "content": chunk_content.strip(),
                    "metadata": {
                        "file_path": file_path,
                        "chunk_type": "token-based",
                        "char_len": len(chunk_content),
                        "token_len": len(self.tokenizer.encode(chunk_content, add_special_tokens=False)),
                        "ingest_run_id": self.ingest_run_id,
                        "chunk_variant": self.chunk_variant,
                        "chunker_name": content_type,
                        "chunk_overlap_tokens": self.chunk_overlap_tokens,
                        "source_path": file_path,
                        "source_commit": self.source_commit,
                    },
                }
            )

        return processed_chunks

    def generate_embeddings(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Generate embeddings for content chunks."""
        print(f"   🧠 Generating embeddings for {len(chunks)} chunks...")

        # Prepare texts for embedding (passages don't need prefix)
        texts = [chunk["content"] for chunk in chunks]

        # Normalize embeddings (cosine similarity)
        embeddings = self.embedding_model.encode(texts, normalize_embeddings=True, show_progress_bar=True)

        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i].tolist()

        return chunks

    def ingest_documents(self, files: list[Path]) -> dict[str, dict[str, Any]]:
        """Ingest documents into the database."""
        document_map: dict[str, dict[str, Any]] = {}

        with psycopg.connect(self.dsn, cursor_factory=RealDictCursor) as conn:
            with conn.cursor() as cur:
                for file_path in files:
                    # Skip excluded directories and files
                    if any(exclude in str(file_path) for exclude in self.exclude_dirs):
                        continue
                    if file_path.suffix.lower() in self.exclude_extensions:
                        continue

                    # Skip non-matching patterns
                    if not self._should_include_file(file_path):
                        continue

                    # Read file content
                    content = self.read_file_content(file_path)

                    # Compute content hash
                    content_sha = hashlib.sha256(content.encode("utf-8")).hexdigest()

                    # Determine content type
                    content_type = self._get_content_type(file_path)

                    # Call provenance tracking function
                    cur.execute(
                        """
                        SELECT track_document_provenance(
                            %s, %s, %s, %s, %s
                        ) AS document_id
                    """,
                        (
                            str(file_path),
                            file_path.name,
                            content_sha,
                            content_type,
                            json.dumps(
                                {
                                    "ingest_run_id": self.ingest_run_id,
                                    "source_commit": self.source_commit,
                                    "embedder_name": EMBEDDER_NAME,
                                }
                            ),
                        ),
                    )

                    # Get the document ID (RealDictCursor returns a dict row)
                    result = cast(dict[str, Any] | None, cur.fetchone())
                    document_id = cast(int | None, (result or {}).get("document_id"))

                    if document_id is None:
                        print(f"   ⚠️ Failed to insert document for {file_path}")
                        continue

                    # Store document in map for later chunk reference
                    document_map[str(file_path)] = {
                        "id": document_id,
                        "content_sha": content_sha,
                    }

        return document_map

    def ingest_chunks(self, files: list[Path], document_map: dict[str, dict[str, Any]]):
        """Ingest document chunks into the database."""
        with psycopg.connect(self.dsn, cursor_factory=RealDictCursor) as conn:
            with conn.cursor() as cur:
                for file_path in files:
                    # Skip excluded directories and files
                    if any(exclude in str(file_path) for exclude in self.exclude_dirs):
                        continue
                    if file_path.suffix.lower() in self.exclude_extensions:
                        continue

                    # Skip non-matching patterns
                    if not self._should_include_file(file_path):
                        continue

                    # Read file content
                    content = self.read_file_content(file_path)

                    # Determine content type
                    content_type = self._get_content_type(file_path)

                    # Get document details
                    doc_details = document_map.get(str(file_path))
                    if not doc_details:
                        print(f"   ⚠️ Skipping chunks for {file_path}: No document record")
                        continue

                    # Chunk and embed content
                    chunks = self.chunk_content(content, str(file_path), content_type)
                    chunks = self.generate_embeddings(chunks)

                    # Insert chunks
                    for chunk in chunks:
                        cur.execute(
                            """
                            INSERT INTO document_chunks
                            (document_id, chunk_index, content, embedding, metadata)
                            VALUES (%s, %s, %s, %s, %s)
                        """,
                            (
                                doc_details["id"],
                                chunk["chunk_index"],
                                chunk["content"],
                                chunk["embedding"],
                                json.dumps(chunk["metadata"]),
                            ),
                        )

                # Commit transaction
                conn.commit()

    def main(self):
        """Main ingestion workflow."""
        print("🚀 Starting document ingestion...")
        print(f"   📂 Project root: {project_root}")

        # Find all files to ingest
        files: list[Path] = []
        for root, _, filenames in os.walk(project_root):
            for filename in filenames:
                file_path = Path(root) / filename

                # Skip excluded directories
                if any(exclude in str(file_path.parent) for exclude in self.exclude_dirs):
                    continue

                # Skip excluded file extensions
                if file_path.suffix.lower() in self.exclude_extensions:
                    continue

                # Skip non-matching patterns
                if not self._should_include_file(file_path):
                    continue

                files.append(file_path)

        print(f"   🔍 Found {len(files)} files to process")

        # Ingest documents first
        document_map = self.ingest_documents(files)

        # Then ingest chunks
        self.ingest_chunks(files, document_map)

        # Print summary
        with psycopg.connect(self.dsn, cursor_factory=RealDictCursor) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM document_chunk_stats")
                stats = cur.fetchone()
                if stats is not None:
                    s: dict[str, Any] = dict(stats)  # Convert RealDictCursor row to dict
                    print("\n📊 Ingestion Summary:")
                    print(f"Total Chunks: {s.get('total_chunks', 0)}")
                    print(f"Unique Documents: {s.get('unique_documents', 0)}")
                    avg_len = cast(float | int, s.get("avg_chunk_length", 0))
                    print(f"Avg Chunk Length: {avg_len:.2f}")
                    print(f"Min Chunk Length: {s.get('min_chunk_length', 0)}")
                    print(f"Max Chunk Length: {s.get('max_chunk_length', 0)}")
                    print(f"Small Chunks (< 140 chars): {s.get('small_chunks_count', 0)}")

        return 0


def main():
    """Entry point for script."""
    dsn: str = resolve_dsn(strict=True)
    ingester = RealDataIngester(dsn)
    return ingester.main()


if __name__ == "__main__":
    sys.exit(main())
