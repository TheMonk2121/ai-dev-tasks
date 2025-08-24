#!/bin/bash
# <!-- ANCHOR_KEY: rollback-doc -->
# <!-- ANCHOR_PRIORITY: 25 -->
# <!-- ROLE_PINS: ["coder", "implementer"] -->
# Documentation Recovery & Rollback System (B-063)
#
# Git snapshot system and rollback script for documentation recovery.
# Provides automated snapshots and quick recovery procedures.
#
# Usage:
#     ./scripts/rollback_doc.sh [snapshot|rollback|list|status] [options]
#     ./scripts/rollback_doc.sh snapshot --message "Pre-maintenance backup"
#     ./scripts/rollback_doc.sh rollback --snapshot abc123
#     ./scripts/rollback_doc.sh list
#     ./scripts/rollback_doc.sh status

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SNAPSHOT_PREFIX="doc-snapshot"
SNAPSHOT_DIR=".doc_snapshots"
LOG_FILE="doc_rollback.log"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️${NC} $1" | tee -a "$LOG_FILE"
}

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "Not in a git repository"
        exit 1
    fi
}

# Create snapshot directory if it doesn't exist
ensure_snapshot_dir() {
    if [ ! -d "$SNAPSHOT_DIR" ]; then
        mkdir -p "$SNAPSHOT_DIR"
        log "Created snapshot directory: $SNAPSHOT_DIR"
    fi
}

