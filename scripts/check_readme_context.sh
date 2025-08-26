#!/usr/bin/env bash
set -euo pipefail

# README Context Pattern Validation Hook
# - Ensures significant changes have corresponding README context updates
# - Checks for backlog item references in commit messages
# - Validates README context section is updated for major changes
# - Fast execution (<1 second)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_suggestion() {
    echo -e "${BLUE}[SUGGESTION]${NC} $1"
}

# Check if commit message references a backlog item
has_backlog_reference() {
    local commit_msg="$1"
    # Check for B-#### pattern in commit message
    if echo "$commit_msg" | grep -qE "B-[0-9]+"; then
        return 0
    fi
    return 1
}

# Extract backlog ID from commit message
extract_backlog_id() {
    local commit_msg="$1"
    echo "$commit_msg" | grep -oE "B-[0-9]+" | head -1
}

# Check if README context section exists and is recent
check_readme_context_section() {
    local readme_file="README.md"

    if [[ ! -f "$readme_file" ]]; then
        log_error "README.md not found"
        return 1
    fi

    # Check if Commit Context section exists
    if ! grep -q "## 📝 Commit Context & Implementation Details" "$readme_file"; then
        log_error "README missing 'Commit Context & Implementation Details' section"
        log_suggestion "Add this section to preserve implementation context"
        return 1
    fi

    # Check if section was updated recently (within last 7 days)
    local section_start
    section_start=$(grep -n "## 📝 Commit Context & Implementation Details" "$readme_file" | cut -d: -f1)
    if [[ -z "$section_start" ]]; then
        return 1
    fi

    # Get the last modification time of README
    local readme_mtime
    local current_time
    local days_since_update
    readme_mtime=$(stat -f "%m" "$readme_file" 2>/dev/null || stat -c "%Y" "$readme_file" 2>/dev/null)
    current_time=$(date +%s)
    days_since_update=$(( (current_time - readme_mtime) / 86400 ))

    if [[ $days_since_update -gt 7 ]]; then
        log_suggestion "README context section hasn't been updated in $days_since_update days"
        log_suggestion "Consider updating with recent implementation details"
    fi

    return 0
}

# Check if this is a significant change that needs README context
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

# Main validation function
validate_readme_context_pattern() {
    local commit_msg_file="$1"
    local failed=0

    log_info "Checking README context pattern..."

    # Read commit message
    local commit_msg
    commit_msg=""
    while IFS= read -r line; do
        if [[ -z "$commit_msg" ]]; then
            commit_msg="$line"
        fi
    done < "$commit_msg_file"

    # Get staged files
    local staged_files
    staged_files=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || echo "")

    # Check if this is a significant change
    if ! is_significant_change "$staged_files"; then
        log_success "Minor change detected - README context not required"
        return 0
    fi

    # Check for backlog reference
    if ! has_backlog_reference "$commit_msg"; then
        log_suggestion "Consider adding backlog reference (e.g., B-077) to commit message"
        log_suggestion "This helps with traceability and README context updates"
    else
        local backlog_id
        backlog_id=$(extract_backlog_id "$commit_msg")
        log_success "Backlog reference found: $backlog_id"
    fi

    # Check README context section
    if ! check_readme_context_section; then
        log_suggestion "Update README 'Commit Context & Implementation Details' section with:"
        log_suggestion "  - Technical decisions and reasoning"
        log_suggestion "  - Implementation challenges and solutions"
        log_suggestion "  - Performance impact and metrics"
        log_suggestion "  - Integration points and dependencies"
        failed=1
    else
        log_success "README context section is present and recent"
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

    # Provide guidance for README updates
    if [[ $failed -eq 0 ]]; then
        log_suggestion "💡 Remember to update README context section with implementation details"
        log_suggestion "   This preserves rich context while keeping commits GitHub-compliant"
    fi

    return $failed
}

# Main execution
main() {
    local commit_msg_file="$1"

    if [[ -z "$commit_msg_file" ]]; then
        log_error "No commit message file provided"
        exit 1
    fi

    if ! validate_readme_context_pattern "$commit_msg_file"; then
        exit 1
    fi

    exit 0
}

main "$@"
