#!/usr/bin/env bash
set -euo pipefail

# Post-commit hook for workflow integration
# - Triggers Scribe for backlog changes
# - Updates cursor memory for core documentation changes
# - Suggests README context updates for backlog items
# - Includes corruption detection guards

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_suggestion() {
    echo -e "${BLUE}[SUGGESTION]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Corruption detection guard
check_for_corruption() {
    log_info "Running corruption detection..."
    
    # Check for corruption markers in critical directories
    if command -v python3 >/dev/null 2>&1 && [[ -f "scripts/detect_corruption.py" ]]; then
        if ! python3 scripts/detect_corruption.py scripts src 2>/dev/null; then
            log_error "Corruption markers detected - skipping automation to prevent further damage"
            log_error "Run 'python3 scripts/detect_corruption.py scripts src' to see details"
            exit 0
        fi
    else
        # Fallback: simple grep check
        if grep -r 'result\.get("key", "")' scripts src 2>/dev/null | grep -q '.'; then
            log_error "Corruption markers present – skipping automation"
            exit 0
        fi
    fi
    
    log_success "No corruption detected"
}

# Get the last commit message
get_last_commit_message() {
    git log -1 --pretty=format:"%s"
}

# Check if commit message contains backlog reference
has_backlog_reference() {
    local commit_msg="$1"
    echo "$commit_msg" | grep -qE "B-[0-9]+"
}

# Extract backlog ID from commit message
extract_backlog_id() {
    local commit_msg="$1"
    echo "$commit_msg" | grep -oE "B-[0-9]+" | head -1 || true
}

# Check if backlog item is documented in README
is_backlog_documented() {
    local backlog_id="$1"
    grep -q "$backlog_id" README.md 2>/dev/null
}

# Check for changes in backlog-related files
check_backlog_changes() {
    local last_commit="$1"

    # Check if backlog files were modified
    if git show --name-only "$last_commit" | grep -qE "(000_core/000_backlog\.md|backlog)"; then
        log_info "Backlog changes detected - triggering Scribe..."

        # Trigger Scribe if available
        if command -v uv >/dev/null 2>&1 && [[ -f "scripts/utilities/trigger_scribe_update.py" ]]; then
            if ! uv run python scripts/utilities/trigger_scribe_update.py; then
                log_error "Failed to run trigger_scribe_update.py"
                return 1
            fi
        elif command -v uv >/dev/null 2>&1 && [[ -f "scripts/utilities/backlog_parser.py" ]]; then
            if ! uv run python scripts/utilities/backlog_parser.py --update; then
                log_error "Failed to run backlog_parser.py"
                return 1
            fi
        fi

        log_success "Backlog processing triggered"
    fi
}

# Check for core documentation changes
check_core_doc_changes() {
    local last_commit="$1"

    # Check if core documentation was modified
    if git show --name-only "$last_commit" | grep -qE "(100_memory/|400_guides/|000_core/)"; then
        log_info "Core documentation changes detected - updating cursor memory..."

        # Update cursor memory if available
        if command -v uv >/dev/null 2>&1 && [[ -f "scripts/utilities/update_cursor_memory.py" ]]; then
            if ! uv run python scripts/utilities/update_cursor_memory.py --no-few-shot; then
                log_error "Failed to run update_cursor_memory.py"
                return 1
            fi
        fi

        log_success "Cursor memory updated"
    fi
}

# Suggest README context updates
suggest_readme_updates() {
    local commit_msg="$1"

    if has_backlog_reference "$commit_msg"; then
        local backlog_id
        backlog_id=$(extract_backlog_id "$commit_msg")

        if [[ -n "$backlog_id" ]]; then
            if ! is_backlog_documented "$backlog_id"; then
                log_suggestion "📝 Backlog item $backlog_id committed but not documented in README"
                log_suggestion "   Consider adding implementation details to preserve context:"
                log_suggestion "   - Run: ./scripts/suggest_readme_update.sh 1"
                log_suggestion "   - Run: uv run python scripts/utilities/readme_context_manager.py --report"
                log_suggestion "   - Add to README.md 'Commit Context & Implementation Details' section"
            else
                log_success "Backlog item $backlog_id already documented in README"
            fi
        fi
    fi
}

# Run README context analysis if significant changes
run_context_analysis() {
    local commit_msg="$1"

    # Check if this was a significant change
    if has_backlog_reference "$commit_msg" || echo "$commit_msg" | grep -qE "(feat|fix|enhance|implement|complete)"; then
        log_info "Significant change detected - running README context analysis..."

        if command -v uv >/dev/null 2>&1 && [[ -f "scripts/utilities/readme_context_manager.py" ]]; then
            local analysis_output
            if analysis_output=$(uv run python scripts/utilities/readme_context_manager.py --analyze 1 2>/dev/null); then
                if [[ -n "$analysis_output" ]]; then
                    echo "$analysis_output" | while IFS= read -r line; do
                        if [[ "$line" == *"Need documentation"* ]]; then
                            log_suggestion "$line"
                        fi
                    done
                fi
            else
                log_error "Failed to run readme_context_manager.py"
                return 1
            fi
        fi
    fi
}

# Main execution
main() {
    local last_commit
    local commit_msg

    # Get the last commit hash and message
    last_commit=$(git rev-parse HEAD)
    commit_msg=$(get_last_commit_message)

    log_info "Post-commit processing for: $commit_msg"

    # Run corruption detection first
    check_for_corruption

    # Check for backlog changes
    if ! check_backlog_changes "$last_commit"; then
        log_error "Backlog processing failed"
        exit 1
    fi

    # Check for core documentation changes
    if ! check_core_doc_changes "$last_commit"; then
        log_error "Core documentation processing failed"
        exit 1
    fi

    # Suggest README context updates
    suggest_readme_updates "$commit_msg"

    # Run context analysis for significant changes
    if ! run_context_analysis "$commit_msg"; then
        log_error "Context analysis failed"
        exit 1
    fi

    log_success "Post-commit processing completed"
}

# Run main function
main "$@"
