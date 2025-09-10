#!/usr/bin/env python3
"""
Test Multi-Agent Chat System
"""

import asyncio
import json
import time
from pathlib import Path

import websockets


async def demo_agent_connection(agent_name: str, chat_url: str = "ws://localhost:8004"):
    """Test connecting an agent to the chat system"""
    try:
        websocket_url = f"{chat_url}/ws/{agent_name}"
        async with websockets.connect(websocket_url) as websocket:
            print(f"✅ {agent_name} connected successfully")

            # Send a test message
            test_message = {
                "message": f"Hello from {agent_name}! Testing multi-agent communication.",
                "type": "chat",
                "priority": "normal",
                "metadata": {"test": True},
            }

            await websocket.send(json.dumps(test_message))
            print(f"📤 {agent_name} sent test message")

            # Listen for a few seconds
            try:
                async for message in websocket:
                    data = json.loads(message)
                    print(f"📥 {agent_name} received: {data.get('message', '')[:50]}...")
                    break  # Just get one message for testing
            except asyncio.TimeoutError:
                print(f"⏰ {agent_name} timeout waiting for response")

            return True

    except Exception as e:
        print(f"❌ {agent_name} connection failed: {e}")
        return False


async def demo_chat_system():
    """Test the multi-agent chat system"""
    print("🧪 Testing Multi-Agent Chat System")
    print("=" * 50)

    # Test agents
    test_agents = ["cursor", "codex", "dspy_planner", "dspy_implementer", "dspy_researcher"]

    results = {}

    for agent in test_agents:
        print(f"\n🔌 Testing {agent}...")
        success = await demo_agent_connection(agent)
        results[agent] = success
        await asyncio.sleep(1)  # Small delay between tests

    print("\n📊 Test Results:")
    print("-" * 30)
    for agent, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{agent}: {status}")

    total_tests = len(results)
    passed_tests = sum(results.values())

    print(f"\n🎯 Summary: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🎉 All tests passed! Multi-agent chat system is working!")
    else:
        print("⚠️  Some tests failed. Check the chat bridge server.")


async def demo_http_endpoints():
    """Test HTTP endpoints"""
    import aiohttp

    print("\n🌐 Testing HTTP Endpoints")
    print("-" * 30)

    endpoints = [
        "http://localhost:8004/",
        "http://localhost:8004/health",
        "http://localhost:8004/agents",
        "http://localhost:8004/status",
        "http://localhost:8004/chat/rooms",
    ]

    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {endpoint}: {response.status}")
                        if endpoint.endswith("/agents"):
                            print(f"   📋 Available agents: {len(data.get('agents', {}))}")
                    else:
                        print(f"❌ {endpoint}: {response.status}")
            except Exception as e:
                print(f"❌ {endpoint}: {e}")


def main():
    """Main test function"""
    print("🚀 Multi-Agent Chat System Test Suite")
    print("=" * 50)

    # Check if chat bridge is running
    try:
        import requests

        response = requests.get("http://localhost:8004/health", timeout=5)
        if response.status_code == 200:
            print("✅ Chat bridge server is running")
        else:
            print("❌ Chat bridge server not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to chat bridge: {e}")
        print("💡 Make sure to start the chat bridge first:")
        print("   python3 scripts/multi_agent_chat.py")
        return

    # Run tests
    asyncio.run(demo_chat_system())
    asyncio.run(demo_http_endpoints())


if __name__ == "__main__":
    main()
