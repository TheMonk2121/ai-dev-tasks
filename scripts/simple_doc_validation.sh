#!/usr/bin/env bash
set -euo pipefail

# Simple Documentation Validation Hook
# - Basic checks for broken links and structure
# - Fast execution (<1 second)
# - No complex caching or worker pools

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check for broken internal links
check_broken_links() {
    local staged_files
    staged_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$' || true)

    if [[ -z "$staged_files" ]]; then
        return 0
    fi

    log_info "Checking for broken internal links..."

    # Simple check for obvious broken links
    local broken_links=0

    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            # Check for links to non-existent files (simplified)
            while IFS= read -r link; do
                # Extract filename from markdown link
                local link_file=$(echo "$link" | sed -n 's/.*](\([^)]*\)).*/\1/p')
                # Skip external links and anchors
                if [[ "$link_file" =~ ^https?:// ]] || [[ "$link_file" =~ ^# ]]; then
                    continue
                fi
                # Check if file exists
                if [[ -n "$link_file" ]] && [[ ! -f "$link_file" ]]; then
                    log_error "Broken link in $file: $link"
                    ((broken_links++))
                fi
            done < <(grep -o '\[[^\]]*\]([^)]*)' "$file" || true)
        fi
    done <<< "$staged_files"

    if [[ $broken_links -gt 0 ]]; then
        log_error "Found $broken_links broken link(s)"
        return 1
    fi

    return 0
}

# Check for basic markdown structure
check_markdown_structure() {
    local staged_files
    staged_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$' || true)

    if [[ -z "$staged_files" ]]; then
        return 0
    fi

    log_info "Checking markdown structure..."

    local issues=0

    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            # Check for trailing spaces
            if grep -q '[[:space:]]$' "$file" 2>/dev/null; then
                log_error "Trailing spaces found in $file"
                ((issues++))
            fi

            # Check for hard tabs
            if grep -q $'\t' "$file"; then
                log_error "Hard tabs found in $file"
                ((issues++))
            fi
        fi
    done <<< "$staged_files"

    if [[ $issues -gt 0 ]]; then
        log_error "Found $issues structure issue(s)"
        return 1
    fi

    return 0
}

# Main execution
main() {
    log_info "Running simple documentation validation..."

    local failed=0

    # Run checks
    if ! check_broken_links; then
        failed=1
    fi

    if ! check_markdown_structure; then
        failed=1
    fi

    if [[ $failed -eq 0 ]]; then
        log_success "Documentation validation passed"
        exit 0
    else
        log_error "Documentation validation failed"
        exit 1
    fi
}

main "$@"
