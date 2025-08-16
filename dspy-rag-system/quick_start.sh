#!/bin/bash
# Quick Start Script for DSPy RAG Watch Folder

echo "🚀 DSPy RAG Watch Folder - Quick Start"
echo "======================================"

# Check if watch folder is already running
if pgrep -f "watch_folder.py" > /dev/null; then
    echo "✅ Watch folder is already running!"
    echo "📁 Drop files into: $(pwd)/watch_folder"
    echo "⏹️  To stop: pkill -f watch_folder.py"
    exit 0
fi

# Activate virtual environment and start watch folder
echo "🔧 Starting watch folder..."

# Check if virtual environment exists
if [[ ! -f "venv/bin/activate" ]]; then
    echo "❌ Virtual environment not found at venv/bin/activate"
    echo "💡 Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# shellcheck disable=SC1091
source venv/bin/activate

# Start in background
python3 watch_folder.py &
WATCH_PID=$!

echo "✅ Watch folder started! (PID: $WATCH_PID)"
echo "📁 Drop files into: $(pwd)/watch_folder"
echo "📄 Supported: .txt, .md, .pdf files"
echo ""
echo "🔧 Commands:"
echo "   Stop:     pkill -f watch_folder.py"
echo "   Status:   ps aux | grep watch_folder.py"
echo "   Logs:     tail -f watch_folder.log"
echo ""
echo "💡 The watch folder will automatically:"
echo "   1. Detect new files"
echo "   2. Process and chunk them"
echo "   3. Add them to your RAG system"
echo "   4. Move them to processed_documents/"
echo ""
echo "⏹️  Press Ctrl+C to stop this script (watch folder will continue running)"
echo "======================================"

# Wait for user to stop
trap "echo 'Stopping...'; pkill -f watch_folder.py; exit" INT
wait
