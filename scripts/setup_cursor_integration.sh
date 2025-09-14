#!/bin/bash
# Setup Cursor Integration for AI Dev Tasks
# This script configures Cursor to work with the MCP server and conversation capture

set -e

echo "🚀 Setting up Cursor Integration for AI Dev Tasks"
echo "=================================================="

# Check if Cursor is installed
if ! command -v cursor &> /dev/null; then
    echo "❌ Cursor is not installed or not in PATH"
    echo "   Please install Cursor from https://cursor.sh/"
    exit 1
fi

echo "✅ Cursor found: $(which cursor)"

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed or not in PATH"
    echo "   Please install uv: pip install uv"
    exit 1
fi

echo "✅ uv found: $(which uv)"

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 &> /dev/null; then
    echo "⚠️  PostgreSQL is not running on localhost:5432"
    echo "   Please start PostgreSQL before using the integration"
fi

# Create .vscode directory if it doesn't exist
mkdir -p .vscode

# Make scripts executable
chmod +x scripts/utilities/cursor_commands.sh
chmod +x scripts/utilities/cursor_mcp_capture.py

echo "✅ Scripts made executable"

# Test the MCP server
echo "🧪 Testing MCP server..."
if curl -s http://localhost:3000/health > /dev/null; then
    echo "✅ MCP server is running"
else
    echo "⚠️  MCP server is not running. Starting it..."
    export POSTGRES_DSN="postgresql://danieljacobs@localhost:5432/ai_agency"
    nohup uv run python scripts/utilities/mcp_memory_server.py > mcp_server.log 2>&1 &
    sleep 3
    
    if curl -s http://localhost:3000/health > /dev/null; then
        echo "✅ MCP server started successfully"
    else
        echo "❌ Failed to start MCP server. Check mcp_server.log for details"
        exit 1
    fi
fi

# Test conversation capture
echo "🧪 Testing conversation capture..."
export POSTGRES_DSN="postgresql://danieljacobs@localhost:5432/ai_agency"
test_result=$(uv run python scripts/utilities/cursor_mcp_capture.py --capture-query "Test setup query" --metadata '{"source": "setup_test"}')

if echo "$test_result" | grep -q '"success": true'; then
    echo "✅ Conversation capture test passed"
else
    echo "❌ Conversation capture test failed:"
    echo "$test_result"
    exit 1
fi

echo ""
echo "🎉 Cursor Integration Setup Complete!"
echo "====================================="
echo ""
echo "📋 What was configured:"
echo "  ✅ MCP server configuration in ~/.cursor/mcp.json"
echo "  ✅ Conversation capture scripts"
echo "  ✅ VS Code/Cursor tasks and keybindings"
echo "  ✅ MCP server running on http://localhost:3000"
echo ""
echo "🔧 How to use:"
echo "  1. Restart Cursor to load the MCP configuration"
echo "  2. Use Command Palette (Cmd+Shift+P) to run tasks:"
echo "     - 'Capture Conversation Turn'"
echo "     - 'Capture User Query'"
echo "     - 'Capture AI Response'"
echo "     - 'Get Session Stats'"
echo "     - 'Close Session'"
echo ""
echo "⌨️  Keyboard shortcuts:"
echo "  Cmd+Shift+C, Cmd+Shift+T  - Capture conversation turn"
echo "  Cmd+Shift+C, Cmd+Shift+Q  - Capture user query"
echo "  Cmd+Shift+C, Cmd+Shift+R  - Capture AI response"
echo "  Cmd+Shift+C, Cmd+Shift+S  - Get session stats"
echo "  Cmd+Shift+C, Cmd+Shift+X  - Close session"
echo ""
echo "🌐 MCP Server:"
echo "  Health: http://localhost:3000/health"
echo "  Tools:  http://localhost:3000/mcp/tools"
echo ""
echo "📝 Manual capture commands:"
echo "  ./scripts/utilities/cursor_commands.sh capture-turn 'query' 'response'"
echo "  ./scripts/utilities/cursor_commands.sh capture-query 'query'"
echo "  ./scripts/utilities/cursor_commands.sh capture-response 'response'"
echo ""
echo "✨ Ready to capture conversations from Cursor!"

