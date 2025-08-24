"""
LTST Performance Optimizer

This module provides performance optimization and benchmarking capabilities
for the LTST Memory System, including database query optimization, caching
strategies, and performance monitoring.
"""

import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .context_merger import ContextMerger
from .conversation_storage import ConversationStorage
from .database_resilience import DatabaseResilienceManager as DatabaseManager
from .logger import setup_logger
from .ltst_memory_integration import LTSTMemoryIntegration
from .session_manager import SessionManager

logger = setup_logger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for LTST operations."""

    operation_type: str
    execution_time_ms: float
    result_count: int
    cache_hit: bool = False
    database_queries: int = 0
    memory_usage_mb: float = 0.0
    error_count: int = 0
    timestamp: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PerformanceBenchmark:
    """Performance benchmark results."""

    benchmark_name: str
    total_operations: int
    total_time_ms: float
    average_time_ms: float
    min_time_ms: float
    max_time_ms: float
    success_rate: float
    cache_hit_rate: float
    database_query_count: int
    memory_usage_mb: float
    timestamp: datetime = None
    details: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.details is None:
            self.details = {}


class LTSTPerformanceOptimizer:
    """Handles performance optimization for the LTST Memory System."""

    def __init__(
        self,
        conversation_storage: Optional[ConversationStorage] = None,
        context_merger: Optional[ContextMerger] = None,
        session_manager: Optional[SessionManager] = None,
    ):
        """Initialize performance optimizer."""
        self.conversation_storage = conversation_storage or ConversationStorage()
        self.context_merger = context_merger or ContextMerger(self.conversation_storage)
        self.session_manager = session_manager or SessionManager(self.conversation_storage, self.context_merger)
        self.ltst_integration = LTSTMemoryIntegration(
            self.conversation_storage, self.context_merger, self.session_manager
        )
        self.db_manager = DatabaseManager()

        # Performance tracking
        self.performance_metrics: List[PerformanceMetrics] = []
        self.benchmarks: Dict[str, PerformanceBenchmark] = {}
        self.cache_stats = {"hits": 0, "misses": 0}

    def optimize_database_queries(self) -> Dict[str, Any]:
        """Optimize database queries for better performance."""
        try:
            optimization_results = {}

            # Analyze and optimize conversation storage queries
            storage_optimizations = self._optimize_storage_queries()
            optimization_results["storage"] = storage_optimizations

            # Analyze and optimize context merger queries
            merger_optimizations = self._optimize_merger_queries()
            optimization_results["merger"] = merger_optimizations

            # Analyze and optimize session manager queries
            session_optimizations = self._optimize_session_queries()
            optimization_results["session"] = session_optimizations

            # Update database statistics
            self._update_database_statistics()

            logger.info("Database query optimization completed")
            return optimization_results

        except Exception as e:
            logger.error(f"Failed to optimize database queries: {e}")
            return {"error": str(e)}

    def _optimize_storage_queries(self) -> Dict[str, Any]:
        """Optimize conversation storage queries."""
        try:
            optimizations = {}

            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Check index usage
                    cursor.execute(
                        """
                        SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
                        FROM pg_stat_user_indexes
                        WHERE tablename IN ('conversation_sessions', 'conversation_messages', 'user_preferences')
                        ORDER BY idx_scan DESC
                    """
                    )

                    index_stats = []
                    for row in cursor.fetchall():
                        index_stats.append(
                            {
                                "table": row[1],
                                "index": row[2],
                                "scans": row[3],
                                "tuples_read": row[4],
                                "tuples_fetched": row[5],
                            }
                        )

                    optimizations["index_usage"] = index_stats

                    # Check table statistics
                    cursor.execute(
                        """
                        SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del, n_live_tup, n_dead_tup
                        FROM pg_stat_user_tables
                        WHERE tablename IN ('conversation_sessions', 'conversation_messages', 'user_preferences')
                    """
                    )

                    table_stats = []
                    for row in cursor.fetchall():
                        table_stats.append(
                            {
                                "table": row[1],
                                "inserts": row[2],
                                "updates": row[3],
                                "deletes": row[4],
                                "live_tuples": row[5],
                                "dead_tuples": row[6],
                            }
                        )

                    optimizations["table_stats"] = table_stats

                    # Check for missing indexes
                    missing_indexes = self._identify_missing_indexes(cursor)
                    optimizations["missing_indexes"] = missing_indexes

            return optimizations

        except Exception as e:
            logger.error(f"Failed to optimize storage queries: {e}")
            return {"error": str(e)}

    def _optimize_merger_queries(self) -> Dict[str, Any]:
        """Optimize context merger queries."""
        try:
            optimizations = {}

            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Check context query performance
                    cursor.execute(
                        """
                        SELECT query, calls, total_time, mean_time, rows
                        FROM pg_stat_statements
                        WHERE query LIKE '%conversation_context%'
                        ORDER BY total_time DESC
                        LIMIT 10
                    """
                    )

                    context_queries = []
                    for row in cursor.fetchall():
                        context_queries.append(
                            {
                                "query": row[0][:100] + "..." if len(row[0]) > 100 else row[0],
                                "calls": row[1],
                                "total_time": row[2],
                                "mean_time": row[3],
                                "rows": row[4],
                            }
                        )

                    optimizations["context_queries"] = context_queries

            return optimizations

        except Exception as e:
            logger.error(f"Failed to optimize merger queries: {e}")
            return {"error": str(e)}

    def _optimize_session_queries(self) -> Dict[str, Any]:
        """Optimize session manager queries."""
        try:
            optimizations = {}

            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Check session query performance
                    cursor.execute(
                        """
                        SELECT query, calls, total_time, mean_time, rows
                        FROM pg_stat_statements
                        WHERE query LIKE '%conversation_sessions%'
                        ORDER BY total_time DESC
                        LIMIT 10
                    """
                    )

                    session_queries = []
                    for row in cursor.fetchall():
                        session_queries.append(
                            {
                                "query": row[0][:100] + "..." if len(row[0]) > 100 else row[0],
                                "calls": row[1],
                                "total_time": row[2],
                                "mean_time": row[3],
                                "rows": row[4],
                            }
                        )

                    optimizations["session_queries"] = session_queries

            return optimizations

        except Exception as e:
            logger.error(f"Failed to optimize session queries: {e}")
            return {"error": str(e)}

    def _identify_missing_indexes(self, cursor) -> List[Dict[str, Any]]:
        """Identify potentially missing indexes."""
        try:
            missing_indexes = []

            # Check for slow queries that might benefit from indexes
            cursor.execute(
                """
                SELECT query, calls, total_time, mean_time
                FROM pg_stat_statements
                WHERE mean_time > 10  -- Queries taking more than 10ms on average
                AND query LIKE '%conversation_%'
                ORDER BY total_time DESC
                LIMIT 5
            """
            )

            for row in cursor.fetchall():
                missing_indexes.append(
                    {
                        "query": row[0][:100] + "..." if len(row[0]) > 100 else row[0],
                        "calls": row[1],
                        "total_time": row[2],
                        "mean_time": row[3],
                        "suggestion": "Consider adding index based on WHERE clause",
                    }
                )

            return missing_indexes

        except Exception as e:
            logger.error(f"Failed to identify missing indexes: {e}")
            return []

    def _update_database_statistics(self) -> None:
        """Update database statistics for better query planning."""
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Update statistics for LTST tables
                    tables = [
                        "conversation_sessions",
                        "conversation_messages",
                        "conversation_context",
                        "user_preferences",
                        "memory_retrieval_cache",
                        "session_relationships",
                    ]

                    for table in tables:
                        cursor.execute(f"ANALYZE {table}")

                    conn.commit()
                    logger.info("Database statistics updated")

        except Exception as e:
            logger.error(f"Failed to update database statistics: {e}")

    def implement_caching_strategies(self) -> Dict[str, Any]:
        """Implement caching strategies for context retrieval."""
        try:
            caching_results = {}

            # Optimize context merger cache
            merger_cache_optimization = self._optimize_merger_cache()
            caching_results["merger_cache"] = merger_cache_optimization

            # Optimize session manager cache
            session_cache_optimization = self._optimize_session_cache()
            caching_results["session_cache"] = session_cache_optimization

            # Optimize conversation storage cache
            storage_cache_optimization = self._optimize_storage_cache()
            caching_results["storage_cache"] = storage_cache_optimization

            logger.info("Caching strategies implemented")
            return caching_results

        except Exception as e:
            logger.error(f"Failed to implement caching strategies: {e}")
            return {"error": str(e)}

    def _optimize_merger_cache(self) -> Dict[str, Any]:
        """Optimize context merger cache."""
        try:
            # Clean up expired cache entries
            self.context_merger.cleanup_cache()

            # Adjust cache TTL based on usage patterns
            cache_size = len(self.context_merger.cache)
            cache_ttl = self.context_merger.cache_ttl

            optimization = {
                "cache_size": cache_size,
                "cache_ttl_minutes": cache_ttl.total_seconds() / 60,
                "optimization_applied": True,
            }

            # Adjust TTL based on cache size
            if cache_size > 1000:
                # Reduce TTL for large caches
                self.context_merger.cache_ttl = timedelta(minutes=15)
                optimization["ttl_adjusted"] = True
                optimization["new_ttl_minutes"] = 15

            return optimization

        except Exception as e:
            logger.error(f"Failed to optimize merger cache: {e}")
            return {"error": str(e)}

    def _optimize_session_cache(self) -> Dict[str, Any]:
        """Optimize session manager cache."""
        try:
            # Clean up expired sessions
            cleaned_count = self.session_manager.cleanup_expired_sessions()

            # Get cache statistics
            active_sessions = self.session_manager.get_active_sessions_count()

            optimization = {
                "active_sessions": active_sessions,
                "cleaned_sessions": cleaned_count,
                "optimization_applied": True,
            }

            return optimization

        except Exception as e:
            logger.error(f"Failed to optimize session cache: {e}")
            return {"error": str(e)}

    def _optimize_storage_cache(self) -> Dict[str, Any]:
        """Optimize conversation storage cache."""
        try:
            # Clean up expired data
            self.conversation_storage.cleanup_expired_data()

            optimization = {"cleanup_applied": True, "optimization_applied": True}

            return optimization

        except Exception as e:
            logger.error(f"Failed to optimize storage cache: {e}")
            return {"error": str(e)}

    def benchmark_memory_rehydration(self, test_queries: List[str], user_id: str = "test_user") -> PerformanceBenchmark:
        """Benchmark memory rehydration performance."""
        try:
            start_time = time.time()
            total_operations = len(test_queries)
            execution_times = []
            success_count = 0
            cache_hits = 0
            database_queries = 0

            for query in test_queries:
                try:
                    operation_start = time.time()

                    # Perform memory rehydration
                    bundle = self.ltst_integration.rehydrate_with_conversation_context(
                        query=query,
                        user_id=user_id,
                        include_conversation_history=True,
                        include_user_preferences=True,
                        include_session_context=True,
                    )

                    operation_time = (time.time() - operation_start) * 1000  # Convert to ms
                    execution_times.append(operation_time)

                    # Track cache hits (simplified)
                    if bundle.metadata.get("cache_hit", False):
                        cache_hits += 1

                    success_count += 1

                except Exception as e:
                    logger.error(f"Benchmark operation failed for query '{query}': {e}")
                    execution_times.append(0)

            total_time = (time.time() - start_time) * 1000  # Convert to ms

            # Calculate statistics
            if execution_times:
                avg_time = sum(execution_times) / len(execution_times)
                min_time = min(execution_times)
                max_time = max(execution_times)
            else:
                avg_time = min_time = max_time = 0

            success_rate = success_count / total_operations if total_operations > 0 else 0
            cache_hit_rate = cache_hits / success_count if success_count > 0 else 0

            benchmark = PerformanceBenchmark(
                benchmark_name="memory_rehydration",
                total_operations=total_operations,
                total_time_ms=total_time,
                average_time_ms=avg_time,
                min_time_ms=min_time,
                max_time_ms=max_time,
                success_rate=success_rate,
                cache_hit_rate=cache_hit_rate,
                database_query_count=database_queries,
                memory_usage_mb=0.0,  # Would need psutil for accurate measurement
                details={"test_queries": test_queries, "user_id": user_id},
            )

            self.benchmarks["memory_rehydration"] = benchmark
            logger.info(f"Memory rehydration benchmark completed: {avg_time:.2f}ms average")

            return benchmark

        except Exception as e:
            logger.error(f"Failed to benchmark memory rehydration: {e}")
            return PerformanceBenchmark(
                benchmark_name="memory_rehydration",
                total_operations=0,
                total_time_ms=0,
                average_time_ms=0,
                min_time_ms=0,
                max_time_ms=0,
                success_rate=0,
                cache_hit_rate=0,
                database_query_count=0,
                memory_usage_mb=0.0,
                details={"error": str(e)},
            )

    def benchmark_conversation_retrieval(self, session_id: str, message_count: int = 100) -> PerformanceBenchmark:
        """Benchmark conversation retrieval performance."""
        try:
            start_time = time.time()
            execution_times = []
            success_count = 0

            # Generate test messages
            for i in range(message_count):
                try:
                    operation_start = time.time()

                    # Retrieve messages
                    _ = self.conversation_storage.get_messages(session_id, limit=10, offset=i * 10)

                    operation_time = (time.time() - operation_start) * 1000
                    execution_times.append(operation_time)
                    success_count += 1

                except Exception as e:
                    logger.error(f"Benchmark operation failed for message {i}: {e}")
                    execution_times.append(0)

            total_time = (time.time() - start_time) * 1000

            # Calculate statistics
            if execution_times:
                avg_time = sum(execution_times) / len(execution_times)
                min_time = min(execution_times)
                max_time = max(execution_times)
            else:
                avg_time = min_time = max_time = 0

            success_rate = success_count / message_count if message_count > 0 else 0

            benchmark = PerformanceBenchmark(
                benchmark_name="conversation_retrieval",
                total_operations=message_count,
                total_time_ms=total_time,
                average_time_ms=avg_time,
                min_time_ms=min_time,
                max_time_ms=max_time,
                success_rate=success_rate,
                cache_hit_rate=0.0,  # Not applicable for this benchmark
                database_query_count=message_count,
                memory_usage_mb=0.0,
                details={"session_id": session_id, "message_count": message_count},
            )

            self.benchmarks["conversation_retrieval"] = benchmark
            logger.info(f"Conversation retrieval benchmark completed: {avg_time:.2f}ms average")

            return benchmark

        except Exception as e:
            logger.error(f"Failed to benchmark conversation retrieval: {e}")
            return PerformanceBenchmark(
                benchmark_name="conversation_retrieval",
                total_operations=0,
                total_time_ms=0,
                average_time_ms=0,
                min_time_ms=0,
                max_time_ms=0,
                success_rate=0,
                cache_hit_rate=0,
                database_query_count=0,
                memory_usage_mb=0.0,
                details={"error": str(e)},
            )

    def benchmark_context_merging(
        self, session_id: str, user_id: str, test_messages: List[str]
    ) -> PerformanceBenchmark:
        """Benchmark context merging performance."""
        try:
            start_time = time.time()
            total_operations = len(test_messages)
            execution_times = []
            success_count = 0

            for message in test_messages:
                try:
                    operation_start = time.time()

                    # Perform context merging
                    request = self.context_merger.ContextMergeRequest(
                        session_id=session_id, user_id=user_id, current_message=message
                    )

                    _ = self.context_merger.merge_context(request)

                    operation_time = (time.time() - operation_start) * 1000
                    execution_times.append(operation_time)
                    success_count += 1

                except Exception as e:
                    logger.error(f"Benchmark operation failed for message '{message}': {e}")
                    execution_times.append(0)

            total_time = (time.time() - start_time) * 1000

            # Calculate statistics
            if execution_times:
                avg_time = sum(execution_times) / len(execution_times)
                min_time = min(execution_times)
                max_time = max(execution_times)
            else:
                avg_time = min_time = max_time = 0

            success_rate = success_count / total_operations if total_operations > 0 else 0

            benchmark = PerformanceBenchmark(
                benchmark_name="context_merging",
                total_operations=total_operations,
                total_time_ms=total_time,
                average_time_ms=avg_time,
                min_time_ms=min_time,
                max_time_ms=max_time,
                success_rate=success_rate,
                cache_hit_rate=0.0,  # Would need to track cache hits
                database_query_count=total_operations,
                memory_usage_mb=0.0,
                details={"session_id": session_id, "user_id": user_id, "test_messages": test_messages},
            )

            self.benchmarks["context_merging"] = benchmark
            logger.info(f"Context merging benchmark completed: {avg_time:.2f}ms average")

            return benchmark

        except Exception as e:
            logger.error(f"Failed to benchmark context merging: {e}")
            return PerformanceBenchmark(
                benchmark_name="context_merging",
                total_operations=0,
                total_time_ms=0,
                average_time_ms=0,
                min_time_ms=0,
                max_time_ms=0,
                success_rate=0,
                cache_hit_rate=0,
                database_query_count=0,
                memory_usage_mb=0.0,
                details={"error": str(e)},
            )

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "benchmarks": {},
                "optimizations": {},
                "cache_stats": self.cache_stats,
                "system_health": self._get_system_health(),
            }

            # Add benchmark results
            for name, benchmark in self.benchmarks.items():
                report["benchmarks"][name] = asdict(benchmark)

            # Add optimization results
            optimization_results = self.optimize_database_queries()
            report["optimizations"]["database"] = optimization_results

            caching_results = self.implement_caching_strategies()
            report["optimizations"]["caching"] = caching_results

            return report

        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def _get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics."""
        try:
            health_metrics = {
                "active_sessions": self.session_manager.get_active_sessions_count(),
                "session_health": self.session_manager.get_session_health(),
                "integration_health": self.ltst_integration.get_integration_health(),
            }

            return health_metrics

        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {"error": str(e)}

    def track_performance_metric(
        self,
        operation_type: str,
        execution_time_ms: float,
        result_count: int,
        cache_hit: bool = False,
        database_queries: int = 0,
        error_count: int = 0,
    ) -> None:
        """Track a performance metric."""
        try:
            metric = PerformanceMetrics(
                operation_type=operation_type,
                execution_time_ms=execution_time_ms,
                result_count=result_count,
                cache_hit=cache_hit,
                database_queries=database_queries,
                error_count=error_count,
            )

            self.performance_metrics.append(metric)

            # Update cache stats
            if cache_hit:
                self.cache_stats["hits"] += 1
            else:
                self.cache_stats["misses"] += 1

        except Exception as e:
            logger.error(f"Failed to track performance metric: {e}")

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        try:
            if not self.performance_metrics:
                return {"message": "No performance metrics available"}

            # Group by operation type
            operation_stats = {}
            for metric in self.performance_metrics:
                op_type = metric.operation_type
                if op_type not in operation_stats:
                    operation_stats[op_type] = {
                        "count": 0,
                        "total_time": 0,
                        "total_results": 0,
                        "cache_hits": 0,
                        "errors": 0,
                    }

                stats = operation_stats[op_type]
                stats["count"] += 1
                stats["total_time"] += metric.execution_time_ms
                stats["total_results"] += metric.result_count
                if metric.cache_hit:
                    stats["cache_hits"] += 1
                stats["errors"] += metric.error_count

            # Calculate averages
            for op_type, stats in operation_stats.items():
                if stats["count"] > 0:
                    stats["avg_time"] = stats["total_time"] / stats["count"]
                    stats["avg_results"] = stats["total_results"] / stats["count"]
                    stats["cache_hit_rate"] = stats["cache_hits"] / stats["count"]
                    stats["error_rate"] = stats["errors"] / stats["count"]

            summary = {
                "total_metrics": len(self.performance_metrics),
                "operation_stats": operation_stats,
                "cache_stats": self.cache_stats,
                "timestamp": datetime.now().isoformat(),
            }

            return summary

        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {"error": str(e)}
