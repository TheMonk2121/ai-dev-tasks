#!/bin/bash
# Startup script for NiceGUI Graph Visualization Application.
#
# This script starts the NiceGUI graph visualization application that provides
# interactive network graph visualization for chunk relationships.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔗 Starting NiceGUI Graph Visualization...${NC}"

# Check if we're in the right directory
if [ ! -f "src/nicegui_graph_view.py" ]; then
    echo -e "${RED}X Error: nicegui_graph_view.py not found.${NC}"
    echo "Please run this script from the dspy-rag-system directory."
    exit 1
fi

# Check if NiceGUI is installed
if ! python3 -c "import nicegui" 2>/dev/null; then
    echo -e "${YELLOW}!️  NiceGUI not found. Installing...${NC}"
    pip3 install nicegui>=1.4.0
fi

# Check if httpx is installed
if ! python3 -c "import httpx" 2>/dev/null; then
    echo -e "${YELLOW}!️  httpx not found. Installing...${NC}"
    pip3 install httpx
fi

# Set environment variables
export DASHBOARD_URL=${DASHBOARD_URL:-"http://localhost:5000"}

echo -e "${GREEN}OK Environment configured:${NC}"
echo -e "   Dashboard URL: ${DASHBOARD_URL}"
echo -e "   Graph Data Endpoint: ${DASHBOARD_URL}/graph-data"

# Check if dashboard is running
echo -e "${BLUE}🔍 Checking if dashboard is running...${NC}"
if curl -s "${DASHBOARD_URL}/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}OK Dashboard is running${NC}"
else
    echo -e "${YELLOW}!️  Dashboard not detected at ${DASHBOARD_URL}${NC}"
    echo -e "${YELLOW}   Make sure the Flask dashboard is running first.${NC}"
    echo -e "${YELLOW}   You can start it with: ./start_mission_dashboard.sh${NC}"
fi

echo -e "${BLUE}🚀 Starting NiceGUI Graph Visualization...${NC}"
echo -e "${GREEN}   URL: http://localhost:8080${NC}"
echo -e "${GREEN}   Press Ctrl+C to stop${NC}"

# Start the NiceGUI application
python3 src/nicegui_graph_view.py
