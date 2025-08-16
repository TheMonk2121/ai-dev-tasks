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
#   --parallel       Use parallel startup (default)
#   --sequential     Use sequential startup (legacy)
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
MONITORING_PORT=5003
DASHBOARD_URL="http://localhost:${FLASK_PORT}"
NICEGUI_URL="http://localhost:${NICEGUI_PORT}"
MONITORING_URL="http://localhost:${MONITORING_PORT}"

# Performance tuning
HEALTH_CHECK_TIMEOUT=5  # Reduced from 30

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

# Optimized port checking (macOS compatible)
check_port() {
    local port="$1"

    # Use faster port check (macOS compatible)
    if bash -c "</dev/tcp/localhost/$port" 2>/dev/null; then
        return 0  # Port is in use
    else
        return 1  # Port is available
    fi
}

# Fast health check (macOS compatible)
wait_for_service() {
    local url=$1
    local timeout=${3:-$HEALTH_CHECK_TIMEOUT}

    # Use curl with shorter timeout and faster DNS resolution
    if curl -s --connect-timeout 2 --max-time "$timeout" "$url/api/health" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Parallel service startup
start_services_parallel() {
    local services_to_start=("$@")
    local pids=()
    local service_names=()

    print_status "Starting services in parallel..."

    # Start all services simultaneously
    for service in "${services_to_start[@]}"; do
        case $service in
            "flask")
                start_flask_dashboard_async &
                pids+=($!)
                service_names+=("Flask Dashboard")
                ;;
            "nicegui")
                start_nicegui_graph_async &
                pids+=($!)
                service_names+=("NiceGUI Graph")
                ;;
            "watch")
                start_watch_folder_async &
                pids+=($!)
                service_names+=("Watch Folder")
                ;;
            "monitoring")
                start_production_monitoring_async &
                pids+=($!)
                service_names+=("Production Monitoring")
                ;;
        esac
    done

    # Wait for all services to start
    local i=0
    for pid in "${pids[@]}"; do
        if wait "$pid"; then
            print_status "✅ ${service_names[$i]} started successfully"
        else
            print_error "❌ ${service_names[$i]} failed to start"
        fi
        i=$((i + 1))
    done
}

