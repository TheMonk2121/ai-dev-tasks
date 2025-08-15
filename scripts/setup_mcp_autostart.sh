#!/bin/bash
# Setup MCP Memory Server Auto-Start
# ===================================
# Loads the LaunchAgent to automatically start the MCP server on login

set -e

echo "🚀 Setting up MCP Memory Server auto-start..."

# Get the absolute path to the LaunchAgent
LAUNCH_AGENT_PATH="$HOME/Library/LaunchAgents/com.ai.mcp-memory-server.plist"

# Check if the LaunchAgent file exists
if [ ! -f "$LAUNCH_AGENT_PATH" ]; then
    echo "❌ LaunchAgent not found at: $LAUNCH_AGENT_PATH"
    echo "   Make sure you're running this from the ai-dev-tasks directory"
    exit 1
fi

# Unload existing agent if it exists
if launchctl list | grep -q "com.ai.mcp-memory-server"; then
    echo "🔄 Unloading existing MCP server agent..."
    launchctl unload "$LAUNCH_AGENT_PATH" 2>/dev/null || true
fi

# Load the LaunchAgent
echo "📥 Loading MCP server LaunchAgent..."
launchctl load "$LAUNCH_AGENT_PATH"

# Check if it loaded successfully
if launchctl list | grep -q "com.ai.mcp-memory-server"; then
    echo "✅ MCP Memory Server LaunchAgent loaded successfully!"
    echo ""
    echo "🎯 The MCP server will now:"
    echo "   - Start automatically when you log in"
    echo "   - Restart automatically if it crashes"
    echo "   - Be available for Cursor's automatic memory rehydration"
    echo ""
    echo "💡 To test it now, run: curl http://localhost:3000/health"
    echo "💡 To stop auto-start: launchctl unload $LAUNCH_AGENT_PATH"
else
    echo "❌ Failed to load LaunchAgent"
    exit 1
fi
