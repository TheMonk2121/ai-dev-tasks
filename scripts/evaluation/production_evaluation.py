from typing import Any, Optional, Union
#!/usr/bin/env python3
"""
Production Evaluation - Clean & Reproducible
Runs two passes: retrieval-only baseline and deterministic few-shot
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# Add project paths - use absolute paths and check for duplicates
project_root = Path(__file__).parent.parent.resolve()
dspy_rag_path = project_root / "dspy-rag-system"

# Add paths only if not already present
paths_to_add = [project_root, dspy_rag_path]
for path in paths_to_add:
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

# Import settings to validate configuration
from src.config import get_settings

# Validate configuration on import
try:
    settings = get_settings()
    print(f"✅ Configuration loaded successfully for environment: {settings.env}")
except Exception as e:
    print(f"❌ Configuration validation failed: {e}")
    sys.exit(1)

def run_evaluation_pass(pass_name: str, config: dict[str, Any], output_file: str) -> dict[str, Any]:
    """Run a single evaluation pass with specific configuration."""
    print(f"\n🔄 Running {pass_name}")
    print("=" * 60)

    # Set environment variables for this pass
    for key, value in config.items():
        os.environ[key] = str(value)
        print(f"   {key}={value}")

    # Import and run evaluation
    try:
        from scripts.ragchecker_official_evaluation import main as run_eval

        # Capture the evaluation results
        start_time = time.time()

        # Run the evaluation with required arguments
        import subprocess
        # Create output directory for this pass
        pass_output_dir = Path("metrics/production_evaluations") / f"pass_{pass_name.lower().replace(' ', '_')}"
        pass_output_dir.mkdir(parents=True, exist_ok=True)

        # Use existing test cases
        test_cases_file = "300_evals/legacy/test_cases.json"

        result = subprocess.run(
            [
                sys.executable,
                "scripts/ragchecker_official_evaluation.py",
                "--cases",
                test_cases_file,
                "--outdir",
                str(pass_output_dir),
                "--use-bedrock",
                "--bypass-cli",
            ],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        eval_time = time.time() - start_time

        # Parse results from the output
        results = {
            "pass_name": pass_name,
            "config": config,
            "eval_time_seconds": eval_time,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Save results
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        if result.returncode == 0:
            print(f"✅ {pass_name} completed successfully")
        else:
            print(f"❌ {pass_name} failed with return code {result.returncode}")
            print(f"STDERR: {result.stderr}")

        return results

    except Exception as e:
        error_result = {
            "pass_name": pass_name,
            "config": config,
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        with open(output_file, "w") as f:
            json.dump(error_result, f, indent=2)

        print(f"❌ {pass_name} failed with exception: {e}")
        return error_result

def analyze_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze evaluation results and check pass criteria."""
    print("\n📊 Analysis Results")
    print("=" * 60)

    analysis = {
        "total_passes": len(results),
        "successful_passes": sum(1 for r in results if r.get("return_code") == 0),
        "failed_passes": sum(1 for r in results if r.get("return_code") != 0),
        "pass_criteria": {
            "oracle_retrieval_hit_prefilter": "≥ +5-15 pts vs baseline",
            "reader_used_gold": "≥ baseline",
            "f1_score": "≥ baseline",
            "precision_drift": "≤ 2 pts",
            "p95_latency": "≤ +15%",
        },
        "recommendations": [],
    }

    # Check each pass
    for result in results:
        if result.get("return_code") == 0:
            print(f"✅ {result['pass_name']}: SUCCESS")
        else:
            print(f"❌ {result['pass_name']}: FAILED")
            analysis["recommendations"].append(f"Fix {result['pass_name']} before proceeding")

    # Overall assessment
    if analysis["successful_passes"] == analysis["total_passes"]:
        print("🎉 ALL PASSES SUCCESSFUL - Ready for production!")
        analysis["status"] = "READY_FOR_PRODUCTION"
    elif analysis["successful_passes"] > 0:
        print("⚠️  PARTIAL SUCCESS - Review failed passes")
        analysis["status"] = "PARTIAL_SUCCESS"
    else:
        print("❌ ALL PASSES FAILED - Fix issues before proceeding")
        analysis["status"] = "ALL_FAILED"

    return analysis

def main():
    """Run production evaluation with two passes."""
    print("🚀 PRODUCTION EVALUATION - Clean & Reproducible")
    print("=" * 80)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Create results directory
    results_dir = Path("metrics/production_evaluations")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Define evaluation passes
    passes = [
        {
            "name": "Retrieval-Only Baseline",
            "config": {
                "FEW_SHOT_K": "0",
                "EVAL_COT": "0",
                "TEMPERATURE": "0",
                "EVAL_DISABLE_CACHE": "1",
                "DSPY_TELEPROMPT_CACHE": "false",
            },
            "description": "Confirms retrieval, rerank, and chunk config (450/10%/J=0.8/prefix-A)",
        },
        {
            "name": "Deterministic Few-Shot",
            "config": {
                "FEW_SHOT_K": "5",
                "FEW_SHOT_SELECTOR": "knn",
                "FEW_SHOT_SEED": "42",
                "EVAL_COT": "0",
                "EVAL_DISABLE_CACHE": "1",
                "DSPY_TELEPROMPT_CACHE": "false",
            },
            "description": "Records prompt_audit.few_shot_ids, prompt_hash, cot_enabled=false",
        },
    ]

    results = []

    # Run each pass
    for i, pass_config in enumerate(passes, 1):
        output_file = results_dir / f"pass_{i}_{pass_config['name'].lower().replace(' ', '_')}.json"

        print(f"\n📋 PASS {i}: {pass_config['name']}")
        print(f"   {pass_config['description']}")

        result = run_evaluation_pass(pass_config["name"], pass_config["config"], str(output_file))
        results.append(result)

    # Analyze results
    analysis = analyze_results(results)

    # Save analysis
    analysis_file = results_dir / f"analysis_{int(time.time())}.json"
    with open(analysis_file, "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"\n📁 Results saved to: {results_dir}")
    print(f"📊 Analysis saved to: {analysis_file}")

    # Exit with appropriate code
    if analysis["status"] == "READY_FOR_PRODUCTION":
        print("\n🎯 NEXT STEPS:")
        print("   1. Review evaluation results")
        print("   2. Proceed with canary rollout")
        print("   3. Monitor production metrics")
        sys.exit(0)
    else:
        print("\n🔧 NEXT STEPS:")
        print("   1. Fix failed evaluation passes")
        print("   2. Re-run production evaluation")
        print("   3. Address any issues before production")
        sys.exit(1)

if __name__ == "__main__":
    main()
