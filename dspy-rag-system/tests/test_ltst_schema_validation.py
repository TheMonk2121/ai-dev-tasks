#!/usr/bin/env python3
# type: ignore
"""
LTST Memory System Schema Validation Tests

This module provides comprehensive validation tests for the LTST memory system schema,
ensuring proper table creation, index performance, and data integrity.

Note: Type ignore is used because RealDictCursor returns dictionary-like objects
that the type checker doesn't properly recognize, and database connection objects
are properly handled with null checks at runtime.
"""

import os
import time
from typing import Any, Dict, List, Optional

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor


class LTSTSchemaValidator:
    """Validator for LTST memory system schema."""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize validator with database connection."""
        self.database_url = database_url or os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(self.database_url)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False

    def disconnect(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_sql_file(self, file_path: str) -> bool:
        """Execute SQL file and return success status."""
        try:
            with open(file_path, "r") as f:
                sql_content = f.read()

            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

            for statement in statements:
                if statement and not statement.startswith("--"):
                    self.cursor.execute(statement)

            self.connection.commit()
            return True
        except Exception as e:
            print(f"SQL execution failed: {e}")
            self.connection.rollback()
            return False

    def validate_table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        try:
            self.cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = %s
                );
            """,
                (table_name,),
            )
            return self.cursor.fetchone()["exists"]
        except Exception as e:
            print(f"Table validation failed for {table_name}: {e}")
            return False

    def validate_table_structure(self, table_name: str, expected_columns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate table structure against expected columns."""
        try:
            self.cursor.execute(
                """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = %s
                ORDER BY ordinal_position;
            """,
                (table_name,),
            )

            actual_columns = self.cursor.fetchall()
            expected_column_names = {col["name"] for col in expected_columns}
            actual_column_names = {col["column_name"] for col in actual_columns}

            missing_columns = expected_column_names - actual_column_names
            extra_columns = actual_column_names - expected_column_names

            return {
                "valid": len(missing_columns) == 0,
                "missing_columns": list(missing_columns),
                "extra_columns": list(extra_columns),
                "actual_columns": actual_columns,
                "expected_columns": expected_columns,
            }
        except Exception as e:
            print(f"Structure validation failed for {table_name}: {e}")
            return {"valid": False, "error": str(e)}

    def validate_indexes(self, table_name: str, expected_indexes: List[str]) -> Dict[str, Any]:
        """Validate that expected indexes exist."""
        try:
            self.cursor.execute(
                """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = %s
                AND schemaname = 'public';
            """,
                (table_name,),
            )

            actual_indexes = [row["indexname"] for row in self.cursor.fetchall()]
            missing_indexes = set(expected_indexes) - set(actual_indexes)

            return {
                "valid": len(missing_indexes) == 0,
                "missing_indexes": list(missing_indexes),
                "actual_indexes": actual_indexes,
                "expected_indexes": expected_indexes,
            }
        except Exception as e:
            print(f"Index validation failed for {table_name}: {e}")
            return {"valid": False, "error": str(e)}

    def validate_foreign_keys(self, table_name: str, expected_fks: List[Dict[str, str]]) -> Dict[str, Any]:
        """Validate foreign key constraints."""
        try:
            self.cursor.execute(
                """
                SELECT
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name = %s;
            """,
                (table_name,),
            )

            actual_fks = self.cursor.fetchall()
            actual_fk_map = {
                f"{fk['column_name']}": f"{fk['foreign_table_name']}.{fk['foreign_column_name']}" for fk in actual_fks
            }

            missing_fks = []
            for expected_fk in expected_fks:
                if expected_fk["column"] not in actual_fk_map:
                    missing_fks.append(expected_fk)
                elif actual_fk_map[expected_fk["column"]] != expected_fk["references"]:
                    missing_fks.append(expected_fk)

            return {
                "valid": len(missing_fks) == 0,
                "missing_foreign_keys": missing_fks,
                "actual_foreign_keys": actual_fk_map,
            }
        except Exception as e:
            print(f"Foreign key validation failed for {table_name}: {e}")
            return {"valid": False, "error": str(e)}

    def test_data_insertion(self, table_name: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test data insertion and retrieval."""
        try:
            # Insert test data
            columns = list(test_data.keys())
            placeholders = ", ".join(["%s"] * len(columns))
            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders}) RETURNING *"

            self.cursor.execute(insert_query, list(test_data.values()))
            inserted_row = self.cursor.fetchone()

            # Verify insertion
            if inserted_row:
                # Clean up test data
                self.cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (inserted_row["id"],))
                self.connection.commit()

                return {
                    "valid": True,
                    "inserted_data": dict(inserted_row),
                    "message": "Data insertion and retrieval successful",
                }
            else:
                return {"valid": False, "message": "Data insertion failed - no row returned"}
        except Exception as e:
            self.connection.rollback()
            return {"valid": False, "error": str(e), "message": "Data insertion test failed"}

    def validate_performance(self, table_name: str) -> Dict[str, Any]:
        """Validate basic performance characteristics."""
        try:
            # Test basic query performance
            start_time = time.time()
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count_result = self.cursor.fetchone()
            query_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            return {
                "valid": query_time < 1000,  # Should complete in under 1 second
                "query_time_ms": query_time,
                "row_count": count_result["count"] if count_result else 0,
                "performance_acceptable": query_time < 1000,
            }
        except Exception as e:
            return {"valid": False, "error": str(e), "message": "Performance validation failed"}


