#!/usr/bin/env python3
"""
Database Utilities
Context-aware helper functions for safe database operations.
"""
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple

import psycopg2

DB_DSN = "postgresql://danieljacobs@localhost:5432/ai_agency"


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = None
    try:
        conn = psycopg2.connect(DB_DSN)
        yield conn
    finally:
        if conn:
            conn.close()


def safe_fetchone(cursor, context: str = "operational", error_msg: str = "Database query failed") -> tuple[Any, ...]:
    """
    Safely fetch one row from cursor with context-aware error handling.

    Args:
        cursor: Database cursor
        context: "operational" (fast, assumes data exists) or "production" (robust error handling)
        error_msg: Custom error message for production context

    Returns:
        Tuple of row data

    Raises:
        RuntimeError: If context is "production" and no data found
    """
    result = cursor.fetchone()

    if context == "production" and result is None:
        raise RuntimeError(error_msg)

    # For operational context, we assume data exists (known database state)
    # This allows fast development while maintaining type safety
    return result


def safe_fetchall(
    cursor, context: str = "operational", error_msg: str = "Database query failed"
) -> list[tuple[Any, ...]]:
    """
    Safely fetch all rows from cursor with context-aware error handling.

    Args:
        cursor: Database cursor
        context: "operational" (fast, assumes data exists) or "production" (robust error handling)
        error_msg: Custom error message for production context

    Returns:
        List of row tuples

    Raises:
        RuntimeError: If context is "production" and no data found
    """
    result = cursor.fetchall()

    if context == "production" and not result:
        raise RuntimeError(error_msg)

    return result


def execute_query(query: str, params: tuple | None = None, context: str = "operational") -> list[tuple[Any, ...]]:
    """
    Execute a query and return results with context-aware error handling.

    Args:
        query: SQL query string
        params: Query parameters (optional)
        context: "operational" or "production"

    Returns:
        List of result tuples
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return safe_fetchall(cursor, context)


def execute_single_query(query: str, params: tuple | None = None, context: str = "operational") -> tuple[Any, ...]:
    """
    Execute a query and return single result with context-aware error handling.

    Args:
        query: SQL query string
        params: Query parameters (optional)
        context: "operational" or "production"

    Returns:
        Single result tuple
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return safe_fetchone(cursor, context)


def get_database_stats(context: str = "operational") -> dict[str, Any]:
    """
    Get database statistics with context-aware error handling.

    Args:
        context: "operational" or "production"

    Returns:
        Dictionary with database statistics
    """
    query = """
        SELECT
            COUNT(*) as total_documents,
            SUM(chunk_count) as total_chunks,
            AVG(file_size) as avg_file_size,
            AVG(chunk_count) as avg_chunks_per_doc
        FROM documents
    """

    result = execute_single_query(query, context=context)

    return {
        "total_documents": result[0],
        "total_chunks": result[1],
        "avg_file_size": result[2],
        "avg_chunks_per_doc": result[3],
    }


def get_chunk_size_analysis(context: str = "operational") -> list[tuple[str, int, int, float]]:
    """
    Get chunk size analysis for 400_ guides with context-aware error handling.

    Args:
        context: "operational" or "production"

    Returns:
        List of (filename, file_size, chunk_count, avg_chunk_size) tuples
    """
    query = """
        SELECT
            filename,
            file_size,
            chunk_count,
            ROUND(file_size::numeric / chunk_count, 1) as avg_chunk_size
        FROM documents
        WHERE filename LIKE '400_%'
        ORDER BY avg_chunk_size DESC
    """

    return execute_query(query, context=context)


def get_cross_reference_analysis(context: str = "operational") -> list[tuple[str, int, int, float]]:
    """
    Get cross-reference analysis with context-aware error handling.

    Args:
        context: "operational" or "production"

    Returns:
        List of (filename, chunks_with_refs, total_chunks, coverage_pct) tuples
    """
    query = """
        SELECT
            d.filename,
            COUNT(dc.id) as chunks_with_refs,
            d.chunk_count,
            ROUND(COUNT(dc.id)::numeric / d.chunk_count * 100, 1) as coverage_pct
        FROM documents d
        LEFT JOIN document_chunks dc ON d.id::text = dc.document_id AND dc.content LIKE '%400_%'
        WHERE d.filename LIKE '400_%'
        GROUP BY d.filename, d.chunk_count
        ORDER BY coverage_pct DESC
    """

    return execute_query(query, context=context)


def get_duplicate_chunk_count(context: str = "operational") -> int:
    """
    Get count of duplicate chunks with context-aware error handling.

    Args:
        context: "operational" or "production"

    Returns:
        Number of duplicate chunks
    """
    query = """
        SELECT COUNT(*) as duplicate_chunks
        FROM document_chunks dc1
        JOIN document_chunks dc2 ON dc1.content = dc2.content AND dc1.id != dc2.id
    """

    result = execute_single_query(query, context=context)
    return result[0]


def get_storage_analysis(context: str = "operational") -> tuple[str, str]:
    """
    Get storage analysis with context-aware error handling.

    Args:
        context: "operational" or "production"

    Returns:
        Tuple of (documents_size, chunks_size) as formatted strings
    """
    query = """
        SELECT
            pg_size_pretty(pg_total_relation_size('documents')) as docs_size,
            pg_size_pretty(pg_total_relation_size('document_chunks')) as chunks_size
    """

    result = execute_single_query(query, context=context)
    return result[0], result[1]


# Usage examples and documentation
if __name__ == "__main__":
    # Example usage for operational scripts (fast development)
    try:
        stats = get_database_stats("operational")
        print(f"Operational: {stats['total_documents']} documents")

        # Example usage for production code (robust error handling)
        stats = get_database_stats("production")
        print(f"Production: {stats['total_documents']} documents")

    except RuntimeError as e:
        print(f"Production error: {e}")
