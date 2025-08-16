#!/bin/bash
# Wake Up Nemo - Unified Startup Script
#
# This script launches all visualization components and dashboards
# for the chunk relationship visualization system.
#
# Usage: ./wake_up_nemo.sh [options]
# Options:
#   --flask-only     Start only Flask dashboard
#   --nicegui-only   Start only NiceGUI graph visualization
#   --api-only       Start only API server (for testing)
#   --all            Start all components (default)
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
WATCH_FOLDER_PORT=5001
MONITORING_PORT=5003
DASHBOARD_URL="http://localhost:${FLASK_PORT}"
NICEGUI_URL="http://localhost:${NICEGUI_PORT}"
WATCH_FOLDER_URL="http://localhost:${WATCH_FOLDER_PORT}"
MONITORING_URL="http://localhost:${MONITORING_PORT}"

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

# Function to check if a port is available
check_port() {
    local port="$1"
    if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is available
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1

    print_info "Waiting for $service_name to be ready..."

    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url/api/health" >/dev/null 2>&1; then
            print_status "$service_name is ready!"
            return 0
        fi

        print_info "Attempt $attempt/$max_attempts - waiting for $service_name..."
        sleep 2
        attempt=$((attempt + 1))
    done

    print_error "$service_name failed to start within expected time"
    return 1
}

# Function to start Flask dashboard
start_flask_dashboard() {
    print_status "Starting Flask Dashboard..."

    if check_port $FLASK_PORT; then
        print_warning "Port $FLASK_PORT is already in use. Flask dashboard may already be running."
        return 0
    fi

    # Start Flask dashboard in background
    cd dspy-rag-system
    nohup ./start_mission_dashboard.sh > flask_dashboard.log 2>&1 &
    FLASK_PID=$!
    echo $FLASK_PID > flask_dashboard.pid

    print_status "Flask Dashboard started with PID: $FLASK_PID"
    print_info "Dashboard URL: $DASHBOARD_URL"
    print_info "Cluster Visualization: $DASHBOARD_URL/cluster"
    print_info "API Endpoint: $DASHBOARD_URL/graph-data"

    # Wait for Flask to be ready
    wait_for_service $DASHBOARD_URL "Flask Dashboard"
}

# Function to start NiceGUI graph visualization
start_nicegui_graph() {
    print_status "Starting NiceGUI Graph Visualization..."

    if check_port $NICEGUI_PORT; then
        print_warning "Port $NICEGUI_PORT is already in use. NiceGUI may already be running."
        return 0
    fi

    # Check if Flask dashboard is running
    if ! check_port $FLASK_PORT; then
        print_error "Flask dashboard must be running first. Please start it with --flask-only first."
        return 1
    fi

    # Start NiceGUI in background
    cd dspy-rag-system
    nohup ./start_graph_visualization.sh > nicegui_graph.log 2>&1 &
    NICEGUI_PID=$!
    echo $NICEGUI_PID > nicegui_graph.pid

    print_status "NiceGUI Graph Visualization started with PID: $NICEGUI_PID"
    print_info "Graph URL: $NICEGUI_URL"
    print_info "Dashboard Link: Available in the NiceGUI interface"

    # Wait for NiceGUI to be ready
    sleep 3
    if curl -s "$NICEGUI_URL" >/dev/null 2>&1; then
        print_status "NiceGUI Graph Visualization is ready!"
    else
        print_warning "NiceGUI may still be starting up..."
    fi
}

# Function to start watch folder service
start_watch_folder() {
    print_status "Starting Watch Folder Service..."

    # Check if watch folder is already running
    if pgrep -f "watch_folder.py" > /dev/null; then
        print_warning "Watch folder service is already running."
        return 0
    fi

    # Check if watch folder directory exists
    if [ ! -d "watch_folder" ]; then
        print_info "Creating watch folder directory..."
        mkdir -p watch_folder
        mkdir -p processed_documents
    fi

    # Start watch folder in background
    cd dspy-rag-system
    nohup python3 src/watch_folder.py > watch_folder.log 2>&1 &
    WATCH_PID=$!
    echo $WATCH_PID > watch_folder.pid

    print_status "Watch Folder Service started with PID: $WATCH_PID"
    print_info "Watch folder: $(pwd)/watch_folder"
    print_info "Processed documents: $(pwd)/processed_documents"
    print_info "Logs: watch_folder.log"

    # Wait a moment for service to start
    sleep 2
    if pgrep -f "watch_folder.py" > /dev/null; then
        print_status "✅ Watch Folder Service is ready!"
    else
        print_error "❌ Watch Folder Service failed to start"
        return 1
    fi
}

# Function to check database health
check_database_health() {
    print_status "Checking database health..."

    # Check if PostgreSQL is running
    if ! pgrep -f "postgres" > /dev/null; then
        print_error "❌ PostgreSQL is not running"
        print_warning "Please start PostgreSQL before running Nemo"
        return 1
    fi

    # Check database connection
    if psql -d ai_agency -c "SELECT COUNT(*) as total_chunks FROM document_chunks;" >/dev/null 2>&1; then
        print_status "✅ Database connected and accessible"

        # Get chunk count
        local chunk_count
        chunk_count=$(psql -d ai_agency -t -c "SELECT COUNT(*) FROM document_chunks;" 2>/dev/null | tr -d ' ')
        print_info "Total document chunks: ${chunk_count:-0}"
    else
        print_error "❌ Database connection failed"
        print_warning "Please check PostgreSQL configuration and ai_agency database"
        return 1
    fi
}

