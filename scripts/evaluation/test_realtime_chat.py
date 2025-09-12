from __future__ import annotations
import asyncio
import json
import time
import websockets
import os
#!/usr/bin/env python3
"""
Test Real-time Chat Between Agents
"""

async def simulate_cursor_agent():
    """Simulate Cursor agent connecting and chatting"""
    try:
        async with websockets.connect("ws://localhost:8004/ws/cursor") as websocket:
            print("🤖 Cursor Agent connected!")

            # Send a message
            message = {
                "message": "Hello from Cursor! I'm working on the MCP integration.",
                "type": "chat",
                "priority": "normal",
            }
            await websocket.send(json.dumps(message))
            print("📤 Cursor sent: Hello from Cursor! I'm working on the MCP integration.")

            # Listen for responses
            try:
                async for response in websocket:
                    data = json.loads(response)
                    if data.get("sender") != "cursor":  # Don't echo our own messages
                        print(f"📥 Cursor received from {data.get('sender')}: {data.get('message')}")
            except TimeoutError:
                print("⏰ Cursor timeout waiting for responses")

    except Exception as e:
        print(f"❌ Cursor connection failed: {e}")

async def simulate_codex_agent():
    """Simulate Codex agent connecting and chatting"""
    try:
        async with websockets.connect("ws://localhost:8004/ws/codex") as websocket:
            print("🤖 Codex Agent connected!")

            # Wait a moment then respond
            await asyncio.sleep(1)

            message = {
                "message": "Hi Cursor! I can see your MCP integration work. The 8 tools look great!",
                "type": "chat",
                "priority": "normal",
            }
            await websocket.send(json.dumps(message))
            print("📤 Codex sent: Hi Cursor! I can see your MCP integration work. The 8 tools look great!")

            # Listen for more messages
            try:
                async for response in websocket:
                    data = json.loads(response)
                    if data.get("sender") != "codex":  # Don't echo our own messages
                        print(f"📥 Codex received from {data.get('sender')}: {data.get('message')}")
            except TimeoutError:
                print("⏰ Codex timeout waiting for responses")

    except Exception as e:
        print(f"❌ Codex connection failed: {e}")

async def simulate_dspy_agent():
    """Simulate a DSPy agent joining the conversation"""
    try:
        async with websockets.connect("ws://localhost:8004/ws/dspy_planner") as websocket:
            print("🤖 DSPy Planner connected!")

            # Wait a moment then join the conversation
            await asyncio.sleep(2)

            message = {
                "message": "Hello team! DSPy Planner here. I can help coordinate the precision evaluation tasks.",
                "type": "chat",
                "priority": "normal",
            }
            await websocket.send(json.dumps(message))
            print(
                "📤 DSPy Planner sent: Hello team! DSPy Planner here. I can help coordinate the precision evaluation tasks."
            )

            # Listen for responses
            try:
                async for response in websocket:
                    data = json.loads(response)
                    if data.get("sender") != "dspy_planner":
                        print(f"📥 DSPy Planner received from {data.get('sender')}: {data.get('message')}")
            except TimeoutError:
                print("⏰ DSPy Planner timeout waiting for responses")

    except Exception as e:
        print(f"❌ DSPy Planner connection failed: {e}")

async def main():
    """Run the real-time chat simulation"""
    print("🌐 Testing Real-time Multi-Agent Chat")
    print("=" * 50)

    # Start all agents concurrently
    tasks = [
        asyncio.create_task(simulate_cursor_agent()),
        asyncio.create_task(simulate_codex_agent()),
        asyncio.create_task(simulate_dspy_agent()),
    ]

    # Run for 10 seconds
    try:
        await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=10)
    except TimeoutError:
        print("\n⏰ Test completed (10 second timeout)")

    print("\n🎉 Real-time chat test completed!")

if __name__ == "__main__":
    asyncio.run(main())
