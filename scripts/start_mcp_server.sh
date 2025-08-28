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

# Default port and fallback range
DEFAULT_PORT=${1:-3000}
FALLBACK_START=3000
FALLBACK_END=3010

# Ensure we use Python 3.12
PYTHON_CMD="python3.12"
if ! command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_CMD="python3"
    echo "⚠️  python3.12 not found, using python3"
fi

echo "🚀 Starting MCP Memory Rehydrator Server..."
echo "🐍 Python: $($PYTHON_CMD --version)"
echo "📡 Default Port: $DEFAULT_PORT"
echo "🔄 Fallback Range: $FALLBACK_START-$FALLBACK_END"
echo ""

# Function to find available port
find_available_port() {
    local start_port=$1
    local end_port=$2

    for port in $(seq $start_port $end_port); do
        if ! lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "$port"
            return 0
        fi
    done
    return 1
}

# Try default port first
if ! lsof -Pi :"$DEFAULT_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    PORT=$DEFAULT_PORT
    echo "✅ Default port $PORT is available"
else
    echo "⚠️  Default port $DEFAULT_PORT is already in use!"
    echo "🔄 Searching for available port in range $FALLBACK_START-$FALLBACK_END..."

    # Find available port in fallback range
    PORT=$(find_available_port $FALLBACK_START $FALLBACK_END)

    if [ $? -eq 0 ]; then
        echo "✅ Found available port: $PORT"
    else
        echo "❌ No available ports found in range $FALLBACK_START-$FALLBACK_END"
        echo "   Please stop conflicting processes or specify a different port:"
        echo "   ./scripts/start_mcp_server.sh 3011"
        exit 1
    fi
fi

echo "🔗 URL: http://localhost:$PORT/mcp"
echo ""

# Start the server
echo "✅ Starting server on port $PORT..."
echo "   Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")/.."
$PYTHON_CMD scripts/mcp_memory_server.py --port "$PORT"
