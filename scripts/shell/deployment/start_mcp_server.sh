#!/bin/bash
# Start MCP Memory Server
# ======================

set -e

echo "🚀 Starting MCP Memory Server..."

# Get the project root (go up from scripts/shell/deployment to project root)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$PROJECT_ROOT"

# Use uv-managed environment
export UV_PROJECT_ENVIRONMENT=.venv

# Set environment variables
export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT/scripts:$PYTHONPATH"
export POSTGRES_DSN="${POSTGRES_DSN:-postgresql://danieljacobs@localhost:5432/ai_agency}"

# Default port
PORT=${PORT:-3000}

# Check if port is available
if lsof -i :"$PORT" >/dev/null 2>&1; then
    echo "⚠️  Port $PORT is already in use, trying next available port..."
    for ((i=PORT; i<=PORT+10; i++)); do
        if ! lsof -i :"$i" >/dev/null 2>&1; then
            PORT=$i
            echo "✅ Using port $PORT"
            break
        fi
    done
else
    echo "✅ Port $PORT is available"
fi

# Start the server
echo "🚀 Starting MCP Memory Server on port $PORT..."
echo "📡 Health check: http://localhost:$PORT/health"
echo "🔧 MCP tools: http://localhost:$PORT/mcp/tools"
echo ""

uv run python scripts/utilities/memory/mcp_memory_server.py --port "$PORT"
