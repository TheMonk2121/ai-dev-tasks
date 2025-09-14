from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, Union

import psycopg2
from psycopg2.extras import RealDictCursor
from sentence_transformers import SentenceTransformer

from src.common.db_dsn import resolve_dsn

#!/usr/bin/env python3
"""
Real Data Ingestion for Evaluation System
Ingests actual project documentation and files into the database.
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class RealDataIngester:
    """Ingests real project data into the database for evaluation."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embedding_dim = 384

        # Ingest metadata controls
        self.ingest_run_id = os.getenv("INGEST_RUN_ID") or f"ing-{os.getpid()}"
        self.chunk_variant = os.getenv("CHUNK_VARIANT", "md_512_o64_v2")
        self.chunk_size_cfg = int(os.getenv("CHUNK_SIZE", "512"))
        self.chunk_overlap_cfg = int(os.getenv("CHUNK_OVERLAP", "64"))
        # Best-effort source commit
        try:

            self.source_commit = (
                os.getenv("SOURCE_COMMIT")
                or subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(project_root)).decode().strip()
            )
        except Exception:
            self.source_commit = "unknown"

        # Optional targeted re-ingest file list
        self.include_paths_file = os.getenv("INCLUDE_PATHS_FILE")
        self._explicit_paths: set[str] = set()
        if self.include_paths_file and Path(self.include_paths_file).exists():
            try:
                self._explicit_paths = {
                    p.strip() for p in Path(self.include_paths_file).read_text().splitlines() if p.strip()
                }
                print(f"🎯 Targeted re-ingest enabled for {len(self._explicit_paths)} paths")
            except Exception as e:
                print(f"⚠️ Failed reading INCLUDE_PATHS_FILE: {e}")

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
            "600_archives",
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

    def scan_project_files(self) -> list[dict[str, Any]]:
        """Scan project for files to ingest."""
        print("🔍 Scanning project for files to ingest...")

        files = []
        for root, dirs, filenames in os.walk(project_root):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for filename in filenames:
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(project_root)

                # Skip excluded files
                if file_path.suffix in self.exclude_extensions:
                    continue

                # Check if file matches include patterns
                if self._should_include_file(file_path):
                    if self._explicit_paths and str(rel_path) not in self._explicit_paths:
                        continue
                    files.append(
                        {
                            "file_path": str(rel_path),
                            "absolute_path": str(file_path),
                            "file_name": filename,
                            "content_type": self._get_content_type(file_path),
                        }
                    )

        print(f"   📁 Found {len(files)} files to process")
        return files

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

    def chunk_content(self, content: str, file_path: str, content_type: str) -> list[dict[str, Any]]:
        """Chunk content into smaller pieces for vector search."""
        # Simple chunking strategy - split by paragraphs and limit size
        paragraphs = content.split("\n\n")
        chunks = []

        current_chunk = ""
        chunk_index = 0

        for paragraph in paragraphs:
            # If adding this paragraph would make chunk too large, save current chunk
            if len(current_chunk) + len(paragraph) > self.chunk_size_cfg and current_chunk:
                chunks.append(
                    {
                        "chunk_index": chunk_index,
                        "content": current_chunk.strip(),
                        "metadata": {
                            "file_path": file_path,
                            "chunk_type": "paragraph",
                            "chunk_size": len(current_chunk),
                            "ingest_run_id": self.ingest_run_id,
                            "chunk_variant": self.chunk_variant,
                            "chunker_name": content_type,
                            "chunk_overlap": self.chunk_overlap_cfg,
                            "source_path": file_path,
                            "source_commit": self.source_commit,
                        },
                    }
                )
                current_chunk = paragraph
                chunk_index += 1
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph

        # Add final chunk
        if current_chunk.strip():
            chunks.append(
                {
                    "chunk_index": chunk_index,
                    "content": current_chunk.strip(),
                    "metadata": {
                        "file_path": file_path,
                        "chunk_type": "paragraph",
                        "chunk_size": len(current_chunk),
                        "ingest_run_id": self.ingest_run_id,
                        "chunk_variant": self.chunk_variant,
                        "chunker_name": content_type,
                        "chunk_overlap": self.chunk_overlap_cfg,
                        "source_path": file_path,
                        "source_commit": self.source_commit,
                    },
                }
            )

        return chunks

    def generate_embeddings(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Generate embeddings for content chunks."""
        print(f"   🧠 Generating embeddings for {len(chunks)} chunks...")

        texts = [chunk["content"] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)

        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i].tolist()

        return chunks

    def ingest_documents(self, files: list[dict[str, Any]]) -> dict[int, str]:
        """Ingest documents into the database."""
        print("📄 Ingesting documents...")

        document_map = {}  # file_path -> document_id

        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for file_info in files:
                    file_path = file_info["file_path"]
                    absolute_path = file_info["absolute_path"]

                    # Read file content
                    content = self.read_file_content(Path(absolute_path))
                    content_sha = hashlib.sha256(content.encode()).hexdigest()

                    # Check if document already exists
                    cur.execute(
                        """
                        SELECT id FROM documents WHERE file_path = %s
                    """,
                        (file_path,),
                    )
                    existing = cur.fetchone()

                    if existing:
                        document_id = existing["id"]
                        print(f"   📄 {file_path} (existing, ID: {document_id})")
                    else:
                        # Insert new document (align to existing schema)
                        cur.execute(
                            """
                            INSERT INTO documents (filename, file_path, file_type, file_size, chunk_count, status, content_sha)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING id
                        """,
                            (
                                file_info["file_name"],
                                file_path,
                                file_info["content_type"],
                                len(content),
                                0,
                                "ingested",
                                content_sha,
                            ),
                        )
                        row = cur.fetchone()
                        document_id = row["id"] if row else None
                        if document_id is None:
                            raise RuntimeError("Failed to insert document record")
                        print(f"   📄 {file_path} (new, ID: {document_id})")

                    document_map[file_path] = document_id

        return document_map

    def ingest_chunks(self, files: list[dict[str, Any]], document_map: dict[int, str]) -> None:
        """Ingest document chunks with embeddings."""
        print("📝 Ingesting document chunks...")

        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for file_info in files:
                    file_path = file_info["file_path"]
                    absolute_path = file_info["absolute_path"]
                    document_id = document_map[file_path]

                    # Read and chunk content
                    content = self.read_file_content(Path(absolute_path))
                    chunks = self.chunk_content(content, file_path, file_info["content_type"])

                    if not chunks:
                        continue

                    # Generate embeddings
                    chunks = self.generate_embeddings(chunks)

                    # Clear existing chunks for this document
                    cur.execute(
                        """
                        DELETE FROM document_chunks WHERE document_id = %s
                    """,
                        (document_id,),
                    )

                    # Insert new chunks
                    for chunk in chunks:
                        cur.execute(
                            """
                            INSERT INTO document_chunks 
                            (document_id, chunk_index, content, embedding, metadata, filename, file_path)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                            (
                                document_id,
                                chunk["chunk_index"],
                                chunk["content"],
                                chunk["embedding"],
                                json.dumps(chunk["metadata"]),
                                file_info["file_name"],
                                file_path,
                            ),
                        )

                    print(f"   📝 {file_path}: {len(chunks)} chunks")

    def ingest_gold_cases(self) -> None:
        """Ingest gold evaluation cases."""
        print("🏆 Ingesting gold evaluation cases...")

        gold_cases_path = project_root / "evals" / "gold" / "v1" / "gold_cases.jsonl"
        if not gold_cases_path.exists():
            print("   ⚠️  Gold cases file not found, skipping")
            return

        with open(gold_cases_path) as f:
            cases = [json.loads(line) for line in f if line.strip()]

        print(f"   🏆 Found {len(cases)} gold cases")

        # Store gold cases in conversation_context for easy access
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Clear existing gold cases
                cur.execute(
                    """
                    DELETE FROM conversation_context 
                    WHERE context_type = 'gold_cases'
                """
                )

                # Insert gold cases

                for case in cases:
                    value_json = json.dumps(case)
                    context_hash = hashlib.sha256(value_json.encode()).hexdigest()
                    cur.execute(
                        """
                        INSERT INTO conversation_context 
                        (session_id, context_type, context_key, context_value, context_hash, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (session_id, context_type, context_key)
                        DO UPDATE SET 
                            context_value = EXCLUDED.context_value,
                            context_hash = EXCLUDED.context_hash,
                            metadata = EXCLUDED.metadata
                    """,
                        (
                            "gold_cases",
                            "gold_cases",
                            case.get("id", ""),
                            value_json,
                            context_hash,
                            json.dumps({"mode": case.get("mode"), "tags": case.get("tags", [])}),
                        ),
                    )

        print(f"   ✅ Ingested {len(cases)} gold cases")

    def verify_ingestion(self) -> None:
        """Verify that data was ingested successfully."""
        print("🔍 Verifying data ingestion...")

        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check document count
                cur.execute("SELECT COUNT(*) FROM documents")
                row = cur.fetchone()
                doc_count = (row and list(row.values())[0]) or 0
                print(f"   📄 Documents: {doc_count}")

                # Check chunk count
                cur.execute("SELECT COUNT(*) FROM document_chunks")
                row = cur.fetchone()
                chunk_count = (row and list(row.values())[0]) or 0
                print(f"   📝 Chunks: {chunk_count}")

                # Check chunks with embeddings
                cur.execute("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL")
                row = cur.fetchone()
                embedded_count = (row and list(row.values())[0]) or 0
                print(f"   🧠 Chunks with embeddings: {embedded_count}")

                # Check gold cases
                cur.execute("SELECT COUNT(*) FROM conversation_context WHERE context_type = 'gold_cases'")
                row = cur.fetchone()
                gold_count = (row and list(row.values())[0]) or 0
                print(f"   🏆 Gold cases: {gold_count}")

                # Sample some data
                cur.execute(
                    """
                    SELECT file_path, filename, file_type 
                    FROM documents 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """
                )
                recent_docs = cur.fetchall()
                print("   📋 Recent documents:")
                for doc in recent_docs:
                    print(f"      - {doc['file_path']} ({doc['filename']})")

    def main(self):
        """Main ingestion process."""
        print("🚀 Starting real data ingestion...")
        print("=" * 60)

        # Scan project files
        files = self.scan_project_files()
        if not files:
            print("❌ No files found to ingest")
            return 1

        # Ingest documents
        document_map = self.ingest_documents(files)

        # Ingest chunks with embeddings
        self.ingest_chunks(files, document_map)

        # Ingest gold cases
        self.ingest_gold_cases()

        # Verify ingestion
        self.verify_ingestion()

        print("\n✅ Real data ingestion completed successfully!")
        print("🎉 Database is now ready for evaluation")
        return 0


def main():
    """Main entry point."""
    dsn = resolve_dsn(strict=True)
    if not dsn:
        print("❌ No database DSN configured")
        print("   Set POSTGRES_DSN or DATABASE_URL environment variable")
        return 1

    ingester = RealDataIngester(dsn)
    return ingester.main()


if __name__ == "__main__":
    sys.exit(main())
