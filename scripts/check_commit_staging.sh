#!/usr/bin/env bash
set -euo pipefail

# Commit Staging Pattern Validation Hook
# - Ensures consistent staging and commit patterns
# - Validates commit scope and granularity
# - Checks for proper file organization in commits
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

# Check if staged files are logically grouped
check_commit_scope() {
    local staged_files="$1"
    local commit_msg="$2"

        # Count different file types
    local python_files
    local doc_files
    local config_files
    local test_files
    local total_files

    if [[ -n "$staged_files" ]]; then
        python_files=$(echo "$staged_files" | grep -E "\.py$" | wc -l)
        doc_files=$(echo "$staged_files" | grep -E "\.md$" | wc -l)
        config_files=$(echo "$staged_files" | grep -E "\.(yml|yaml|json|toml)$" | wc -l)
        test_files=$(echo "$staged_files" | grep -E "test_.*\.py$" | wc -l)
        total_files=$(echo "$staged_files" | wc -l)
    else
        python_files=0
        doc_files=0
        config_files=0
        test_files=0
        total_files=0
    fi

    # Check for mixed file types (potential scope creep)
    local file_types=0
    if [[ $python_files -gt 0 ]]; then ((file_types++)); fi
    if [[ $doc_files -gt 0 ]]; then ((file_types++)); fi
    if [[ $config_files -gt 0 ]]; then ((file_types++)); fi
    if [[ $test_files -gt 0 ]]; then ((file_types++)); fi

    # Large commits with mixed types might need splitting
    if [[ $total_files -gt 10 && $file_types -gt 2 ]]; then
        log_suggestion "Large commit with mixed file types detected ($total_files files, $file_types types)"
        log_suggestion "Consider splitting into smaller, focused commits:"
        log_suggestion "  - Core functionality changes"
        log_suggestion "  - Documentation updates"
        log_suggestion "  - Configuration changes"
        log_suggestion "  - Test updates"
        return 1
    fi

    # Check for test files without corresponding source changes
    if [[ $test_files -gt 0 && $python_files -eq 0 ]]; then
        log_suggestion "Test files staged without source code changes"
        log_suggestion "Consider if tests should be committed with their source changes"
    fi

    return 0
}

# Check for common staging anti-patterns
check_staging_anti_patterns() {
    local staged_files="$1"
    local failed=0

    # Check for temporary files
    local temp_files
    temp_files=$(echo "$staged_files" | grep -E "(\.tmp$|\.temp$|\.log$|\.cache$)" || true)
    if [[ -n "$temp_files" ]]; then
        log_error "Temporary files detected in staging:"
        echo "$temp_files" | while read -r file; do
            log_error "  - $file"
        done
        log_suggestion "Remove temporary files: git reset HEAD <file>"
        failed=1
    fi

    # Check for IDE/editor files
    local ide_files
    ide_files=$(echo "$staged_files" | grep -E "(\.vscode/|\.idea/|\.swp$|\.swo$|~$)" || true)
    if [[ -n "$ide_files" ]]; then
        log_error "IDE/editor files detected in staging:"
        echo "$ide_files" | while read -r file; do
            log_error "  - $file"
        done
        log_suggestion "Remove IDE files: git reset HEAD <file>"
        log_suggestion "Add to .gitignore to prevent future staging"
        failed=1
    fi

    # Check for large binary files
    local large_files
    large_files=$(echo "$staged_files" | while read -r file; do
        if [[ -f "$file" ]]; then
            local size
            size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
            if [[ $size -gt 1048576 ]]; then  # 1MB
                echo "$file ($((size/1024))KB)"
            fi
        fi
    done)

    if [[ -n "$large_files" ]]; then
        log_suggestion "Large files detected (>1MB):"
        echo "$large_files" | while read -r file; do
            log_suggestion "  - $file"
        done
        log_suggestion "Consider if large files should be in version control"
    fi

    return $failed
}

# Validate commit message matches staged changes
validate_commit_message_scope() {
    local staged_files="$1"
    local commit_msg="$2"

    # Extract commit type and scope
    local commit_type
    local has_backlog_ref
    commit_type=$(echo "$commit_msg" | grep -oE "^(feat|fix|docs|style|refactor|test|chore)" || echo "")
    has_backlog_ref=$(echo "$commit_msg" | grep -qE "B-[0-9]+" && echo "yes" || echo "no")

        # Check for appropriate commit type based on file types
    local python_files
    local doc_files
    local test_files
    local config_files

    if [[ -n "$staged_files" ]]; then
        python_files=$(echo "$staged_files" | grep -E "\.py$" | wc -l)
        doc_files=$(echo "$staged_files" | grep -E "\.md$" | wc -l)
        test_files=$(echo "$staged_files" | grep -E "test_.*\.py$" | wc -l)
        config_files=$(echo "$staged_files" | grep -E "\.(yml|yaml|json|toml)$" | wc -l)
    else
        python_files=0
        doc_files=0
        test_files=0
        config_files=0
    fi

    # Suggest appropriate commit type
    if [[ -z "$commit_type" ]]; then
        log_suggestion "No conventional commit type detected"
        if [[ $python_files -gt 0 ]]; then
            log_suggestion "Consider: feat (new feature), fix (bug fix), refactor (code changes)"
        elif [[ $doc_files -gt 0 ]]; then
            log_suggestion "Consider: docs (documentation changes)"
        elif [[ $test_files -gt 0 ]]; then
            log_suggestion "Consider: test (test changes)"
        elif [[ $config_files -gt 0 ]]; then
            log_suggestion "Consider: chore (configuration changes)"
        fi
    fi

    # Check for backlog reference consistency
    if [[ $python_files -gt 0 && "$has_backlog_ref" == "no" ]]; then
        log_suggestion "Code changes detected without backlog reference"
        log_suggestion "Consider adding backlog ID (e.g., B-077) for traceability"
    fi

    return 0
}

# Main validation function
validate_commit_staging() {
    local commit_msg_file="$1"
    local failed=0

    log_info "Checking commit staging patterns..."

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

    if [[ -z "$staged_files" ]]; then
        log_error "No files staged for commit"
        log_suggestion "Stage files: git add <files>"
        return 1
    fi

    # Check commit scope
    if ! check_commit_scope "$staged_files" "$commit_msg"; then
        failed=1
    fi

    # Check for anti-patterns
    if ! check_staging_anti_patterns "$staged_files"; then
        failed=1
    fi

    # Validate commit message scope
    if ! validate_commit_message_scope "$staged_files" "$commit_msg"; then
        failed=1
    fi

    # Success summary
    if [[ $failed -eq 0 ]]; then
        local file_count
        file_count=$(echo "$staged_files" | wc -l | tr -d ' ')
        log_success "Commit staging validation passed ($file_count files)"
        log_suggestion "💡 Remember to update README context section for significant changes"
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

    if ! validate_commit_staging "$commit_msg_file"; then
        exit 1
    fi

    exit 0
}

main "$@"
