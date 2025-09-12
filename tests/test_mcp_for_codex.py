#!/usr/bin/env python3
"""
Test script for Codex to verify MCP tool access
"""

import json
import sys

import requests

# MCP Server endpoint
MCP_BASE_URL = "http://localhost:3000"

def test_mcp_connection():
    """Test basic MCP server connectivity"""
    try:
        response = requests.get(f"{MCP_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ MCP Server is running and healthy")
            return True
        else:
            print(f"❌ MCP Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to MCP server: {e}")
        return False

def list_mcp_tools():
    """List available MCP tools"""
    try:
        response = requests.get(f"{MCP_BASE_URL}/mcp/tools", timeout=5)
        if response.status_code == 200:
            tools = response.json()
            print("🔧 Available MCP Tools:")
            for tool in tools.get("tools", []):
                print(f"  - {tool['name']}: {tool['description']}")
            return tools.get("tools", [])
        else:
            print(f"❌ Failed to list tools: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
        return []

def test_project_context_tool():
    """Test the get_project_context tool"""
    try:
        payload = {"tool_name": "get_project_context", "arguments": {}}
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/tools/call", json=payload, headers={"Content-Type": "application/json"}, timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Project context tool working")
                data = result.get("data", {})
                print(f"  - Project root: {data.get('project_root', 'N/A')}")
                print(f"  - Backlog available: {'Yes' if data.get('current_backlog') else 'No'}")
                print(f"  - System overview available: {'Yes' if data.get('system_overview') else 'No'}")
                return True
            else:
                print(f"❌ Project context tool failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Project context tool HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing project context: {e}")
        return False

def test_precision_eval_tool():
    """Test the run_precision_eval tool"""
    try:
        payload = {
            "tool_name": "run_precision_eval",
            "arguments": {
                "config_file": "configs/precision_evidence_filter.env",
                "script": "scripts/run_precision_with_env_file.sh",
            },
        }
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/tools/call", json=payload, headers={"Content-Type": "application/json"}, timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Precision evaluation tool working")
                data = result.get("data", {})
                print(f"  - Return code: {data.get('returncode', 'N/A')}")
                print(f"  - Config file: {data.get('config_file', 'N/A')}")
                return True
            else:
                print(f"❌ Precision evaluation tool failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Precision evaluation tool HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing precision evaluation: {e}")
        return False

def main():
    """Run all MCP tests"""
    print("🧪 Testing MCP Integration for Codex")
    print("=" * 50)

    # Test 1: Basic connectivity
    if not test_mcp_connection():
        print("\n❌ MCP server not accessible. Please check:")
        print("  1. Server is running: curl http://localhost:3000/health")
        print("  2. No firewall blocking port 3000")
        print("  3. Server started with: python3 scripts/mcp_memory_server.py --port 3000")
        sys.exit(1)

    print()

    # Test 2: List tools
    tools = list_mcp_tools()
    if not tools:
        print("❌ No MCP tools available")
        sys.exit(1)

    print()

    # Test 3: Test working tools
    project_context_ok = test_project_context_tool()
    print()

    precision_eval_ok = test_precision_eval_tool()
    print()

    # Summary
    print("📊 Test Summary:")
    print("  - MCP Server: ✅ Running")
    print(f"  - Available Tools: {len(tools)}")
    print(f"  - Project Context: {'✅' if project_context_ok else '❌'}")
    print(f"  - Precision Evaluation: {'✅' if precision_eval_ok else '❌'}")

    if project_context_ok and precision_eval_ok:
        print("\n🎉 MCP integration is ready for Codex!")
        print("\n📋 For Codex to use:")
        print("  - MCP Server URL: http://localhost:3000")
        print("  - Health Check: http://localhost:3000/health")
        print("  - Tools List: http://localhost:3000/mcp/tools")
        print("  - Tool Call: POST http://localhost:3000/mcp/tools/call")
    else:
        print("\n⚠️  Some tools are not working. Check the errors above.")

if __name__ == "__main__":
    main()
