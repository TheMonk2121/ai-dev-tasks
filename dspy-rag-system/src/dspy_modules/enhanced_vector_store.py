#!/usr/bin/env python3.12.123.11
"""
Enhanced Vector Store Module
Leverages advanced PostgreSQL + PGVector capabilities with performance monitoring,
caching, and health checks for improved RAG system performance.
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import psycopg2

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import get_logger

logger = get_logger(__name__)


class EnhancedVectorStore:
    """
    Enhanced vector store with advanced PostgreSQL + PGVector capabilities
    including performance monitoring, caching, and health checks.
    """

    def __init__(self, db_connection_string: str, dimension: int = 384):
        self.db_connection_string = db_connection_string
        self.dimension = dimension

    def _get_query_hash(self, query: str) -> str:
        """Generate a hash for the query for caching and performance tracking"""
        return hashlib.md5(query.encode()).hexdigest()

    def _record_performance(
        self, operation_type: str, query_hash: str, execution_time_ms: int, result_count: int, cache_hit: bool = False
    ) -> None:
        """Record performance metrics for vector operations"""
        try:
            conn = psycopg2.connect(self.db_connection_string)
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT record_vector_performance(%s, %s, %s, %s, %s)
                """,
                    (operation_type, query_hash, execution_time_ms, result_count, cache_hit),
                )
                conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Failed to record performance metrics: {e}")

    def _get_cache_entry(self, cache_key: str) -> dict[str, Any] | None:
        """Get cached embedding data"""
        try:
            conn = psycopg2.connect(self.db_connection_string)
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT embedding_data, last_accessed
                    FROM vector_cache
                    WHERE cache_key = %s AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                """,
                    (cache_key,),
                )
                result = cursor.fetchone()

                if result:
                    # Update last accessed
                    cursor.execute(
                        """
                        UPDATE vector_cache
                        SET last_accessed = CURRENT_TIMESTAMP
                        WHERE cache_key = %s
                    """,
                        (cache_key,),
                    )
                    conn.commit()

                    return {"embedding_data": result[0], "last_accessed": result[1]}
            conn.close()
        except Exception as e:
            logger.warning(f"Failed to get cache entry: {e}")
        return None

    def _set_cache_entry(
        self, cache_key: str, embedding_data: dict[str, Any], expires_at: datetime | None = None
    ) -> None:
        """Set cached embedding data"""
        try:
            conn = psycopg2.connect(self.db_connection_string)
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO vector_cache (cache_key, embedding_data, expires_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (cache_key)
                    DO UPDATE SET
                        embedding_data = EXCLUDED.embedding_data,
                        expires_at = EXCLUDED.expires_at,
                        last_accessed = CURRENT_TIMESTAMP
                """,
                    (cache_key, json.dumps(embedding_data), expires_at),
                )
                conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Failed to set cache entry: {e}")

    def _clean_expired_cache(self) -> int:
        """Clean expired cache entries"""
        try:
            conn = psycopg2.connect(self.db_connection_string)
            with conn.cursor() as cursor:
                cursor.execute("SELECT clean_expired_vector_cache()")
                deleted_count = cursor.fetchone()[0]
                conn.commit()
            conn.close()
            return deleted_count
        except Exception as e:
            logger.warning(f"Failed to clean expired cache: {e}")
            return 0

    def add_documents(self, documents: list[dict[str, Any]]) -> bool:
        """
        Add documents to the vector store with enhanced performance tracking

        Args:
            documents: List of documents with content and metadata

        Returns:
            bool: Success status
        """
        start_time = time.time()

        try:
            conn = psycopg2.connect(self.db_connection_string)
            with conn.cursor() as cursor:
                for doc in documents:
                    # Insert document
                    cursor.execute(
                        """
                        INSERT INTO documents (filename, file_path, file_type, file_size, status)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """,
                        (
                            doc.get("filename", "unknown"),
                            doc.get("file_path", ""),
                            doc.get("file_type", "text"),
                            doc.get("file_size", 0),
                            "processed",
                        ),
                    )
                    doc_id = cursor.fetchone()[0]

                    # Insert chunks
                    chunks = doc.get("chunks", [])
                    for i, chunk in enumerate(chunks):
                        embedding = chunk.get("embedding")
                        if embedding:
                            cursor.execute(
                                """
                                INSERT INTO document_chunks
                                (content, embedding, metadata, document_id, chunk_index)
                                VALUES (%s, %s, %s, %s, %s)
                            """,
                                (chunk["content"], embedding, json.dumps(chunk.get("metadata", {})), str(doc_id), i),
                            )

                conn.commit()
            conn.close()

            execution_time = int((time.time() - start_time) * 1000)
            self._record_performance("add_documents", "batch", execution_time, len(documents))

            logger.info(f"Successfully added {len(documents)} documents")
            return True

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False

    def similarity_search(
        self, query_embedding: list[float], top_k: int = 5, use_cache: bool = True
    ) -> list[dict[str, Any]]:
        """
        Perform similarity search with caching and performance monitoring

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            use_cache: Whether to use caching

        Returns:
            List of similar documents with scores
        """
        start_time = time.time()
        query_hash = self._get_query_hash(str(query_embedding))
        cache_hit = False

        # Try cache first
        if use_cache:
            cache_key = f"search_{query_hash}"
            cached_result = self._get_cache_entry(cache_key)
            if cached_result:
                cache_hit = True
                execution_time = int((time.time() - start_time) * 1000)
                self._record_performance(
                    "similarity_search", query_hash, execution_time, len(cached_result["embedding_data"]), True
                )
                return cached_result["embedding_data"]

        try:
            conn = psycopg2.connect(self.db_connection_string)
            with conn.cursor() as cursor:
                # Perform similarity search
                cursor.execute(
                    """
                    SELECT
                        dc.content,
                        dc.metadata,
                        dc.document_id,
                        dc.chunk_index,
                        1 - (dc.embedding <=> %s::vector) as similarity_score
                    FROM document_chunks dc
                    WHERE dc.embedding IS NOT NULL
                    ORDER BY dc.embedding <=> %s::vector
                    LIMIT %s
                """,
                    (query_embedding, query_embedding, top_k),
                )

                results = []
                for row in cursor.fetchall():
                    results.append(
                        {
                            "content": row[0],
                            "metadata": row[1] if isinstance(row[1], dict) else (json.loads(row[1]) if row[1] else {}),
                            "document_id": row[2],
                            "chunk_index": row[3],
                            "similarity_score": float(row[4]),
                        }
                    )

            conn.close()

            execution_time = int((time.time() - start_time) * 1000)
            self._record_performance("similarity_search", query_hash, execution_time, len(results), cache_hit)

            # Cache the result
            if use_cache and results:
                cache_key = f"search_{query_hash}"
                expires_at = datetime.now() + timedelta(hours=1)  # Cache for 1 hour
                self._set_cache_entry(cache_key, results, expires_at)

            return results

        except Exception as e:
            logger.error(f"Failed to perform similarity search: {e}")
            return []

    def get_health_status(self) -> dict[str, Any]:
        """
        Get comprehensive health status of the vector store

        Returns:
            Dict with health status information
        """
        try:
            conn = psycopg2.connect(self.db_connection_string)
            with conn.cursor() as cursor:
                cursor.execute("SELECT get_vector_health_status()")
                health_status = cursor.fetchone()[0]
            conn.close()

            # Add additional health checks
            health_status["cache_cleanup_needed"] = self._clean_expired_cache()
            health_status["timestamp"] = datetime.now().isoformat()

            return health_status

        except Exception as e:
            logger.error(f"Failed to get health status: {e}")
            return {"error": str(e)}

    def create_vector_index(
        self, table_name: str, column_name: str, index_type: str = "hnsw", parameters: dict[str, Any] = None
    ) -> bool:
        """
        Create a vector index for improved search performance

        Args:
            table_name: Name of the table to index
            column_name: Name of the vector column
            index_type: Type of index (hnsw, ivfflat)
            parameters: Index parameters

        Returns:
            bool: Success status
        """
        try:
            conn = psycopg2.connect(self.db_connection_string)
            with conn.cursor() as cursor:
                # Record index creation
                index_name = f"idx_{table_name}_{column_name}_{index_type}"
                cursor.execute(
                    """
                    INSERT INTO vector_indexes (index_name, table_name, column_name, index_type, parameters, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """,
                    (index_name, table_name, column_name, index_type, json.dumps(parameters or {}), "creating"),
                )

                # Create the actual index
                if index_type == "hnsw":
                    cursor.execute(
                        f"""
                        CREATE INDEX {index_name}
                        ON {table_name} USING hnsw ({column_name} vector_cosine_ops)
                    """
                    )
                elif index_type == "ivfflat":
                    cursor.execute(
                        f"""
                        CREATE INDEX {index_name}
                        ON {table_name} USING ivfflat ({column_name} vector_cosine_ops)
                    """
                    )

                # Update status
                cursor.execute(
                    """
                    UPDATE vector_indexes
                    SET status = 'active', updated_at = CURRENT_TIMESTAMP
                    WHERE index_name = %s
                """,
                    (index_name,),
                )

                conn.commit()
            conn.close()

            logger.info(f"Successfully created vector index: {index_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create vector index: {e}")
            return False

    def get_performance_metrics(self, hours: int = 24) -> list[dict[str, Any]]:
        """
        Get performance metrics for the specified time period

        Args:
            hours: Number of hours to look back

        Returns:
            List of performance metrics
        """
        try:
            conn = psycopg2.connect(self.db_connection_string)
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        operation_type,
                        AVG(execution_time_ms) as avg_execution_time,
                        MAX(execution_time_ms) as max_execution_time,
                        COUNT(*) as operation_count,
                        AVG(result_count) as avg_result_count,
                        SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hits,
                        COUNT(*) as total_operations
                    FROM vector_performance_metrics
                    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '%s hours'
                    GROUP BY operation_type
                    ORDER BY avg_execution_time DESC
                """,
                    (hours,),
                )

                results = []
                for row in cursor.fetchall():
                    results.append(
                        {
                            "operation_type": row[0],
                            "avg_execution_time_ms": float(row[1]) if row[1] else 0,
                            "max_execution_time_ms": row[2],
                            "operation_count": row[3],
                            "avg_result_count": float(row[4]) if row[4] else 0,
                            "cache_hit_rate": float(row[5]) / row[6] if row[6] > 0 else 0,
                            "total_operations": row[6],
                        }
                    )

            conn.close()
            return results

        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return []

    def optimize_performance(self) -> dict[str, Any]:
        """
        Optimize vector store performance based on metrics

        Returns:
            Dict with optimization recommendations
        """
        try:
            # Get recent performance metrics
            metrics = self.get_performance_metrics(hours=1)

            recommendations = {"cache_cleanup": 0, "index_creation": [], "performance_issues": []}

            # Check for cache cleanup
            recommendations["cache_cleanup"] = self._clean_expired_cache()

            # Analyze performance issues
            for metric in metrics:
                if metric["avg_execution_time_ms"] > 100:  # More than 100ms
                    recommendations["performance_issues"].append(
                        {
                            "operation": metric["operation_type"],
                            "avg_time_ms": metric["avg_execution_time_ms"],
                            "suggestion": "Consider creating HNSW index for faster searches",
                        }
                    )

                if metric["cache_hit_rate"] < 0.5:  # Less than 50% cache hit rate
                    recommendations["performance_issues"].append(
                        {
                            "operation": metric["operation_type"],
                            "cache_hit_rate": metric["cache_hit_rate"],
                            "suggestion": "Consider increasing cache size or TTL",
                        }
                    )

            # Suggest index creation if needed
            if not self._has_vector_index("document_chunks", "embedding"):
                recommendations["index_creation"].append(
                    {
                        "table": "document_chunks",
                        "column": "embedding",
                        "type": "hnsw",
                        "reason": "No vector index found for similarity search",
                    }
                )

            return recommendations

        except Exception as e:
            logger.error(f"Failed to optimize performance: {e}")
            return {"error": str(e)}

    def _has_vector_index(self, table_name: str, column_name: str) -> bool:
        """Check if a vector index exists for the given table and column"""
        try:
            conn = psycopg2.connect(self.db_connection_string)
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM vector_indexes
                    WHERE table_name = %s AND column_name = %s AND status = 'active'
                """,
                    (table_name, column_name),
                )
                count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception as e:
            logger.warning(f"Failed to check vector index: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Initialize enhanced vector store
    db_connection = os.environ.get("POSTGRES_DSN")
    if not db_connection:
        print("POSTGRES_DSN environment variable not set")
        sys.exit(1)

    vector_store = EnhancedVectorStore(db_connection)

    # Get health status
    health = vector_store.get_health_status()
    print(f"Health Status: {json.dumps(health, indent=2)}")

    # Get performance metrics
    metrics = vector_store.get_performance_metrics()
    print(f"Performance Metrics: {json.dumps(metrics, indent=2)}")

    # Get optimization recommendations
    optimization = vector_store.optimize_performance()
    print(f"Optimization Recommendations: {json.dumps(optimization, indent=2)}")
