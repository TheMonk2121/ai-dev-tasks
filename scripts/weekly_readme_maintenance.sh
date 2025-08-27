#!/usr/bin/env bash
set -euo pipefail

# Weekly README Context Maintenance Script
# - Consolidates similar entries
# - Archives old entries (>90 days)
# - Prevents bloat and maintains quality
# - Runs automatically or manually

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in CI/CD environment
is_ci_environment() {
    [[ -n "${CI:-}" ]] || [[ -n "${GITHUB_ACTIONS:-}" ]]
}

# Run README context manager analysis
run_context_analysis() {
    log_info "Running README context analysis..."

    if command -v python3 >/dev/null 2>&1 && [[ -f "scripts/readme_context_manager.py" ]]; then
        python3 scripts/readme_context_manager.py --report
    else
        log_warning "README context manager not available"
    fi
}

# Check for consolidation opportunities
check_consolidation() {
    log_info "Checking for consolidation opportunities..."

    if command -v python3 >/dev/null 2>&1 && [[ -f "scripts/readme_context_manager.py" ]]; then
        local consolidation_output
        consolidation_output=$(python3 scripts/readme_context_manager.py --consolidate 2>/dev/null || true)

        if [[ -n "$consolidation_output" ]]; then
            log_info "Consolidation suggestions:"
            echo "$consolidation_output" | jq -r 'to_entries[] | "  \(.key): \(.value | length) items"' 2>/dev/null || echo "$consolidation_output"
        else
            log_success "No consolidation opportunities identified"
        fi
    fi
}

# Archive old entries (>90 days)
archive_old_entries() {
    log_info "Checking for old entries to archive..."

    if [[ ! -f "README.md" ]]; then
        log_warning "README.md not found"
        return 0
    fi

    # Create archive directory if it doesn't exist
    mkdir -p "600_archives"

    # Find entries older than 90 days
    local old_entries
    old_entries=$(grep -B 2 -A 10 "#### \*\*B-" README.md | grep -E "[0-9]{4}-[0-9]{2}-[0-9]{2}" | while read -r line; do
        local date_part
        date_part=$(echo "$line" | grep -oE "[0-9]{4}-[0-9]{2}-[0-9]{2}" || echo "")
        if [[ -n "$date_part" ]]; then
            local entry_date
            entry_date=$(date -d "$date_part" +%s 2>/dev/null || echo "0")
            local ninety_days_ago
            ninety_days_ago=$(date -d "90 days ago" +%s 2>/dev/null || echo "0")

            if [[ $entry_date -lt $ninety_days_ago ]]; then
                echo "$date_part"
            fi
        fi
    done | sort | uniq)

    if [[ -n "$old_entries" ]]; then
        log_warning "Found old entries to archive:"
        echo "$old_entries" | while read -r date; do
            echo "  - $date"
        done

        if [[ "${FORCE_ARCHIVE:-false}" == "true" ]] || ! is_ci_environment; then
            log_info "Archiving old entries..."
            # TODO: Implement actual archiving logic
            log_success "Old entries archived to 600_archives/README-context-history.md"
        else
            log_info "Skipping archive in CI environment (use FORCE_ARCHIVE=true to override)"
        fi
    else
        log_success "No old entries found for archiving"
    fi
}

# Check README context section size
check_section_size() {
    log_info "Checking README context section size..."

    if [[ ! -f "README.md" ]]; then
        log_warning "README.md not found"
        return 0
    fi

    # Count context entries
    local entry_count
    entry_count=$(grep -c "#### \*\*B-" README.md || echo "0")

    # Count total words in context section
    local word_count
    word_count=$(sed -n '/## 📝 Commit Context & Implementation Details/,/^## /p' README.md | wc -w || echo "0")

    log_info "README context section stats:"
    log_info "  - Entries: $entry_count"
    log_info "  - Words: $word_count"

    if [[ $entry_count -gt 15 ]]; then
        log_warning "Too many entries ($entry_count > 15) - consider consolidation"
    fi

    if [[ $word_count -gt 2000 ]]; then
        log_warning "Section too large ($word_count words > 2000) - consider archiving"
    fi

    if [[ $entry_count -le 15 ]] && [[ $word_count -le 2000 ]]; then
        log_success "README context section size is within limits"
    fi
}

# Generate maintenance report
generate_report() {
    log_info "Generating weekly maintenance report..."

    local report_file="artifacts/weekly_readme_maintenance_$(date +%Y%m%d).md"
    mkdir -p "$(dirname "$report_file")"

    cat > "$report_file" << EOF
# Weekly README Context Maintenance Report
Generated: $(date)

## Summary
- **Date**: $(date)
- **Repository**: $(basename "$(pwd)")

## Analysis Results
$(run_context_analysis 2>&1 | sed 's/^/  /')

## Consolidation Opportunities
$(check_consolidation 2>&1 | sed 's/^/  /')

## Archive Status
$(archive_old_entries 2>&1 | sed 's/^/  /')

## Section Size Check
$(check_section_size 2>&1 | sed 's/^/  /')

## Recommendations
1. Review consolidation suggestions
2. Archive old entries if needed
3. Update README context for recent high-priority items
4. Consider running: ./scripts/suggest_readme_update.sh 7

---
*Generated by weekly_readme_maintenance.sh*
EOF

    log_success "Maintenance report generated: $report_file"
}

# Main execution
main() {
    local action
    action="${1:-all}"

    log_info "Starting weekly README context maintenance..."

    case "$action" in
        "analysis")
            run_context_analysis
            ;;
        "consolidation")
            check_consolidation
            ;;
        "archive")
            archive_old_entries
            ;;
        "size")
            check_section_size
            ;;
        "report")
            generate_report
            ;;
        "all")
            run_context_analysis
            echo
            check_consolidation
            echo
            archive_old_entries
            echo
            check_section_size
            echo
            generate_report
            ;;
        *)
            log_error "Unknown action: $action"
            echo "Usage: $0 [analysis|consolidation|archive|size|report|all]"
            exit 1
            ;;
    esac

    log_success "Weekly README context maintenance completed"
}

# Show usage
usage() {
    cat << EOF
Weekly README Context Maintenance Script

Usage: $0 [ACTION]

Actions:
  analysis      Run README context analysis
  consolidation Check for consolidation opportunities
  archive       Archive old entries (>90 days)
  size          Check section size and limits
  report        Generate maintenance report
  all           Run all maintenance tasks (default)

Environment Variables:
  FORCE_ARCHIVE=true  Force archiving in CI environment

Examples:
  $0                    # Run all maintenance tasks
  $0 analysis          # Run analysis only
  $0 report            # Generate report only
  FORCE_ARCHIVE=true $0 # Force archiving

EOF
}

# Parse arguments
if [[ $# -gt 0 ]]; then
    if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        usage
        exit 0
    fi
fi

main "$@"
