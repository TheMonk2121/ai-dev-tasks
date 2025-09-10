#!/usr/bin/env python3
"""
Simple Vector Database Enhancement Script
Creates essential vector enhancement tables and functions step by step.
"""

import os
import sys
from pathlib import Path

import psycopg2

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from utils.logger import get_logger

logger = get_logger(__name__)


class SimpleVectorEnhancement:
    """Handles simple vector database enhancement"""

    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string

    def create_vector_indexes_table(self):
        """Create the vector_indexes table"""
        sql = """
        CREATE TABLE IF NOT EXISTS vector_indexes (
            id SERIAL PRIMARY KEY,
            index_name VARCHAR(255) UNIQUE NOT NULL,
            table_name VARCHAR(255) NOT NULL,
            column_name VARCHAR(255) NOT NULL,
            index_type VARCHAR(50) DEFAULT 'hnsw',
            parameters JSONB DEFAULT '{}',
            status VARCHAR(50) DEFAULT 'creating',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        return self.execute_sql(sql, "vector_indexes table")

    def create_vector_performance_metrics_table(self):
        """Create the vector_performance_metrics table"""
        sql = """
        CREATE TABLE IF NOT EXISTS vector_performance_metrics (
            id SERIAL PRIMARY KEY,
            operation_type VARCHAR(100) NOT NULL,
            query_hash VARCHAR(64),
            execution_time_ms INTEGER,
            result_count INTEGER,
            cache_hit BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        return self.execute_sql(sql, "vector_performance_metrics table")

    def create_vector_cache_table(self):
        """Create the vector_cache table"""
        sql = """
        CREATE TABLE IF NOT EXISTS vector_cache (
            id SERIAL PRIMARY KEY,
            cache_key VARCHAR(255) UNIQUE NOT NULL,
            embedding_data JSONB NOT NULL,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        return self.execute_sql(sql, "vector_cache table")

    def create_vector_health_checks_table(self):
        """Create the vector_health_checks table"""
        sql = """
        CREATE TABLE IF NOT EXISTS vector_health_checks (
            id SERIAL PRIMARY KEY,
            check_type VARCHAR(100) NOT NULL,
            status VARCHAR(50) NOT NULL,
            message TEXT,
            details JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        return self.execute_sql(sql, "vector_health_checks table")

    def create_indexes(self):
        """Create essential indexes"""
        indexes = [
            (
                "CREATE INDEX IF NOT EXISTS idx_vector_performance_metrics_created_at ON vector_performance_metrics(created_at);",
                "vector_performance_metrics created_at index",
            ),
            (
                "CREATE INDEX IF NOT EXISTS idx_vector_performance_metrics_execution_time ON vector_performance_metrics(execution_time_ms);",
                "vector_performance_metrics execution_time index",
            ),
            (
                "CREATE INDEX IF NOT EXISTS idx_vector_cache_last_accessed ON vector_cache(last_accessed);",
                "vector_cache last_accessed index",
            ),
            (
                "CREATE INDEX IF NOT EXISTS idx_vector_cache_expires_at ON vector_cache(expires_at);",
                "vector_cache expires_at index",
            ),
            (
                "CREATE INDEX IF NOT EXISTS idx_vector_health_checks_status ON vector_health_checks(status);",
                "vector_health_checks status index",
            ),
            (
                "CREATE INDEX IF NOT EXISTS idx_vector_health_checks_created_at ON vector_health_checks(created_at);",
                "vector_health_checks created_at index",
            ),
            (
                "CREATE INDEX IF NOT EXISTS idx_vector_indexes_status ON vector_indexes(status);",
                "vector_indexes status index",
            ),
            (
                "CREATE INDEX IF NOT EXISTS idx_vector_indexes_table_name ON vector_indexes(table_name);",
                "vector_indexes table_name index",
            ),
        ]

        for sql, description in indexes:
            if not self.execute_sql(sql, description):
                logger.warning(f"Failed to create {description}")

    def create_functions(self):
        """Create essential functions"""
        functions = [
            # Record vector performance
            """
            CREATE OR REPLACE FUNCTION record_vector_performance(
                p_operation_type VARCHAR(100),
                p_query_hash VARCHAR(64),
                p_execution_time_ms INTEGER,
                p_result_count INTEGER,
                p_cache_hit BOOLEAN DEFAULT FALSE
            ) RETURNS INTEGER AS $$
            DECLARE
                v_id INTEGER;
            BEGIN
                INSERT INTO vector_performance_metrics (
                    operation_type, query_hash, execution_time_ms, result_count, cache_hit
                ) VALUES (
                    p_operation_type, p_query_hash, p_execution_time_ms, p_result_count, p_cache_hit
                ) RETURNING id INTO v_id;
                RETURN v_id;
            END;
            $$ LANGUAGE plpgsql;
            """,
            # Get vector health status
            """
            CREATE OR REPLACE FUNCTION get_vector_health_status() RETURNS JSONB AS $$
            DECLARE
                v_result JSONB;
            BEGIN
                SELECT jsonb_build_object(
                    'total_documents', (SELECT COUNT(*) FROM documents),
                    'total_chunks', (SELECT COUNT(*) FROM document_chunks),
                    'cache_entries', (SELECT COUNT(*) FROM vector_cache),
                    'performance_metrics', (SELECT COUNT(*) FROM vector_performance_metrics),
                    'health_checks', (SELECT COUNT(*) FROM vector_health_checks),
                    'last_health_check', (SELECT MAX(created_at) FROM vector_health_checks)
                ) INTO v_result;
                RETURN v_result;
            END;
            $$ LANGUAGE plpgsql;
            """,
            # Clean expired cache
            """
            CREATE OR REPLACE FUNCTION clean_expired_vector_cache() RETURNS INTEGER AS $$
            DECLARE
                v_deleted_count INTEGER;
            BEGIN
                DELETE FROM vector_cache 
                WHERE expires_at IS NOT NULL AND expires_at < CURRENT_TIMESTAMP;
                GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
                RETURN v_deleted_count;
            END;
            $$ LANGUAGE plpgsql;
            """,
        ]

        for sql in functions:
            if not self.execute_sql(sql, "function"):
                logger.warning("Failed to create function")

    def execute_sql(self, sql: str, description: str) -> bool:
        """Execute SQL statement with error handling"""
        try:
            conn = psycopg2.connect(self.db_connection_string)
            with conn.cursor() as cursor:
                cursor.execute(sql)
                conn.commit()
            conn.close()
            logger.info(f"Successfully created {description}")
            return True
        except Exception as e:
            logger.error(f"Failed to create {description}: {e}")
            return False

    def validate_tables(self):
        """Validate that all tables were created successfully"""
        tables = ["vector_indexes", "vector_performance_metrics", "vector_cache", "vector_health_checks"]

        conn = psycopg2.connect(self.db_connection_string)
        with conn.cursor() as cursor:
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    logger.info(f"Table {table}: {count} rows")
                except Exception as e:
                    logger.error(f"Validation failed for {table}: {e}")
                    conn.close()
                    return False
        conn.close()
        return True

    def run_enhancement(self):
        """Run the complete vector enhancement"""
        logger.info("Starting Simple Vector Database Enhancement")

        # Create tables
        if not self.create_vector_indexes_table():
            return False
        if not self.create_vector_performance_metrics_table():
            return False
        if not self.create_vector_cache_table():
            return False
        if not self.create_vector_health_checks_table():
            return False

        # Create indexes
        self.create_indexes()

        # Create functions
        self.create_functions()

        # Validate
        if not self.validate_tables():
            logger.error("Validation failed")
            return False

        logger.info("Vector enhancement completed successfully")
        return True


def main():
    """Main function"""
    db_connection_string = os.environ.get("POSTGRES_DSN")
    if not db_connection_string:
        logger.error("POSTGRES_DSN environment variable not set")
        return False

    enhancement = SimpleVectorEnhancement(db_connection_string)
    return enhancement.run_enhancement()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
