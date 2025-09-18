from typing import Any, Optional, Union
#!/usr/bin/env python3
"""
Reranker Comparison Evaluation Script
Compares performance with and without the PyTorch reranker.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

def run_evaluation_with_config(config_name: str, config_file: str, output_dir: str) -> dict[str, Any]:
    """Run evaluation with a specific configuration"""
    print(f"\n🧪 Running evaluation: {config_name}")
    print(f"📁 Config: {config_file}")

    # Create output file
    timestamp = int(time.time())
    output_file = Path(output_dir) / f"{config_name}_{timestamp}.json"

    try:
        # Source the config and run evaluation
        cmd = f"source {config_file} && python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --outdir {output_dir}"

        print(f"🔧 Command: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)

        # Find the actual output file (ragchecker creates timestamped files)
        import glob
        pattern = str(Path(output_dir) / "ragchecker_*_*.json")
        all_files = glob.glob(pattern)

        if all_files:
            actual_output = max(all_files, key=os.path.getctime)
        else:
            actual_output = output_file

        print(f"✅ Evaluation completed: {actual_output}")

        # Load results
        with open(actual_output) as f:
            results = json.load(f)

        return {
            "status": "success",
            "config_name": config_name,
            "output_file": str(actual_output),
            "results": results,
            "timestamp": timestamp,
        }

    except subprocess.CalledProcessError as e:
        print(f"❌ Evaluation failed: {e.stderr}")
        return {"status": "failed", "config_name": config_name, "error": e.stderr, "timestamp": timestamp}

def compare_results(results_with_reranker: dict[str, Any], results_without_reranker: dict[str, Any]) -> dict[str, Any]:
    """Compare results between reranker enabled and disabled"""
    comparison = {
        "reranker_enabled": results_with_reranker,
        "reranker_disabled": results_without_reranker,
        "comparison": {},
    }

    if results_with_reranker["status"] == "success" and results_without_reranker["status"] == "success":
        with_reranker = results_with_reranker["results"]
        without_reranker = results_without_reranker["results"]

        # Compare key metrics
        metrics_to_compare = ["precision", "recall", "f1", "faithfulness"]

        for metric in metrics_to_compare:
            if metric in with_reranker and metric in without_reranker:
                with_val = with_reranker[metric]
                without_val = without_reranker[metric]
                diff = with_val - without_val
                comparison["comparison"][metric] = {
                    "with_reranker": with_val,
                    "without_reranker": without_val,
                    "difference": diff,
                    "improvement": diff > 0,
                }

    return comparison

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Compare reranker performance")
    parser.add_argument("--output-dir", default="metrics/reranker_comparison", help="Output directory for results")
    parser.add_argument("--config-dir", default="configs", help="Directory containing config files")

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    config_dir = Path(args.config_dir)

    print("🚀 Reranker Comparison Evaluation")
    print("=" * 50)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output directory: {output_dir}")

    # Run evaluation with reranker enabled
    reranker_enabled_config = config_dir / "reranker_toggle.env"
    results_with_reranker = run_evaluation_with_config(
        "reranker_enabled", str(reranker_enabled_config), str(output_dir)
    )

    # Run evaluation with reranker disabled
    reranker_disabled_config = config_dir / "reranker_disabled.env"
    results_without_reranker = run_evaluation_with_config(
        "reranker_disabled", str(reranker_disabled_config), str(output_dir)
    )

    # Compare results
    comparison = compare_results(results_with_reranker, results_without_reranker)

    # Save comparison
    comparison_file = output_dir / f"reranker_comparison_{int(time.time())}.json"
    with open(comparison_file, "w") as f:
        json.dump(comparison, f, indent=2)

    print("\n📊 Comparison Results:")
    print(f"📁 Saved to: {comparison_file}")

    if "comparison" in comparison:
        for metric, data in comparison["comparison"].items():
            improvement = "📈" if data["improvement"] else "📉"
            print(
                f"{improvement} {metric}: {data['with_reranker']:.3f} vs {data['without_reranker']:.3f} (Δ{data['difference']:+.3f})"
            )

    return comparison

if __name__ == "__main__":
    result = main()
