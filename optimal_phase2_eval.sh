#!/usr/bin/env bash
# Optimal Phase-2 Configuration for Official RAGChecker Evaluator
# Only sets variables actually consumed by scripts/ragchecker_official_evaluation.py

echo "🎯 Loading Optimal Phase-2 Configuration"
echo "=========================================="

# Bedrock Rate Limiting (Anti-Throttling) - Actually consumed by evaluator
export USE_BEDROCK_QUEUE=1                     # Line 88: use_queue = os.getenv("USE_BEDROCK_QUEUE", "1")
export BEDROCK_MAX_RPS=0.15                    # Line 317: max_rps = float(os.getenv("BEDROCK_MAX_RPS", "0.25"))
export BEDROCK_MAX_IN_FLIGHT=1                 # Line 318: max_in_flight = int(os.getenv("BEDROCK_MAX_IN_FLIGHT", "1"))
export BEDROCK_COOLDOWN_SEC=12                 # Line 373: cd = float(os.getenv("BEDROCK_COOLDOWN_SEC", "8"))
export BEDROCK_RETRY_BASE=1.8                  # Line 310: self._bedrock_retry_base = float(os.getenv("BEDROCK_RETRY_BASE", "1.6"))
export BEDROCK_RETRY_MAX_SLEEP=20              # Line 311: self._bedrock_retry_max_sleep = float(os.getenv("BEDROCK_RETRY_MAX_SLEEP", "12"))

# Evidence Selection Gates - Actually consumed by evaluator
export RAGCHECKER_EVIDENCE_JACCARD=0.07        # Line 721: j_min = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.08"))
export RAGCHECKER_EVIDENCE_COVERAGE=0.20       # Line 2209: coverage_min = float(os.getenv("RAGCHECKER_EVIDENCE_COVERAGE", "0.16"))

# Additional Evidence Settings (if consumed by current evaluator path)
export RAGCHECKER_EVIDENCE_MIN_SENT=2          # Conservative minimum
export RAGCHECKER_EVIDENCE_MAX_SENT=11         # Conservative maximum
export RAGCHECKER_TARGET_K_WEAK=3              # Conservative target-K settings
export RAGCHECKER_TARGET_K_BASE=5
export RAGCHECKER_TARGET_K_STRONG=9

# JSON Prompts (if consumed)
export RAGCHECKER_JSON_PROMPTS=1               # Line 350: if os.getenv("RAGCHECKER_JSON_PROMPTS", "1") == "1"

echo "✅ Phase-2 Configuration Loaded"
echo "🎯 Target: Stable evaluation without throttling"
echo "📊 Settings: Conservative Bedrock caps + proven evidence thresholds"
echo "🚀 Ready for: python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli"
