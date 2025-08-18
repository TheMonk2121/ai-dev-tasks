#!/bin/bash
# Check DSPy RAG System Status

echo "🔍 DSPy RAG System Status Check"
echo "================================"

# Check if watch folder is running
if pgrep -f "watch_folder.py" > /dev/null; then
    echo "OK Watch folder is RUNNING"
    echo "📁 Drop files into: $(pwd)/watch_folder"
else
    echo "X Watch folder is NOT running"
    echo "💡 To start: ./quick_start.sh"
fi

echo ""

# Check database status
echo "🗄️  Database Status:"
if psql -d ai_agency -c "SELECT COUNT(*) as total_chunks FROM document_chunks;" 2>/dev/null; then
    echo "OK Database connected"
else
    echo "X Database not accessible"
fi

echo ""

# Show folder contents
echo "📁 Watch folder contents:"
ls -la watch_folder/ 2>/dev/null || echo "   (empty)"

echo ""

echo "📁 Processed documents:"
ls -la processed_documents/ 2>/dev/null || echo "   (empty)"

echo ""

echo "🔧 Quick Commands:"
echo "   Start watch:    ./quick_start.sh"
echo "   Stop watch:     pkill -f watch_folder.py"
echo "   Check status:   ./check_status.sh"
echo "   Setup service:  ./setup_watch_service.sh" 