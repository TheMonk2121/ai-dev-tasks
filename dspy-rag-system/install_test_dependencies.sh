#!/bin/bash
# Install test dependencies for DSPy RAG System

echo "🔧 Installing test dependencies..."

# Install psutil if not already installed
if ! python -c "import psutil" 2>/dev/null; then
    echo "📦 Installing psutil..."
    pip install psutil>=5.9.0
else
    echo "OK psutil already installed"
fi

# Install other test dependencies
echo "📦 Installing test dependencies..."
pip install -r requirements.txt

# Install additional test-specific packages
pip install coverage pytest pytest-cov pytest-mock bandit

echo "OK Test dependencies installed successfully!"
echo ""
echo "To run the comprehensive test suite:"
echo "  python tests/comprehensive_test_suite.py"
echo ""
echo "To run specific test categories:"
echo "  python tests/comprehensive_test_suite.py --categories unit integration"
