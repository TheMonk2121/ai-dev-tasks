#!/usr/bin/env python3
"""
Test script to verify thread isolation in MCP memory system.
"""

import asyncio
import time
import uuid
from typing import Any

import httpx


async def test_thread_isolation_detailed():
    """Test detailed thread isolation with database verification."""
    print("🔍 Testing detailed thread isolation in MCP memory system...")

    base_url = "http://localhost:8000"

    # Create two distinct threads
    thread1_id = f"isolation_test_1_{uuid.uuid4().hex[:8]}"
    thread2_id = f"isolation_test_2_{uuid.uuid4().hex[:8]}"

    print(f"Thread 1 ID: {thread1_id}")
    print(f"Thread 2 ID: {thread2_id}")

    async with httpx.AsyncClient() as client:
        # Capture queries in both threads
        print("\n📝 Capturing queries in both threads...")

        # Thread 1 queries
        thread1_queries = [
            "What is the project structure?",
            "How does the memory system work?",
            "What are the main components?",
        ]

        # Thread 2 queries
        thread2_queries = ["How do I run tests?", "What is the database schema?", "How do I deploy the system?"]

        # Capture Thread 1 queries
        thread1_turn_ids = []
        for i, query in enumerate(thread1_queries):
            response = await client.post(
                f"{base_url}/mcp/tools/call",
                json={
                    "tool_name": "capture_user_query",
                    "arguments": {
                        "thread_id": thread1_id,
                        "query": query,
                        "metadata": {"test": "isolation", "thread": 1, "query_index": i + 1},
                    },
                },
            )

            if response.status_code == 200:
                turn_id = response.json().get("data", {}).get("turn_id")
                thread1_turn_ids.append(turn_id)
                print(f"   ✅ Thread 1 Query {i+1}: {turn_id}")
            else:
                print(f"   ❌ Thread 1 Query {i+1}: Failed - {response.status_code}")

        # Capture Thread 2 queries
        thread2_turn_ids = []
        for i, query in enumerate(thread2_queries):
            response = await client.post(
                f"{base_url}/mcp/tools/call",
                json={
                    "tool_name": "capture_user_query",
                    "arguments": {
                        "thread_id": thread2_id,
                        "query": query,
                        "metadata": {"test": "isolation", "thread": 2, "query_index": i + 1},
                    },
                },
            )

            if response.status_code == 200:
                turn_id = response.json().get("data", {}).get("turn_id")
                thread2_turn_ids.append(turn_id)
                print(f"   ✅ Thread 2 Query {i+1}: {turn_id}")
            else:
                print(f"   ❌ Thread 2 Query {i+1}: Failed - {response.status_code}")

        # Capture AI responses for both threads
        print("\n🤖 Capturing AI responses...")

        # Thread 1 responses
        for i, turn_id in enumerate(thread1_turn_ids):
            response = await client.post(
                f"{base_url}/mcp/tools/call",
                json={
                    "tool_name": "capture_ai_response",
                    "arguments": {
                        "thread_id": thread1_id,
                        "response": f"AI response to Thread 1 query {i+1}",
                        "query_turn_id": turn_id,
                        "metadata": {"test": "isolation", "thread": 1, "response_index": i + 1},
                    },
                },
            )

            if response.status_code == 200:
                print(f"   ✅ Thread 1 Response {i+1}: {response.json().get('data', {}).get('turn_id')}")
            else:
                print(f"   ❌ Thread 1 Response {i+1}: Failed - {response.status_code}")

        # Thread 2 responses
        for i, turn_id in enumerate(thread2_turn_ids):
            response = await client.post(
                f"{base_url}/mcp/tools/call",
                json={
                    "tool_name": "capture_ai_response",
                    "arguments": {
                        "thread_id": thread2_id,
                        "response": f"AI response to Thread 2 query {i+1}",
                        "query_turn_id": turn_id,
                        "metadata": {"test": "isolation", "thread": 2, "response_index": i + 1},
                    },
                },
            )

            if response.status_code == 200:
                print(f"   ✅ Thread 2 Response {i+1}: {response.json().get('data', {}).get('turn_id')}")
            else:
                print(f"   ❌ Thread 2 Response {i+1}: Failed - {response.status_code}")

        # Get stats for both threads
        print("\n📊 Getting thread statistics...")

        stats1 = await client.post(
            f"{base_url}/mcp/tools/call",
            json={"tool_name": "get_session_stats", "arguments": {"thread_id": thread1_id}},
        )

        stats2 = await client.post(
            f"{base_url}/mcp/tools/call",
            json={"tool_name": "get_session_stats", "arguments": {"thread_id": thread2_id}},
        )

        if stats1.status_code == 200 and stats2.status_code == 200:
            data1 = stats1.json().get("data", {}).get("stats", {})
            data2 = stats2.json().get("data", {}).get("stats", {})

            print(f"   Thread 1 stats: {data1}")
            print(f"   Thread 2 stats: {data2}")

            # Verify isolation
            thread1_messages = data1.get("message_count", 0)
            thread2_messages = data2.get("message_count", 0)

            print("\n🔍 Isolation Verification:")
            print(f"   Thread 1 messages: {thread1_messages}")
            print(f"   Thread 2 messages: {thread2_messages}")

            if thread1_messages == 6 and thread2_messages == 6:  # 3 queries + 3 responses each
                print("   ✅ Thread isolation working correctly - each thread has its own message count")
            else:
                print("   ❌ Thread isolation may have issues - unexpected message counts")

            # Check if threads have different session IDs
            session1 = data1.get("session_id")
            session2 = data2.get("session_id")
            thread_id1 = data1.get("thread_id")
            thread_id2 = data2.get("thread_id")

            print("\n🔍 Thread Identity Verification:")
            print(f"   Thread 1: session={session1}, thread_id={thread_id1}")
            print(f"   Thread 2: session={session2}, thread_id={thread_id2}")

            if thread_id1 == thread1_id and thread_id2 == thread2_id:
                print("   ✅ Thread IDs match expected values")
            else:
                print("   ❌ Thread ID mismatch")

        else:
            print(f"   ❌ Failed to get thread stats: {stats1.status_code}, {stats2.status_code}")