# Function to start production monitoring
start_production_monitoring() {
    print_status "Starting Production Monitoring..."

    if check_port $MONITORING_PORT; then
        print_warning "Port $MONITORING_PORT is already in use. Monitoring may already be running."
        return 0
    fi

    # Start monitoring in background
    cd dspy-rag-system
    nohup python3 src/monitoring/production_monitor.py > production_monitor.log 2>&1 &
    MONITOR_PID=$!
    echo $MONITOR_PID > production_monitor.pid

    print_status "Production Monitoring started with PID: $MONITOR_PID"
    print_info "Monitoring URL: $MONITORING_URL"
    print_info "Health endpoint: $MONITORING_URL/health"
    print_info "Metrics endpoint: $MONITORING_URL/metrics"

    # Wait for monitoring to be ready
    sleep 3
    if curl -s "$MONITORING_URL/health" >/dev/null 2>&1; then
        print_status "✅ Production Monitoring is ready!"
    else
        print_warning "⚠️  Production Monitoring may still be starting up..."
    fi
}

# Function to test API endpoint
test_api() {
    print_status "Testing API endpoint..."

    if ! check_port $FLASK_PORT; then
        print_error "Flask dashboard is not running. Cannot test API."
        return 1
    fi

    local response
    response=$(curl -s "$DASHBOARD_URL/graph-data?max_nodes=10" 2>/dev/null)
    if echo "$response" | grep -q '"nodes"'; then
        print_status "API endpoint is working correctly!"
        print_info "Sample response: $(echo "$response" | jq -r '.nodes | length') nodes, $(echo "$response" | jq -r '.edges | length') edges"
    else
        print_error "API endpoint test failed"
        return 1
    fi
}

# Function to show status
show_status() {
    print_status "Nemo System Status:"
    echo

    # Database health
    if psql -d ai_agency -c "SELECT 1;" >/dev/null 2>&1; then
        print_status "✅ Database: Connected and healthy"
        local chunk_count
        chunk_count=$(psql -d ai_agency -t -c "SELECT COUNT(*) FROM document_chunks;" 2>/dev/null | tr -d ' ')
        print_info "   Document chunks: ${chunk_count:-0}"
    else
        print_error "❌ Database: Not accessible"
    fi

    # Watch folder service
    if pgrep -f "watch_folder.py" > /dev/null; then
        print_status "✅ Watch Folder: Running"
        print_info "   Drop files into: dspy-rag-system/watch_folder"
    else
        print_error "❌ Watch Folder: Not running"
    fi

    # Flask dashboard
    if check_port $FLASK_PORT; then
        print_status "✅ Flask Dashboard: Running on port $FLASK_PORT"
        print_info "   URL: $DASHBOARD_URL"
        print_info "   Cluster: $DASHBOARD_URL/cluster"
    else
        print_error "❌ Flask Dashboard: Not running"
    fi

    # NiceGUI graph
    if check_port $NICEGUI_PORT; then
        print_status "✅ NiceGUI Graph: Running on port $NICEGUI_PORT"
        print_info "   URL: $NICEGUI_URL"
    else
        print_error "❌ NiceGUI Graph: Not running"
    fi

    # Production monitoring
    if check_port $MONITORING_PORT; then
        print_status "✅ Production Monitoring: Running on port $MONITORING_PORT"
        print_info "   URL: $MONITORING_URL"
        print_info "   Health: $MONITORING_URL/health"
    else
        print_error "❌ Production Monitoring: Not running"
    fi

    echo
    print_info "Quick Commands:"
    print_info "  Test API: curl '$DASHBOARD_URL/graph-data?max_nodes=10'"
    print_info "  Stop all: ./sleep_nemo.sh"
    print_info "  View logs: tail -f dspy-rag-system/flask_dashboard.log"
    print_info "  View logs: tail -f dspy-rag-system/nicegui_graph.log"
    print_info "  View logs: tail -f dspy-rag-system/watch_folder.log"
    print_info "  View logs: tail -f dspy-rag-system/production_monitor.log"
}

# Function to refresh memory context
refresh_memory() {
    print_status "🧠 Refreshing memory context..."

    # Check if we're in the right directory
    if [ ! -f "scripts/prime_cursor_chat.py" ]; then
        print_warning "Memory refresh scripts not found. Skipping memory refresh."
        return 0
    fi

    # Try Python implementation first (more reliable)
    if command -v python3 >/dev/null 2>&1; then
        print_info "Running memory refresh with Python implementation..."
        cd ..
        if python3 scripts/prime_cursor_chat.py planner "current project status and core documentation" > memory_refresh_output.txt 2>&1; then
            print_status "✅ Memory context refreshed successfully!"
            print_info "Memory bundle saved to: memory_refresh_output.txt"
            print_info "Copy the bundle content into your Cursor chat for context"
        else
            print_warning "⚠️  Memory refresh completed with warnings (check memory_refresh_output.txt)"
        fi
        cd dspy-rag-system
    else
        print_warning "Python3 not found. Skipping memory refresh."
    fi
}

