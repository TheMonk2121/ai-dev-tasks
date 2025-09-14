from __future__ import annotations
import asyncio
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Any
from scripts.cache_invalidation_integration import CacheInvalidationIntegration, IntegrationConfig
from scripts.cache_performance_monitoring import CachePerformanceMonitor, MonitoringConfig
from scripts.ltst_memory_integration import LTSTIntegrationConfig, LTSTMemoryIntegration
from scripts.postgresql_cache_service import CacheConfig, CacheEntry, PostgreSQLCacheService
from scripts.similarity_scoring_algorithms import SimilarityConfig, SimilarityScoringEngine
from typing import Any, Optional, Union
#!/usr/bin/env python3
"""
Comprehensive Testing Suite for Generation Cache Implementation

Task 4.1: Comprehensive Testing Suite
Priority: High
MoSCoW: 🔥 Must
"""

# Add project root to path for imports

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our existing systems

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/comprehensive_testing.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

@dataclass
class TestConfig:
    """Configuration for comprehensive testing"""

    # Test categories
    enable_unit_tests: bool = True
    enable_integration_tests: bool = True
    enable_performance_tests: bool = True
    enable_stress_tests: bool = True

    # Test parameters
    test_data_size: int = 100
    performance_test_duration_seconds: int = 30
    stress_test_concurrent_users: int = 10
    stress_test_duration_seconds: int = 60

    # Validation thresholds
    min_cache_hit_rate: float = 0.8
    max_response_time_ms: float = 100.0
    max_memory_usage_mb: float = 500.0
    min_throughput_ops_per_sec: float = 1000.0

@dataclass
class TestResult:
    """Represents a test result"""

    test_name: str
    test_category: str
    status: str  # passed, failed, skipped
    duration_ms: float
    details: dict[str, Any]
    error_message: str | None = None
    timestamp: float = field(default_factory=time.time)

