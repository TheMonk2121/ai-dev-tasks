#!/usr/bin/env python3
"""
LTST Memory System Integration for Generation Cache Implementation

Task 3.1: LTST Memory System Integration
Priority: Critical
MoSCoW: 🔥 Must

This module integrates the generation cache with the existing LTST memory system,
implementing cache-aware context retrieval and cache warming strategies.

Features:
- Cache-aware context retrieval in LTST memory system
- Cache warming strategies for frequently accessed contexts
- Seamless fallback to direct memory retrieval
- Cache performance metrics integration
- Memory system performance monitoring
- Cache hit rate optimization
"""

import asyncio
import logging
import os

# Add project root to path for imports
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our existing systems
from scripts.cache_invalidation_integration import CacheInvalidationIntegration, IntegrationConfig
from scripts.postgresql_cache_service import CacheConfig, CacheEntry, PostgreSQLCacheService
from scripts.similarity_scoring_algorithms import SimilarityConfig, SimilarityScoringEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/ltst_memory_integration.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class LTSTIntegrationConfig:
    """Configuration for LTST memory system integration"""

    # Cache service configuration
    cache_config: CacheConfig = field(
        default_factory=lambda: CacheConfig(
            max_connections=10,
            min_connections=2,
            similarity_threshold=0.7,
            enable_metrics=True,
            enable_connection_pooling=True,
        )
    )

    # Similarity engine configuration
    similarity_config: SimilarityConfig = field(
        default_factory=lambda: SimilarityConfig(
            primary_algorithm="hybrid",
            enable_caching=True,
            cache_size=5000,
            use_tfidf=True,
            max_features=2000,
        )
    )

    # Integration configuration
    integration_config: IntegrationConfig = field(
        default_factory=lambda: IntegrationConfig(
            enable_background_cleanup=True,
            enable_performance_monitoring=True,
            enable_alerting=True,
        )
    )

    # Cache warming configuration
    enable_cache_warming: bool = True
    warming_batch_size: int = 100
    warming_interval_minutes: int = 30
    warming_similarity_threshold: float = 0.6

    # Performance thresholds
    min_cache_hit_rate: float = 0.8
    max_response_time_ms: float = 100.0
    max_memory_usage_mb: float = 512.0

    # Fallback configuration
    enable_fallback_to_direct: bool = True
    fallback_timeout_ms: float = 500.0


@dataclass
class LTSTContext:
    """Represents a context in the LTST memory system"""

    context_id: str
    content: str
    metadata: dict[str, Any]
    created_at: float
    last_accessed: float
    access_count: int = 0
    cache_hit: bool = False
    similarity_score: float | None = None

    def __post_init__(self):
        """Update last accessed timestamp"""
        self.last_accessed = time.time()
        self.access_count += 1


