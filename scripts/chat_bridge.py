#!/usr/bin/env python3
"""
Chat Bridge - Real-time communication between Cursor Agent and Codex
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Cursor-Codex Chat Bridge")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active connections
cursor_connections: list[WebSocket] = []
codex_connections: list[WebSocket] = []

# Message history
message_history: list[dict] = []


class ChatMessage(BaseModel):
    sender: str  # "cursor" or "codex"
    message: str
    timestamp: float
    message_type: str = "chat"  # "chat", "status", "log", "command"


class StatusUpdate(BaseModel):
    agent: str
    status: str
    details: dict | None = None
    timestamp: float


@app.get("/")
async def root():
    return {
        "service": "Cursor-Codex Chat Bridge",
        "endpoints": {"websocket": "/ws/{agent}", "messages": "/messages", "status": "/status", "health": "/health"},
        "agents": ["cursor", "codex"],
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "active_connections": {"cursor": len(cursor_connections), "codex": len(codex_connections)},
    }


@app.get("/messages")
async def get_messages(limit: int = 50):
    """Get recent message history"""
    return {"messages": message_history[-limit:], "count": len(message_history), "timestamp": time.time()}


@app.get("/status")
async def get_status():
    """Get current status of both agents"""
    return {
        "cursor": {
            "connected": len(cursor_connections) > 0,
            "last_seen": "active" if cursor_connections else "disconnected",
        },
        "codex": {
            "connected": len(codex_connections) > 0,
            "last_seen": "active" if codex_connections else "disconnected",
        },
        "timestamp": time.time(),
    }


@app.websocket("/ws/{agent}")
async def websocket_endpoint(websocket: WebSocket, agent: str):
    """WebSocket endpoint for agent communication"""
    if agent not in ["cursor", "codex"]:
        await websocket.close(code=4000, reason="Invalid agent")
        return

    await websocket.accept()

    # Add to appropriate connection list
    if agent == "cursor":
        cursor_connections.append(websocket)
    else:
        codex_connections.append(websocket)

    # Send connection confirmation
    await websocket.send_text(
        json.dumps({"type": "connection", "agent": agent, "status": "connected", "timestamp": time.time()})
    )

    # Broadcast status update
    await broadcast_status_update(agent, "connected")

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Add to message history
            message = {
                "sender": agent,
                "message": message_data.get("message", ""),
                "timestamp": time.time(),
                "message_type": message_data.get("type", "chat"),
                "raw_data": message_data,
            }
            message_history.append(message)

            # Broadcast to other agent
            target_connections = codex_connections if agent == "cursor" else cursor_connections
            for connection in target_connections:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    pass  # Connection might be closed

            # Keep only last 1000 messages
            if len(message_history) > 1000:
                message_history[:] = message_history[-1000:]

    except WebSocketDisconnect:
        pass
    finally:
        # Remove from connection list
        if agent == "cursor" and websocket in cursor_connections:
            cursor_connections.remove(websocket)
        elif agent == "codex" and websocket in codex_connections:
            codex_connections.remove(websocket)

        # Broadcast status update
        await broadcast_status_update(agent, "disconnected")


async def broadcast_status_update(agent: str, status: str):
    """Broadcast status update to all connections"""
    status_message = {"type": "status", "agent": agent, "status": status, "timestamp": time.time()}

    all_connections = cursor_connections + codex_connections
    for connection in all_connections:
        try:
            await connection.send_text(json.dumps(status_message))
        except:
            pass  # Connection might be closed


@app.post("/send-message")
async def send_message(message: ChatMessage):
    """Send a message programmatically"""
    # Add to message history
    message_dict = message.dict()
    message_history.append(message_dict)

    # Broadcast to appropriate connections
    target_connections = codex_connections if message.sender == "cursor" else cursor_connections
    for connection in target_connections:
        try:
            await connection.send_text(json.dumps(message_dict))
        except:
            pass  # Connection might be closed

    return {"success": True, "message": "Message sent"}


@app.get("/cursor-status")
async def cursor_status():
    """Get Cursor agent status"""
    return {
        "connected": len(cursor_connections) > 0,
        "connections": len(cursor_connections),
        "last_message": message_history[-1] if message_history else None,
        "timestamp": time.time(),
    }


@app.get("/codex-status")
async def codex_status():
    """Get Codex agent status"""
    return {
        "connected": len(codex_connections) > 0,
        "connections": len(codex_connections),
        "last_message": message_history[-1] if message_history else None,
        "timestamp": time.time(),
    }


if __name__ == "__main__":
    import uvicorn

    print("🌉 Starting Cursor-Codex Chat Bridge on port 8002")
    print("📡 WebSocket endpoints:")
    print("  - Cursor: ws://localhost:8002/ws/cursor")
    print("  - Codex: ws://localhost:8002/ws/codex")
    print("📋 HTTP endpoints:")
    print("  - Messages: http://localhost:8002/messages")
    print("  - Status: http://localhost:8002/status")
    print("  - Health: http://localhost:8002/health")
    uvicorn.run(app, host="localhost", port=8002)
