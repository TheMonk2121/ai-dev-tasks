#!/usr/bin/env python3
"""
Agent Monitor - Monitor Cursor and Codex activity
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Agent Monitor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "Agent Monitor",
        "endpoints": {"cursor": "/cursor", "codex": "/codex", "activity": "/activity", "logs": "/logs"},
    }


@app.get("/cursor")
async def cursor_status():
    """Get Cursor agent status"""
    # Check if Cursor is active by looking for recent MCP calls
    try:
        # Check recent MCP server activity
        if Path(".mcp-server.out").exists():
            with open(".mcp-server.out") as f:
                lines = f.readlines()
                recent_lines = [line for line in lines[-10:] if "POST /mcp/tools/call" in line]
                last_activity = lines[-1].strip() if lines else "No activity"
        else:
            recent_lines = []
            last_activity = "No log file"

        return {
            "agent": "cursor",
            "status": "active" if recent_lines else "inactive",
            "last_activity": last_activity,
            "recent_calls": len(recent_lines),
            "timestamp": time.time(),
        }
    except Exception as e:
        return {"agent": "cursor", "status": "error", "error": str(e), "timestamp": time.time()}


@app.get("/codex")
async def codex_status():
    """Get Codex agent status"""
    # Check if Codex is active by looking for specific patterns
    try:
        # Check for Codex-specific activity in logs
        if Path(".mcp-server.out").exists():
            with open(".mcp-server.out") as f:
                lines = f.readlines()
                # Look for patterns that might indicate Codex activity
                codex_indicators = ["GET /health", "GET /mcp/tools", "POST /mcp/tools/call"]
                recent_activity = [
                    line for line in lines[-20:] if any(indicator in line for indicator in codex_indicators)
                ]
                last_activity = lines[-1].strip() if lines else "No activity"
        else:
            recent_activity = []
            last_activity = "No log file"

        return {
            "agent": "codex",
            "status": "active" if recent_activity else "inactive",
            "last_activity": last_activity,
            "recent_calls": len(recent_activity),
            "timestamp": time.time(),
        }
    except Exception as e:
        return {"agent": "codex", "status": "error", "error": str(e), "timestamp": time.time()}


@app.get("/activity")
async def get_activity():
    """Get combined activity status"""
    cursor_status_data = await cursor_status()
    codex_status_data = await codex_status()

    return {
        "cursor": cursor_status_data,
        "codex": codex_status_data,
        "timestamp": time.time(),
        "summary": {
            "both_active": cursor_status_data["status"] == "active" and codex_status_data["status"] == "active",
            "any_active": cursor_status_data["status"] == "active" or codex_status_data["status"] == "active",
        },
    }


@app.get("/logs")
async def get_recent_logs():
    """Get recent log activity"""
    try:
        logs = []

        if Path(".mcp-server.out").exists():
            with open(".mcp-server.out") as f:
                lines = f.readlines()
                for line in lines[-10:]:
                    if line.strip():
                        logs.append({"file": "stdout", "line": line.strip(), "timestamp": time.time()})

        if Path(".mcp-server.err").exists():
            with open(".mcp-server.err") as f:
                lines = f.readlines()
                for line in lines[-5:]:
                    if line.strip() and "INFO:" in line:
                        logs.append({"file": "stderr", "line": line.strip(), "timestamp": time.time()})

        return {"logs": logs, "count": len(logs), "timestamp": time.time()}
    except Exception as e:
        return {"error": str(e), "timestamp": time.time()}


if __name__ == "__main__":
    import uvicorn

    print("👁️ Starting Agent Monitor on port 8003")
    print("📡 Monitor endpoints:")
    print("  - Cursor status: http://localhost:8003/cursor")
    print("  - Codex status: http://localhost:8003/codex")
    print("  - Combined activity: http://localhost:8003/activity")
    print("  - Recent logs: http://localhost:8003/logs")
    uvicorn.run(app, host="localhost", port=8003)
