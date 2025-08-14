#!/bin/bash
# AI Development Tasks - Dependency Installation Script
# Uses consolidated requirements with constraints for version consistency

set -e

echo "🚀 Installing AI Development Tasks Dependencies"
echo "================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source venv/bin/activate
else
    echo "❌ Error: Virtual environment activate script not found"
    exit 1
fi

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies with constraints
echo "📥 Installing dependencies with version constraints..."
pip install -r requirements.txt -c requirements-constraints.txt

# Install subproject dependencies
echo "📥 Installing DSPy RAG system dependencies..."
cd dspy-rag-system
pip install -r requirements.txt -c ../requirements-constraints.txt
cd ..

echo "📥 Installing dashboard dependencies..."
cd dashboard
pip install -r requirements.txt -c ../requirements-constraints.txt
cd ..

echo "📥 Installing conflict detection dependencies..."
cd config
pip install -r requirements-conflict-detection.txt -c ../requirements-constraints.txt
cd ..

# Verify installation
echo "✅ Verifying installation..."
python -c "import dspy, flask, psycopg2, pytest; print('✅ Core dependencies verified')"

echo ""
echo "🎉 Installation complete!"
echo "========================="
echo "Virtual environment: ./venv"
echo "Activate with: source venv/bin/activate"
echo ""
echo "Available commands:"
echo "  pytest dspy-rag-system/tests/    # Run DSPy tests"
echo "  python dspy-rag-system/src/dashboard.py  # Start dashboard"
echo "  python scripts/process_tasks.py   # Run task processor"
