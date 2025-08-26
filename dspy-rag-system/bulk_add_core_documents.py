#!/usr/bin/env python3
# ANCHOR_KEY: bulk-add-core-documents
# ANCHOR_PRIORITY: 25
# ROLE_PINS: ["implementer", "coder"]
"""
Bulk Core Document Processor
---------------------------
Efficiently process and add all core documentation files to the memory rehydrator system.

This script identifies all core documentation files and processes them in batches
for optimal performance and memory usage.
"""

import concurrent.futures
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path
sys.path.append("src")

try:
    from dspy_modules.document_processor import DocumentIngestionPipeline
    from dspy_modules.vector_store import HybridVectorStore
    from utils.logger import setup_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the dspy-rag-system directory")
    sys.exit(1)

from utils.database_resilience import get_database_manager

# Setup logging
logger = setup_logger("bulk_processor")


@dataclass
class DocumentInfo:
    """Information about a document file"""

    file_path: str
    relative_path: str
    size_bytes: int
    last_modified: float
    priority_score: float = 0.0
    in_database: bool = False
    database_id: Optional[int] = None


def get_core_document_files() -> List[DocumentInfo]:
    """Get all core documentation files that should be in the memory rehydrator"""
    core_dirs = ["../000_core", "../100_memory", "../400_guides", "../200_setup"]

    documents = []

    for core_dir in core_dirs:
        if not os.path.exists(core_dir):
            logger.warning(f"Core directory not found: {core_dir}")
            continue

        for file_path in Path(core_dir).rglob("*.md"):
            if file_path.is_file():
                # Skip archive directories
                if "600_archives" in str(file_path):
                    continue

                stat = file_path.stat()
                relative_path = str(file_path.relative_to(Path("..")))

                # Calculate priority score based on file location and name
                priority_score = calculate_priority_score(relative_path)

                doc_info = DocumentInfo(
                    file_path=str(file_path),
                    relative_path=relative_path,
                    size_bytes=stat.st_size,
                    last_modified=stat.st_mtime,
                    priority_score=priority_score,
                )
                documents.append(doc_info)

    logger.info(f"Found {len(documents)} core documentation files")
    return sorted(documents, key=lambda x: x.priority_score, reverse=True)


def calculate_priority_score(file_path: str) -> float:
    """Calculate priority score for a document based on its importance"""
    score = 0.0

    # Core files get highest priority
    if file_path.startswith("000_core/"):
        score += 10.0
        if "backlog" in file_path.lower():
            score += 5.0
        if "prd" in file_path.lower():
            score += 3.0
        if "task" in file_path.lower():
            score += 3.0

    # Memory context files are critical
    elif file_path.startswith("100_memory/"):
        score += 9.0
        if "cursor-memory-context" in file_path:
            score += 5.0
        if "dspy-development-context" in file_path:
            score += 4.0

    # Setup files are important
    elif file_path.startswith("200_setup/"):
        score += 7.0

    # Guide files vary in importance
    elif file_path.startswith("400_guides/"):
        score += 6.0
        if "system-overview" in file_path:
            score += 4.0
        if "project-overview" in file_path:
            score += 3.0
        if "best-practices" in file_path:
            score += 2.0

    # Penalize very large files (likely not core docs)
    if score > 0:
        try:
            size_mb = os.path.getsize(f"../{file_path}") / (1024 * 1024)
            if size_mb > 1.0:  # Files over 1MB get penalized
                score -= min(size_mb - 1.0, 3.0)
        except Exception:
            pass

    return max(score, 0.0)


def analyze_database_gap(core_documents: List[DocumentInfo]) -> Dict[str, Any]:
    """Analyze the gap between core documents and what's in the database"""
    try:
        db = get_database_manager()

        # Get all documents currently in database
        result = db.execute_query("SELECT id, file_path, filename FROM documents")
        db_documents = {row["file_path"] + "/" + row["filename"]: row["id"] for row in result}

        # Check which core documents are already in database
        missing_docs = []
        present_docs = []

        for doc in core_documents:
            # Check if document is in database (handle different path formats)
            doc_found = False
            for db_key, db_id in db_documents.items():
                # Extract just the filename from the database key
                db_filename = db_key.split("/")[-1] if "/" in db_key else db_key
                doc_filename = doc.relative_path.split("/")[-1] if "/" in doc.relative_path else doc.relative_path

                # Check for filename match (more reliable than path matching)
                if db_filename == doc_filename:
                    doc.in_database = True
                    doc.database_id = db_id
                    present_docs.append(doc)
                    doc_found = True
                    break

            if not doc_found:
                missing_docs.append(doc)

        # Calculate statistics
        total_core = len(core_documents)
        total_present = len(present_docs)
        total_missing = len(missing_docs)
        coverage_percentage = (total_present / total_core * 100) if total_core > 0 else 0

        return {
            "total_core_documents": total_core,
            "present_in_database": total_present,
            "missing_from_database": total_missing,
            "coverage_percentage": coverage_percentage,
            "missing_documents": missing_docs,
            "present_documents": present_docs,
            "database_documents": db_documents,
        }

    except Exception as e:
        logger.error(f"Error analyzing database gap: {e}")
        return {
            "total_core_documents": len(core_documents),
            "present_in_database": 0,
            "missing_from_database": len(core_documents),
            "coverage_percentage": 0,
            "missing_documents": core_documents,
            "present_documents": [],
            "database_documents": {},
            "error": str(e),
        }


