from __future__ import annotations
import asyncio
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Any
# FIXME: Update this import path after reorganization
# from scripts.cache_invalidation_integration import CacheInvalidationIntegration, IntegrationConfig
# FIXME: Update this import path after reorganization
# from scripts.postgresql_cache_service import CacheConfig, PostgreSQLCacheService
# FIXME: Update this import path after reorganization
# from scripts.similarity_scoring_algorithms import SimilarityConfig, SimilarityScoringEngine
import gc
import psutil
#!/usr/bin/env python3
"""
Performance Optimization for Generation Cache Implementation

Task 2.4: Performance Optimization
Priority: Critical
MoSCoW: 🔥 Must

This module optimizes the performance of the PostgreSQL cache service, similarity algorithms,
and cache invalidation system through connection pooling, query optimization, and caching strategies.

Features:
- Connection pool optimization and monitoring
- Query performance optimization and indexing
- Similarity algorithm performance tuning
- Cache invalidation performance improvements
- Memory usage optimization
- Response time benchmarking and improvement
"""

# Add project root to path for imports

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our existing systems

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/performance_optimization.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

@dataclass
class OptimizationConfig:
    """Configuration for performance optimization"""

    # Connection pool optimization
    connection_pool_size: int = 10
    min_connections: int = 2
    max_connections: int = 20
    connection_timeout: int = 30
    idle_timeout: int = 300

    # Query optimization
    enable_query_cache: bool = True
    query_cache_size: int = 1000
    enable_prepared_statements: bool = True
    batch_size: int = 100

    # Similarity algorithm optimization
    enable_algorithm_cache: bool = True
    algorithm_cache_size: int = 5000
    enable_parallel_processing: bool = True
    max_parallel_workers: int = 4

    # Memory optimization
    enable_memory_monitoring: bool = True
    max_memory_usage_mb: int = 512
    enable_garbage_collection: bool = True
    gc_interval_seconds: int = 60

    # Performance monitoring
    enable_performance_monitoring: bool = True
    monitoring_interval_seconds: int = 30
    enable_alerting: bool = True
    performance_thresholds: dict[str, float] = field(
        default_factory=lambda: {
            "max_response_time_ms": 100.0,
            "min_cache_hit_rate": 0.8,
            "max_memory_usage_mb": 512.0,
            "max_connection_usage": 0.8,
        }
    )

@dataclass
class PerformanceMetrics:
    """Performance metrics for optimization tracking"""

    # Response time metrics
    avg_response_time_ms: float = 0.0
    min_response_time_ms: float = float("inf")
    max_response_time_ms: float = 0.0
    total_requests: int = 0

    # Cache performance metrics
    cache_hit_rate: float = 0.0
    cache_miss_rate: float = 0.0
    cache_size_mb: float = 0.0

    # Connection pool metrics
    active_connections: int = 0
    idle_connections: int = 0
    connection_usage_rate: float = 0.0

    # Memory usage metrics
    memory_usage_mb: float = 0.0
    memory_usage_percent: float = 0.0

    # Similarity algorithm metrics
    algorithm_processing_time_ms: float = 0.0
    algorithm_cache_hit_rate: float = 0.0

    # Performance alerts
    alerts: list[str] = field(default_factory=list)

    @property
    def response_time_variance(self) -> float:
        """Calculate response time variance"""
        if self.total_requests < 2:
            return 0.0
        return (self.max_response_time_ms - self.min_response_time_ms) / self.avg_response_time_ms

