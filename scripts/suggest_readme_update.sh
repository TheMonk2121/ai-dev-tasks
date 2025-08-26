#!/usr/bin/env bash
set -euo pipefail

# README Context Update Suggestion Script
# - Analyzes recent changes and suggests README context updates
# - Helps maintain the README context pattern
# - Provides templates and guidance for implementation details

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Get recent commits that might need README context
get_recent_commits() {
    local days="${1:-7}"
    git log --since="$days days ago" --oneline --grep="B-[0-9]" | head -10 || true
}

# Extract backlog IDs from recent commits
extract_recent_backlog_ids() {
    local days="${1:-7}"
    git log --since="$days days ago" --oneline | grep -oE "B-[0-9]+" | sort | uniq || true
}

# Check if backlog item is documented in README
is_backlog_documented() {
    local backlog_id="$1"
    grep -q "$backlog_id" README.md 2>/dev/null
}

# Generate README context template for a backlog item
generate_readme_template() {
    local backlog_id="$1"
    local commit_hash="$2"
    local commit_msg="$3"
    
    cat << EOF

#### **$backlog_id: Feature Name** ($(date +%Y-%m-%d))
**Commit**: \`$commit_msg\`

**Rich Context:**
- **Feature Description**: Brief description of what was implemented
- **Technical Implementation**:
  - Key technical decisions and architecture choices
  - Technologies used and integration points
  - Database changes or schema modifications
- **Key Features**:
  - List of main features implemented
  - Performance improvements or optimizations
  - New capabilities or functionality
- **Implementation Challenges**:
  - Technical challenges encountered and solutions
  - Bugs fixed or issues resolved
  - Learning experiences and insights
- **Performance Impact**:
  - Performance metrics and improvements
  - Resource usage changes
  - Scalability considerations
- **Integration Points**:
  - How this integrates with existing systems
  - Dependencies and affected components
  - Future considerations or next steps

EOF
}

# Main function
main() {
    local days="${1:-7}"
    
    log_info "Analyzing recent commits for README context updates..."
    
    # Get recent backlog commits
    local recent_commits
    recent_commits=$(get_recent_commits "$days")
    
    if [[ -z "$recent_commits" ]]; then
        log_info "No recent commits with backlog references found"
        return 0
    fi
    
    echo
    log_info "Recent commits with backlog references:"
    echo "$recent_commits"
    echo
    
    # Check which backlog items need README documentation
    local backlog_ids
    backlog_ids=$(extract_recent_backlog_ids "$days")
    
    local needs_documentation=()
    
    for backlog_id in $backlog_ids; do
        if ! is_backlog_documented "$backlog_id"; then
            needs_documentation+=("$backlog_id")
        fi
    done
    
    if [[ ${#needs_documentation[@]} -eq 0 ]]; then
        log_success "All recent backlog items are already documented in README"
        return 0
    fi
    
    log_suggestion "The following backlog items need README context documentation:"
    echo
    
    for backlog_id in "${needs_documentation[@]}"; do
        echo "  - $backlog_id"
    done
    
    echo
    log_suggestion "To add README context for these items:"
    echo "1. Open README.md"
    echo "2. Find the 'Commit Context & Implementation Details' section"
    echo "3. Add entries for each backlog item using this template:"
    echo
    
    # Show template for first item
    local first_commit
    first_commit=$(git log --oneline --grep="${needs_documentation[0]}" | head -1)
    
    if [[ -n "$first_commit" ]]; then
        local commit_hash
        local commit_msg
        commit_hash=$(echo "$first_commit" | cut -d' ' -f1)
        commit_msg=$(echo "$first_commit" | cut -d' ' -f2-)
        
        generate_readme_template "${needs_documentation[0]}" "$commit_hash" "$commit_msg"
    fi
    
    log_suggestion "💡 Remember: README context preserves rich implementation details"
    log_suggestion "   while keeping commit messages GitHub-compliant (50/72 chars)"
}

# Show usage
usage() {
    echo "Usage: $0 [days]"
    echo "  days: Number of days to look back (default: 7)"
    echo
    echo "Examples:"
    echo "  $0        # Check last 7 days"
    echo "  $0 3      # Check last 3 days"
    echo "  $0 14     # Check last 14 days"
}

# Parse arguments
if [[ $# -gt 1 ]]; then
    usage
    exit 1
fi

if [[ $# -eq 1 ]]; then
    if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        usage
        exit 0
    fi
    
    if ! [[ "$1" =~ ^[0-9]+$ ]]; then
        log_error "Days must be a number"
        usage
        exit 1
    fi
fi

main "$@"
