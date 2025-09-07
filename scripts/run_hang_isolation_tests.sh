#!/usr/bin/env bash
set -euo pipefail

# Hang isolation tests to identify the root cause
# Based on the analysis in the user's message

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR%/scripts}"

echo "🔍 Running hang isolation tests..."
echo "=================================="

# Test A: Bypass Bedrock and embeddings
echo ""
echo "🧪 Test A: Bypass Bedrock and embeddings (should complete if hang is Bedrock/embeddings)"
echo "Command: export RAGCHECKER_BYPASS_CLI=1 && export RAGCHECKER_DISABLE_EMBEDDINGS=1 && python3 scripts/ragchecker_official_evaluation.py --use-local-llm --stable"

export RAGCHECKER_BYPASS_CLI=1
export RAGCHECKER_DISABLE_EMBEDDINGS=1

if timeout 300 python3 "${REPO_ROOT}/scripts/ragchecker_official_evaluation.py" --use-local-llm --stable; then
    echo "✅ Test A PASSED - No hang with local LLM"
    TEST_A_RESULT="PASS"
else
    echo "❌ Test A FAILED - Still hanging with local LLM"
    TEST_A_RESULT="FAIL"
fi

echo ""
echo "🧪 Test B: Use Bedrock but keep everything else the same"
echo "Command: export RAGCHECKER_BYPASS_CLI=1 && export RAGCHECKER_DISABLE_EMBEDDINGS=1 && export BEDROCK_MAX_IN_FLIGHT=1 && export BEDROCK_MAX_RPS=0.12 && python3 scripts/ragchecker_official_evaluation.py --use-bedrock --stable"

export RAGCHECKER_BYPASS_CLI=1
export RAGCHECKER_DISABLE_EMBEDDINGS=1
export BEDROCK_MAX_IN_FLIGHT=1
export BEDROCK_MAX_RPS=0.12

if timeout 300 python3 "${REPO_ROOT}/scripts/ragchecker_official_evaluation.py" --use-bedrock --stable; then
    echo "✅ Test B PASSED - No hang with Bedrock"
    TEST_B_RESULT="PASS"
else
    echo "❌ Test B FAILED - Hanging with Bedrock"
    TEST_B_RESULT="FAIL"
fi

echo ""
echo "🧪 Test C: Disable semantic features completely"
echo "Command: export RAGCHECKER_SEMANTIC_FEATURES=0 && python3 scripts/ragchecker_official_evaluation.py --use-bedrock --stable"

export RAGCHECKER_SEMANTIC_FEATURES=0

if timeout 300 python3 "${REPO_ROOT}/scripts/ragchecker_official_evaluation.py" --use-bedrock --stable; then
    echo "✅ Test C PASSED - No hang with semantic features disabled"
    TEST_C_RESULT="PASS"
else
    echo "❌ Test C FAILED - Still hanging with semantic features disabled"
    TEST_C_RESULT="FAIL"
fi

echo ""
echo "📊 Test Results Summary:"
echo "========================"
echo "Test A (Local LLM): $TEST_A_RESULT"
echo "Test B (Bedrock): $TEST_B_RESULT"
echo "Test C (No Semantic): $TEST_C_RESULT"

echo ""
echo "🔍 Analysis:"
if [[ "$TEST_A_RESULT" == "PASS" && "$TEST_B_RESULT" == "FAIL" ]]; then
    echo "🎯 ROOT CAUSE: Bedrock calls are hanging"
    echo "💡 Solution: Use the conservative Bedrock settings or --bypass-cli"
elif [[ "$TEST_A_RESULT" == "FAIL" && "$TEST_C_RESULT" == "PASS" ]]; then
    echo "🎯 ROOT CAUSE: Semantic features (SentenceTransformer) are hanging"
    echo "💡 Solution: Set RAGCHECKER_SEMANTIC_FEATURES=0"
elif [[ "$TEST_A_RESULT" == "FAIL" && "$TEST_B_RESULT" == "FAIL" && "$TEST_C_RESULT" == "FAIL" ]]; then
    echo "🎯 ROOT CAUSE: Multiple issues or deeper problem"
    echo "💡 Solution: Check dependencies, network, or other system issues"
else
    echo "🎯 ROOT CAUSE: Unclear - may be intermittent or environment-specific"
    echo "💡 Solution: Use conservative settings and monitor logs"
fi

echo ""
echo "🚀 Recommended next steps:"
echo "1. Use conservative Bedrock settings: source configs/bedrock_conservative.env"
echo "2. Run with --bypass-cli to avoid CLI hangs"
echo "3. Monitor progress logs for detailed debugging"
