#!/bin/bash
# DSPy RAG System Test Runner
# Enhanced with marker-based test selection (Phase 1)

echo "🧪 DSPy RAG System Test Runner"
echo "================================"
echo ""

# Show usage examples if no arguments provided
if [ $# -eq 0 ]; then
    echo "📋 Usage Examples:"
    echo "  $0                    # Run all tests (legacy mode)"
    echo "  $0 --tiers 1 --kinds smoke          # Fast PR gate"
    echo "  $0 --tiers 1 --kinds unit           # Critical unit tests"
    echo "  $0 --tiers 1 2 --kinds integration # Production integration"
    echo "  $0 --markers 'tier1 and not e2e'    # Custom expression"
    echo "  $0 --legacy-files                   # Force legacy mode"
    echo "  $0 --strict-markers                 # Enable strict validation"
    echo "  $0 --show-suggestions               # Show all examples"
    echo ""
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "OK Virtual environment found"
    # shellcheck disable=SC1091
    source venv/bin/activate
else
    echo "!️  No virtual environment found. Tests may fail if dependencies aren't installed."
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

    if python3 -m pytest "$test_path" "$options"; then
        echo "OK Tests passed!"
    else
        echo "X Tests failed!"
    fi
}

# Check for marker-based arguments (new interface)
if [[ "$*" == *"--tiers"* ]] || [[ "$*" == *"--kinds"* ]] || [[ "$*" == *"--markers"* ]] || [[ "$*" == *"--show-suggestions"* ]] || [[ "$*" == *"--strict-markers"* ]]; then
    echo "🚀 Using marker-based test selection..."
    echo "----------------------------------------"

    # Pass through to comprehensive test suite
    python3 tests/comprehensive_test_suite.py "$@"
    exit_code=$?

    echo ""
    echo "OK Marker-based execution completed (exit code: $exit_code)"
    exit $exit_code
fi

# Legacy argument parsing (preserved for backward compatibility)
case "${1:-all}" in
    "all")
        echo "Running all tests (modern mode)..."
        run_tests "../tests/" "-v"
        ;;
    "unit")
        echo "Running unit tests only (modern mode)..."
        run_tests "../tests/" "-v -m unit"
        ;;
    "integration")
        echo "Running integration tests only (modern mode)..."
        run_tests "../tests/" "-v -m integration"
        ;;
    "enhanced")
        echo "Running enhanced RAG system tests (modern mode)..."
        run_tests "../tests/" "-v -m tier2"
        ;;
    "coverage")
        echo "Running tests with coverage (modern mode)..."
        run_tests "../tests/" "-v --cov=src --cov-report=html"
        echo "📊 Coverage report generated in htmlcov/"
        ;;
    "quick")
        echo "Running quick tests (modern mode)..."
        run_tests "../tests/" "-v -m smoke"
        ;;
    *)
        echo "Usage: $0 [all|unit|integration|enhanced|coverage|quick]"
        echo ""
        echo "Modern Options:"
        echo "  all        - Run all tests"
        echo "  unit       - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  enhanced   - Run enhanced RAG system tests"
        echo "  coverage   - Run tests with coverage report"
        echo "  quick      - Run quick tests (no external deps)"
        echo ""
        echo "Marker-Based Options (Recommended):"
        echo "  --tiers 1 --kinds smoke          # Fast PR gate"
        echo "  --tiers 1 --kinds unit           # Critical unit tests"
        echo "  --tiers 1 2 --kinds integration # Production integration"
        echo "  --markers 'tier1 and not e2e'    # Custom expression"
        echo "  --show-suggestions               # Show all examples"
        echo ""
        echo "Examples:"
        echo "  $0 all          # Run all tests"
        echo "  $0 --tiers 1 --kinds smoke  # Fast PR gate"
        echo "  $0 --show-suggestions       # Show examples"
        ;;
esac
