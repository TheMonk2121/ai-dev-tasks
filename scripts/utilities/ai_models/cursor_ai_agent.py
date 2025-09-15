from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from datetime import datetime

import websockets

#!/usr/bin/env python3
"""
Cursor AI Agent - Connects to the multi-agent chat system
This allows me (Cursor AI) to participate in the chat!
"""

class CursorAIAgent:
    def __init__(self):
        self.websocket = None
        self.connected = False
        self.agent_id = "cursor_ai"
        self.agent_name = "Cursor AI"
        self.last_response_time = 0
        self.min_response_interval = 2.0  # Minimum 2 seconds between responses

    async def connect(self, uri="ws://localhost:8004/ws/cursor_ai"):
        """Connect to the multi-agent chat system"""
        try:
            print(f"🤖 {self.agent_name} connecting to {uri}...")
            self.websocket = await websockets.connect(uri)
            self.connected = True
            print(f"✅ {self.agent_name} connected successfully!")

            # Send initial greeting
            await self.send_message(
                "Hello! I'm Cursor AI, your AI assistant and code partner. I'm now part of the multi-agent chat system! 🚀"
            )

            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False

    async def send_message(self, message, message_type="chat"):
        """Send a message to the chat"""
        if not self.connected or not self.websocket:
            print("❌ Not connected to chat system")
            return

        try:
            message_data = {
                "type": message_type,
                "content": message,
                "agent": self.agent_id,
                "timestamp": time.time(),
                "metadata": {"agent_name": self.agent_name, "role": "AI Assistant & Code Partner"},
            }

            await self.websocket.send(json.dumps(message_data))
            print(f"📤 {self.agent_name}: {message}")

        except Exception as e:
            print(f"❌ Failed to send message: {e}")

    async def listen_for_messages(self):
        """Listen for incoming messages and respond"""
        if not self.connected or not self.websocket:
            print("❌ Not connected to chat system")
            return

        try:
            async for message in self.websocket:
                try:
                    # Skip empty messages
                    if not message or not message.strip():
                        continue

                    data = json.loads(message)
                    await self.handle_message(data)
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON received: {message[:100]}... Error: {e}")
                except Exception as e:
                    print(f"❌ Error handling message: {e}")

        except websockets.exceptions.ConnectionClosed as e:
            print(f"🔌 Connection closed: {e}")
            self.connected = False
        except Exception as e:
            print(f"❌ Error in message loop: {e}")
            self.connected = False

    async def handle_message(self, data):
        """Handle incoming messages and generate responses"""
        message_type = data.get("type", "chat")
        content = data.get("content", "")
        sender = data.get("agent", "unknown")

        print(f"📥 Received from {sender}: '{content}'")

        # Don't respond to my own messages
        if sender == self.agent_id:
            print("🔄 Ignoring my own message")
            return

        # Don't respond to empty or whitespace-only messages
        if not content or not content.strip():
            print("🔄 Ignoring empty message")
            return

        # Don't respond to system messages
        if message_type != "chat":
            print(f"🔄 Ignoring non-chat message type: {message_type}")
            return

        # Rate limiting - don't respond too frequently
        current_time = time.time()
        if current_time - self.last_response_time < self.min_response_interval:
            print(
                f"🔄 Rate limiting: waiting {self.min_response_interval - (current_time - self.last_response_time):.1f}s"
            )
            return

        # Generate a response based on the message
        response = await self.generate_response(content, sender)
        if response:
            await self.send_message(response)
            self.last_response_time = current_time

    async def generate_response(self, message, sender):
        """Generate a response to a message"""
        # Simple response logic - in a real implementation, this would use AI
        message_lower = message.lower()

        if "hello" in message_lower or "hi" in message_lower:
            return "Hello! Great to chat with you! I'm here to help with coding, debugging, and any questions you have. What can I assist you with today? 😊"

        elif "help" in message_lower:
            return "I'm here to help! I can assist with:\n- Code writing and debugging\n- Explaining programming concepts\n- Project architecture and design\n- Problem solving and optimization\n- And much more! What do you need help with? 🛠️"

        elif "code" in message_lower or "programming" in message_lower:
            return "I love coding! I can help you with:\n- Writing clean, efficient code\n- Debugging issues\n- Code reviews and improvements\n- Best practices and patterns\n- Language-specific questions\nWhat programming challenge are you working on? 💻"

        elif "?" in message:
            return "That's a great question! I'd be happy to help you find the answer. Could you provide a bit more context so I can give you the most helpful response? 🤔"

        else:
            return "Thanks for your message! I'm here to help with coding, debugging, and any technical questions you have. Feel free to ask me anything! 🚀"

    async def disconnect(self):
        """Disconnect from the chat system"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            print(f"👋 {self.agent_name} disconnected")

async def main():
    """Main function to run the Cursor AI agent"""
    agent = CursorAIAgent()

    # Connect to the chat system
    if await agent.connect():
        try:
            # Start listening for messages
            await agent.listen_for_messages()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
        finally:
            await agent.disconnect()
    else:
        print("❌ Failed to connect to chat system")

if __name__ == "__main__":
    print("🤖 Starting Cursor AI Agent...")
    print("📡 This will connect me to your multi-agent chat system!")
    print("🔄 Press Ctrl+C to stop")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Cursor AI Agent stopped")
