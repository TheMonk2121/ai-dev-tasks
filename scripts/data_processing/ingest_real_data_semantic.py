#!/usr/bin/env python3
"""
Real Data Ingestion with Semantic Chunking
Ingests actual project documentation and files into the database using semantic chunking.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

import psycopg2
from psycopg2.extras import RealDictCursor
from sentence_transformers import SentenceTransformer

if TYPE_CHECKING:
    import psycopg2.extensions

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import the semantic chunker
from scripts.semantic_chunker import SemanticChunker


class SemanticDataIngester:
    """Ingests real project data using semantic chunking for better retrieval."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        self.embedding_dim = 384

        # Chunking configuration - using project standards
        self.chunk_size = 450
        self.overlap_ratio = 0.10
        self.overlap_size = int(self.chunk_size * self.overlap_ratio)  # 45 characters

        # Initialize semantic chunker
        self.chunker = SemanticChunker(
            chunk_size=self.chunk_size, overlap_ratio=self.overlap_ratio, min_chunk_size=100, max_chunk_size=600
        )

        # Ingest metadata controls
        self.ingest_run_id = os.getenv("INGEST_RUN_ID") or f"ing-{os.getpid()}"
        self.chunk_variant = f"semantic_{self.chunk_size}_o{int(self.overlap_ratio*100)}"

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
            "600_deprecated",
        }

        # File extensions to exclude
        self.exclude_extensions = {
            ".pyc",
            ".pyo",
            ".pyd",
            ".so",
            ".dll",
            ".exe",
            ".bin",
            ".obj",
            ".o",
            ".a",
            ".lib",
            ".dylib",
            ".whl",
            ".tar.gz",
            ".zip",
            ".rar",
            ".7z",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".svg",
            ".ico",
            ".mp4",
            ".avi",
            ".mov",
            ".wmv",
            ".flv",
            ".webm",
            ".mp3",
            ".wav",
            ".flac",
            ".aac",
            ".ogg",
            ".wma",
        }

    def get_content_type(self, file_path: Path) -> str:
        """Determine content type based on file extension."""
        suffix = file_path.suffix.lower()

        if suffix in [".md", ".markdown"]:
            return "markdown"
        elif suffix == ".py":
            return "python"
        elif suffix in [".yaml", ".yml"]:
            return "yaml"
        elif suffix == ".json":
            return "json"
        elif suffix in [".sh", ".bash"]:
            return "shell"
        elif suffix == ".sql":
            return "sql"
        elif suffix in [".txt", ".text"]:
            return "text"
        else:
            return "text"

    def read_file_content(self, file_path: Path) -> str:
        """Read file content with proper encoding handling."""
        try:
            # Try UTF-8 first
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                # Fallback to latin-1
                return file_path.read_text(encoding="latin-1")
            except Exception as e:
                return f"[Error reading file: {e}]"

    def chunk_content(self, content: str, file_path: str, content_type: str) -> list[dict[str, Any]]:
        """Chunk content using semantic chunking."""
        if not content.strip():
            return []

        # Prepare metadata for chunks
        metadata: dict[str, str | int | float] = {
            "ingest_run_id": self.ingest_run_id,
            "chunk_variant": self.chunk_variant,
            "chunker_name": content_type,
            "source_path": file_path,
            "source_commit": self.source_commit,
            "chunk_size_target": self.chunk_size,
            "overlap_ratio": self.overlap_ratio,
            "overlap_size": self.overlap_size,
        }

        # Use semantic chunker
        chunks = self.chunker.chunk_content(content, file_path, content_type, metadata)

        return chunks

    def get_file_hash(self, file_path: Path) -> str:
        """Get SHA-256 hash of file content."""
        try:
            content = self.read_file_content(file_path)
            return hashlib.sha256(content.encode("utf-8")).hexdigest()
        except Exception:
            return "unknown"

    def should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included in ingestion."""
        # Check explicit paths if specified
        if self._explicit_paths:
            return str(file_path) in self._explicit_paths

        # Check if in excluded directory
        for part in file_path.parts:
            if part in self.exclude_dirs:
                return False

        # Check file extension
        if file_path.suffix.lower() in self.exclude_extensions:
            return False

        # Skip JSON files that cause tsvector issues
        if file_path.suffix.lower() == ".json":
            return False

        # Check if matches include patterns
        for pattern in self.include_patterns:
            if file_path.match(pattern):
                return True

        return False

    def find_files_to_ingest(self) -> list[Path]:
        """Find all files that should be ingested."""
        files: list[Path] = []

        for root, dirs, filenames in os.walk(project_root):
            # Remove excluded directories from dirs to prevent walking into them
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for filename in filenames:
                file_path = Path(root) / filename
                if self.should_include_file(file_path):
                    files.append(file_path)

        return sorted(files)

    def clear_existing_chunks(self, conn: psycopg2.extensions.connection) -> None:
        """Clear existing chunks for this ingest run."""
        print("🧹 Clearing existing chunks...")
        with conn.cursor() as cur:
            cur.execute("DELETE FROM document_chunks WHERE metadata->>'ingest_run_id' = %s", (self.ingest_run_id,))
            deleted_count: int = cur.rowcount
            print(f"   Deleted {deleted_count} existing chunks")

        conn.commit()

    def ingest_document(self, conn: psycopg2.extensions.connection, file_path: Path) -> dict[str, Any]:
        """Ingest a single document."""
        try:
            # Check if connection is still valid
            if conn.closed != 0:
                return {"status": "error", "error": "Database connection is closed"}

            content = self.read_file_content(file_path)
            if not content.strip():
                return {"status": "skipped", "reason": "empty file"}

            content_type = self.get_content_type(file_path)
            file_hash = self.get_file_hash(file_path)

            # Chunk the content
            chunks = self.chunk_content(content, str(file_path), content_type)
            if not chunks:
                return {"status": "skipped", "reason": "no chunks created"}

            # Use a single transaction for the entire document
            with conn.cursor() as cur:
                # Insert document record
                cur.execute(
                    """
                    INSERT INTO documents (file_path, filename, file_type, file_size, content_sha, created_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (file_path) 
                    DO UPDATE SET 
                        filename = EXCLUDED.filename,
                        file_type = EXCLUDED.file_type,
                        file_size = EXCLUDED.file_size,
                        content_sha = EXCLUDED.content_sha,
                        updated_at = NOW()
                    RETURNING id
                    """,
                    (str(file_path), file_path.name, content_type, len(content), file_hash),
                )
                result = cur.fetchone()
                if result is None:
                    raise RuntimeError("Failed to get document ID from database")
                document_id: int = result[0]

                # Insert chunks
                chunk_count: int = 0
                for chunk in chunks:
                    # Generate embedding - encode returns numpy array, convert to list of floats
                    embedding_raw = self.embedding_model.encode(chunk["content"])  # type: ignore
                    embedding: list[float] = list(embedding_raw.tolist())  # type: ignore[assignment]

                    # Extract and type-check chunk data
                    chunk_index: int = int(chunk["chunk_index"])
                    chunk_content: str = str(chunk["content"])
                    chunk_metadata: dict[str, Any] = dict(chunk["metadata"])

                    cur.execute(
                        """
                        INSERT INTO document_chunks (
                            document_id, chunk_index, content, embedding, metadata, 
                            file_path, filename, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                        """,
                        (
                            document_id,
                            chunk_index,
                            chunk_content,
                            embedding,
                            json.dumps(chunk_metadata),
                            str(file_path),
                            file_path.name,
                        ),
                    )
                    chunk_count += 1

                # Commit this document's changes
                conn.commit()

            return {
                "status": "success",
                "document_id": document_id,
                "chunk_count": chunk_count,
                "file_size": len(content),
            }

        except Exception as e:
            # Rollback this document's transaction
            try:
                conn.rollback()
            except Exception:
                pass  # Ignore rollback errors
            return {"status": "error", "error": str(e)}

    def run_ingestion(self):
        """Run the complete ingestion process."""
        print("🚀 Starting Semantic Data Ingestion")
        print("=" * 50)
        print("📊 Configuration:")
        print(f"   Chunk size: {self.chunk_size} characters")
        print(f"   Overlap ratio: {self.overlap_ratio} ({self.overlap_size} chars)")
        print(f"   Embedding model: {self.embedding_model}")
        print(f"   Embedding dimension: {self.embedding_dim}")
        print(f"   Ingest run ID: {self.ingest_run_id}")
        print()

        # Connect to database
        try:
            conn = psycopg2.connect(self.dsn)
            print("✅ Connected to database")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return 1

        try:
            # Clear existing chunks for this run
            self.clear_existing_chunks(conn)

            # Find files to ingest
            files = self.find_files_to_ingest()
            print(f"📁 Found {len(files)} files to process")
            print()

            # Process files
            stats = {
                "total_files": len(files),
                "successful": 0,
                "skipped": 0,
                "errors": 0,
                "total_chunks": 0,
                "total_size": 0,
            }

            for i, file_path in enumerate(files, 1):
                print(f"[{i:3d}/{len(files)}] Processing: {file_path}")

                # Check if connection is still valid before processing
                if conn.closed != 0:
                    print("   ❌ Database connection lost, attempting to reconnect...")
                    try:
                        conn.close()
                        conn = psycopg2.connect(self.dsn)
                        print("   ✅ Reconnected to database")
                    except Exception as e:
                        print(f"   ❌ Reconnection failed: {e}")
                        stats["errors"] += 1
                        continue

                result = self.ingest_document(conn, file_path)

                if result["status"] == "success":
                    stats["successful"] += 1
                    stats["total_chunks"] += result["chunk_count"]
                    stats["total_size"] += result["file_size"]
                    print(f"   ✅ {result['chunk_count']} chunks, {result['file_size']} bytes")
                elif result["status"] == "skipped":
                    stats["skipped"] += 1
                    print(f"   ⏭️  {result['reason']}")
                else:
                    stats["errors"] += 1
                    print(f"   ❌ {result['error']}")

            # Final commit (though individual documents are already committed)
            try:
                conn.commit()
            except Exception as e:
                print(f"⚠️  Final commit warning: {e}")
            print()
            print("✅ Ingestion completed successfully!")
            print()
            print("📊 Final Statistics:")
            print(f"   Total files: {stats['total_files']}")
            print(f"   Successful: {stats['successful']}")
            print(f"   Skipped: {stats['skipped']}")
            print(f"   Errors: {stats['errors']}")
            print(f"   Total chunks: {stats['total_chunks']}")
            print(f"   Total size: {stats['total_size']:,} bytes")
            print(
                f"   Average chunk size: {stats['total_chunks'] and stats['total_size'] // stats['total_chunks']} bytes"
            )

            return 0

        except Exception as e:
            print(f"❌ Ingestion failed: {e}")
            conn.rollback()
            return 1
        finally:
            conn.close()


def main():
    """Main entry point."""
    # Get database DSN from environment
    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
    if not dsn or dsn == "mock://test":
        print("❌ No real database DSN configured")
        print("   Please set POSTGRES_DSN environment variable")
        print("   Example: export POSTGRES_DSN='postgresql://user:pass@localhost:5432/db'")
        return 1

    # Create ingester and run
    ingester = SemanticDataIngester(dsn)
    return ingester.run_ingestion()


if __name__ == "__main__":
    sys.exit(main())
