#!/usr/bin/env bash
# Startup script for Real-time Mission Dashboard
# Handles environment setup and launches the dashboard

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DASHBOARD_PORT="${MISSION_DASHBOARD_PORT:-5002}"
DASHBOARD_HOST="${MISSION_DASHBOARD_HOST:-0.0.0.0}"
ENVIRONMENT="${ENVIRONMENT:-development}"

echo -e "${BLUE}🚀 Starting Real-time Mission Dashboard${NC}"
echo "=================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
port_available() {
    ! nc -z localhost "$1" 2>/dev/null
}

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check Python version
echo "🔍 Checking Python version..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "   Python version: $PYTHON_VERSION"

    # Check if version is 3.8 or higher
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        print_status "Python version is compatible"
    else
        print_error "Python 3.8 or higher is required"
        exit 1
    fi
else
    print_error "Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
echo "🔍 Checking virtual environment..."
if [ -d "$PROJECT_ROOT/venv" ]; then
    print_status "Virtual environment found"
    VENV_PATH="$PROJECT_ROOT/venv"
else
    print_warning "Virtual environment not found, creating one..."
    python3 -m venv "$PROJECT_ROOT/venv"
    VENV_PATH="$PROJECT_ROOT/venv"
    print_status "Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
# shellcheck disable=SC1091
source "$VENV_PATH/bin/activate"
print_status "Virtual environment activated"

# Install/upgrade pip
echo "📦 Upgrading pip..."
python3 -m pip install --upgrade pip >/dev/null 2>&1
print_status "Pip upgraded"

# Install requirements
echo "📦 Installing requirements..."
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip install -r "$SCRIPT_DIR/requirements.txt" >/dev/null 2>&1
    print_status "Requirements installed"
else
    print_warning "No requirements.txt found, installing basic dependencies..."
    pip install flask flask-socketio psutil opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-http >/dev/null 2>&1
    print_status "Basic dependencies installed"
fi

# Check database connection
echo "🔍 Checking database connection..."
if [ -n "$POSTGRES_DSN" ]; then
    echo "   Using database: $POSTGRES_DSN"
    # Try to connect to database
    if python3 -c "
import os
import sys
sys.path.append('src')
try:
    from utils.database_resilience import get_database_manager
    db_manager = get_database_manager()
    with db_manager.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1')
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
" 2>/dev/null; then
        print_status "Database connection successful"
    else
        print_warning "Database connection failed, continuing without database..."
    fi
else
    print_warning "No database configuration found, continuing without database..."
fi

# Check if port is available
echo "🔍 Checking port availability..."
if port_available "$DASHBOARD_PORT"; then
    print_status "Port $DASHBOARD_PORT is available"
else
    print_error "Port $DASHBOARD_PORT is already in use"
    echo "   Please stop the service using port $DASHBOARD_PORT or change the port:"
    echo "   export MISSION_DASHBOARD_PORT=5003"
    exit 1
fi

# Set environment variables
export MISSION_DASHBOARD_PORT="$DASHBOARD_PORT"
export MISSION_DASHBOARD_HOST="$DASHBOARD_HOST"
export ENVIRONMENT="$ENVIRONMENT"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Start the dashboard
echo "🚀 Starting Mission Dashboard..."
echo "   Host: $DASHBOARD_HOST"
echo "   Port: $DASHBOARD_PORT"
echo "   Environment: $ENVIRONMENT"
echo "   Dashboard URL: http://localhost:$DASHBOARD_PORT"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Start the dashboard with proper error handling
cd "$SCRIPT_DIR"
python3 src/mission_dashboard/mission_dashboard.py 2>&1 | tee logs/mission_dashboard.log

# Handle exit
echo ""
echo -e "${BLUE}🛑 Mission Dashboard stopped${NC}"
