#!/bin/bash
"""
Pre-commit Documentation Validation Hook

Automatically runs documentation coherence validation before commits.
Integrates with the B-060 Documentation Coherence Validation System.

Usage: This script is automatically called by git pre-commit hooks.
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR_SCRIPT="$SCRIPT_DIR/doc_coherence_validator.py"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if we're in the right directory
check_environment() {
    if [[ ! -f "$PROJECT_ROOT/000_backlog.md" ]]; then
        log_error "Not in AI development ecosystem project root"
        exit 1
    fi
    
    if [[ ! -f "$VALIDATOR_SCRIPT" ]]; then
        log_error "Documentation validator script not found: $VALIDATOR_SCRIPT"
        exit 1
    fi
}

# Check if any markdown files are staged
check_staged_markdown() {
    local staged_md_files
    staged_md_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$' || true)
    
    if [[ -z "$staged_md_files" ]]; then
        log_info "No markdown files staged for commit - skipping validation"
        return 0
    fi
    
    log_info "Found staged markdown files:"
    echo "$staged_md_files" | while read -r file; do
        log_info "  - $file"
    done
    
    return 1
}

# Run documentation validation
run_validation() {
    log_info "Running documentation coherence validation..."
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Run validator in dry-run mode for pre-commit
    if python3 "$VALIDATOR_SCRIPT" --dry-run; then
        log_success "Documentation validation passed"
        return 0
    else
        log_error "Documentation validation failed"
        log_warning "Please fix documentation issues before committing"
        log_info "Run 'python3 $VALIDATOR_SCRIPT --no-dry-run' to see detailed issues"
        return 1
    fi
}

# Check for critical files
check_critical_files() {
    local critical_files=(
        "100_cursor-memory-context.md"
        "000_backlog.md"
        "400_system-overview.md"
        "400_project-overview.md"
    )
    
    local has_critical_changes=false
    
    for file in "${critical_files[@]}"; do
        if git diff --cached --name-only | grep -q "$file"; then
            log_warning "Critical file modified: $file"
            has_critical_changes=true
        fi
    done
    
    if [[ "$has_critical_changes" == "true" ]]; then
        log_info "Critical files modified - running enhanced validation"
        return 0
    fi
    
    return 1
}

# Main execution
main() {
    log_info "Pre-commit documentation validation hook"
    
    # Check environment
    check_environment
    
    # Check if we have staged markdown files
    if check_staged_markdown; then
        log_success "No markdown files to validate"
        exit 0
    fi
    
    # Check for critical file changes
    if check_critical_files; then
        log_info "Critical files detected - running full validation"
    else
        log_info "Running standard validation"
    fi
    
    # Run validation
    if run_validation; then
        log_success "Pre-commit validation completed successfully"
        exit 0
    else
        log_error "Pre-commit validation failed"
        log_warning "Commit blocked due to documentation issues"
        log_info "Fix the issues above and try committing again"
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Pre-commit Documentation Validation Hook"
        echo ""
        echo "Usage: $0 [--help]"
        echo ""
        echo "This script is automatically called by git pre-commit hooks."
        echo "It validates documentation coherence before commits."
        exit 0
        ;;
    --install)
        log_info "Installing pre-commit hook..."
        if [[ -d ".git/hooks" ]]; then
            cp "$0" ".git/hooks/pre-commit"
            chmod +x ".git/hooks/pre-commit"
            log_success "Pre-commit hook installed"
        else
            log_error "Not a git repository"
            exit 1
        fi
        exit 0
        ;;
    --uninstall)
        log_info "Uninstalling pre-commit hook..."
        if [[ -f ".git/hooks/pre-commit" ]]; then
            rm ".git/hooks/pre-commit"
            log_success "Pre-commit hook uninstalled"
        else
            log_warning "Pre-commit hook not found"
        fi
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
