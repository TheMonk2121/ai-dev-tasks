#!/usr/bin/env python3.12.123.11
"""
MCP Memory Rehydrator Server
----------------------------
Minimal HTTP server that exposes the memory rehydrator as MCP-compatible endpoints.
This allows Cursor to automatically access database-based memory rehydration.

Usage:
    python3 scripts/mcp_memory_server.py
    # Then configure Cursor to connect to http://localhost:3000/mcp
"""

import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# Add the dspy-rag-system src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system", "src"))

try:
    from utils.memory_rehydrator import build_hydration_bundle
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the ai-dev-tasks root directory")
    sys.exit(1)


class MCPMemoryHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP-compatible memory rehydration endpoints"""

    def do_GET(self):
        """Handle GET requests for MCP server info"""
        if self.path == "/mcp":
            self.send_mcp_info()
        elif self.path == "/health":
            self.send_health_check()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests for memory rehydration"""
        if self.path == "/mcp/tools/call":
            self.handle_memory_rehydration()
        else:
            self.send_error(404, "Not Found")

    def send_mcp_info(self):
        """Send MCP server information"""
        mcp_info = {
            "name": "memory-rehydrator",
            "version": "1.0.0",
            "description": "Database-based memory rehydration for Cursor AI",
            "tools": [
                {
                    "name": "rehydrate_memory",
                    "description": "Get role-aware context from PostgreSQL database",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "role": {
                                "type": "string",
                                "enum": ["planner", "implementer", "researcher"],
                                "description": "AI role for context selection",
                            },
                            "task": {"type": "string", "description": "Specific task or query for context"},
                            "limit": {
                                "type": "integer",
                                "default": 8,
                                "description": "Maximum number of sections to return",
                            },
                            "token_budget": {
                                "type": "integer",
                                "default": 1200,
                                "description": "Token budget for context",
                            },
                        },
                        "required": ["task"],
                    },
                }
            ],
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(mcp_info).encode())

    def send_health_check(self):
        """Send health check response"""
        health = {"status": "healthy", "timestamp": time.time(), "service": "mcp-memory-rehydrator"}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(health).encode())

    def handle_memory_rehydration(self):
        """Handle memory rehydration requests"""
        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            request = json.loads(body.decode())

            # Extract parameters
            tool_name = request.get("name")
            arguments = request.get("arguments", {})

            if tool_name != "rehydrate_memory":
                self.send_error(400, "Unknown tool")
                return

            # Get parameters with defaults
            role = arguments.get("role", "planner")
            task = arguments.get("task", "general context")
            limit = arguments.get("limit", 8)
            token_budget = arguments.get("token_budget", 1200)

            # Build hydration bundle
            bundle = build_hydration_bundle(role=role, task=task, limit=limit, token_budget=token_budget)

            # Prepare response
            response = {"content": [{"type": "text", "text": bundle.text}], "metadata": bundle.meta}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            error_response = {"error": {"code": "internal_error", "message": str(e)}}
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())

    def log_message(self, format, *args):
        """Custom logging to avoid cluttering output"""
        pass


def start_server(port=3000):
    """Start the MCP memory server"""
    server_address = ("", port)
    httpd = HTTPServer(server_address, MCPMemoryHandler)

    print(f"🚀 MCP Memory Rehydrator Server starting on port {port}")
    print(f"📡 MCP endpoint: http://localhost:{port}/mcp")
    print(f"🏥 Health check: http://localhost:{port}/health")
    print(f"🔄 Memory rehydration: POST http://localhost:{port}/mcp/tools/call")
    print("\n💡 Configure Cursor to connect to this server for automatic memory rehydration!")
    print("   Press Ctrl+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MCP Memory Rehydrator Server")
    parser.add_argument("--port", type=int, default=3000, help="Port to run server on")

    args = parser.parse_args()
    start_server(args.port)
