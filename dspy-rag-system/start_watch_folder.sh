#!/bin/bash
# DSPy RAG System - Watch Folder Launcher

echo "🚀 Starting DSPy RAG Watch Folder..."
echo "======================================"

# Activate virtual environment
source venv/bin/activate

# Check if watch folder exists, if not create it
if [ ! -d "watch_folder" ]; then
    echo "📁 Creating watch folder..."
    mkdir -p watch_folder
    mkdir -p processed_documents
fi

echo "📁 Watch folder: $(pwd)/watch_folder"
echo "📁 Processed folder: $(pwd)/processed_documents"
echo ""
echo "💡 Simply drag and drop files into the watch_folder!"
echo "📄 Supported: .txt, .md, .pdf files"
echo ""
echo "⏹️  Press Ctrl+C to stop"
echo "======================================"

# Start the watch folder
python3 watch_folder.py 