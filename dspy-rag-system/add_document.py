#!/usr/bin/env python3
"""
Add Document to DSPy RAG System
Simple script to add documents to your knowledge base for testing.
"""

import os
import sys
import time

# Add src to path
sys.path.append("src")

from dspy_modules.document_processor import DocumentProcessor
from dspy_modules.vector_store import HybridVectorStore
from utils.logger import setup_logger


def add_document_to_rag(file_path):
    """Add a document to the RAG system"""

    logger = setup_logger("add_document")
    start_time = time.time()
    document_id = f"doc_{int(start_time)}"

    logger.info(
        "Starting document addition", extra={"document_id": document_id, "stage": "start", "file_path": file_path}
    )

    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error("File not found", extra={"document_id": document_id, "stage": "error", "file_path": file_path})
            return False

        # Process document
        logger.info("Processing document", extra={"document_id": document_id, "stage": "processing"})

        processor = DocumentProcessor(chunk_size=300, chunk_overlap=50)
        result = processor(file_path)

        logger.info(
            "Document processed successfully",
            extra={
                "document_id": document_id,
                "stage": "complete",
                "chunk_count": result["total_chunks"],
                "file_size": result["metadata"]["file_size"],
                "elapsed_ms": result["metadata"]["processing_time_ms"],
            },
        )

        # Display enhanced metadata
        metadata = result["metadata"]
        logger.info(
            "Enhanced metadata extracted",
            extra={
                "document_id": document_id,
                "stage": "metadata",
                "category": metadata.get("category", "Uncategorized"),
                "priority": metadata.get("priority", "medium"),
                "confidence_score": metadata.get("confidence_score", 0.0),
                "tags": metadata.get("tags", []),
            },
        )

        # Store in vector database
        logger.info("Storing in vector database", extra={"document_id": document_id, "stage": "storage"})

        vector_store = HybridVectorStore("postgresql://danieljacobs@localhost:5432/ai_agency")

        # Store chunks
        store_result = vector_store("store_chunks", chunks=result["chunks"], metadata=result["metadata"])

        if store_result["status"] == "success":
            logger.info(
                "Document stored successfully",
                extra={
                    "document_id": document_id,
                    "stage": "storage_complete",
                    "chunks_stored": store_result["chunks_stored"],
                },
            )

            return True
        else:
            logger.error(
                "Failed to store document",
                extra={
                    "document_id": document_id,
                    "stage": "storage_error",
                    "error": store_result.get("error", "Unknown error"),
                },
            )
            return False

    except Exception as e:
        logger.error("Error processing document", extra={"document_id": document_id, "stage": "error", "error": str(e)})
        return False


def query_knowledge_base(query, limit=3):
    """Query the knowledge base"""

    logger = setup_logger("query_knowledge_base")

    logger.info("Querying knowledge base", extra={"query": query, "limit": limit, "stage": "query_start"})

    try:
        vector_store = VectorStore("postgresql://danieljacobs@localhost:5432/ai_agency")
        results = vector_store("search", query=query, limit=limit)

        if results["status"] == "success":
            logger.info(
                "Query completed successfully",
                extra={"query": query, "stage": "query_complete", "total_results": results["total_results"]},
            )

            return results["results"]
        else:
            logger.error(
                "Search failed",
                extra={"query": query, "stage": "query_error", "error": results.get("error", "Unknown error")},
            )
            return []

    except Exception as e:
        logger.error("Error querying knowledge base", extra={"query": query, "stage": "query_error", "error": str(e)})
        return []


def main():
    """Main function"""
    logger = setup_logger("main")

    logger.info("Starting DSPy RAG System - Document Addition Tool")

    # Check if file path provided
    if len(sys.argv) < 2:
        logger.info(
            "No file path provided, showing usage", extra={"component": "add_document", "action": "usage_display"}
        )
        print("Usage: python3 add_document.py <file_path>")
        print("\nExample:")
        print("  python3 add_document.py my_document.pdf")
        print("  python3 add_document.py my_notes.txt")
        print("  python3 add_document.py pricing_data.csv")
        print("\nThe system will automatically:")
        print("  - Categorize your document based on filename")
        print("  - Assign priority (high/medium/low)")
        print("  - Extract tags and metadata")
        print("  - Process and store in the vector database")
        return

    file_path = sys.argv[1]

    # Add document to RAG system
    success = add_document_to_rag(file_path)

    if success:
        logger.info(
            "Document addition completed successfully",
            extra={
                "file_path": file_path,
                "stage": "complete",
                "component": "add_document",
                "action": "document_added",
            },
        )
        print(f"\n🎉 Document '{file_path}' successfully added to RAG system!")
        print("💡 You can now query this document using the RAG system.")
        print("📊 View enhanced metadata in the dashboard at http://localhost:5001")
    else:
        logger.error(
            "Document addition failed",
            extra={"file_path": file_path, "stage": "failed", "component": "add_document", "action": "document_failed"},
        )
        print(f"\n❌ Failed to add document '{file_path}' to RAG system.")


if __name__ == "__main__":
    main()
