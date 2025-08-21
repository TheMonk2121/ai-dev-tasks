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

# Check if virtual environment exists (check both local and parent directory)
if [ -d "venv" ]; then
    echo "✅ Virtual environment found (local)"
    # shellcheck disable=SC1091
    source venv/bin/activate
elif [ -d "../venv" ]; then
    echo "✅ Virtual environment found (parent directory)"
    # shellcheck disable=SC1091
    source ../venv/bin/activate
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

    if python3 -m pytest "$test_path" "$options"; then
        echo "✅ Tests passed!"
    else
        echo "❌ Tests failed!"
    fi
}

###############################################
# SHIM: Translate marker flags to root pytest #
###############################################
if [[ "$*" == *"--tiers"* ]] || [[ "$*" == *"--kinds"* ]] || [[ "$*" == *"--markers"* ]] || [[ "$*" == *"--show-suggestions"* ]] || [[ "$*" == *"--strict-markers"* ]]; then
    echo "🚀 Using marker-based test selection (shim to root pytest)..."
    echo "----------------------------------------"

    # Handle suggestions only
    if [[ "$*" == *"--show-suggestions"* ]]; then
        echo "Examples (root pytest):"
        echo "  python -m pytest -v -m smoke"
        echo "  python -m pytest -v -m unit"
        echo "  python -m pytest -v -m 'tier1 and not e2e'"
        echo "  python -m pytest -v -m '(tier1 or tier2) and integration'"
        exit 0
    fi

    # Parse flags into a pytest -m expression
    TIERS_EXPR=""
    KINDS_EXPR=""
    CUSTOM_EXPR=""

    # Simple parser for --tiers/--kinds/--markers
    ARGS=("$@")
    i=0
    while [[ $i -lt ${#ARGS[@]} ]]; do
        case "${ARGS[$i]}" in
            --tiers)
                i=$((i+1))
                TIERS_LIST=()
                while [[ $i -lt ${#ARGS[@]} ]] && [[ "${ARGS[$i]}" != --* ]]; do
                    t="${ARGS[$i]}"
                    # Map numeric tiers to marker names (1 -> tier1)
                    if [[ "$t" =~ ^[0-9]+$ ]]; then
                        TIERS_LIST+=("tier${t}")
                    else
                        TIERS_LIST+=("${t}")
                    fi
                    i=$((i+1))
                done
                i=$((i-1))
                if [[ ${#TIERS_LIST[@]} -gt 0 ]]; then
                    TIERS_EXPR="($(IFS=' or '; echo "${TIERS_LIST[*]}"))"
                fi
                ;;
            --kinds)
                i=$((i+1))
                KINDS_LIST=()
                while [[ $i -lt ${#ARGS[@]} ]] && [[ "${ARGS[$i]}" != --* ]]; do
                    KINDS_LIST+=("${ARGS[$i]}")
                    i=$((i+1))
                done
                i=$((i-1))
                if [[ ${#KINDS_LIST[@]} -gt 0 ]]; then
                    KINDS_EXPR="($(IFS=' or '; echo "${KINDS_LIST[*]}"))"
                fi
                ;;
            --markers)
                i=$((i+1))
                if [[ $i -lt ${#ARGS[@]} ]]; then
                    CUSTOM_EXPR="${ARGS[$i]}"
                fi
                ;;
        esac
        i=$((i+1))
    done

    # Combine expressions
    EXPR_PARTS=()
    [[ -n "$TIERS_EXPR" ]] && EXPR_PARTS+=("$TIERS_EXPR")
    [[ -n "$KINDS_EXPR" ]] && EXPR_PARTS+=("$KINDS_EXPR")
    [[ -n "$CUSTOM_EXPR" ]] && EXPR_PARTS+=("$CUSTOM_EXPR")

    if [[ ${#EXPR_PARTS[@]} -gt 0 ]]; then
        # Join expressions with ' and ' but handle single expressions properly
        if [[ ${#EXPR_PARTS[@]} -eq 1 ]]; then
            MARKERS_EXPR="${EXPR_PARTS[0]}"
        else
            # Use printf to properly join with ' and ' separator
            MARKERS_EXPR=$(printf "%s and %s" "${EXPR_PARTS[0]}" "${EXPR_PARTS[1]}")
        fi
    else
        MARKERS_EXPR=""
    fi

    # Determine repo root (parent of this script's dir)
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

    echo "Root: $REPO_ROOT"
    echo "Markers: ${MARKERS_EXPR:-<none>}"

    cd "$REPO_ROOT" || exit 1
    if [[ -n "$MARKERS_EXPR" ]]; then
        python3 -m pytest -v -m "$MARKERS_EXPR" -m "not deprecated"
    else
        python3 -m pytest -v -m "not deprecated"
    fi
    exit $?
fi

# Legacy argument parsing (preserved for backward compatibility)
case "${1:-all}" in
    "all")
        echo "Running all tests (unified root pytest)..."
        SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
        REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
        cd "$REPO_ROOT" || exit 1
        python3 -m pytest -v -m "not deprecated"
        ;;
    "unit")
        echo "Running unit tests only (unified root pytest)..."
        SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
        REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
        cd "$REPO_ROOT" || exit 1
        python3 -m pytest -v -m "unit and not deprecated"
        ;;
    "integration")
        echo "Running integration tests only (unified root pytest)..."
        SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
        REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
        cd "$REPO_ROOT" || exit 1
        python3 -m pytest -v -m "integration and not deprecated"
        ;;
    "enhanced")
        echo "Running enhanced RAG system tests (unified root pytest)..."
        SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
        REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
        cd "$REPO_ROOT" || exit 1
        python3 -m pytest -v -m "tier2 and not deprecated"
        ;;
    "coverage")
        echo "Running tests with coverage (unified root pytest)..."
        SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
        REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
        cd "$REPO_ROOT" || exit 1
        python3 -m pytest -v -m "not deprecated" --cov=. --cov-report=html
        echo "📊 Coverage report generated in htmlcov/"
        ;;
    "quick")
        echo "Running quick tests (unified root pytest)..."
        SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
        REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
        cd "$REPO_ROOT" || exit 1
        python3 -m pytest -v -m "smoke and not deprecated"
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
