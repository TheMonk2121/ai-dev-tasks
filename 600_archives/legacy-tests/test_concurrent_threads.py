#!/usr/bin/env python3
"""
Test script to verify concurrent thread handling in MCP memory system.
"""

import asyncio
import time
import uuid
from typing import Any

import httpx


async def test_concurrent_threads() -> dict[str, int | float]:
    """Test concurrent thread handling in MCP memory system."""
    print("🧪 Testing concurrent thread handling in MCP memory system...")

    # Test parameters
    base_url = "http://localhost:8000"
    num_threads = 5
    queries_per_thread = 3

    async def simulate_thread_with_delay(thread_id: str, queries: list[str], delay: float) -> dict[str, Any]:
        """Simulate a thread with a startup delay."""
        if delay > 0:
            await asyncio.sleep(delay)
        return await simulate_thread(thread_id, queries)

    async def simulate_thread(thread_id: str, queries: list[str]) -> dict[str, Any]:
        """Simulate a thread with multiple queries."""
        results = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            for i, query in enumerate(queries):
                try:
                    # Add small delay for first query to allow DB initialization
                    if i == 0:
                        await asyncio.sleep(0.2)
                    # Test capture_user_query
                    user_response = await client.post(
                        f"{base_url}/mcp/tools/call",
                        json={
                            "tool_name": "capture_user_query",
                            "arguments": {
                                "thread_id": thread_id,
                                "query": f"{query} (thread {thread_id}, query {i+1})",
                                "metadata": {"test": True, "thread_id": thread_id, "query_index": i + 1},
                            },
                        },
                    )

                    # Test capture_ai_response
                    ai_response = await client.post(
                        f"{base_url}/mcp/tools/call",
                        json={
                            "tool_name": "capture_ai_response",
                            "arguments": {
                                "thread_id": thread_id,
                                "response": f"AI response to: {query} (thread {thread_id})",
                                "query_turn_id": user_response.json().get("data", {}).get("turn_id"),
                                "metadata": {"test": True, "thread_id": thread_id, "response_index": i + 1},
                            },
                        },
                    )

                    # Test get_conversation_stats
                    stats_response = await client.post(
                        f"{base_url}/mcp/tools/call",
                        json={"tool_name": "get_conversation_stats", "arguments": {"thread_id": thread_id}},
                    )

                    # Check for HTTP errors
                    if user_response.status_code != 200:
                        print(
                            f"   ❌ Thread {thread_id} Query {i+1} User HTTP {user_response.status_code}: {user_response.text}"
                        )
                    if ai_response.status_code != 200:
                        print(
                            f"   ❌ Thread {thread_id} Query {i+1} AI HTTP {ai_response.status_code}: {ai_response.text}"
                        )
                    if stats_response.status_code != 200:
                        print(
                            f"   ❌ Thread {thread_id} Query {i+1} Stats HTTP {stats_response.status_code}: {stats_response.text}"
                        )

                    results.append(
                        {
                            "thread_id": thread_id,
                            "query_index": i + 1,
                            "user_success": user_response.status_code == 200,
                            "ai_success": ai_response.status_code == 200,
                            "stats_success": stats_response.status_code == 200,
                            "user_turn_id": user_response.json().get("data", {}).get("turn_id"),
                            "ai_turn_id": ai_response.json().get("data", {}).get("turn_id"),
                            "stats": stats_response.json().get("data", {}).get("stats", {}),
                        }
                    )

                    # Small delay between queries
                    await asyncio.sleep(0.1)

                except Exception as e:
                    error_msg = str(e) if str(e) else f"Unknown error: {type(e).__name__}"
                    print(f"   ❌ Thread {thread_id} Query {i+1} Exception: {error_msg}")
                    results.append({"thread_id": thread_id, "query_index": i + 1, "error": error_msg, "success": False})

        return {
            "thread_id": thread_id,
            "results": results,
            "total_queries": len(queries),
            "successful_queries": sum(
                1 for r in results if r.get("user_success", False) and r.get("ai_success", False)
            ),
        }

    # Generate test data
    test_queries = [
        "What is the current project status?",
        "How does the memory system work?",
        "Can you explain the database schema?",
        "What are the main components?",
        "How do I use the MCP server?",
    ]

    # Create tasks for concurrent execution
    tasks = []
    for i in range(num_threads):
        thread_id = f"test_thread_{i+1}_{uuid.uuid4().hex[:8]}"
        queries = test_queries[:queries_per_thread]  # Each thread gets subset of queries
        # Add small random delay to stagger thread starts
        delay = i * 0.1  # 100ms between each thread start
        tasks.append(simulate_thread_with_delay(thread_id, queries, delay))

    print(f"🚀 Starting {num_threads} concurrent threads with {queries_per_thread} queries each...")
    start_time = time.time()

    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()
    duration = end_time - start_time

    # Analyze results
    print(f"\n📊 Test Results (Duration: {duration:.2f}s):")
    print("=" * 60)

    total_queries = 0
    successful_queries = 0
    failed_threads = 0

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ Thread {i+1} failed with exception: {result}")
            failed_threads += 1
            continue

        # Type guard: result is now guaranteed to be a dict
        if not isinstance(result, dict):
            print(f"❌ Thread {i+1} returned unexpected type: {type(result)}")
            failed_threads += 1
            continue

        thread_id = result["thread_id"]
        total_queries += result["total_queries"]
        successful_queries += result["successful_queries"]

        print(f"🧵 Thread {i+1} ({thread_id}):")
        print(f"   Queries: {result['successful_queries']}/{result['total_queries']} successful")

        # Show some detailed results
        for j, query_result in enumerate(result["results"][:2]):  # Show first 2 queries
            if query_result.get("user_success") and query_result.get("ai_success"):
                print(
                    f"   ✅ Query {j+1}: {query_result.get('user_turn_id', 'N/A')} -> {query_result.get('ai_turn_id', 'N/A')}"
                )
            else:
                print(f"   ❌ Query {j+1}: Failed")

        if len(result["results"]) > 2:
            print(f"   ... and {len(result['results']) - 2} more queries")

        print()

    # Summary
    print("=" * 60)
    print("📈 Summary:")
    print(f"   Total threads: {num_threads}")
    print(f"   Failed threads: {failed_threads}")
    print(f"   Total queries: {total_queries}")
    print(f"   Successful queries: {successful_queries}")
    print(
        f"   Success rate: {(successful_queries/total_queries*100):.1f}%"
        if total_queries > 0
        else "   Success rate: N/A"
    )
    print(f"   Duration: {duration:.2f}s")
    print(f"   Queries/second: {total_queries/duration:.1f}" if duration > 0 else "   Queries/second: N/A")

    # Test thread isolation
    print("\n🔍 Testing thread isolation...")
    await test_thread_isolation()

    return {
        "total_threads": num_threads,
        "failed_threads": failed_threads,
        "total_queries": total_queries,
        "successful_queries": successful_queries,
        "duration": duration,
        "success_rate": successful_queries / total_queries if total_queries > 0 else 0,
    }


