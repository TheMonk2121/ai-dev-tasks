#!/bin/bash
# Cursor Command Palette Integration Scripts
# These can be called from Cursor's command palette or as external commands

# Set up environment
export POSTGRES_DSN="postgresql://danieljacobs@localhost:5432/ai_agency"
cd /Users/danieljacobs/Code/ai-dev-tasks || exit 1

# Function to capture conversation turn
capture_turn() {
    local query="$1"
    local response="$2"
    local metadata="${3:-{}}"
    
    uv run python scripts/utilities/cursor_mcp_capture.py \
        --capture-turn "$query" "$response" \
        --metadata "$metadata"
}

# Function to capture user query only
capture_query() {
    local query="$1"
    local metadata="${2:-{}}"
    
    uv run python scripts/utilities/cursor_mcp_capture.py \
        --capture-query "$query" \
        --metadata "$metadata"
}

# Function to capture AI response only
capture_response() {
    local response="$1"
    local query_turn_id="$2"
    local metadata="${3:-{}}"
    
    uv run python scripts/utilities/cursor_mcp_capture.py \
        --capture-response "$response" \
        --query-turn-id "$query_turn_id" \
        --metadata "$metadata"
}

# Function to get session stats
get_stats() {
    uv run python scripts/utilities/cursor_mcp_capture.py --stats
}

# Function to close session
close_session() {
    uv run python scripts/utilities/cursor_mcp_capture.py --close
}

# Main command dispatcher
case "$1" in
    "capture-turn")
        capture_turn "$2" "$3" "$4"
        ;;
    "capture-query")
        capture_query "$2" "$3"
        ;;
    "capture-response")
        capture_response "$2" "$3" "$4"
        ;;
    "stats")
        get_stats
        ;;
    "close")
        close_session
        ;;
    *)
        echo "Usage: $0 {capture-turn|capture-query|capture-response|stats|close} [args...]"
        echo ""
        echo "Commands:"
        echo "  capture-turn <query> <response> [metadata]  - Capture complete conversation turn"
        echo "  capture-query <query> [metadata]            - Capture user query only"
        echo "  capture-response <response> [turn_id] [metadata] - Capture AI response only"
        echo "  stats                                       - Get session statistics"
        echo "  close                                       - Close current session"
        exit 1
        ;;
esac

