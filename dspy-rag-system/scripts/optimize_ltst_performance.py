#!/usr/bin/env python3
# type: ignore
"""
LTST Memory System Performance Optimization Script

This script optimizes database queries, implements caching strategies,
and benchmarks performance for the LTST Memory System.

Note: Type ignore is used because RealDictCursor returns dictionary-like objects
that the type checker doesn't properly recognize, and database connection objects
are properly handled with null checks at runtime.
"""

import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.context_merger import ContextMerger
from utils.conversation_storage import ConversationMessage, ConversationStorage
from utils.memory_rehydrator import MemoryRehydrator, RehydrationRequest
from utils.session_manager import SessionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LTSTPerformanceOptimizer:
    """Optimizes LTST Memory System performance."""

    def __init__(self):
        """Initialize the performance optimizer."""
        self.storage = ConversationStorage()
        self.session_manager = SessionManager(self.storage)
        self.context_merger = ContextMerger(self.storage)
        self.rehydrator = MemoryRehydrator(self.storage)

        self.benchmark_results = {}
        self.optimization_suggestions = []

    def optimize_database_queries(self) -> Dict[str, Any]:
        """Optimize database queries for better performance."""
        logger.info("🔧 Optimizing database queries...")

        optimizations = {"indexes_created": [], "query_optimizations": [], "performance_improvements": {}}

        try:
            # Connect to database
            if not self.storage.connect():
                logger.error("Failed to connect to database")
                return optimizations

            # Create performance indexes
            indexes = [
                (
                    "conversation_messages",
                    "session_id_idx",
                    "CREATE INDEX IF NOT EXISTS session_id_idx ON conversation_messages(session_id)",
                ),
                (
                    "conversation_messages",
                    "timestamp_idx",
                    "CREATE INDEX IF NOT EXISTS timestamp_idx ON conversation_messages(timestamp DESC)",
                ),
                (
                    "conversation_messages",
                    "role_idx",
                    "CREATE INDEX IF NOT EXISTS role_idx ON conversation_messages(role)",
                ),
                (
                    "conversation_sessions",
                    "user_id_idx",
                    "CREATE INDEX IF NOT EXISTS user_id_idx ON conversation_sessions(user_id)",
                ),
                (
                    "conversation_sessions",
                    "status_idx",
                    "CREATE INDEX IF NOT EXISTS status_idx ON conversation_sessions(status)",
                ),
                (
                    "conversation_context",
                    "session_type_idx",
                    "CREATE INDEX IF NOT EXISTS session_type_idx ON conversation_context(session_id, context_type)",
                ),
                (
                    "user_preferences",
                    "user_pref_idx",
                    "CREATE INDEX IF NOT EXISTS user_pref_idx ON user_preferences(user_id, preference_type)",
                ),
            ]

            for table, index_name, sql in indexes:
                try:
                    self.storage.cursor.execute(sql)
                    optimizations["indexes_created"].append(index_name)
                    logger.info(f"✅ Created index: {index_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to create index {index_name}: {e}")

            # Optimize query patterns
            query_optimizations = [
                "Use LIMIT clauses for all retrieval queries",
                "Implement connection pooling for high concurrency",
                "Add query result caching with TTL",
                "Use prepared statements for repeated queries",
                "Optimize vector similarity searches with proper indexing",
            ]

            optimizations["query_optimizations"] = query_optimizations

            # Analyze table statistics
            self.storage.cursor.execute("ANALYZE conversation_messages")
            self.storage.cursor.execute("ANALYZE conversation_sessions")
            self.storage.cursor.execute("ANALYZE conversation_context")
            self.storage.cursor.execute("ANALYZE user_preferences")

            logger.info("✅ Database query optimization completed")

        except Exception as e:
            logger.error(f"❌ Database optimization failed: {e}")

        finally:
            self.storage.disconnect()

        return optimizations

    def implement_caching_strategies(self) -> Dict[str, Any]:
        """Implement caching strategies for context retrieval."""
        logger.info("💾 Implementing caching strategies...")

        caching_config = {
            "session_cache_ttl": 3600,  # 1 hour
            "context_cache_ttl": 1800,  # 30 minutes
            "preference_cache_ttl": 7200,  # 2 hours
            "rehydration_cache_ttl": 900,  # 15 minutes
            "cache_size_limits": {"sessions": 1000, "contexts": 5000, "preferences": 2000, "rehydration": 500},
        }

        # Update cache configurations
        self.session_manager.session_cache_ttl = timedelta(seconds=caching_config["session_cache_ttl"])
        self.rehydrator.cache_ttl = timedelta(seconds=caching_config["rehydration_cache_ttl"])

        logger.info("✅ Caching strategies implemented")
        return caching_config

    def benchmark_memory_rehydration(self) -> Dict[str, Any]:
        """Benchmark memory rehydration performance."""
        logger.info("⚡ Benchmarking memory rehydration performance...")

        benchmarks = {"rehydration_times": [], "cache_performance": {}, "concurrent_requests": {}, "memory_usage": {}}

        try:
            if not self.storage.connect():
                logger.error("Failed to connect to database")
                return benchmarks

            # Create test session
            session_id = self.session_manager.create_session(
                user_id="benchmark_user", session_name="Performance Benchmark", session_type="benchmark"
            )

            # Add test messages
            for i in range(20):
                message = f"Test message {i} for performance benchmarking"
                self.storage.store_message(ConversationMessage(session_id, "human", message))

            # Benchmark rehydration times
            test_requests = [
                RehydrationRequest(session_id, "benchmark_user", "test query 1"),
                RehydrationRequest(session_id, "benchmark_user", "test query 2"),
                RehydrationRequest(session_id, "benchmark_user", "test query 3"),
            ]

            for i, request in enumerate(test_requests):
                start_time = time.time()
                result = self.rehydrator.rehydrate_memory(request)
                end_time = time.time()

                rehydration_time = (end_time - start_time) * 1000  # Convert to ms
                benchmarks["rehydration_times"].append(
                    {"request": i + 1, "time_ms": rehydration_time, "cache_hit": result.cache_hit if result else False}
                )

                logger.info(f"Rehydration {i+1}: {rehydration_time:.2f}ms")

            # Test cache performance
            cache_request = RehydrationRequest(session_id, "benchmark_user", "cached query")
            start_time = time.time()
            cached_result = self.rehydrator.rehydrate_memory(cache_request)
            cache_time = (time.time() - start_time) * 1000

            benchmarks["cache_performance"] = {
                "cache_hit_time_ms": cache_time,
                "cache_hit": cached_result.cache_hit if cached_result else False,
            }

            # Cleanup
            self.session_manager.close_session(session_id, "benchmark_completed")

            logger.info("✅ Memory rehydration benchmarking completed")

        except Exception as e:
            logger.error(f"❌ Benchmarking failed: {e}")

        finally:
            self.storage.disconnect()

        return benchmarks

    def benchmark_conversation_retrieval(self) -> Dict[str, Any]:
        """Benchmark conversation retrieval performance."""
        logger.info("💬 Benchmarking conversation retrieval performance...")

        benchmarks = {"retrieval_times": [], "message_counts": [], "query_complexity": {}}

        try:
            if not self.storage.connect():
                logger.error("Failed to connect to database")
                return benchmarks

            # Create test session with many messages
            session_id = self.session_manager.create_session(
                user_id="retrieval_benchmark_user", session_name="Retrieval Benchmark", session_type="benchmark"
            )

            # Add varying numbers of messages
            message_counts = [10, 50, 100, 200]

            for count in message_counts:
                # Add messages
                for i in range(count):
                    message = f"Retrieval test message {i} for count {count}"
                    self.storage.store_message(ConversationMessage(session_id, "human", message))

                # Benchmark retrieval
                start_time = time.time()
                messages = self.storage.retrieve_session_messages(session_id, limit=count)
                end_time = time.time()

                retrieval_time = (end_time - start_time) * 1000
                benchmarks["retrieval_times"].append(
                    {"message_count": count, "time_ms": retrieval_time, "actual_retrieved": len(messages)}
                )

                logger.info(f"Retrieved {count} messages: {retrieval_time:.2f}ms")

            # Cleanup
            self.session_manager.close_session(session_id, "retrieval_benchmark_completed")

            logger.info("✅ Conversation retrieval benchmarking completed")

        except Exception as e:
            logger.error(f"❌ Retrieval benchmarking failed: {e}")

        finally:
            self.storage.disconnect()

        return benchmarks

    def benchmark_context_merging(self) -> Dict[str, Any]:
        """Benchmark context merging performance."""
        logger.info("🔗 Benchmarking context merging performance...")

        benchmarks = {"merging_times": [], "context_counts": [], "similarity_calculations": {}}

        try:
            if not self.storage.connect():
                logger.error("Failed to connect to database")
                return benchmarks

            # Create test session
            session_id = self.session_manager.create_session(
                user_id="merging_benchmark_user", session_name="Merging Benchmark", session_type="benchmark"
            )

            # Add test contexts
            context_types = ["conversation", "preference", "project"]
            context_counts = [5, 10, 20, 50]

            for count in context_counts:
                for context_type in context_types:
                    for i in range(count):
                        context_key = f"test_context_{context_type}_{i}"
                        context_value = f"Test context value for {context_type} context {i}"

                        self.storage.store_context(
                            session_id=session_id,
                            context_type=context_type,
                            context_key=context_key,
                            context_value=context_value,
                            relevance_score=0.8,
                        )

                # Benchmark merging
                start_time = time.time()
                merge_result = self.context_merger.merge_contexts(
                    session_id, context_type="conversation", relevance_threshold=0.5
                )
                end_time = time.time()

                merging_time = (end_time - start_time) * 1000
                benchmarks["merging_times"].append(
                    {
                        "context_count": count * len(context_types),
                        "time_ms": merging_time,
                        "merged_contexts": len(merge_result.merged_contexts) if merge_result else 0,
                    }
                )

                logger.info(f"Merged {count * len(context_types)} contexts: {merging_time:.2f}ms")

            # Cleanup
            self.session_manager.close_session(session_id, "merging_benchmark_completed")

            logger.info("✅ Context merging benchmarking completed")

        except Exception as e:
            logger.error(f"❌ Merging benchmarking failed: {e}")

        finally:
            self.storage.disconnect()

        return benchmarks

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        logger.info("📊 Generating performance report...")

        # Run all benchmarks
        db_optimizations = self.optimize_database_queries()
        caching_config = self.implement_caching_strategies()
        rehydration_benchmarks = self.benchmark_memory_rehydration()
        retrieval_benchmarks = self.benchmark_conversation_retrieval()
        merging_benchmarks = self.benchmark_context_merging()

        # Calculate performance metrics
        avg_rehydration_time = (
            sum(b["time_ms"] for b in rehydration_benchmarks["rehydration_times"])
            / len(rehydration_benchmarks["rehydration_times"])
            if rehydration_benchmarks["rehydration_times"]
            else 0
        )
        avg_retrieval_time = (
            sum(b["time_ms"] for b in retrieval_benchmarks["retrieval_times"])
            / len(retrieval_benchmarks["retrieval_times"])
            if retrieval_benchmarks["retrieval_times"]
            else 0
        )
        avg_merging_time = (
            sum(b["time_ms"] for b in merging_benchmarks["merging_times"]) / len(merging_benchmarks["merging_times"])
            if merging_benchmarks["merging_times"]
            else 0
        )

        # Performance targets
        targets = {
            "rehydration_time_ms": 5000,  # 5 seconds
            "retrieval_time_ms": 2000,  # 2 seconds
            "merging_time_ms": 1000,  # 1 second
        }

        # Performance status
        performance_status = {
            "rehydration": {
                "target": targets["rehydration_time_ms"],
                "actual": avg_rehydration_time,
                "status": "✅ PASS" if avg_rehydration_time < targets["rehydration_time_ms"] else "❌ FAIL",
            },
            "retrieval": {
                "target": targets["retrieval_time_ms"],
                "actual": avg_retrieval_time,
                "status": "✅ PASS" if avg_retrieval_time < targets["retrieval_time_ms"] else "❌ FAIL",
            },
            "merging": {
                "target": targets["merging_time_ms"],
                "actual": avg_merging_time,
                "status": "✅ PASS" if avg_merging_time < targets["merging_time_ms"] else "❌ FAIL",
            },
        }

        report = {
            "timestamp": datetime.now().isoformat(),
            "performance_status": performance_status,
            "optimizations": {"database": db_optimizations, "caching": caching_config},
            "benchmarks": {
                "rehydration": rehydration_benchmarks,
                "retrieval": retrieval_benchmarks,
                "merging": merging_benchmarks,
            },
            "recommendations": self._generate_recommendations(performance_status),
        }

        logger.info("✅ Performance report generated")
        return report

    def _generate_recommendations(self, performance_status: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []

        for operation, status in performance_status.items():
            if status["status"] == "❌ FAIL":
                recommendations.append(
                    f"Optimize {operation} performance: {status['actual']:.2f}ms > {status['target']}ms target"
                )

        if not recommendations:
            recommendations.append("All performance targets met! System is performing well.")

        recommendations.extend(
            [
                "Consider implementing connection pooling for high concurrency",
                "Monitor cache hit rates and adjust TTL values as needed",
                "Use database query analysis tools for further optimization",
                "Consider implementing read replicas for heavy read workloads",
            ]
        )

        return recommendations


def main():
    """Main function to run performance optimization."""
    optimizer = LTSTPerformanceOptimizer()

    logger.info("🚀 Starting LTST Memory System Performance Optimization")

    try:
        # Generate comprehensive performance report
        report = optimizer.generate_performance_report()

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 LTST PERFORMANCE REPORT SUMMARY")
        logger.info("=" * 60)

        for operation, status in report["performance_status"].items():
            logger.info(f"{operation.upper()}: {status['status']}")
            logger.info(f"  Target: {status['target']}ms, Actual: {status['actual']:.2f}ms")

        logger.info("\n🔧 OPTIMIZATIONS APPLIED:")
        logger.info(f"  Database indexes: {len(report['optimizations']['database']['indexes_created'])}")
        logger.info(f"  Caching strategies: {len(report['optimizations']['caching'])}")

        logger.info("\n💡 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            logger.info(f"  • {rec}")

        logger.info("\n✅ Performance optimization completed!")

        return report

    except Exception as e:
        logger.error(f"❌ Performance optimization failed: {e}")
        return None


if __name__ == "__main__":
    main()
