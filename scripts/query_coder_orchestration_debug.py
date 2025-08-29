#!/usr/bin/env python3
"""
Query Coder agent about orchestration gateway async health check debugging
"""

import asyncio
import sys
from pathlib import Path

# Add the dspy-rag-system to the path
project_root = Path(__file__).parent.parent
dspy_path = project_root / "dspy-rag-system" / "src"
sys.path.insert(0, str(dspy_path))

# Import after path manipulation
try:
    from specialized_agent_framework import CoderAgent
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure the dspy-rag-system is properly set up.")
    sys.exit(1)


def main():
    """Query the Coder agent about orchestration debugging"""

    # Create Coder agent
    coder_agent = CoderAgent()

    # Define the debugging problem
    problem_description = """
    I'm debugging an async health check issue in our MCP Orchestration Gateway. Here's what's happening:

    **Current Status:**
    - Orchestration gateway starts successfully on port 3002
    - 2 MCP servers are added (ports 3000, 3001)
    - Health check loop starts and runs (we see the logs)
    - But servers remain in "offline" status

    **What We Know:**
    - MCP servers are responding to health checks:
      - Server 1 (port 3000): returns "degraded" status
      - Server 2 (port 3001): returns "healthy" status
    - Health check logic accepts both "healthy" and "degraded" as success
    - Async health check loop is running (we see "Running health checks for 2 servers")
    - But server status never updates from "offline" to "healthy"/"degraded"

    **Key Files:**
    - scripts/mcp_orchestrator.py: Contains HealthChecker and MCPOrchestrator classes
    - scripts/mcp_orchestration_gateway.py: Main gateway server
    - The health check method: check_server_health() in HealthChecker class

    **Questions for Coder:**
    1. What could be causing the server status to not update despite successful health checks?
    2. Are there any async task scheduling issues in the health check loop?
    3. Could there be a race condition or timing issue?
    4. What debugging steps would you recommend?
    5. Should we modify the health check logic or the server status update mechanism?

    Please analyze the code and provide specific debugging recommendations.
    """

    # Query the Coder agent
    print("🤖 Querying Coder agent for orchestration debugging help...")
    print("=" * 80)

    try:
        # Create request format for CoderAgent
        request = {
            "query": problem_description,
            "file_path": "scripts/mcp_orchestration_gateway.py",
            "code_content": "",  # We'll let the agent analyze the file
            "analysis_type": "comprehensive",
        }

        # Use asyncio to run the async method
        response = asyncio.run(coder_agent.process_request(request))
        print("📝 Coder Agent Response:")
        print(response)

    except Exception as e:
        print(f"❌ Error querying Coder agent: {e}")
        print("This might be due to database connection issues or missing dependencies.")
        print("The orchestration gateway is still functional with manual health marking.")


if __name__ == "__main__":
    main()