def test_ltst_schema_creation():
    """Test LTST schema creation and validation."""
    validator = LTSTSchemaValidator()

    if not validator.connect():
        pytest.skip("Database connection failed")

    try:
        # Define expected table structures
        expected_tables = {
            "conversation_sessions": {
                "columns": [
                    {"name": "session_id", "type": "character varying"},
                    {"name": "user_id", "type": "character varying"},
                    {"name": "session_name", "type": "character varying"},
                    {"name": "session_type", "type": "character varying"},
                    {"name": "status", "type": "character varying"},
                    {"name": "created_at", "type": "timestamp without time zone"},
                    {"name": "last_activity", "type": "timestamp without time zone"},
                    {"name": "metadata", "type": "jsonb"},
                    {"name": "context_summary", "type": "text"},
                    {"name": "relevance_score", "type": "double precision"},
                    {"name": "session_length", "type": "integer"},
                    {"name": "updated_at", "type": "timestamp without time zone"},
                ],
                "indexes": [
                    "idx_conversation_sessions_user_id",
                    "idx_conversation_sessions_last_activity",
                    "idx_conversation_sessions_relevance_score",
                    "idx_conversation_sessions_status",
                ],
                "foreign_keys": [],
            },
            "conversation_messages": {
                "columns": [
                    {"name": "message_id", "type": "integer"},
                    {"name": "session_id", "type": "character varying"},
                    {"name": "message_type", "type": "character varying"},
                    {"name": "role", "type": "character varying"},
                    {"name": "content", "type": "text"},
                    {"name": "content_hash", "type": "character varying"},
                    {"name": "context_hash", "type": "character varying"},
                    {"name": "timestamp", "type": "timestamp without time zone"},
                    {"name": "message_index", "type": "integer"},
                    {"name": "metadata", "type": "jsonb"},
                    {"name": "embedding", "type": "USER-DEFINED"},  # vector type
                    {"name": "relevance_score", "type": "double precision"},
                    {"name": "is_context_message", "type": "boolean"},
                    {"name": "parent_message_id", "type": "integer"},
                    {"name": "created_at", "type": "timestamp without time zone"},
                ],
                "indexes": [
                    "idx_conversation_messages_session_id",
                    "idx_conversation_messages_timestamp",
                    "idx_conversation_messages_role",
                    "idx_conversation_messages_content_hash",
                    "idx_conversation_messages_relevance_score",
                    "idx_conversation_messages_message_index",
                    "idx_conversation_messages_embedding",
                ],
                "foreign_keys": [
                    {"column": "session_id", "references": "conversation_sessions.session_id"},
                    {"column": "parent_message_id", "references": "conversation_messages.message_id"},
                ],
            },
        }

        # Execute schema creation
        schema_file = "dspy-rag-system/config/database/ltst_memory_schema.sql"
        assert validator.execute_sql_file(schema_file), "Schema creation failed"

        # Validate each table
        for table_name, expectations in expected_tables.items():
            # Check table exists
            assert validator.validate_table_exists(table_name), f"Table {table_name} does not exist"

            # Validate structure
            structure_result = validator.validate_table_structure(table_name, expectations["columns"])
            assert structure_result["valid"], f"Table {table_name} structure validation failed: {structure_result}"

            # Validate indexes
            index_result = validator.validate_indexes(table_name, expectations["indexes"])
            assert index_result["valid"], f"Table {table_name} index validation failed: {index_result}"

            # Validate foreign keys
            if expectations["foreign_keys"]:
                fk_result = validator.validate_foreign_keys(table_name, expectations["foreign_keys"])
                assert fk_result["valid"], f"Table {table_name} foreign key validation failed: {fk_result}"

            # Test data insertion
            if table_name == "conversation_sessions":
                test_data = {
                    "session_id": "test_session_001",
                    "user_id": "test_user",
                    "session_name": "Test Session",
                    "session_type": "conversation",
                    "status": "active",
                }
                insertion_result = validator.test_data_insertion(table_name, test_data)
                assert insertion_result["valid"], f"Data insertion test failed for {table_name}: {insertion_result}"

            # Validate performance
            performance_result = validator.validate_performance(table_name)
            assert performance_result["valid"], f"Performance validation failed for {table_name}: {performance_result}"

        print("✅ All LTST schema validation tests passed!")

    finally:
        validator.disconnect()


def test_pgvector_integration():
    """Test pgvector extension integration."""
    validator = LTSTSchemaValidator()

    if not validator.connect():
        pytest.skip("Database connection failed")

    try:
        # Check pgvector extension
        validator.cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        vector_ext = validator.cursor.fetchone()
        assert vector_ext is not None, "pgvector extension not installed"

        # Test vector operations
        validator.cursor.execute("SELECT '[1,2,3]'::vector;")
        vector_result = validator.cursor.fetchone()
        assert vector_result is not None, "Vector operations not working"

        print("✅ pgvector integration validation passed!")

    finally:
        validator.disconnect()


def test_schema_compatibility():
    """Test backward compatibility with existing schema."""
    validator = LTSTSchemaValidator()

    if not validator.connect():
        pytest.skip("Database connection failed")

    try:
        # Check existing conversation_memory table still exists
        assert validator.validate_table_exists("conversation_memory"), "Existing conversation_memory table missing"

        # Check document_chunks table exists
        assert validator.validate_table_exists("document_chunks"), "Existing document_chunks table missing"

        # Check documents table exists
        assert validator.validate_table_exists("documents"), "Existing documents table missing"

        print("✅ Schema compatibility validation passed!")

    finally:
        validator.disconnect()


if __name__ == "__main__":
    # Run validation tests
    print("🧪 Running LTST Schema Validation Tests...")

    test_ltst_schema_creation()
    test_pgvector_integration()
    test_schema_compatibility()

    print("🎉 All validation tests completed successfully!")
