from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Union
from urllib.parse import urlparse

import asyncpg
from asyncpg import Connection, Pool

#!/usr/bin/env python3
"""
PostgreSQL Cache Service Core
=============================
Task 2.1: PostgreSQL Cache Service Core for B-1054 Generation Cache Implementation

This script implements the core PostgreSQL-based cache service with:
- Async/await support for non-blocking operations
- Vector similarity search using pgvector extension
- Cache retrieval and storage operations
- Performance monitoring and metrics collection
- Error handling and recovery mechanisms
- Configuration management and validation
"""

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database configuration - simplified for this script
def get_database_url():
    return os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")

def validate_database_config():
    database_url = get_database_url()
    return database_url.startswith("postgresql://")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/postgresql_cache_service.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    """Configuration for PostgreSQL cache service"""

    max_connections: int = 10
    min_connections: int = 2
    connection_timeout: float = 30.0
    command_timeout: float = 60.0
    similarity_threshold: float = 0.7
    max_cache_size_mb: int = 100
    enable_metrics: bool = True
    enable_connection_pooling: bool = True
    vector_dimension: int = 1536  # Default for OpenAI embeddings

@dataclass
class CacheEntry:
    """Represents a cache entry"""

    id: int | None = None
    user_id: str | None = None
    model_type: str | None = None
    prompt: str | None = None
    response: str | None = None
    tokens_used: int | None = None
    cache_hit: bool = False
    similarity_score: float = 0.0
    last_verified: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    embedding: list[float] | None = None

@dataclass
class CacheMetrics:
    """Cache performance metrics"""

    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_response_time_ms: float = 0.0
    total_response_time_ms: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100.0

    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_misses / self.total_requests) * 100.0

