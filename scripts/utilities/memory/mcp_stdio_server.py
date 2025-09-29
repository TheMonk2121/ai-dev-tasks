#!/usr/bin/env python3
"""
MCP Stdio Server for Cursor Integration

This script provides a stdio-based MCP server that Cursor can communicate with.
It acts as a bridge between Cursor's MCP protocol and the HTTP-based MCP memory server.
"""

import asyncio
import json
import logging
import sys
from typing import Any

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP server configuration
MCP_SERVER_URL = "http://localhost:3000"

class MCPStdioServer:
    """MCP server that communicates via stdio and proxies to HTTP server."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle MCP requests by proxying to HTTP server."""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "ai-dev-tasks-memory",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                # Get tools from HTTP server
                response = await self.client.get(f"{MCP_SERVER_URL}/mcp/tools")
                tools_data = response.json()
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "tools": tools_data.get("tools", [])
                    }
                }
            
            elif method == "tools/call":
                # Call tool on HTTP server
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                response = await self.client.post(
                    f"{MCP_SERVER_URL}/mcp/tools/call",
                    json={
                        "tool_name": tool_name,
                        "arguments": arguments
                    }
                )
                
                result = response.json()
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def run(self):
        """Run the stdio-based MCP server."""
        logger.info("Starting MCP stdio server...")
        
        # Test connection to HTTP server
        try:
            response = await self.client.get(f"{MCP_SERVER_URL}/health")
            if response.status_code != 200:
                logger.error(f"HTTP server not available: {response.status_code}")
                return
        except Exception as e:
            logger.error(f"Cannot connect to HTTP server: {e}")
            return
        
        logger.info("Connected to HTTP MCP server")
        
        # Read from stdin and write to stdout
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = await self.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                continue

async def main():
    """Main entry point."""
    server = MCPStdioServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
