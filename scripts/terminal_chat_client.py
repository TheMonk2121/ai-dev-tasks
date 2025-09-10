#!/usr/bin/env python3
"""
Terminal-based Multi-Agent Chat Client
Join the chat from your terminal
"""

import asyncio
import json
import sys
from datetime import datetime

import websockets


class ChatClient:
    def __init__(self, agent_name="user"):
        self.agent_name = agent_name
        self.websocket = None
        self.running = True

    async def connect(self):
        """Connect to the chat server"""
        try:
            uri = f"ws://localhost:8004/ws/{self.agent_name}"
            print(f"🔌 Connecting to {uri} as {self.agent_name}...")

            self.websocket = await websockets.connect(uri)
            print(f"✅ Connected as {self.agent_name}!")
            print("💬 Type your messages and press Enter. Type 'quit' to exit.")
            print("=" * 50)

            # Start listening for messages
            await asyncio.gather(self.listen_for_messages(), self.send_messages())

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("Make sure the multi-agent chat server is running on port 8004")

    async def listen_for_messages(self):
        """Listen for incoming messages"""
        try:
            ws = self.websocket
            if ws is None:
                return
            async for message in ws:
                data = json.loads(message)
                if data.get("type") == "message":
                    sender = data.get("sender", "unknown")
                    content = data.get("message", "")
                    timestamp = data.get("timestamp", 0)

                    # Format timestamp
                    time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

                    # Color coding for different agents
                    colors = {
                        "cursor": "\033[94m",  # Blue
                        "codex": "\033[92m",  # Green
                        "dspy_planner": "\033[93m",  # Yellow
                        "dspy_implementer": "\033[95m",  # Magenta
                        "dspy_researcher": "\033[96m",  # Cyan
                        "dspy_coder": "\033[94m",  # Blue
                        "dspy_optimizer": "\033[93m",  # Yellow
                        "dspy_evaluator": "\033[91m",  # Red
                        "dspy_debugger": "\033[92m",  # Green
                        "dspy_architect": "\033[95m",  # Magenta
                        "dspy_analyst": "\033[91m",  # Red
                        "dspy_coordinator": "\033[96m",  # Cyan
                        "user": "\033[97m",  # White
                    }

                    color = colors.get(sender, "\033[97m")
                    reset = "\033[0m"

                    print(f"{color}[{time_str}] {sender}:{reset} {content}")

        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed by server")
            self.running = False
        except Exception as e:
            print(f"❌ Error receiving message: {e}")
            self.running = False

    async def send_messages(self):
        """Send messages from user input"""
        try:
            while self.running:
                # Use asyncio to get input without blocking
                message = await asyncio.get_event_loop().run_in_executor(None, input, f"{self.agent_name}> ")

                if message.lower() in ["quit", "exit", "q"]:
                    self.running = False
                    break

                if message.strip():
                    if self.websocket:
                        await self.websocket.send(json.dumps({"type": "message", "message": message}))

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            self.running = False
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            self.running = False

    async def disconnect(self):
        """Disconnect from the chat server"""
        if self.websocket:
            await self.websocket.close()
            print("🔌 Disconnected from chat server")


async def main():
    """Main function"""
    if len(sys.argv) > 1:
        agent_name = sys.argv[1]
    else:
        agent_name = "user"

    print("🤖 Multi-Agent Chat Terminal Client")
    print("=" * 40)

    client = ChatClient(agent_name)

    try:
        await client.connect()
    finally:
        await client.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
