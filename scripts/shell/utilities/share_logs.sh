#!/bin/bash
# Share MCP Server Logs with Cursor and Codex

echo "🔍 MCP Server Log Sharing"
echo "========================="

# Function to show recent logs
show_logs() {
    echo "📋 Recent MCP Server Logs:"
    echo "-------------------------"

    if [ -f ".mcp-server.out" ]; then
        echo "📤 STDOUT (.mcp-server.out):"
        tail -20 .mcp-server.out
        echo ""
    fi

    if [ -f ".mcp-server.err" ]; then
        echo "📥 STDERR (.mcp-server.err):"
        tail -20 .mcp-server.err
        echo ""
    fi

    echo "🔧 MCP Server Process:"
    pgrep -f mcp_memory_server
    echo ""

    echo "🌐 Server Status:"
    curl -s http://localhost:3000/health | jq '.' 2>/dev/null || echo "Server not responding"
    echo ""
}

# Function to stream logs
stream_logs() {
    echo "📡 Streaming MCP Server Logs (Ctrl+C to stop)..."
    echo "================================================"

    # Start log monitor in background
    bin/py scripts/log_monitor.py &
    MONITOR_PID=$!

    # Wait a moment for server to start
    sleep 2

    echo "🔗 Log Monitor running on:"
    echo "  - Recent logs: http://localhost:8001/logs"
    echo "  - Stream logs: http://localhost:8001/logs/stream"
    echo "  - WebSocket: ws://localhost:8001/ws/logs"
    echo ""

    # Show initial logs
    show_logs

    # Stream logs
    tail -f .mcp-server.out .mcp-server.err &
    TAIL_PID=$!

    # Wait for interrupt
    trap 'kill $MONITOR_PID $TAIL_PID 2>/dev/null; exit' INT
    wait
}

# Function to create log summary
create_summary() {
    echo "📊 Creating Log Summary..."

    SUMMARY_FILE="mcp_logs_summary_$(date +%Y%m%d_%H%M%S).txt"

    {
        echo "MCP Server Log Summary - $(date)"
        echo "================================="
        echo ""

        echo "Server Health:"
        curl -s http://localhost:3000/health | jq '.' 2>/dev/null || echo "Server not responding"
        echo ""

        echo "Recent STDOUT:"
        if [ -f ".mcp-server.out" ]; then
            tail -50 .mcp-server.out
        else
            echo "No stdout log file found"
        fi
        echo ""

        echo "Recent STDERR:"
        if [ -f ".mcp-server.err" ]; then
            tail -50 .mcp-server.err
        else
            echo "No stderr log file found"
        fi
        echo ""

        echo "Process Info:"
        pgrep -f mcp_memory_server
        echo ""

    } > "$SUMMARY_FILE"

    echo "✅ Log summary created: $SUMMARY_FILE"
    echo "📋 Summary preview:"
    head -20 "$SUMMARY_FILE"
}

# Main menu
case "${1:-show}" in
    "show")
        show_logs
        ;;
    "stream")
        stream_logs
        ;;
    "summary")
        create_summary
        ;;
    "monitor")
        echo "🚀 Starting Log Monitor Server..."
        bin/py scripts/log_monitor.py
        ;;
    *)
        echo "Usage: $0 [show|stream|summary|monitor]"
        echo ""
        echo "Commands:"
        echo "  show     - Show recent logs (default)"
        echo "  stream   - Stream logs in real-time"
        echo "  summary  - Create log summary file"
        echo "  monitor  - Start log monitor server"
        echo ""
        show_logs
        ;;
esac
