#!/bin/bash
# Start MCP Memory Rehydrator Server
# ==================================
# Quick script to start the MCP server for automatic memory rehydration in Cursor.
#
# Usage:
#     ./scripts/start_mcp_server.sh [port]
#
# Default port: 3000

set -e

# Default port
PORT=${1:-3000}

echo "🚀 Starting MCP Memory Rehydrator Server..."
echo "📡 Port: $PORT"
echo "🔗 URL: http://localhost:$PORT/mcp"
echo ""

# Check if port is already in use
if lsof -Pi :"$PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port $PORT is already in use!"
    echo "   Either stop the existing process or use a different port:"
    echo "   ./scripts/start_mcp_server.sh 3001"
    exit 1
fi

# Start the server
echo "✅ Starting server on port $PORT..."
echo "   Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")/.."
python3 scripts/mcp_memory_server.py --port "$PORT"
