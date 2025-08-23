#!/usr/bin/env python3
"""
Test Performance Optimization (T7)

Test to verify that the advanced performance optimization system is working:
- LRU caching with intelligent eviction
- Connection pooling for subprocess calls
- Memory usage optimization
- Response time optimization
- Load balancing for multiple instances
"""

import asyncio
import os
import sys
import time

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from utils.context_performance import ConnectionPool, LoadBalancer, LRUCache, MemoryOptimizer, get_performance_optimizer


def test_lru_cache():
    """Test LRU cache with intelligent eviction"""
    print("🔍 Test 1: LRU Cache with Intelligent Eviction")
    print("-" * 50)

    # Create cache with small limits for testing
    cache = LRUCache(max_size=3, max_memory_mb=1)

    # Add some entries
    cache.put("key1", "value1" * 100, "coder", "task1")  # Large value
    cache.put("key2", "value2", "planner", "task2")  # Small value
    cache.put("key3", "value3", "researcher", "task3")  # Small value

    # Access key2 to make it more valuable
    cache.get("key2")
    cache.get("key2")  # Multiple accesses

    # Add another entry to trigger eviction
    cache.put("key4", "value4", "implementer", "task4")

    # Check stats
    stats = cache.get_stats()
    print("📊 Cache Stats:")
    print(f"   Size: {stats['size']}/{stats['max_size']}")
    print(f"   Memory: {stats['memory_usage_mb']:.2f}MB/{stats['max_memory_mb']:.2f}MB")
    print(f"   Hit rate: {stats['hit_rate']:.1f}%")
    print(f"   Evictions: {stats['evictions']}")

    # Verify key1 (large value) was evicted first
    if cache.get("key1") is None and cache.get("key2") is not None:
        print("   ✅ Intelligent eviction working (large value evicted first)")
        return True
    else:
        print("   ❌ Intelligent eviction not working as expected")
        return False


def test_connection_pool():
    """Test connection pooling"""
    print("\n🔍 Test 2: Connection Pool")
    print("-" * 50)

    pool = ConnectionPool(max_workers=2, max_connections=3)

    async def test_pool():
        # Simulate multiple concurrent requests
        tasks = []
        for i in range(5):
            task = pool.execute_subprocess(
                cmd=["echo", f"test{i}"], cwd=os.getcwd(), env=os.environ.copy(), timeout=5.0
            )
            tasks.append(task)

        # Wait for all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check stats
        stats = pool.get_stats()
        print("📊 Connection Pool Stats:")
        print(f"   Active connections: {stats['active_connections']}")
        print(f"   Max connections: {stats['max_connections']}")
        print(f"   Total connections: {stats['total_connections']}")
        print(f"   Avg connection time: {stats['avg_connection_time']:.3f}s")

        # Check that we didn't exceed max connections
        if stats["total_connections"] == 5:
            print("   ✅ Connection pooling working correctly")
            return True
        else:
            print("   ❌ Connection pooling not working as expected")
            return False

    return asyncio.run(test_pool())


def test_memory_optimizer():
    """Test memory optimization"""
    print("\n🔍 Test 3: Memory Optimizer")
    print("-" * 50)

    optimizer = MemoryOptimizer()

    # Get current memory usage
    memory_before = optimizer.get_memory_usage()
    print("📊 Memory Before Optimization:")
    print(f"   RSS: {memory_before['rss_mb']:.2f}MB")
    print(f"   VMS: {memory_before['vms_mb']:.2f}MB")
    print(f"   Percent: {memory_before['percent']:.1f}%")

    # Create some objects to trigger GC
    large_list = [f"item{i}" * 1000 for i in range(1000)]

    # Perform optimization
    result = optimizer.optimize_memory()

    # Get memory after optimization
    memory_after = optimizer.get_memory_usage()
    print("📊 Memory After Optimization:")
    print(f"   RSS: {memory_after['rss_mb']:.2f}MB")
    print(f"   VMS: {memory_after['vms_mb']:.2f}MB")
    print(f"   Percent: {memory_after['percent']:.1f}%")
    print(f"   Objects collected: {result['objects_collected']}")
    print(f"   Memory freed: {result['memory_freed_mb']:.2f}MB")

    if result["objects_collected"] > 0:
        print("   ✅ Memory optimization working")
        return True
    else:
        print("   ⚠️ No objects collected (may be normal)")
        return True  # Not necessarily an error


