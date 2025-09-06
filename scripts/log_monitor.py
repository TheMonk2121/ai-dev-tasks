#!/usr/bin/env python3
"""
Log Monitor for MCP Server - Provides real-time logs to both Cursor and Codex
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI(title="MCP Log Monitor")

# CORS middleware for Cursor integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
active_connections: List[WebSocket] = []


@app.get("/")
async def root():
    return {
        "service": "MCP Log Monitor",
        "endpoints": {"logs": "/logs", "stream": "/logs/stream", "websocket": "/ws/logs", "health": "/health"},
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/logs")
async def get_recent_logs(lines: int = 50):
    """Get recent log entries from MCP server"""
    log_files = [".mcp-server.out", ".mcp-server.err"]
    logs = []

    for log_file in log_files:
        if Path(log_file).exists():
            try:
                with open(log_file, "r") as f:
                    file_lines = f.readlines()
                    recent_lines = file_lines[-lines:] if len(file_lines) > lines else file_lines
                    logs.extend(
                        [
                            {"file": log_file, "line": line.strip(), "timestamp": time.time()}
                            for line in recent_lines
                            if line.strip()
                        ]
                    )
            except Exception as e:
                logs.append({"file": log_file, "error": str(e), "timestamp": time.time()})

    return {"logs": logs, "count": len(logs), "timestamp": time.time()}


@app.get("/logs/stream")
async def stream_logs():
    """Stream logs in real-time"""

    async def generate_logs():
        log_files = [".mcp-server.out", ".mcp-server.err"]

        while True:
            for log_file in log_files:
                if Path(log_file).exists():
                    try:
                        with open(log_file, "r") as f:
                            # Read new lines since last check
                            f.seek(0, 2)  # Go to end of file
                            new_lines = f.readlines()

                            for line in new_lines:
                                if line.strip():
                                    log_entry = {
                                        "file": log_file,
                                        "line": line.strip(),
                                        "timestamp": time.time(),
                                        "datetime": datetime.now().isoformat(),
                                    }
                                    yield f"data: {json.dumps(log_entry)}\n\n"
                    except Exception as e:
                        error_entry = {"file": log_file, "error": str(e), "timestamp": time.time()}
                        yield f"data: {json.dumps(error_entry)}\n\n"

            await asyncio.sleep(1)  # Check every second

    return StreamingResponse(
        generate_logs(), media_type="text/plain", headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for real-time log streaming"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        log_files = [".mcp-server.out", ".mcp-server.err"]

        while True:
            for log_file in log_files:
                if Path(log_file).exists():
                    try:
                        with open(log_file, "r") as f:
                            f.seek(0, 2)  # Go to end of file
                            new_lines = f.readlines()

                            for line in new_lines:
                                if line.strip():
                                    log_entry = {
                                        "file": log_file,
                                        "line": line.strip(),
                                        "timestamp": time.time(),
                                        "datetime": datetime.now().isoformat(),
                                    }
                                    await websocket.send_text(json.dumps(log_entry))
                    except Exception as e:
                        error_entry = {"file": log_file, "error": str(e), "timestamp": time.time()}
                        await websocket.send_text(json.dumps(error_entry))

            await asyncio.sleep(1)  # Check every second

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)


@app.get("/logs/mcp-server")
async def get_mcp_server_logs():
    """Get MCP server logs specifically"""
    return await get_recent_logs(100)


@app.get("/logs/system")
async def get_system_logs():
    """Get system logs and process info"""
    import subprocess

    try:
        # Get MCP server process info
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)

        mcp_processes = []
        for line in result.stdout.split("\n"):
            if "mcp_memory_server" in line or "mcp-server" in line:
                mcp_processes.append(line.strip())

        return {"mcp_processes": mcp_processes, "timestamp": time.time()}
    except Exception as e:
        return {"error": str(e), "timestamp": time.time()}


if __name__ == "__main__":
    import uvicorn

    print("🔍 Starting MCP Log Monitor on port 8001")
    print("📡 Log endpoints:")
    print("  - Recent logs: http://localhost:8001/logs")
    print("  - Stream logs: http://localhost:8001/logs/stream")
    print("  - WebSocket: ws://localhost:8001/ws/logs")
    print("  - MCP logs: http://localhost:8001/logs/mcp-server")
    uvicorn.run(app, host="localhost", port=8001)