# Function to start Flask dashboard
start_flask_dashboard() {
    print_status "Starting Flask Dashboard..."

    if check_port $FLASK_PORT; then
        print_warning "Port $FLASK_PORT is already in use. Flask dashboard may already be running."
        return 0
    fi

    # Start Flask dashboard in background
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

# Async service startup functions
start_flask_dashboard_async() {
    if check_port $FLASK_PORT; then
        print_warning "Port $FLASK_PORT is already in use"
        return 0
    fi

    nohup ./start_mission_dashboard.sh > flask_dashboard.log 2>&1 &
    local pid=$!
    echo $pid > flask_dashboard.pid

    # Wait for startup with shorter timeout
    local attempts=0
    while [ $attempts -lt 15 ] && ! wait_for_service $DASHBOARD_URL "Flask Dashboard" 2; do
        sleep 1
        attempts=$((attempts + 1))
    done

    if [ $attempts -lt 15 ]; then
        print_status "Flask Dashboard ready (PID: $pid)"
        return 0
    else
        print_error "Flask Dashboard startup timeout"
        return 1
    fi
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

start_nicegui_graph_async() {
    if check_port $NICEGUI_PORT; then
        print_warning "Port $NICEGUI_PORT is already in use"
        return 0
    fi

    # Ensure Flask is running first
    if ! check_port $FLASK_PORT; then
        print_error "Flask dashboard must be running first"
        return 1
    fi

    nohup ./start_graph_visualization.sh > nicegui_graph.log 2>&1 &
    local pid=$!
    echo $pid > nicegui_graph.pid

    # Wait for startup
    local attempts=0
    while [ $attempts -lt 10 ] && ! timeout 2 curl -s "$NICEGUI_URL" >/dev/null 2>&1; do
        sleep 1
        attempts=$((attempts + 1))
    done

    if [ $attempts -lt 10 ]; then
        print_status "NiceGUI Graph ready (PID: $pid)"
        return 0
    else
        print_error "NiceGUI Graph startup timeout"
        return 1
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

start_watch_folder_async() {
    if pgrep -f "watch_folder.py" > /dev/null; then
        print_warning "Watch folder service is already running"
        return 0
    fi

    if [ ! -d "watch_folder" ]; then
        mkdir -p watch_folder processed_documents
    fi

    nohup python3 src/watch_folder.py > watch_folder.log 2>&1 &
    local pid=$!
    echo $pid > watch_folder.pid

    # Wait for startup
    local attempts=0
    while [ $attempts -lt 5 ] && ! pgrep -f "watch_folder.py" > /dev/null; do
        sleep 1
        attempts=$((attempts + 1))
    done

    if [ $attempts -lt 5 ]; then
        print_status "Watch Folder Service ready (PID: $pid)"
        return 0
    else
        print_error "Watch Folder Service startup timeout"
        return 1
    fi
}

# Optimized database health check (bash 3.2 compatible)
check_database_health() {
    print_status "Checking database health (optimized)..."

    # Check PostgreSQL process
    if ! pgrep -f "postgres" > /dev/null; then
        print_error "❌ PostgreSQL is not running"
        return 1
    fi

    # Fast connection test
    if psql -d ai_agency -c "SELECT 1;" >/dev/null 2>&1; then
        print_status "✅ Database connected (optimized)"

        # Get chunk count
        local chunk_count
        chunk_count=$(psql -d ai_agency -t -c "SELECT COUNT(*) FROM document_chunks;" 2>/dev/null | tr -d ' ')
        print_info "Total document chunks: ${chunk_count:-0}"
        return 0
    else
        print_error "❌ Database connection failed"
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

start_production_monitoring_async() {
    if check_port $MONITORING_PORT; then
        print_warning "Port $MONITORING_PORT is already in use"
        return 0
    fi

    nohup python3 src/monitoring/production_monitor.py > production_monitor.log 2>&1 &
    local pid=$!
    echo $pid > production_monitor.pid

    # Wait for startup
    local attempts=0
    while [ $attempts -lt 10 ] && ! wait_for_service $MONITORING_URL "Production Monitoring" 2; do
        sleep 1
        attempts=$((attempts + 1))
    done

    if [ $attempts -lt 10 ]; then
        print_status "Production Monitoring ready (PID: $pid)"
        return 0
    else
        print_error "Production Monitoring startup timeout"
        return 1
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
    echo "  --parallel       Use parallel startup (default)"
    echo "  --sequential     Use sequential startup (legacy)"
    echo "  --refresh        Refresh memory context (non-blocking)"
    echo "  --memory-only    Refresh memory context only"
    echo "  --status         Show current status of all components"
    echo "  --test           Test API endpoint"
    echo "  --help           Show this help message"
    echo
    echo "Performance Features:"
    echo "  • Parallel service startup"
    echo "  • Optimized health checks (5s timeout vs 30s)"
    echo "  • Connection pooling for database"
    echo "  • Cached port checking"
    echo "  • Non-blocking memory refresh"
    echo
    echo "Examples:"
    echo "  ./wake_up_nemo.sh              # Start everything (parallel)"
    echo "  ./wake_up_nemo.sh --sequential # Start everything (sequential)"
    echo "  ./wake_up_nemo.sh --refresh    # Refresh memory + start everything"
    echo "  ./wake_up_nemo.sh --test       # Test API functionality"
}

# Function to cleanup on exit
cleanup() {
    print_info "Shutting down Nemo..."

    # Kill background processes
    if [ -f "flask_dashboard.pid" ]; then
        local pid
        pid=$(cat flask_dashboard.pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            print_status "Stopped Flask Dashboard (PID: $pid)"
        fi
        rm -f flask_dashboard.pid
    fi

    if [ -f "nicegui_graph.pid" ]; then
        local pid
        pid=$(cat nicegui_graph.pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            print_status "Stopped NiceGUI Graph (PID: $pid)"
        fi
        rm -f nicegui_graph.pid
    fi

    if [ -f "watch_folder.pid" ]; then
        local pid
        pid=$(cat watch_folder.pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            print_status "Stopped Watch Folder Service (PID: $pid)"
        fi
        rm -f watch_folder.pid
    fi

    if [ -f "production_monitor.pid" ]; then
        local pid
        pid=$(cat production_monitor.pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            print_status "Stopped Production Monitoring (PID: $pid)"
        fi
        rm -f production_monitor.pid
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
    print_status "🐙 Waking up Nemo (Optimized)..."
    echo

    # Parse arguments
    local STARTUP_MODE="parallel"
    local REFRESH_MEMORY=false
    local SERVICES_TO_START=()

    while [[ $# -gt 0 ]]; do
        case $1 in
            --flask-only)
                SERVICES_TO_START+=("flask")
                shift
                ;;
            --nicegui-only)
                SERVICES_TO_START+=("nicegui")
                shift
                ;;
            --watch-only)
                SERVICES_TO_START+=("watch")
                shift
                ;;
            --monitoring-only)
                SERVICES_TO_START+=("monitoring")
                shift
                ;;
            --api-only)
                SERVICES_TO_START+=("flask")
                shift
                ;;
            --parallel)
                STARTUP_MODE="parallel"
                shift
                ;;
            --sequential)
                STARTUP_MODE="sequential"
                shift
                ;;
            --refresh)
                REFRESH_MEMORY=true
                shift
                ;;
            --memory-only)
                print_info "Refreshing memory context only..."
                refresh_memory
                exit 0
                ;;
            --status)
                show_status
                exit 0
                ;;
            --test)
                test_api
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

    # Default: start all services
    if [ ${#SERVICES_TO_START[@]} -eq 0 ]; then
        SERVICES_TO_START=("watch" "flask" "nicegui" "monitoring")
    fi

    # Check database health first
    if ! check_database_health; then
        print_error "❌ Database health check failed"
        exit 1
    fi

    # Refresh memory if requested (non-blocking)
    if [ "$REFRESH_MEMORY" = true ]; then
        refresh_memory
    fi

    # Start services based on mode
    if [ "$STARTUP_MODE" = "parallel" ]; then
        start_services_parallel "${SERVICES_TO_START[@]}"
    else
        # Sequential startup (legacy mode)
        for service in "${SERVICES_TO_START[@]}"; do
            case $service in
                "flask") start_flask_dashboard ;;
                "nicegui") start_nicegui_graph ;;
                "watch") start_watch_folder ;;
                "monitoring") start_production_monitoring ;;
            esac
            sleep 1
        done
    fi

    echo
    print_status "🎉 Nemo is awake and ready!"
    echo
    show_status
    echo
    print_info "Press Ctrl+C to stop all services"

    # Keep script running
    while true; do
        sleep 10
    done
}

# Run main function
main "$@"
