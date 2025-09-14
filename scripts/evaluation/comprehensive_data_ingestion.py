#!/usr/bin/env python3
"""
Comprehensive Data Ingestion

Ingests all documentation from 000-500 directories into the database
for RAG evaluation system.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class ComprehensiveDataIngestion:
    """Comprehensive data ingestion for evaluation system."""

    def __init__(self) -> None:
        self.project_root: Path = project_root
        self.dsn: str = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")

        # Configuration
        self.chunk_size: int = 450
        self.overlap_ratio: float = 0.10
        self.overlap_size: int = int(self.chunk_size * self.overlap_ratio)
        self.embedding_dim: int = 384

        # Directories to ingest
        self.directories_to_ingest: list[str] = [
            "000_core",
            "100_memory",
            "200_setup",
            "300_evals",
            "400_guides",
            "500_research",
        ]

        # Statistics
        self.stats: dict[str, Any] = {
            "files_processed": 0,
            "chunks_created": 0,
            "documents_created": 0,
            "errors": 0,
            "start_time": time.time(),
        }

    def create_mock_embedding(self, text: str) -> list[float]:
        """Create a mock embedding for testing purposes."""
        # Use text hash to create deterministic mock embedding
        text_hash = hashlib.md5(text.encode()).hexdigest()
        np.random.seed(int(text_hash[:8], 16))
        return np.random.random(self.embedding_dim).tolist()

    def chunk_text(self, text: str, file_path: str) -> list[dict[str, Any]]:
        """Chunk text into overlapping segments."""
        chunks = []

        # Simple chunking strategy
        start = 0
        chunk_id = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]

            # Skip very short chunks
            if len(chunk_text.strip()) < 50:
                start += self.chunk_size - self.overlap_size
                continue

            chunk = {
                "chunk_id": f"{file_path}_{chunk_id}",
                "text": chunk_text,
                "start_pos": start,
                "end_pos": end,
                "file_path": file_path,
                "chunk_index": chunk_id,
            }

            chunks.append(chunk)
            chunk_id += 1
            start += self.chunk_size - self.overlap_size

        return chunks

    def process_markdown_file(self, file_path: Path) -> dict[str, Any] | None:
        """Process a single markdown file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Skip empty files
            if not content.strip():
                return None

            # Create document metadata
            document = {
                "file_path": str(file_path.relative_to(self.project_root)),
                "title": file_path.stem,
                "content": content,
                "content_type": "markdown",
                "file_size": len(content),
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "metadata": {
                    "directory": file_path.parent.name,
                    "file_name": file_path.name,
                    "ingestion_run": f"comprehensive_{int(time.time())}",
                },
            }

            return document

        except Exception as e:
            print(f"   ❌ Error processing {file_path}: {e}")
            self.stats["errors"] += 1
            return None

    def ingest_document(self, document: dict[str, Any]) -> bool:
        """Ingest a document into the database."""
        try:
            conn = psycopg2.connect(self.dsn)
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # Insert document
            cur.execute(
                """
                INSERT INTO documents (file_path, filename, file_type, file_size, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (file_path) DO UPDATE SET
                    filename = EXCLUDED.filename,
                    file_type = EXCLUDED.file_type,
                    file_size = EXCLUDED.file_size,
                    created_at = EXCLUDED.created_at
                RETURNING id
            """,
                (
                    document["file_path"],
                    document["title"],  # Use title as filename
                    document["content_type"],
                    document["file_size"],
                    document["created_at"],
                ),
            )

            result = cur.fetchone()
            if result is None:
                raise ValueError("Failed to insert document - no ID returned")
            doc_id = result["id"]

            # Create chunks
            chunks = self.chunk_text(document["content"], document["file_path"])

            for chunk in chunks:
                # Create mock embedding
                embedding = self.create_mock_embedding(chunk["text"])

                # Insert chunk
                cur.execute(
                    """
                    INSERT INTO document_chunks (document_id, content, chunk_index, file_path, line_start, line_end, embedding, metadata, filename)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (document_id, chunk_index) DO UPDATE SET
                        content = EXCLUDED.content,
                        file_path = EXCLUDED.file_path,
                        line_start = EXCLUDED.line_start,
                        line_end = EXCLUDED.line_end,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata,
                        filename = EXCLUDED.filename
                """,
                    (
                        doc_id,
                        chunk["text"],
                        chunk["chunk_index"],
                        chunk["file_path"],
                        chunk["start_pos"],
                        chunk["end_pos"],
                        embedding,
                        json.dumps(
                            {
                                "file_path": chunk["file_path"],
                                "chunk_id": chunk["chunk_id"],
                                "ingestion_run": document["metadata"]["ingestion_run"],
                            }
                        ),
                        document["title"],
                    ),
                )

                self.stats["chunks_created"] += 1

            conn.commit()
            conn.close()

            self.stats["documents_created"] += 1
            return True

        except Exception as e:
            print(f"   ❌ Error ingesting document {document['file_path']}: {e}")
            self.stats["errors"] += 1
            return False

    def ingest_directory(self, directory: str) -> dict[str, Any]:
        """Ingest all markdown files in a directory."""
        print(f"\n📁 Ingesting directory: {directory}")
        print("=" * 50)

        dir_path = self.project_root / directory
        if not dir_path.exists():
            print(f"   ❌ Directory not found: {directory}")
            return {"status": "failed", "reason": "Directory not found"}

        # Find all markdown files
        md_files = list(dir_path.rglob("*.md"))
        print(f"   📄 Found {len(md_files)} markdown files")

        dir_stats = {
            "files_found": len(md_files),
            "files_processed": 0,
            "chunks_created": 0,
            "errors": 0,
        }

        for file_path in md_files:
            print(f"   📝 Processing: {file_path.relative_to(self.project_root)}")

            # Process file
            document = self.process_markdown_file(file_path)
            if document is None:
                continue

            # Ingest document
            if self.ingest_document(document):
                dir_stats["files_processed"] += 1
                # Calculate new chunks created for this document
                new_chunks = len(self.chunk_text(document["content"], document["file_path"]))
                dir_stats["chunks_created"] += new_chunks
                print(f"      ✅ Created {len(self.chunk_text(document['content'], document['file_path']))} chunks")
            else:
                dir_stats["errors"] += 1

        print(
            f"   📊 Directory summary: {dir_stats['files_processed']}/{dir_stats['files_found']} files, {dir_stats['chunks_created']} chunks"
        )

        return dir_stats

    def run_comprehensive_ingestion(self) -> dict[str, Any]:
        """Run comprehensive data ingestion."""
        print("🚀 COMPREHENSIVE DATA INGESTION")
        print("=" * 60)
        print("Ingesting all documentation from 000-500 directories")
        print("into the database for RAG evaluation system")
        print()

        # Test database connection
        try:
            conn = psycopg2.connect(self.dsn)
            cur = conn.cursor()
            cur.execute("SELECT 1")
            conn.close()
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return {"status": "failed", "reason": "Database connection failed"}

        # Ingest each directory
        ingestion_results = {}
        total_files = 0
        total_chunks = 0
        total_errors = 0

        for directory in self.directories_to_ingest:
            dir_results = self.ingest_directory(directory)
            ingestion_results[directory] = dir_results

            if dir_results.get("status") != "failed":
                total_files += dir_results["files_processed"]
                total_chunks += dir_results["chunks_created"]
                total_errors += dir_results["errors"]

        # Calculate final statistics
        duration = time.time() - self.stats["start_time"]

        final_results = {
            "ingestion_summary": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_seconds": duration,
                "status": "✅ COMPLETED",
            },
            "statistics": {
                "total_files_processed": total_files,
                "total_chunks_created": total_chunks,
                "total_errors": total_errors,
                "directories_processed": len(self.directories_to_ingest),
            },
            "directory_results": ingestion_results,
            "configuration": {
                "chunk_size": self.chunk_size,
                "overlap_ratio": self.overlap_ratio,
                "embedding_dim": self.embedding_dim,
            },
        }

        # Save results
        output_dir = Path("metrics/ingestion")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"ingestion_results_{int(time.time())}.json"
        with open(output_file, "w") as f:
            json.dump(final_results, f, indent=2)

        # Print final summary
        print("\n" + "=" * 60)
        print("🎯 INGESTION SUMMARY")
        print("=" * 60)

        print(f"📄 Total files processed: {total_files}")
        print(f"🧩 Total chunks created: {total_chunks}")
        print(f"❌ Total errors: {total_errors}")
        print(f"⏱️ Duration: {duration:.2f} seconds")

        print(f"\n📁 Directory breakdown:")
        for directory, results in ingestion_results.items():
            if results.get("status") != "failed":
                print(f"   • {directory}: {results['files_processed']} files, {results['chunks_created']} chunks")
            else:
                print(f"   • {directory}: {results['reason']}")

        if total_errors == 0:
            print(f"\n✅ Data ingestion completed successfully!")
            print(f"   Database is now populated and ready for RAG evaluation.")
        else:
            print(f"\n⚠️ Data ingestion completed with {total_errors} errors.")
            print(f"   Check the error messages above for details.")

        print(f"\n💾 Detailed results saved to: {output_file}")

        return final_results


def main():
    """Main function."""
    ingestion = ComprehensiveDataIngestion()
    results = ingestion.run_comprehensive_ingestion()
    return results


if __name__ == "__main__":
    _ = main()
