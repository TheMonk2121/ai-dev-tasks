from __future__ import annotations
import json
import os
import subprocess
from pathlib import Path
#!/usr/bin/env python3
"""
Test script for enhanced RAGChecker with RRF, MMR, and claim binding.
"""

def run_test_configuration(config_name: str, env_vars: dict, description: str):
    """Run a test configuration and return results."""
    print(f"\n🧪 Testing Configuration: {config_name}")
    print(f"📋 Description: {description}")
    print("=" * 60)

    # Set environment variables
    env = os.environ.copy()
    env.update(env_vars)

    # Convert all values to strings
    for key, value in \1.items()
        env[key] = str(value)

    # Run the evaluation
    cmd = ["python3", "scripts/ragchecker_official_evaluation.py", "--use-bedrock", "--bypass-cli"]

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=1800)  # 30 minute timeout

        if result.returncode == 0:
            print(f"✅ {config_name} completed successfully")
            # Extract metrics from output
            lines = result.stdout.split("\n")
            case_results = []
            for line in lines:
                if "✅ Case" in line and "P=" in line:
                    case_results.append(line.strip())

            return {
                "config": config_name,
                "status": "success",
                "case_results": case_results,
                "stdout": result.stdout[-2000:],  # Last 2000 chars
                "stderr": result.stderr[-1000:] if result.stderr else "",
            }
        else:
            print(f"❌ {config_name} failed with exit code {result.returncode}")
            return {
                "config": config_name,
                "status": "failed",
                "returncode": result.returncode,
                "stdout": result.stdout[-2000:],
                "stderr": result.stderr[-1000:] if result.stderr else "",
            }
    except subprocess.TimeoutExpired:
        print(f"⏰ {config_name} timed out")
        return {"config": config_name, "status": "timeout"}
    except Exception as e:
        print(f"💥 {config_name} crashed: {e}")
        return {"config": config_name, "status": "crashed", "error": str(e)}

def main():
    """Run comprehensive test suite."""

    # Base configuration (our proven baseline)
    base_config = {
        "AWS_REGION": "us-east-1",
        "RAGCHECKER_JSON_PROMPTS": "1",
        "RAGCHECKER_FAST_MODE": "1",  # Use fast mode for testing
        "BEDROCK_MAX_RPS": "0.5",
        "BEDROCK_MAX_IN_FLIGHT": "2",
        "BEDROCK_MAX_RETRIES": "3",
        "BEDROCK_RETRY_BASE": "1.5",
        "BEDROCK_RETRY_MAX_SLEEP": "8",
        "BEDROCK_COOLDOWN_SEC": "4",
        "TOKENIZERS_PARALLELISM": "false",
        "RAGCHECKER_CONTEXT_TOPK": "16",
        "RAGCHECKER_COVERAGE_REWRITE": "1",
        "RAGCHECKER_TARGET_WORDS": "1000",
        "RAGCHECKER_EVIDENCE_GUARD": "1",
        "RAGCHECKER_EVIDENCE_KEEP_MODE": "target_k",
        "RAGCHECKER_EVIDENCE_MIN_SENT": "2",
        "RAGCHECKER_EVIDENCE_MAX_SENT": "9",
        "RAGCHECKER_TARGET_K_WEAK": "3",
        "RAGCHECKER_TARGET_K_BASE": "5",
        "RAGCHECKER_TARGET_K_STRONG": "7",
        "RAGCHECKER_SIGNAL_DELTA_WEAK": "0.10",
        "RAGCHECKER_SIGNAL_DELTA_STRONG": "0.22",
        "RAGCHECKER_WEIGHT_JACCARD": "0.20",
        "RAGCHECKER_WEIGHT_ROUGE": "0.30",
        "RAGCHECKER_WEIGHT_COSINE": "0.50",
        "RAGCHECKER_EVIDENCE_JACCARD": "0.05",
        "RAGCHECKER_EVIDENCE_COVERAGE": "0.18",
        "RAGCHECKER_EVIDENCE_MIN_FACT_COVERAGE": "0.30",
        "RAGCHECKER_REDUNDANCY_TRIGRAM_MAX": "0.50",
        "RAGCHECKER_PER_CHUNK_CAP": "2",
        "RAGCHECKER_PER_CHUNK_CAP_SMALL": "3",
        "RAGCHECKER_PER_CASE_SLEEP": "0.3",
    }

    # Test configurations
    test_configs = [
        {
            "name": "baseline_locked",
            "env": base_config,
            "description": "Locked baseline configuration (proven to work)",
        },
        {
            "name": "claim_binding_enabled",
            "env": {
                **base_config,
                **{"RAGCHECKER_CLAIM_BINDING": "1", "RAGCHECKER_CLAIM_TOPK": "2", "RAGCHECKER_DROP_UNSUPPORTED": "1"},
            },
            "description": "Baseline + per-claim evidence binding",
        },
        {
            "name": "enhanced_retrieval",
            "env": {
                **base_config,
                **{
                    "RAGCHECKER_REWRITE_K": "6",
                    "RAGCHECKER_RETRIEVAL_HYBRID": "1",
                    "RAGCHECKER_USE_RRF": "1",
                    "RAGCHECKER_USE_MMR": "1",
                    "RAGCHECKER_MMR_LAMBDA": "0.7",
                },
            },
            "description": "Baseline + multi-query expansion + RRF + MMR",
        },
        {
            "name": "full_enhanced",
            "env": {
                **base_config,
                **{
                    "RAGCHECKER_CLAIM_BINDING": "1",
                    "RAGCHECKER_CLAIM_TOPK": "2",
                    "RAGCHECKER_DROP_UNSUPPORTED": "1",
                    "RAGCHECKER_REWRITE_K": "6",
                    "RAGCHECKER_RETRIEVAL_HYBRID": "1",
                    "RAGCHECKER_USE_RRF": "1",
                    "RAGCHECKER_USE_MMR": "1",
                    "RAGCHECKER_MMR_LAMBDA": "0.7",
                    "RAGCHECKER_UNIQUE_ANCHOR_MIN": "1",
                    "RAGCHECKER_ANCHOR_NGRAM": "3",
                },
            },
            "description": "All enhancements: claim binding + RRF + MMR + precision-guard 2.0",
        },
    ]

    # Run tests
    results = []
    for config in test_configs:
        result = run_test_configuration(result.get("key", "")
        results.append(result)

    # Save results
    results_file = Path("metrics/baseline_evaluations/enhanced_test_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    for result in results:
        status_emoji = {"success": "✅", "failed": "❌", "timeout": "⏰", "crashed": "💥"}.get(result.get("key", "")

        print(f"{status_emoji} {result.get("key", "")

        if result.get("key", "")
            # Extract some key metrics
            case_results = result.get("key", "")
            if case_results:
                print(f"   📈 Completed {len(case_results)} test cases")
                # Show a few sample results
                for case_result in case_results[:3]:
                    print(f"   📝 {case_result}")
                if len(case_results) > 3:
                    print(f"   ... and {len(case_results) - 3} more")

    print(f"\n📁 Detailed results saved to: {results_file}")
    print("\n🎯 Next steps:")
    print("   1. Review successful configurations")
    print("   2. Compare metrics against locked baseline")
    print("   3. Promote best performer with two-run rule")

if __name__ == "__main__":
    main()