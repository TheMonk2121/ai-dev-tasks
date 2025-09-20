import json
from typing import Any

#!/usr/bin/env python3
"""
Direct RAGChecker evaluation with Bedrock - bypasses the complex wrapper

Usage:
  # Fast mode (default): basic metrics, no joint checking
  python3 scripts/run_bedrock_eval_direct.py

  # Full mode: all metrics and features (slower)
  FAST_MODE=0 python3 scripts/run_bedrock_eval_direct.py

  # Custom timeout (default: 60s)
  LITELLM_TIMEOUT=120 python3 scripts/run_bedrock_eval_direct.py
"""
import os
import subprocess
import sys
import time
from pathlib import Path


def main() -> Any:
    # Set AWS region for LiteLLM Bedrock integration
    os.environ

    # Set LiteLLM timeouts and retries to prevent hanging
    os.environ
    os.environ
    os.environ

    print("⏱️  LiteLLM timeouts: 60s, max retries: 1, workers: 1")

    # Ensure we're in the right directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Find the latest input file
    input_dir = Path("metrics/baseline_evaluations")
    input_files = list(input_dir.glob("ragchecker_official_input_*.json"))

    if not input_files:
        print("❌ No input files found. Run the data preparation first.")
        return 1

    # Use the most recent input file
    latest_input = max(input_files, key=lambda f: f.stat().st_mtime)
    print(f"📁 Using input file: {latest_input}")

    # Create output filename
    timestamp = latest_input.stem.replace("ragchecker_official_input_", "")
    output_file = input_dir / f"ragchecker_official_eval_bedrock_{timestamp}.json"

    # Build the command with fast mode defaults
    # Honor RAGCHECKER_FAST_MODE if set; fallback to FAST_MODE; default = 1
    fast_env: Any = os.getenv("RAGCHECKER_FAST_MODE")
    if fast_env is None:
        fast_env: Any = os.getenv("FAST_MODE")
    fast_mode = (fast_env or "1") == "1"

    if fast_mode:
        # Fast mode: basic metrics, no joint checking
        cmd = [
            sys.executable,
            "-m",
            "ragchecker.cli",
            "--input_path",
            str(latest_input),
            "--output_path",
            str(output_file),
            "--extractor_name",
            "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",
            "--checker_name",
            "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",
            "--batch_size_extractor",
            "1",
            "--batch_size_checker",
            "1",
            "--metrics",
            "precision",
            "recall",
            "f1",
            "--disable_joint_check",
        ]
        print("⚡ Fast mode: basic metrics only, joint checking disabled")
    else:
        # Full mode: all metrics and features
        cmd = [
            sys.executable,
            "-m",
            "ragchecker.cli",
            "--input_path",
            str(latest_input),
            "--output_path",
            str(output_file),
            "--extractor_name",
            "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",
            "--checker_name",
            "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",
            "--batch_size_extractor",
            "1",
            "--batch_size_checker",
            "1",
            "--metrics",
            "all_metrics",
        ]
        print("🐌 Full mode: all metrics enabled (will take longer)")

    print("🚀 Running RAGChecker CLI with Bedrock models...")
    print(f"📊 Command: {' '.join(cmd)}")
    print("=" * 80)

    # Run with real-time output
    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True
        )

        # Stream output in real-time with progress indicator
        start_time: Any = time.time()
        last_progress = start_time

        while True:
            stdout_line = process.stdout.readline()
            stderr_line = process.stderr.readline()

            if stdout_line:
                print(f"📊 {stdout_line.rstrip()}")
                last_progress: Any = time.time()

            if stderr_line:
                print(f"⚠️  {stderr_line.rstrip()}")
                last_progress: Any = time.time()

            # Check if process is still running
            if process.poll() is not None:
                break

            # Show progress indicator every 30 seconds
            current_time: Any = time.time()
            if current_time - last_progress > 30:
                elapsed = current_time - start_time
                print(f"⏳ Still processing... (elapsed: {elapsed:.0f}s)")
                last_progress = current_time

        # Wait for completion
        return_code: Any = process.wait()

        if return_code == 0:
            print("\n✅ RAGChecker evaluation completed successfully!")
            print(f"📊 Results saved to: {output_file}")
            return 0
        else:
            print(f"\n❌ RAGChecker failed with return code: {return_code}")
            return return_code

    except KeyboardInterrupt:
        print("\n⚠️ Evaluation interrupted by user")
        process.terminate()
        process.wait()
        return 1
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
