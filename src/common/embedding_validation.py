#!/usr/bin/env python3
"""
Embedding dimension validation utilities.
Prevents silent failures from dimension mismatches between DB and model.
"""

# Add project paths
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.psycopg3_config import Psycopg3Config


def _pg_vector_dim(dsn: str, table: str = "document_chunks", column: str = "embedding") -> int:
    """Get the actual vector dimension from PostgreSQL pgvector column.

    Args:
        dsn: Database connection string
        table: Table name containing the vector column
        column: Vector column name

    Returns:
        Vector dimension, or -1 if not found
    """
    try:
        with Psycopg3Config.get_cursor("default") as cur:
            # atttypmod directly contains the dimension for vector columns
            q = """
            SELECT a.atttypmod AS dim
            FROM pg_attribute a
            JOIN pg_class c ON a.attrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE c.relname = %s AND a.attname = %s AND n.nspname = ANY (current_schemas(true));
            """
            cur.execute(q, (table, column))
            row: Any = cur.fetchone()
            return int(row[0]) if row and row[0] else -1
    except Exception as e:
        print(f"Warning: Could not determine vector dimension: {e}")
        return -1


def assert_embedding_dim(
    dsn: str, expected_dim: int, table: str = "document_chunks", column: str = "embedding"
) -> None:
    """Assert that database vector dimension matches expected dimension.

    Args:
        dsn: Database connection string
        expected_dim: Expected vector dimension from config
        table: Table name containing the vector column
        column: Vector column name

    Raises:
        RuntimeError: If dimensions don't match or column not found
    """
    actual = _pg_vector_dim(dsn, table, column)
    if actual <= 0:
        raise RuntimeError(f"Vector column '{column}' not found in table '{table}' for {dsn}")
    if actual != expected_dim:
        raise RuntimeError(
            f"Embedding dimension mismatch: DB={actual}, config={expected_dim}. "
            "Fix before running. "
            f"Table: {table}, Column: {column}"
        )


def get_embedding_dim(dsn: str, table: str = "document_chunks", column: str = "embedding") -> int:
    """Get the current embedding dimension from the database.

    Args:
        dsn: Database connection string
        table: Table name containing the vector column
        column: Vector column name

    Returns:
        Vector dimension, or -1 if not found
    """
    return _pg_vector_dim(dsn, table, column)


def suggest_dimension_fix(current_dim: int, expected_dim: int) -> str:
    """Suggest how to fix dimension mismatch.

    Args:
        current_dim: Current database dimension
        expected_dim: Expected dimension from config

    Returns:
        Human-readable suggestion for fixing the mismatch
    """
    if current_dim == 95:  # Common wrong dimension
        return (
            "Database has dimension 95 (likely wrong). "
            f"Expected {expected_dim}. "
            "This suggests the database was created with incorrect schema. "
            "Consider recreating the table with correct dimension."
        )
    elif current_dim == 384:
        return f"Database has 384 dimensions, config expects {expected_dim}. Consider updating config to 384."
    elif current_dim == 1024:
        return f"Database has 1024 dimensions, config expects {expected_dim}. Consider updating config to 1024."
    else:
        return f"Database has {current_dim} dimensions, config expects {expected_dim}. Update either DB or config."
