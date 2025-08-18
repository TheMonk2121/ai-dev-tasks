#!/bin/bash

echo "🚀 Starting Document Management Dashboard..."

# Check if we're in the right directory
if [ ! -f "dashboard.py" ]; then
    echo "X Error: dashboard.py not found. Please run this script from the dashboard directory."
    exit 1
fi

# Check if PostgreSQL is running
echo "🔍 Checking database connection..."
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        database='ai_agency',
        user='danieljacobs'
    )
    conn.close()
    print('OK Database connection successful')
except Exception as e:
    print(f'X Database connection failed: {e}')
    exit(1)
"

# Install requirements if needed
if [ ! -d "venv" ]; then
    echo "📦 Installing requirements..."
    python3 -m pip install -r requirements.txt
fi

# Start the dashboard
echo "🌐 Starting Flask dashboard on http://localhost:5001"
echo "📊 Dashboard will be available at: http://localhost:5001"
echo "🔍 Health check: http://localhost:5001/health"
echo "⏹️  Press Ctrl+C to stop"
echo ""

python3 dashboard.py 