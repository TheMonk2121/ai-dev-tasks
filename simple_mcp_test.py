#!/usr/bin/env python3
"""
Simple MCP test endpoint for Codex
"""

import json

import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Simple MCP Test for Codex")


class TestRequest(BaseModel):
    tool_name: str
    arguments: dict = {}


@app.get("/")
async def root():
    return {
        "message": "Simple MCP Test Endpoint for Codex",
        "mcp_server": "http://localhost:3000",
        "available_tools": ["get_project_context", "run_precision_eval", "query_memory"],
    }


@app.post("/test-tool")
async def test_tool(request: TestRequest):
    """Test MCP tool and return result"""
    try:
        # Forward request to MCP server
        response = requests.post(
            "http://localhost:3000/mcp/tools/call",
            json={"tool_name": request.tool_name, "arguments": request.arguments},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            result = response.json()
            return {"success": True, "tool_name": request.tool_name, "result": result}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/quick-test")
async def quick_test():
    """Quick test of project context tool"""
    try:
        response = requests.post(
            "http://localhost:3000/mcp/tools/call",
            json={"tool_name": "get_project_context", "arguments": {}},
            headers={"Content-Type": "application/json"},
            timeout=5,
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "mcp_server_status": "✅ Running",
                "project_context_test": "✅ Working" if result.get("success") else "❌ Failed",
                "project_root": result.get("data", {}).get("project_root", "N/A"),
                "full_result": result,
            }
        else:
            return {"mcp_server_status": "❌ Error", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"mcp_server_status": "❌ Cannot connect", "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Simple MCP Test Server on port 8000")
    print("📡 Test endpoint: http://localhost:8000/quick-test")
    print("🔧 Tool test: POST http://localhost:8000/test-tool")
    uvicorn.run(app, host="localhost", port=8000)