async def test_concurrent_capture() -> dict[str, int | float]:
    """Test concurrent capture from multiple threads simultaneously."""
    print("\n🚀 Testing concurrent capture from multiple threads...")

    base_url = "http://localhost:8000"
    num_threads = 3
    queries_per_thread = 2

    async def capture_thread_queries(thread_id: str, queries: list[str]) -> dict[str, Any]:
        """Capture queries for a single thread."""
        results = []

        async with httpx.AsyncClient() as client:
            for i, query in enumerate(queries):
                # Capture user query
                user_response = await client.post(
                    f"{base_url}/mcp/tools/call",
                    json={
                        "tool_name": "capture_user_query",
                        "arguments": {
                            "thread_id": thread_id,
                            "query": f"{query} (concurrent test)",
                            "metadata": {"test": "concurrent", "thread_id": thread_id, "query_index": i + 1},
                        },
                    },
                )

                if user_response.status_code == 200:
                    turn_id = user_response.json().get("data", {}).get("turn_id")

                    # Capture AI response
                    ai_response = await client.post(
                        f"{base_url}/mcp/tools/call",
                        json={
                            "tool_name": "capture_ai_response",
                            "arguments": {
                                "thread_id": thread_id,
                                "response": f"AI response to: {query}",
                                "query_turn_id": turn_id,
                                "metadata": {"test": "concurrent", "thread_id": thread_id, "response_index": i + 1},
                            },
                        },
                    )

                    results.append(
                        {
                            "query_index": i + 1,
                            "user_success": user_response.status_code == 200,
                            "ai_success": ai_response.status_code == 200,
                            "user_turn_id": turn_id,
                            "ai_turn_id": (
                                ai_response.json().get("data", {}).get("turn_id")
                                if ai_response.status_code == 200
                                else None
                            ),
                        }
                    )
                else:
                    results.append(
                        {
                            "query_index": i + 1,
                            "user_success": False,
                            "ai_success": False,
                            "error": f"User query failed: {user_response.status_code}",
                        }
                    )

        return {
            "thread_id": thread_id,
            "results": results,
            "successful": sum(1 for r in results if r.get("user_success") and r.get("ai_success")),
            "total": len(queries),
        }

    # Create concurrent tasks
    tasks = []
    test_queries = [
        "What is the project structure?",
        "How does the memory system work?",
        "What are the main components?",
        "How do I run tests?",
        "What is the database schema?",
        "How do I deploy the system?",
    ]

    for i in range(num_threads):
        thread_id = f"concurrent_test_{i+1}_{uuid.uuid4().hex[:8]}"
        queries = test_queries[i * queries_per_thread : (i + 1) * queries_per_thread]
        tasks.append(capture_thread_queries(thread_id, queries))

    print(f"   Starting {num_threads} concurrent threads...")
    start_time = time.time()

    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()
    duration = end_time - start_time

    # Analyze results
    print(f"\n📊 Concurrent Test Results (Duration: {duration:.2f}s):")
    print("=" * 60)

    total_queries = 0
    successful_queries = 0

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ Thread {i+1} failed with exception: {result}")
            continue

        # Type guard: result is now guaranteed to be a dict
        if not isinstance(result, dict):
            print(f"❌ Thread {i+1} returned unexpected type: {type(result)}")
            continue

        thread_id = result["thread_id"]
        successful = result["successful"]
        total = result["total"]
        total_queries += total
        successful_queries += successful

        print(f"🧵 Thread {i+1} ({thread_id}):")
        print(f"   Queries: {successful}/{total} successful")

        # Show turn IDs for verification
        for j, query_result in enumerate(result["results"]):
            if query_result.get("user_success") and query_result.get("ai_success"):
                print(f"   ✅ Query {j+1}: {query_result.get('user_turn_id')} -> {query_result.get('ai_turn_id')}")
            else:
                print(f"   ❌ Query {j+1}: Failed")

        print()

    print("=" * 60)
    print("📈 Summary:")
    print(f"   Total threads: {num_threads}")
    print(f"   Total queries: {total_queries}")
    print(f"   Successful queries: {successful_queries}")
    print(
        f"   Success rate: {(successful_queries/total_queries*100):.1f}%"
        if total_queries > 0
        else "   Success rate: N/A"
    )
    print(f"   Duration: {duration:.2f}s")
    print(f"   Queries/second: {total_queries/duration:.1f}" if duration > 0 else "   Queries/second: N/A")

    return {
        "total_threads": num_threads,
        "total_queries": total_queries,
        "successful_queries": successful_queries,
        "duration": duration,
        "success_rate": successful_queries / total_queries if total_queries > 0 else 0,
    }


if __name__ == "__main__":
    print("🔍 MCP Memory System Thread Isolation Test")
    print("=" * 50)
    print("Make sure the MCP server is running on localhost:8000")
    print()

    try:
        asyncio.run(test_thread_isolation_detailed())
        _ = asyncio.run(test_concurrent_capture())

        print("\n🎉 Thread isolation test completed!")

    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
