#!/bin/bash
# Comprehensive Test Suite Runner
# T-4.1: Advanced Testing Framework Implementation

echo "🧪 Comprehensive Test Suite Runner T-4.1"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "success") echo -e "${GREEN}✅ $message${NC}" ;;
        "error") echo -e "${RED}❌ $message${NC}" ;;
        "warning") echo -e "${YELLOW}⚠️ $message${NC}" ;;
        "info") echo -e "${BLUE}ℹ️ $message${NC}" ;;
    esac
}

# Function to check dependencies
check_dependencies() {
    print_status "info" "Checking dependencies..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_status "error" "Python3 is not installed"
        exit 1
    fi

    # Check virtual environment
    if [ ! -d "venv" ]; then
        print_status "warning" "Virtual environment not found. Creating one..."
        python3 -m venv venv
        # shellcheck disable=SC1091
        source venv/bin/activate
        pip install -r requirements.txt
    else
        # shellcheck disable=SC1091
        source venv/bin/activate
    fi

    # Check required packages
    if ! python3 -c "import pytest, coverage, psutil, bandit" 2>/dev/null; then
        print_status "warning" "Installing missing test dependencies..."
        pip install pytest coverage psutil bandit pytest-cov pytest-mock
    fi

    print_status "success" "Dependencies check complete"
}

# SHIM: Run comprehensive suite via unified root pytest
run_comprehensive_suite() {
    local options="$1"

    print_status "info" "Running comprehensive test suite (shim to root pytest)..."

    # Determine repo root (parent of this script's dir)
    local SCRIPT_DIR
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    local REPO_ROOT
    REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

    cd "$REPO_ROOT" || exit 1

    # Map simple categories to marker expressions when passed by callers
    case "$options" in
        *"unit"*) pytest -v -m unit; return $? ;;
        *"integration"*) pytest -v -m integration; return $? ;;
        *"e2e"*) pytest -v -m e2e; return $? ;;
        *"performance"*) pytest -v -m performance; return $? ;;
        *"security"*) pytest -v -m security; return $? ;;
        *) pytest -v; return $? ;;
    esac
}

# Function to run specific test categories
run_test_category() {
    local category=$1
    local options="$2"

    print_status "info" "Running $category tests..."

    case $category in
        "unit")
            run_comprehensive_suite "--categories unit" "$options"
            ;;
        "integration")
            run_comprehensive_suite "--categories integration" "$options"
            ;;
        "e2e")
            run_comprehensive_suite "--categories e2e" "$options"
            ;;
        "performance")
            run_comprehensive_suite "--categories performance" "$options"
            ;;
        "security")
            run_comprehensive_suite "--categories security" "$options"
            ;;
        "quick")
            run_comprehensive_suite "--categories unit integration --timeout 60" "$options"
            ;;
        "full")
            run_comprehensive_suite "$options"
            ;;
        *)
            print_status "error" "Unknown test category: $category"
            exit 1
            ;;
    esac
}

# Function to run with coverage
run_with_coverage() {
    local options="$1"

    print_status "info" "Running tests with coverage analysis..."

    # Run comprehensive suite with coverage
    run_comprehensive_suite "--coverage-threshold 80.0" "$options"

    # Generate HTML coverage report
    if [ -f ".coverage" ]; then
        coverage html
        print_status "success" "Coverage report generated in htmlcov/"
    fi
}

# Function to run performance benchmarks
run_performance_benchmarks() {
    print_status "info" "Running performance benchmarks..."

    # Run performance tests with detailed metrics
    run_comprehensive_suite "--categories performance --timeout 600"

    # Generate performance report
    if [ -f "test_report_*.json" ]; then
        python3 -c "
import json
import glob
import os

# Find the latest test report
reports = glob.glob('test_report_*.json')
if reports:
    latest_report = max(reports, key=os.path.getctime)
    with open(latest_report) as f:
        data = json.load(f)

    print('\\n📊 PERFORMANCE BENCHMARKS')
    print('=' * 40)
    print(f'Average Duration: {data[\"performance_metrics\"][\"average_duration_seconds\"]:.2f}s')
    print(f'Average Memory: {data[\"performance_metrics\"][\"average_memory_mb\"]:.1f}MB')
    print(f'Average CPU: {data[\"performance_metrics\"][\"average_cpu_percent\"]:.1f}%')
    print(f'Meets Threshold: {data[\"performance_metrics\"][\"meets_performance_threshold\"]}')
"
    fi
}

