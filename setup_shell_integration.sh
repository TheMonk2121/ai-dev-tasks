#!/usr/bin/env bash
# Setup script for AI Dev Tasks shell integration (idempotent)

set -euo pipefail

echo "🔧 Setting up AI Dev Tasks shell integration"
echo "============================================="

# Resolve paths
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE_SOURCE="$PROJECT_DIR/env.ai-dev-tasks"
ENV_FILE_TARGET="$HOME/.env.ai-dev-tasks"

echo "📁 Project directory: $PROJECT_DIR"
echo "📄 Environment file (source): $ENV_FILE_SOURCE"
echo "🏠 Environment file (target): $ENV_FILE_TARGET"

# Check if environment file exists in repo
if [ ! -f "$ENV_FILE_SOURCE" ]; then
    echo "❌ Environment file not found: $ENV_FILE_SOURCE"
    exit 1
fi

echo "✅ Environment file found in repo"

# Copy env file to home if missing or changed
copy_env() {
    if [ ! -f "$ENV_FILE_TARGET" ]; then
        cp "$ENV_FILE_SOURCE" "$ENV_FILE_TARGET"
        echo "📦 Copied env file to $ENV_FILE_TARGET"
    elif ! cmp -s "$ENV_FILE_SOURCE" "$ENV_FILE_TARGET"; then
        cp "$ENV_FILE_TARGET" "${ENV_FILE_TARGET}.bak.$(date +%Y%m%d%H%M%S)"
        cp "$ENV_FILE_SOURCE" "$ENV_FILE_TARGET"
        echo "♻️  Updated env file and created backup"
    else
        echo "ℹ️  Env file already up-to-date"
    fi
}

# Ensure a line exists in a shell rc file (create file if missing)
ensure_source_line() {
    local rc_file="$1"
    local line='[ -f ~/.env.ai-dev-tasks ] && source ~/.env.ai-dev-tasks'
    if [ ! -f "$rc_file" ]; then
        printf "\n%s\n" "$line" > "$rc_file"
        echo "➕ Added source line to new $rc_file"
        return
    fi
    if ! grep -Fq "$line" "$rc_file"; then
        cp "$rc_file" "${rc_file}.bak.$(date +%Y%m%d%H%M%S)"
        printf "\n%s\n" "$line" >> "$rc_file"
        echo "➕ Appended source line to $rc_file (backup created)"
    else
        echo "ℹ️  Source line already present in $rc_file"
    fi
}

# Suppress macOS bash deprecation banner if using /bin/bash
ensure_bash_silence() {
    local rc_file="$1"
    local line='export BASH_SILENCE_DEPRECATION_WARNING=1'
    if [ -f "$rc_file" ] && ! grep -Fq "$line" "$rc_file"; then
        cp "$rc_file" "${rc_file}.bak.$(date +%Y%m%d%H%M%S)"
        printf "\n%s\n" "$line" >> "$rc_file"
        echo "🙈 Added BASH_SILENCE_DEPRECATION_WARNING to $rc_file"
    fi
}

copy_env

# Update zsh and bash rc files
ensure_source_line "$HOME/.zshrc"
ensure_source_line "$HOME/.zprofile"
ensure_source_line "$HOME/.bashrc"
ensure_source_line "$HOME/.bash_profile"

# Quiet the zsh message in bash sessions (optional but harmless)
ensure_bash_silence "$HOME/.bashrc"
ensure_bash_silence "$HOME/.bash_profile"

# Add bash completion for Homebrew bash
ensure_bash_completion() {
    local rc_file="$1"
    local line='[[ -r "/opt/homebrew/etc/profile.d/bash_completion.sh" ]] && . "/opt/homebrew/etc/profile.d/bash_completion.sh"'
    if [ -f "$rc_file" ] && ! grep -Fq "$line" "$rc_file"; then
        cp "$rc_file" "${rc_file}.bak.$(date +%Y%m%d%H%M%S)"
        printf "\n%s\n" "$line" >> "$rc_file"
        echo "🔧 Added bash completion to $rc_file"
    fi
}

ensure_bash_completion "$HOME/.bashrc"
ensure_bash_completion "$HOME/.bash_profile"

echo ""
echo "🧪 Verification: open a NEW integrated terminal and run:"
echo "  echo \$BEDROCK_MAX_RPS \$ASYNC_MAX_CONCURRENCY \$RAGCHECKER_COVERAGE_REWRITE \$RAGCHECKER_JSON_PROMPTS"
echo "  echo \"SHELL=\$SHELL\"; ps -o pid=,ppid=,comm= -p \$\$"
echo "  echo \"TERM_PROGRAM=\$TERM_PROGRAM\"; echo \"VSCODE_SHELL_INTEGRATION=\$VSCODE_SHELL_INTEGRATION\"; echo \"FLAGS=\$-\""
echo ""
echo "✅ Done. If variables are empty, set your default profile to 'zsh (login)' or 'bash (login)' in VS Code and open a fresh terminal."
