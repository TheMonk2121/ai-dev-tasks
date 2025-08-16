#!/bin/bash
# Sleep Nemo - Unified Shutdown Script
#
# This script stops all visualization components and dashboards
# for the chunk relationship visualization system.
#
# Usage: ./sleep_nemo.sh [options]
# Options:
#   --flask-only     Stop only Flask dashboard
#   --nicegui-only   Stop only NiceGUI graph visualization
#   --all            Stop all components (default)
#   --force          Force kill processes
#   --help           Show this help message

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FLASK_PORT=5000
NICEGUI_PORT=8080

# Function to print colored output
print_status() {
    echo -e "${GREEN}[NEMO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[NEMO]${NC} $1"
}

print_error() {
    echo -e "${RED}[NEMO]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[NEMO]${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port="$1"
    if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is available
    fi
}

# Function to stop Flask dashboard
stop_flask_dashboard() {
    print_status "Stopping Flask Dashboard..."

    # Try to stop using PID file first
    if [ -f "dspy-rag-system/flask_dashboard.pid" ]; then
        local pid
        pid=$(cat dspy-rag-system/flask_dashboard.pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            print_status "Sent SIGTERM to Flask Dashboard (PID: $pid)"

            # Wait for graceful shutdown
            local attempts=0
            while kill -0 "$pid" 2>/dev/null && [ $attempts -lt 10 ]; do
                sleep 1
                attempts=$((attempts + 1))
            done

            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                if [ "$FORCE_KILL" = "true" ]; then
                    kill -9 "$pid"
                    print_warning "Force killed Flask Dashboard (PID: $pid)"
                else
                    print_warning "Flask Dashboard still running. Use --force to kill."
                fi
            else
                print_status "Flask Dashboard stopped gracefully"
            fi
        fi
        rm -f dspy-rag-system/flask_dashboard.pid
    fi

    # Also try to kill by port if still running
    if check_port $FLASK_PORT; then
        local pids
        pids=$(lsof -ti:$FLASK_PORT)
        if [ -n "$pids" ]; then
            if [ "$FORCE_KILL" = "true" ]; then
                echo "$pids" | xargs kill -9
                print_warning "Force killed processes on port $FLASK_PORT"
            else
                echo "$pids" | xargs kill
                print_status "Sent SIGTERM to processes on port $FLASK_PORT"
            fi
        fi
    fi
}

# Function to stop NiceGUI graph visualization
stop_nicegui_graph() {
    print_status "Stopping NiceGUI Graph Visualization..."

    # Try to stop using PID file first
    if [ -f "dspy-rag-system/nicegui_graph.pid" ]; then
        local pid
        pid=$(cat dspy-rag-system/nicegui_graph.pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            print_status "Sent SIGTERM to NiceGUI Graph (PID: $pid)"

            # Wait for graceful shutdown
            local attempts=0
            while kill -0 "$pid" 2>/dev/null && [ $attempts -lt 10 ]; do
                sleep 1
                attempts=$((attempts + 1))
            done

            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                if [ "$FORCE_KILL" = "true" ]; then
                    kill -9 "$pid"
                    print_warning "Force killed NiceGUI Graph (PID: $pid)"
                else
                    print_warning "NiceGUI Graph still running. Use --force to kill."
                fi
            else
                print_status "NiceGUI Graph stopped gracefully"
            fi
        fi
        rm -f dspy-rag-system/nicegui_graph.pid
    fi

    # Also try to kill by port if still running
    if check_port $NICEGUI_PORT; then
        local pids
        pids=$(lsof -ti:$NICEGUI_PORT)
        if [ -n "$pids" ]; then
            if [ "$FORCE_KILL" = "true" ]; then
                echo "$pids" | xargs kill -9
                print_warning "Force killed processes on port $NICEGUI_PORT"
            else
                echo "$pids" | xargs kill
                print_status "Sent SIGTERM to processes on port $NICEGUI_PORT"
            fi
        fi
    fi
}

# Function to show status
show_status() {
    print_status "Nemo System Status:"
    echo

    if check_port $FLASK_PORT; then
        print_warning "⚠️  Flask Dashboard: Still running on port $FLASK_PORT"
    else
        print_status "✅ Flask Dashboard: Stopped"
    fi

    if check_port $NICEGUI_PORT; then
        print_warning "⚠️  NiceGUI Graph: Still running on port $NICEGUI_PORT"
    else
        print_status "✅ NiceGUI Graph: Stopped"
    fi

    echo
    print_info "Log files:"
    print_info "  Flask: dspy-rag-system/flask_dashboard.log"
    print_info "  NiceGUI: dspy-rag-system/nicegui_graph.log"
}

# Function to show help
show_help() {
    echo "Sleep Nemo - Unified Shutdown Script"
    echo
    echo "Usage: ./sleep_nemo.sh [options]"
    echo
    echo "Options:"
    echo "  --flask-only     Stop only Flask dashboard"
    echo "  --nicegui-only   Stop only NiceGUI graph visualization"
    echo "  --all            Stop all components (default)"
    echo "  --force          Force kill processes (use SIGKILL)"
    echo "  --status         Show current status of all components"
    echo "  --help           Show this help message"
    echo
    echo "Examples:"
    echo "  ./sleep_nemo.sh              # Stop everything gracefully"
    echo "  ./sleep_nemo.sh --force      # Force stop everything"
    echo "  ./sleep_nemo.sh --flask-only # Stop only Flask dashboard"
    echo "  ./sleep_nemo.sh --status     # Check what's still running"
}

# Main script logic
main() {
    print_status "😴 Putting Nemo to sleep..."
    echo

    # Parse command line arguments
    FORCE_KILL=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --flask-only)
                print_info "Stopping Flask Dashboard only..."
                stop_flask_dashboard
                shift
                ;;
            --nicegui-only)
                print_info "Stopping NiceGUI Graph only..."
                stop_nicegui_graph
                shift
                ;;
            --all)
                print_info "Stopping all components..."
                stop_flask_dashboard
                stop_nicegui_graph
                shift
                ;;
            --force)
                FORCE_KILL=true
                shift
                ;;
            --status)
                show_status
                exit 0
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Default behavior: stop all
    if [ $# -eq 0 ]; then
        print_info "Stopping all components..."
        stop_flask_dashboard
        stop_nicegui_graph
    fi

    echo
    print_status "💤 Nemo is sleeping..."
    echo
    show_status
}

# Run main function
main "$@"
