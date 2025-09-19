#!/bin/bash
# Quick script to load persistent configuration for current session
# Use this if you need to load config without restarting terminal

echo "🔧 Loading AI Dev Tasks persistent configuration..."

# Source the environment file
if [ -f "$HOME/.env.ai-dev-tasks" ]; then
    # shellcheck source=/dev/null
    source "$HOME/.env.ai-dev-tasks"
    echo "✅ Configuration loaded successfully"
    echo "   📊 Database: ${POSTGRES_DSN:0:30}..."
    echo "   🔧 Evaluation: $EVAL_DRIVER"
    echo "   🐍 UV Environment: $UV_PROJECT_ENVIRONMENT"
else
    echo "❌ Configuration file not found: $HOME/.env.ai-dev-tasks"
    echo "   Run: ./scripts/shell/setup/setup_shell_integration.sh"
    exit 1
fi
