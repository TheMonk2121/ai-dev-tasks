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

    if [[ -f "scripts/readme_context_manager.py" ]]; then
        uv run python scripts/readme_context_manager.py --report
    else
        log_warning "README context manager not available"
    fi
}

# Check for consolidation opportunities
check_consolidation() {
    log_info "Checking for consolidation opportunities..."

    if [[ -f "scripts/readme_context_manager.py" ]]; then
        local consolidation_output
        consolidation_output=$(uv run python scripts/readme_context_manager.py --consolidate 2>/dev/null || true)

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

    if [[ "${FORCE_ARCHIVE:-false}" != "true" ]] && is_ci_environment; then
        log_info "Skipping archive in CI environment (use FORCE_ARCHIVE=true to override)"
        return 0
    fi

    mkdir -p "600_archives"

    local archive_output
    archive_output=$(uv run python - "$(pwd)/README.md" "$(pwd)/600_archives/README-context-history.md" 90 <<'PY'
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

readme_path = Path(sys.argv[1])
archive_path = Path(sys.argv[2])
threshold_days = int(sys.argv[3])

if not readme_path.exists():
    print(json.dumps({"archived_count": 0, "archived_entries": []}))
    sys.exit(0)

content = readme_path.read_text(encoding="utf-8")
pattern = re.compile(r"(^#### \*\*B-[^\n]+\n(?:.*?))(?:^#### \*\*B-|^## |\Z)", re.MULTILINE | re.DOTALL)
threshold_date = datetime.now().date() - timedelta(days=threshold_days)

archived_blocks: list[str] = []
archived_entries: list[dict[str, Any]] = []
new_parts: list[str] = []
last_end = 0

for match in pattern.finditer(content):
    new_parts.append(content[last_end:match.start()])
    block = match.group(1)
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", block)
    should_archive = False
    block_date = None
    if date_match:
        try:
            block_date = datetime.strptime(date_match.group(1), "%Y-%m-%d").date()
            should_archive = block_date <= threshold_date
        except ValueError:
            should_archive = False

    if should_archive:
        archived_blocks.append(block.strip("\n") + "\n")
        archived_entries.append({
            "heading": block.splitlines()[0].strip(),
            "date": block_date.isoformat() if block_date else None,
        })
    else:
        new_parts.append(block)
    last_end = match.end()

new_parts.append(content[last_end:])

if archived_blocks:
    new_content = "".join(new_parts)
    new_content = re.sub(r"\n{3,}", "\n\n", new_content).strip("\n") + "\n"
    readme_path.write_text(new_content, encoding="utf-8")

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with archive_path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n<!-- Archived on {datetime.now().isoformat()} -->\n\n")
        for block in archived_blocks:
            handle.write(block.rstrip("\n") + "\n\n")

print(json.dumps({
    "archived_count": len(archived_entries),
    "archived_entries": archived_entries,
    "archive_path": str(archive_path),
}))
PY
)

    if [[ $? -ne 0 ]]; then
        log_error "Archiving script failed"
        echo "$archive_output"
        return 1
    fi

    local archived_count
    archived_count=$(echo "$archive_output" | jq '.archived_count' 2>/dev/null || echo "0")

    if [[ "$archived_count" -gt 0 ]]; then
        log_success "Archived $archived_count README context entries"
        echo "$archive_output" | jq -r '.archived_entries[] | "  - \(.heading)"' 2>/dev/null || true
        log_info "Archive file: $(echo "$archive_output" | jq -r '.archive_path')"
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

    local report_file
    report_file="artifacts/weekly_readme_maintenance_$(date +%Y%m%d).md"
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
