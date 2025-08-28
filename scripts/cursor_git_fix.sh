#!/usr/bin/env bash
# Cursor Git Integration Fix Script
# Bypasses Cursor's built-in conflict detection that interferes with pre-commit hooks

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

# Function to commit with Cursor Git integration bypass
cursor_commit() {
    local commit_message="$1"

    log_info "Using Cursor Git integration bypass..."
    log_info "This will avoid the 'Quick conflict check' messages"

    # Temporarily unset Cursor's Git environment variables
    local original_git_askpass="$GIT_ASKPASS"
    local original_vscode_git_askpass="$VSCODE_GIT_ASKPASS_NODE"
    local original_vscode_git_ipc="$VSCODE_GIT_IPC_HANDLE"

    # Unset the variables
    unset GIT_ASKPASS
    unset VSCODE_GIT_ASKPASS_NODE
    unset VSCODE_GIT_IPC_HANDLE

    # Run git commit
    if git commit -m "$commit_message"; then
        log_success "Commit successful!"
        log_info "Pre-commit hooks ran without Cursor interference"
    else
        log_error "Commit failed"
        return 1
    fi

    # Restore environment variables
    export GIT_ASKPASS="$original_git_askpass"
    export VSCODE_GIT_ASKPASS_NODE="$original_vscode_git_askpass"
    export VSCODE_GIT_IPC_HANDLE="$original_vscode_git_ipc"
}

# Function to show current Cursor Git integration status
show_status() {
    log_info "Cursor Git Integration Status:"
    echo "  GIT_ASKPASS: ${GIT_ASKPASS:-'Not set'}"
    echo "  VSCODE_GIT_ASKPASS_NODE: ${VSCODE_GIT_ASKPASS_NODE:-'Not set'}"
    echo "  VSCODE_GIT_IPC_HANDLE: ${VSCODE_GIT_IPC_HANDLE:-'Not set'}"

    if [[ -n "${GIT_ASKPASS:-}" ]]; then
        log_warning "Cursor Git integration is active"
        log_info "This may cause 'Quick conflict check' messages"
    else
        log_success "Cursor Git integration is not active"
    fi
}

# Function to disable Cursor Git integration temporarily
disable_cursor_git() {
    log_info "Temporarily disabling Cursor Git integration..."

    # Save current environment
    export CURSOR_GIT_ASKPASS_BACKUP="$GIT_ASKPASS"
    export CURSOR_VSCODE_GIT_ASKPASS_BACKUP="$VSCODE_GIT_ASKPASS_NODE"
    export CURSOR_VSCODE_GIT_IPC_BACKUP="$VSCODE_GIT_IPC_HANDLE"

    # Unset variables
    unset GIT_ASKPASS
    unset VSCODE_GIT_ASKPASS_NODE
    unset VSCODE_GIT_IPC_HANDLE

    log_success "Cursor Git integration disabled"
    log_info "Run 'source scripts/cursor_git_fix.sh && restore_cursor_git' to restore"
}

# Function to restore Cursor Git integration
restore_cursor_git() {
    log_info "Restoring Cursor Git integration..."

    # Restore environment variables
    export GIT_ASKPASS="$CURSOR_GIT_ASKPASS_BACKUP"
    export VSCODE_GIT_ASKPASS_NODE="$CURSOR_VSCODE_GIT_ASKPASS_BACKUP"
    export VSCODE_GIT_IPC_HANDLE="$CURSOR_VSCODE_GIT_IPC_BACKUP"

    # Clean up backup variables
    unset CURSOR_GIT_ASKPASS_BACKUP
    unset CURSOR_VSCODE_GIT_ASKPASS_BACKUP
    unset CURSOR_VSCODE_GIT_IPC_BACKUP

    log_success "Cursor Git integration restored"
}

# Main execution
main() {
    case "${1:-}" in
        "commit")
            if [[ -z "${2:-}" ]]; then
                log_error "Usage: $0 commit \"commit message\""
                exit 1
            fi
            cursor_commit "$2"
            ;;
        "status")
            show_status
            ;;
        "disable")
            disable_cursor_git
            ;;
        "restore")
            restore_cursor_git
            ;;
        *)
            echo "Cursor Git Integration Fix Script"
            echo ""
            echo "Usage:"
            echo "  $0 commit \"message\"    - Commit with Cursor Git bypass"
            echo "  $0 status               - Show current Cursor Git integration status"
            echo "  $0 disable              - Temporarily disable Cursor Git integration"
            echo "  $0 restore              - Restore Cursor Git integration"
            echo ""
            echo "Examples:"
            echo "  $0 commit \"fix: resolve pre-commit hook issue\""
            echo "  $0 status"
            echo "  $0 disable"
            ;;
    esac
}

main "$@"
