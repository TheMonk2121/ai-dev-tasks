#!/usr/bin/env python3
"""
Cache Invalidation Service Integration for Generation Cache Implementation

Task 2.3: Cache Invalidation Service Integration
Priority: Critical
MoSCoW: 🔥 Must

This module integrates the cache invalidation system with the PostgreSQL cache service,
implementing automatic cache cleanup, TTL management, and performance optimization.

Features:
- Cache invalidation system integrated with PostgreSQL cache service
- Automatic TTL-based cache expiration
- Similarity threshold-based invalidation
- Frequency-based cache cleanup
- Manual invalidation capabilities
- Performance monitoring and alerting
"""

import asyncio
import logging
import os

# Add project root to path for imports
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our existing systems
from scripts.cache_invalidation_system import CacheInvalidationSystem, InvalidationConfig
from scripts.postgresql_cache_service import CacheConfig, PostgreSQLCacheService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/cache_invalidation_integration.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class IntegrationConfig:
    """Configuration for cache invalidation integration"""

    # Cache service configuration
    cache_config: CacheConfig = field(
        default_factory=lambda: CacheConfig(
            max_connections=5, min_connections=1, similarity_threshold=0.7, enable_metrics=True
        )
    )

    # Invalidation configuration
    invalidation_config: InvalidationConfig = field(
        default_factory=lambda: InvalidationConfig(
            ttl_hours=24,
            similarity_threshold=0.5,
            cleanup_interval_minutes=30,
            max_cache_size_mb=100,
            enable_logging=True,
            enable_monitoring=True,
        )
    )

    # Integration settings
    enable_background_cleanup: bool = True
    enable_performance_monitoring: bool = True
    enable_alerting: bool = True

    # Performance thresholds
    max_invalidation_time_ms: float = 1000.0
    max_cache_size_mb: float = 100.0
    min_cache_hit_rate: float = 0.8


@dataclass
class IntegrationMetrics:
    """Performance metrics for cache invalidation integration"""

    total_invalidations: int = 0
    ttl_invalidations: int = 0
    similarity_invalidations: int = 0
    frequency_invalidations: int = 0
    manual_invalidations: int = 0

    total_cleanup_time_ms: float = 0.0
    avg_cleanup_time_ms: float = 0.0

    cache_size_before_mb: float = 0.0
    cache_size_after_mb: float = 0.0

    performance_alerts: list[str] = field(default_factory=list)

    @property
    def total_cleanup_time_seconds(self) -> float:
        """Convert cleanup time to seconds"""
        return self.total_cleanup_time_ms / 1000.0

    @property
    def cache_size_reduction_mb(self) -> float:
        """Calculate cache size reduction"""
        return self.cache_size_before_mb - self.cache_size_after_mb


