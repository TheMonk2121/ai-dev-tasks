#!/bin/bash

# MCP Orchestration Gateway Startup Script
# Provides load balancing, failover, and intelligent routing for multiple MCP servers

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEFAULT_PORT=3002
FALLBACK_START=3002
FALLBACK_END=3010

# Python command
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
else
    PYTHON_CMD="python3"
fi

echo "🚀 Starting MCP Orchestration Gateway..."
echo "🐍 Python: $($PYTHON_CMD --version)"
echo "📡 Default Port: $DEFAULT_PORT"
echo "🔄 Fallback Range: $FALLBACK_START-$FALLBACK_END"

# Function to find available port
find_available_port() {
    local start_port=$1
    local end_port=$2

    for port in $(seq "$start_port" "$end_port"); do
        if ! lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "$port"
            return 0
        fi
    done
    return 1
}

# Check if default port is available
if lsof -Pi :"$DEFAULT_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Default port $DEFAULT_PORT is already in use!"
    echo "🔄 Searching for available port in range $FALLBACK_START-$FALLBACK_END..."

    if PORT=$(find_available_port "$FALLBACK_START" "$FALLBACK_END"); then
        echo "✅ Found available port: $PORT"
    else
        echo "❌ No available ports found in range $FALLBACK_START-$FALLBACK_END"
        exit 1
    fi
else
    PORT=$DEFAULT_PORT
    echo "✅ Default port $PORT is available"
fi

echo "🔗 URL: http://localhost:$PORT/orchestration/dashboard"
echo "✅ Starting gateway on port $PORT..."

# Activate virtual environment if it exists
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$PROJECT_ROOT/venv/bin/activate"
    echo "🐍 Virtual environment activated"
fi

# Start the orchestration gateway
cd "$PROJECT_ROOT"
$PYTHON_CMD scripts/mcp_orchestration_gateway.py --port "$PORT"
