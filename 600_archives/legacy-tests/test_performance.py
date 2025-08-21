#!/usr/bin/env python3
"""
Performance Tests for DSPy RAG System
"""
import pytest

# Mark all tests in this file as deprecated
pytestmark = pytest.mark.deprecated
import time
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor
from src.enhanced_rag_system import EnhancedRAGSystem
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class TestPerformance:
    """Performance test suite"""

    def test_rag_system_response_time(self):
        """Test RAG system response time under load"""
        rag_system = EnhancedRAGSystem()

        # Test query response time
        start_time = time.time()
        response = rag_system.ask_question("What is the main purpose of this system?")
        end_time = time.time()

        response_time = end_time - start_time
        assert response_time < 5.0, f"Response time {response_time}s exceeds 5s threshold"

        logger.info(f"✅ RAG system response time: {response_time:.2f}s")

    def test_concurrent_queries(self):
        """Test system performance under concurrent load"""
        rag_system = EnhancedRAGSystem()

        def make_query(query_id):
            start_time = time.time()
            response = rag_system.ask_question(f"Test query {query_id}")
            end_time = time.time()
            return end_time - start_time

        # Run 5 concurrent queries
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_query, i) for i in range(5)]
            response_times = [future.result() for future in futures]

        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)

        assert avg_response_time < 3.0, f"Average response time {avg_response_time}s exceeds 3s threshold"
        assert max_response_time < 10.0, f"Max response time {max_response_time}s exceeds 10s threshold"

        logger.info(f"✅ Concurrent queries - Avg: {avg_response_time:.2f}s, Max: {max_response_time:.2f}s")

    def test_memory_usage(self):
        """Test memory usage during operation"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        rag_system = EnhancedRAGSystem()

        # Perform multiple operations
        for i in range(10):
            rag_system.ask_question(f"Memory test query {i}")

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        assert memory_increase < 100.0, f"Memory increase {memory_increase}MB exceeds 100MB threshold"

        logger.info(f"✅ Memory usage - Initial: {initial_memory:.1f}MB, Final: {final_memory:.1f}MB, Increase: {memory_increase:.1f}MB")

    def test_cpu_usage(self):
        """Test CPU usage during operation"""
        rag_system = EnhancedRAGSystem()

        # Monitor CPU usage during query
        cpu_percentages = []
        def monitor_cpu():
            while not hasattr(self, '_stop_monitoring'):
                cpu_percentages.append(psutil.cpu_percent(interval=0.1))

        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()

        # Perform query
        response = rag_system.ask_question("CPU usage test query")

        # Stop monitoring
        self._stop_monitoring = True
        monitor_thread.join()

        avg_cpu = sum(cpu_percentages) / len(cpu_percentages) if cpu_percentages else 0
        max_cpu = max(cpu_percentages) if cpu_percentages else 0

        assert avg_cpu < 80.0, f"Average CPU usage {avg_cpu}% exceeds 80% threshold"
        assert max_cpu < 95.0, f"Max CPU usage {max_cpu}% exceeds 95% threshold"

        logger.info(f"✅ CPU usage - Avg: {avg_cpu:.1f}%, Max: {max_cpu:.1f}%")