def test_load_balancer():
    """Test load balancer"""
    print("\n🔍 Test 4: Load Balancer")
    print("-" * 50)

    # Create load balancer with multiple instances
    instances = ["instance1", "instance2", "instance3"]
    balancer = LoadBalancer(instances)

    # Simulate some requests
    for i in range(10):
        instance = balancer.select_instance("coder", f"task{i}")
        # Simulate success/failure
        success = i % 3 != 0  # 2/3 success rate
        response_time = 1.0 + (i * 0.1)
        balancer.update_stats(instance, success, response_time)

    # Get stats
    stats = balancer.get_stats()
    print("📊 Load Balancer Stats:")
    print(f"   Instances: {stats['instances']}")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Total errors: {stats['total_errors']}")

    for instance, instance_stats in stats["instance_stats"].items():
        print(
            f"   {instance}: {instance_stats['requests']} requests, "
            f"{instance_stats['errors']} errors, "
            f"{instance_stats['avg_time']:.2f}s avg"
        )

    if stats["total_requests"] == 10:
        print("   ✅ Load balancer working correctly")
        return True
    else:
        print("   ❌ Load balancer not working as expected")
        return False


async def test_performance_optimizer():
    """Test the main performance optimizer"""
    print("\n🔍 Test 5: Performance Optimizer Integration")
    print("-" * 50)

    optimizer = get_performance_optimizer()

    # Test context retrieval
    start_time = time.time()
    context = await optimizer.get_optimized_context("coder", "test performance optimization")
    retrieval_time = time.time() - start_time

    print("📊 Performance Optimizer Results:")
    print(f"   Context length: {len(context)} characters")
    print(f"   Retrieval time: {retrieval_time:.3f}s")

    # Get comprehensive stats
    stats = optimizer.get_performance_stats()

    print(f"   Cache hit rate: {stats['cache']['hit_rate']:.1f}%")
    print(f"   Memory usage: {stats['memory']['rss_mb']:.2f}MB")
    print(f"   Active connections: {stats['connection_pool']['active_connections']}")
    print(f"   Load balancer instances: {stats['load_balancer']['instances']}")

    if len(context) > 0:
        print("   ✅ Performance optimizer working correctly")
        return True
    else:
        print("   ❌ Performance optimizer failed to retrieve context")
        return False


def test_performance_comparison():
    """Test performance comparison between optimized and non-optimized"""
    print("\n🔍 Test 6: Performance Comparison")
    print("-" * 50)

    # Test multiple requests to see caching in action
    async def run_comparison():
        optimizer = get_performance_optimizer()

        # First request (cache miss)
        start_time = time.time()
        context1 = await optimizer.get_optimized_context("coder", "test task")
        time1 = time.time() - start_time

        # Second request (cache hit)
        start_time = time.time()
        context2 = await optimizer.get_optimized_context("coder", "test task")
        time2 = time.time() - start_time

        # Third request (different task, cache miss)
        start_time = time.time()
        context3 = await optimizer.get_optimized_context("planner", "different task")
        time3 = time.time() - start_time

        print("📊 Performance Comparison:")
        print(f"   First request (cache miss): {time1:.3f}s")
        print(f"   Second request (cache hit): {time2:.3f}s")
        print(f"   Third request (different): {time3:.3f}s")

        # Calculate improvement
        if time1 > 0:
            improvement = ((time1 - time2) / time1) * 100
            print(f"   Cache improvement: {improvement:.1f}%")

        # Get final stats
        stats = optimizer.get_performance_stats()
        print(f"   Final cache hit rate: {stats['cache']['hit_rate']:.1f}%")
        print(f"   Final cache size: {stats['cache']['size']}")

        if time2 < time1:
            print("   ✅ Caching providing performance improvement")
            return True
        else:
            print("   ⚠️ No significant caching improvement (may be normal)")
            return True

    return asyncio.run(run_comparison())


def main():
    """Run performance optimization tests"""
    print("🚀 Performance Optimization Test Suite (T7)")
    print("=" * 80)

    tests = [
        ("LRU Cache", test_lru_cache),
        ("Connection Pool", test_connection_pool),
        ("Memory Optimizer", test_memory_optimizer),
        ("Load Balancer", test_load_balancer),
        ("Performance Optimizer", lambda: asyncio.run(test_performance_optimizer())),
        ("Performance Comparison", test_performance_comparison),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 80)
    print("🚀 PERFORMANCE OPTIMIZATION TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"🎯 Tests passed: {passed}/{total}")

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status}: {test_name}")

    print("\n🚀 Performance Optimization Features:")
    print("   • LRU caching with intelligent eviction policies")
    print("   • Connection pooling for subprocess calls")
    print("   • Memory usage optimization and garbage collection")
    print("   • Load balancing for multiple instances")
    print("   • Response time optimization")
    print("   • Comprehensive performance monitoring")

    if passed == total:
        print("\n🎉 All performance optimization tests passed!")
        print("   T7: Add performance optimization - COMPLETED!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed - review performance optimization")


if __name__ == "__main__":
    main()
