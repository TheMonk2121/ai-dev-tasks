# 🚀 DSPy RAG System - Watch Folder Guide

## 📁 Quick Start

### Option 1: Simple Launcher (Recommended)
```bash
./start_watch_folder.sh
```

### Option 2: Direct Python
```bash
source venv/bin/activate
python3 watch_folder.py
```

## 🎯 How It Works

1. **Start the watch folder** - Run one of the commands above
2. **Drag & drop files** - Simply drag files into the `watch_folder` directory
3. **Automatic processing** - Files are automatically:
   - Detected and processed
   - Chunked and embedded
   - Added to your RAG knowledge base
   - Moved to `processed_documents` folder

## 📄 Supported File Types

- **Text files** (`.txt`)
- **Markdown files** (`.md`)
- **PDF files** (`.pdf`)

## 📁 Folder Structure

```
dspy-rag-system/
├── watch_folder/          # Drop files here
├── processed_documents/   # Processed files go here
├── start_watch_folder.sh  # Quick launcher
└── watch_folder.py       # Main watch script
```

## 💡 Usage Examples

### Start the watch folder:
```bash
./start_watch_folder.sh
```

### Drag and drop files:
1. Open Finder
2. Navigate to: `/Users/danieljacobs/Documents/cursor-projects/ai-dev-tasks/dspy-rag-system/watch_folder`
3. Drag any `.txt`, `.md`, or `.pdf` files into this folder
4. Watch them get automatically processed!

### Check processed files:
```bash
ls -la processed_documents/
```

### Query your knowledge base:
```bash
python3 -c "
import sys; sys.path.append('src')
from dspy_modules.vector_store import VectorStore
vs = VectorStore('postgresql://danieljacobs@localhost:5432/ai_agency')
results = vs('search', query='Your question?', limit=3)
print(f'Found {len(results[\"results\"])} results')
"
```

## 🔧 Troubleshooting

### If files aren't being processed:
1. Make sure the watch folder is running
2. Check file extensions (must be .txt, .md, or .pdf)
3. Check the console output for error messages

### If you get permission errors:
```bash
chmod +x start_watch_folder.sh
```

### To stop the watch folder:
Press `Ctrl+C` in the terminal

## 🎉 Benefits

- **Super easy** - Just drag and drop!
- **Automatic** - No manual commands needed
- **Organized** - Processed files are moved to a separate folder
- **Real-time** - Files are processed immediately when dropped
- **Cross-platform** - Works on macOS, Linux, Windows

## 📊 Current Status

Your RAG system currently has:
- ✅ Watch folder ready
- ✅ Automatic processing enabled
- ✅ PostgreSQL database connected
- ✅ Vector embeddings working
- ✅ Semantic search functional

Ready to start building your AI-powered knowledge base! 🚀 