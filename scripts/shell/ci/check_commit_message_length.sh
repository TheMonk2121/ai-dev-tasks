#!/usr/bin/env bash
set -euo pipefail

# Commit Message Line Length Validation Hook
# - Enforces GitHub's recommended line length limits
# - Subject line: 50 characters maximum
# - Body lines: 72 characters maximum
# - Provides clear guidance for improvement
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

# Check commit message line lengths
check_commit_message_length() {
    local commit_msg_file="$1"
    local failed=0

    log_info "Checking commit message line lengths..."

    # Read the commit message file
    if [[ ! -f "$commit_msg_file" ]]; then
        log_error "Commit message file not found: $commit_msg_file"
        return 1
    fi

    local line_number=0
    local subject_line=""
    local body_lines=()
    local body_line_count=0

    while IFS= read -r line; do
        ((line_number++))

        # Skip empty lines and comments
        if [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi

        # First non-empty line is the subject
        if [[ -z "$subject_line" ]]; then
            subject_line="$line"
            local subject_length=${#line}

            if [[ $subject_length -gt 50 ]]; then
                log_error "Subject line too long: $subject_length characters (max 50)"
                log_error "  Line $line_number: $line"
                log_suggestion "Consider: $(echo "$line" | cut -c1-47)..."
                failed=1
            fi
        else
            # Subsequent lines are body
            body_lines+=("$line")
            local body_length=${#line}
            ((body_line_count++))

            if [[ $body_length -gt 72 ]]; then
                log_error "Body line too long: $body_length characters (max 72)"
                log_error "  Line $line_number: $line"
                log_suggestion "Consider breaking into multiple lines or shortening"
                failed=1
            fi
        fi
    done < "$commit_msg_file"

    # Provide simple, actionable guidance
    if [[ $body_line_count -eq 0 ]]; then
        log_suggestion "Consider adding a body to explain the change in detail"
    fi

    if [[ -n "$subject_line" ]]; then
        if echo "$subject_line" | grep -qE "^[a-z]+\([^)]+\):"; then
            log_success "Subject line follows conventional commits format"
        else
            log_suggestion "Consider using conventional commits format: type(scope): description"
        fi
    fi

    # Encourage README context pattern
    if [[ $body_line_count -gt 0 ]]; then
        log_suggestion "💡 Tip: For rich implementation details, consider updating the README's 'Commit Context & Implementation Details' section"
        log_suggestion "   This preserves context while keeping commit messages concise and GitHub-compliant"
    fi

    if [[ $failed -eq 0 ]]; then
        log_success "Commit message line lengths are within limits"
        log_info "  Subject: ${#subject_line} characters"
        log_info "  Body: $body_line_count lines"
        return 0
    else
        log_error "Commit message line length validation failed"
        log_info "GitHub recommendations:"
        log_info "  - Subject line: 50 characters maximum"
        log_info "  - Body lines: 72 characters maximum"
        log_info "  - Use conventional commits format: type(scope): description"
        return 1
    fi
}

# Main execution
main() {
    # Pre-commit passes the commit message file as the first argument
    local commit_msg_file="$1"

    if [[ -z "$commit_msg_file" ]]; then
        log_error "No commit message file provided"
        exit 1
    fi

    if ! check_commit_message_length "$commit_msg_file"; then
        exit 1
    fi

    exit 0
}

main "$@"
