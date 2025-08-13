#!/usr/bin/env python3
"""
Simple Add Documents with Anchor Metadata
Direct database connection without using the database manager.
"""

import json
import os
import sys
from pathlib import Path

import psycopg2

# Add src to path
sys.path.append("src")

from utils.anchor_metadata_parser import extract_anchor_metadata, extract_anchor_metadata_from_file


def add_document_simple(file_path):
    """Add a document with anchor metadata using direct database connection"""

    print(f"📄 Processing: {file_path}")

    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False

        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract anchor metadata
        anchor_metadata = extract_anchor_metadata_from_file(file_path)
        print(f"   Found anchor metadata: {anchor_metadata.to_dict()}")

        # Split content into chunks (simple approach)
        chunks = []
        lines = content.split("\n")
        current_chunk = []
        chunk_size = 0
        max_chunk_size = 500  # characters

        for i, line in enumerate(lines):
            if chunk_size + len(line) > max_chunk_size and current_chunk:
                # Save current chunk
                chunk_text = "\n".join(current_chunk)
                chunks.append(
                    {
                        "content": chunk_text,
                        "chunk_index": len(chunks),
                        "start_offset": i - len(current_chunk),
                        "end_offset": i,
                    }
                )
                current_chunk = [line]
                chunk_size = len(line)
            else:
                current_chunk.append(line)
                chunk_size += len(line)

        # Add final chunk
        if current_chunk:
            chunk_text = "\n".join(current_chunk)
            chunks.append(
                {
                    "content": chunk_text,
                    "chunk_index": len(chunks),
                    "start_offset": len(lines) - len(current_chunk),
                    "end_offset": len(lines),
                }
            )

        print(f"   Created {len(chunks)} chunks")

        # Add anchor metadata to chunks that contain anchor comments
        chunks_with_anchors = 0
        for chunk in chunks:
            chunk_content = chunk["content"]
            chunk_metadata = extract_anchor_metadata(chunk_content)

            if chunk_metadata.anchor_key or chunk_metadata.anchor_priority is not None or chunk_metadata.role_pins:
                chunk["metadata"] = chunk_metadata.to_dict()
                chunks_with_anchors += 1
                print(f"   Chunk {chunk['chunk_index']} has anchor metadata: {chunk['metadata']}")

        print(f"   Found {chunks_with_anchors} chunks with anchor metadata")

        # Store in database using direct connection
        conn = psycopg2.connect("postgresql://danieljacobs@localhost:5432/ai_agency")

        with conn.cursor() as cur:
            # Insert document record
            cur.execute(
                """
                INSERT INTO documents (filename, file_path, file_type, file_size, chunk_count, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """,
                (
                    os.path.basename(file_path),
                    file_path,
                    Path(file_path).suffix,
                    len(content),
                    len(chunks),
                    "completed",
                ),
            )
            doc_id = cur.fetchone()[0]

            # Insert chunks
            for chunk in chunks:
                cur.execute(
                    """
                    INSERT INTO document_chunks (content, metadata, document_id, chunk_index, start_offset, end_offset)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """,
                    (
                        chunk["content"],
                        json.dumps(chunk.get("metadata", {})),
                        str(doc_id),
                        chunk["chunk_index"],
                        chunk["start_offset"],
                        chunk["end_offset"],
                    ),
                )

            conn.commit()

        conn.close()

        print(f"✅ Successfully added: {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def main():
    """Main function"""
    print("🚀 Starting Simple Document Addition with Anchor Metadata")

    # Core files with anchor metadata
    core_files = [
        "../100_memory/100_cursor-memory-context.md",
        "../000_core/000_backlog.md",
        "../100_memory/104_dspy-development-context.md",
        "../400_guides/400_system-overview.md",
    ]

    success_count = 0
    total_count = len(core_files)

    for file_path in core_files:
        success = add_document_simple(file_path)
        if success:
            success_count += 1

    print(f"\n🎉 Summary: {success_count}/{total_count} documents added successfully")

    if success_count > 0:
        print("💡 You can now test the memory rehydrator with:")
        print("   python3 -m src.utils.memory_rehydrator --role planner --task 'test' --json")


if __name__ == "__main__":
    main()
