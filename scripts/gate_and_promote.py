#!/usr/bin/env python3
"""
Gate and Promote System
Promotes compiled DSPy artifacts only if thresholds pass.
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class GateAndPromoteSystem:
    """Gate and promote system for DSPy compiled artifacts."""

    def __init__(
        self, compiled_artifacts_dir: str = "compiled_artifacts", promoted_artifacts_dir: str = "promoted_artifacts"
    ):
        self.compiled_artifacts_dir = Path(compiled_artifacts_dir)
        self.promoted_artifacts_dir = Path(promoted_artifacts_dir)
        self.promoted_artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Production thresholds
        self.thresholds = {
            "f1_score": 0.22,  # Baseline F1 score
            "precision_drift_max": 0.02,  # Max precision drift
            "latency_increase_max": 0.15,  # Max latency increase
            "oracle_prefilter_min": 0.85,  # Min oracle prefilter rate
            "reader_used_gold_min": 0.70,  # Min reader used gold rate
            "tool_schema_conformance_min": 0.95,  # Min tool schema conformance
        }

    def gate_and_promote(
        self, config_hash: str, evaluation_results: dict[str, Any], baseline_results: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Gate and promote compiled artifacts if thresholds pass."""
        print("🚪 GATE AND PROMOTE SYSTEM")
        print("=" * 50)
        print(f"🔧 Config Hash: {config_hash}")

        # Find compiled artifacts (skip check for gate-only mode)
        compiled_path = self.compiled_artifacts_dir / config_hash
        if not compiled_path.exists():
            print(f"⚠️ Compiled artifacts not found for config_hash: {config_hash}")
            print("🔍 Running gate checks only (no promotion)")

        # Run gate checks
        if evaluation_results is None:
            raise ValueError("evaluation_results is required")
        gate_results = self._run_gate_checks(evaluation_results, baseline_results)

        # Determine if promotion is allowed
        promotion_allowed = all(check["passed"] for check in gate_results["checks"].values())

        print(f"🔍 Gate results: {gate_results['passed_checks']}/{gate_results['total_checks']} checks passed")

        result = {
            "config_hash": config_hash,
            "timestamp": datetime.now().isoformat(),
            "gate_results": gate_results,
            "promotion_allowed": promotion_allowed,
            "promoted": False,
            "promotion_path": None,
        }

        if promotion_allowed:
            if compiled_path.exists():
                # Promote artifacts
                promotion_result = self._promote_artifacts(compiled_path, config_hash)
                result["promoted"] = True
                result["promotion_path"] = promotion_result["promotion_path"]
                result["promotion_manifest"] = promotion_result["manifest"]

                print("✅ Artifacts promoted successfully")
            else:
                print("✅ Gate checks passed (no artifacts to promote)")
        else:
            print("❌ Gate checks failed - artifacts not promoted")
            print("🔍 Failed checks:")
            for check_name, check_result in gate_results["checks"].items():
                if not check_result["passed"]:
                    print(f"  • {check_name}: {check_result['message']}")

        # Save gate and promote result
        self._save_gate_result(result)

        return result

    def _run_gate_checks(
        self, evaluation_results: dict[str, Any], baseline_results: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Run all gate checks against thresholds."""
        print("🔍 Running gate checks...")

        checks = {}

        # Extract metrics from evaluation results
        summary = evaluation_results.get("summary", {}) or evaluation_results.get("overall_metrics", {})

        # Check if this is a gold dataset
        has_gold = os.getenv("DATASET_HAS_GOLD", "1") == "1"

        # F1 Score Check (only for gold datasets with few-shot)
        if has_gold:
            # Primary accuracy gates for repo-gold: file-oracle
            try:
                cases = evaluation_results.get("case_results", [])
                n = max(1, len(cases))
                fop = sum(1 for c in cases if c.get("file_oracle_prefilter_hit")) / n
                foru = sum(1 for c in cases if c.get("file_oracle_reader_used")) / n
            except Exception:
                fop = 0.0
                foru = 0.0

            fop_min = float(os.getenv("FILE_ORACLE_PREFILTER_MIN", "0.85"))
            foru_min = float(os.getenv("FILE_ORACLE_READER_MIN", "0.70"))

            checks["file_oracle_prefilter"] = {
                "metric": "file_oracle_prefilter_rate",
                "value": fop,
                "threshold": fop_min,
                "passed": fop >= fop_min,
                "message": f"File-oracle prefilter {fop:.2%} {'≥' if fop >= fop_min else '<'} {fop_min:.2%}",
            }

            checks["file_oracle_reader_used"] = {
                "metric": "file_oracle_reader_used_rate",
                "value": foru,
                "threshold": foru_min,
                "passed": foru >= foru_min,
                "message": f"File-oracle reader used {foru:.2%} {'≥' if foru >= foru_min else '<'} {foru_min:.2%}",
            }

            # Keep F1 >= baseline
            f1_score = summary.get("f1_score", 0.0)
            checks["f1_score"] = {
                "metric": "f1_score",
                "value": f1_score,
                "threshold": self.thresholds["f1_score"],
                "passed": f1_score >= self.thresholds["f1_score"],
                "message": f"F1 score {f1_score:.3f} {'≥' if f1_score >= self.thresholds['f1_score'] else '<'} threshold {self.thresholds['f1_score']:.3f}",
            }

        # Precision Drift Check
        precision = summary.get("precision", 0.0)
        if baseline_results is not None:
            baseline_precision = baseline_results.get("summary", {}).get("precision", 0.0)
            precision_drift = abs(precision - baseline_precision)
        else:
            precision_drift = 0.0  # No baseline to compare against

        checks["precision_drift"] = {
            "metric": "precision_drift",
            "value": precision_drift,
            "threshold": self.thresholds["precision_drift_max"],
            "passed": precision_drift <= self.thresholds["precision_drift_max"],
            "message": f"Precision drift {precision_drift:.3f} {'≤' if precision_drift <= self.thresholds['precision_drift_max'] else '>'} threshold {self.thresholds['precision_drift_max']:.3f}",
        }

        # Latency Increase Check
        p95_latency = summary.get("p95_latency", 1.0)
        if baseline_results is not None:
            baseline_latency = baseline_results.get("summary", {}).get("p95_latency", 1.0)
            latency_increase = (p95_latency - baseline_latency) / baseline_latency
        else:
            latency_increase = 0.0  # No baseline to compare against

        checks["latency_increase"] = {
            "metric": "latency_increase",
            "value": latency_increase,
            "threshold": self.thresholds["latency_increase_max"],
            "passed": latency_increase <= self.thresholds["latency_increase_max"],
            "message": f"Latency increase {latency_increase:.1%} {'≤' if latency_increase <= self.thresholds['latency_increase_max'] else '>'} threshold {self.thresholds['latency_increase_max']:.1%}",
        }

        # Remove weak-oracle as gating metric for gold; keep as diagnostic only

        # Tool Schema Conformance Check
        tool_conformance = summary.get("tool_schema_conformance", 1.0)
        checks["tool_schema_conformance"] = {
            "metric": "tool_schema_conformance",
            "value": tool_conformance,
            "threshold": self.thresholds["tool_schema_conformance_min"],
            "passed": tool_conformance >= self.thresholds["tool_schema_conformance_min"],
            "message": f"Tool schema conformance {tool_conformance:.2%} {'≥' if tool_conformance >= self.thresholds['tool_schema_conformance_min'] else '<'} threshold {self.thresholds['tool_schema_conformance_min']:.2%}",
        }

        # Non-gold dataset gates (when DATASET_HAS_GOLD=0)
        def tokenize(s):
            import re

            return [w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if w]

        def query_coverage(case):
            q = set(tokenize(case.get("query", "")))
            texts = []
            for d in case.get("retrieval_snapshot", []) or []:
                t = d.get("text") or ""
                if t:
                    texts += tokenize(t)
            seen = set(texts)
            return len(q & seen) / max(1, len(q))

        if not has_gold:
            # Non-gold gates
            case_results = evaluation_results.get("case_results", [])
            snap_max = max(len(c.get("retrieval_snapshot", [])) for c in case_results) if case_results else 0
            bm25_hits = summary.get("bm25_hit_mean", 0)  # optional; compute if available
            vec_hits = summary.get("vec_hit_mean", 0)
            fused_max = summary.get("fused_pool_max", 0)
            cov = sum(query_coverage(c) for c in case_results) / max(1, len(case_results)) if case_results else 0

            # Snapshot breadth check
            checks["snapshot_breadth"] = {
                "metric": "snapshot_breadth",
                "value": snap_max,
                "threshold": int(os.getenv("SNAPSHOT_MIN", "30")),
                "passed": snap_max >= int(os.getenv("SNAPSHOT_MIN", "30")),
                "message": f"Snapshot max {snap_max} {'≥' if snap_max >= int(os.getenv('SNAPSHOT_MIN','30')) else '<'} min {os.getenv('SNAPSHOT_MIN','30')}",
            }

            # Query coverage check
            checks["query_coverage"] = {
                "metric": "query_coverage",
                "value": cov,
                "threshold": float(os.getenv("COVERAGE_MIN", "0.70")),
                "passed": cov >= float(os.getenv("COVERAGE_MIN", "0.70")),
                "message": f"Query coverage {cov:.2f} {'≥' if cov >= float(os.getenv('COVERAGE_MIN','0.70')) else '<'} min {os.getenv('COVERAGE_MIN','0.70')}",
            }

            # Optional breadth checks (if metrics are computed)
            if bm25_hits:
                checks["bm25_breadth"] = {
                    "metric": "bm25_breadth",
                    "value": bm25_hits,
                    "threshold": int(os.getenv("BM25_MIN", "50")),
                    "passed": bm25_hits >= int(os.getenv("BM25_MIN", "50")),
                    "message": f"BM25 breadth {bm25_hits} {'≥' if bm25_hits >= int(os.getenv('BM25_MIN','50')) else '<'} min {os.getenv('BM25_MIN','50')}",
                }

            if vec_hits:
                checks["vec_breadth"] = {
                    "metric": "vec_breadth",
                    "value": vec_hits,
                    "threshold": int(os.getenv("VEC_MIN", "50")),
                    "passed": vec_hits >= int(os.getenv("VEC_MIN", "50")),
                    "message": f"Vector breadth {vec_hits} {'≥' if vec_hits >= int(os.getenv('VEC_MIN','50')) else '<'} min {os.getenv('VEC_MIN','50')}",
                }

            if fused_max:
                checks["fused_breadth"] = {
                    "metric": "fused_breadth",
                    "value": fused_max,
                    "threshold": int(os.getenv("FUSED_MIN", "80")),
                    "passed": fused_max >= int(os.getenv("FUSED_MIN", "80")),
                    "message": f"Fused pool max {fused_max} {'≥' if fused_max >= int(os.getenv('FUSED_MIN','80')) else '<'} min {os.getenv('FUSED_MIN','80')}",
                }

        # Overall gate result
        all_passed = all(check["passed"] for check in checks.values())

        return {
            "timestamp": datetime.now().isoformat(),
            "checks": checks,
            "all_passed": all_passed,
            "total_checks": len(checks),
            "passed_checks": sum(1 for check in checks.values() if check["passed"]),
            "failed_checks": sum(1 for check in checks.values() if not check["passed"]),
        }

    def _promote_artifacts(self, compiled_path: Path, config_hash: str) -> dict[str, Any]:
        """Promote compiled artifacts to production."""
        print("🚀 Promoting artifacts to production...")

        # Create promotion directory
        promotion_id = f"promoted_{config_hash}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        promotion_path = self.promoted_artifacts_dir / promotion_id
        promotion_path.mkdir(parents=True, exist_ok=True)

        # Copy compiled artifacts
        shutil.copytree(compiled_path, promotion_path / "compiled_artifacts")

        # Create promotion manifest
        promotion_manifest = {
            "promotion_id": promotion_id,
            "config_hash": config_hash,
            "promotion_time": datetime.now().isoformat(),
            "source_path": str(compiled_path),
            "promotion_path": str(promotion_path),
            "artifacts": {
                "compiled_program": "compiled_artifacts/compiled_program.json",
                "prompts": "compiled_artifacts/prompts/",
                "few_shots": "compiled_artifacts/few_shots/",
                "config": "compiled_artifacts/config.json",
            },
            "status": "promoted",
        }

        # Save promotion manifest
        manifest_file = promotion_path / "promotion_manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(promotion_manifest, f, indent=2)

        # Update active pointer to promoted artifacts
        self._update_active_pointer(promotion_id, config_hash)

        print(f"✅ Artifacts promoted to: {promotion_path}")

        return {"promotion_path": str(promotion_path), "manifest": promotion_manifest}

    def _update_active_pointer(self, promotion_id: str, config_hash: str):
        """Update active pointer to promoted artifacts."""
        pointer_config = {
            "promotion_id": promotion_id,
            "config_hash": config_hash,
            "timestamp": datetime.now().isoformat(),
            "active": True,
            "type": "promoted_artifacts",
        }

        pointer_file = self.promoted_artifacts_dir / "active_pointer.json"
        with open(pointer_file, "w") as f:
            json.dump(pointer_config, f, indent=2)

        print(f"📍 Active pointer updated to: {promotion_id}")

    def _save_gate_result(self, result: dict[str, Any]):
        """Save gate and promote result."""
        result_file = (
            self.promoted_artifacts_dir
            / f"gate_result_{result['config_hash']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(result_file, "w") as f:
            json.dump(result, f, indent=2)

    def get_promotion_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get promotion history."""
        promotions = []

        for promotion_dir in self.promoted_artifacts_dir.iterdir():
            if promotion_dir.is_dir() and promotion_dir.name.startswith("promoted_"):
                manifest_file = promotion_dir / "promotion_manifest.json"
                if manifest_file.exists():
                    with open(manifest_file) as f:
                        manifest = json.load(f)
                    promotions.append(manifest)

        # Sort by promotion time (newest first)
        promotions.sort(key=lambda x: x["promotion_time"], reverse=True)
        return promotions[:limit]

    def get_active_promotion(self) -> dict[str, Any] | None:
        """Get currently active promotion."""
        pointer_file = self.promoted_artifacts_dir / "active_pointer.json"

        if not pointer_file.exists():
            return None

        with open(pointer_file) as f:
            pointer_config = json.load(f)

        if not pointer_config.get("active", False):
            return None

        promotion_id = pointer_config["promotion_id"]
        promotion_path = self.promoted_artifacts_dir / promotion_id

        if not promotion_path.exists():
            return None

        manifest_file = promotion_path / "promotion_manifest.json"
        if not manifest_file.exists():
            return None

        with open(manifest_file) as f:
            return json.load(f)


def main():
    """Main entry point for gate and promote system."""
    import argparse

    parser = argparse.ArgumentParser(description="Gate and promote system")
    parser.add_argument("--action", choices=["gate", "history", "active"], required=True)
    parser.add_argument("--config-hash", help="Configuration hash")
    parser.add_argument("--evaluation-results", help="Evaluation results JSON file")
    parser.add_argument("--baseline-results", help="Baseline results JSON file")
    parser.add_argument("--limit", type=int, default=10, help="Limit for history action")

    args = parser.parse_args()

    gate_system = GateAndPromoteSystem()

    if args.action == "gate":
        if not all([args.config_hash, args.evaluation_results]):
            print("❌ --config-hash and --evaluation-results required for gate action")
            sys.exit(1)

        # Load evaluation results
        with open(args.evaluation_results) as f:
            evaluation_results = json.load(f)

        # Load baseline results if provided
        baseline_results = None
        if args.baseline_results:
            with open(args.baseline_results) as f:
                baseline_results = json.load(f)

        result = gate_system.gate_and_promote(
            config_hash=args.config_hash, evaluation_results=evaluation_results, baseline_results=baseline_results
        )

        if result["promotion_allowed"]:
            if result["promoted"]:
                print("✅ Artifacts promoted successfully")
            else:
                print("✅ Gate checks passed (no artifacts to promote)")
            sys.exit(0)
        else:
            print("❌ Gate checks failed - artifacts not promoted")
            sys.exit(1)

    elif args.action == "history":
        history = gate_system.get_promotion_history(limit=args.limit)
        print(f"📋 Promotion History (last {len(history)} entries):")
        for promotion in history:
            print(f"  • {promotion['promotion_id']} - {promotion['promotion_time']}")
            print(f"    Config: {promotion['config_hash']}, Status: {promotion['status']}")

    elif args.action == "active":
        active = gate_system.get_active_promotion()
        if active:
            print(f"📍 Active Promotion: {active['promotion_id']}")
            print(f"🔧 Config Hash: {active['config_hash']}")
            print(f"⏰ Promotion Time: {active['promotion_time']}")
        else:
            print("❌ No active promotion found")


if __name__ == "__main__":
    main()
