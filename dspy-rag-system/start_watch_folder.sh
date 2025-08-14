#!/bin/bash
# DSPy RAG System - Watch Folder Launcher

echo "🚀 Starting DSPy RAG Watch Folder..."
echo "======================================"

# Activate virtual environment (try multiple locations)
VENV_ACTIVATED=false
for venv_path in "../venv/bin/activate" "venv/bin/activate" "../../venv/bin/activate"; do
    if [ -f "$venv_path" ]; then
        # shellcheck disable=SC1090
        source "$venv_path"
        VENV_ACTIVATED=true
        echo "✅ Virtual environment activated: $venv_path"
        break
    fi
done

if [ "$VENV_ACTIVATED" = false ]; then
    echo "⚠️  Virtual environment not found. Continuing without activation..."
    echo "💡 To create a virtual environment: python3 -m venv venv"
fi

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
python3 src/watch_folder.py
