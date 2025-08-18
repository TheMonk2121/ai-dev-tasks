#!/bin/bash

# Bug-Fix CI Guard Script
# Validates bugfix PR requirements based on commit message prefixes

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REQUIRED_SECTIONS=("Problem Snapshot" "Fix Plan" "Test Plan")
REQUIRED_CHECKLIST_ITEMS=(
    "Problem Snapshot is complete and clear"
    "Fix Plan documents what was changed and what wasn't"
    "Blast radius is assessed and documented"
    "Confidence level is ≥ 0.8"
    "Repro test demonstrates the original bug"
    "Guardrail test prevents regression"
    "Test files are included in the PR"
)

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "PASS")
            echo -e "${GREEN}OK PASS${NC}: $message"
            ;;
        "FAIL")
            echo -e "${RED}X FAIL${NC}: $message"
            ;;
        "WARN")
            echo -e "${YELLOW}!️  WARN${NC}: $message"
            ;;
    esac
}

# Function to check if PR is a bugfix
is_bugfix_pr() {
    local commit_msg="$1"
    if [[ "$commit_msg" =~ ^(fix|hotfix): ]]; then
        return 0
    fi
    return 1
}

# Function to check if files are in hot zones
is_hot_zone_change() {
    local files="$1"
    if echo "$files" | grep -q -E "(src/validator/|src/vector_store/|src/dashboard/|scripts/archive_.*\.py)"; then
        return 0
    fi
    return 1
}

# Function to validate PR description
validate_pr_description() {
    local pr_body="$1"
    local missing_sections=()

    for section in "${REQUIRED_SECTIONS[@]}"; do
        if ! echo "$pr_body" | grep -q "### $section"; then
            missing_sections+=("$section")
        fi
    done

    if [ ${#missing_sections[@]} -gt 0 ]; then
        print_status "FAIL" "Missing required sections: ${missing_sections[*]}"
        return 1
    fi

    print_status "PASS" "All required sections present"
    return 0
}

# Function to validate checklist
validate_checklist() {
    local pr_body="$1"
    local missing_items=()

    for item in "${REQUIRED_CHECKLIST_ITEMS[@]}"; do
        if ! echo "$pr_body" | grep -q "\\[ \\] $item"; then
            missing_items+=("$item")
        fi
    done

    if [ ${#missing_items[@]} -gt 0 ]; then
        print_status "WARN" "Missing checklist items: ${missing_items[*]}"
        return 1
    fi

    print_status "PASS" "All checklist items present"
    return 0
}

# Function to check for test files
validate_test_files() {
    local changed_files="$1"
    local test_files_found=false

    while IFS= read -r file; do
        if [[ "$file" =~ test.*\.py$ ]] || [[ "$file" =~ .*_test\.py$ ]]; then
            test_files_found=true
            break
        fi
    done <<< "$changed_files"

    if [ "$test_files_found" = false ]; then
        print_status "FAIL" "No test files found in changes"
        return 1
    fi

    print_status "PASS" "Test files included"
    return 0
}

# Function to validate commit message format
validate_commit_message() {
    local commit_msg="$1"

    if [[ ! "$commit_msg" =~ ^(fix|hotfix|feat|refactor|docs|style|test|chore)(\(.+\))?: ]]; then
        print_status "FAIL" "Invalid commit message format. Must follow Conventional Commits: type(scope): description"
        return 1
    fi

    print_status "PASS" "Commit message format valid"
    return 0
}

# Main validation function
main() {
    local commit_msg="$1"
    local pr_body="$2"
    local changed_files="$3"
    local mode="${4:-WARN}"  # WARN or BLOCK

    echo "🔍 Bug-Fix CI Guard - Mode: $mode"
    echo "=================================="

    local exit_code=0
    local validation_failures=0

    # Check if this is a bugfix PR
    if is_bugfix_pr "$commit_msg"; then
        echo "🐛 Bugfix PR detected"

        # Validate commit message format
        if ! validate_commit_message "$commit_msg"; then
            ((validation_failures++))
        fi

        # Validate PR description
        if ! validate_pr_description "$pr_body"; then
            ((validation_failures++))
        fi

        # Validate checklist
        if ! validate_checklist "$pr_body"; then
            ((validation_failures++))
        fi

        # Validate test files
        if ! validate_test_files "$changed_files"; then
            ((validation_failures++))
        fi

    elif is_hot_zone_change "$changed_files"; then
        echo "🔥 Hot-zone change detected"
        print_status "WARN" "Changes in hot zones should use bug-fix playbook"

        # Validate commit message format
        if ! validate_commit_message "$commit_msg"; then
            ((validation_failures++))
        fi

        # Validate test files
        if ! validate_test_files "$changed_files"; then
            ((validation_failures++))
        fi

    else
        echo "📝 Regular PR - basic validation only"

        # Validate commit message format
        if ! validate_commit_message "$commit_msg"; then
            ((validation_failures++))
        fi
    fi

    echo ""
    echo "📊 Validation Summary"
    echo "===================="

    if [ $validation_failures -eq 0 ]; then
        print_status "PASS" "All validations passed"
        exit_code=0
    else
        print_status "FAIL" "$validation_failures validation(s) failed"
        exit_code=1
    fi

    # In BLOCK mode, exit with failure code
    if [ "$mode" = "BLOCK" ] && [ $exit_code -ne 0 ]; then
        echo ""
        echo "🚫 BLOCK mode enabled - PR blocked due to validation failures"
        echo "Please fix the issues above and try again."
        exit $exit_code
    fi

    # In WARN mode, always exit successfully but show warnings
    if [ "$mode" = "WARN" ] && [ $exit_code -ne 0 ]; then
        echo ""
        echo "!️  WARN mode - PR allowed but please address the issues above"
        exit 0
    fi

    exit $exit_code
}

# Help function
show_help() {
    cat << EOF
Bug-Fix CI Guard Script

Usage: $0 <commit_message> <pr_body> <changed_files> [mode]

Arguments:
  commit_message  The commit message for the PR
  pr_body         The PR description/body
  changed_files   List of changed files (one per line)
  mode            Validation mode: WARN (default) or BLOCK

Examples:
  $0 "fix: resolve validation error" "PR body content" "file1.py\nfile2.py" WARN
  $0 "hotfix: critical bug fix" "PR body content" "test_file.py" BLOCK

Environment Variables:
  BUGFIX_GUARD_MODE  Override mode (WARN/BLOCK)

EOF
}

# Check if help is requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

# Validate arguments
if [ $# -lt 3 ]; then
    echo "Error: Insufficient arguments"
    show_help
    exit 1
fi

# Get mode from environment or argument
MODE="${BUGFIX_GUARD_MODE:-${4:-WARN}}"

# Run main validation
main "$1" "$2" "$3" "$MODE"