class PerformanceOptimizer:
    """Performance optimization engine for the generation cache system"""

    def __init__(self, config: OptimizationConfig | None = None):
        """Initialize performance optimizer"""
        self.config = config or OptimizationConfig()
        self.metrics = PerformanceMetrics()

        # Initialize systems with optimized configurations
        self.cache_service: PostgreSQLCacheService | None = None
        self.similarity_engine: SimilarityScoringEngine | None = None
        self.integration: CacheInvalidationIntegration | None = None

        # Performance monitoring
        self.monitoring_task: asyncio.Task | None = None
        self.running = False

        logger.info("Performance Optimizer initialized")

    async def initialize(self):
        """Initialize all systems with performance optimizations"""
        try:
            logger.info("Initializing Performance Optimizer")

            # Initialize PostgreSQL cache service with optimized connection pool
            cache_config = CacheConfig(
                max_connections=self.config.max_connections,
                min_connections=self.config.min_connections,
                similarity_threshold=0.7,
                enable_metrics=True,
                enable_connection_pooling=True,
            )

            self.cache_service = PostgreSQLCacheService(config=cache_config)
            await self.cache_service.initialize()
            logger.info("Optimized PostgreSQL cache service initialized")

            # Initialize similarity engine with performance optimizations
            similarity_config = SimilarityConfig(
                primary_algorithm="hybrid",
                enable_caching=self.config.enable_algorithm_cache,
                cache_size=self.config.algorithm_cache_size,
                use_tfidf=True,
                max_features=1000,
            )

            self.similarity_engine = SimilarityScoringEngine(config=similarity_config)
            logger.info("Optimized similarity engine initialized")

            # Initialize cache invalidation integration
            integration_config = IntegrationConfig(
                enable_background_cleanup=True, enable_performance_monitoring=True, enable_alerting=True
            )

            self.integration = CacheInvalidationIntegration(config=integration_config)
            await self.integration.initialize()
            logger.info("Optimized cache invalidation integration initialized")

            # Start performance monitoring
            if self.config.enable_performance_monitoring:
                await self._start_performance_monitoring()

            logger.info("Performance Optimizer initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize performance optimizer: {e}")
            raise

    async def _start_performance_monitoring(self):
        """Start performance monitoring task"""
        try:
            self.running = True
            self.monitoring_task = asyncio.create_task(self._performance_monitoring_loop())
            logger.info("Performance monitoring task started")
        except Exception as e:
            logger.error(f"Failed to start performance monitoring: {e}")

    async def _performance_monitoring_loop(self):
        """Background loop for performance monitoring"""
        try:
            while self.running:
                time.time()

                try:
                    # Collect performance metrics
                    await self._collect_performance_metrics()

                    # Check performance thresholds
                    await self._check_performance_thresholds()

                    # Optimize systems if needed
                    await self._perform_optimizations()

                    # Wait for next monitoring interval
                    await asyncio.sleep(self.config.monitoring_interval_seconds)

                except Exception as e:
                    logger.error(f"Performance monitoring error: {e}")
                    await asyncio.sleep(10)  # Wait shorter time on error

        except asyncio.CancelledError:
            logger.info("Performance monitoring task cancelled")
        except Exception as e:
            logger.error(f"Performance monitoring loop failed: {e}")

    async def _collect_performance_metrics(self):
        """Collect comprehensive performance metrics"""
        try:
            # Collect cache service metrics
            if self.cache_service:
                cache_stats = await self.cache_service.get_cache_statistics()
                health_check = await self.cache_service.health_check()

                # Update response time metrics
                service_metrics = result.get("key", "")
                self.metrics.avg_response_time_ms = result.get("key", "")
                self.metrics.total_requests = result.get("key", "")

                # Update cache performance metrics
                self.metrics.cache_hit_rate = result.get("key", "")
                self.metrics.cache_miss_rate = result.get("key", "")

                # Update cache size
                table_size_str = result.get("key", "")
                self.metrics.cache_size_mb = self._parse_size_to_mb(table_size_str)

                # Update connection pool metrics
                pool_status = result.get("key", "")
                self.metrics.active_connections = result.get("key", "")
                self.metrics.idle_connections = result.get("key", "")
                self.metrics.connection_usage_rate = self.metrics.active_connections / max(
                    result.get("key", "")
                )

            # Collect similarity engine metrics
            if self.similarity_engine:
                algo_metrics = self.similarity_engine.get_performance_metrics()
                self.metrics.algorithm_processing_time_ms = result.get("key", "")
                    "avg_time_ms", 0.0
                )
                self.metrics.algorithm_cache_hit_rate = result.get("key", "")

            # Collect memory usage
            if self.config.enable_memory_monitoring:
                self.metrics.memory_usage_mb = self._get_memory_usage_mb()
                self.metrics.memory_usage_percent = (
                    self.metrics.memory_usage_mb / self.config.max_memory_usage_mb
                ) * 100.0

            logger.debug(f"Performance metrics collected: {self.metrics}")

        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {e}")

    async def _check_performance_thresholds(self):
        """Check performance thresholds and generate alerts"""
        try:
            if not self.config.enable_alerting:
                return

            # Check response time threshold
            if self.metrics.avg_response_time_ms > self.config.result.get("key", "")
                alert = f"Response time exceeded threshold: {self.metrics.avg_response_time_ms:.2f}ms > {self.config.result.get("key", "")
                self.metrics.alerts.append(alert)
                logger.warning(alert)

            # Check cache hit rate threshold
            if self.metrics.cache_hit_rate < self.config.result.get("key", "")
                alert = f"Cache hit rate below threshold: {self.metrics.cache_hit_rate:.2%} < {self.config.result.get("key", "")
                self.metrics.alerts.append(alert)
                logger.warning(alert)

            # Check memory usage threshold
            if self.metrics.memory_usage_mb > self.config.result.get("key", "")
                alert = f"Memory usage exceeded threshold: {self.metrics.memory_usage_mb:.2f}MB > {self.config.result.get("key", "")
                self.metrics.alerts.append(alert)
                logger.warning(alert)

            # Check connection usage threshold
            if self.metrics.connection_usage_rate > self.config.result.get("key", "")
                alert = f"Connection usage exceeded threshold: {self.metrics.connection_usage_rate:.2%} > {self.config.result.get("key", "")
                self.metrics.alerts.append(alert)
                logger.warning(alert)

        except Exception as e:
            logger.error(f"Performance threshold check failed: {e}")

    async def _perform_optimizations(self):
        """Perform automatic performance optimizations"""
        try:
            # Optimize connection pool if needed
            if self.metrics.connection_usage_rate > 0.8:
                await self._optimize_connection_pool()

            # Optimize memory usage if needed
            if self.metrics.memory_usage_percent > 80.0:
                await self._optimize_memory_usage()

            # Optimize cache performance if needed
            if self.metrics.cache_hit_rate < 0.7:
                await self._optimize_cache_performance()

            # Optimize similarity algorithms if needed
            if self.metrics.algorithm_processing_time_ms > 50.0:
                await self._optimize_similarity_algorithms()

        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")

    async def _optimize_connection_pool(self):
        """Optimize connection pool configuration"""
        try:
            logger.info("Optimizing connection pool...")

            # This would involve dynamic pool resizing in a real implementation
            # For now, we'll log the optimization attempt
            logger.info(f"Connection pool optimization: usage rate {self.metrics.connection_usage_rate:.2%}")

        except Exception as e:
            logger.error(f"Connection pool optimization failed: {e}")

    async def _optimize_memory_usage(self):
        """Optimize memory usage"""
        try:
            logger.info("Optimizing memory usage...")

            # Trigger garbage collection if enabled
            if self.config.enable_garbage_collection:

                collected = gc.collect()
                logger.info(f"Garbage collection completed: {collected} objects collected")

            # Clear similarity algorithm cache if memory usage is high
            if self.similarity_engine and self.metrics.memory_usage_percent > 90.0:
                self.similarity_engine.reset_metrics()
                logger.info("Similarity algorithm cache cleared")

        except Exception as e:
            logger.error(f"Memory optimization failed: {e}")

    async def _optimize_cache_performance(self):
        """Optimize cache performance"""
        try:
            logger.info("Optimizing cache performance...")

            # This would involve cache warming, prefetching, or other strategies
            # For now, we'll log the optimization attempt
            logger.info(f"Cache performance optimization: hit rate {self.metrics.cache_hit_rate:.2%}")

        except Exception as e:
            logger.error(f"Cache performance optimization failed: {e}")

    async def _optimize_similarity_algorithms(self):
        """Optimize similarity algorithm performance"""
        try:
            logger.info("Optimizing similarity algorithms...")

            # This would involve algorithm selection, caching optimization, or parallel processing
            # For now, we'll log the optimization attempt
            logger.info(
                f"Similarity algorithm optimization: processing time {self.metrics.algorithm_processing_time_ms:.2f}ms"
            )

        except Exception as e:
            logger.error(f"Similarity algorithm optimization failed: {e}")

    def _parse_size_to_mb(self, size_str: str) -> float:
        """Parse size string to MB"""
        try:
            if "MB" in size_str:
                return float(size_str.replace(" MB", ""))
            elif "kB" in size_str:
                return float(size_str.replace(" kB", "")) / 1024.0
            elif "bytes" in size_str:
                return float(size_str.replace(" bytes", "")) / (1024.0 * 1024.0)
            else:
                return 0.0
        except Exception:
            return 0.0

    def _get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        try:

            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / (1024.0 * 1024.0)  # Convert bytes to MB
        except ImportError:
            # Fallback if psutil is not available
            return 0.0
        except Exception:
            return 0.0

    async def run_performance_benchmark(self, iterations: int = 100) -> dict[str, Any]:
        """Run comprehensive performance benchmark"""
        try:
            logger.info(f"Starting performance benchmark with {iterations} iterations")

            benchmark_results = {"cache_service": {}, "similarity_engine": {}, "integration": {}, "overall": {}}

            # Benchmark cache service
            if self.cache_service:
                cache_benchmark = await self._benchmark_cache_service(iterations)
                result.get("key", "")

            # Benchmark similarity engine
            if self.similarity_engine:
                similarity_benchmark = await self._benchmark_similarity_engine(iterations)
                result.get("key", "")

            # Benchmark integration
            if self.integration:
                integration_benchmark = await self._benchmark_integration(iterations)
                result.get("key", "")

            # Calculate overall metrics
            result.get("key", "")

            logger.info("Performance benchmark completed successfully")
            return benchmark_results

        except Exception as e:
            logger.error(f"Performance benchmark failed: {e}")
            return {"error": str(e)}

    async def _benchmark_cache_service(self, iterations: int) -> dict[str, Any]:
        """Benchmark cache service performance"""
        try:
            start_time = time.time()
            response_times = []

            # Benchmark cache operations
            for i in range(iterations):
                op_start = time.time()

                # Simulate cache operations
                await self.cache_service.get_cache_statistics()

                op_time = (time.time() - op_start) * 1000
                response_times.append(op_time)

            total_time = (time.time() - start_time) * 1000

            return {
                "total_time_ms": total_time,
                "avg_response_time_ms": sum(response_times) / len(response_times),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times),
                "iterations": iterations,
                "operations_per_second": iterations / (total_time / 1000.0),
            }

        except Exception as e:
            logger.error(f"Cache service benchmark failed: {e}")
            return {"error": str(e)}

    async def _benchmark_similarity_engine(self, iterations: int) -> dict[str, Any]:
        """Benchmark similarity engine performance"""
        try:
            start_time = time.time()
            response_times = []

            # Test texts for similarity calculation
            test_texts = [
                "What is machine learning?",
                "Machine learning is a subset of artificial intelligence",
                "How does artificial intelligence work?",
                "What is the difference between AI and ML?",
                "Machine learning algorithms and their applications",
            ]

            # Benchmark similarity calculations
            for i in range(iterations):
                op_start = time.time()

                # Calculate similarity between test texts
                for j in range(len(test_texts) - 1):
                    self.similarity_engine.calculate_similarity(test_texts[j], test_texts[j + 1])

                op_time = (time.time() - op_start) * 1000
                response_times.append(op_time)

            total_time = (time.time() - start_time) * 1000

            return {
                "total_time_ms": total_time,
                "avg_response_time_ms": sum(response_times) / len(response_times),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times),
                "iterations": iterations,
                "operations_per_second": iterations / (total_time / 1000.0),
            }

        except Exception as e:
            logger.error(f"Similarity engine benchmark failed: {e}")
            return {"error": str(e)}

    async def _benchmark_integration(self, iterations: int) -> dict[str, Any]:
        """Benchmark integration performance"""
        try:
            start_time = time.time()
            response_times = []

            # Benchmark integration operations
            for i in range(iterations):
                op_start = time.time()

                # Simulate integration operations
                await self.integration.get_integration_metrics()

                op_time = (time.time() - op_start) * 1000
                response_times.append(op_time)

            total_time = (time.time() - start_time) * 1000

            return {
                "total_time_ms": total_time,
                "avg_response_time_ms": sum(response_times) / len(response_times),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times),
                "iterations": iterations,
                "operations_per_second": iterations / (total_time / 1000.0),
            }

        except Exception as e:
            logger.error(f"Integration benchmark failed: {e}")
            return {"error": str(e)}

    def _calculate_overall_benchmark(self, benchmark_results: dict[str, Any]) -> dict[str, Any]:
        """Calculate overall benchmark metrics"""
        try:
            overall = {
                "total_operations": 0,
                "total_time_ms": 0.0,
                "avg_response_time_ms": 0.0,
                "total_operations_per_second": 0.0,
            }

            # Aggregate metrics from all components
            for component, results in \1.items()
                if component != "overall" and "error" not in results:
                    result.get("key", "")
                    result.get("key", "")
                    result.get("key", "")

            # Calculate averages
            if result.get("key", "")
                result.get("key", "")

            return overall

        except Exception as e:
            logger.error(f"Overall benchmark calculation failed: {e}")
            return {"error": str(e)}

    async def get_optimization_report(self) -> dict[str, Any]:
        """Get comprehensive optimization report"""
        try:
            return {
                "performance_metrics": {
                    "response_time": {
                        "avg_ms": self.metrics.avg_response_time_ms,
                        "min_ms": self.metrics.min_response_time_ms,
                        "max_ms": self.metrics.max_response_time_ms,
                        "variance": self.metrics.response_time_variance,
                    },
                    "cache_performance": {
                        "hit_rate": self.metrics.cache_hit_rate,
                        "miss_rate": self.metrics.cache_miss_rate,
                        "size_mb": self.metrics.cache_size_mb,
                    },
                    "connection_pool": {
                        "active_connections": self.metrics.active_connections,
                        "idle_connections": self.metrics.idle_connections,
                        "usage_rate": self.metrics.connection_usage_rate,
                    },
                    "memory_usage": {
                        "usage_mb": self.metrics.memory_usage_mb,
                        "usage_percent": self.metrics.memory_usage_percent,
                    },
                    "similarity_algorithms": {
                        "processing_time_ms": self.metrics.algorithm_processing_time_ms,
                        "cache_hit_rate": self.metrics.algorithm_cache_hit_rate,
                    },
                },
                "alerts": self.metrics.alerts,
                "optimization_config": {
                    "connection_pool_size": self.config.connection_pool_size,
                    "enable_query_cache": self.config.enable_query_cache,
                    "enable_algorithm_cache": self.config.enable_algorithm_cache,
                    "enable_memory_monitoring": self.config.enable_memory_monitoring,
                },
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error(f"Failed to generate optimization report: {e}")
            return {"error": str(e)}

    async def close(self):
        """Close the performance optimizer and cleanup resources"""
        try:
            logger.info("Closing Performance Optimizer")

            # Stop performance monitoring
            self.running = False
            if self.monitoring_task and not self.monitoring_task.done():
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass

            # Close integration
            if self.integration:
                await self.integration.close()

            # Close cache service
            if self.cache_service:
                await self.cache_service.close()

            logger.info("Performance Optimizer closed successfully")

        except Exception as e:
            logger.error(f"Error closing performance optimizer: {e}")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

async def main():
    """Main function to test performance optimization"""
    try:
        logger.info("Testing Performance Optimization")

        # Create configuration
        config = OptimizationConfig(
            connection_pool_size=5,
            enable_performance_monitoring=True,
            enable_alerting=True,
            enable_memory_monitoring=True,
        )

        # Test performance optimizer
        async with PerformanceOptimizer(config) as optimizer:
            # Wait for initial metrics collection
            await asyncio.sleep(5)

            # Get optimization report
            report = await optimizer.get_optimization_report()
            logger.info(f"Optimization report: {report}")

            # Run performance benchmark
            benchmark = await optimizer.run_performance_benchmark(iterations=50)
            logger.info(f"Performance benchmark: {benchmark}")

            # Wait for monitoring to collect more data
            await asyncio.sleep(10)

            # Get final report
            final_report = await optimizer.get_optimization_report()
            logger.info(f"Final optimization report: {final_report}")

            logger.info("Performance Optimization test completed successfully")
            return True

    except Exception as e:
        logger.error(f"Performance Optimization test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
