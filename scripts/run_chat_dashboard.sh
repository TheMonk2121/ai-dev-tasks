#!/bin/bash
# Multi-Agent Chat Dashboard Startup Script
# Starts the backend bridge (8004) and a web UI (simple:8006 or fancy:8005)

echo "🚀 Starting Multi-Agent Chat Dashboard System"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "scripts/multi_agent_chat.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Use uv-managed project environment
export UV_PROJECT_ENVIRONMENT=.venv

# Kill any existing processes on these apps
echo "🧹 Cleaning up existing processes..."
pkill -f "multi_agent_chat.py" 2>/dev/null || true
pkill -f "simple_chat_web.py" 2>/dev/null || true
pkill -f "chat_web_interface.py" 2>/dev/null || true
sleep 2

# Start the backend bridge (port 8004)
echo "🔧 Starting backend bridge on port 8004..."
uv run python scripts/multi_agent_chat.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! curl -s http://localhost:8004/health > /dev/null; then
    echo "❌ Backend failed to start. Check the logs above."
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Backend bridge is running on port 8004"

# Choose UI: simple (default) or fancy
UI_MODE="simple"
if [ $# -ge 1 ]; then
  case "$1" in
    simple|fancy) UI_MODE="$1" ;;
    *) echo "⚠️  Unknown UI '$1' — using 'simple' (valid: simple|fancy)" ;;
  esac
fi

if [ "$UI_MODE" = "fancy" ]; then
  echo "🌐 Starting fancy dashboard on port 8005..."
  uv run python scripts/chat_web_interface.py &
  DASHBOARD_PID=$!
  DASHBOARD_PORT=8005
else
  echo "🌐 Starting simple dashboard on port 8006..."
  uv run python scripts/simple_chat_web.py &
  DASHBOARD_PID=$!
  DASHBOARD_PORT=8006
fi

# Wait a moment for dashboard to start
sleep 3

# Check if dashboard started successfully
if ! curl -s "http://localhost:${DASHBOARD_PORT}/health" > /dev/null; then
    echo "❌ Dashboard failed to start on ${DASHBOARD_PORT}. Check the logs above."
    kill $BACKEND_PID $DASHBOARD_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Dashboard is running on port ${DASHBOARD_PORT}"

echo ""
echo "🎉 Multi-Agent Chat System is ready!"
echo "====================================="
echo "📡 Backend Bridge:   http://localhost:8004"
echo "🌐 Dashboard:        http://localhost:${DASHBOARD_PORT}"
echo "🔧 Health Check:     http://localhost:8004/health"
echo "📊 Dashboard Health: http://localhost:${DASHBOARD_PORT}/health"
echo ""
echo "🤖 Open http://localhost:8006 in your browser to start chatting!"
echo ""
echo "💡 Tips:"
echo "   - Use 'Connect as User/Codex/Cursor' buttons"
echo "   - Open multiple browser tabs to simulate multiple agents"
echo "   - Terminal client: uv run python scripts/terminal_chat_client.py [agent]"
echo ""
echo "🛑 To stop: Press Ctrl+C or run 'pkill -f multi_agent_chat.py && pkill -f \"simple_chat_web.py|chat_web_interface.py\"'"
echo ""

# Keep the script running and show logs
echo "📋 Live logs (Press Ctrl+C to stop all services):"
echo "=================================================="

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $DASHBOARD_PID 2>/dev/null || true
    pkill -f "multi_agent_chat.py" 2>/dev/null || true
    pkill -f "simple_chat_web.py" 2>/dev/null || true
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for processes
wait $BACKEND_PID $DASHBOARD_PID
