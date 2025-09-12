#!/usr/bin/env bash

# File Protection Script - Prevents corruption and monitors for issues
# Usage: ./scripts/protect_files.sh [--monitor] [--backup] [--restore]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/.file_backups"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check for file corruption
check_file_corruption() {
    local file="$1"
    local issues=0

    # Check for malformed content patterns
    if grep -q '```text' "$file" 2>/dev/null; then
        log_warning "Found malformed code block in $file"
        ((issues++))
    fi

    if grep -q '####\*\*' "$file" 2>/dev/null; then
        log_warning "Found malformed headers in $file"
        ((issues++))
    fi

    if grep -q '-\*\*' "$file" 2>/dev/null; then
        log_warning "Found malformed list items in $file"
        ((issues++))
    fi

    # Check for excessive content (more than 1000 lines)
    local line_count
    line_count=$(wc -l < "$file" 2>/dev/null || echo "0")
    if [ "$line_count" -gt 1000 ]; then
        log_warning "File $file is very large ($line_count lines) - possible corruption"
        ((issues++))
    fi

    return $issues
}

# Create backup of critical files
create_backup() {
    log_info "Creating backup of critical files..."

    mkdir -p "$BACKUP_DIR"

    local critical_files=(
        "100_cursor-memory-context.md"
        "000_backlog.md"
        "400_system-overview.md"
        "400_project-overview.md"
        "400_context-priority-guide.md"
    )

    for file in "${critical_files[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$BACKUP_DIR/${file}.$(date +%Y%m%d_%H%M%S)"
            log_success "Backed up $file"
        fi
    done
}

# Monitor files for changes
monitor_files() {
    log_info "Starting file monitoring..."

    local critical_files=(
        "100_cursor-memory-context.md"
        "000_backlog.md"
        "400_system-overview.md"
        "400_project-overview.md"
        "400_context-priority-guide.md"
    )

    for file in "${critical_files[@]}"; do
        if [ -f "$file" ]; then
            if check_file_corruption "$file"; then
                log_error "Corruption detected in $file"
                return 1
            fi
        fi
    done

    log_success "All critical files appear healthy"
    return 0
}

# Restore from backup
restore_from_backup() {
    local file="$1"
    local backup_file

    if [ -d "$BACKUP_DIR" ]; then
        # Use find with stat for cross-platform compatibility (avoids SC2012)
        backup_file=$(find "$BACKUP_DIR" -name "${file}.*" -type f -exec stat -f "%m %N" {} \; 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)
        if [ -n "$backup_file" ] && [ -f "$backup_file" ]; then
            log_info "Restoring $file from $backup_file"
            cp "$backup_file" "$file"
            log_success "Restored $file"
            return 0
        fi
    fi

    log_error "No backup found for $file"
    return 1
}

# Check git hooks
check_git_hooks() {
    log_info "Checking git hooks..."

    if [ -f ".git/hooks/pre-commit" ]; then
        if grep -q "dry-run" ".git/hooks/pre-commit"; then
            log_success "Pre-commit hook is safe (dry-run mode)"
        else
            log_warning "Pre-commit hook may modify files"
        fi
    else
        log_warning "No pre-commit hook found"
    fi

    if [ -f ".git/hooks/pre-commit.disabled" ]; then
        log_info "Disabled pre-commit hook found (good)"
    fi
}

# Main function
main() {
    case "${1:-}" in
        --monitor)
            monitor_files
            ;;
        --backup)
            create_backup
            ;;
        --restore)
            if [ -z "${2:-}" ]; then
                log_error "Please specify a file to restore"
                exit 1
            fi
            restore_from_backup "$2"
            ;;
        --check-hooks)
            check_git_hooks
            ;;
        --help|-h)
            echo "File Protection Script"
            echo ""
            echo "Usage: $0 [OPTION]"
            echo ""
            echo "Options:"
            echo "  --monitor     Check for file corruption"
            echo "  --backup      Create backup of critical files"
            echo "  --restore FILE Restore file from backup"
            echo "  --check-hooks Check git hooks for safety"
            echo "  --help        Show this help"
            ;;
        *)
            log_info "Running comprehensive file protection check..."
            check_git_hooks
            monitor_files
            log_info "Run '$0 --backup' to create backups"
            ;;
    esac
}

main "$@"
