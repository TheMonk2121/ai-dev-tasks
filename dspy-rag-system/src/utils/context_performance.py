#!/usr/bin/env python3
"""
Context Integration Performance Optimization (T7)

Advanced performance optimizations for the context integration system:
- LRU caching with intelligent eviction
- Connection pooling for subprocess calls
- Memory usage optimization
- Response time optimization
- Load balancing for multiple instances
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import psutil

_LOG = logging.getLogger("context_performance")


@dataclass
class CacheEntry:
    """Cache entry with metadata for intelligent eviction"""

    data: str
    timestamp: float
    access_count: int = 0
    size_bytes: int = 0
    role: str = ""
    task_hash: str = ""
    last_access: float = field(default_factory=time.time)

    def update_access(self):
        """Update access metadata"""
        self.access_count += 1
        self.last_access = time.time()


class LRUCache:
    """Advanced LRU cache with intelligent eviction policies"""

    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        """
        Initialize LRU cache.

        Args:
            max_size: Maximum number of entries
            max_memory_mb: Maximum memory usage in MB
        """
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.current_memory_bytes = 0
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get(self, key: str) -> Optional[str]:
        """Get value from cache with access tracking"""
        if key in self.cache:
            entry = self.cache[key]
            entry.update_access()
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            return entry.data
        else:
            self.misses += 1
            return None

    def put(self, key: str, value: str, role: str = "", task_hash: str = "") -> None:
        """Put value in cache with intelligent eviction"""
        # Calculate size
        size_bytes = len(value.encode("utf-8"))

        # Create entry
        entry = CacheEntry(data=value, timestamp=time.time(), size_bytes=size_bytes, role=role, task_hash=task_hash)

        # Check if key already exists
        if key in self.cache:
            old_entry = self.cache[key]
            self.current_memory_bytes -= old_entry.size_bytes
            self.cache.move_to_end(key)
        else:
            # Check if we need to evict
            while len(self.cache) >= self.max_size or self.current_memory_bytes + size_bytes > self.max_memory_bytes:
                self._evict_least_valuable()

        # Add new entry
        self.cache[key] = entry
        self.current_memory_bytes += size_bytes

    def _evict_least_valuable(self) -> None:
        """Evict least valuable entry based on multiple factors"""
        if not self.cache:
            return

        # Calculate value scores for all entries
        scores = {}
        current_time = time.time()

        for key, entry in self.cache.items():
            # Time-based decay (older entries get lower scores)
            time_factor = 1.0 / (1.0 + (current_time - entry.timestamp) / 3600)  # 1 hour decay

            # Access-based boost (frequently accessed entries get higher scores)
            access_factor = 1.0 + (entry.access_count * 0.1)

            # Size penalty (larger entries get lower scores)
            size_factor = 1.0 / (1.0 + entry.size_bytes / 1024)  # 1KB baseline

            # Combined score
            score = time_factor * access_factor * size_factor
            scores[key] = score

        # Find least valuable entry
        least_valuable_key = min(scores.keys(), key=lambda k: scores[k])

        # Evict it
        entry = self.cache[least_valuable_key]
        self.current_memory_bytes -= entry.size_bytes
        del self.cache[least_valuable_key]
        self.evictions += 1

        _LOG.debug(f"Evicted cache entry: {least_valuable_key} (score: {scores[least_valuable_key]:.3f})")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "memory_usage_mb": self.current_memory_bytes / (1024 * 1024),
            "max_memory_mb": self.max_memory_bytes / (1024 * 1024),
            "hit_rate": self.hits / max(self.hits + self.misses, 1) * 100,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
        }


class ConnectionPool:
    """Connection pool for subprocess calls to reduce overhead"""

    def __init__(self, max_workers: int = 4, max_connections: int = 10):
        """
        Initialize connection pool.

        Args:
            max_workers: Maximum number of worker threads
            max_connections: Maximum number of concurrent connections
        """
        self.max_workers = max_workers
        self.max_connections = max_connections
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_connections = 0
        self.connection_semaphore = asyncio.Semaphore(max_connections)
        self.connection_times = []

    async def execute_subprocess(
        self, cmd: List[str], cwd: str, env: Dict[str, str], timeout: float
    ) -> Tuple[int, str, str]:
        """Execute subprocess with connection pooling"""
        async with self.connection_semaphore:
            self.active_connections += 1
            start_time = time.time()

            try:
                # Run in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(self.executor, self._run_subprocess, cmd, cwd, env, timeout)

                execution_time = time.time() - start_time
                self.connection_times.append(execution_time)

                return result

            finally:
                self.active_connections -= 1

    def _run_subprocess(self, cmd: List[str], cwd: str, env: Dict[str, str], timeout: float) -> Tuple[int, str, str]:
        """Run subprocess in thread"""
        import subprocess

        try:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout expired"
        except Exception as e:
            return -1, "", str(e)

    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        if not self.connection_times:
            avg_time = 0
        else:
            avg_time = sum(self.connection_times) / len(self.connection_times)

        return {
            "active_connections": self.active_connections,
            "max_connections": self.max_connections,
            "max_workers": self.max_workers,
            "avg_connection_time": avg_time,
            "total_connections": len(self.connection_times),
        }


class MemoryOptimizer:
    """Memory usage optimization for context integration"""

    def __init__(self):
        """Initialize memory optimizer"""
        self.process = psutil.Process()
        self.memory_threshold_mb = 500  # 500MB threshold
        self.gc_threshold = 0.8  # 80% memory usage triggers GC

    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        memory_info = self.process.memory_info()
        return {
            "rss_mb": memory_info.rss / (1024 * 1024),  # Resident Set Size
            "vms_mb": memory_info.vms / (1024 * 1024),  # Virtual Memory Size
            "percent": self.process.memory_percent(),
        }

    def should_optimize(self) -> bool:
        """Check if memory optimization is needed"""
        memory_usage = self.get_memory_usage()
        return memory_usage["rss_mb"] > self.memory_threshold_mb or memory_usage["percent"] > self.gc_threshold * 100

    def optimize_memory(self) -> Dict[str, Any]:
        """Perform memory optimization"""
        import gc

        # Force garbage collection
        collected = gc.collect()

        # Get memory before and after
        before = self.get_memory_usage()

        # Additional optimization: clear Python's internal caches
        if hasattr(gc, "garbage"):
            gc.garbage.clear()

        after = self.get_memory_usage()

        optimization_result = {
            "objects_collected": collected,
            "memory_freed_mb": before["rss_mb"] - after["rss_mb"],
            "before_mb": before["rss_mb"],
            "after_mb": after["rss_mb"],
        }

        _LOG.info(f"Memory optimization: freed {optimization_result['memory_freed_mb']:.2f}MB")
        return optimization_result


class LoadBalancer:
    """Load balancer for multiple memory rehydrator instances"""

    def __init__(self, instances: List[str] = None):
        """
        Initialize load balancer.

        Args:
            instances: List of memory rehydrator instance URLs/commands
        """
        self.instances = instances or ["scripts/cursor_memory_rehydrate.py"]
        self.instance_weights = {instance: 1.0 for instance in self.instances}
        self.instance_stats = {instance: {"requests": 0, "errors": 0, "avg_time": 0.0} for instance in self.instances}
        self.current_index = 0

    def select_instance(self, role: str, task: str) -> str:
        """Select best instance based on load balancing strategy"""
        if len(self.instances) == 1:
            return self.instances[0]

        # Round-robin with health checking
        for _ in range(len(self.instances)):
            instance = self.instances[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.instances)

            # Check if instance is healthy (low error rate)
            stats = self.instance_stats[instance]
            if stats["requests"] == 0 or stats["errors"] / stats["requests"] < 0.3:
                return instance

        # Fallback to first instance
        return self.instances[0]

    def update_stats(self, instance: str, success: bool, response_time: float):
        """Update instance statistics"""
        if instance not in self.instance_stats:
            return

        stats = self.instance_stats[instance]
        stats["requests"] += 1

        if not success:
            stats["errors"] += 1

        # Update average time
        if stats["requests"] == 1:
            stats["avg_time"] = response_time
        else:
            stats["avg_time"] = (stats["avg_time"] * (stats["requests"] - 1) + response_time) / stats["requests"]

    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        return {
            "instances": len(self.instances),
            "instance_stats": self.instance_stats,
            "total_requests": sum(stats["requests"] for stats in self.instance_stats.values()),
            "total_errors": sum(stats["errors"] for stats in self.instance_stats.values()),
        }


class PerformanceOptimizer:
    """Main performance optimizer that coordinates all optimizations"""

    def __init__(self, cache_size: int = 1000, max_memory_mb: int = 100, max_workers: int = 4):
        """
        Initialize performance optimizer.

        Args:
            cache_size: Maximum cache entries
            max_memory_mb: Maximum cache memory usage
            max_workers: Maximum worker threads
        """
        self.cache = LRUCache(cache_size, max_memory_mb)
        self.connection_pool = ConnectionPool(max_workers)
        self.memory_optimizer = MemoryOptimizer()
        self.load_balancer = LoadBalancer()
        self.optimization_enabled = True

    def get_context_hash(self, role: str, task: str) -> str:
        """Generate hash for context caching"""
        content = f"{role}:{task}"
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    async def get_optimized_context(self, role: str, task: str) -> str:
        """Get context with all performance optimizations"""
        start_time = time.time()

        # Check memory optimization
        if self.memory_optimizer.should_optimize():
            self.memory_optimizer.optimize_memory()

        # Generate cache key
        cache_key = self.get_context_hash(role, task)

        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            _LOG.info(f"Cache hit for role {role}")
            return cached_result

        # Select best instance
        instance = self.load_balancer.select_instance(role, task)

        # Execute with connection pooling
        try:
            import sys

            cmd = [sys.executable, instance, role, task, "--stability", "0.4"]
            current_dir = os.getcwd()
            project_root = os.path.join(current_dir, "..")
            env = os.environ.copy()
            env["REHYDRATE_FAST"] = "1"

            returncode, stdout, stderr = await self.connection_pool.execute_subprocess(
                cmd, project_root, env, timeout=10.0
            )

            response_time = time.time() - start_time

            # Update load balancer stats
            self.load_balancer.update_stats(instance, returncode == 0, response_time)

            if returncode == 0:
                # Parse and cache result
                context = self._parse_context_output(stdout)
                self.cache.put(cache_key, context, role, task)
                return context
            else:
                _LOG.error(f"Context retrieval failed: {stderr}")
                return self._get_fallback_context(role, task)

        except Exception as e:
            _LOG.error(f"Context retrieval error: {e}")
            return self._get_fallback_context(role, task)

    def _parse_context_output(self, output: str) -> str:
        """Parse context from memory rehydrator output"""
        if "MEMORY REHYDRATION BUNDLE" in output:
            start_marker = "================================================================================\n🧠 MEMORY REHYDRATION BUNDLE\n================================================================================\nCopy the content below into your Cursor conversation:\n================================================================================\n"
            end_marker = "\n================================================================================\n📊 Bundle Statistics:"

            start_idx = output.find(start_marker)
            if start_idx != -1:
                start_idx += len(start_marker)
                end_idx = output.find(end_marker, start_idx)
                if end_idx != -1:
                    return output[start_idx:end_idx].strip()

        return "PROJECT CONTEXT: No context available"

    def _get_fallback_context(self, role: str, task: str) -> str:
        """Get fallback context when retrieval fails"""
        return f"PROJECT CONTEXT (FALLBACK): You are a {role} working on an AI development project."

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        return {
            "cache": self.cache.get_stats(),
            "connection_pool": self.connection_pool.get_stats(),
            "memory": self.memory_optimizer.get_memory_usage(),
            "load_balancer": self.load_balancer.get_stats(),
            "optimization_enabled": self.optimization_enabled,
        }

    def enable_optimization(self, enabled: bool = True):
        """Enable or disable performance optimization"""
        self.optimization_enabled = enabled
        _LOG.info(f"Performance optimization {'enabled' if enabled else 'disabled'}")


# Global performance optimizer instance
_performance_optimizer = None


def get_performance_optimizer() -> PerformanceOptimizer:
    """Get global performance optimizer instance"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer


async def get_optimized_context(role: str, task: str) -> str:
    """Get context with performance optimization"""
    optimizer = get_performance_optimizer()
    return await optimizer.get_optimized_context(role, task)


def get_performance_stats() -> Dict[str, Any]:
    """Get performance statistics"""
    optimizer = get_performance_optimizer()
    return optimizer.get_performance_stats()


if __name__ == "__main__":
    # Example usage
    import asyncio

    async def test_performance():
        optimizer = get_performance_optimizer()

        # Test context retrieval
        context = await optimizer.get_optimized_context("coder", "test task")
        print(f"Context: {context[:100]}...")

        # Get stats
        stats = optimizer.get_performance_stats()
        print(json.dumps(stats, indent=2))

    asyncio.run(test_performance())
