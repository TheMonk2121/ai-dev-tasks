#!/usr/bin/env bash
# Hermetic RAGChecker Evaluation Runner
# Runs in clean environment to avoid global env conflicts

set -euo pipefail

echo "🔒 Running Hermetic RAGChecker Evaluation"
echo "=========================================="

# Clean environment with minimal PATH
export CLEAN_PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Optional preflight diff in the current shell (helps spot global overrides)
if [[ "${HERMITIC_PREFLIGHT:-1}" == "1" ]]; then
  if [[ -f scripts/preflight_env_diff.sh ]]; then
    printf "\n🔎 Preflight (current shell vs throttle profile)\n"
    bash scripts/preflight_env_diff.sh --profile throttle || true
    echo
  fi
fi

# Run in clean environment with virtual environment
env -i \
    HOME="$HOME" \
    PATH="$CLEAN_PATH" \
    zsh -lc "
        cd /Users/danieljacobs/Code/ai-dev-tasks
        # Activate virtual environment
        if [ -f '.venv/bin/activate' ]; then
            source .venv/bin/activate
            echo '📦 Virtual environment activated'
        elif [ -f 'venv/bin/activate' ]; then
            source venv/bin/activate
            echo '📦 Virtual environment activated'
        else
            echo '⚠️  No virtual environment found, using system Python'
        fi
        # Load throttle-free configuration
        source throttle_free_eval.sh
        if [[ -f scripts/preflight_env_diff.sh && \"${HERMITIC_PREFLIGHT:-1}\" == \"1\" ]]; then
          echo '🔎 Preflight (hermetic shell after sourcing throttle profile)'
          bash scripts/preflight_env_diff.sh --profile throttle || true
          echo
        fi
        echo '🚀 Starting evaluation with clean environment...'
        python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli \"\$@\"
    " "$@"