# Create a documentation snapshot
create_snapshot() {
    local message
    local timestamp
    local snapshot_id
    local snapshot_file
    local doc_files
    local file
    local file_hash
    local file_size

    message="$1"
    timestamp=$(date '+%Y%m%d_%H%M%S')
    snapshot_id="${SNAPSHOT_PREFIX}_${timestamp}"

    log "Creating documentation snapshot: $snapshot_id"

    # Ensure we're in a clean state
    if ! git diff-index --quiet HEAD --; then
        warning "Working directory has uncommitted changes"
        echo "Current changes:"
        git status --porcelain
        echo ""
        read -p "Continue with snapshot? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Snapshot cancelled by user"
            exit 0
        fi
    fi

    # Create snapshot metadata
    snapshot_file="$SNAPSHOT_DIR/${snapshot_id}.json"
    cat > "$snapshot_file" << EOF
{
    "snapshot_id": "$snapshot_id",
    "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
    "message": "$message",
    "git_commit": "$(git rev-parse HEAD)",
    "git_branch": "$(git branch --show-current)",
    "files": [
EOF

    # Get list of documentation files
    doc_files=()
    while IFS= read -r -d '' file; do
        doc_files+=("$file")
    done < <(find . -name "*.md" -type f -print0)

    # Add file information to snapshot
    for file in "${doc_files[@]}"; do
        file_hash=$(git hash-object "$file" 2>/dev/null || echo "untracked")
        file_size=$(stat -f%z "$file" 2>/dev/null || echo "0")
        echo "        {\"path\": \"$file\", \"hash\": \"$file_hash\", \"size\": $file_size}," >> "$snapshot_file"
    done

    # Remove trailing comma and close JSON
    sed -i '' '$ s/,$//' "$snapshot_file"
    echo "    ]" >> "$snapshot_file"
    echo "}" >> "$snapshot_file"

    # Commit snapshot if there are changes
    if git diff-index --quiet HEAD -- "$SNAPSHOT_DIR"; then
        log "No changes to snapshot"
    else
        git add "$SNAPSHOT_DIR"
        git commit -m "📸 $message (snapshot: $snapshot_id)" --no-verify
        success "Snapshot created: $snapshot_id"
    fi

    echo "$snapshot_id"
}

# List available snapshots
list_snapshots() {
    local snapshot_file
    local snapshot_id
    local timestamp
    local message
    local commit

    log "Available documentation snapshots:"
    echo ""

    if [ ! -d "$SNAPSHOT_DIR" ] || [ -z "$(ls -A "$SNAPSHOT_DIR" 2>/dev/null)" ]; then
        echo "No snapshots found"
        return
    fi

    echo "ID | Timestamp | Message | Commit"
    echo "---|-----------|---------|-------"

    for snapshot_file in "$SNAPSHOT_DIR"/*.json; do
        if [ -f "$snapshot_file" ]; then
            snapshot_id=$(basename "$snapshot_file" .json)
            timestamp=$(jq -r '.timestamp' "$snapshot_file" 2>/dev/null || echo "unknown")
            message=$(jq -r '.message' "$snapshot_file" 2>/dev/null || echo "unknown")
            commit=$(jq -r '.git_commit' "$snapshot_file" 2>/dev/null || echo "unknown")

            echo "$snapshot_id | $timestamp | $message | ${commit:0:8}"
        fi
    done
}

# Rollback to a specific snapshot
rollback_snapshot() {
    local snapshot_id
    local snapshot_file
    local commit
    local message
    local timestamp

    snapshot_id="$1"
    snapshot_file="$SNAPSHOT_DIR/${snapshot_id}.json"

    if [ ! -f "$snapshot_file" ]; then
        error "Snapshot not found: $snapshot_id"
        exit 1
    fi

    log "Rolling back to snapshot: $snapshot_id"

    # Get snapshot information
    commit=$(jq -r '.git_commit' "$snapshot_file")
    message=$(jq -r '.message' "$snapshot_file")
    timestamp=$(jq -r '.timestamp' "$snapshot_file")

    echo "Snapshot details:"
    echo "  ID: $snapshot_id"
    echo "  Message: $message"
    echo "  Created: $timestamp"
    echo "  Commit: $commit"
    echo ""

    # Confirm rollback
    read -p "⚠️  This will reset documentation to the snapshot state. Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Rollback cancelled by user"
        exit 0
    fi

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        warning "Working directory has uncommitted changes"
        echo "Current changes:"
        git status --porcelain
        echo ""
        read -p "Stash changes before rollback? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git stash push -m "Auto-stash before rollback to $snapshot_id"
            log "Changes stashed"
        else
            error "Cannot proceed with uncommitted changes"
            exit 1
        fi
    fi

    # Reset to the snapshot commit
    log "Resetting to commit: $commit"
    git reset --hard "$commit"

    success "Rollback completed to snapshot: $snapshot_id"

    # Show current status
    echo ""
    echo "Current documentation status:"
    git status --porcelain
}

# Show current status
show_status() {
    local snapshot_count
    local latest_snapshot
    local latest_id
    local latest_time
    local doc_count
    local recent_changes

    log "Documentation Recovery System Status"
    echo ""

    # Git status
    echo "Git Status:"
    if git diff-index --quiet HEAD --; then
        success "Working directory is clean"
    else
        warning "Working directory has changes:"
        git status --porcelain
    fi
    echo ""

    # Snapshot status
    echo "Snapshot Status:"
    if [ -d "$SNAPSHOT_DIR" ]; then
        snapshot_count=$(find "$SNAPSHOT_DIR" -name "*.json" | wc -l)
        echo "  Snapshots available: $snapshot_count"

        if [ "$snapshot_count" -gt 0 ]; then
            latest_snapshot=$(find "$SNAPSHOT_DIR" -name "*.json" -type f -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2-)
            if [ -n "$latest_snapshot" ]; then
                latest_id=$(basename "$latest_snapshot" .json)
                latest_time=$(jq -r '.timestamp' "$latest_snapshot" 2>/dev/null || echo "unknown")
                echo "  Latest snapshot: $latest_id ($latest_time)"
            fi
        fi
    else
        echo "  No snapshot directory found"
    fi
    echo ""

    # Documentation files status
    echo "Documentation Files:"
    doc_count=$(find . -name "*.md" -type f | wc -l)
    echo "  Markdown files: $doc_count"

    # Check for recent changes
    recent_changes=$(git log --since="1 day ago" --name-only --pretty=format: | grep "\.md$" | sort -u | wc -l)
    echo "  Recent changes (24h): $recent_changes files"
}

# Show help
show_help() {
    cat << EOF
Documentation Recovery & Rollback System (B-063)

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    snapshot [--message "description"]  Create a new documentation snapshot
    rollback --snapshot <id>           Rollback to a specific snapshot
    list                               List all available snapshots
    status                             Show current system status
    help                               Show this help message

Examples:
    $0 snapshot --message "Pre-maintenance backup"
    $0 rollback --snapshot doc-snapshot_20231201_143022
    $0 list
    $0 status

Options:
    --message "text"                   Custom message for snapshot
    --snapshot <id>                    Snapshot ID for rollback
    --force                            Skip confirmation prompts

EOF
}

# Main function
main() {
    local message
    local snapshot_id

    # Ensure we're in a git repository
    check_git_repo

    # Ensure snapshot directory exists
    ensure_snapshot_dir

    # Parse command line arguments
    case "${1:-help}" in
        "snapshot")
            message="Documentation snapshot"
            shift

            # Parse options
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --message)
                        message="$2"
                        shift 2
                        ;;
                    *)
                        error "Unknown option: $1"
                        exit 1
                        ;;
                esac
            done

            create_snapshot "$message"
            ;;

        "rollback")
            snapshot_id=""
            shift

            # Parse options
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --snapshot)
                        snapshot_id="$2"
                        shift 2
                        ;;
                    *)
                        error "Unknown option: $1"
                        exit 1
                        ;;
                esac
            done

            if [ -z "$snapshot_id" ]; then
                error "Snapshot ID required. Use --snapshot <id>"
                exit 1
            fi

            rollback_snapshot "$snapshot_id"
            ;;

        "list")
            list_snapshots
            ;;

        "status")
            show_status
            ;;

        "help"|"-h"|"--help")
            show_help
            ;;

        *)
            error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
