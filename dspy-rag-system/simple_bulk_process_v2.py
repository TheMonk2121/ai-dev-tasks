#!/usr/bin/env python3
"""
Simple bulk document processing using the new database pool implementation.
"""

import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Add src to path
sys.path.append("src")

from utils.db_pool import get_conn, init_pool

load_dotenv()


def get_core_document_files():
    """Get all core documentation files"""
    core_dirs = ["../000_core", "../100_memory", "../400_guides", "../200_setup"]
    documents = []

    for core_dir in core_dirs:
        if not os.path.exists(core_dir):
            print(f"Warning: Core directory not found: {core_dir}")
            continue

        for file_path in Path(core_dir).rglob("*.md"):
            if file_path.is_file():
                # Skip archive directories
                if "600_archives" in str(file_path):
                    continue

                relative_path = str(file_path.relative_to(Path("..")))
                documents.append(
                    {
                        "file_path": str(file_path),
                        "relative_path": relative_path,
                        "size_bytes": file_path.stat().st_size,
                    }
                )

    print(f"Found {len(documents)} core documentation files")
    return documents


def process_document_with_pool(doc_info):
    """Process a single document using the new pool"""
    try:
        file_path = doc_info["file_path"]
        relative_path = doc_info["relative_path"]

        # Read the file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split content into chunks (simple approach)
        chunks = []
        lines = content.split("\n")
        current_chunk = []
        current_size = 0
        max_chunk_size = 1000  # characters

        for line in lines:
            if current_size + len(line) > max_chunk_size and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_size = len(line)
            else:
                current_chunk.append(line)
                current_size += len(line)

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        # Insert document using the new pool
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO documents (filename, file_path, file_type, file_size, status)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """,
                    (os.path.basename(file_path), relative_path, "markdown", doc_info["size_bytes"], "completed"),
                )

                result = cur.fetchone()
                if result and result[0]:
                    doc_id = result[0]

                    # Insert chunks
                    for i, chunk_content in enumerate(chunks):
                        cur.execute(
                            """
                            INSERT INTO document_chunks (content, document_id, chunk_index, metadata)
                            VALUES (%s, %s, %s, %s)
                        """,
                            (chunk_content, str(doc_id), i, json.dumps({"filename": os.path.basename(file_path)})),
                        )

                    conn.commit()
                    print(f"✅ Processed: {relative_path} ({len(chunks)} chunks)")
                    return True
                else:
                    print(f"❌ Failed to get document ID for {relative_path}")
                    return False

    except Exception as e:
        print(f"❌ Failed to process {doc_info['relative_path']}: {e}")
        return False


def main():
    """Main processing function"""
    print("=== Simple Bulk Document Processing (v2) ===")

    # Initialize the pool
    try:
        init_pool()
        print("✅ Database pool initialized")
    except Exception as e:
        print(f"❌ Database pool initialization failed: {e}")
        return

    # Get documents
    documents = get_core_document_files()

    if not documents:
        print("No documents found to process")
        return

    # Process documents
    successful = 0
    failed = 0

    start_time = time.time()

    for i, doc in enumerate(documents, 1):
        print(f"Processing {i}/{len(documents)}: {doc['relative_path']}")

        if process_document_with_pool(doc):
            successful += 1
        else:
            failed += 1

    elapsed_time = time.time() - start_time
    print("\n📊 Processing Results:")
    print(f"   • Total: {len(documents)}")
    print(f"   • Successful: {successful}")
    print(f"   • Failed: {failed}")
    print(f"   • Processing Time: {elapsed_time:.2f}s")


if __name__ == "__main__":
    main()
