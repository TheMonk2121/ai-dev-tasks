#!/usr/bin/env python3
"""
Freeze Baseline Artifacts
Save results JSON + eval manifest + dataset checksums + CONFIG_HASH/INGEST_RUN_ID.
"""

import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class BaselineArtifactFreezer:
    """Freezes baseline artifacts for production go-live."""

    def __init__(self, baseline_dir: str = "baseline_artifacts"):
        self.baseline_dir = Path(baseline_dir)
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def freeze_baseline_artifacts(
        self,
        results_json: str,
        eval_manifest: str,
        dataset_files: List[str],
        config_hash: str = None,
        ingest_run_id: str = None,
    ) -> Dict[str, Any]:
        """Freeze all baseline artifacts with integrity protection."""
        print("🔒 FREEZING BASELINE ARTIFACTS")
        print("=" * 50)

        # Generate baseline ID
        baseline_id = f"baseline_{self.timestamp}"
        baseline_path = self.baseline_dir / baseline_id
        baseline_path.mkdir(parents=True, exist_ok=True)

        print(f"📋 Baseline ID: {baseline_id}")
        print(f"📁 Baseline Path: {baseline_path}")

        # Freeze results JSON
        results_info = self._freeze_results_json(results_json, baseline_path)

        # Freeze eval manifest
        manifest_info = self._freeze_eval_manifest(eval_manifest, baseline_path)

        # Freeze dataset checksums
        dataset_info = self._freeze_dataset_checksums(dataset_files, baseline_path)

        # Freeze configuration
        config_info = self._freeze_configuration(config_hash, ingest_run_id, baseline_path)

        # Create baseline manifest
        baseline_manifest = {
            "baseline_id": baseline_id,
            "timestamp": self.timestamp,
            "freeze_time": datetime.now().isoformat(),
            "artifacts": {
                "results_json": results_info,
                "eval_manifest": manifest_info,
                "datasets": dataset_info,
                "configuration": config_info,
            },
            "integrity": {
                "baseline_checksum": self._calculate_baseline_checksum(baseline_path),
                "freeze_complete": True,
            },
        }

        # Save baseline manifest
        manifest_file = baseline_path / "baseline_manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(baseline_manifest, f, indent=2)

        print("✅ Baseline artifacts frozen successfully")
        print(f"📋 Manifest: {manifest_file}")
        print(f"🔒 Baseline checksum: {baseline_manifest['integrity']['baseline_checksum']}")

        return baseline_manifest

    def _freeze_results_json(self, results_json: str, baseline_path: Path) -> Dict[str, Any]:
        """Freeze evaluation results JSON with integrity check."""
        print("📊 Freezing results JSON...")

        if not os.path.exists(results_json):
            raise FileNotFoundError(f"Results JSON not found: {results_json}")

        # Copy results file
        results_baseline = baseline_path / "results.json"
        shutil.copy2(results_json, results_baseline)

        # Calculate checksum
        with open(results_baseline, "rb") as f:
            checksum = hashlib.sha256(f.read()).hexdigest()

        # Extract key metrics
        with open(results_baseline, "r") as f:
            results_data = json.load(f)

        metrics = results_data.get("summary", {})

        return {
            "source_file": results_json,
            "baseline_file": str(results_baseline),
            "checksum": checksum,
            "metrics": {
                "f1_score": metrics.get("f1_score", 0.0),
                "precision": metrics.get("precision", 0.0),
                "recall": metrics.get("recall", 0.0),
                "oracle_prefilter_rate": metrics.get("oracle_prefilter_rate", 0.0),
                "reader_used_gold_rate": metrics.get("reader_used_gold_rate", 0.0),
            },
        }

    def _freeze_eval_manifest(self, eval_manifest: str, baseline_path: Path) -> Dict[str, Any]:
        """Freeze evaluation manifest with integrity check."""
        print("📋 Freezing eval manifest...")

        if not os.path.exists(eval_manifest):
            raise FileNotFoundError(f"Eval manifest not found: {eval_manifest}")

        # Copy manifest file
        manifest_baseline = baseline_path / "eval_manifest.yaml"
        shutil.copy2(eval_manifest, manifest_baseline)

        # Calculate checksum
        with open(manifest_baseline, "rb") as f:
            checksum = hashlib.sha256(f.read()).hexdigest()

        return {"source_file": eval_manifest, "baseline_file": str(manifest_baseline), "checksum": checksum}

    def _freeze_dataset_checksums(self, dataset_files: List[str], baseline_path: Path) -> Dict[str, Any]:
        """Freeze dataset checksums for integrity verification."""
        print("📚 Freezing dataset checksums...")

        dataset_info = {}

        for dataset_file in dataset_files:
            if not os.path.exists(dataset_file):
                print(f"⚠️ Dataset file not found: {dataset_file}")
                continue

            # Calculate checksum
            with open(dataset_file, "rb") as f:
                checksum = hashlib.sha256(f.read()).hexdigest()

            # Get file info
            file_stat = os.stat(dataset_file)

            dataset_info[dataset_file] = {
                "checksum": checksum,
                "size_bytes": file_stat.st_size,
                "modified_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            }

        # Save dataset checksums
        checksums_file = baseline_path / "dataset_checksums.json"
        with open(checksums_file, "w") as f:
            json.dump(dataset_info, f, indent=2)

        return {"checksums_file": str(checksums_file), "datasets": dataset_info, "total_datasets": len(dataset_info)}

    def _freeze_configuration(self, config_hash: str, ingest_run_id: str, baseline_path: Path) -> Dict[str, Any]:
        """Freeze configuration parameters."""
        print("⚙️ Freezing configuration...")

        # Get current environment variables
        config_vars = {
            "CONFIG_HASH": config_hash or os.getenv("CONFIG_HASH", "unknown"),
            "INGEST_RUN_ID": ingest_run_id or os.getenv("INGEST_RUN_ID", "unknown"),
            "TIMESTAMP": self.timestamp,
            "EVAL_DISABLE_CACHE": os.getenv("EVAL_DISABLE_CACHE", "1"),
            "FEW_SHOT_K": os.getenv("FEW_SHOT_K", "0"),
            "EVAL_COT": os.getenv("EVAL_COT", "0"),
            "TEMPERATURE": os.getenv("TEMPERATURE", "0"),
        }

        # Save configuration
        config_file = baseline_path / "configuration.json"
        with open(config_file, "w") as f:
            json.dump(config_vars, f, indent=2)

        return {
            "config_file": str(config_file),
            "config_hash": config_vars["CONFIG_HASH"],
            "ingest_run_id": config_vars["INGEST_RUN_ID"],
            "environment_vars": config_vars,
        }

    def _calculate_baseline_checksum(self, baseline_path: Path) -> str:
        """Calculate overall baseline checksum."""
        checksums = []

        # Collect all file checksums
        for file_path in baseline_path.rglob("*"):
            if file_path.is_file():
                with open(file_path, "rb") as f:
                    file_checksum = hashlib.sha256(f.read()).hexdigest()
                    checksums.append(f"{file_path.name}:{file_checksum}")

        # Sort for consistent ordering
        checksums.sort()

        # Calculate overall checksum
        combined = "\n".join(checksums)
        return hashlib.sha256(combined.encode()).hexdigest()

    def verify_baseline_integrity(self, baseline_id: str) -> Dict[str, Any]:
        """Verify baseline artifact integrity."""
        baseline_path = self.baseline_dir / baseline_id

        if not baseline_path.exists():
            return {"valid": False, "error": f"Baseline {baseline_id} not found"}

        # Load baseline manifest
        manifest_file = baseline_path / "baseline_manifest.json"
        if not manifest_file.exists():
            return {"valid": False, "error": "Baseline manifest not found"}

        with open(manifest_file, "r") as f:
            manifest = json.load(f)

        # Verify checksums
        verification_results = {
            "baseline_id": baseline_id,
            "valid": True,
            "verification_time": datetime.now().isoformat(),
            "checksums": {},
        }

        # Verify results JSON
        results_info = manifest["artifacts"]["results_json"]
        if os.path.exists(results_info["baseline_file"]):
            with open(results_info["baseline_file"], "rb") as f:
                current_checksum = hashlib.sha256(f.read()).hexdigest()
            verification_results["checksums"]["results_json"] = {
                "expected": results_info["checksum"],
                "actual": current_checksum,
                "valid": current_checksum == results_info["checksum"],
            }

        # Verify eval manifest
        manifest_info = manifest["artifacts"]["eval_manifest"]
        if os.path.exists(manifest_info["baseline_file"]):
            with open(manifest_info["baseline_file"], "rb") as f:
                current_checksum = hashlib.sha256(f.read()).hexdigest()
            verification_results["checksums"]["eval_manifest"] = {
                "expected": manifest_info["checksum"],
                "actual": current_checksum,
                "valid": current_checksum == manifest_info["checksum"],
            }

        # Overall validity
        all_valid = all(checksum_info["valid"] for checksum_info in verification_results["checksums"].values())
        verification_results["valid"] = all_valid

        return verification_results

    def list_baselines(self) -> List[Dict[str, Any]]:
        """List all frozen baselines."""
        baselines = []

        for baseline_dir in self.baseline_dir.iterdir():
            if baseline_dir.is_dir():
                manifest_file = baseline_dir / "baseline_manifest.json"
                if manifest_file.exists():
                    with open(manifest_file, "r") as f:
                        manifest = json.load(f)

                    baselines.append(
                        {
                            "baseline_id": manifest["baseline_id"],
                            "timestamp": manifest["timestamp"],
                            "freeze_time": manifest["freeze_time"],
                            "config_hash": manifest["artifacts"]["configuration"]["config_hash"],
                            "ingest_run_id": manifest["artifacts"]["configuration"]["ingest_run_id"],
                            "metrics": manifest["artifacts"]["results_json"]["metrics"],
                        }
                    )

        # Sort by timestamp (newest first)
        baselines.sort(key=lambda x: x["timestamp"], reverse=True)
        return baselines


def main():
    """Main entry point for baseline artifact freezer."""
    import argparse

    parser = argparse.ArgumentParser(description="Freeze baseline artifacts")
    parser.add_argument("--action", choices=["freeze", "verify", "list"], required=True)
    parser.add_argument("--results-json", help="Results JSON file to freeze")
    parser.add_argument("--eval-manifest", help="Eval manifest file to freeze")
    parser.add_argument("--datasets", nargs="+", help="Dataset files to freeze")
    parser.add_argument("--config-hash", help="Configuration hash")
    parser.add_argument("--ingest-run-id", help="Ingest run ID")
    parser.add_argument("--baseline-id", help="Baseline ID for verify action")

    args = parser.parse_args()

    freezer = BaselineArtifactFreezer()

    if args.action == "freeze":
        if not args.results_json or not args.eval_manifest:
            print("❌ --results-json and --eval-manifest required for freeze action")
            sys.exit(1)

        result = freezer.freeze_baseline_artifacts(
            results_json=args.results_json,
            eval_manifest=args.eval_manifest,
            dataset_files=args.datasets or [],
            config_hash=args.config_hash,
            ingest_run_id=args.ingest_run_id,
        )

        print(f"✅ Baseline frozen: {result['baseline_id']}")

    elif args.action == "verify":
        if not args.baseline_id:
            print("❌ --baseline-id required for verify action")
            sys.exit(1)

        result = freezer.verify_baseline_integrity(args.baseline_id)
        if result["valid"]:
            print(f"✅ Baseline {args.baseline_id} integrity verified")
        else:
            print(f"❌ Baseline {args.baseline_id} integrity check failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    elif args.action == "list":
        baselines = freezer.list_baselines()
        print("📋 Frozen Baselines:")
        for baseline in baselines:
            print(f"  • {baseline['baseline_id']} - {baseline['freeze_time']}")
            print(f"    Config: {baseline['config_hash']}, Run: {baseline['ingest_run_id']}")
            print(
                f"    F1: {baseline['metrics']['f1_score']:.3f}, Oracle: {baseline['metrics']['oracle_prefilter_rate']:.2%}"
            )


if __name__ == "__main__":
    main()
