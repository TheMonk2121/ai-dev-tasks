from __future__ import annotations
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Phase-2 Kickstart System
Safest path for DSPy compilation and deployment.
"""

class Phase2KickstartSystem:
    """Phase-2 kickstart system for DSPy compilation."""

    def __init__(self, config_dir: str = "configs/phase2"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.kickstart_log_file = self.config_dir / "kickstart_log.jsonl"

    def run_phase2_kickstart(self) -> dict[str, Any]:
        """Run Phase-2 kickstart with safest path."""
        print("🚀 PHASE-2 KICKSTART")
        print("=" * 50)
        print("🧠 Safest path for DSPy compilation and deployment")
        print()

        kickstart_result = {"timestamp": datetime.now().isoformat(), "phases": {}, "overall_status": "unknown"}

        # Phase 1: Baseline run saved
        print("📊 Phase 1: Baseline run saved...")
        baseline_result = self._save_baseline_run()
        kickstart_result["phases"]["baseline_saved"] = baseline_result

        # Phase 2: Compile on dev set only
        print("🧠 Phase 2: Compile on dev set only...")
        compile_result = self._compile_on_dev_set()
        kickstart_result["phases"]["dev_compile"] = compile_result

        # Phase 3: Gate & promote
        print("🚪 Phase 3: Gate & promote...")
        gate_result = self._gate_and_promote()
        kickstart_result["phases"]["gate_promote"] = gate_result

        # Determine overall status
        all_phases_passed = all(phase["success"] for phase in kickstart_result["phases"].values())
        kickstart_result["overall_status"] = "completed" if all_phases_passed else "failed"

        # Print summary
        print("\n📊 Phase-2 Kickstart Summary:")
        for phase_name, phase_result in kickstart_result["phases"].items():
            status_emoji = "✅" if phase_result["success"] else "❌"
            print(f"  {status_emoji} {phase_name}: {phase_result['message']}")

        if all_phases_passed:
            print("\n🎉 Phase-2 kickstart completed successfully!")
        else:
            print("\n⚠️ Phase-2 kickstart failed - Review issues")

        # Log results
        self._log_kickstart_results(kickstart_result)

        return kickstart_result

    def _save_baseline_run(self) -> dict[str, Any]:
        """Save baseline run for retrieval-only and deterministic few-shot."""
        print("  📊 Saving baseline artifacts...")

        baseline_result = {
            "phase_name": "baseline_saved",
            "timestamp": datetime.now().isoformat(),
            "steps": {},
            "success": False,
        }

        try:
            # Step 1: Freeze retrieval-only baseline
            print("    🔍 Step 1: Freezing retrieval-only baseline...")
            retrieval_result = self._freeze_retrieval_baseline()
            baseline_result["steps"]["retrieval_baseline"] = retrieval_result

            # Step 2: Freeze deterministic few-shot baseline
            print("    🧠 Step 2: Freezing deterministic few-shot baseline...")
            fewshot_result = self._freeze_fewshot_baseline()
            baseline_result["steps"]["fewshot_baseline"] = fewshot_result

            # Step 3: Generate baseline manifest
            print("    📋 Step 3: Generating baseline manifest...")
            manifest_result = self._generate_baseline_manifest()
            baseline_result["steps"]["baseline_manifest"] = manifest_result

            # Determine if baseline save was successful
            all_steps_successful = all(step["success"] for step in baseline_result["steps"].values())
            baseline_result["success"] = all_steps_successful

            baseline_result["message"] = (
                f"Baseline saved: {'success' if all_steps_successful else 'failed'} - {len([s for s in baseline_result['steps'].values() if s['success']])}/{len(baseline_result['steps'])} steps successful"
            )

        except Exception as e:
            baseline_result["error"] = str(e)
            baseline_result["message"] = f"Baseline save failed with exception: {e}"

        return baseline_result

    def _compile_on_dev_set(self) -> dict[str, Any]:
        """Compile on dev set only."""
        print("  🧠 Compiling DSPy program on dev set...")

        compile_result = {
            "phase_name": "dev_compile",
            "timestamp": datetime.now().isoformat(),
            "steps": {},
            "success": False,
        }

        try:
            # Step 1: Prepare dev set
            print("    📚 Step 1: Preparing dev set...")
            devset_result = self._prepare_dev_set()
            compile_result["steps"]["devset_prep"] = devset_result

            # Step 2: Run DSPy compilation
            print("    🔧 Step 2: Running DSPy compilation...")
            dspy_result = self._run_dspy_compilation()
            compile_result["steps"]["dspy_compile"] = dspy_result

            # Step 3: Save compiled artifacts
            print("    💾 Step 3: Saving compiled artifacts...")
            artifacts_result = self._save_compiled_artifacts()
            compile_result["steps"]["artifacts_save"] = artifacts_result

            # Determine if compilation was successful
            all_steps_successful = all(step["success"] for step in compile_result["steps"].values())
            compile_result["success"] = all_steps_successful

            compile_result["message"] = (
                f"Dev set compilation: {'success' if all_steps_successful else 'failed'} - {len([s for s in compile_result['steps'].values() if s['success']])}/{len(compile_result['steps'])} steps successful"
            )

        except Exception as e:
            compile_result["error"] = str(e)
            compile_result["message"] = f"Dev set compilation failed with exception: {e}"

        return compile_result

    def _gate_and_promote(self) -> dict[str, Any]:
        """Gate and promote compiled artifacts."""
        print("  🚪 Gating and promoting compiled artifacts...")

        gate_result = {
            "phase_name": "gate_promote",
            "timestamp": datetime.now().isoformat(),
            "steps": {},
            "success": False,
        }

        try:
            # Step 1: Run gate checks
            print("    🔍 Step 1: Running gate checks...")
            gate_checks = self._run_gate_checks()
            gate_result["steps"]["gate_checks"] = gate_checks

            # Step 2: Promote if gates pass
            if gate_checks["success"]:
                print("    🚀 Step 2: Promoting compiled artifacts...")
                promote_result = self._promote_compiled_artifacts()
                gate_result["steps"]["promote"] = promote_result
            else:
                print("    ⏸️ Step 2: Gates failed - retaining baseline...")
                retain_result = self._retain_baseline()
                gate_result["steps"]["retain_baseline"] = retain_result

            # Determine if gate and promote was successful
            gate_result["success"] = gate_checks["success"]

            if gate_checks["success"]:
                gate_result["message"] = "Gate and promote: success - compiled artifacts promoted"
            else:
                gate_result["message"] = "Gate and promote: gates failed - baseline retained"

        except Exception as e:
            gate_result["error"] = str(e)
            gate_result["message"] = f"Gate and promote failed with exception: {e}"

        return gate_result

    def _freeze_retrieval_baseline(self) -> dict[str, Any]:
        """Freeze retrieval-only baseline."""
        try:
            # Run retrieval-only evaluation
            result = subprocess.run(
                "python3 scripts/ragchecker_official_evaluation.py --use-bedrock --retrieval-only",
                shell=True,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    def _freeze_fewshot_baseline(self) -> dict[str, Any]:
        """Freeze deterministic few-shot baseline."""
        try:
            # Run deterministic few-shot evaluation
            result = subprocess.run(
                "python3 scripts/ragchecker_official_evaluation.py --use-bedrock --deterministic-fewshot",
                shell=True,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    def _generate_baseline_manifest(self) -> dict[str, Any]:
        """Generate baseline manifest."""
        try:
            # Generate baseline manifest
            result = subprocess.run(
                "python3 scripts/freeze_baseline_artifacts.py --action freeze --baseline-only",
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    def _prepare_dev_set(self) -> dict[str, Any]:
        """Prepare dev set for compilation."""
        try:
            # Check if dev set exists
            dev_set_file = Path("datasets/dev.jsonl")
            if not dev_set_file.exists():
                return {"success": False, "error": "Dev set file not found"}

            # Validate dev set format
            with open(dev_set_file) as f:
                lines = f.readlines()

            valid_lines = 0
            for line in lines:
                try:
                    json.loads(line.strip())
                    valid_lines += 1
                except json.JSONDecodeError:
                    continue

            return {
                "success": valid_lines > 0,
                "total_lines": len(lines),
                "valid_lines": valid_lines,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    def _run_dspy_compilation(self) -> dict[str, Any]:
        """Run DSPy compilation."""
        try:
            # Run DSPy compilation
            result = subprocess.run(
                "python3 dspy_program.py --compile --trainset datasets/train.jsonl --valset datasets/dev.jsonl",
                shell=True,
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    def _save_compiled_artifacts(self) -> dict[str, Any]:
        """Save compiled artifacts under CONFIG_HASH."""
        try:
            config_hash = os.getenv("CONFIG_HASH", "default")
            compiled_artifacts_dir = Path("compiled_artifacts") / config_hash

            if not compiled_artifacts_dir.exists():
                return {"success": False, "error": "Compiled artifacts directory not found"}

            # Check if artifacts exist
            artifacts = list(compiled_artifacts_dir.rglob("*"))
            artifact_files = [f for f in artifacts if f.is_file()]

            return {
                "success": len(artifact_files) > 0,
                "artifact_count": len(artifact_files),
                "artifacts_dir": str(compiled_artifacts_dir),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    def _run_gate_checks(self) -> dict[str, Any]:
        """Run gate checks for compiled artifacts."""
        try:
            # Run gate and promote system
            result = subprocess.run(
                "python3 scripts/gate_and_promote.py --action gate --compiled-artifacts",
                shell=True,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    def _promote_compiled_artifacts(self) -> dict[str, Any]:
        """Promote compiled artifacts to production."""
        try:
            # Promote artifacts
            result = subprocess.run(
                "python3 scripts/gate_and_promote.py --action promote --compiled-artifacts",
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    def _retain_baseline(self) -> dict[str, Any]:
        """Retain baseline configuration."""
        try:
            # Ensure baseline is active
            result = subprocess.run(
                "python3 scripts/retain_baseline.py",
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    def _log_kickstart_results(self, kickstart_result: dict[str, Any]):
        """Log kickstart results."""
        log_entry = {"timestamp": datetime.now().isoformat(), "type": "phase2_kickstart", "data": kickstart_result}

        with open(self.kickstart_log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

def main():
    """Main entry point for Phase-2 kickstart."""
    kickstart_system = Phase2KickstartSystem()
    result = kickstart_system.run_phase2_kickstart()

    # Exit with appropriate code
    if result["overall_status"] == "completed":
        print("\n🎉 Phase-2 kickstart completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️ Phase-2 kickstart failed - Review issues")
        sys.exit(1)

if __name__ == "__main__":
    main()
