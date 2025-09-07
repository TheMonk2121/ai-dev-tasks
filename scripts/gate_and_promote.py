#!/usr/bin/env python3
"""
Gate and Promote System
Promotes compiled DSPy artifacts only if thresholds pass.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class GateAndPromoteSystem:
    """Gate and promote system for DSPy compiled artifacts."""

    def __init__(self, 
                 compiled_artifacts_dir: str = "compiled_artifacts",
                 promoted_artifacts_dir: str = "promoted_artifacts"):
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
            "tool_schema_conformance_min": 0.95  # Min tool schema conformance
        }

    def gate_and_promote(self, 
                        config_hash: str,
                        evaluation_results: Dict[str, Any],
                        baseline_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """Gate and promote compiled artifacts if thresholds pass."""
        print("🚪 GATE AND PROMOTE SYSTEM")
        print("="*50)
        print(f"🔧 Config Hash: {config_hash}")
        
        # Find compiled artifacts
        compiled_path = self.compiled_artifacts_dir / config_hash
        if not compiled_path.exists():
            return {
                "success": False,
                "error": f"Compiled artifacts not found for config_hash: {config_hash}",
                "promoted": False
            }
        
        # Run gate checks
        gate_results = self._run_gate_checks(evaluation_results, baseline_results)
        
        # Determine if promotion is allowed
        promotion_allowed = all(
            check["passed"] for check in gate_results["checks"].values()
        )
        
        result = {
            "config_hash": config_hash,
            "timestamp": datetime.now().isoformat(),
            "gate_results": gate_results,
            "promotion_allowed": promotion_allowed,
            "promoted": False,
            "promotion_path": None
        }
        
        if promotion_allowed:
            # Promote artifacts
            promotion_result = self._promote_artifacts(compiled_path, config_hash)
            result["promoted"] = True
            result["promotion_path"] = promotion_result["promotion_path"]
            result["promotion_manifest"] = promotion_result["manifest"]
            
            print("✅ Artifacts promoted successfully")
        else:
            print("❌ Gate checks failed - artifacts not promoted")
            print("🔍 Failed checks:")
            for check_name, check_result in gate_results["checks"].items():
                if not check_result["passed"]:
                    print(f"  • {check_name}: {check_result['message']}")
        
        # Save gate and promote result
        self._save_gate_result(result)
        
        return result

    def _run_gate_checks(self, 
                        evaluation_results: Dict[str, Any],
                        baseline_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run all gate checks against thresholds."""
        print("🔍 Running gate checks...")
        
        checks = {}
        
        # Extract metrics from evaluation results
        summary = evaluation_results.get("summary", {})
        
        # F1 Score Check
        f1_score = summary.get("f1_score", 0.0)
        checks["f1_score"] = {
            "metric": "f1_score",
            "value": f1_score,
            "threshold": self.thresholds["f1_score"],
            "passed": f1_score >= self.thresholds["f1_score"],
            "message": f"F1 score {f1_score:.3f} {'≥' if f1_score >= self.thresholds['f1_score'] else '<'} threshold {self.thresholds['f1_score']:.3f}"
        }
        
        # Precision Drift Check
        precision = summary.get("precision", 0.0)
        if baseline_results:
            baseline_precision = baseline_results.get("summary", {}).get("precision", 0.0)
            precision_drift = abs(precision - baseline_precision)
        else:
            precision_drift = 0.0  # No baseline to compare against
        
        checks["precision_drift"] = {
            "metric": "precision_drift",
            "value": precision_drift,
            "threshold": self.thresholds["precision_drift_max"],
            "passed": precision_drift <= self.thresholds["precision_drift_max"],
            "message": f"Precision drift {precision_drift:.3f} {'≤' if precision_drift <= self.thresholds['precision_drift_max'] else '>'} threshold {self.thresholds['precision_drift_max']:.3f}"
        }
        
        # Latency Increase Check
        p95_latency = summary.get("p95_latency", 1.0)
        if baseline_results:
            baseline_latency = baseline_results.get("summary", {}).get("p95_latency", 1.0)
            latency_increase = (p95_latency - baseline_latency) / baseline_latency
        else:
            latency_increase = 0.0  # No baseline to compare against
        
        checks["latency_increase"] = {
            "metric": "latency_increase",
            "value": latency_increase,
            "threshold": self.thresholds["latency_increase_max"],
            "passed": latency_increase <= self.thresholds["latency_increase_max"],
            "message": f"Latency increase {latency_increase:.1%} {'≤' if latency_increase <= self.thresholds['latency_increase_max'] else '>'} threshold {self.thresholds['latency_increase_max']:.1%}"
        }
        
        # Oracle Prefilter Check
        oracle_prefilter = summary.get("oracle_prefilter_rate", 0.0)
        checks["oracle_prefilter"] = {
            "metric": "oracle_prefilter_rate",
            "value": oracle_prefilter,
            "threshold": self.thresholds["oracle_prefilter_min"],
            "passed": oracle_prefilter >= self.thresholds["oracle_prefilter_min"],
            "message": f"Oracle prefilter {oracle_prefilter:.2%} {'≥' if oracle_prefilter >= self.thresholds['oracle_prefilter_min'] else '<'} threshold {self.thresholds['oracle_prefilter_min']:.2%}"
        }
        
        # Reader Used Gold Check
        reader_used_gold = summary.get("reader_used_gold_rate", 0.0)
        checks["reader_used_gold"] = {
            "metric": "reader_used_gold_rate",
            "value": reader_used_gold,
            "threshold": self.thresholds["reader_used_gold_min"],
            "passed": reader_used_gold >= self.thresholds["reader_used_gold_min"],
            "message": f"Reader used gold {reader_used_gold:.2%} {'≥' if reader_used_gold >= self.thresholds['reader_used_gold_min'] else '<'} threshold {self.thresholds['reader_used_gold_min']:.2%}"
        }
        
        # Tool Schema Conformance Check
        tool_conformance = summary.get("tool_schema_conformance", 1.0)
        checks["tool_schema_conformance"] = {
            "metric": "tool_schema_conformance",
            "value": tool_conformance,
            "threshold": self.thresholds["tool_schema_conformance_min"],
            "passed": tool_conformance >= self.thresholds["tool_schema_conformance_min"],
            "message": f"Tool schema conformance {tool_conformance:.2%} {'≥' if tool_conformance >= self.thresholds['tool_schema_conformance_min'] else '<'} threshold {self.thresholds['tool_schema_conformance_min']:.2%}"
        }
        
        # Overall gate result
        all_passed = all(check["passed"] for check in checks.values())
        
        return {
            "timestamp": datetime.now().isoformat(),
            "checks": checks,
            "all_passed": all_passed,
            "total_checks": len(checks),
            "passed_checks": sum(1 for check in checks.values() if check["passed"]),
            "failed_checks": sum(1 for check in checks.values() if not check["passed"])
        }

    def _promote_artifacts(self, compiled_path: Path, config_hash: str) -> Dict[str, Any]:
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
                "config": "compiled_artifacts/config.json"
            },
            "status": "promoted"
        }
        
        # Save promotion manifest
        manifest_file = promotion_path / "promotion_manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(promotion_manifest, f, indent=2)
        
        # Update active pointer to promoted artifacts
        self._update_active_pointer(promotion_id, config_hash)
        
        print(f"✅ Artifacts promoted to: {promotion_path}")
        
        return {
            "promotion_path": str(promotion_path),
            "manifest": promotion_manifest
        }

    def _update_active_pointer(self, promotion_id: str, config_hash: str):
        """Update active pointer to promoted artifacts."""
        pointer_config = {
            "promotion_id": promotion_id,
            "config_hash": config_hash,
            "timestamp": datetime.now().isoformat(),
            "active": True,
            "type": "promoted_artifacts"
        }
        
        pointer_file = self.promoted_artifacts_dir / "active_pointer.json"
        with open(pointer_file, "w") as f:
            json.dump(pointer_config, f, indent=2)
        
        print(f"📍 Active pointer updated to: {promotion_id}")

    def _save_gate_result(self, result: Dict[str, Any]):
        """Save gate and promote result."""
        result_file = self.promoted_artifacts_dir / f"gate_result_{result['config_hash']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, "w") as f:
            json.dump(result, f, indent=2)

    def get_promotion_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get promotion history."""
        promotions = []
        
        for promotion_dir in self.promoted_artifacts_dir.iterdir():
            if promotion_dir.is_dir() and promotion_dir.name.startswith("promoted_"):
                manifest_file = promotion_dir / "promotion_manifest.json"
                if manifest_file.exists():
                    with open(manifest_file, "r") as f:
                        manifest = json.load(f)
                    promotions.append(manifest)
        
        # Sort by promotion time (newest first)
        promotions.sort(key=lambda x: x["promotion_time"], reverse=True)
        return promotions[:limit]

    def get_active_promotion(self) -> Optional[Dict[str, Any]]:
        """Get currently active promotion."""
        pointer_file = self.promoted_artifacts_dir / "active_pointer.json"
        
        if not pointer_file.exists():
            return None
        
        with open(pointer_file, "r") as f:
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
        
        with open(manifest_file, "r") as f:
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
        with open(args.evaluation_results, "r") as f:
            evaluation_results = json.load(f)
        
        # Load baseline results if provided
        baseline_results = None
        if args.baseline_results:
            with open(args.baseline_results, "r") as f:
                baseline_results = json.load(f)
        
        result = gate_system.gate_and_promote(
            config_hash=args.config_hash,
            evaluation_results=evaluation_results,
            baseline_results=baseline_results
        )
        
        if result["promoted"]:
            print(f"✅ Artifacts promoted successfully")
            sys.exit(0)
        else:
            print(f"❌ Gate checks failed - artifacts not promoted")
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