class PostgreSQLCacheService:
    """Core PostgreSQL cache service with async support and vector similarity search"""

    def __init__(self, database_url: str | None = None, config: CacheConfig | None = None):
        """Initialize PostgreSQL cache service"""
        self.database_url = database_url or get_database_url()
        self.config = config or CacheConfig()
        self.pool: Pool | None = None
        self.metrics = CacheMetrics()
        self.initialized = False

        # Validate database configuration
        if not validate_database_config():
            raise ValueError("Invalid database configuration")

        # Parse connection parameters
        self.connection_params = self._parse_connection_url()

    def _parse_connection_url(self) -> dict[str, Any]:
        """Parse PostgreSQL connection URL into connection parameters"""
        try:
            parsed = urlparse(self.database_url)

            return {
                "host": parsed.hostname or "localhost",
                "port": parsed.port or 5432,
                "user": parsed.username,
                "password": parsed.password,
                "database": parsed.path.lstrip("/"),
                "command_timeout": self.config.command_timeout,
                "server_settings": {"application_name": "postgresql_cache_service"},
            }
        except Exception as e:
            logger.error(f"Error parsing connection URL: {e}")
            raise

    async def initialize(self):
        """Initialize the cache service and connection pool"""
        try:
            if self.initialized:
                logger.info("Cache service already initialized")
                return

            logger.info("Initializing PostgreSQL Cache Service")

            # Create connection pool
            if self.config.enable_connection_pooling:
                self.pool = await asyncpg.create_pool(
                    **self.connection_params, min_size=self.config.min_connections, max_size=self.config.max_connections
                )
                logger.info(
                    f"Connection pool created: {self.config.min_connections}-{self.config.max_connections} connections"
                )
            else:
                # Single connection mode for testing
                self.pool = None
                logger.info("Single connection mode enabled")

            # Verify database connectivity and schema
            await self._verify_database_schema()

            # Initialize pgvector extension if needed
            await self._ensure_pgvector_extension()

            self.initialized = True
            logger.info("PostgreSQL Cache Service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize cache service: {e}")
            raise

    async def _verify_database_schema(self):
        """Verify that required database schema exists"""
        try:
            conn = await self._get_connection()
            try:
                # Check if episodic_logs table exists
                table_exists = await conn.fetchval(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = 'episodic_logs'
                    );
                """
                )

                if not table_exists:
                    raise ValueError("Table 'episodic_logs' does not exist. Run schema migration first.")

                # Check if required cache columns exist
                required_columns = ["cache_hit", "similarity_score", "last_verified"]
                for column in required_columns:
                    column_exists = await conn.fetchval(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns
                            WHERE table_schema = 'public'
                            AND table_name = 'episodic_logs'
                            AND column_name = $1
                        );
                    """,
                        column,
                    )

                    if not column_exists:
                        raise ValueError(f"Required column '{column}' does not exist. Run schema migration first.")

                logger.info("Database schema verification completed successfully")
            finally:
                if not self.pool:
                    await conn.close()

        except Exception as e:
            logger.error(f"Database schema verification failed: {e}")
            raise

    async def _ensure_pgvector_extension(self):
        """Ensure required extensions are available for similarity operations"""
        try:
            conn = await self._get_connection()
            try:
                # Check if pgvector extension exists
                pgvector_exists = await conn.fetchval(
                    """
                    SELECT EXISTS (
                        SELECT FROM pg_extension
                        WHERE extname = 'vector'
                    );
                """
                )

                # Check if pg_trgm extension exists (for text similarity)
                pg_trgm_exists = await conn.fetchval(
                    """
                    SELECT EXISTS (
                        SELECT FROM pg_extension
                        WHERE extname = 'pg_trgm'
                    );
                """
                )

                if not pgvector_exists:
                    logger.warning("pgvector extension not found. Vector similarity search will be limited.")
                    logger.info("Install pgvector extension for full vector search capabilities:")
                    logger.info("  CREATE EXTENSION IF NOT EXISTS vector;")
                else:
                    logger.info("pgvector extension found and available")

                if not pg_trgm_exists:
                    logger.warning("pg_trgm extension not found. Text similarity search will be limited.")
                    logger.info("Install pg_trgm extension for text similarity capabilities:")
                    logger.info("  CREATE EXTENSION IF NOT EXISTS pg_trgm;")
                else:
                    logger.info("pg_trgm extension found and available")

            finally:
                if not self.pool:
                    await conn.close()

        except Exception as e:
            logger.warning(f"Could not verify extensions: {e}")

    async def _get_connection(self) -> Pool | Connection:
        """Get database connection from pool or create new one"""
        if self.pool:
            return self.pool
        else:
            # Single connection mode
            return await asyncpg.connect(**self.connection_params)

    async def close(self):
        """Close the cache service and connection pool"""
        try:
            if self.pool:
                await self.pool.close()
                logger.info("Connection pool closed")

            self.initialized = False
            logger.info("PostgreSQL Cache Service closed")

        except Exception as e:
            logger.error(f"Error closing cache service: {e}")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def store_cache_entry(self, entry: CacheEntry) -> int:
        """Store a new cache entry in the database"""
        try:
            start_time = time.time()

            conn = await self._get_connection()
            try:
                # Insert new cache entry
                result = await conn.fetchrow(
                    """
                    INSERT INTO episodic_logs (
                        user_id, model_type, prompt, response, tokens_used,
                        cache_hit, similarity_score, last_verified, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    RETURNING id;
                """,
                    entry.user_id,
                    entry.model_type,
                    entry.prompt,
                    entry.response,
                    entry.tokens_used,
                    entry.cache_hit,
                    entry.similarity_score,
                    entry.last_verified or datetime.now(),
                    entry.created_at or datetime.now(),
                    datetime.now(),
                )

                if result is None:
                    raise RuntimeError("Failed to insert cache entry; no ID returned")
                entry_id = result["id"]

                # Update metrics
                self._update_metrics(start_time, cache_hit=False)

                logger.info(f"Cache entry stored successfully with ID: {entry_id}")
                return entry_id
            finally:
                if not self.pool:
                    await conn.close()

        except Exception as e:
            logger.error(f"Error storing cache entry: {e}")
            raise

    async def retrieve_cache_entry(
        self, prompt: str | None, user_id: str | None = None, similarity_threshold: float | None = None
    ) -> CacheEntry | None:
        """Retrieve a cache entry entry by prompt similarity"""
        try:
            start_time = time.time()
            threshold = similarity_threshold or self.config.similarity_threshold

            conn = await self._get_connection()
            try:
                # Check if similarity function is available
                similarity_function_exists = await conn.fetchval(
                    """
                    SELECT EXISTS (
                        SELECT 1 FROM pg_proc
                        WHERE proname = 'similarity'
                        AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
                    );
                """
                )

                if similarity_function_exists:
                    # Use similarity function for text matching
                    query = """
                        SELECT id, user_id, model_type, prompt, response, tokens_used,
                               cache_hit, similarity_score, last_verified, created_at, updated_at
                        FROM episodic_logs
                        WHERE (cache_hit = TRUE OR cache_hit = FALSE OR cache_hit IS NULL)
                        AND (
                            CASE
                                WHEN $1 IS NOT NULL THEN user_id = $1
                                ELSE TRUE
                            END
                        )
                        AND similarity(prompt, $2) > $3
                        ORDER BY similarity_score DESC, last_verified DESC
                        LIMIT 1;
                    """
                    result = await conn.fetchrow(query, user_id, prompt or "", threshold)
                else:
                    # Fallback to exact text matching when similarity function not available
                    if user_id:
                        query = """
                            SELECT id, user_id, model_type, prompt, response, tokens_used,
                                   cache_hit, similarity_score, last_verified, created_at, updated_at
                            FROM episodic_logs
                            WHERE (cache_hit = TRUE OR cache_hit = FALSE OR cache_hit IS NULL)
                            AND user_id = $1
                            AND prompt = $2
                            ORDER BY similarity_score DESC, last_verified DESC
                            LIMIT 1;
                        """
                        result = await conn.fetchrow(query, user_id, prompt or "")
                    else:
                        query = """
                            SELECT id, user_id, model_type, prompt, response, tokens_used,
                                   cache_hit, similarity_score, last_verified, created_at, updated_at
                            FROM episodic_logs
                            WHERE (cache_hit = TRUE OR cache_hit = FALSE OR cache_hit IS NULL)
                            AND prompt = $1
                            ORDER BY similarity_score DESC, last_verified DESC
                            LIMIT 1;
                        """
                        result = await conn.fetchrow(query, prompt or "")

                if result:
                    # Create cache entry from result
                    cache_entry = CacheEntry(
                        id=result["id"],
                        user_id=result["user_id"],
                        model_type=result["model_type"],
                        prompt=result["prompt"],
                        response=result["response"],
                        tokens_used=result["tokens_used"],
                        cache_hit=result["cache_hit"],
                        similarity_score=result["similarity_score"],
                        last_verified=result["last_verified"],
                        created_at=result["created_at"],
                        updated_at=result["updated_at"],
                    )

                    # Update cache hit metrics
                    self._update_metrics(start_time, cache_hit=True)

                    # Update last_verified timestamp (guard int | None)
                    if cache_entry.id is not None:
                        await self._update_cache_verification(int(cache_entry.id))

                    logger.info(
                        f"Cache hit: Entry {cache_entry.id} retrieved with similarity {cache_entry.similarity_score:.3f}"
                    )
                    return cache_entry
                else:
                    # Cache miss
                    self._update_metrics(start_time, cache_hit=False)
                    logger.info(f"Cache miss: No entry found for prompt with threshold {threshold}")
                    return None
            finally:
                if not self.pool:
                    await conn.close()

        except Exception as e:
            logger.error(f"Error retrieving cache entry: {e}")
            raise

    async def _update_cache_verification(self, entry_id: int):
        """Update the last_verified timestamp for a cache entry"""
        try:
            conn = await self._get_connection()
            try:
                await conn.execute(
                    """
                    UPDATE episodic_logs
                    SET last_verified = NOW(), updated_at = NOW()
                    WHERE id = $1;
                """,
                    entry_id,
                )
            finally:
                if not self.pool:
                    await conn.close()

        except Exception as e:
            logger.error(f"Error updating cache verification: {e}")

    async def search_similar_entries(
        self, prompt: str, limit: int = 10, similarity_threshold: float = 0.5
    ) -> list[CacheEntry]:
        """Search for similar cache entries"""
        try:
            conn = await self._get_connection()
            try:
                # Check if similarity function is available
                similarity_function_exists = await conn.fetchval(
                    """
                    SELECT EXISTS (
                        SELECT 1 FROM pg_proc
                        WHERE proname = 'similarity'
                        AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
                    );
                """
                )

                if similarity_function_exists:
                    # Use similarity function for text matching
                    query = """
                        SELECT id, user_id, model_type, prompt, response, tokens_used,
                               cache_hit, similarity_score, last_verified, created_at, updated_at
                        FROM episodic_logs
                        WHERE similarity(prompt, $1) > $2
                        ORDER BY similarity_score DESC, last_verified DESC
                        LIMIT $3;
                    """
                    results = await conn.fetch(query, prompt, similarity_threshold, limit)
                else:
                    # Fallback to basic text matching using ILIKE
                    query = """
                        SELECT id, user_id, model_type, prompt, response, tokens_used,
                               cache_hit, similarity_score, last_verified, created_at, updated_at
                        FROM episodic_logs
                        WHERE (
                            prompt ILIKE '%' || $1 || '%'
                            OR $1 ILIKE '%' || prompt || '%'
                        )
                        ORDER BY similarity_score DESC, last_verified DESC
                        LIMIT $2;
                    """
                    results = await conn.fetch(query, prompt, limit)

                entries = []
                for result in results:
                    entry = CacheEntry(
                        id=result["id"],
                        user_id=result["user_id"],
                        model_type=result["model_type"],
                        prompt=result["prompt"],
                        response=result["response"],
                        tokens_used=result["tokens_used"],
                        cache_hit=result["cache_hit"],
                        similarity_score=result["similarity_score"],
                        last_verified=result["last_verified"],
                        created_at=result["created_at"],
                        updated_at=result["updated_at"],
                    )
                    entries.append(entry)

                logger.info(f"Found {len(entries)} similar entries with threshold {similarity_threshold}")
                return entries
            finally:
                if not self.pool:
                    await conn.close()

        except Exception as e:
            logger.error(f"Error searching similar entries: {e}")
            raise

    async def update_cache_entry(self, entry_id: int, updates: dict[str, Any]) -> bool:
        """Update an existing cache entry"""
        try:
            conn = await self._get_connection()
            try:
                # Build dynamic UPDATE query
                set_clauses = []
                values = []
                param_count = 1

                for key, value in updates.items():
                    if key in ["prompt", "response", "tokens_used", "cache_hit", "similarity_score"]:
                        set_clauses.append(f"{key} = ${param_count}")
                        values.append(value)
                        param_count += 1

                if not set_clauses:
                    logger.warning("No valid fields to update")
                    return False

                # Add updated_at timestamp
                set_clauses.append("updated_at = NOW()")

                query = f"""
                    UPDATE episodic_logs
                    SET {', '.join(set_clauses)}
                    WHERE id = ${param_count};
                """

                values.append(entry_id)

                result = await conn.execute(query, *values)

                if result == "UPDATE 1":
                    logger.info(f"Cache entry {entry_id} updated successfully")
                    return True
                else:
                    logger.warning(f"No rows updated for entry {entry_id}")
                    return False
            finally:
                if not self.pool:
                    await conn.close()

        except Exception as e:
            logger.error(f"Error updating cache entry: {e}")
            raise

    async def delete_cache_entry(self, entry_id: int) -> bool:
        """Delete a cache entry"""
        try:
            conn = await self._get_connection()
            try:
                result = await conn.execute(
                    """
                    DELETE FROM episodic_logs WHERE id = $1;
                """,
                    entry_id,
                )

                if result == "DELETE 1":
                    logger.info(f"Cache entry {entry_id} deleted successfully")
                    return True
                else:
                    logger.warning(f"No rows deleted for entry {entry_id}")
                    return False
            finally:
                if not self.pool:
                    await conn.close()

        except Exception as e:
            logger.error(f"Error deleting cache entry: {e}")
            raise

    async def get_cache_statistics(self) -> dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            conn = await self._get_connection()
            try:
                # Get basic statistics
                stats = await conn.fetchrow(
                    """
                    SELECT
                        COUNT(*) as total_entries,
                        COUNT(*) FILTER (WHERE cache_hit = TRUE) as cache_hits,
                        COUNT(*) FILTER (WHERE cache_hit = FALSE) as cache_misses,
                        AVG(similarity_score) as avg_similarity,
                        MIN(last_verified) as oldest_verification,
                        MAX(last_verified) as newest_verification,
                        AVG(tokens_used) as avg_tokens
                    FROM episodic_logs;
                """
                )

                # Get table size information
                size_info = await conn.fetchrow(
                    """
                    SELECT
                        pg_size_pretty(pg_total_relation_size('episodic_logs')) as table_size,
                        pg_size_pretty(pg_relation_size('episodic_logs')) as data_size,
                        pg_size_pretty(pg_total_relation_size('episodic_logs') - pg_relation_size('episodic_logs')) as index_size
                    FROM pg_class
                    WHERE relname = 'episodic_logs';
                """
                )

                # Combine statistics
                cache_stats = {
                    "total_entries": stats["total_entries"] if stats else 0,
                    "cache_hits": stats["cache_hits"] if stats else 0,
                    "cache_misses": stats["cache_misses"] if stats else 0,
                    "avg_similarity": float(stats["avg_similarity"]) if stats and stats["avg_similarity"] else 0.0,
                    "oldest_verification": stats["oldest_verification"] if stats else None,
                    "newest_verification": stats["newest_verification"] if stats else None,
                    "avg_tokens": float(stats["avg_tokens"]) if stats and stats["avg_tokens"] else 0.0,
                    "table_size": size_info["table_size"] if size_info else "Unknown",
                    "data_size": size_info["data_size"] if size_info else "Unknown",
                    "index_size": size_info["index_size"] if size_info else "Unknown",
                    "service_metrics": {
                        "total_requests": self.metrics.total_requests,
                        "cache_hits": self.metrics.cache_hits,
                        "cache_misses": self.metrics.cache_misses,
                        "hit_rate": self.metrics.hit_rate,
                        "miss_rate": self.metrics.miss_rate,
                        "avg_response_time_ms": self.metrics.avg_response_time_ms,
                        "last_updated": self.metrics.last_updated.isoformat(),
                    },
                }

                return cache_stats
            finally:
                if not self.pool:
                    await conn.close()

        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {}

    def _update_metrics(self, start_time: float, cache_hit: bool):
        """Update performance metrics"""
        try:
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            self.metrics.total_requests += 1
            if cache_hit:
                self.metrics.cache_hits += 1
            else:
                self.metrics.cache_misses += 1

            # Update average response time
            self.metrics.total_response_time_ms += response_time
            self.metrics.avg_response_time_ms = self.metrics.total_response_time_ms / self.metrics.total_requests

            self.metrics.last_updated = datetime.now()

        except Exception as e:
            logger.error(f"Error updating metrics: {e}")

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on the cache service"""
        try:
            health_status = {
                "service": "postgresql_cache_service",
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "initialized": self.initialized,
                "connection_pool": self.pool is not None,
                "database_connection": False,
                "schema_valid": False,
                "metrics": {
                    "total_requests": self.metrics.total_requests,
                    "hit_rate": self.metrics.hit_rate,
                    "avg_response_time_ms": self.metrics.avg_response_time_ms,
                },
            }

            if not self.initialized:
                health_status["status"] = "not_initialized"
                return health_status

            # Test database connection
            try:
                conn = await self._get_connection()
                try:
                    # Simple query test
                    result = await conn.fetchval("SELECT 1")
                    if result == 1:
                        health_status["database_connection"] = True

                        # Test schema access
                        table_count = await conn.fetchval("SELECT COUNT(*) FROM episodic_logs")
                        if table_count is not None:
                            health_status["schema_valid"] = True
                finally:
                    if not self.pool:
                        await conn.close()

            except Exception as e:
                health_status["status"] = "unhealthy"
                health_status["error"] = str(e)
                logger.error(f"Health check failed: {e}")

            return health_status

        except Exception as e:
            logger.error(f"Error during health check: {e}")
            return {
                "service": "postgresql_cache_service",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_connection_pool_info(self) -> dict[str, Any]:
        """Return basic connection pool information for validators."""
        try:
            return {
                "pool_active": self.pool is not None,
                "min_size": self.config.min_connections if self.pool else 0,
                "max_size": self.config.max_connections if self.pool else 0,
                "pool_size": self.config.max_connections if self.pool else 0,
                "ssl_enabled": False,
                "initialized": self.initialized,
            }
        except Exception as e:
            logger.error(f"Error getting connection pool info: {e}")
            return {"pool_active": False, "error": str(e)}

async def main():
    """Main function to test PostgreSQL cache service"""
    try:
        logger.info("Testing PostgreSQL Cache Service")

        # Create configuration
        config = CacheConfig(max_connections=5, min_connections=1, similarity_threshold=0.7, enable_metrics=True)

        # Test cache service
        async with PostgreSQLCacheService(config=config) as cache_service:
            # Health check
            health = await cache_service.health_check()
            logger.info(f"Health check: {json.dumps(health, indent=2, default=str)}")

            # Get initial statistics
            initial_stats = await cache_service.get_cache_statistics()
            logger.info(f"Initial cache statistics: {json.dumps(initial_stats, indent=2, default=str)}")

            # Test cache entry storage
            test_entry = CacheEntry(
                user_id="test_user",
                model_type="gpt-4",
                prompt="What is machine learning?",
                response="Machine learning is a subset of artificial intelligence...",
                tokens_used=150,
                cache_hit=False,
                similarity_score=0.0,
            )

            entry_id = await cache_service.store_cache_entry(test_entry)
            logger.info(f"Test entry stored with ID: {entry_id}")

            # Test cache retrieval
            retrieved_entry = await cache_service.retrieve_cache_entry("What is machine learning?", user_id="test_user")

            if retrieved_entry:
                logger.info(f"Cache hit: Retrieved entry {retrieved_entry.id}")
            else:
                logger.info("Cache miss: No similar entry found")

            # Get final statistics
            final_stats = await cache_service.get_cache_statistics()
            logger.info(f"Final cache statistics: {json.dumps(final_stats, indent=2, default=str)}")

            logger.info("PostgreSQL Cache Service test completed successfully")

    except Exception as e:
        logger.error(f"PostgreSQL Cache Service test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
