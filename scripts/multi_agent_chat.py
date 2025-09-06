#!/usr/bin/env python3
"""
Multi-Agent Chat Bridge - Real-time communication between Cursor, Codex, and DSPy agents
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Multi-Agent Chat Bridge")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active connections by agent type
agent_connections: Dict[str, List[WebSocket]] = {
    "user": [],
    "cursor": [],
    "codex": [],
    "dspy_planner": [],
    "dspy_implementer": [],
    "dspy_researcher": [],
    "dspy_coder": [],
    "dspy_optimizer": [],
    "dspy_evaluator": [],
    "dspy_debugger": [],
    "dspy_architect": [],
    "dspy_analyst": [],
    "dspy_coordinator": [],
    "cursor_ai": [],  # Me - Cursor AI Assistant
}

# Message history
message_history: List[Dict] = []

# Agent metadata
agent_metadata: Dict[str, Dict] = {
    "user": {"name": "User", "role": "Human User", "color": "#6C757D"},
    "cursor": {"name": "Cursor Agent", "role": "Code Editor Assistant", "color": "#007ACC"},
    "codex": {"name": "Codex", "role": "AI Code Generator", "color": "#00D4AA"},
    "dspy_planner": {"name": "DSPy Planner", "role": "Strategic Planning", "color": "#FF6B6B"},
    "dspy_implementer": {"name": "DSPy Implementer", "role": "Code Implementation", "color": "#4ECDC4"},
    "dspy_researcher": {"name": "DSPy Researcher", "role": "Research & Analysis", "color": "#45B7D1"},
    "dspy_coder": {"name": "DSPy Coder", "role": "Code Development", "color": "#96CEB4"},
    "dspy_optimizer": {"name": "DSPy Optimizer", "role": "Performance Optimization", "color": "#FFEAA7"},
    "dspy_evaluator": {"name": "DSPy Evaluator", "role": "Quality Assessment", "color": "#DDA0DD"},
    "dspy_debugger": {"name": "DSPy Debugger", "role": "Bug Detection & Fixing", "color": "#F39C12"},
    "dspy_architect": {"name": "DSPy Architect", "role": "System Architecture", "color": "#E74C3C"},
    "dspy_analyst": {"name": "DSPy Analyst", "role": "Data Analysis", "color": "#9B59B6"},
    "dspy_coordinator": {"name": "DSPy Coordinator", "role": "Task Coordination", "color": "#1ABC9C"},
    "cursor_ai": {"name": "Cursor AI", "role": "AI Assistant & Code Partner", "color": "#FF6B35"},
}


class ChatMessage(BaseModel):
    sender: str
    message: str
    timestamp: float
    message_type: str = "chat"  # "chat", "status", "log", "command", "system"
    target_agents: Optional[List[str]] = None  # None = broadcast to all
    priority: str = "normal"  # "low", "normal", "high", "urgent"
    metadata: Optional[Dict] = None


class AgentStatus(BaseModel):
    agent: str
    status: str  # "connected", "disconnected", "busy", "idle"
    last_seen: float
    metadata: Optional[Dict] = None


@app.get("/")
async def root():
    return {
        "service": "Multi-Agent Chat Bridge",
        "endpoints": {
            "websocket": "/ws/{agent}",
            "messages": "/messages",
            "status": "/status",
            "agents": "/agents",
            "health": "/health",
        },
        "supported_agents": list(agent_connections.keys()),
        "agent_metadata": agent_metadata,
    }


@app.get("/health")
async def health():
    total_connections = sum(len(connections) for connections in agent_connections.values())
    active_agents = [agent for agent, connections in agent_connections.items() if connections]

    return {
        "status": "healthy",
        "timestamp": time.time(),
        "total_connections": total_connections,
        "active_agents": active_agents,
        "agent_connections": {agent: len(connections) for agent, connections in agent_connections.items()},
    }


@app.get("/agents")
async def get_agents():
    """Get information about all supported agents"""
    return {
        "agents": agent_metadata,
        "active_agents": [agent for agent, connections in agent_connections.items() if connections],
        "connection_counts": {agent: len(connections) for agent, connections in agent_connections.items()},
        "timestamp": time.time(),
    }


@app.get("/messages")
async def get_messages(limit: int = 50, agent: Optional[str] = None):
    """Get recent message history, optionally filtered by agent"""
    messages = message_history
    if agent:
        messages = [msg for msg in messages if msg.get("sender") == agent]

    return {"messages": messages[-limit:], "count": len(messages), "filtered_by": agent, "timestamp": time.time()}


@app.get("/status")
async def get_status():
    """Get current status of all agents"""
    status = {}
    for agent, connections in agent_connections.items():
        status[agent] = {
            "connected": len(connections) > 0,
            "connection_count": len(connections),
            "last_seen": "active" if connections else "disconnected",
            "metadata": agent_metadata.get(agent, {}),
        }

    return {
        "agents": status,
        "summary": {
            "total_agents": len(agent_connections),
            "active_agents": len([a for a, c in agent_connections.items() if c]),
            "total_connections": sum(len(c) for c in agent_connections.values()),
        },
        "timestamp": time.time(),
    }


@app.websocket("/ws/{agent}")
async def websocket_endpoint(websocket: WebSocket, agent: str):
    """WebSocket endpoint for agent communication"""
    if agent not in agent_connections:
        await websocket.close(code=4000, reason=f"Invalid agent. Supported: {list(agent_connections.keys())}")
        return

    await websocket.accept()

    # Add to appropriate connection list
    agent_connections[agent].append(websocket)

    # Send connection confirmation
    await websocket.send_text(
        json.dumps(
            {
                "type": "connection",
                "agent": agent,
                "status": "connected",
                "timestamp": time.time(),
                "metadata": agent_metadata.get(agent, {}),
            }
        )
    )

    # Broadcast status update to all agents
    await broadcast_status_update(agent, "connected")

    # Send welcome message
    welcome_message = {
        "type": "system",
        "sender": "system",
        "message": f"🤖 {agent_metadata.get(agent, {}).get('name', agent)} has joined the chat",
        "timestamp": time.time(),
        "metadata": {"agent": agent, "action": "joined"},
    }
    await broadcast_message(welcome_message)

    try:
        while True:
            # Receive message
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

            # Lightweight heartbeat handling
            mtype = message_data.get("type")
            if mtype in ("ping", "heartbeat"):
                try:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "system",
                                "sender": "system",
                                "message": "pong",
                                "timestamp": time.time(),
                            }
                        )
                    )
                except Exception:
                    pass
                continue

            # Process @mentions in the message
            message_text = message_data.get("message", "")
            target_agents = message_data.get("target_agents")

            # Auto-detect @mentions if no target_agents specified
            if not target_agents and "@" in message_text:
                mentioned_agents = []
                for agent_name in agent_connections.keys():
                    if f"@{agent_name}" in message_text.lower():
                        mentioned_agents.append(agent_name)
                if mentioned_agents:
                    target_agents = mentioned_agents

            # Routing defaults:
            # - If message contains "@all", broadcast to everyone
            # - If no target_agents and no @mentions, broadcast to everyone (group chat default)
            if "@all" in message_text.lower():
                target_agents = None  # Broadcast to all
            elif not target_agents:
                target_agents = None  # Default to broadcast

            # Create message object
            message = {
                "type": "message",  # Ensure web UIs recognize chat payloads
                "sender": agent,
                "message": message_text,
                "timestamp": time.time(),
                "message_type": message_data.get("type", "chat"),
                "target_agents": target_agents,
                "priority": message_data.get("priority", "normal"),
                "metadata": message_data.get("metadata", {}),
            }

            # Add to message history
            message_history.append(message)

            # Broadcast message
            await broadcast_message(message)

            # Keep only last 2000 messages
            if len(message_history) > 2000:
                message_history[:] = message_history[-2000:]

    except WebSocketDisconnect:
        pass
    finally:
        # Remove from connection list
        if websocket in agent_connections[agent]:
            agent_connections[agent].remove(websocket)

        # Broadcast status update
        await broadcast_status_update(agent, "disconnected")

        # Send goodbye message
        goodbye_message = {
            "type": "system",
            "sender": "system",
            "message": f"👋 {agent_metadata.get(agent, {}).get('name', agent)} has left the chat",
            "timestamp": time.time(),
            "metadata": {"agent": agent, "action": "left"},
        }
        await broadcast_message(goodbye_message)


async def broadcast_message(message: Dict):
    """Broadcast message to appropriate agents"""
    target_agents = message.get("target_agents")
    sender = message.get("sender")

    if isinstance(target_agents, list) and target_agents:
        # Send to specific agents and always echo to sender
        delivery_agents: Set[str] = set(target_agents)
        if sender:
            delivery_agents.add(sender)
        for agent in delivery_agents:
            if agent in agent_connections:
                for connection in agent_connections[agent]:
                    try:
                        await connection.send_text(json.dumps(message))
                    except Exception:
                        pass  # Connection might be closed
    else:
        # Broadcast to all connected agents
        for agent, connections in agent_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    pass  # Connection might be closed


async def broadcast_status_update(agent: str, status: str):
    """Broadcast status update to all agents"""
    status_message = {
        "type": "status",
        "sender": "system",
        "message": f"📊 {agent_metadata.get(agent, {}).get('name', agent)} status: {status}",
        "timestamp": time.time(),
        "metadata": {"agent": agent, "status": status},
    }

    await broadcast_message(status_message)


@app.post("/send-message")
async def send_message(message: ChatMessage):
    """Send a message programmatically"""
    message_dict = message.dict()

    # Apply same routing logic as WebSocket endpoint
    message_text = message_dict.get("message", "")
    target_agents = message_dict.get("target_agents")

    # Auto-detect @mentions if no target_agents specified
    if not target_agents and "@" in message_text:
        mentioned_agents = []
        for agent_name in agent_connections.keys():
            if f"@{agent_name}" in message_text.lower():
                mentioned_agents.append(agent_name)
        if mentioned_agents:
            target_agents = mentioned_agents

    # Routing defaults mirror WebSocket behavior
    if "@all" in message_text.lower():
        target_agents = None
    elif not target_agents:
        target_agents = None  # Default to broadcast

    # Update the message with the determined target_agents
    message_dict["target_agents"] = target_agents
    # Ensure web UIs recognize chat payloads
    message_dict.setdefault("type", "message")

    message_history.append(message_dict)
    await broadcast_message(message_dict)

    return {"success": True, "message": "Message sent", "timestamp": time.time()}


@app.get("/agent/{agent_name}/status")
async def get_agent_status(agent_name: str):
    """Get status of a specific agent"""
    if agent_name not in agent_connections:
        return {"error": f"Agent {agent_name} not found", "timestamp": time.time()}

    connections = agent_connections[agent_name]
    recent_messages = [msg for msg in message_history[-50:] if msg.get("sender") == agent_name]

    return {
        "agent": agent_name,
        "connected": len(connections) > 0,
        "connection_count": len(connections),
        "last_seen": "active" if connections else "disconnected",
        "recent_messages": len(recent_messages),
        "metadata": agent_metadata.get(agent_name, {}),
        "timestamp": time.time(),
    }


@app.get("/chat/rooms")
async def get_chat_rooms():
    """Get available chat rooms/channels"""
    return {
        "rooms": {
            "general": {
                "name": "General Chat",
                "description": "All agents welcome",
                "active_agents": [agent for agent, connections in agent_connections.items() if connections],
            },
            "dspy_team": {
                "name": "DSPy Team",
                "description": "DSPy agents coordination",
                "active_agents": [
                    agent
                    for agent, connections in agent_connections.items()
                    if agent.startswith("dspy_") and connections
                ],
            },
            "development": {
                "name": "Development",
                "description": "Cursor, Codex, and coding agents",
                "active_agents": [
                    agent
                    for agent, connections in agent_connections.items()
                    if agent in ["cursor", "codex", "dspy_coder", "dspy_implementer"] and connections
                ],
            },
        },
        "timestamp": time.time(),
    }


if __name__ == "__main__":
    import uvicorn

    print("🌐 Starting Multi-Agent Chat Bridge on port 8004")
    print("📡 WebSocket endpoints:")
    for agent in agent_connections.keys():
        print(f"  - {agent}: ws://localhost:8004/ws/{agent}")
    print("📋 HTTP endpoints:")
    print("  - Agents: http://localhost:8004/agents")
    print("  - Status: http://localhost:8004/status")
    print("  - Messages: http://localhost:8004/messages")
    print("  - Health: http://localhost:8004/health")
    print("  - Chat Rooms: http://localhost:8004/chat/rooms")
    uvicorn.run(app, host="localhost", port=8004)
