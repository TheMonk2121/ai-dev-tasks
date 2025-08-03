#!/bin/bash
# DSPy RAG System Test Runner

echo "🧪 DSPy RAG System Test Runner"
echo "================================"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment found"
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found. Tests may fail if dependencies aren't installed."
    echo "💡 To create a virtual environment:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
fi

# Function to run tests
run_tests() {
    local test_path="$1"
    local options="$2"
    
    echo ""
    echo "🔍 Running tests: $test_path"
    echo "Options: $options"
    echo "----------------------------------------"
    
    python3 -m pytest "$test_path" $options
    
    if [ $? -eq 0 ]; then
        echo "✅ Tests passed!"
    else
        echo "❌ Tests failed!"
    fi
}

# Parse command line arguments
case "${1:-all}" in
    "all")
        echo "Running all tests..."
        run_tests "tests/" "-v"
        ;;
    "unit")
        echo "Running unit tests only..."
        run_tests "tests/test_logger.py tests/test_tokenizer.py tests/test_metadata_extractor.py" "-v"
        ;;
    "integration")
        echo "Running integration tests only..."
        run_tests "tests/test_document_processor.py tests/test_rag_system.py tests/test_vector_store.py tests/test_watch_folder.py" "-v"
        ;;
    "enhanced")
        echo "Running enhanced RAG system tests..."
        run_tests "tests/test_enhanced_rag_system.py" "-v"
        ;;
    "coverage")
        echo "Running tests with coverage..."
        run_tests "tests/" "-v --cov=src --cov-report=html"
        echo "📊 Coverage report generated in htmlcov/"
        ;;
    "quick")
        echo "Running quick tests (no external dependencies)..."
        run_tests "tests/test_logger.py tests/test_tokenizer.py" "-v"
        ;;
    *)
        echo "Usage: $0 [all|unit|integration|enhanced|coverage|quick]"
        echo ""
        echo "Options:"
        echo "  all        - Run all tests"
        echo "  unit       - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  enhanced   - Run enhanced RAG system tests"
        echo "  coverage   - Run tests with coverage report"
        echo "  quick      - Run quick tests (no external deps)"
        echo ""
        echo "Examples:"
        echo "  $0 all          # Run all tests"
        echo "  $0 unit         # Run unit tests only"
        echo "  $0 coverage     # Run with coverage report"
        ;;
esac 