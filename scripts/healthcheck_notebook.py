#!/usr/bin/env python3
"""
Healthcheck Notebook - Traffic Light System Health Report
Runs comprehensive DB/index/tracing checks and prints a traffic-light report.
"""

import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

# Add project paths
project_root = Path(__file__).parent.parent
dspy_rag_path = project_root / "dspy-rag-system"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(dspy_rag_path))

try:
    import numpy as np
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Run: pip install psycopg2-binary sentence-transformers numpy")
    sys.exit(1)


class HealthStatus(Enum):
    GREEN = "🟢"
    YELLOW = "🟡"
    RED = "🔴"
    UNKNOWN = "⚪"


@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    message: str
    details: dict[str, Any] | None = None
    latency_ms: float | None = None


class HealthcheckNotebook:
    """Comprehensive health monitoring for RAG system components."""

    def __init__(self, db_connection_string: str | None = None):
        self.db_connection_string = db_connection_string or os.getenv(
            "POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency?sslmode=disable"
        )
        self.checks: list[HealthCheck] = []

    def add_check(self, check: HealthCheck):
        """Add a health check result."""
        self.checks.append(check)

    def get_overall_status(self) -> HealthStatus:
        """Determine overall system health."""
        if not self.checks:
            return HealthStatus.UNKNOWN

        red_count = sum(1 for c in self.checks if c.status == HealthStatus.RED)
        yellow_count = sum(1 for c in self.checks if c.status == HealthStatus.YELLOW)

        if red_count > 0:
            return HealthStatus.RED
        elif yellow_count > 0:
            return HealthStatus.YELLOW
        else:
            return HealthStatus.GREEN

    def print_report(self):
        """Print comprehensive traffic-light health report."""
        overall = self.get_overall_status()

        print("\n" + "=" * 80)
        print(f"🏥 RAG SYSTEM HEALTH REPORT - {overall.value} {overall.name}")
        print("=" * 80)
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Checks: {len(self.checks)}")

        # Group by category
        categories = {
            "Database": [],
            "Vector Store": [],
            "Embeddings": [],
            "Indexes": [],
            "Configuration": [],
            "Performance": [],
            "Memory": [],
        }

        for check in self.checks:
            category = self._categorize_check(check.name)
            categories[category].append(check)

        # Print each category
        for category, checks in categories.items():
            if not checks:
                continue

            print(f"\n📋 {category.upper()}")
            print("-" * 40)

            for check in checks:
                latency_str = f" ({check.latency_ms:.1f}ms)" if check.latency_ms else ""
                print(f"{check.status.value} {check.name}{latency_str}")
                print(f"   {check.message}")

                if check.details:
                    for key, value in check.details.items():
                        print(f"   • {key}: {value}")

        # Summary
        print("\n📊 SUMMARY")
        print("-" * 40)
        green_count = sum(1 for c in self.checks if c.status == HealthStatus.GREEN)
        yellow_count = sum(1 for c in self.checks if c.status == HealthStatus.YELLOW)
        red_count = sum(1 for c in self.checks if c.status == HealthStatus.RED)

        print(f"🟢 Healthy: {green_count}")
        print(f"🟡 Warning: {yellow_count}")
        print(f"🔴 Critical: {red_count}")

        if overall == HealthStatus.RED:
            print("\n🚨 SYSTEM CRITICAL - Immediate attention required!")
        elif overall == HealthStatus.YELLOW:
            print("\n⚠️  SYSTEM WARNING - Monitor closely")
        else:
            print("\n✅ SYSTEM HEALTHY - All systems operational")

        print("=" * 80)

    def _categorize_check(self, name: str) -> str:
        """Categorize check by name."""
        name_lower = name.lower()
        if "database" in name_lower or "postgres" in name_lower or "connection" in name_lower:
            return "Database"
        elif "vector" in name_lower or "embedding" in name_lower:
            return "Vector Store"
        elif "index" in name_lower or "hnsw" in name_lower:
            return "Indexes"
        elif "config" in name_lower or "environment" in name_lower:
            return "Configuration"
        elif "memory" in name_lower or "ram" in name_lower:
            return "Memory"
        elif "latency" in name_lower or "performance" in name_lower or "speed" in name_lower:
            return "Performance"
        else:
            return "Database"

    async def run_all_checks(self):
        """Run all health checks."""
        print("🔍 Running comprehensive health checks...")

        # Database checks
        await self._check_database_connection()
        await self._check_database_schema()
        await self._check_table_sizes()
        await self._check_recent_ingestion()

        # Vector store checks
        await self._check_vector_extension()
        await self._check_embedding_dimensions()
        await self._check_vector_indexes()

        # Configuration checks
        await self._check_environment_variables()
        await self._check_config_consistency()

        # Performance checks
        await self._check_query_performance()
        await self._check_embedding_performance()

        # Memory checks
        await self._check_memory_usage()

        print("✅ All health checks completed")

    async def _check_database_connection(self):
        """Check database connectivity."""
        start_time = time.time()
        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()

            latency = (time.time() - start_time) * 1000
            self.add_check(
                HealthCheck(
                    name="Database Connection",
                    status=HealthStatus.GREEN,
                    message="Successfully connected to PostgreSQL",
                    latency_ms=latency,
                )
            )
        except Exception as e:
            self.add_check(
                HealthCheck(name="Database Connection", status=HealthStatus.RED, message=f"Failed to connect: {str(e)}")
            )

    async def _check_database_schema(self):
        """Check database schema integrity."""
        start_time = time.time()
        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()

            # Check required tables exist
            cursor.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('documents', 'document_chunks')
            """
            )
            tables = [row[0] for row in cursor.fetchall()]

            # Check required columns exist
            cursor.execute(
                """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'document_chunks' 
                AND column_name IN ('embedding', 'bm25_text', 'embedding_text', 'metadata')
            """
            )
            columns = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.close()
            conn.close()

            latency = (time.time() - start_time) * 1000

            missing_tables = set(["documents", "document_chunks"]) - set(tables)
            missing_columns = set(["embedding", "bm25_text", "embedding_text", "metadata"]) - set(columns.keys())

            if missing_tables or missing_columns:
                status = HealthStatus.RED
                message = f"Schema incomplete. Missing: tables={missing_tables}, columns={missing_columns}"
            else:
                status = HealthStatus.GREEN
                message = "Schema is complete and valid"

            self.add_check(
                HealthCheck(
                    name="Database Schema",
                    status=status,
                    message=message,
                    details={"tables": tables, "columns": list(columns.keys())},
                    latency_ms=latency,
                )
            )

        except Exception as e:
            self.add_check(
                HealthCheck(name="Database Schema", status=HealthStatus.RED, message=f"Schema check failed: {str(e)}")
            )

    async def _check_table_sizes(self):
        """Check table sizes and growth."""
        start_time = time.time()
        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE schemaname = 'public' 
                AND tablename IN ('documents', 'document_chunks')
                ORDER BY tablename, attname
            """
            )
            stats = cursor.fetchall()

            cursor.execute(
                """
                SELECT 
                    COUNT(*) as doc_count,
                    (SELECT COUNT(*) FROM document_chunks) as chunk_count
                FROM documents
            """
            )
            counts = cursor.fetchone()

            cursor.close()
            conn.close()

            latency = (time.time() - start_time) * 1000

            if counts is None:
                doc_count, chunk_count = 0, 0
            else:
                doc_count, chunk_count = counts
            avg_chunks_per_doc = chunk_count / doc_count if doc_count > 0 else 0

            if doc_count == 0:
                status = HealthStatus.RED
                message = "No documents found in database"
            elif chunk_count == 0:
                status = HealthStatus.RED
                message = "No chunks found in database"
            elif avg_chunks_per_doc < 1:
                status = HealthStatus.YELLOW
                message = "Low chunk-to-document ratio"
            else:
                status = HealthStatus.GREEN
                message = "Table sizes are healthy"

            self.add_check(
                HealthCheck(
                    name="Table Sizes",
                    status=status,
                    message=message,
                    details={
                        "documents": doc_count,
                        "chunks": chunk_count,
                        "avg_chunks_per_doc": round(avg_chunks_per_doc, 2),
                    },
                    latency_ms=latency,
                )
            )

        except Exception as e:
            self.add_check(
                HealthCheck(name="Table Sizes", status=HealthStatus.RED, message=f"Table size check failed: {str(e)}")
            )

    async def _check_recent_ingestion(self):
        """Check for recent ingestion activity."""
        start_time = time.time()
        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT 
                    MAX(created_at) as last_ingestion,
                    COUNT(DISTINCT metadata->>'ingest_run_id') as unique_runs,
                    COUNT(DISTINCT metadata->>'chunk_variant') as unique_variants
                FROM document_chunks
            """
            )
            result = cursor.fetchone()

            cursor.close()
            conn.close()

            latency = (time.time() - start_time) * 1000

            if result is None:
                last_ingestion, unique_runs, unique_variants = None, 0, 0
            else:
                last_ingestion, unique_runs, unique_variants = result

            if last_ingestion is None:
                status = HealthStatus.RED
                message = "No ingestion history found"
            else:
                hours_ago = (time.time() - last_ingestion.timestamp()) / 3600
                if hours_ago > 24:
                    status = HealthStatus.YELLOW
                    message = f"Last ingestion was {hours_ago:.1f} hours ago"
                else:
                    status = HealthStatus.GREEN
                    message = f"Recent ingestion activity ({hours_ago:.1f}h ago)"

            self.add_check(
                HealthCheck(
                    name="Recent Ingestion",
                    status=status,
                    message=message,
                    details={
                        "last_ingestion": str(last_ingestion) if last_ingestion else "Never",
                        "unique_runs": unique_runs,
                        "unique_variants": unique_variants,
                    },
                    latency_ms=latency,
                )
            )

        except Exception as e:
            self.add_check(
                HealthCheck(
                    name="Recent Ingestion", status=HealthStatus.RED, message=f"Ingestion check failed: {str(e)}"
                )
            )

    async def _check_vector_extension(self):
        """Check pgvector extension status."""
        start_time = time.time()
        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
            extension = cursor.fetchone()

            cursor.close()
            conn.close()

            latency = (time.time() - start_time) * 1000

            if extension:
                status = HealthStatus.GREEN
                message = "pgvector extension is installed and active"
            else:
                status = HealthStatus.RED
                message = "pgvector extension not found"

            self.add_check(HealthCheck(name="Vector Extension", status=status, message=message, latency_ms=latency))

        except Exception as e:
            self.add_check(
                HealthCheck(
                    name="Vector Extension", status=HealthStatus.RED, message=f"Vector extension check failed: {str(e)}"
                )
            )

    async def _check_embedding_dimensions(self):
        """Check embedding vector dimensions."""
        start_time = time.time()
        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()

            # Use the custom function we created in the SQL script
            cursor.execute("SELECT * FROM check_embedding_dimensions()")
            dimensions = cursor.fetchall()

            cursor.close()
            conn.close()

            latency = (time.time() - start_time) * 1000

            if not dimensions:
                status = HealthStatus.RED
                message = "No embeddings found"
            else:
                # Check if all dimensions are consistent and correct
                expected_dim = 384  # all-MiniLM-L6-v2
                mismatches = [row for row in dimensions if row[3] == "MISMATCH"]
                total_count = sum(row[2] for row in dimensions)

                if mismatches:
                    status = HealthStatus.RED
                    message = f"Embedding dimension mismatches detected: {len(mismatches)} tables"
                elif all(row[1] == expected_dim for row in dimensions):
                    status = HealthStatus.GREEN
                    message = f"All embeddings are correct dimension ({expected_dim})"
                else:
                    status = HealthStatus.YELLOW
                    message = "Mixed embedding dimensions detected"

            self.add_check(
                HealthCheck(
                    name="Embedding Dimensions",
                    status=status,
                    message=message,
                    details={
                        "total_embeddings": total_count,
                        "tables_checked": len(dimensions),
                        "dimensions": [
                            {"table": row[0], "dim": row[1], "count": row[2], "status": row[3]} for row in dimensions
                        ],
                    },
                    latency_ms=latency,
                )
            )

        except Exception as e:
            # Fallback to direct query if function doesn't exist yet
            try:
                conn = psycopg2.connect(self.db_connection_string)
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT 
                        'document_chunks' as table_name,
                        vector_dims(embedding) as dim,
                        COUNT(*) as count
                    FROM document_chunks 
                    WHERE embedding IS NOT NULL 
                    GROUP BY vector_dims(embedding)
                    ORDER BY count DESC
                    LIMIT 5
                """
                )
                dimensions = cursor.fetchall()

                cursor.close()
                conn.close()

                latency = (time.time() - start_time) * 1000

                if not dimensions:
                    status = HealthStatus.RED
                    message = "No embeddings found"
                else:
                    # Handle the tuple structure from the query
                    table_name, dim, count = dimensions[0]
                    if dim == 384:  # all-MiniLM-L6-v2
                        status = HealthStatus.GREEN
                        message = f"Embeddings are correct dimension ({dim})"
                    elif dim in [768, 1024, 1536]:  # Other common dimensions
                        status = HealthStatus.YELLOW
                        message = f"Embeddings dimension {dim} (may need model alignment)"
                    else:
                        status = HealthStatus.RED
                        message = f"Unexpected embedding dimension: {dim}"

                self.add_check(
                    HealthCheck(
                        name="Embedding Dimensions",
                        status=status,
                        message=message,
                        details={f"dim_{dim}": count for _, dim, count in dimensions},
                        latency_ms=latency,
                    )
                )

            except Exception as e2:
                self.add_check(
                    HealthCheck(
                        name="Embedding Dimensions",
                        status=HealthStatus.RED,
                        message=f"Embedding dimension check failed: {str(e2)}",
                    )
                )

    async def _check_vector_indexes(self):
        """Check vector index status."""
        start_time = time.time()
        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT 
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE tablename = 'document_chunks'
                AND indexdef LIKE '%embedding%'
            """
            )
            indexes = cursor.fetchall()

            cursor.close()
            conn.close()

            latency = (time.time() - start_time) * 1000

            if not indexes:
                status = HealthStatus.RED
                message = "No vector indexes found"
            else:
                index_names = [idx[0] for idx in indexes]
                if any("hnsw" in idx[1].lower() for idx in indexes):
                    status = HealthStatus.GREEN
                    message = "HNSW vector indexes are present"
                else:
                    status = HealthStatus.YELLOW
                    message = "Vector indexes present but may not be optimal"

            self.add_check(
                HealthCheck(
                    name="Vector Indexes",
                    status=status,
                    message=message,
                    details={"indexes": index_names},
                    latency_ms=latency,
                )
            )

        except Exception as e:
            self.add_check(
                HealthCheck(
                    name="Vector Indexes", status=HealthStatus.RED, message=f"Vector index check failed: {str(e)}"
                )
            )

    async def _check_environment_variables(self):
        """Check critical environment variables."""
        required_vars = ["POSTGRES_DSN", "OPENAI_API_KEY", "AWS_REGION"]

        missing_vars = []
        present_vars = []

        for var in required_vars:
            if os.getenv(var):
                present_vars.append(var)
            else:
                missing_vars.append(var)

        if missing_vars:
            status = HealthStatus.RED
            message = f"Missing environment variables: {', '.join(missing_vars)}"
        else:
            status = HealthStatus.GREEN
            message = "All required environment variables are set"

        self.add_check(
            HealthCheck(
                name="Environment Variables",
                status=status,
                message=message,
                details={"present": present_vars, "missing": missing_vars},
            )
        )

    async def _check_config_consistency(self):
        """Check configuration consistency across components."""
        start_time = time.time()
        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()

            # Check if active configuration is set
            cursor.execute("SELECT ingest_run_id FROM chunk_config_active WHERE key = 'active'")
            active_config = cursor.fetchone()

            if not active_config:
                status = HealthStatus.RED
                message = "No active configuration set"
                self.add_check(
                    HealthCheck(
                        name="Configuration Consistency",
                        status=status,
                        message=message,
                        latency_ms=(time.time() - start_time) * 1000,
                    )
                )
                return

            active_run_id = active_config[0]

            # Check configuration consistency for active run
            cursor.execute(
                """
                SELECT 
                    metadata->>'chunk_size' as chunk_size,
                    metadata->>'overlap_ratio' as overlap_ratio,
                    metadata->>'chunk_variant' as variant,
                    COUNT(*) as count
                FROM document_chunks 
                WHERE metadata->>'ingest_run_id' = %s
                AND metadata->>'chunk_size' IS NOT NULL
                GROUP BY 
                    metadata->>'chunk_size',
                    metadata->>'overlap_ratio', 
                    metadata->>'chunk_variant'
                ORDER BY count DESC
            """,
                (active_run_id,),
            )
            configs = cursor.fetchall()

            # Also check total configurations across all runs
            cursor.execute(
                """
                SELECT 
                    metadata->>'chunk_size' as chunk_size,
                    metadata->>'overlap_ratio' as overlap_ratio,
                    metadata->>'chunk_variant' as variant,
                    metadata->>'ingest_run_id' as run_id,
                    COUNT(*) as count
                FROM document_chunks 
                WHERE metadata->>'chunk_size' IS NOT NULL
                GROUP BY 
                    metadata->>'chunk_size',
                    metadata->>'overlap_ratio', 
                    metadata->>'chunk_variant',
                    metadata->>'ingest_run_id'
                ORDER BY count DESC
            """
            )
            all_configs = cursor.fetchall()

            cursor.close()
            conn.close()

            latency = (time.time() - start_time) * 1000

            if not configs:
                status = HealthStatus.RED
                message = f"No configuration metadata found for active run: {active_run_id}"
            else:
                active_configs = len(configs)
                total_runs = len(set(c[3] for c in all_configs))

                if active_configs == 1 and total_runs == 1:
                    status = HealthStatus.GREEN
                    message = "Configuration is consistent - single active configuration"
                elif active_configs == 1:
                    status = HealthStatus.YELLOW
                    message = f"Active configuration is consistent, but {total_runs} total runs exist"
                else:
                    status = HealthStatus.RED
                    message = f"Multiple configurations in active run ({active_configs} variants)"

            self.add_check(
                HealthCheck(
                    name="Configuration Consistency",
                    status=status,
                    message=message,
                    details={
                        "active_run_id": active_run_id,
                        "active_config_variants": len(configs),
                        "total_runs": len(set(c[3] for c in all_configs)),
                        "active_configs": [
                            {"size": c[0], "overlap": c[1], "variant": c[2], "count": c[3]} for c in configs
                        ],
                    },
                    latency_ms=latency,
                )
            )

        except Exception as e:
            self.add_check(
                HealthCheck(
                    name="Configuration Consistency",
                    status=HealthStatus.RED,
                    message=f"Configuration check failed: {str(e)}",
                )
            )

    async def _check_query_performance(self):
        """Check query performance with sample queries."""
        start_time = time.time()
        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()

            # Test vector similarity query
            cursor.execute(
                """
                SELECT embedding 
                FROM document_chunks 
                WHERE embedding IS NOT NULL 
                LIMIT 1
            """
            )
            sample_embedding = cursor.fetchone()

            if sample_embedding:
                query_start = time.time()
                cursor.execute(
                    """
                    SELECT id, 1 - (embedding <=> %s::vector) as similarity
                    FROM document_chunks 
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> %s::vector
                    LIMIT 10
                """,
                    (sample_embedding[0], sample_embedding[0]),
                )
                results = cursor.fetchall()
                query_time = (time.time() - query_start) * 1000

                if query_time < 100:
                    status = HealthStatus.GREEN
                    message = f"Vector queries are fast ({query_time:.1f}ms)"
                elif query_time < 500:
                    status = HealthStatus.YELLOW
                    message = f"Vector queries are slow ({query_time:.1f}ms)"
                else:
                    status = HealthStatus.RED
                    message = f"Vector queries are very slow ({query_time:.1f}ms)"
            else:
                status = HealthStatus.RED
                message = "No embeddings available for performance test"
                query_time = None

            cursor.close()
            conn.close()

            latency = (time.time() - start_time) * 1000

            self.add_check(
                HealthCheck(
                    name="Query Performance",
                    status=status,
                    message=message,
                    details={"vector_query_ms": query_time},
                    latency_ms=latency,
                )
            )

        except Exception as e:
            self.add_check(
                HealthCheck(
                    name="Query Performance", status=HealthStatus.RED, message=f"Performance check failed: {str(e)}"
                )
            )

    async def _check_embedding_performance(self):
        """Check embedding model performance."""
        start_time = time.time()
        try:
            # Import optimized embedder
            embedder = None
            try:
                from dspy_rag_system.src.utils.optimized_embeddings import OptimizedEmbedder

                embedder = OptimizedEmbedder()

                # Run benchmark
                benchmark_results = embedder.benchmark(num_texts=50)
                embedding_time = benchmark_results["batch_encoding_ms"]
                device = benchmark_results["device"]
                speedup = benchmark_results["speedup"]

            except ImportError:
                # Fallback to standard embedder
                model = SentenceTransformer("all-MiniLM-L6-v2")
                test_text = "This is a test document for embedding performance."

                embedding_start = time.time()
                embedding = model.encode(test_text)
                embedding_time = (time.time() - embedding_start) * 1000
                device = "cpu"
                speedup = 1.0

            if embedding_time < 20:
                status = HealthStatus.GREEN
                message = f"Embedding generation is excellent ({embedding_time:.1f}ms)"
            elif embedding_time < 50:
                status = HealthStatus.GREEN
                message = f"Embedding generation is fast ({embedding_time:.1f}ms)"
            elif embedding_time < 100:
                status = HealthStatus.YELLOW
                message = f"Embedding generation is acceptable ({embedding_time:.1f}ms)"
            else:
                status = HealthStatus.RED
                message = f"Embedding generation is slow ({embedding_time:.1f}ms)"

            self.add_check(
                HealthCheck(
                    name="Embedding Performance",
                    status=status,
                    message=message,
                    details={
                        "embedding_time_ms": embedding_time,
                        "device": device,
                        "speedup": speedup,
                        "optimized": "optimized_embeddings" in str(type(embedder)),
                    },
                    latency_ms=(time.time() - start_time) * 1000,
                )
            )

        except Exception as e:
            self.add_check(
                HealthCheck(
                    name="Embedding Performance",
                    status=HealthStatus.RED,
                    message=f"Embedding performance check failed: {str(e)}",
                )
            )

    async def _check_memory_usage(self):
        """Check system memory usage."""
        try:
            import psutil

            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            if memory_percent < 70:
                status = HealthStatus.GREEN
                message = f"Memory usage is healthy ({memory_percent:.1f}%)"
            elif memory_percent < 85:
                status = HealthStatus.YELLOW
                message = f"Memory usage is high ({memory_percent:.1f}%)"
            else:
                status = HealthStatus.RED
                message = f"Memory usage is critical ({memory_percent:.1f}%)"

            self.add_check(
                HealthCheck(
                    name="Memory Usage",
                    status=status,
                    message=message,
                    details={
                        "total_gb": round(memory.total / (1024**3), 2),
                        "available_gb": round(memory.available / (1024**3), 2),
                        "used_percent": memory_percent,
                    },
                )
            )

        except ImportError:
            self.add_check(
                HealthCheck(
                    name="Memory Usage",
                    status=HealthStatus.YELLOW,
                    message="psutil not available for memory monitoring",
                )
            )
        except Exception as e:
            self.add_check(
                HealthCheck(name="Memory Usage", status=HealthStatus.RED, message=f"Memory check failed: {str(e)}")
            )


async def main():
    """Main healthcheck execution."""
    print("🏥 Starting RAG System Health Check...")

    # Initialize healthcheck
    healthcheck = HealthcheckNotebook()

    # Run all checks
    await healthcheck.run_all_checks()

    # Print comprehensive report
    healthcheck.print_report()

    # Exit with appropriate code
    overall_status = healthcheck.get_overall_status()
    if overall_status == HealthStatus.RED:
        sys.exit(1)
    elif overall_status == HealthStatus.YELLOW:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
