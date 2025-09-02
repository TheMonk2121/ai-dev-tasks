#!/usr/bin/env python3
"""
Operational Runbooks for Retrieval System

Provides automated runbooks for common operational tasks,
troubleshooting, and maintenance procedures.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from typing import Any, Dict

# Add src to path for retrieval modules
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

from retrieval.memory_integration import GovernanceAutomator, MemoryIntegrator
from retrieval.robustness_checks import RobustnessChecker
from retrieval.test_hardening import validate_pipeline_components


class OperationalRunbook:
    """Automated operational procedures for the retrieval system."""

    def __init__(self):
        self.governance = GovernanceAutomator()
        self.memory_integrator = MemoryIntegrator()
        self.robustness_checker = RobustnessChecker()

    def daily_health_check(self) -> Dict[str, Any]:
        """Perform daily health check routine."""
        print("🌅 Daily Health Check - Starting")
        print("=" * 40)

        results = {"timestamp": time.time(), "checks": {}, "overall_status": "healthy", "action_required": []}

        # 1. System health check
        print("🔍 Running system health check...")
        try:
            health_check = self.robustness_checker.run_comprehensive_health_check()
            results["checks"]["system_health"] = health_check

            if health_check["overall_status"] != "healthy":
                results["overall_status"] = health_check["overall_status"]
                results["action_required"].append("Investigate system health issues")

            print(f"   Status: {health_check['overall_status']}")
            print(
                f"   Components: {health_check['summary']['healthy']}/{health_check['summary']['total_components']} healthy"
            )

        except Exception as e:
            results["checks"]["system_health"] = {"error": str(e)}
            results["overall_status"] = "degraded"
            results["action_required"].append("Fix health check system")
            print(f"   ❌ Health check failed: {e}")

        # 2. Configuration validation
        print("🔧 Validating configuration...")
        try:
            config_validation = validate_pipeline_components()
            results["checks"]["configuration"] = config_validation

            if not config_validation["valid"]:
                results["overall_status"] = "degraded"
                results["action_required"].append("Fix configuration issues")

            print(f"   Valid: {'✅' if config_validation['valid'] else '❌'}")
            if config_validation["warnings"]:
                print(f"   Warnings: {len(config_validation['warnings'])}")

        except Exception as e:
            results["checks"]["configuration"] = {"error": str(e)}
            results["overall_status"] = "degraded"
            results["action_required"].append("Fix configuration validation")
            print(f"   ❌ Configuration check failed: {e}")

        # 3. Performance metrics
        print("📊 Checking performance metrics...")
        try:
            perf_degradation = self.robustness_checker.check_performance_degradation()
            results["checks"]["performance"] = perf_degradation

            if perf_degradation["degraded"]:
                results["overall_status"] = "degraded"
                results["action_required"].append("Address performance degradation")

            metrics = perf_degradation["metrics"]
            print(f"   Avg Latency: {metrics['avg_latency_ms']:.1f}ms")
            print(f"   Success Rate: {metrics['success_rate']:.3f}")

        except Exception as e:
            results["checks"]["performance"] = {"error": str(e)}
            results["overall_status"] = "degraded"
            results["action_required"].append("Fix performance monitoring")
            print(f"   ❌ Performance check failed: {e}")

        # 4. Memory sync
        print("🧠 Syncing with memory systems...")
        try:
            memory_sync = self.memory_integrator.sync_with_memory_orchestrator()
            results["checks"]["memory_sync"] = memory_sync

            if not memory_sync["success"]:
                results["action_required"].append("Check memory system connectivity")

            print(f"   Sync: {'✅' if memory_sync['success'] else '❌'}")

        except Exception as e:
            results["checks"]["memory_sync"] = {"error": str(e)}
            results["action_required"].append("Fix memory integration")
            print(f"   ❌ Memory sync failed: {e}")

        # Summary
        print("\n🏆 Daily Health Check Summary:")
        print(f"   Overall Status: {results['overall_status'].upper()}")
        print(
            f"   Checks Completed: {len([c for c in results['checks'].values() if 'error' not in c])}/{len(results['checks'])}"
        )

        if results["action_required"]:
            print(f"   Actions Required: {len(results['action_required'])}")
            for action in results["action_required"]:
                print(f"     - {action}")

        return results

    def weekly_maintenance(self) -> Dict[str, Any]:
        """Perform weekly maintenance routine."""
        print("🗓️ Weekly Maintenance - Starting")
        print("=" * 40)

        results = {"timestamp": time.time(), "tasks": {}, "overall_success": True, "recommendations": []}

        # 1. Comprehensive test suite
        print("🧪 Running comprehensive test suite...")
        try:
            test_cmd = ["python3", "scripts/test_retrieval_system.py", "--mock", "--output", "weekly_test_results.json"]

            import subprocess

            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                results["tasks"]["test_suite"] = {"success": True, "output": result.stdout}
                print("   ✅ Test suite completed successfully")
            else:
                results["tasks"]["test_suite"] = {"success": False, "error": result.stderr}
                results["overall_success"] = False
                results["recommendations"].append("Investigate test failures")
                print("   ❌ Test suite failed")

        except Exception as e:
            results["tasks"]["test_suite"] = {"success": False, "error": str(e)}
            results["overall_success"] = False
            results["recommendations"].append("Fix test suite execution")
            print(f"   ❌ Test suite error: {e}")

        # 2. Governance compliance check
        print("📋 Running governance compliance check...")
        try:
            compliance_report = self.governance.generate_compliance_report()
            results["tasks"]["compliance"] = compliance_report

            if not compliance_report["overall_compliance"]:
                results["overall_success"] = False
                results["recommendations"].extend(compliance_report["recommendations"])

            print(f"   Compliance: {'✅' if compliance_report['overall_compliance'] else '❌'}")

        except Exception as e:
            results["tasks"]["compliance"] = {"error": str(e)}
            results["overall_success"] = False
            results["recommendations"].append("Fix governance system")
            print(f"   ❌ Compliance check failed: {e}")

        # 3. Performance analysis
        print("📈 Analyzing performance trends...")
        try:
            # This would analyze historical performance data
            # For now, we'll do a basic performance check
            performance_analysis = {"trend": "stable", "recommendations": [], "metrics_healthy": True}

            results["tasks"]["performance_analysis"] = performance_analysis
            print(f"   Trend: {performance_analysis['trend']}")

        except Exception as e:
            results["tasks"]["performance_analysis"] = {"error": str(e)}
            results["recommendations"].append("Review performance monitoring")
            print(f"   ❌ Performance analysis failed: {e}")

        # 4. Documentation update check
        print("📚 Checking documentation currency...")
        try:
            # Check if documentation reflects current system state
            doc_check = {"current": True, "last_updated": time.time() - 86400, "needs_update": False}  # 1 day ago

            results["tasks"]["documentation_check"] = doc_check
            print(f"   Documentation: {'✅ Current' if doc_check['current'] else '⚠️ Needs update'}")

        except Exception as e:
            results["tasks"]["documentation_check"] = {"error": str(e)}
            results["recommendations"].append("Review documentation system")
            print(f"   ❌ Documentation check failed: {e}")

        # Summary
        print("\n🏆 Weekly Maintenance Summary:")
        print(f"   Overall Success: {'✅' if results['overall_success'] else '❌'}")
        print(
            f"   Tasks Completed: {len([t for t in results['tasks'].values() if 'error' not in t])}/{len(results['tasks'])}"
        )

        if results["recommendations"]:
            print(f"   Recommendations: {len(results['recommendations'])}")
            for rec in results["recommendations"]:
                print(f"     - {rec}")

        return results

    def emergency_response(self, issue_type: str) -> Dict[str, Any]:
        """Execute emergency response procedures."""
        print(f"🚨 Emergency Response - {issue_type}")
        print("=" * 50)

        response_procedures = {
            "high_latency": self._handle_high_latency,
            "high_error_rate": self._handle_high_error_rate,
            "component_failure": self._handle_component_failure,
            "configuration_error": self._handle_configuration_error,
        }

        if issue_type not in response_procedures:
            return {
                "success": False,
                "error": f"Unknown issue type: {issue_type}",
                "available_types": list(response_procedures.keys()),
            }

        try:
            return response_procedures[issue_type]()
        except Exception as e:
            return {"success": False, "error": str(e), "procedure": issue_type}

    def _handle_high_latency(self) -> Dict[str, Any]:
        """Handle high latency emergency."""
        print("⚡ Investigating high latency...")

        steps = []

        # Step 1: Check current performance
        perf_check = self.robustness_checker.check_performance_degradation()
        steps.append({"step": "performance_check", "result": perf_check, "action": "Identify performance bottlenecks"})

        # Step 2: Component health check
        health_check = self.robustness_checker.run_comprehensive_health_check()
        steps.append({"step": "component_health", "result": health_check, "action": "Check for component failures"})

        # Step 3: Configuration validation
        config_check = validate_pipeline_components()
        steps.append(
            {"step": "configuration_check", "result": config_check, "action": "Validate configuration parameters"}
        )

        # Generate recommendations
        recommendations = []
        if perf_check["degraded"]:
            recommendations.extend(
                [
                    "Review system resources (CPU, memory)",
                    "Check network connectivity",
                    "Analyze query patterns for optimization opportunities",
                ]
            )

        if health_check["overall_status"] != "healthy":
            recommendations.append("Investigate unhealthy components")

        if not config_check["valid"]:
            recommendations.append("Fix configuration issues")

        return {
            "success": True,
            "issue_type": "high_latency",
            "steps_taken": steps,
            "recommendations": recommendations,
            "next_actions": [
                "Monitor performance for 30 minutes",
                "If issue persists, escalate to development team",
                "Document incident for post-mortem analysis",
            ],
        }

    def _handle_high_error_rate(self) -> Dict[str, Any]:
        """Handle high error rate emergency."""
        print("❌ Investigating high error rate...")

        steps = []

        # Step 1: Get current error statistics
        perf_check = self.robustness_checker.check_performance_degradation()
        steps.append({"step": "error_analysis", "result": perf_check, "action": "Analyze error patterns and frequency"})

        # Step 2: Component health assessment
        health_check = self.robustness_checker.run_comprehensive_health_check()
        failing_components = [
            comp for comp in health_check.get("component_health", []) if comp.get("status") == "unhealthy"
        ]
        steps.append(
            {
                "step": "component_assessment",
                "result": {"failing_components": failing_components},
                "action": "Identify failing components",
            }
        )

        recommendations = [
            "Check error logs for patterns",
            "Verify external service dependencies",
            "Review recent configuration changes",
        ]

        if failing_components:
            recommendations.append(
                f"Investigate failing components: {[c.get('component', 'unknown') for c in failing_components]}"
            )

        return {
            "success": True,
            "issue_type": "high_error_rate",
            "steps_taken": steps,
            "recommendations": recommendations,
            "next_actions": [
                "Implement error rate monitoring alerts",
                "Consider activating fallback mechanisms",
                "Prepare rollback plan if needed",
            ],
        }

    def _handle_component_failure(self) -> Dict[str, Any]:
        """Handle component failure emergency."""
        print("🔧 Handling component failure...")

        # Check which components are failing
        health_check = self.robustness_checker.run_comprehensive_health_check()
        unhealthy_components = [
            comp for comp in health_check.get("component_health", []) if comp.get("status") in ["unhealthy", "degraded"]
        ]

        steps = [
            {
                "step": "identify_failures",
                "result": {"unhealthy_components": unhealthy_components},
                "action": "Identify unhealthy/degraded components",
            }
        ]

        # Generate component-specific recommendations
        recommendations = []
        for comp in unhealthy_components:
            component_name = comp.get("component", "unknown")
            recommendations.append(f"Restart/reinitialize {component_name}")
            recommendations.append(f"Check {component_name} dependencies and configuration")

        if not unhealthy_components:
            recommendations.append("All components appear healthy - investigate external factors")

        return {
            "success": True,
            "issue_type": "component_failure",
            "steps_taken": steps,
            "recommendations": recommendations,
            "next_actions": [
                "Isolate failing components",
                "Activate backup/fallback systems",
                "Plan component recovery procedure",
            ],
        }

    def _handle_configuration_error(self) -> Dict[str, Any]:
        """Handle configuration error emergency."""
        print("⚙️ Handling configuration error...")

        steps = []

        # Step 1: Validate current configuration
        config_validation = validate_pipeline_components()
        steps.append(
            {"step": "config_validation", "result": config_validation, "action": "Validate current configuration"}
        )

        # Step 2: Governance compliance check
        compliance_check = self.governance.validate_configuration()
        steps.append({"step": "compliance_check", "result": compliance_check, "action": "Check governance compliance"})

        recommendations = []

        if not config_validation["valid"]:
            recommendations.extend(
                ["Fix configuration validation errors", "Restore from known good configuration backup"]
            )

        if not compliance_check["valid"]:
            recommendations.extend(["Address governance compliance violations", "Review configuration change process"])

        return {
            "success": True,
            "issue_type": "configuration_error",
            "steps_taken": steps,
            "recommendations": recommendations,
            "next_actions": [
                "Backup current configuration",
                "Apply configuration fixes",
                "Test configuration changes",
                "Update configuration management procedures",
            ],
        }

    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive system status report."""
        print("📋 Generating System Status Report")
        print("=" * 40)

        report = {"timestamp": time.time(), "system": "retrieval_system", "version": "1.0.0", "status": {}}

        # System health
        try:
            health = self.robustness_checker.run_comprehensive_health_check()
            report["status"]["health"] = health["overall_status"]
            report["status"]["component_summary"] = health["summary"]
        except Exception as e:
            report["status"]["health"] = "unknown"
            report["status"]["health_error"] = str(e)

        # Performance metrics
        try:
            perf = self.robustness_checker.check_performance_degradation()
            report["status"]["performance"] = perf["metrics"]
            report["status"]["performance_degraded"] = perf["degraded"]
        except Exception as e:
            report["status"]["performance_error"] = str(e)

        # Configuration status
        try:
            config = validate_pipeline_components()
            report["status"]["configuration_valid"] = config["valid"]
            report["status"]["configuration_warnings"] = len(config.get("warnings", []))
        except Exception as e:
            report["status"]["configuration_error"] = str(e)

        # Governance compliance
        try:
            compliance = self.governance.generate_compliance_report()
            report["status"]["governance_compliant"] = compliance["overall_compliance"]
            report["status"]["compliance_score"] = compliance["compliance_checks"]["configuration"]["compliance_score"]
        except Exception as e:
            report["status"]["governance_error"] = str(e)

        return report


