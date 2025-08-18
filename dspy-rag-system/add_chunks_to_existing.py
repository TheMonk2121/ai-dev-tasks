#!/usr/bin/env python3.12.123.11
"""
Add Chunks to Existing Documents
Add chunks with anchor metadata to documents that already exist in the database.
"""

import json
import os
import sys

import psycopg2

# Import the centralized import utility
try:
    from setup_imports import get_common_imports, setup_dspy_imports
except ImportError:
    # Fallback: try to import directly
    sys.path.insert(0, "src")
    from setup_imports import get_common_imports, setup_dspy_imports

# Setup imports
if not setup_dspy_imports():
    print("X Error: Could not setup DSPy import paths")
    sys.exit(1)

# Get common imports
try:
    imports = get_common_imports()
    extract_anchor_metadata = imports["extract_anchor_metadata"]
    extract_anchor_metadata_from_file = imports["extract_anchor_metadata_from_file"]
except KeyError as e:
    print(f"X Error: Missing required import: {e}")
    sys.exit(1)


def add_chunks_to_existing_document(file_path):
    """Add chunks with anchor metadata to an existing document"""

    print(f"📄 Processing: {file_path}")

    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"X File not found: {file_path}")
            return False

        # Read file content
        with open(file_path, encoding="utf-8") as f:
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
            # Get the existing document ID
            filename = os.path.basename(file_path)
            cur.execute("SELECT document_id FROM documents WHERE filename = %s", (filename,))
            result = cur.fetchone()

            if not result:
                print(f"X Document not found in database: {filename}")
                return False

            doc_id = result[0]
            print(f"   Found existing document ID: {doc_id}")

            # Delete existing chunks for this document
            cur.execute("DELETE FROM document_chunks WHERE document_id = %s", (doc_id,))
            deleted_count = cur.rowcount
            print(f"   Deleted {deleted_count} existing chunks")

            # Insert new chunks
            for chunk in chunks:
                cur.execute(
                    """
                    INSERT INTO document_chunks (content, metadata, document_id, chunk_index, start_offset, end_offset)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        chunk["content"],
                        json.dumps(chunk.get("metadata", {})),
                        doc_id,
                        chunk["chunk_index"],
                        chunk["start_offset"],
                        chunk["end_offset"],
                    ),
                )

            # Update document chunk count
            cur.execute("UPDATE documents SET chunk_count = %s WHERE document_id = %s", (len(chunks), doc_id))

            conn.commit()

        conn.close()

        print(f"OK Successfully updated: {file_path}")
        return True

    except Exception as e:
        print(f"X Error processing {file_path}: {e}")
        return False


def main():
    """Main function"""
    print("🚀 Starting Chunk Addition to Existing Documents")

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
        success = add_chunks_to_existing_document(file_path)
        if success:
            success_count += 1

    print(f"\n🎉 Summary: {success_count}/{total_count} documents updated successfully")

    if success_count > 0:
        print("💡 You can now test the memory rehydrator with:")
        print("   python3 -m src.utils.memory_rehydrator --role planner --task 'test' --json")


if __name__ == "__main__":
    main()
