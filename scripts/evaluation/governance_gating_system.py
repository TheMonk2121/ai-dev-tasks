#!/usr/bin/env python3
"""
Governance Gating System

Comprehensive governance system that consumes real metrics from evaluations
and enforces quality gates, regression detection, and baseline compliance.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.schemas.eval_settings import EvalSettings


class GovernanceGatingSystem:
    """Comprehensive governance gating system for evaluation quality enforcement."""
    
    def __init__(self, profile: str = "gold"):
        self.profile: str = profile
        self.settings: EvalSettings = EvalSettings.from_profile(profile)
        self.quality_thresholds: dict[str, float] = self._load_quality_thresholds()
        self.baseline_metrics: dict[str, float] = self._load_baseline_metrics()
        self.regression_thresholds: dict[str, float] = self._load_regression_thresholds()
        
    def _load_quality_thresholds(self) -> dict[str, float]:
        """Load quality thresholds for the current profile."""
        if self.profile == "gold":
            return {
                "precision": 0.85,
                "recall": 0.75,
                "f1_score": 0.80,
                "faithfulness": 0.90,
                "retrieval_precision": 0.85,
                "retrieval_recall": 0.75,
            }
        elif self.profile == "real":
            return {
                "precision": 0.80,
                "recall": 0.70,
                "f1_score": 0.75,
                "faithfulness": 0.85,
                "retrieval_precision": 0.80,
                "retrieval_recall": 0.70,
            }
        else:  # mock
            return {
                "precision": 0.70,
                "recall": 0.60,
                "f1_score": 0.65,
                "faithfulness": 0.75,
                "retrieval_precision": 0.70,
                "retrieval_recall": 0.60,
            }
    
    def _load_baseline_metrics(self) -> dict[str, float]:
        """Load baseline metrics for regression detection."""
        baseline_file = Path("metrics/baseline_manifest.json")
        if baseline_file.exists():
            try:
                with open(baseline_file) as f:
                    baseline_data = json.load(f)
                return baseline_data.get("metrics", {})
            except Exception as e:
                print(f"⚠️ Failed to load baseline metrics: {e}")
        
        # Fallback to default baselines
        return {
            "precision": 0.85,
            "recall": 0.75,
            "f1_score": 0.80,
            "faithfulness": 0.90,
        }
    
    def _load_regression_thresholds(self) -> dict[str, float]:
        """Load regression detection thresholds."""
        return {
            "precision": 0.10,  # 10% decline threshold
            "recall": 0.10,
            "f1_score": 0.10,
            "faithfulness": 0.05,  # 5% decline threshold
        }
    
    def validate_evaluation_results(self, results_file: str) -> dict[str, Any]:
        """Validate evaluation results against quality gates and baselines."""
        try:
            with open(results_file) as f:
                results_data = json.load(f)
        except Exception as e:
            return {
                "status": "fail",
                "error": f"Failed to load results file: {e}",
                "message": "Cannot validate results"
            }
        
        # Extract metrics - handle both old format (overall_metrics) and new format (summary)
        overall_metrics = results_data.get("overall_metrics", {})
        case_results = results_data.get("case_results", [])
        
        # If no overall_metrics, try to extract from summary (new smoke runner format)
        if not overall_metrics:
            summary = results_data.get("summary", {})
            if summary:
                # Convert summary to overall_metrics format for compatibility
                overall_metrics = {
                    "precision": summary.get("success_rate", 0) / 100,  # Use success rate as proxy
                    "recall": summary.get("success_rate", 0) / 100,
                    "f1_score": summary.get("success_rate", 0) / 100,
                    "faithfulness": summary.get("success_rate", 0) / 100,
                    "retrieval_precision": summary.get("success_rate", 0) / 100,
                    "retrieval_recall": summary.get("success_rate", 0) / 100,
                }
                case_results = []  # No individual case results in smoke format
        
        if not overall_metrics:
            return {
                "status": "fail",
                "error": "No overall metrics found in results",
                "message": "Cannot validate without metrics"
            }
        
        # Validate quality gates
        quality_validation = self._validate_quality_gates(overall_metrics)
        
        # Validate baseline compliance
        baseline_validation = self._validate_baseline_compliance(overall_metrics)
        
        # Detect regressions
        regression_analysis = self._detect_regressions(overall_metrics)
        
        # Calculate overall status
        overall_status = self._calculate_overall_status(
            quality_validation, baseline_validation, regression_analysis
        )
        
        return {
            "status": overall_status,
            "quality_validation": quality_validation,
            "baseline_validation": baseline_validation,
            "regression_analysis": regression_analysis,
            "overall_metrics": overall_metrics,
            "case_count": len(case_results),
            "timestamp": datetime.now().isoformat(),
        }
    
    def validate_evaluation_results_from_dict(self, results_data: dict[str, Any]) -> dict[str, Any]:
        """Validate evaluation results from dictionary data."""
        # Extract metrics
        overall_metrics = results_data.get("overall_metrics", {})
        case_results = results_data.get("case_results", [])
        
        if not overall_metrics:
            return {
                "status": "fail",
                "error": "No overall metrics found in results",
                "message": "Cannot validate without metrics"
            }
        
        # Validate quality gates
        quality_validation = self._validate_quality_gates(overall_metrics)
        
        # Validate baseline compliance
        baseline_validation = self._validate_baseline_compliance(overall_metrics)
        
        # Detect regressions
        regression_analysis = self._detect_regressions(overall_metrics)
        
        # Calculate overall status
        overall_status = self._calculate_overall_status(
            quality_validation, baseline_validation, regression_analysis
        )
        
        return {
            "status": overall_status,
            "quality_validation": quality_validation,
            "baseline_validation": baseline_validation,
            "regression_analysis": regression_analysis,
            "overall_metrics": overall_metrics,
            "case_count": len(case_results),
            "timestamp": datetime.now().isoformat(),
        }
    
    def _validate_quality_gates(self, metrics: dict[str, Any]) -> dict[str, Any]:
        """Validate metrics against quality gates."""
        violations = []
        passed_metrics = []
        
        for metric, threshold in self.quality_thresholds.items():
            current_value = metrics.get(metric, 0.0)
            if current_value < threshold:
                violations.append({
                    "metric": metric,
                    "current": current_value,
                    "threshold": threshold,
                    "deficit": threshold - current_value,
                    "deficit_percent": ((threshold - current_value) / threshold) * 100
                })
            else:
                passed_metrics.append({
                    "metric": metric,
                    "current": current_value,
                    "threshold": threshold,
                    "excess": current_value - threshold,
                    "excess_percent": ((current_value - threshold) / threshold) * 100
                })
        
        return {
            "status": "pass" if not violations else "fail",
            "violations": violations,
            "passed_metrics": passed_metrics,
            "violation_count": len(violations),
            "pass_count": len(passed_metrics),
        }
    
    def _validate_baseline_compliance(self, metrics: dict[str, Any]) -> dict[str, Any]:
        """Validate metrics against baseline compliance."""
        if not self.baseline_metrics:
            return {
                "status": "warn",
                "message": "No baseline metrics available for compliance checking",
                "baseline_available": False
            }
        
        compliance_issues = []
        compliant_metrics = []
        
        for metric, baseline_value in self.baseline_metrics.items():
            current_value = metrics.get(metric, 0.0)
            if current_value < baseline_value * 0.95:  # 5% tolerance
                compliance_issues.append({
                    "metric": metric,
                    "current": current_value,
                    "baseline": baseline_value,
                    "deficit": baseline_value - current_value,
                    "deficit_percent": ((baseline_value - current_value) / baseline_value) * 100
                })
            else:
                compliant_metrics.append({
                    "metric": metric,
                    "current": current_value,
                    "baseline": baseline_value,
                    "improvement": current_value - baseline_value,
                    "improvement_percent": ((current_value - baseline_value) / baseline_value) * 100
                })
        
        return {
            "status": "pass" if not compliance_issues else "fail",
            "compliance_issues": compliance_issues,
            "compliant_metrics": compliant_metrics,
            "issue_count": len(compliance_issues),
            "compliant_count": len(compliant_metrics),
            "baseline_available": True
        }
    
    def _detect_regressions(self, metrics: dict[str, Any]) -> dict[str, Any]:
        """Detect regressions from baseline metrics."""
        if not self.baseline_metrics:
            return {
                "status": "warn",
                "message": "No baseline metrics available for regression detection",
                "regressions": []
            }
        
        regressions = []
        improvements = []
        
        for metric, baseline_value in self.baseline_metrics.items():
            current_value = metrics.get(metric, 0.0)
            threshold = self.regression_thresholds.get(metric, 0.10)
            
            if current_value < baseline_value * (1 - threshold):
                regressions.append({
                    "metric": metric,
                    "current": current_value,
                    "baseline": baseline_value,
                    "decline": baseline_value - current_value,
                    "decline_percent": ((baseline_value - current_value) / baseline_value) * 100,
                    "threshold": threshold,
                    "severity": "high" if current_value < baseline_value * 0.8 else "medium"
                })
            elif current_value > baseline_value * (1 + threshold):
                improvements.append({
                    "metric": metric,
                    "current": current_value,
                    "baseline": baseline_value,
                    "improvement": current_value - baseline_value,
                    "improvement_percent": ((current_value - baseline_value) / baseline_value) * 100
                })
        
        return {
            "status": "pass" if not regressions else "fail",
            "regressions": regressions,
            "improvements": improvements,
            "regression_count": len(regressions),
            "improvement_count": len(improvements),
            "high_severity_regressions": [r for r in regressions if r["severity"] == "high"]
        }
    
    def _calculate_overall_status(self, quality_validation: dict[str, Any], 
                                 baseline_validation: dict[str, Any], 
                                 regression_analysis: dict[str, Any]) -> str:
        """Calculate overall validation status."""
        # Check for critical failures
        if quality_validation["status"] == "fail":
            return "fail"
        
        if baseline_validation["status"] == "fail":
            return "fail"
        
        if regression_analysis["status"] == "fail":
            return "fail"
        
        # Check for warnings
        if (quality_validation["status"] == "warn" or 
            baseline_validation["status"] == "warn" or 
            regression_analysis["status"] == "warn"):
            return "warn"
        
        return "pass"
    
    def generate_governance_report(self, validation_results: dict[str, Any]) -> dict[str, Any]:
        """Generate comprehensive governance report."""
        report = {
            "governance_summary": {
                "overall_status": validation_results.get("status", "unknown"),
                "profile": self.profile,
                "timestamp": validation_results.get("timestamp", datetime.now().isoformat()),
                "quality_gates": validation_results.get("quality_validation", {}).get("status", "unknown"),
                "baseline_compliance": validation_results.get("baseline_validation", {}).get("status", "unknown"),
                "regression_status": validation_results.get("regression_analysis", {}).get("status", "unknown"),
            },
            "quality_metrics": {
                "violations": validation_results.get("quality_validation", {}).get("violations", []),
                "passed_metrics": validation_results.get("quality_validation", {}).get("passed_metrics", []),
                "violation_count": validation_results.get("quality_validation", {}).get("violation_count", 0),
            },
            "baseline_metrics": {
                "compliance_issues": validation_results.get("baseline_validation", {}).get("compliance_issues", []),
                "compliant_metrics": validation_results.get("baseline_validation", {}).get("compliant_metrics", []),
                "issue_count": validation_results.get("baseline_validation", {}).get("issue_count", 0),
            },
            "regression_analysis": {
                "regressions": validation_results.get("regression_analysis", {}).get("regressions", []),
                "improvements": validation_results.get("regression_analysis", {}).get("improvements", []),
                "high_severity_regressions": validation_results.get("regression_analysis", {}).get("high_severity_regressions", []),
            },
            "recommendations": self._generate_recommendations(validation_results),
        }
        
        return report
    
    def save_governance_report(self, validation_results: dict[str, Any]) -> str:
        """Generate and save governance report to file."""
        import json
        import time
        from pathlib import Path
        
        report = self.generate_governance_report(validation_results)
        
        # Save governance report
        output_dir = Path("metrics/governance_reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = output_dir / f"governance_report_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        return str(report_file)
    
    def _generate_recommendations(self, validation_results: dict[str, Any]) -> list[str]:
        """Generate actionable recommendations based on validation results."""
        recommendations = []
        
        # Quality gate recommendations
        quality_validation = validation_results.get("quality_validation", {})
        if quality_validation.get("violations"):
            recommendations.append(
                f"Address {quality_validation.get('violation_count', 0)} quality gate violations"
            )
        
        # Baseline compliance recommendations
        baseline_validation = validation_results.get("baseline_validation", {})
        if baseline_validation.get("compliance_issues"):
            recommendations.append(
                f"Improve {baseline_validation.get('issue_count', 0)} baseline compliance issues"
            )
        
        # Regression recommendations
        regression_analysis = validation_results.get("regression_analysis", {})
        if regression_analysis.get("regressions"):
            high_severity = regression_analysis.get("high_severity_regressions", [])
            if high_severity:
                recommendations.append(
                    f"URGENT: Address {len(high_severity)} high-severity regressions"
                )
            else:
                recommendations.append(
                    f"Address {regression_analysis.get('regression_count', 0)} regressions"
                )
        
        # General recommendations
        status = validation_results.get("status", "unknown")
        if status == "pass":
            recommendations.append("Maintain current performance levels")
        elif status == "warn":
            recommendations.append("Monitor metrics closely for potential issues")
        else:
            recommendations.append("Immediate action required to restore quality")
        
        return recommendations
    
    def enforce_governance_gates(self, results_file: str) -> bool:
        """Enforce governance gates and return whether evaluation should proceed."""
        validation_results = self.validate_evaluation_results(results_file)
        
        # Print governance report
        self.print_governance_report(validation_results)
        
        # Determine if evaluation should proceed
        if validation_results["status"] == "fail":
            print("🚨 GOVERNANCE GATE FAILED: Evaluation blocked due to quality issues")
            return False
        elif validation_results["status"] == "warn":
            print("⚠️ GOVERNANCE GATE WARNING: Evaluation allowed but quality issues detected")
            return True
        else:
            print("✅ GOVERNANCE GATE PASSED: Evaluation quality meets standards")
            return True
    
    def print_governance_report(self, validation_results: dict[str, Any]):
        """Print comprehensive governance report."""
        print("\n" + "=" * 60)
        print("🏛️ GOVERNANCE GATING REPORT")
        print("=" * 60)
        
        # Overall status
        status_icon = "✅" if validation_results["status"] == "pass" else "❌" if validation_results["status"] == "fail" else "⚠️"
        print(f"📊 Overall Status: {status_icon} {validation_results['status'].upper()}")
        
        # Quality gates
        quality_validation = validation_results.get("quality_validation", {})
        quality_status = quality_validation.get("status", "unknown")
        quality_icon = "✅" if quality_status == "pass" else "❌" if quality_status == "fail" else "⚠️"
        print(f"🎯 Quality Gates: {quality_icon} {quality_status.upper()}")
        
        if quality_validation.get("violations"):
            print(f"   Violations: {quality_validation.get('violation_count', 0)}")
            for violation in quality_validation.get("violations", [])[:3]:  # Show first 3
                print(f"     • {violation.get('metric', 'unknown')}: {violation.get('current', 0):.3f} < {violation.get('threshold', 0):.3f}")
        
        # Baseline compliance
        baseline_validation = validation_results.get("baseline_validation", {})
        baseline_status = baseline_validation.get("status", "unknown")
        baseline_icon = "✅" if baseline_status == "pass" else "❌" if baseline_status == "fail" else "⚠️"
        print(f"📈 Baseline Compliance: {baseline_icon} {baseline_status.upper()}")
        
        if baseline_validation.get("compliance_issues"):
            print(f"   Issues: {baseline_validation.get('issue_count', 0)}")
        
        # Regression analysis
        regression_analysis = validation_results.get("regression_analysis", {})
        regression_status = regression_analysis.get("status", "unknown")
        regression_icon = "✅" if regression_status == "pass" else "❌" if regression_status == "fail" else "⚠️"
        print(f"📉 Regression Analysis: {regression_icon} {regression_status.upper()}")
        
        if regression_analysis.get("regressions"):
            print(f"   Regressions: {regression_analysis.get('regression_count', 0)}")
            high_severity = regression_analysis.get("high_severity_regressions", [])
            if high_severity:
                print(f"   High Severity: {len(high_severity)}")
        
        print("=" * 60)


def main():
    """Main entry point for governance gating system."""
    
    parser = argparse.ArgumentParser(description="Governance gating system for evaluation quality")
    _ = parser.add_argument("results_file", help="Path to evaluation results file")
    _ = parser.add_argument("--profile", default="gold", choices=["gold", "real", "mock"], 
                       help="Evaluation profile for governance rules")
    _ = parser.add_argument("--enforce", action="store_true", 
                       help="Enforce governance gates (block if failed)")
    
    args = parser.parse_args()
    
    # Initialize governance system
    governance = GovernanceGatingSystem(args.profile)
    
    # Validate results
    validation_results = governance.validate_evaluation_results(args.results_file)
    
    # Generate and save report
    report = governance.generate_governance_report(validation_results)
    
    # Save governance report
    output_dir = Path("metrics/governance_reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = output_dir / f"governance_report_{int(time.time())}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"📁 Governance report saved to: {report_file}")
    
    # Enforce gates if requested
    if args.enforce:
        should_proceed = governance.enforce_governance_gates(args.results_file)
        sys.exit(0 if should_proceed else 1)
    else:
        # Just validate and report
        governance.print_governance_report(validation_results)
        sys.exit(0 if validation_results["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
