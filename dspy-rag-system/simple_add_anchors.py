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
            result = cur.fetchone()
            if result is None:
                raise Exception("Failed to insert document record - no ID returned")
            doc_id = result[0]

            # Insert chunks
            for chunk in chunks:
                meta = chunk.get("metadata", {})
                anchor_key = meta.get("anchor_key")
                is_anchor = bool(anchor_key)

                cur.execute(
                    """
                    INSERT INTO document_chunks (
                        document_id,
                        chunk_index,
                        file_path,
                        line_start,
                        line_end,
                        content,
                        is_anchor,
                        anchor_key,
                        metadata
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        str(doc_id),
                        chunk["chunk_index"],
                        file_path,
                        chunk["start_offset"],  # use computed line offsets as line numbers
                        chunk["end_offset"],
                        chunk["content"],
                        is_anchor,
                        anchor_key,
                        json.dumps(meta),
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

    # Process all markdown files in watch_folder
    watch_folder = "watch_folder"
    core_files = []

    if os.path.exists(watch_folder):
        for file in os.listdir(watch_folder):
            if file.endswith(".md"):
                file_path = os.path.join(watch_folder, file)
                core_files.append(file_path)

    if not core_files:
        print("❌ No markdown files found in watch_folder")
        return

    print(f"📁 Found {len(core_files)} markdown files in watch_folder")

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
