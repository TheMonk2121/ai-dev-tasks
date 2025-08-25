#!/usr/bin/env python3
"""
Performance Benchmark for MCP Integration System

This script benchmarks the performance of various MCP components:
- Server initialization time
- Document processing speed
- Memory usage
- Concurrent processing capabilities
- Cache performance
"""

import asyncio
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List

import psutil

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.mcp_integration import (
    DatabaseMCPServer,
    FileSystemMCPServer,
    GitHubMCPServer,
    MCPConfig,
    OfficeMCPServer,
    PDFMCPServer,
    ProcessedDocument,
    WebMCPServer,
)


@dataclass
class BenchmarkResult:
    """Results from a performance benchmark."""

    test_name: str
    duration: float
    memory_usage: float
    success_count: int
    error_count: int
    throughput: float  # operations per second


class PerformanceBenchmark:
    """Comprehensive performance benchmarking for MCP integration."""

    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.base_config = MCPConfig(
            server_name="benchmark_server",
            max_file_size=10 * 1024 * 1024,  # 10MB
            timeout=30,
            retry_attempts=3,
            cache_enabled=True,
            cache_ttl=3600,
        )

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024

    async def benchmark_server_initialization(self) -> BenchmarkResult:
        """Benchmark server initialization times."""
        print("🔧 Benchmarking server initialization...")

        servers = [
            ("FileSystem", FileSystemMCPServer),
            ("Web", WebMCPServer),
            ("PDF", PDFMCPServer),
            ("GitHub", GitHubMCPServer),
            ("Database", DatabaseMCPServer),
            ("Office", OfficeMCPServer),
        ]

        start_time = time.time()
        start_memory = self.get_memory_usage()
        success_count = 0
        error_count = 0

        for name, server_class in servers:
            try:
                config = MCPConfig(server_name=f"{name.lower()}_server")
                server = server_class(config)
                success_count += 1
                print(f"  ✅ {name} server initialized successfully")
            except Exception as e:
                print(f"  ❌ {name} server failed: {e}")
                error_count += 1

        duration = time.time() - start_time
        end_memory = self.get_memory_usage()
        memory_usage = end_memory - start_memory

        return BenchmarkResult(
            test_name="Server Initialization",
            duration=duration,
            memory_usage=memory_usage,
            success_count=success_count,
            error_count=error_count,
            throughput=len(servers) / duration,
        )

    async def benchmark_document_processing(self) -> BenchmarkResult:
        """Benchmark document processing performance."""
        print("📄 Benchmarking document processing...")

        # Create test documents
        test_docs = [
            ("test.txt", "This is a test document for benchmarking."),
            ("test.html", "<html><body><h1>Test</h1><p>Benchmark content</p></body></html>"),
            ("test.md", "# Test Document\n\nThis is a markdown test document."),
        ]

        # Create temporary files
        temp_files = []
        for filename, content in test_docs:
            filepath = Path(f"/tmp/{filename}")
            filepath.write_text(content)
            temp_files.append(str(filepath))

        try:
            config = MCPConfig(server_name="filesystem_benchmark")
            server = FileSystemMCPServer(config)

            start_time = time.time()
            start_memory = self.get_memory_usage()
            success_count = 0
            error_count = 0

            for filepath in temp_files:
                try:
                    result = await server.process_document(filepath)
                    if result.success:
                        success_count += 1
                        print(f"  ✅ Processed {Path(filepath).name}")
                    else:
                        error_count += 1
                        print(f"  ❌ Failed to process {Path(filepath).name}")
                except Exception as e:
                    print(f"  ❌ Processing {filepath} failed: {e}")
                    error_count += 1

            duration = time.time() - start_time
            end_memory = self.get_memory_usage()
            memory_usage = end_memory - start_memory

            server.cleanup()

            return BenchmarkResult(
                test_name="Document Processing",
                duration=duration,
                memory_usage=memory_usage,
                success_count=success_count,
                error_count=error_count,
                throughput=len(temp_files) / duration,
            )

        finally:
            # Clean up temporary files
            for filepath in temp_files:
                try:
                    Path(filepath).unlink()
                except:
                    pass

    async def benchmark_concurrent_processing(self) -> BenchmarkResult:
        """Benchmark concurrent document processing."""
        print("⚡ Benchmarking concurrent processing...")

        # Create multiple test documents
        test_docs = []
        for i in range(10):
            content = f"This is test document {i} for concurrent benchmarking."
            filepath = Path(f"/tmp/concurrent_test_{i}.txt")
            filepath.write_text(content)
            test_docs.append(str(filepath))

        try:
            config = MCPConfig(server_name="concurrent_benchmark")
            server = FileSystemMCPServer(config)

            start_time = time.time()
            start_memory = self.get_memory_usage()

            # Process documents concurrently
            tasks = []
            for filepath in test_docs:
                task = server.process_document(filepath)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            duration = time.time() - start_time
            end_memory = self.get_memory_usage()
            memory_usage = end_memory - start_memory

            success_count = sum(1 for r in results if isinstance(r, ProcessedDocument) and r.success)
            error_count = len(results) - success_count

            print(f"  ✅ Concurrent processing: {success_count} success, {error_count} errors")

            server.cleanup()

            return BenchmarkResult(
                test_name="Concurrent Processing",
                duration=duration,
                memory_usage=memory_usage,
                success_count=success_count,
                error_count=error_count,
                throughput=len(test_docs) / duration,
            )

        finally:
            # Clean up temporary files
            for filepath in test_docs:
                try:
                    Path(filepath).unlink()
                except:
                    pass

    async def benchmark_cache_performance(self) -> BenchmarkResult:
        """Benchmark cache performance."""
        print("💾 Benchmarking cache performance...")

        # Create a test document
        filepath = "/tmp/cache_test.txt"
        Path(filepath).write_text("This is a test document for cache benchmarking.")

        try:
            config = MCPConfig(server_name="cache_benchmark")
            server = FileSystemMCPServer(config)

            start_time = time.time()
            start_memory = self.get_memory_usage()

            # First access (cache miss)
            result1 = await server.process_document(filepath)

            # Second access (cache hit)
            result2 = await server.process_document(filepath)

            # Third access (cache hit)
            result3 = await server.process_document(filepath)

            duration = time.time() - start_time
            end_memory = self.get_memory_usage()
            memory_usage = end_memory - start_memory

            success_count = sum(1 for r in [result1, result2, result3] if r.success)
            error_count = 3 - success_count

            print(f"  ✅ Cache performance: {success_count} success, {error_count} errors")

            server.cleanup()

            return BenchmarkResult(
                test_name="Cache Performance",
                duration=duration,
                memory_usage=memory_usage,
                success_count=success_count,
                error_count=error_count,
                throughput=3 / duration,
            )

        finally:
            # Clean up temporary file
            try:
                Path(filepath).unlink()
            except:
                pass

    async def benchmark_memory_efficiency(self) -> BenchmarkResult:
        """Benchmark memory efficiency with large documents."""
        print("🧠 Benchmarking memory efficiency...")

        # Create a larger test document
        large_content = "This is a large test document. " * 10000  # ~300KB
        filepath = "/tmp/large_test.txt"
        Path(filepath).write_text(large_content)

        try:
            config = MCPConfig(server_name="memory_benchmark")
            server = FileSystemMCPServer(config)

            start_time = time.time()
            start_memory = self.get_memory_usage()

            # Process the large document multiple times
            success_count = 0
            error_count = 0

            for i in range(5):
                try:
                    result = await server.process_document(filepath)
                    if result.success:
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    print(f"  ❌ Large document processing failed: {e}")
                    error_count += 1

            duration = time.time() - start_time
            end_memory = self.get_memory_usage()
            memory_usage = end_memory - start_memory

            print(f"  ✅ Memory efficiency: {success_count} success, {error_count} errors")

            server.cleanup()

            return BenchmarkResult(
                test_name="Memory Efficiency",
                duration=duration,
                memory_usage=memory_usage,
                success_count=success_count,
                error_count=error_count,
                throughput=5 / duration,
            )

        finally:
            # Clean up temporary file
            try:
                Path(filepath).unlink()
            except:
                pass

    def print_results(self):
        """Print benchmark results in a formatted table."""
        print("\n" + "=" * 80)
        print("📊 PERFORMANCE BENCHMARK RESULTS")
        print("=" * 80)

        print(
            f"{'Test Name':<25} {'Duration (s)':<12} {'Memory (MB)':<12} {'Success':<8} {'Errors':<8} {'Throughput':<12}"
        )
        print("-" * 80)

        for result in self.results:
            print(
                f"{result.test_name:<25} {result.duration:<12.3f} {result.memory_usage:<12.2f} "
                f"{result.success_count:<8} {result.error_count:<8} {result.throughput:<12.2f}"
            )

        print("-" * 80)

        # Summary statistics
        total_duration = sum(r.duration for r in self.results)
        total_memory = sum(r.memory_usage for r in self.results)
        total_success = sum(r.success_count for r in self.results)
        total_errors = sum(r.error_count for r in self.results)

        print("\n📈 SUMMARY:")
        print(f"   Total Duration: {total_duration:.3f} seconds")
        print(f"   Total Memory Usage: {total_memory:.2f} MB")
        print(f"   Total Success: {total_success}")
        print(f"   Total Errors: {total_errors}")
        if total_success + total_errors > 0:
            print(f"   Success Rate: {total_success/(total_success+total_errors)*100:.1f}%")

        # Performance recommendations
        print("\n💡 PERFORMANCE RECOMMENDATIONS:")

        for result in self.results:
            if result.duration > 1.0:
                print(f"   ⚠️  {result.test_name}: Consider optimizing for faster execution")
            if result.memory_usage > 50:
                print(f"   ⚠️  {result.test_name}: Consider memory optimization")
            if result.error_count > 0:
                print(f"   ⚠️  {result.test_name}: Address {result.error_count} errors")
            if result.throughput < 1.0:
                print(f"   ⚠️  {result.test_name}: Consider improving throughput")

        # Overall assessment
        print("\n🎯 OVERALL ASSESSMENT:")
        if total_errors == 0:
            print("   ✅ All tests passed successfully!")
        else:
            print(f"   ⚠️  {total_errors} errors detected - review and fix")

        if total_duration < 5.0:
            print(f"   ✅ Performance is excellent ({total_duration:.3f}s total)")
        elif total_duration < 10.0:
            print(f"   ⚠️  Performance is good ({total_duration:.3f}s total)")
        else:
            print(f"   ❌ Performance needs improvement ({total_duration:.3f}s total)")

    async def run_all_benchmarks(self):
        """Run all performance benchmarks."""
        print("🚀 Starting MCP Integration Performance Benchmarks...")
        print("=" * 60)

        benchmarks = [
            self.benchmark_server_initialization,
            self.benchmark_document_processing,
            self.benchmark_concurrent_processing,
            self.benchmark_cache_performance,
            self.benchmark_memory_efficiency,
        ]

        for benchmark in benchmarks:
            try:
                result = await benchmark()
                self.results.append(result)
            except Exception as e:
                print(f"❌ Benchmark failed: {e}")

        self.print_results()


async def main():
    """Main function to run performance benchmarks."""
    benchmark = PerformanceBenchmark()
    await benchmark.run_all_benchmarks()


if __name__ == "__main__":
    asyncio.run(main())