def print_inventory_report(analysis: Dict[str, Any]):
    """Print a comprehensive inventory report"""
    print("\n" + "=" * 80)
    print("📊 CORE DOCUMENT INVENTORY ANALYSIS")
    print("=" * 80)

    print("\n📈 Coverage Statistics:")
    print(f"   • Total Core Documents: {analysis['total_core_documents']}")
    print(f"   • Present in Database: {analysis['present_in_database']}")
    print(f"   • Missing from Database: {analysis['missing_from_database']}")
    print(f"   • Coverage: {analysis['coverage_percentage']:.1f}%")

    if analysis["missing_from_database"] > 0:
        print(f"\n❌ Missing Documents ({analysis['missing_from_database']}):")
        for i, doc in enumerate(analysis["missing_documents"][:20], 1):
            print(f"   {i:2d}. {doc.relative_path} (Priority: {doc.priority_score:.1f})")

        if len(analysis["missing_documents"]) > 20:
            print(f"   ... and {len(analysis['missing_documents']) - 20} more")

    if analysis["present_in_database"] > 0:
        print(f"\n✅ Present Documents ({analysis['present_in_database']}):")
        for i, doc in enumerate(analysis["present_documents"][:10], 1):
            print(f"   {i:2d}. {doc.relative_path} (DB ID: {doc.database_id})")

        if len(analysis["present_documents"]) > 10:
            print(f"   ... and {len(analysis['present_documents']) - 10} more")

    print("\n" + "=" * 80)


def process_documents_bulk(documents: List[DocumentInfo], max_workers: int = 4, batch_size: int = 10) -> Dict[str, Any]:
    """Process documents in bulk with concurrent processing"""
    logger.info(f"Starting bulk processing of {len(documents)} documents")

    results = {"total": len(documents), "successful": 0, "failed": 0, "errors": [], "processing_time": 0}

    start_time = time.time()

    try:
        # Initialize processing pipeline with parent directory access
        pipeline = DocumentIngestionPipeline(allowed_paths=[".."])

        # Get database connection string and initialize vector store
        db_manager = get_database_manager()
        vector_store = HybridVectorStore(db_connection_string=db_manager.connection_string)

        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")

            # Process batch concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_doc = {
                    executor.submit(process_single_document, doc, pipeline, vector_store): doc for doc in batch
                }

                for future in concurrent.futures.as_completed(future_to_doc):
                    doc = future_to_doc[future]
                    try:
                        result = future.result()
                        if result["success"]:
                            results["successful"] += 1
                            logger.info(f"✅ Processed: {doc.relative_path}")
                        else:
                            results["failed"] += 1
                            results["errors"].append({"file": doc.relative_path, "error": result["error"]})
                            logger.error(f"❌ Failed: {doc.relative_path} - {result['error']}")
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append({"file": doc.relative_path, "error": str(e)})
                        logger.error(f"❌ Exception processing {doc.relative_path}: {e}")

    except Exception as e:
        logger.error(f"Bulk processing failed: {e}")
        results["errors"].append({"file": "bulk_processing", "error": str(e)})

    results["processing_time"] = time.time() - start_time
    return results


def process_single_document(
    doc: DocumentInfo, pipeline: DocumentIngestionPipeline, vector_store: HybridVectorStore
) -> Dict[str, Any]:
    """Process a single document"""
    try:
        # Process through pipeline with vector store
        result = pipeline.forward(document_path=doc.file_path, vector_store=vector_store)

        return {"success": True, "result": result}

    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Bulk process core documentation files")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be processed without actually processing"
    )
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum concurrent workers")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for processing")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze inventory, don't process")

    args = parser.parse_args()

    # Get core documents
    core_documents = get_core_document_files()

    # Analyze database gap
    analysis = analyze_database_gap(core_documents)

    # Print inventory report
    print_inventory_report(analysis)

    if args.analyze_only:
        return

    if args.dry_run:
        print("\n🔍 DRY RUN - Showing files that would be processed:")
        for i, doc in enumerate(core_documents, 1):
            status = "✅" if doc.in_database else "❌"
            print(f"    {i:2d}. {status} {doc.relative_path}")
        print(f"\nTotal: {len(core_documents)} files would be processed")
        return

    # Process missing documents only
    missing_docs = [doc for doc in core_documents if not doc.in_database]

    if not missing_docs:
        print("\n🎉 All core documents are already in the database!")
        return

    print(f"\n🚀 Processing {len(missing_docs)} missing documents...")

    # Process documents
    results = process_documents_bulk(missing_docs, args.max_workers, args.batch_size)

    # Print results
    print("\n📊 Processing Results:")
    print(f"   • Total: {results['total']}")
    print(f"   • Successful: {results['successful']}")
    print(f"   • Failed: {results['failed']}")
    print(f"   • Processing Time: {results['processing_time']:.2f}s")

    if results["errors"]:
        print("\n❌ Errors:")
        for error in results["errors"][:5]:  # Show first 5 errors
            print(f"   • {error['file']}: {error['error']}")
        if len(results["errors"]) > 5:
            print(f"   ... and {len(results['errors']) - 5} more errors")


if __name__ == "__main__":
    main()
