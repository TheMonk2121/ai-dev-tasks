#!/usr/bin/env bash

set -eo pipefail

# Resolve paths relative to this script so it works from any CWD
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Test script to verify multi-key Bedrock setup
echo "🔑 Testing Multi-Key Bedrock Configuration"
echo "=========================================="

# Activate virtual environment (prefer .venv, then venv) under repo root
VENV_DIR="${VENV_DIR:-$REPO_ROOT/.venv}"
if [ -f "$VENV_DIR/bin/activate" ]; then
  # shellcheck disable=SC1091
  . "$VENV_DIR/bin/activate"
elif [ -f "$REPO_ROOT/venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  . "$REPO_ROOT/venv/bin/activate"
else
  echo "⚠️  No virtualenv found at .venv/ or venv/. Continuing without activation." >&2
fi

# Load multi-key configuration from env file if available
MULTI_ENV="$REPO_ROOT/config/multi_key_bedrock.env"
if [ -f "$MULTI_ENV" ]; then
  echo "🔧 Loading multi-key configuration from $MULTI_ENV"
  # shellcheck source=config/multi_key_bedrock.env
  # shellcheck disable=SC1091
  . "$MULTI_ENV"
else
  echo "⚠️  $MULTI_ENV not found. Proceeding with existing environment variables." >&2
fi

# Derive multi-key config from primary creds if only primary is set
if [ -n "${AWS_ACCESS_KEY_ID:-}" ] && [ -n "${AWS_SECRET_ACCESS_KEY:-}" ]; then
  if [ -z "${AWS_ACCESS_KEY_ID_1:-}" ] && [ -z "${AWS_ACCESS_KEY_ID_2:-}" ] && [ -z "${AWS_ACCESS_KEY_ID_3:-}" ]; then
    echo "🔁 Deriving multi-key configuration from primary AWS credentials"
    export AWS_ACCESS_KEY_ID_1="${AWS_ACCESS_KEY_ID}"
    export AWS_SECRET_ACCESS_KEY_1="${AWS_SECRET_ACCESS_KEY}"
    export AWS_REGION_1="${AWS_REGION:-us-west-2}"

    export AWS_ACCESS_KEY_ID_2="${AWS_ACCESS_KEY_ID}"
    export AWS_SECRET_ACCESS_KEY_2="${AWS_SECRET_ACCESS_KEY}"
    export AWS_REGION_2="${AWS_REGION:-eu-west-1}"

    # Keep primary as key_0 (unsuffixed); also provide a suffixed 3 for convenience
    export AWS_ACCESS_KEY_ID_3="${AWS_ACCESS_KEY_ID}"
    export AWS_SECRET_ACCESS_KEY_3="${AWS_SECRET_ACCESS_KEY}"
    export AWS_REGION_3="${AWS_REGION:-ap-southeast-2}"
  fi
fi

# Ensure we have at least single-key credentials for the client to initialize
if [ -z "${AWS_ACCESS_KEY_ID:-}" ] || [ -z "${AWS_SECRET_ACCESS_KEY:-}" ]; then
  echo "❌ No primary AWS credentials found (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY)." >&2
  echo "   Set them in your environment or via $MULTI_ENV, then re-run." >&2
  exit 1
fi

# Test configuration
echo "🧪 Testing Enhanced Bedrock Client with 3 keys..."
PYTHONPATH="$REPO_ROOT" python3 - <<'PY'
from scripts.enhanced_bedrock_client import SyncBedrockClientWrapper
import os
import json
import traceback

print('🔍 Environment check:')
print(f"Primary: {os.getenv('AWS_REGION', 'Not set')}")
print(f"Key 1: {os.getenv('AWS_REGION_1', 'Not set')}")
print(f"Key 2: {os.getenv('AWS_REGION_2', 'Not set')}")
print(f"Key 3: {os.getenv('AWS_REGION_3', 'Not set')}")
print()

try:
    client = SyncBedrockClientWrapper()
    status = client.get_status()
    print(f"✅ Successfully loaded {status['total_keys']} API keys")
    print('📊 Key details:')
    print(f"Total keys loaded: {status['total_keys']}")
    # Show a compact view of load balancer keys
    lb = status.get('load_balancer', {})
    print(f"Load balancer keys: {list(lb.keys())}")
    print()
    print('🎯 Multi-key setup is ready for RAGChecker!')
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()
PY