async def test_thread_isolation():
    """Test that threads are properly isolated."""
    print("🔍 Testing thread isolation...")

    base_url = "http://localhost:8000"
    thread1_id = f"isolation_test_1_{uuid.uuid4().hex[:8]}"
    thread2_id = f"isolation_test_2_{uuid.uuid4().hex[:8]}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Capture queries in both threads
        _ = await client.post(
            f"{base_url}/mcp/tools/call",
            json={
                "tool_name": "capture_user_query",
                "arguments": {
                    "thread_id": thread1_id,
                    "query": "Thread 1 query",
                    "metadata": {"test": "isolation", "thread": 1},
                },
            },
        )

        _ = await client.post(
            f"{base_url}/mcp/tools/call",
            json={
                "tool_name": "capture_user_query",
                "arguments": {
                    "thread_id": thread2_id,
                    "query": "Thread 2 query",
                    "metadata": {"test": "isolation", "thread": 2},
                },
            },
        )

        # Get stats for both threads
        stats1 = await client.post(
            f"{base_url}/mcp/tools/call",
            json={"tool_name": "get_conversation_stats", "arguments": {"thread_id": thread1_id}},
        )

        stats2 = await client.post(
            f"{base_url}/mcp/tools/call",
            json={"tool_name": "get_conversation_stats", "arguments": {"thread_id": thread2_id}},
        )

        print(f"   Stats1 status: {stats1.status_code}")
        print(f"   Stats2 status: {stats2.status_code}")
        print(f"   Stats1 response: {stats1.json()}")
        print(f"   Stats2 response: {stats2.json()}")

        if stats1.status_code == 200 and stats2.status_code == 200:
            data1 = stats1.json().get("data", {}).get("stats", {})
            data2 = stats2.json().get("data", {}).get("stats", {})

            print(f"   Thread 1 stats: {data1}")
            print(f"   Thread 2 stats: {data2}")
            print(f"   Thread 1 messages: {data1.get('message_count', 0)}")
            print(f"   Thread 2 messages: {data2.get('message_count', 0)}")

            if data1.get("message_count", 0) == 1 and data2.get("message_count", 0) == 1:
                print("   ✅ Thread isolation working correctly")
            else:
                print("   ❌ Thread isolation may have issues")
        else:
            print("   ❌ Failed to get thread stats")


async def test_database_connection_pooling():
    """Test database connection handling under load."""
    print("🔍 Testing database connection handling...")

    base_url = "http://localhost:8000"

    # Test rapid sequential requests
    async with httpx.AsyncClient(timeout=30.0) as client:
        start_time = time.time()

        # Make 10 rapid requests
        tasks = []
        for i in range(10):
            tasks.append(
                client.post(
                    f"{base_url}/mcp/tools/call",
                    json={
                        "tool_name": "capture_user_query",
                        "arguments": {
                            "thread_id": f"rapid_test_{i}",
                            "query": f"Rapid test query {i}",
                            "metadata": {"test": "rapid", "index": i},
                        },
                    },
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        successful = sum(
            1
            for r in results
            if not isinstance(r, Exception) and hasattr(r, "status_code") and getattr(r, "status_code", None) == 200
        )
        print(f"   Rapid requests: {successful}/10 successful in {end_time - start_time:.2f}s")

        if successful == 10:
            print("   ✅ Database connection handling working correctly")
        else:
            print("   ❌ Database connection handling may have issues")


if __name__ == "__main__":
    print("🧪 MCP Memory System Concurrent Thread Test")
    print("=" * 50)
    print("Make sure the MCP server is running on localhost:8000")
    print("Start it with: uv run python scripts/utilities/mcp_memory_server.py")
    print()

    try:
        result = asyncio.run(test_concurrent_threads())
        asyncio.run(test_database_connection_pooling())

        print("\n🎉 Test completed!")
        if result["success_rate"] > 0.9:
            print("✅ Concurrent thread handling is working well!")
        else:
            print("⚠️  Some issues detected with concurrent thread handling")

    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
