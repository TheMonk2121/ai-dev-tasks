#!/bin/bash

# DSPy RAG System Setup Script
# This script sets up the DSPy RAG system with your existing infrastructure

set -e  # Exit on any error

echo "🚀 Setting up DSPy RAG System for Cursor + Mistral-7B"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    print_error "Please run this script from the dspy-rag-system directory"
    exit 1
fi

print_status "Checking prerequisites..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_error "Python 3.8+ is required. Found: $python_version"
    exit 1
fi

print_success "Python version: $python_version"

# Check if PostgreSQL is running
if ! pg_isready -q; then
    print_warning "PostgreSQL is not running. Please start PostgreSQL before continuing."
    print_status "You can start PostgreSQL with: brew services start postgresql"
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_warning "Ollama is not running. Please start Ollama before continuing."
    print_status "You can start Ollama with: ollama serve"
fi

# Check if Mistral-7B is available
if curl -s http://localhost:11434/api/tags | grep -q "mistral"; then
    print_success "Mistral-7B model is available"
else
    print_warning "Mistral-7B model not found. You may need to pull it:"
    print_status "Run: ollama pull mistral:7b-instruct"
fi

print_status "Setting up Python virtual environment..."

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Created virtual environment"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

print_status "Installing Python dependencies..."

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

print_success "Python dependencies installed"

print_status "Setting up PostgreSQL database..."

# Check if pgvector extension is available
if ! psql -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null; then
    print_error "pgvector extension is not available. Please install it:"
    print_status "For macOS: brew install pgvector"
    print_status "For Ubuntu: sudo apt-get install postgresql-14-pgvector"
    exit 1
fi

print_success "PostgreSQL with pgvector is ready"

print_status "Creating database schema..."

# Apply database schema
psql -f config/database/schema.sql

print_success "Database schema created"

print_status "Testing DSPy modules..."

# Test the document processor
python3 -c "
import sys
sys.path.append('src')
from dspy_modules.document_processor import DocumentProcessor

# Create a test document
with open('test_doc.txt', 'w') as f:
    f.write('This is a test document for DSPy RAG system. ' * 50)

try:
    processor = DocumentProcessor()
    result = processor('test_doc.txt')
    print(f'✅ Document processor test passed: {result[\"total_chunks\"]} chunks created')
except Exception as e:
    print(f'❌ Document processor test failed: {e}')
finally:
    import os
    if os.path.exists('test_doc.txt'):
        os.remove('test_doc.txt')
"

print_status "Creating configuration files..."

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cat > .env << EOF
# DSPy RAG System Configuration

# Database Configuration
DATABASE_URL=postgresql://ai_user:ai_password@localhost:5432/ai_agency

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b-instruct

# Vector Store Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# RAG Configuration
MAX_RESULTS=5
SIMILARITY_THRESHOLD=0.7

# Memory Configuration
MAX_CONVERSATION_HISTORY=10
MEMORY_CLEANUP_DAYS=30
EOF
    print_success "Created .env configuration file"
else
    print_status ".env file already exists"
fi

print_status "Setting up development environment..."

# Create test directory structure
mkdir -p tests/unit tests/integration

# Create basic test files
cat > tests/unit/__init__.py << EOF
# Unit tests for DSPy RAG system
EOF

cat > tests/integration/__init__.py << EOF
# Integration tests for DSPy RAG system
EOF

print_success "Development environment set up"

print_status "Creating documentation..."

# Create basic documentation
mkdir -p docs

cat > docs/setup.md << 'EOF'
# DSPy RAG System Setup Guide

## Prerequisites

1. **Python 3.8+** - Already installed
2. **PostgreSQL** - Running with pgvector extension
3. **Ollama** - Running with Mistral 7B Instruct model
4. **n8n** - Your existing n8n instance

## Quick Start

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Test the system:**
   ```bash
   python3 -c "
   import sys
   sys.path.append('src')
   from dspy_modules.document_processor import DocumentProcessor
   from dspy_modules.vector_store import VectorStore
   
   # Test document processing
   processor = DocumentProcessor()
   result = processor('your_document.pdf')
   print(f'Processed: {result[\"total_chunks\"]} chunks')
   "
   ```

3. **Query your knowledge base:**
   ```bash
   python3 -c "
   import sys
   sys.path.append('src')
   from dspy_modules.vector_store import VectorStore
   
   vector_store = VectorStore('postgresql://ai_user:ai_password@localhost:5432/ai_agency')
   result = vector_store('search', query='Your question here?')
   print(f'Found {result[\"total_results\"]} relevant chunks')
   "
   ```

## Configuration

Edit the `.env` file to customize:
- Database connection
- Ollama settings
- Vector store parameters
- RAG configuration

## Next Steps

1. Add documents to your knowledge base
2. Test RAG queries
3. Integrate with Cursor IDE
4. Set up n8n workflows
EOF

print_success "Documentation created"

print_status "Setting up n8n workflow templates..."

# Create n8n workflow templates
mkdir -p src/n8n_workflows

cat > src/n8n_workflows/document_processing.json << 'EOF'
{
  "name": "Document Processing Workflow",
  "nodes": [
    {
      "parameters": {
        "path": "/path/to/documents",
        "options": {
          "includeSubdirectories": true,
          "fileTypes": ["pdf", "txt", "md"]
        }
      },
      "id": "file-watcher",
      "name": "File Watcher",
      "type": "n8n-nodes-base.fileWatcher",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "url": "http://localhost:8000/process-document",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "file_path",
              "value": "={{ $json.file_path }}"
            }
          ]
        }
      },
      "id": "http-request",
      "name": "Process Document",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [460, 300]
    }
  ],
  "connections": {
    "File Watcher": {
      "main": [
        [
          {
            "node": "Process Document",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
EOF

print_success "n8n workflow templates created"

print_status "Finalizing setup..."

# Make scripts executable
chmod +x scripts/*.sh

print_success "🎉 DSPy RAG System setup complete!"

echo ""
echo "📋 Next Steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Test document processing: python3 src/dspy_modules/document_processor.py"
echo "3. Test vector storage: python3 src/dspy_modules/vector_store.py"
echo "4. Add documents to your knowledge base"
echo "5. Start querying with RAG!"
echo ""
echo "📚 Documentation: docs/setup.md"
echo "🔧 Configuration: .env"
echo "🧪 Tests: tests/"
echo ""

print_success "Your DSPy RAG system is ready to use with Cursor + Mistral-7B + PostgreSQL!" 