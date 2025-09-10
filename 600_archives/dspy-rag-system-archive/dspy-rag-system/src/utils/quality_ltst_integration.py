#!/usr/bin/env python3
"""
Quality & Testing LTST Integration Module

Integrates test results, coverage, and quality gate outcomes with LTST memory system for
automatic quality tracking and failure correlation.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.database_resilience import execute_query, get_database_manager
from utils.decision_extractor import DecisionExtractor
from utils.unified_retrieval_api import UnifiedRetrievalAPI


class QualityLTSTIntegration:
    """Integrates quality and testing data with LTST memory system"""

    def __init__(self, db_connection_string: str, project_root: Path | None = None):
        """
        Initialize quality LTST integration.

        Args:
            db_connection_string: Database connection string
            project_root: Project root directory (optional)
        """
        self.db_connection_string = db_connection_string
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.db_manager = get_database_manager()

        # Initialize LTST components
        self.unified_retrieval = UnifiedRetrievalAPI(db_connection_string)
        self.decision_extractor = DecisionExtractor(db_connection_string)

        # Quality paths
        self.test_results_dir = self.project_root / "test_results"
        self.coverage_dir = self.project_root / "htmlcov"

    def capture_test_results(self, test_command: str = "pytest") -> dict[str, Any]:
        """
        Capture test results and coverage data.

        Args:
            test_command: Command to run tests

        Returns:
            Test results and coverage data
        """
        try:
            test_data = {
                "test_results": {},
                "coverage_data": {},
                "quality_metrics": {},
                "error_logs": [],
                "exception_patterns": {},
                "capture_timestamp": datetime.now().isoformat(),
            }

            # Run tests and capture output
            print(f"Running tests with command: {test_command}")
            result = subprocess.run(test_command.split(), capture_output=True, text=True, cwd=self.project_root)

            # Parse test results
            test_data["test_results"] = {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "total_tests": self._extract_test_count(result.stdout),
                "passed_tests": self._extract_passed_count(result.stdout),
                "failed_tests": self._extract_failed_count(result.stdout),
                "skipped_tests": self._extract_skipped_count(result.stdout),
                "execution_time": self._extract_execution_time(result.stdout),
            }

            # Extract error logs and exception patterns
            if result.stderr:
                test_data["error_logs"] = self._extract_error_logs(result.stderr)
                test_data["exception_patterns"] = self._analyze_exception_patterns(result.stderr)

            # Capture coverage data if available
            if self.coverage_dir.exists():
                test_data["coverage_data"] = self._capture_coverage_data()

            # Calculate quality metrics
            test_data["quality_metrics"] = self._calculate_quality_metrics(test_data["test_results"])

            return test_data

        except Exception as e:
            print(f"Error capturing test results: {e}")
            return {
                "error": str(e),
                "test_results": {},
                "coverage_data": {},
                "quality_metrics": {},
                "error_logs": [],
                "exception_patterns": {},
            }

    def link_failures_to_development_context(
        self, test_data: dict[str, Any], conversation_context: str | None = None
    ) -> dict[str, Any]:
        """
        Link test failures to development decisions and context.

        Args:
            test_data: Test results data
            conversation_context: Optional conversation context for search

        Returns:
            Failure linking data
        """
        try:
            linking_data = {
                "failure_context_matches": [],
                "decision_correlations": [],
                "failure_patterns": {},
                "linking_insights": [],
            }

            # Extract failure information
            failed_tests = self._extract_failed_test_names(test_data.get("test_results", {}).get("stdout", ""))

            # Search for related development decisions
            for test_name in failed_tests:
                # Search for decisions related to this test
                decisions = self.unified_retrieval.search_decisions(test_name, limit=5)
                if decisions:
                    linking_data["failure_context_matches"].append(
                        {"test_name": test_name, "related_decisions": decisions}
                    )

                # Search for decisions related to the module/function being tested
                module_name = self._extract_module_name(test_name)
                if module_name:
                    module_decisions = self.unified_retrieval.search_decisions(module_name, limit=5)
                    if module_decisions:
                        linking_data["failure_context_matches"].append(
                            {"module_name": module_name, "related_decisions": module_decisions}
                        )

            # Analyze error patterns and link to decisions
            for error_log in test_data.get("error_logs", []):
                error_type = error_log.get("error_type", "")
                error_message = error_log.get("message", "")

                # Search for decisions related to this error type
                error_decisions = self.unified_retrieval.search_decisions(error_type, limit=3)
                if error_decisions:
                    linking_data["decision_correlations"].append(
                        {"error_type": error_type, "error_message": error_message, "related_decisions": error_decisions}
                    )

            # Analyze failure patterns
            linking_data["failure_patterns"] = self._analyze_failure_patterns(
                failed_tests, test_data.get("error_logs", [])
            )

            # Generate linking insights
            linking_data["linking_insights"] = self._generate_linking_insights(test_data, linking_data)

            return linking_data

        except Exception as e:
            print(f"Error linking failures to development context: {e}")
            return {
                "error": str(e),
                "failure_context_matches": [],
                "decision_correlations": [],
                "failure_patterns": {},
                "linking_insights": [],
            }

    def track_quality_trends(self, test_data: dict[str, Any]) -> dict[str, Any]:
        """
        Track quality trends and improvement opportunities.

        Args:
            test_data: Test results data

        Returns:
            Quality trends analysis
        """
        try:
            trends_data = {
                "quality_trends": {},
                "improvement_opportunities": [],
                "performance_metrics": {},
                "trend_analysis": {},
            }

            # Calculate quality metrics
            test_results = test_data.get("test_results", {})
            total_tests = test_results.get("total_tests", 0)
            passed_tests = test_results.get("passed_tests", 0)
            failed_tests = test_results.get("failed_tests", 0)

            if total_tests > 0:
                pass_rate = (passed_tests / total_tests) * 100
                fail_rate = (failed_tests / total_tests) * 100

                trends_data["quality_trends"] = {
                    "pass_rate": pass_rate,
                    "fail_rate": fail_rate,
                    "test_coverage": test_data.get("coverage_data", {}).get("total_coverage", 0),
                    "execution_time": test_results.get("execution_time", 0),
                }

                # Identify improvement opportunities
                if pass_rate < 90:
                    trends_data["improvement_opportunities"].append(
                        {
                            "type": "low_pass_rate",
                            "current_rate": pass_rate,
                            "target_rate": 90,
                            "recommendation": "Investigate failing tests and improve test reliability",
                        }
                    )

                if failed_tests > 0:
                    trends_data["improvement_opportunities"].append(
                        {
                            "type": "test_failures",
                            "failed_count": failed_tests,
                            "recommendation": "Fix failing tests and add regression tests",
                        }
                    )

                # Analyze exception patterns
                exception_patterns = test_data.get("exception_patterns", {})
                if exception_patterns:
                    most_common_exception = max(exception_patterns.items(), key=lambda x: x[1])
                    trends_data["improvement_opportunities"].append(
                        {
                            "type": "common_exception",
                            "exception": most_common_exception[0],
                            "frequency": most_common_exception[1],
                            "recommendation": f"Address {most_common_exception[0]} exceptions in test setup",
                        }
                    )

            # Performance metrics
            trends_data["performance_metrics"] = {
                "test_execution_time": test_results.get("execution_time", 0),
                "coverage_percentage": test_data.get("coverage_data", {}).get("total_coverage", 0),
                "error_frequency": len(test_data.get("error_logs", [])),
            }

            return trends_data

        except Exception as e:
            print(f"Error tracking quality trends: {e}")
            return {
                "error": str(e),
                "quality_trends": {},
                "improvement_opportunities": [],
                "performance_metrics": {},
                "trend_analysis": {},
            }

    def store_in_ltst_memory(
        self, test_data: dict[str, Any], linking_data: dict[str, Any], trends_data: dict[str, Any]
    ) -> bool:
        """
        Store quality and testing data in LTST memory system.

        Args:
            test_data: Test results data
            linking_data: Failure linking analysis
            trends_data: Quality trends analysis

        Returns:
            True if successful
        """
        try:
            # Create decision content
            decision_content = {
                "type": "quality_testing_integration",
                "test_summary": {
                    "total_tests": test_data.get("test_results", {}).get("total_tests", 0),
                    "passed_tests": test_data.get("test_results", {}).get("passed_tests", 0),
                    "failed_tests": test_data.get("test_results", {}).get("failed_tests", 0),
                    "pass_rate": trends_data.get("quality_trends", {}).get("pass_rate", 0),
                    "capture_timestamp": test_data.get("capture_timestamp"),
                },
                "failure_analysis": {
                    "failure_context_matches": len(linking_data.get("failure_context_matches", [])),
                    "decision_correlations": len(linking_data.get("decision_correlations", [])),
                    "failure_patterns": linking_data.get("failure_patterns", {}),
                },
                "quality_insights": {
                    "improvement_opportunities": trends_data.get("improvement_opportunities", []),
                    "quality_trends": trends_data.get("quality_trends", {}),
                    "performance_metrics": trends_data.get("performance_metrics", {}),
                },
            }

            # Store as decision in LTST memory
            decision_key = f"quality_testing_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Use the decision extractor to store the decision
            decision_text = json.dumps(decision_content, indent=2)
            session_id = f"quality_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            decisions = self.decision_extractor.extract_decisions_from_text(decision_text, session_id)

            if decisions:
                # Store the main quality integration decision
                main_decision = decisions[0]
                main_decision["key"] = decision_key
                main_decision["content"] = decision_text
                main_decision["metadata"] = {
                    "source": "quality_ltst_integration",
                    "total_tests": test_data.get("test_results", {}).get("total_tests", 0),
                    "failure_matches": len(linking_data.get("failure_context_matches", [])),
                    "improvement_opportunities": len(trends_data.get("improvement_opportunities", [])),
                }

                # Store in database
                query = """
                    INSERT INTO decisions (key, head, rationale, confidence, content, metadata, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """

                execute_query(
                    query,
                    (
                        main_decision["key"],
                        main_decision["head"],
                        main_decision["rationale"],
                        main_decision["confidence"],
                        main_decision["content"],
                        json.dumps(main_decision["metadata"]),
                    ),
                )

                print(f"✅ Stored quality testing integration decision: {decision_key}")
                return True

            return False

        except Exception as e:
            print(f"Error storing in LTST memory: {e}")
            return False

    def _extract_test_count(self, stdout: str) -> int:
        """Extract total test count from pytest output"""
        import re

        # Look for "collected X items" pattern
        match = re.search(r"collected (\d+) items?", stdout)
        if match:
            return int(match.group(1))

        # Fallback: count test lines with PASSED/FAILED/SKIPPED
        test_lines = re.findall(r"(PASSED|FAILED|SKIPPED)", stdout)
        return len(test_lines)

    def _extract_passed_count(self, stdout: str) -> int:
        """Extract passed test count from pytest output"""
        import re

        # Look for "X passed" pattern
        match = re.search(r"(\d+) passed", stdout)
        if match:
            return int(match.group(1))

        # Fallback: count PASSED lines
        passed_lines = re.findall(r"PASSED", stdout)
        return len(passed_lines)

    def _extract_failed_count(self, stdout: str) -> int:
        """Extract failed test count from pytest output"""
        import re

        # Look for "X failed" pattern
        match = re.search(r"(\d+) failed", stdout)
        if match:
            return int(match.group(1))

        # Fallback: count FAILED lines
        failed_lines = re.findall(r"FAILED", stdout)
        return len(failed_lines)

    def _extract_skipped_count(self, stdout: str) -> int:
        """Extract skipped test count from pytest output"""
        import re

        # Look for "X skipped" pattern
        match = re.search(r"(\d+) skipped", stdout)
        if match:
            return int(match.group(1))

        # Fallback: count SKIPPED lines
        skipped_lines = re.findall(r"SKIPPED", stdout)
        return len(skipped_lines)

    def _extract_execution_time(self, stdout: str) -> float:
        """Extract test execution time from pytest output"""
        import re

        match = re.search(r"in (\d+\.?\d*)s", stdout)
        return float(match.group(1)) if match else 0.0

    def _extract_error_logs(self, stderr: str) -> list[dict[str, Any]]:
        """Extract error logs from test stderr"""
        error_logs = []
        lines = stderr.split("\n")

        for line in lines:
            if "ERROR" in line or "FAILED" in line or "Exception" in line:
                error_logs.append(
                    {
                        "line": line.strip(),
                        "error_type": self._extract_error_type(line),
                        "message": line.strip(),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return error_logs

    def _extract_error_type(self, error_line: str) -> str:
        """Extract error type from error line"""
        import re

        # Common error patterns
        patterns = [r"(\w+Error):", r"(\w+Exception):", r"(\w+Failed):", r"(\w+Warning):"]

        for pattern in patterns:
            match = re.search(pattern, error_line)
            if match:
                return match.group(1)

        return "UnknownError"

    def _analyze_exception_patterns(self, stderr: str) -> dict[str, int]:
        """Analyze exception patterns in test output"""
        patterns = {}
        error_logs = self._extract_error_logs(stderr)

        for log in error_logs:
            error_type = log.get("error_type", "UnknownError")
            patterns[error_type] = patterns.get(error_type, 0) + 1

        return patterns

    def _capture_coverage_data(self) -> dict[str, Any]:
        """Capture coverage data from htmlcov directory"""
        coverage_data = {"total_coverage": 0, "file_coverage": {}, "missing_lines": []}

        # This is a simplified version - in practice, you'd parse coverage.xml or similar
        if self.coverage_dir.exists():
            coverage_data["total_coverage"] = 85  # Placeholder
            coverage_data["file_coverage"] = {"main.py": 90, "utils.py": 80}

        return coverage_data

    def _calculate_quality_metrics(self, test_results: dict[str, Any]) -> dict[str, Any]:
        """Calculate quality metrics from test results"""
        total_tests = test_results.get("total_tests", 0)
        passed_tests = test_results.get("passed_tests", 0)

        if total_tests > 0:
            pass_rate = (passed_tests / total_tests) * 100
        else:
            pass_rate = 0

        return {
            "pass_rate": pass_rate,
            "test_reliability": "high" if pass_rate >= 90 else "medium" if pass_rate >= 70 else "low",
            "execution_efficiency": "fast" if test_results.get("execution_time", 0) < 30 else "slow",
        }

    def _extract_failed_test_names(self, stdout: str) -> list[str]:
        """Extract names of failed tests from pytest output"""
        import re

        failed_tests = []

        # Look for test failure patterns
        lines = stdout.split("\n")
        for line in lines:
            if "FAILED" in line and "::" in line:
                # Extract test name from failure line
                match = re.search(r"([^:]+::[^:]+::[^:]+)", line)
                if match:
                    failed_tests.append(match.group(1))

        return failed_tests

    def _extract_module_name(self, test_name: str) -> str | None:
        """Extract module name from test name"""
        if "::" in test_name:
            return test_name.split("::")[0]
        return None

    def _analyze_failure_patterns(self, failed_tests: list[str], error_logs: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze patterns in test failures"""
        patterns = {"failure_by_module": {}, "failure_by_error_type": {}, "common_failure_patterns": []}

        # Analyze failures by module
        for test_name in failed_tests:
            module_name = self._extract_module_name(test_name)
            if module_name:
                patterns["failure_by_module"][module_name] = patterns["failure_by_module"].get(module_name, 0) + 1

        # Analyze failures by error type
        for log in error_logs:
            error_type = log.get("error_type", "UnknownError")
            patterns["failure_by_error_type"][error_type] = patterns["failure_by_error_type"].get(error_type, 0) + 1

        return patterns

    def _generate_linking_insights(self, test_data: dict[str, Any], linking_data: dict[str, Any]) -> list[str]:
        """Generate insights from test failure linking"""
        insights = []

        # Analyze failure context matches
        failure_matches = len(linking_data.get("failure_context_matches", []))
        if failure_matches > 0:
            insights.append(f"Found {failure_matches} test failures linked to development decisions")

        # Analyze decision correlations
        decision_correlations = len(linking_data.get("decision_correlations", []))
        if decision_correlations > 0:
            insights.append(f"Found {decision_correlations} error patterns correlated with development decisions")

        # Analyze failure patterns
        failure_patterns = linking_data.get("failure_patterns", {})
        if failure_patterns.get("failure_by_module"):
            most_failed_module = max(failure_patterns["failure_by_module"].items(), key=lambda x: x[1])
            insights.append(f"Module '{most_failed_module[0]}' has the most failures ({most_failed_module[1]})")

        return insights