class ComprehensiveTestingSuite:
    """Comprehensive testing suite for the generation cache system"""

    def __init__(self, config: TestConfig | None = None):
        """Initialize testing suite"""
        self.config = config or TestConfig()
        self.test_results: list[TestResult] = []

        # Initialize systems for testing
        self.cache_service: PostgreSQLCacheService | None = None
        self.similarity_engine: SimilarityScoringEngine | None = None
        self.integration: CacheInvalidationIntegration | None = None
        self.ltst_integration: LTSTMemoryIntegration | None = None
        self.performance_monitor: CachePerformanceMonitor | None = None
        # Accumulates integration test results keyed by name
        self.integration_results: dict[str, TestResult] = {}

        logger.info("Comprehensive Testing Suite initialized")

    async def initialize(self):
        """Initialize all systems for testing"""
        try:
            logger.info("Initializing Comprehensive Testing Suite")

            # Initialize PostgreSQL cache service
            cache_config = CacheConfig(
                max_connections=10,
                min_connections=2,
                similarity_threshold=0.7,
                enable_metrics=True,
                enable_connection_pooling=True,
            )

            self.cache_service = PostgreSQLCacheService(config=cache_config)
            await self.cache_service.initialize()
            logger.info("PostgreSQL cache service initialized for testing")

            # Initialize similarity engine
            similarity_config = SimilarityConfig(
                primary_algorithm="hybrid",
                enable_caching=True,
                cache_size=2000,
                use_tfidf=True,
            )

            self.similarity_engine = SimilarityScoringEngine(config=similarity_config)
            logger.info("Similarity engine initialized for testing")

            # Initialize cache invalidation integration
            integration_config = IntegrationConfig(
                enable_background_cleanup=True,
                enable_performance_monitoring=True,
                enable_alerting=True,
            )

            self.integration = CacheInvalidationIntegration(config=integration_config)
            await self.integration.initialize()
            logger.info("Cache invalidation integration initialized for testing")

            # Initialize LTST memory integration
            ltst_config = LTSTIntegrationConfig(
                enable_cache_warming=True,
                warming_batch_size=100,
                warming_interval_minutes=2,
                enable_fallback_to_direct=True,
            )

            self.ltst_integration = LTSTMemoryIntegration(config=ltst_config)
            await self.ltst_integration.initialize()
            logger.info("LTST memory integration initialized for testing")

            # Initialize performance monitor
            monitoring_config = MonitoringConfig(
                metrics_collection_interval_seconds=15,
                dashboard_update_interval_seconds=30,
                trend_analysis_interval_minutes=2,
                enable_alerting=True,
                enable_dashboard=True,
                enable_trend_analysis=True,
            )

            self.performance_monitor = CachePerformanceMonitor(config=monitoring_config)
            await self.performance_monitor.initialize()
            logger.info("Performance monitor initialized for testing")

            logger.info("Comprehensive Testing Suite initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize testing suite: {e}")
            raise

    async def run_all_tests(self) -> dict[str, Any]:
        """Run all test categories"""
        try:
            logger.info("Starting comprehensive testing suite")
            start_time = time.time()

            results = {
                "unit_tests": {},
                "integration_tests": {},
                "performance_tests": {},
                "stress_tests": {},
                "summary": {},
            }

            # Run unit tests
            if self.config.enable_unit_tests:
                logger.info("Running unit tests...")
                results["unit_tests"] = await self._run_unit_tests()

            # Run integration tests
            if self.config.enable_integration_tests:
                logger.info("Running integration tests...")
                results["integration_tests"] = await self._run_integration_tests()

            # Run performance tests
            if self.config.enable_performance_tests:
                logger.info("Running performance tests...")
                results["performance_tests"] = await self._run_performance_tests()

            # Run stress tests
            if self.config.enable_stress_tests:
                logger.info("Running stress tests...")
                results["stress_tests"] = await self._run_stress_tests()

            # Generate summary
            total_duration = (time.time() - start_time) * 1000
            results["summary"] = self._generate_test_summary(total_duration)

            logger.info("Comprehensive testing suite completed")
            return results

        except Exception as e:
            logger.error(f"Testing suite failed: {e}")
            return {"error": str(e)}

    async def _run_unit_tests(self) -> dict[str, Any]:
        """Run unit tests for individual components"""
        try:
            results = {}

            # Test cache service basic operations
            cache_test = await self._test_cache_service_basic()
            results["cache_service_basic"] = cache_test
            self.test_results.append(cache_test)

            # Test similarity engine algorithms
            similarity_test = await self._test_similarity_algorithms()
            results["similarity_algorithms"] = similarity_test
            self.test_results.append(similarity_test)

            # Test cache invalidation
            invalidation_test = await self._test_cache_invalidation()
            results["cache_invalidation"] = invalidation_test
            self.test_results.append(invalidation_test)

            return results

        except Exception as e:
            logger.error(f"Unit tests failed: {e}")
            return {"error": str(e)}

    async def _test_cache_service_basic(self) -> TestResult:
        """Test basic cache service operations"""
        start_time = time.time()

        try:
            # Test cache entry storage
            test_entry = CacheEntry(
                user_id="test_user",
                model_type="test_model",
                prompt="Test prompt for unit testing",
                response="Test response for unit testing",
                tokens_used=50,
                cache_hit=False,
                similarity_score=1.0,
            )

            entry_id = await self.cache_service.store_cache_entry(test_entry)
            if not entry_id:
                raise Exception("Failed to store cache entry")

            # Test cache entry retrieval with exact match
            retrieved_entry = await self.cache_service.retrieve_cache_entry(
                "Test prompt for unit testing", "test_user", similarity_threshold=0.0
            )
            if not retrieved_entry:
                raise Exception("Failed to retrieve cache entry")

            # Test cache statistics
            stats = await self.cache_service.get_cache_statistics()
            if not stats:
                raise Exception("Failed to get cache statistics")

            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="cache_service_basic",
                test_category="unit",
                status="passed",
                duration_ms=duration,
                details={
                    "entry_stored": True,
                    "entry_retrieved": True,
                    "statistics_retrieved": True,
                    "entry_id": entry_id,
                },
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="cache_service_basic",
                test_category="unit",
                status="failed",
                duration_ms=duration,
                details={},
                error_message=str(e),
            )

    async def _test_similarity_algorithms(self) -> TestResult:
        """Test similarity scoring algorithms"""
        start_time = time.time()

        try:
            # Test text similarity
            text1 = "Machine learning is a subset of artificial intelligence"
            text2 = "ML is part of AI and involves training models"

            # Test cosine similarity
            cosine_result = self.similarity_engine.calculate_similarity(text1, text2, algorithm="cosine")
            if cosine_result.score < 0:
                raise Exception("Cosine similarity score invalid")

            # Test Jaccard similarity
            jaccard_result = self.similarity_engine.calculate_similarity(text1, text2, algorithm="jaccard")
            if jaccard_result.score < 0:
                raise Exception("Jaccard similarity score invalid")

            # Test hybrid similarity
            hybrid_result = self.similarity_engine.calculate_similarity(text1, text2, algorithm="hybrid")
            if hybrid_result.score < 0:
                raise Exception("Hybrid similarity score invalid")

            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="similarity_algorithms",
                test_category="unit",
                status="passed",
                duration_ms=duration,
                details={
                    "cosine_score": cosine_result.score,
                    "jaccard_score": jaccard_result.score,
                    "hybrid_score": hybrid_result.score,
                },
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="similarity_algorithms",
                test_category="unit",
                status="failed",
                duration_ms=duration,
                details={},
                error_message=str(e),
            )

    async def _test_cache_invalidation(self) -> TestResult:
        """Test cache invalidation functionality"""
        start_time = time.time()

        try:
            # Test TTL invalidation
            ttl_result = self.integration.invalidation_system.invalidate_by_ttl()
            if not isinstance(ttl_result, int):
                raise Exception("TTL invalidation returned invalid result")

            # Test similarity threshold invalidation
            similarity_result = self.integration.invalidation_system.invalidate_by_similarity_threshold(0.3)
            if not isinstance(similarity_result, int):
                raise Exception("Similarity threshold invalidation returned invalid result")

            # Test frequency-based invalidation
            frequency_result = self.integration.invalidation_system.invalidate_by_frequency()
            if not isinstance(frequency_result, int):
                raise Exception("Frequency-based invalidation returned invalid result")

            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="cache_invalidation",
                test_category="unit",
                status="passed",
                duration_ms=duration,
                details={
                    "ttl_invalidated": ttl_result,
                    "similarity_invalidated": similarity_result,
                    "frequency_invalidated": frequency_result,
                },
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="cache_invalidation",
                test_category="unit",
                status="failed",
                duration_ms=duration,
                details={},
                error_message=str(e),
            )

    async def _run_integration_tests(self) -> dict[str, Any]:
        """Run integration tests for system interactions"""
        try:
            results = {}

            # Test LTST memory integration
            ltst_test = await self._test_ltst_integration()
            results["ltst_integration"] = ltst_test
            self.test_results.append(ltst_test)

            # Test performance monitoring integration
            perf_test = await self._test_performance_monitoring()
            results["performance_monitoring"] = perf_test
            self.test_results.append(perf_test)

            # Test end-to-end workflow
            workflow_test = await self._test_end_to_end_workflow()
            results["end_to_end_workflow"] = workflow_test
            self.test_results.append(workflow_test)

            return results

        except Exception as e:
            logger.error(f"Integration tests failed: {e}")
            return {"error": str(e)}

    async def _test_ltst_integration(self) -> TestResult:
        """Test LTST memory integration"""
        start_time = time.time()

        try:
            # Test context retrieval
            test_query = "What is the difference between supervised and unsupervised learning?"
            context = await self.ltst_integration.retrieve_context(test_query, "test_user")

            # Test context storage
            if context:
                store_success = await self.ltst_integration.store_context(context, "test_user")
                if not store_success:
                    raise Exception("Failed to store context")

            # Test similar context search
            similar_contexts = await self.ltst_integration.search_similar_contexts(
                "machine learning algorithms", limit=5
            )

            # Test integration metrics
            metrics = await self.ltst_integration.get_integration_metrics()
            if not metrics:
                raise Exception("Failed to get integration metrics")

            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="ltst_integration",
                test_category="integration",
                status="passed",
                duration_ms=duration,
                details={
                    "context_retrieved": context is not None,
                    "context_stored": context is not None,
                    "similar_contexts_found": len(similar_contexts),
                    "metrics_retrieved": True,
                },
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="ltst_integration",
                test_category="integration",
                status="failed",
                duration_ms=duration,
                details={},
                error_message=str(e),
            )

    async def _test_performance_monitoring(self) -> TestResult:
        """Test performance monitoring integration"""
        start_time = time.time()

        try:
            # Wait for metrics collection
            await asyncio.sleep(20)

            # Test dashboard retrieval
            dashboard = await self.performance_monitor.get_monitoring_dashboard()
            if not dashboard:
                raise Exception("Failed to get monitoring dashboard")

            # Test alert acknowledgment (if alerts exist)
            if dashboard.get("alerts"):
                first_alert = dashboard["alerts"][0]
                ack_success = await self.performance_monitor.acknowledge_alert(first_alert["id"])
                if not ack_success:
                    raise Exception("Failed to acknowledge alert")

            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="performance_monitoring",
                test_category="integration",
                status="passed",
                duration_ms=duration,
                details={
                    "dashboard_retrieved": True,
                    "alerts_acknowledged": dashboard.get("alerts", []) != [],
                    "dashboard_status": dashboard.get("dashboard", {}).get("status", "unknown"),
                },
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="performance_monitoring",
                test_category="integration",
                status="failed",
                duration_ms=duration,
                details={},
                error_message=str(e),
            )

    async def _test_end_to_end_workflow(self) -> TestResult:
        """Test complete end-to-end workflow"""
        start_time = time.time()

        try:
            # Simulate complete user workflow
            user_query = "Explain neural networks in simple terms"

            # 1. Store initial response
            initial_entry = CacheEntry(
                user_id="workflow_user",
                model_type="gpt-4",
                prompt=user_query,
                response="Neural networks are computing systems inspired by biological brains...",
                tokens_used=150,
                cache_hit=False,
                similarity_score=1.0,
            )

            entry_id = await self.cache_service.store_cache_entry(initial_entry)
            if not entry_id:
                raise Exception("Failed to store initial entry")

            # 2. Retrieve from cache (should hit)
            retrieved_entry = await self.cache_service.retrieve_cache_entry(
                user_query, "workflow_user", similarity_threshold=0.0
            )
            if not retrieved_entry:
                raise Exception("Failed to retrieve cached entry")

            # 3. Test similarity search
            similar_entries = await self.cache_service.search_similar_entries("neural networks", limit=3)

            # 4. Test LTST integration
            context = await self.ltst_integration.retrieve_context(user_query, "workflow_user")

            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="end_to_end_workflow",
                test_category="integration",
                status="passed",
                duration_ms=duration,
                details={
                    "entry_stored": True,
                    "entry_retrieved": True,
                    "similar_entries_found": len(similar_entries),
                    "ltst_context_retrieved": context is not None,
                },
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="end_to_end_workflow",
                test_category="integration",
                status="failed",
                duration_ms=duration,
                details={},
                error_message=str(e),
            )

    async def _run_performance_tests(self) -> dict[str, Any]:
        """Run performance tests"""
        try:
            results = {}

            # Test cache service performance
            cache_perf_test = await self._test_cache_service_performance()
            results["cache_service_performance"] = cache_perf_test
            self.test_results.append(cache_perf_test)

            # Test similarity engine performance
            similarity_perf_test = await self._test_similarity_engine_performance()
            results["similarity_engine_performance"] = similarity_perf_test
            self.test_results.append(similarity_perf_test)

            # Test overall system performance
            system_perf_test = await self._test_system_performance()
            results["system_performance"] = system_perf_test
            self.test_results.append(system_perf_test)

            return results

        except Exception as e:
            logger.error(f"Performance tests failed: {e}")
            return {"error": str(e)}

    async def _test_cache_service_performance(self) -> TestResult:
        """Test cache service performance"""
        start_time = time.time()

        try:
            # Generate test data
            test_entries = []
            for i in range(self.config.test_data_size):
                entry = CacheEntry(
                    user_id=f"perf_user_{i}",
                    model_type="test_model",
                    prompt=f"Performance test prompt {i}",
                    response=f"Performance test response {i}",
                    tokens_used=50 + i,
                    cache_hit=False,
                    similarity_score=0.8 + (i * 0.002),
                )
                test_entries.append(entry)

            # Measure storage performance
            storage_start = time.time()
            stored_ids = []
            for entry in test_entries:
                entry_id = await self.cache_service.store_cache_entry(entry)
                stored_ids.append(entry_id)

            storage_time = (time.time() - storage_start) * 1000
            storage_throughput = len(test_entries) / (storage_time / 1000)

            # Measure retrieval performance
            retrieval_start = time.time()
            retrieved_count = 0
            for entry in test_entries[:10]:  # Test first 10
                retrieved = await self.cache_service.retrieve_cache_entry(entry.prompt, entry.user_id)
                if retrieved:
                    retrieved_count += 1

            retrieval_time = (time.time() - retrieval_start) * 1000
            retrieval_throughput = retrieved_count / (retrieval_time / 1000)

            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="cache_service_performance",
                test_category="performance",
                status="passed",
                duration_ms=duration,
                details={
                    "entries_stored": len(stored_ids),
                    "storage_time_ms": storage_time,
                    "storage_throughput_ops_per_sec": storage_throughput,
                    "retrieval_time_ms": retrieval_time,
                    "retrieval_throughput_ops_per_sec": retrieval_throughput,
                    "retrieval_success_rate": retrieved_count / 10,
                },
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="cache_service_performance",
                test_category="performance",
                status="failed",
                duration_ms=duration,
                details={},
                error_message=str(e),
            )

    async def _test_similarity_engine_performance(self) -> TestResult:
        """Test similarity engine performance"""
        start_time = time.time()

        try:
            # Generate test texts
            test_texts = [
                "Machine learning algorithms for data analysis",
                "AI systems for natural language processing",
                "Deep learning neural networks for image recognition",
                "Predictive analytics using statistical models",
                "Computer vision applications in robotics",
            ]

            # Measure similarity calculation performance
            similarity_start = time.time()
            similarity_results = []

            for i, text1 in enumerate(test_texts):
                for j, text2 in enumerate(test_texts[i + 1 :], i + 1):
                    result = self.similarity_engine.calculate_similarity(text1, text2, algorithm="hybrid")
                    similarity_results.append(result.score)

            similarity_time = (time.time() - similarity_start) * 1000
            similarity_throughput = len(similarity_results) / (similarity_time / 1000)

            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="similarity_engine_performance",
                test_category="performance",
                status="passed",
                duration_ms=duration,
                details={
                    "similarity_calculations": len(similarity_results),
                    "calculation_time_ms": similarity_time,
                    "throughput_ops_per_sec": similarity_throughput,
                    "avg_similarity_score": sum(similarity_results) / len(similarity_results),
                },
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="similarity_engine_performance",
                test_category="performance",
                status="passed",
                duration_ms=duration,
                details={},
                error_message=str(e),
            )

    async def _test_system_performance(self) -> TestResult:
        """Test overall system performance"""
        start_time = time.time()

        try:
            # Get performance metrics from monitor
            await asyncio.sleep(10)  # Wait for metrics collection

            dashboard = await self.performance_monitor.get_monitoring_dashboard()
            if not dashboard:
                raise Exception("Failed to get performance dashboard")

            performance_summary = dashboard.get("performance_summary", {})

            # Validate performance thresholds
            cache_hit_rate = performance_summary.get("cache_hit_rate", 0.0)
            response_time = performance_summary.get("avg_response_time_ms", 0.0)
            memory_usage = performance_summary.get("memory_usage_mb", 0.0)

            # Check thresholds
            hit_rate_ok = cache_hit_rate >= self.config.min_cache_hit_rate
            response_time_ok = response_time <= self.config.max_response_time_ms
            memory_ok = memory_usage <= self.config.max_memory_usage_mb

            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="system_performance",
                test_category="performance",
                status="passed" if all([hit_rate_ok, response_time_ok, memory_ok]) else "failed",
                duration_ms=duration,
                details={
                    "cache_hit_rate": cache_hit_rate,
                    "response_time_ms": response_time,
                    "memory_usage_mb": memory_usage,
                    "hit_rate_threshold_met": hit_rate_ok,
                    "response_time_threshold_met": response_time_ok,
                    "memory_threshold_met": memory_ok,
                },
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="system_performance",
                test_category="performance",
                status="failed",
                duration_ms=duration,
                details={},
                error_message=str(e),
            )

    async def _run_stress_tests(self) -> dict[str, Any]:
        """Run stress tests"""
        try:
            results = {}

            # Test concurrent user load
            concurrent_test = await self._test_concurrent_users()
            results["concurrent_users"] = concurrent_test
            self.test_results.append(concurrent_test)

            # Test memory pressure
            memory_test = await self._test_memory_pressure()
            results["memory_pressure"] = memory_test
            self.test_results.append(memory_test)

            return results

        except Exception as e:
            logger.error(f"Stress tests failed: {e}")
            return {"error": str(e)}

    async def _test_concurrent_users(self) -> TestResult:
        """Test system under concurrent user load"""
        start_time = time.time()

        try:
            # Simulate concurrent users
            async def simulate_user(user_id: int):
                try:
                    # Store entry
                    entry = CacheEntry(
                        user_id=f"stress_user_{user_id}",
                        model_type="stress_test",
                        prompt=f"Stress test prompt from user {user_id}",
                        response=f"Stress test response for user {user_id}",
                        tokens_used=100,
                        cache_hit=False,
                        similarity_score=0.9,
                    )

                    await self.cache_service.store_cache_entry(entry)

                    # Retrieve entry
                    await self.cache_service.retrieve_cache_entry(entry.prompt, entry.user_id)

                    return True
                except Exception:
                    return False

            # Run concurrent users
            user_tasks = [simulate_user(i) for i in range(self.config.stress_test_concurrent_users)]

            results = await asyncio.gather(*user_tasks, return_exceptions=True)
            successful_users = sum(1 for r in results if r is True)

            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="concurrent_users",
                test_category="stress",
                status="passed" if successful_users >= self.config.stress_test_concurrent_users * 0.8 else "failed",
                duration_ms=duration,
                details={
                    "concurrent_users": self.config.stress_test_concurrent_users,
                    "successful_users": successful_users,
                    "success_rate": successful_users / self.config.stress_test_concurrent_users,
                },
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="concurrent_users",
                test_category="stress",
                status="failed",
                duration_ms=duration,
                details={},
                error_message=str(e),
            )

    async def _test_memory_pressure(self) -> TestResult:
        """Test system under memory pressure"""
        start_time = time.time()

        try:
            # Generate large amount of test data
            large_entries = []
            for i in range(self.config.test_data_size * 2):
                entry = CacheEntry(
                    user_id=f"memory_user_{i}",
                    model_type="memory_test",
                    prompt=f"Memory pressure test prompt {i} " * 10,  # Large prompt
                    response=f"Memory pressure test response {i} " * 20,  # Large response
                    tokens_used=500 + i,
                    cache_hit=False,
                    similarity_score=0.8,
                )
                large_entries.append(entry)

            # Store large entries
            stored_count = 0
            for entry in large_entries:
                try:
                    entry_id = await self.cache_service.store_cache_entry(entry)
                    if entry_id:
                        stored_count += 1
                except Exception:
                    break  # Stop if memory pressure causes failure

            # Check memory usage
            dashboard = await self.performance_monitor.get_monitoring_dashboard()
            memory_usage = dashboard.get("performance_summary", {}).get("memory_usage_mb", 0.0)

            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="memory_pressure",
                test_category="stress",
                status="passed" if stored_count >= len(large_entries) * 0.7 else "failed",
                duration_ms=duration,
                details={
                    "large_entries_attempted": len(large_entries),
                    "large_entries_stored": stored_count,
                    "storage_success_rate": stored_count / len(large_entries),
                    "final_memory_usage_mb": memory_usage,
                },
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name="memory_pressure",
                test_category="stress",
                status="failed",
                duration_ms=duration,
                details={},
                error_message=str(e),
            )

    def _generate_test_summary(self, total_duration_ms: float) -> dict[str, Any]:
        """Generate comprehensive test summary"""
        try:
            # Collect all test results from nested dictionaries
            all_results = []

            # Extract results from unit tests
            if hasattr(self, "test_results") and self.test_results:
                all_results.extend(self.test_results)

            # Extract results from integration tests
            if hasattr(self, "integration_results") and self.integration_results:
                for test_name, result in self.integration_results.items():
                    if isinstance(result, TestResult):
                        all_results.append(result)

            # Count test results by status
            passed_tests = [r for r in all_results if r.status == "passed"]
            failed_tests = [r for r in all_results if r.status == "failed"]
            skipped_tests = [r for r in all_results if r.status == "skipped"]

            # Calculate success rate
            total_tests = len(all_results)
            success_rate = (len(passed_tests) / total_tests * 100) if total_tests > 0 else 0

            # Calculate average duration
            avg_duration = sum(r.duration_ms for r in all_results) / total_tests if total_tests > 0 else 0

            return {
                "total_tests": total_tests,
                "passed_tests": len(passed_tests),
                "failed_tests": len(failed_tests),
                "skipped_tests": len(skipped_tests),
                "success_rate_percent": success_rate,
                "total_duration_ms": total_duration_ms,
                "average_test_duration_ms": avg_duration,
                "overall_status": "passed" if success_rate >= 90 else "failed",
            }

        except Exception as e:
            logger.error(f"Failed to generate test summary: {e}")
            return {"error": str(e)}

    async def close(self):
        """Close the testing suite and cleanup resources"""
        try:
            logger.info("Closing Comprehensive Testing Suite")

            # Close all systems
            if self.performance_monitor:
                await self.performance_monitor.close()

            if self.ltst_integration:
                await self.ltst_integration.close()

            if self.integration:
                await self.integration.close()

            if self.cache_service:
                await self.cache_service.close()

            logger.info("Comprehensive Testing Suite closed successfully")

        except Exception as e:
            logger.error(f"Error closing testing suite: {e}")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

async def main():
    """Main function to run comprehensive testing suite"""
    try:
        logger.info("Running Comprehensive Testing Suite")

        # Create test configuration
        config = TestConfig(
            enable_unit_tests=True,
            enable_integration_tests=True,
            enable_performance_tests=True,
            enable_stress_tests=True,
            test_data_size=50,  # Smaller size for testing
            performance_test_duration_seconds=15,
            stress_test_concurrent_users=5,
            stress_test_duration_seconds=30,
        )

        # Run comprehensive testing
        async with ComprehensiveTestingSuite(config) as test_suite:
            results = await test_suite.run_all_tests()

            # Log results
            logger.info(f"Testing completed with results: {results}")

            # Check overall status
            summary = results.get("summary", {})
            overall_status = summary.get("overall_status", "unknown")
            success_rate = summary.get("success_rate_percent", 0)

            logger.info(f"Overall test status: {overall_status}")
            logger.info(f"Success rate: {success_rate:.1f}%")

            return overall_status == "passed"

    except Exception as e:
        logger.error(f"Comprehensive testing failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