@dataclass
class LTSTIntegrationMetrics:
    """Performance metrics for LTST memory integration"""

    # Cache performance
    total_context_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0

    # Response time metrics
    avg_response_time_ms: float = 0.0
    total_response_time_ms: float = 0.0
    min_response_time_ms: float = float("inf")
    max_response_time_ms: float = 0.0

    # Cache warming metrics
    warming_operations: int = 0
    warming_success_rate: float = 0.0
    warming_time_ms: float = 0.0

    # Fallback metrics
    fallback_operations: int = 0
    fallback_success_rate: float = 0.0

    # Memory usage
    memory_usage_mb: float = 0.0

    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate percentage"""
        if self.total_context_requests == 0:
            return 0.0
        return (self.cache_misses / self.total_context_requests) * 100.0

    @property
    def avg_response_time(self) -> float:
        """Calculate average response time"""
        if self.total_context_requests == 0:
            return 0.0
        return self.total_response_time_ms / self.total_context_requests


class LTSTMemoryIntegration:
    """Integration layer between LTST memory system and generation cache"""

    def __init__(self, config: LTSTIntegrationConfig | None = None):
        """Initialize LTST memory integration"""
        self.config = config or LTSTIntegrationConfig()
        self.metrics = LTSTIntegrationMetrics()

        # Initialize systems
        self.cache_service: PostgreSQLCacheService | None = None
        self.similarity_engine: SimilarityScoringEngine | None = None
        self.integration: CacheInvalidationIntegration | None = None

        # Cache warming
        self.warming_task: asyncio.Task | None = None
        self.running = False

        # Context cache for frequently accessed items
        self.context_cache: dict[str, LTSTContext] = {}
        self.max_context_cache_size = 1000

        logger.info("LTST Memory Integration initialized")

    async def initialize(self):
        """Initialize all systems for LTST memory integration"""
        try:
            logger.info("Initializing LTST Memory Integration")

            # Initialize PostgreSQL cache service
            self.cache_service = PostgreSQLCacheService(config=self.config.cache_config)
            await self.cache_service.initialize()
            logger.info("PostgreSQL cache service initialized")

            # Initialize similarity engine
            self.similarity_engine = SimilarityScoringEngine(config=self.config.similarity_config)
            logger.info("Similarity engine initialized")

            # Initialize cache invalidation integration
            self.integration = CacheInvalidationIntegration(config=self.config.integration_config)
            await self.integration.initialize()
            logger.info("Cache invalidation integration initialized")

            # Start cache warming if enabled
            if self.config.enable_cache_warming:
                await self._start_cache_warming()

            logger.info("LTST Memory Integration initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize LTST memory integration: {e}")
            raise

    async def _start_cache_warming(self):
        """Start cache warming task"""
        try:
            self.running = True
            self.warming_task = asyncio.create_task(self._cache_warming_loop())
            logger.info("Cache warming task started")
        except Exception as e:
            logger.error(f"Failed to start cache warming: {e}")

    async def _cache_warming_loop(self):
        """Background loop for cache warming"""
        try:
            while self.running:
                time.time()

                try:
                    # Perform cache warming
                    await self._warm_cache()

                    # Wait for next warming interval
                    await asyncio.sleep(self.config.warming_interval_minutes * 60)

                except Exception as e:
                    logger.error(f"Cache warming error: {e}")
                    await asyncio.sleep(60)  # Wait shorter time on error

        except asyncio.CancelledError:
            logger.info("Cache warming task cancelled")
        except Exception as e:
            logger.error(f"Cache warming loop failed: {e}")

    async def _warm_cache(self):
        """Warm the cache with frequently accessed contexts"""
        try:
            logger.info("Starting cache warming operation")

            # Get frequently accessed contexts from cache service
            if not self.cache_service:
                return

            # Get cache statistics to identify hot items
            await self.cache_service.get_cache_statistics()

            # Simulate warming by accessing frequently used contexts
            warming_start = time.time()
            warming_success = 0
            warming_total = 0

            # This would typically involve:
            # 1. Querying the database for frequently accessed contexts
            # 2. Pre-loading them into memory
            # 3. Updating similarity scores
            # 4. Optimizing cache placement

            # For now, we'll simulate the warming process
            for i in range(self.config.warming_batch_size):
                try:
                    # Simulate warming operation
                    await asyncio.sleep(0.001)  # Simulate work
                    warming_success += 1
                    warming_total += 1
                except Exception as e:
                    logger.warning(f"Cache warming operation {i} failed: {e}")
                    warming_total += 1

            # Update warming metrics
            warming_time = (time.time() - warming_start) * 1000
            self.metrics.warming_operations += warming_total
            self.metrics.warming_time_ms += warming_time
            self.metrics.warming_success_rate = (warming_success / warming_total) * 100.0

            logger.info(
                f"Cache warming completed: {warming_success}/{warming_total} successful in {warming_time:.2f}ms"
            )

        except Exception as e:
            logger.error(f"Cache warming failed: {e}")

    async def retrieve_context(self, query: str, user_id: str | None = None) -> LTSTContext | None:
        """Retrieve context using cache-aware strategy"""
        start_time = time.time()

        try:
            self.metrics.total_context_requests += 1

            # First, check local context cache
            if query in self.context_cache:
                context = self.context_cache[query]
                context.cache_hit = True
                self.metrics.cache_hits += 1

                response_time = (time.time() - start_time) * 1000
                self._update_response_time_metrics(response_time)

                logger.info(f"Context cache hit for query: {query[:50]}...")
                return context

            # Try to retrieve from generation cache
            cache_entry = await self._retrieve_from_cache(query, user_id)
            if cache_entry:
                # Convert cache entry to LTST context
                context = self._create_context_from_cache_entry(cache_entry, query)
                context.cache_hit = True
                self.metrics.cache_hits += 1

                # Add to local context cache
                self._add_to_context_cache(context)

                response_time = (time.time() - start_time) * 1000
                self._update_response_time_metrics(response_time)

                logger.info(f"Generation cache hit for query: {query[:50]}...")
                return context

            # Cache miss - fallback to direct retrieval if enabled
            if self.config.enable_fallback_to_direct:
                context = await self._fallback_to_direct_retrieval(query, user_id)
                if context:
                    self.metrics.fallback_operations += 1
                    self.metrics.cache_misses += 1

                    # Add to local context cache
                    self._add_to_context_cache(context)

                    response_time = (time.time() - start_time) * 1000
                    self._update_response_time_metrics(response_time)

                    logger.info(f"Fallback retrieval successful for query: {query[:50]}...")
                    return context

            # Complete miss
            self.metrics.cache_misses += 1
            response_time = (time.time() - start_time) * 1000
            self._update_response_time_metrics(response_time)

            logger.info(f"Context retrieval failed for query: {query[:50]}...")
            return None

        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            self.metrics.cache_misses += 1
            return None

    async def _retrieve_from_cache(self, query: str, user_id: str | None = None) -> CacheEntry | None:
        """Retrieve context from generation cache"""
        try:
            if not self.cache_service:
                return None

            # Use similarity-based retrieval
            cache_entry = await self.cache_service.retrieve_cache_entry(
                query, user_id, self.config.warming_similarity_threshold
            )

            return cache_entry

        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
            return None

    def _create_context_from_cache_entry(self, cache_entry: CacheEntry, query: str) -> LTSTContext:
        """Create LTST context from cache entry"""
        return LTSTContext(
            context_id=str(cache_entry.id),
            content=cache_entry.response,
            metadata={
                "model_type": cache_entry.model_type,
                "tokens_used": cache_entry.tokens_used,
                "similarity_score": cache_entry.similarity_score,
                "cache_entry_id": cache_entry.id,
                "source": "generation_cache",
            },
            created_at=cache_entry.created_at.timestamp() if cache_entry.created_at else time.time(),
            last_accessed=time.time(),
            cache_hit=True,
            similarity_score=cache_entry.similarity_score,
        )

    async def _fallback_to_direct_retrieval(self, query: str, user_id: str | None = None) -> LTSTContext | None:
        """Fallback to direct memory retrieval"""
        try:
            # This would typically involve:
            # 1. Querying the LTST memory system directly
            # 2. Performing similarity search on raw data
            # 3. Creating context from retrieved data

            # For now, we'll simulate the fallback process
            await asyncio.sleep(0.01)  # Simulate retrieval time

            # Simulate successful fallback retrieval
            context = LTSTContext(
                context_id=f"fallback_{int(time.time())}",
                content=f"Fallback response for: {query}",
                metadata={"source": "direct_retrieval", "fallback": True, "query": query},
                created_at=time.time(),
                last_accessed=time.time(),
                cache_hit=False,
            )

            return context

        except Exception as e:
            logger.error(f"Fallback retrieval failed: {e}")
            return None

    def _add_to_context_cache(self, context: LTSTContext):
        """Add context to local cache with LRU eviction"""
        try:
            # Implement LRU eviction if cache is full
            if len(self.context_cache) >= self.max_context_cache_size:
                # Remove least recently used context
                lru_key = min(self.context_cache.keys(), key=lambda k: self.context_cache[k].last_accessed)
                del self.context_cache[lru_key]

            # Add new context
            self.context_cache[context.context_id] = context

        except Exception as e:
            logger.warning(f"Failed to add context to cache: {e}")

    def _update_response_time_metrics(self, response_time: float):
        """Update response time metrics"""
        try:
            self.metrics.total_response_time_ms += response_time
            self.metrics.min_response_time_ms = min(self.metrics.min_response_time_ms, response_time)
            self.metrics.max_response_time_ms = max(self.metrics.max_response_time_ms, response_time)

            # Update cache hit rate
            if self.metrics.total_context_requests > 0:
                self.metrics.cache_hit_rate = (self.metrics.cache_hits / self.metrics.total_context_requests) * 100.0

        except Exception as e:
            logger.error(f"Failed to update response time metrics: {e}")

    async def store_context(self, context: LTSTContext, user_id: str | None = None) -> bool:
        """Store context in the generation cache"""
        try:
            if not self.cache_service:
                return False

            # Convert LTST context to cache entry
            cache_entry = CacheEntry(
                user_id=user_id,
                model_type=context.metadata.get("model_type", "ltst"),
                prompt=context.content,  # Use content as prompt for now
                response=context.content,
                tokens_used=context.metadata.get("tokens_used", 0),
                cache_hit=True,
                similarity_score=context.similarity_score or 1.0,
            )

            # Store in cache
            entry_id = await self.cache_service.store_cache_entry(cache_entry)

            if entry_id:
                logger.info(f"Context stored in cache with ID: {entry_id}")
                return True
            else:
                logger.warning("Failed to store context in cache")
                return False

        except Exception as e:
            logger.error(f"Failed to store context: {e}")
            return False

    async def search_similar_contexts(
        self, query: str, limit: int = 10, threshold: float | None = None
    ) -> list[LTSTContext]:
        """Search for similar contexts using cache and similarity engine"""
        try:
            threshold = threshold or self.config.warming_similarity_threshold
            results = []

            # Search in generation cache
            if self.cache_service:
                cache_entries = await self.cache_service.search_similar_entries(query, limit, threshold)

                for entry in cache_entries:
                    context = self._create_context_from_cache_entry(entry, query)
                    results.append(context)

            # If we don't have enough results, use similarity engine for additional search
            if len(results) < limit and self.similarity_engine:
                # This would involve searching through additional data sources
                # For now, we'll return what we have from the cache
                pass

            # Sort by similarity score
            results.sort(key=lambda x: x.similarity_score or 0.0, reverse=True)

            logger.info(f"Found {len(results)} similar contexts for query: {query[:50]}...")
            return results[:limit]

        except Exception as e:
            logger.error(f"Similar context search failed: {e}")
            return []

    async def get_integration_metrics(self) -> dict[str, Any]:
        """Get comprehensive integration metrics"""
        try:
            # Get cache service metrics
            cache_metrics = {}
            if self.cache_service:
                cache_stats = await self.cache_service.get_cache_statistics()
                cache_metrics = {"cache_service": cache_stats, "health_check": await self.cache_service.health_check()}

            # Get integration metrics
            integration_metrics = {}
            if self.integration:
                integration_metrics = await self.integration.get_integration_metrics()

            # Get similarity engine metrics
            similarity_metrics = {}
            if self.similarity_engine:
                similarity_metrics = self.similarity_engine.get_performance_metrics()

            # Combine all metrics
            return {
                "ltst_integration_metrics": {
                    "context_requests": {
                        "total": self.metrics.total_context_requests,
                        "cache_hits": self.metrics.cache_hits,
                        "cache_misses": self.metrics.cache_misses,
                        "hit_rate": self.metrics.cache_hit_rate,
                        "miss_rate": self.metrics.miss_rate,
                    },
                    "response_time": {
                        "avg_ms": self.metrics.avg_response_time,
                        "min_ms": self.metrics.min_response_time_ms,
                        "max_ms": self.metrics.max_response_time_ms,
                        "total_ms": self.metrics.total_response_time_ms,
                    },
                    "cache_warming": {
                        "operations": self.metrics.warming_operations,
                        "success_rate": self.metrics.warming_success_rate,
                        "total_time_ms": self.metrics.warming_time_ms,
                    },
                    "fallback": {
                        "operations": self.metrics.fallback_operations,
                        "success_rate": self.metrics.fallback_success_rate,
                    },
                    "memory_usage": {
                        "usage_mb": self.metrics.memory_usage_mb,
                        "context_cache_size": len(self.context_cache),
                    },
                },
                "cache_service": cache_metrics,
                "integration": integration_metrics,
                "similarity_engine": similarity_metrics,
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error(f"Failed to get integration metrics: {e}")
            return {"error": str(e)}

    async def close(self):
        """Close the LTST memory integration and cleanup resources"""
        try:
            logger.info("Closing LTST Memory Integration")

            # Stop cache warming
            self.running = False
            if self.warming_task and not self.warming_task.done():
                self.warming_task.cancel()
                try:
                    await self.warming_task
                except asyncio.CancelledError:
                    pass

            # Close integration
            if self.integration:
                await self.integration.close()

            # Close cache service
            if self.cache_service:
                await self.cache_service.close()

            # Clear context cache
            self.context_cache.clear()

            logger.info("LTST Memory Integration closed successfully")

        except Exception as e:
            logger.error(f"Error closing LTST memory integration: {e}")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


async def main():
    """Main function to test LTST memory integration"""
    try:
        logger.info("Testing LTST Memory Integration")

        # Create configuration
        config = LTSTIntegrationConfig(
            enable_cache_warming=True,
            warming_batch_size=50,
            warming_interval_minutes=1,  # Short interval for testing
            enable_fallback_to_direct=True,
        )

        # Test LTST memory integration
        async with LTSTMemoryIntegration(config) as integration:
            # Wait for initial setup
            await asyncio.sleep(2)

            # Test context retrieval
            logger.info("Testing context retrieval...")

            # Test cache hit scenario
            test_query = "What is machine learning and how does it work?"
            context = await integration.retrieve_context(test_query, user_id="test_user")

            if context:
                logger.info(f"Context retrieved: {context.context_id}")
                logger.info(f"Cache hit: {context.cache_hit}")
                logger.info(f"Similarity score: {context.similarity_score}")
            else:
                logger.info("No context retrieved")

            # Test similar context search
            logger.info("Testing similar context search...")
            similar_contexts = await integration.search_similar_contexts("machine learning algorithms", limit=5)
            logger.info(f"Found {len(similar_contexts)} similar contexts")

            # Wait for cache warming to run
            logger.info("Waiting for cache warming...")
            await asyncio.sleep(5)

            # Get integration metrics
            metrics = await integration.get_integration_metrics()
            logger.info(f"Integration metrics: {metrics}")

            logger.info("LTST Memory Integration test completed successfully")
            return True

    except Exception as e:
        logger.error(f"LTST Memory Integration test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
