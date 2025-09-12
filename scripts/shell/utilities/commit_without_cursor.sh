#!/usr/bin/env bash
# Commit without Cursor Git Integration Interference
# This script bypasses Cursor's built-in conflict detection

set -euo pipefail

# Colors for output
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

if [ $# -eq 0 ]; then
    echo "Usage: $0 \"commit message\""
    echo ""
    echo "This script commits changes while bypassing Cursor's Git integration"
    echo "to avoid the 'Quick conflict check' messages."
    echo ""
    echo "Example:"
    echo "  $0 \"fix: resolve pre-commit hook issue\""
    exit 1
fi

COMMIT_MESSAGE="$1"

log_info "Committing without Cursor Git integration..."
log_info "This will bypass the '🔍 Quick conflict check' messages"

# Use git directly without Cursor's environment
if GIT_ASKPASS="" VSCODE_GIT_ASKPASS_NODE="" VSCODE_GIT_IPC_HANDLE="" git commit -m "$COMMIT_MESSAGE"; then
    log_success "Commit successful!"
    log_info "Pre-commit hooks ran without Cursor interference"
else
    log_warning "Commit failed - this may be due to pre-commit hook failures"
    log_info "Check the output above for specific error messages"
    exit 1
fi
