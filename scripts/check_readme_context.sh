#!/usr/bin/env bash
set -euo pipefail

# README Context Pattern Validation Hook
# - Enforces README context documentation for significant changes
# - Integrates with README context manager for smart analysis
# - Provides actionable suggestions for compliance

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_suggestion() {
    echo -e "${BLUE}[SUGGESTION]${NC} $1"
}

# Get commit message from file or stdin
get_commit_message() {
    if [[ $# -eq 1 ]]; then
        cat "$1"
    else
        cat
    fi
}

# Extract backlog ID from commit message
extract_backlog_id() {
    local commit_msg="$1"
    echo "$commit_msg" | grep -oE "B-[0-9]+" | head -1 || true
}

# Check if change is significant based on file patterns
is_significant_change() {
    local staged_files="$1"

    # High-priority patterns that definitely need README context
    local high_priority_patterns=(
        "scripts/.*\.py$"     # New scripts
        "100_memory/.*\.md$"  # Memory system changes
        "000_core/.*\.md$"    # Core workflow changes
        "400_guides/.*\.md$"  # Guide changes
        "dspy-rag-system/.*\.py$"  # DSPy system changes
        "\.sql$"              # Database schema changes
        "requirements"        # Dependency changes
        "pyproject"           # Project config changes
    )

    # Medium-priority patterns that should have README context
    local medium_priority_patterns=(
        "\.py$"               # Python files
        "\.md$"               # Documentation
        "\.yml$|\.yaml$"      # Configuration
        "\.json$"             # Data files
    )

    # Check high-priority patterns first
    for pattern in "${high_priority_patterns[@]}"; do
        if echo "$staged_files" | grep -qE "$pattern"; then
            return 0
        fi
    done

    # Check medium-priority patterns
    for pattern in "${medium_priority_patterns[@]}"; do
        if echo "$staged_files" | grep -qE "$pattern"; then
            return 0
        fi
    done

    return 1
}

# Check if commit message has backlog reference
has_backlog_reference() {
    local commit_msg="$1"
    echo "$commit_msg" | grep -qE "B-[0-9]+"
}

# Validate README context pattern
validate_readme_context_pattern() {
    local commit_msg="$1"
    local staged_files="$2"
    local failed=0

    # Check if this is a significant change
    if ! is_significant_change "$staged_files"; then
        log_success "Change not significant - no README context required"
        return 0
    fi

    log_suggestion "Significant change detected - checking README context..."

    # Check if README context section exists and is recent
    if ! grep -q "## 📝 Commit Context & Implementation Details" README.md 2>/dev/null; then
        log_warning "README context section not found"
        log_suggestion "Add README context section to preserve implementation details"
        failed=1
    else
        # Check if section was updated recently (within last 7 days)
        local last_update
        last_update=$(grep -A 5 "## 📝 Commit Context & Implementation Details" README.md | grep -E "[0-9]{4}-[0-9]{2}-[0-9]{2}" | tail -1 | grep -oE "[0-9]{4}-[0-9]{2}-[0-9]{2}" || echo "")

        if [[ -n "$last_update" ]]; then
            local last_update_date
            last_update_date=$(date -d "$last_update" +%s 2>/dev/null || echo "0")
            local seven_days_ago
            seven_days_ago=$(date -d "7 days ago" +%s 2>/dev/null || echo "0")

            if [[ $last_update_date -lt $seven_days_ago ]]; then
                log_warning "README context section not updated recently (last: $last_update)"
                log_suggestion "Consider updating README context for recent changes"
            else
                log_success "README context section updated recently"
            fi
        fi
    fi

    # Check if README needs updating for this specific change
    if has_backlog_reference "$commit_msg"; then
        local backlog_id
        backlog_id=$(extract_backlog_id "$commit_msg")

        # Check if this backlog item is already documented in README
        if ! grep -q "$backlog_id" README.md 2>/dev/null; then
            log_suggestion "📝 Backlog item $backlog_id not found in README context section"
            log_suggestion "   Add implementation details to preserve rich context:"
            log_suggestion "   - Technical decisions and reasoning"
            log_suggestion "   - Implementation challenges and solutions"
            log_suggestion "   - Performance impact and metrics"
            log_suggestion "   - Integration points and dependencies"
            failed=1
        else
            log_success "Backlog item $backlog_id already documented in README"
        fi
    fi

    # Run README context manager analysis if available
    if command -v python3 >/dev/null 2>&1 && [[ -f "scripts/readme_context_manager.py" ]]; then
        log_suggestion "Running README context analysis..."

        # Get quick analysis for this specific change
        local analysis_output
        analysis_output=$(python3 scripts/readme_context_manager.py --analyze 7 2>/dev/null || true)

        if [[ -n "$analysis_output" ]]; then
            echo "$analysis_output" | while IFS= read -r line; do
                if [[ "$line" == *"Need documentation"* ]]; then
                    log_suggestion "$line"
                fi
            done
        fi
    fi

    return $failed
}

# Main validation function
main() {
    local commit_msg
    local staged_files
    local failed=0

    # Get commit message
    commit_msg=$(get_commit_message "$@")

    # Get staged files
    staged_files=$(git diff --cached --name-only 2>/dev/null || echo "")

    if [[ -z "$staged_files" ]]; then
        log_success "No staged files - skipping README context validation"
        return 0
    fi

    # Validate README context pattern
    if ! validate_readme_context_pattern "$commit_msg" "$staged_files"; then
        failed=1
    fi

    # Provide helpful suggestions
    if [[ $failed -eq 1 ]]; then
        echo
        log_suggestion "💡 To fix README context issues:"
        log_suggestion "   1. Run: ./scripts/suggest_readme_update.sh 7"
        log_suggestion "   2. Run: python3 scripts/readme_context_manager.py --report"
        log_suggestion "   3. Add implementation details to README.md context section"
        log_suggestion "   4. Use --no-verify for emergency commits (document within 24h)"
        echo
    fi

    return $failed
}

# Run main function with all arguments
main "$@"
