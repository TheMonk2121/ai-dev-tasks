#!/usr/bin/env python3
"""
Test script to verify decision extraction functionality
"""


import requests


def test_decision_extraction():
    """Test decision extraction from conversations"""

    print("🧪 Testing Decision Extraction...")

    # Test conversation turns with decisions
    test_conversations = [
        {
            "session_id": "test_session_1",
            "role": "user",
            "text": "I think we should use PostgreSQL with pgvector for our vector search needs. It's definitely the best approach for our RAG system.",
        },
        {
            "session_id": "test_session_2",
            "role": "assistant",
            "text": "Let's implement the MCP server for Cursor integration. I recommend using FastAPI for the HTTP endpoints.",
        },
        {
            "session_id": "test_session_3",
            "role": "user",
            "text": "We'll go with Python 3.12 for this project. It has better performance than Python 3.11.",
        },
        {
            "session_id": "test_session_4",
            "role": "assistant",
            "text": "For the database schema, we should choose a normalized approach over denormalized. It will be more maintainable.",
        },
    ]

    # Test decision extraction for each conversation
    for i, conv in enumerate(test_conversations, 1):
        print(f"\n📝 Testing conversation {i}:")
        print(f"   Session: {conv['session_id']}")
        print(f"   Role: {conv['role']}")
        print(f"   Text: {conv['text'][:100]}...")

        # Call capture_turn to extract decisions
        response = requests.post(
            "http://localhost:3000/mcp/tools/call",
            json={
                "name": "capture_turn",
                "arguments": {"session_id": conv["session_id"], "role": conv["role"], "text": conv["text"]},
            },
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Capture successful: {result.get('message', 'OK')}")
        else:
            print(f"   ❌ Capture failed: {response.status_code} - {response.text}")

    # Test decision search
    print("\n🔍 Testing decision search...")

    search_queries = ["postgresql", "python", "database", "MCP"]

    for query in search_queries:
        print(f"\n   Searching for: '{query}'")

        response = requests.post(
            "http://localhost:3000/mcp/tools/call",
            json={"name": "search_decisions", "arguments": {"query": query, "limit": 5}},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            result = response.json()
            decisions = result.get("decisions", [])
            print(f"   ✅ Found {len(decisions)} decisions")

            for j, decision in enumerate(decisions, 1):
                print(f"      {j}. {decision.get('head', 'N/A')[:60]}...")
                print(f"         Confidence: {decision.get('confidence', 0):.2f}")
        else:
            print(f"   ❌ Search failed: {response.status_code} - {response.text}")

    print("\n🎉 Decision extraction test completed!")


if __name__ == "__main__":
    test_decision_extraction()