# Function to run security scan
run_security_scan() {
    print_status "info" "Running security scan..."

    # Run security tests
    run_comprehensive_suite "--categories security --no-report"

    # Run additional security tools
    if command -v bandit &> /dev/null; then
        print_status "info" "Running bandit security scan..."
        bandit -r src/ -f json -o security_scan.json
    fi

    if command -v safety &> /dev/null; then
        print_status "info" "Running safety check..."
        safety check --json --output safety_report.json
    fi

    print_status "success" "Security scan complete"
}

# Function to generate test report
generate_test_report() {
    print_status "info" "Generating comprehensive test report..."

    # Run full test suite with report generation
    run_comprehensive_suite "--generate-report"

    # Find and display the latest report
    if [ -f "test_summary_*.txt" ]; then
        # Use a portable approach that works on both macOS and Linux
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            latest_summary=$(find . -maxdepth 1 -name "test_summary_*.txt" -type f -exec stat -f '%m %N' {} \; | sort -n | tail -1 | cut -d' ' -f2-)
        else
            # Linux
            latest_summary=$(find . -maxdepth 1 -name "test_summary_*.txt" -type f -exec stat -c '%Y %n' {} \; | sort -n | tail -1 | cut -d' ' -f2-)
        fi
        if [ -n "$latest_summary" ]; then
            echo ""
            echo "📄 LATEST TEST SUMMARY"
            echo "======================"
            cat "$latest_summary"
        fi
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  all              - Run all tests with comprehensive analysis"
    echo "  unit             - Run unit tests only"
    echo "  integration      - Run integration tests only"
    echo "  e2e              - Run end-to-end tests only"
    echo "  performance      - Run performance benchmarks"
    echo "  security         - Run security tests and scans"
    echo "  quick            - Run quick tests (unit + integration)"
    echo "  coverage         - Run tests with coverage analysis"
    echo "  report           - Generate comprehensive test report"
    echo "  check            - Check dependencies and setup"
    echo "  help             - Show this help message"
    echo ""
    echo "Options:"
    echo "  --parallel       - Enable parallel test execution"
    echo "  --workers N      - Number of parallel workers (default: 4)"
    echo "  --timeout N      - Test timeout in seconds (default: 300)"
    echo "  --coverage-threshold N - Coverage threshold percentage (default: 80.0)"
    echo "  --no-security-scan - Skip security scanning"
    echo "  --no-report      - Skip report generation"
    echo ""
    echo "Examples:"
    echo "  $0 all                    # Run all tests"
    echo "  $0 unit --parallel        # Run unit tests in parallel"
    echo "  $0 performance --timeout 600  # Run performance tests with 10min timeout"
    echo "  $0 coverage --coverage-threshold 90.0  # Run with 90% coverage threshold"
    echo "  $0 security               # Run security tests and scans"
}

# Main execution
case "${1:-help}" in
    "all"|"full")
        check_dependencies
        run_comprehensive_suite "${@:2}"
        ;;
    "unit"|"integration"|"e2e"|"performance"|"security"|"quick")
        check_dependencies
        run_test_category "$1" "${@:2}"
        ;;
    "coverage")
        check_dependencies
        run_with_coverage "${@:2}"
        ;;
    "report")
        check_dependencies
        generate_test_report
        ;;
    "check")
        check_dependencies
        print_status "success" "System check complete"
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        print_status "error" "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