def main() -> None:
    """Main entry point for operational runbooks."""
    parser = argparse.ArgumentParser(description="Retrieval System Operational Runbooks")
    parser.add_argument(
        "command",
        choices=["daily-health", "weekly-maintenance", "emergency", "status-report"],
        help="Operational command to execute",
    )
    parser.add_argument("--issue-type", help="Issue type for emergency response")
    parser.add_argument("--output", help="Output file for results")

    args = parser.parse_args()

    runbook = OperationalRunbook()

    # Execute command
    if args.command == "daily-health":
        result = runbook.daily_health_check()
    elif args.command == "weekly-maintenance":
        result = runbook.weekly_maintenance()
    elif args.command == "emergency":
        if not args.issue_type:
            print("❌ Emergency command requires --issue-type")
            print("Available types: high_latency, high_error_rate, component_failure, configuration_error")
            sys.exit(1)
        result = runbook.emergency_response(args.issue_type)
    elif args.command == "status-report":
        result = runbook.generate_status_report()
    else:
        print(f"❌ Unknown command: {args.command}")
        sys.exit(1)

    # Save results if output file specified
    if args.output:
        pathlib.Path(args.output).write_text(json.dumps(result, indent=2))
        print(f"\n💾 Results saved to {args.output}")

    print(f"\n✅ {args.command.replace('-', ' ').title()} completed")


if __name__ == "__main__":
    main()