class CacheInvalidationIntegration:
    """Integration layer between cache invalidation system and PostgreSQL cache service"""

    def __init__(self, config: IntegrationConfig | None = None):
        """Initialize cache invalidation integration"""
        self.config = config or IntegrationConfig()
        self.metrics = IntegrationMetrics()

        # Initialize systems
        self.cache_service: PostgreSQLCacheService | None = None
        self.invalidation_system: CacheInvalidationSystem | None = None

        # Background task management
        self.cleanup_task: asyncio.Task | None = None
        self.running = False

        logger.info("Cache Invalidation Integration initialized")

    async def initialize(self):
        """Initialize both cache service and invalidation system"""
        try:
            logger.info("Initializing Cache Invalidation Integration")

            # Initialize PostgreSQL cache service
            self.cache_service = PostgreSQLCacheService(config=self.config.cache_config)
            await self.cache_service.initialize()
            logger.info("PostgreSQL cache service initialized")

            # Initialize cache invalidation system
            self.invalidation_system = CacheInvalidationSystem(config=self.config.invalidation_config)
            # Use context manager to connect
            self.invalidation_system.connect()
            logger.info("Cache invalidation system initialized")

            # Start background cleanup if enabled
            if self.config.enable_background_cleanup:
                await self._start_background_cleanup()

            logger.info("Cache Invalidation Integration initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize integration: {e}")
            raise

    async def _start_background_cleanup(self):
        """Start background cleanup task"""
        try:
            self.running = True
            self.cleanup_task = asyncio.create_task(self._background_cleanup_loop())
            logger.info("Background cleanup task started")
        except Exception as e:
            logger.error(f"Failed to start background cleanup: {e}")

    async def _background_cleanup_loop(self):
        """Background loop for automatic cache cleanup"""
        try:
            while self.running:
                time.time()

                try:
                    # Perform comprehensive cache cleanup
                    await self.perform_comprehensive_cleanup()

                    # Wait for next cleanup interval
                    await asyncio.sleep(self.config.invalidation_config.cleanup_interval_minutes * 60)

                except Exception as e:
                    logger.error(f"Background cleanup error: {e}")
                    # Wait shorter time on error
                    await asyncio.sleep(60)  # 1 minute

        except asyncio.CancelledError:
            logger.info("Background cleanup task cancelled")
        except Exception as e:
            logger.error(f"Background cleanup loop failed: {e}")

    async def perform_comprehensive_cleanup(self):
        """Perform comprehensive cache cleanup using all invalidation strategies"""
        try:
            start_time = time.time()
            logger.info("Starting comprehensive cache cleanup")

            # Get initial cache statistics
            initial_stats = await self.cache_service.get_cache_statistics()
            self.metrics.cache_size_before_mb = self._extract_cache_size_mb(initial_stats)

            # Perform TTL-based invalidation
            ttl_count = await self._perform_ttl_invalidation()
            self.metrics.ttl_invalidations += ttl_count

            # Perform similarity threshold invalidation
            similarity_count = await self._perform_similarity_invalidation()
            self.metrics.similarity_invalidations += similarity_count

            # Perform frequency-based invalidation
            frequency_count = await self._perform_frequency_invalidation()
            self.metrics.frequency_invalidations += frequency_count

            # Get final cache statistics
            final_stats = await self.cache_service.get_cache_statistics()
            self.metrics.cache_size_after_mb = self._extract_cache_size_mb(final_stats)

            # Update metrics
            cleanup_time = (time.time() - start_time) * 1000
            self.metrics.total_cleanup_time_ms += cleanup_time
            self.metrics.total_invalidations += ttl_count + similarity_count + frequency_count

            # Check performance thresholds
            await self._check_performance_thresholds(cleanup_time)

            logger.info(
                f"Comprehensive cleanup completed: {ttl_count + similarity_count + frequency_count} entries invalidated in {cleanup_time:.2f}ms"
            )

        except Exception as e:
            logger.error(f"Comprehensive cleanup failed: {e}")
            raise

    async def _perform_ttl_invalidation(self) -> int:
        """Perform TTL-based cache invalidation"""
        try:
            if not self.invalidation_system:
                return 0

            # Use the invalidation system's TTL invalidation
            invalidated_count = self.invalidation_system.invalidate_by_ttl()
            logger.info(f"TTL invalidation: {invalidated_count} entries invalidated")
            return invalidated_count

        except Exception as e:
            logger.error(f"TTL invalidation failed: {e}")
            return 0

    async def _perform_similarity_invalidation(self) -> int:
        """Perform similarity threshold-based invalidation"""
        try:
            if not self.invalidation_system:
                return 0

            # Use the invalidation system's similarity threshold invalidation
            invalidated_count = self.invalidation_system.invalidate_by_similarity_threshold()
            logger.info(f"Similarity threshold invalidation: {invalidated_count} entries invalidated")
            return invalidated_count

        except Exception as e:
            logger.error(f"Similarity threshold invalidation failed: {e}")
            return 0

    async def _perform_frequency_invalidation(self) -> int:
        """Perform frequency-based invalidation"""
        try:
            if not self.invalidation_system:
                return 0

            # Use the invalidation system's frequency-based invalidation
            invalidated_count = self.invalidation_system.invalidate_by_frequency()
            logger.info(f"Frequency-based invalidation: {invalidated_count} entries invalidated")
            return invalidated_count

        except Exception as e:
            logger.error(f"Frequency-based invalidation failed: {e}")
            return 0

    async def manual_invalidation(self, entry_ids: list[int]) -> int:
        """Manually invalidate specific cache entries"""
        try:
            if not self.invalidation_system:
                return 0

            # Use the invalidation system's manual invalidation
            invalidated_count = self.invalidation_system.manual_invalidation(entry_ids)
            self.metrics.manual_invalidations += invalidated_count
            self.metrics.total_invalidations += invalidated_count

            logger.info(f"Manual invalidation: {invalidated_count} entries invalidated")
            return invalidated_count

        except Exception as e:
            logger.error(f"Manual invalidation failed: {e}")
            return 0

    async def _check_performance_thresholds(self, cleanup_time: float):
        """Check performance thresholds and generate alerts"""
        try:
            if not self.config.enable_performance_monitoring:
                return

            # Check cleanup time threshold
            if cleanup_time > self.config.max_invalidation_time_ms:
                alert = f"Cache cleanup exceeded time threshold: {cleanup_time:.2f}ms > {self.config.max_invalidation_time_ms}ms"
                self.metrics.performance_alerts.append(alert)
                logger.warning(alert)

            # Check cache hit rate
            cache_stats = await self.cache_service.get_cache_statistics()
            hit_rate = cache_stats.get("service_metrics", {}).get("hit_rate", 0.0)

            if hit_rate < self.config.min_cache_hit_rate:
                alert = f"Cache hit rate below threshold: {hit_rate:.2%} < {self.config.min_cache_hit_rate:.2%}"
                self.metrics.performance_alerts.append(alert)
                logger.warning(alert)

            # Check cache size
            cache_size_mb = self._extract_cache_size_mb(cache_stats)
            if cache_size_mb > self.config.max_cache_size_mb:
                alert = f"Cache size exceeded threshold: {cache_size_mb:.2f}MB > {self.config.max_cache_size_mb:.2f}MB"
                self.metrics.performance_alerts.append(alert)
                logger.warning(alert)

        except Exception as e:
            logger.error(f"Performance threshold check failed: {e}")

    def _extract_cache_size_mb(self, stats: dict[str, Any]) -> float:
        """Extract cache size in MB from statistics"""
        try:
            table_size_str = stats.get("table_size", "0 bytes")
            # Parse size string like "128 kB" or "1.2 MB"
            if "MB" in table_size_str:
                return float(table_size_str.replace(" MB", ""))
            elif "kB" in table_size_str:
                return float(table_size_str.replace(" kB", "")) / 1024.0
            elif "bytes" in table_size_str:
                return float(table_size_str.replace(" bytes", "")) / (1024.0 * 1024.0)
            else:
                return 0.0
        except Exception:
            return 0.0

    async def get_integration_metrics(self) -> dict[str, Any]:
        """Get comprehensive integration metrics"""
        try:
            # Get cache service metrics
            cache_metrics = {}
            if self.cache_service:
                cache_stats = await self.cache_service.get_cache_statistics()
                cache_metrics = {"cache_service": cache_stats, "health_check": await self.cache_service.health_check()}

            # Get invalidation system metrics
            invalidation_metrics = {}
            if self.invalidation_system:
                invalidation_metrics = {
                    "invalidation_system": self.invalidation_system.get_cache_statistics(),
                    "cleanup_status": {
                        "background_cleanup_running": self.running,
                        "cleanup_task_active": self.cleanup_task and not self.cleanup_task.done(),
                    },
                }

            # Combine all metrics
            return {
                "integration_metrics": {
                    "total_invalidations": self.metrics.total_invalidations,
                    "invalidation_breakdown": {
                        "ttl": self.metrics.ttl_invalidations,
                        "similarity": self.metrics.similarity_invalidations,
                        "frequency": self.metrics.frequency_invalidations,
                        "manual": self.metrics.manual_invalidations,
                    },
                    "performance": {
                        "total_cleanup_time_ms": self.metrics.total_cleanup_time_ms,
                        "avg_cleanup_time_ms": self.metrics.avg_cleanup_time_ms,
                        "cache_size_reduction_mb": self.metrics.cache_size_reduction_mb,
                    },
                    "alerts": self.metrics.performance_alerts,
                },
                "cache_service": cache_metrics,
                "invalidation_system": invalidation_metrics,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get integration metrics: {e}")
            return {"error": str(e)}

    async def close(self):
        """Close the integration and cleanup resources"""
        try:
            logger.info("Closing Cache Invalidation Integration")

            # Stop background cleanup
            self.running = False
            if self.cleanup_task and not self.cleanup_task.done():
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass

            # Close cache service
            if self.cache_service:
                await self.cache_service.close()

            # Close invalidation system
            if self.invalidation_system:
                self.invalidation_system.disconnect()

            logger.info("Cache Invalidation Integration closed successfully")

        except Exception as e:
            logger.error(f"Error closing integration: {e}")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


async def main():
    """Main function to test cache invalidation integration"""
    try:
        logger.info("Testing Cache Invalidation Integration")

        # Create configuration
        config = IntegrationConfig(
            enable_background_cleanup=True, enable_performance_monitoring=True, enable_alerting=True
        )

        # Test integration
        async with CacheInvalidationIntegration(config) as integration:
            # Get initial metrics
            initial_metrics = await integration.get_integration_metrics()
            logger.info(f"Initial integration metrics: {initial_metrics}")

            # Perform manual invalidation test
            logger.info("Testing manual invalidation...")
            manual_result = await integration.manual_invalidation([1, 2, 3])
            logger.info(f"Manual invalidation result: {manual_result}")

            # Wait for background cleanup to run
            logger.info("Waiting for background cleanup...")
            await asyncio.sleep(5)

            # Get final metrics
            final_metrics = await integration.get_integration_metrics()
            logger.info(f"Final integration metrics: {final_metrics}")

            logger.info("Cache Invalidation Integration test completed successfully")
            return True

    except Exception as e:
        logger.error(f"Cache Invalidation Integration test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