# Function to show help
show_help() {
    echo "Wake Up Nemo - Unified Startup Script"
    echo
    echo "Usage: ./wake_up_nemo.sh [options]"
    echo
    echo "Options:"
    echo "  --flask-only     Start only Flask dashboard"
    echo "  --nicegui-only   Start only NiceGUI graph visualization"
    echo "  --watch-only     Start only Watch Folder Service"
    echo "  --monitoring-only Start only Production Monitoring"
    echo "  --api-only       Start only API server (for testing)"
    echo "  --all            Start all components (default)"
    echo "  --refresh        Refresh memory context before starting services"
    echo "  --memory-only    Refresh memory context only (don't start services)"
    echo "  --status         Show current status of all components"
    echo "  --test           Test API endpoint"
    echo "  --help           Show this help message"
    echo
    echo "Examples:"
    echo "  ./wake_up_nemo.sh              # Start everything"
    echo "  ./wake_up_nemo.sh --refresh    # Refresh memory + start everything"
    echo "  ./wake_up_nemo.sh --memory-only # Refresh memory context only"
    echo "  ./wake_up_nemo.sh --watch-only # Start only Watch Folder Service"
    echo "  ./wake_up_nemo.sh --flask-only # Start only Flask dashboard"
    echo "  ./wake_up_nemo.sh --status     # Check what's running"
    echo "  ./wake_up_nemo.sh --test       # Test API functionality"
}

# Function to cleanup on exit
cleanup() {
    print_info "Shutting down Nemo..."

    # Kill background processes
    if [ -f "dspy-rag-system/flask_dashboard.pid" ]; then
        local pid
        pid=$(cat dspy-rag-system/flask_dashboard.pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            print_status "Stopped Flask Dashboard (PID: $pid)"
        fi
        rm -f dspy-rag-system/flask_dashboard.pid
    fi

    if [ -f "dspy-rag-system/nicegui_graph.pid" ]; then
        local pid
        pid=$(cat dspy-rag-system/nicegui_graph.pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            print_status "Stopped NiceGUI Graph (PID: $pid)"
        fi
        rm -f dspy-rag-system/nicegui_graph.pid
    fi

    if [ -f "dspy-rag-system/watch_folder.pid" ]; then
        local pid
        pid=$(cat dspy-rag-system/watch_folder.pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            print_status "Stopped Watch Folder Service (PID: $pid)"
        fi
        rm -f dspy-rag-system/watch_folder.pid
    fi

    if [ -f "dspy-rag-system/production_monitor.pid" ]; then
        local pid
        pid=$(cat dspy-rag-system/production_monitor.pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            print_status "Stopped Production Monitoring (PID: $pid)"
        fi
        rm -f dspy-rag-system/production_monitor.pid
    fi

    # Also kill any remaining watch folder processes
    if pgrep -f "watch_folder.py" > /dev/null; then
        pkill -f "watch_folder.py"
        print_status "Stopped any remaining watch folder processes"
    fi
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Main script logic
main() {
    print_status "🐙 Waking up Nemo..."
    echo

    # Check for refresh flag
    REFRESH_MEMORY=false
    if [[ "$1" == "--refresh" ]]; then
        REFRESH_MEMORY=true
        shift  # Remove --refresh from arguments
    fi

    # Check database health first (critical for all operations)
    if ! check_database_health; then
        print_error "❌ Database health check failed. Please fix database issues before continuing."
        exit 1
    fi

    # Refresh memory if requested
    if [ "$REFRESH_MEMORY" = true ]; then
        refresh_memory
        echo
    fi

    # Parse command line arguments
    case "${1:---all}" in
        --flask-only)
            print_info "Starting Flask Dashboard only..."
            start_flask_dashboard
            ;;
        --nicegui-only)
            print_info "Starting NiceGUI Graph only..."
            start_nicegui_graph
            ;;
        --watch-only)
            print_info "Starting Watch Folder Service only..."
            start_watch_folder
            ;;
        --monitoring-only)
            print_info "Starting Production Monitoring only..."
            start_production_monitoring
            ;;
        --api-only)
            print_info "Starting API server only..."
            start_flask_dashboard
            ;;
        --all)
            print_info "Starting all components..."
            start_watch_folder
            sleep 2
            start_flask_dashboard
            sleep 2
            start_nicegui_graph
            sleep 2
            start_production_monitoring
            ;;
        --status)
            show_status
            exit 0
            ;;
        --test)
            test_api
            exit 0
            ;;
        --memory-only)
            print_info "Refreshing memory context only..."
            refresh_memory
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

    echo
    print_status "🎉 Nemo is awake and ready!"
    echo
    show_status
    echo
    print_info "Press Ctrl+C to stop all services"

    # Keep script running to maintain background processes
    while true; do
        sleep 10
    done
}

# Run main function
main "$@"
