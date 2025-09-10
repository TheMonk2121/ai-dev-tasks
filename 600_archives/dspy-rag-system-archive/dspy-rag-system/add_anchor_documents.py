#!/usr/bin/env python3
"""
Add Documents with Anchor Metadata to DSPy RAG System
Simple script to add core documentation files with anchor metadata.
"""

import os
import sys
import time

# Import the centralized import utility
try:
    from setup_imports import get_common_imports, setup_dspy_imports
except ImportError:
    # Fallback: try to import directly
    sys.path.insert(0, "src")
    from setup_imports import get_common_imports, setup_dspy_imports

# Setup imports
if not setup_dspy_imports():
    print("❌ Error: Could not setup DSPy import paths")
    sys.exit(1)

# Get common imports
imports = {}
try:
    imports = get_common_imports()
    setup_logger = imports["setup_logger"]
    DocumentProcessor = imports["DocumentProcessor"]

    # Try to get HybridVectorStore from common imports
    if "HybridVectorStore" in imports:
        HybridVectorStore = imports["HybridVectorStore"]
    else:
        # Fallback: direct import with workaround
        import sys

        sys.path.insert(0, "src")
        from dspy_modules.vector_store import HybridVectorStore

except KeyError as e:
    print(f"❌ Error: Missing required import: {e}")
    print("💡 Available imports:", list(imports.keys()))
    sys.exit(1)
except ImportError as e:
    print(f"❌ Error: Could not import HybridVectorStore: {e}")
    print("💡 This is due to relative import issues in the vector_store module")
    sys.exit(1)


def add_document_with_anchors(file_path):
    """Add a document with anchor metadata to the RAG system"""

    logger = setup_logger("add_anchor_documents")
    start_time = time.time()

    logger.info("Starting document addition with anchor metadata", extra={"file_path": file_path})

    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False

        # Process document with anchor metadata extraction
        logger.info("Processing document with anchor metadata")

        processor = DocumentProcessor(chunk_size=300, chunk_overlap=50)
        result = processor(file_path)

        logger.info(
            "Document processed successfully",
            extra={
                "chunk_count": result["total_chunks"],
                "file_size": result["metadata"]["file_size"],
                "processing_time_ms": result["metadata"]["processing_time_ms"],
            },
        )

        # Check for anchor metadata in chunks
        chunks_with_anchors = 0
        for chunk in result["chunks"]:
            if "metadata" in chunk and chunk["metadata"]:
                if "anchor_key" in chunk["metadata"]:
                    chunks_with_anchors += 1
                    logger.info(
                        "Found anchor metadata in chunk",
                        extra={
                            "chunk_id": chunk["id"],
                            "anchor_key": chunk["metadata"].get("anchor_key"),
                            "anchor_priority": chunk["metadata"].get("anchor_priority"),
                            "role_pins": chunk["metadata"].get("role_pins"),
                        },
                    )

        logger.info(f"Found {chunks_with_anchors} chunks with anchor metadata")

        # Store in vector database
        logger.info("Storing in vector database")

        vector_store = HybridVectorStore("postgresql://danieljacobs@localhost:5432/ai_agency")

        # Store chunks
        store_result = vector_store("store_chunks", chunks=result["chunks"], metadata=result["metadata"])

        if store_result["status"] == "success":
            processing_time = time.time() - start_time
            logger.info(
                "Document stored successfully",
                extra={
                    "chunks_stored": store_result["chunks_stored"],
                    "chunks_with_anchors": chunks_with_anchors,
                    "total_processing_time_seconds": round(processing_time, 2),
                },
            )

            return True
        else:
            logger.error("Failed to store document", extra={"error": store_result.get("error", "Unknown error")})
            return False

    except Exception as e:
        logger.error("Error processing document", extra={"error": str(e)})
        return False


def main():
    """Main function"""
    logger = setup_logger("main")

    logger.info("Starting DSPy RAG System - Anchor Document Addition Tool")

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
        print(f"\n📄 Processing: {file_path}")

        success = add_document_with_anchors(file_path)

        if success:
            success_count += 1
            print(f"✅ Successfully added: {file_path}")
        else:
            print(f"❌ Failed to add: {file_path}")

    print(f"\n🎉 Summary: {success_count}/{total_count} documents added successfully")

    if success_count > 0:
        print("💡 You can now test the memory rehydrator with:")
        print("   python3 -m src.utils.memory_rehydrator --role planner --task 'test' --json")


if __name__ == "__main__":
    main()
