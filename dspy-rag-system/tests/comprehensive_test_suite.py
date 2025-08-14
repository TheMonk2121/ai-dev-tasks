#!/usr/bin/env python3
"""
⚠️ LEGACY COMPREHENSIVE TEST SUITE ⚠️

This file is LEGACY CODE and should NOT be used for new development.
Use the new marker-based approach instead:

✅ NEW APPROACH (Use This):
  ./run_tests.sh --tiers 1 --kinds smoke    # Fast PR gate
  ./run_tests.sh --tiers 1 --kinds unit     # Critical unit tests
  ./run_tests.sh --tiers 1 2 --kinds integration  # Production integration

❌ LEGACY APPROACH (Avoid):
  python tests/comprehensive_test_suite.py  # This file

This file is maintained for backward compatibility only.
"""

import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import coverage

# Import psutil with fallback for missing dependency
try:
    import psutil  # type: ignore[import-untyped]
except ImportError:
    # Fallback implementation for when psutil is not available
    class MockPsutil:
        """Mock psutil implementation for when the package is not available"""

        class Process:
            def __init__(self):
                pass

            def memory_info(self):
                class MemoryInfo:
                    def __init__(self):
                        self.rss = 0

                return MemoryInfo()

            def cpu_percent(self, interval=None):
                return 0.0

        @staticmethod
        def cpu_percent(interval=None):
            return 0.0

    psutil = MockPsutil()

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import with fallbacks for missing modules
try:
    from utils.logger import setup_logger
except ImportError:

    def setup_logger(name):
        import logging

        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)


try:
    from src.utils.config_manager import ConfigManager as SrcConfigManager

    ConfigManager = SrcConfigManager  # type: ignore[assignment]
except ImportError:

    class ConfigManager:
        def __init__(self):
            pass


try:
    from src.utils.security import SecurityScanner as SrcSecurityScanner

    # Use SecurityScanner as SecurityValidator for compatibility
    SecurityValidator = SrcSecurityScanner  # type: ignore
except ImportError:

    class SecurityValidator:
        def __init__(self):
            pass


try:
    from src.utils.retry_wrapper import retry
except ImportError:

    def retry(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


# Setup logging
logger = setup_logger(__name__)

# Check if psutil is available and warn if using mock
if not hasattr(psutil, "Process") or not hasattr(psutil.Process(), "memory_info"):
    logger.warning("⚠️ psutil not available - using mock implementation for system metrics")


@dataclass
class TestResult:
    """Test result data structure"""

    test_name: str
    test_category: str
    status: str  # 'passed', 'failed', 'skipped', 'error'
    duration: float
    memory_usage: float
    cpu_usage: float
    coverage_percentage: Optional[float] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TestSuiteConfig:
    """Configuration for test suite execution"""

    parallel_execution: bool = True
    max_workers: int = 4
    timeout_seconds: int = 300
    coverage_threshold: float = 80.0
    performance_threshold: float = 2.0  # seconds
    memory_threshold: float = 512.0  # MB
    security_scan: bool = True
    generate_report: bool = True
    test_categories: Optional[List[str]] = None

    def __post_init__(self):
        if self.test_categories is None:
            self.test_categories = ["unit", "integration", "e2e", "performance", "security"]


class ComprehensiveTestSuite:
    """Advanced testing suite with comprehensive capabilities"""

    def __init__(self, config: Optional[TestSuiteConfig] = None):
        self.config = config or TestSuiteConfig()
        self.results: List[TestResult] = []
        self.coverage_data = {}
        self.performance_metrics = {}
        self.security_issues = []
        self.test_start_time = None
        self.test_end_time = None

        # Initialize coverage
        self.cov = coverage.Coverage()

        # Setup test categories
        self.test_categories = {
            "unit": self._get_unit_tests,
            "integration": self._get_integration_tests,
            "e2e": self._get_e2e_tests,
            "performance": self._get_performance_tests,
            "security": self._get_security_tests,
        }

    def run_comprehensive_suite(self) -> Dict[str, Any]:
        """Run the complete testing suite"""
        logger.info("🚀 Starting Comprehensive Test Suite")
        self.test_start_time = datetime.now()

        try:
            # Start coverage collection
            self.cov.start()

            # Run tests by category
            if self.config.test_categories:
                for category in self.config.test_categories:
                    if category in self.test_categories:
                        logger.info(f"📋 Running {category} tests...")
                        self._run_test_category(category)

            # Stop coverage collection
            self.cov.stop()
            self.cov.save()

            # Analyze coverage
            self._analyze_coverage()

            # Run security scan if enabled
            if self.config.security_scan:
                self._run_security_scan()

            # Generate comprehensive report
            if self.config.generate_report:
                report = self._generate_comprehensive_report()
                self._save_report(report)
                return report

        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            raise

        finally:
            self.test_end_time = datetime.now()

        # Return empty report if no report was generated
        return {
            "test_suite_info": {"name": "Comprehensive Test Suite T-4.1", "error": "No report generated"},
            "test_summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0,
                "success_rate": 0,
            },
            "performance_metrics": {
                "average_duration_seconds": 0,
                "average_memory_mb": 0,
                "average_cpu_percent": 0,
                "meets_performance_threshold": True,
            },
            "coverage_data": {},
            "security_scan": {"total_issues": 0, "high_severity": 0, "medium_severity": 0, "low_severity": 0},
            "test_results": [],
            "recommendations": [],
        }

    def _run_test_category(self, category: str):
        """Run tests for a specific category"""
        test_files = self.test_categories[category]()

        if not test_files:
            logger.warning(f"⚠️ No test files found for category: {category}")
            return

        if self.config.parallel_execution:
            self._run_parallel_tests(category, test_files)
        else:
            self._run_sequential_tests(category, test_files)

    def _run_parallel_tests(self, category: str, test_files: List[str]):
        """Run tests in parallel"""
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = []
            for test_file in test_files:
                future = executor.submit(self._run_single_test, category, test_file)
                futures.append(future)

            for future in as_completed(futures):
                try:
                    result = future.result(timeout=self.config.timeout_seconds)
                    self.results.append(result)
                except Exception as e:
                    logger.error(f"❌ Test execution failed: {e}")

    def _run_sequential_tests(self, category: str, test_files: List[str]):
        """Run tests sequentially"""
        for test_file in test_files:
            try:
                result = self._run_single_test(category, test_file)
                self.results.append(result)
            except Exception as e:
                logger.error(f"❌ Test execution failed: {e}")

    def _run_single_test(self, category: str, test_file: str) -> TestResult:
        """Run a single test file and collect metrics"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        start_cpu = psutil.Process().cpu_percent()

        try:
            # Run pytest on the test file
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
            )

            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            end_cpu = psutil.Process().cpu_percent()

            duration = end_time - start_time
            memory_usage = end_memory - start_memory
            cpu_usage = (start_cpu + end_cpu) / 2

            # Determine test status
            if result.returncode == 0:
                status = "passed"
                error_message = None
                stack_trace = None
            else:
                status = "failed"
                error_message = result.stderr
                stack_trace = result.stdout

            return TestResult(
                test_name=os.path.basename(test_file),
                test_category=category,
                status=status,
                duration=duration,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                error_message=error_message,
                stack_trace=stack_trace,
            )

        except subprocess.TimeoutExpired:
            return TestResult(
                test_name=os.path.basename(test_file),
                test_category=category,
                status="timeout",
                duration=self.config.timeout_seconds,
                memory_usage=0,
                cpu_usage=0,
                error_message="Test execution timed out",
            )
        except Exception as e:
            return TestResult(
                test_name=os.path.basename(test_file),
                test_category=category,
                status="error",
                duration=0,
                memory_usage=0,
                cpu_usage=0,
                error_message=str(e),
            )

    def _get_unit_tests(self) -> List[str]:
        """Get list of unit test files"""
        test_dir = Path(__file__).parent
        unit_tests = [
            "test_logger.py",
            "test_tokenizer.py",
            "test_metadata_extractor.py",
            "test_prompt_sanitizer.py",
            "test_timeout_config.py",
            "test_validator.py",
        ]
        return [str(test_dir / test) for test in unit_tests if (test_dir / test).exists()]

    def _get_integration_tests(self) -> List[str]:
        """Get list of integration test files"""
        test_dir = Path(__file__).parent
        integration_tests = [
            "test_document_processor.py",
            "test_rag_system.py",
            "test_vector_store.py",
            "test_enhanced_rag_system.py",
            "test_database_resilience.py",
            "test_n8n_integration.py",
        ]
        return [str(test_dir / test) for test in integration_tests if (test_dir / test).exists()]

    def _get_e2e_tests(self) -> List[str]:
        """Get list of end-to-end test files"""
        test_dir = Path(__file__).parent
        e2e_tests = ["test_mission_dashboard.py", "test_watch_folder.py", "test_backlog_scrubber.py"]
        return [str(test_dir / test) for test in e2e_tests if (test_dir / test).exists()]

    def _get_performance_tests(self) -> List[str]:
        """Get list of performance test files"""
        # Create performance test if it doesn't exist
        performance_test = Path(__file__).parent / "test_performance.py"
        if not performance_test.exists():
            self._create_performance_test(performance_test)
        return [str(performance_test)]

    def _get_security_tests(self) -> List[str]:
        """Get list of security test files"""
        test_dir = Path(__file__).parent
        security_tests = ["test_security.py", "test_secrets_manager.py", "test_enhanced_file_validator.py"]
        return [str(test_dir / test) for test in security_tests if (test_dir / test).exists()]

    def _create_performance_test(self, test_file: Path):
        """Create a performance test file"""
        performance_test_content = '''#!/usr/bin/env python3
"""
Performance Tests for DSPy RAG System
"""
import pytest
import time
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor
from src.enhanced_rag_system import EnhancedRAGSystem
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class TestPerformance:
    """Performance test suite"""

    def test_rag_system_response_time(self):
        """Test RAG system response time under load"""
        rag_system = EnhancedRAGSystem()

        # Test query response time
        start_time = time.time()
        response = rag_system.ask_question("What is the main purpose of this system?")
        end_time = time.time()

        response_time = end_time - start_time
        assert response_time < 5.0, f"Response time {response_time}s exceeds 5s threshold"

        logger.info(f"✅ RAG system response time: {response_time:.2f}s")

    def test_concurrent_queries(self):
        """Test system performance under concurrent load"""
        rag_system = EnhancedRAGSystem()

        def make_query(query_id):
            start_time = time.time()
            response = rag_system.ask_question(f"Test query {query_id}")
            end_time = time.time()
            return end_time - start_time

        # Run 5 concurrent queries
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_query, i) for i in range(5)]
            response_times = [future.result() for future in futures]

        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)

        assert avg_response_time < 3.0, f"Average response time {avg_response_time}s exceeds 3s threshold"
        assert max_response_time < 10.0, f"Max response time {max_response_time}s exceeds 10s threshold"

        logger.info(f"✅ Concurrent queries - Avg: {avg_response_time:.2f}s, Max: {max_response_time:.2f}s")

    def test_memory_usage(self):
        """Test memory usage during operation"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        rag_system = EnhancedRAGSystem()

        # Perform multiple operations
        for i in range(10):
            rag_system.ask_question(f"Memory test query {i}")

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        assert memory_increase < 100.0, f"Memory increase {memory_increase}MB exceeds 100MB threshold"

        logger.info(f"✅ Memory usage - Initial: {initial_memory:.1f}MB, Final: {final_memory:.1f}MB, Increase: {memory_increase:.1f}MB")

    def test_cpu_usage(self):
        """Test CPU usage during operation"""
        rag_system = EnhancedRAGSystem()

        # Monitor CPU usage during query
        cpu_percentages = []
        def monitor_cpu():
            while not hasattr(self, '_stop_monitoring'):
                cpu_percentages.append(psutil.cpu_percent(interval=0.1))

        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()

        # Perform query
        response = rag_system.ask_question("CPU usage test query")

        # Stop monitoring
        self._stop_monitoring = True
        monitor_thread.join()

        avg_cpu = sum(cpu_percentages) / len(cpu_percentages) if cpu_percentages else 0
        max_cpu = max(cpu_percentages) if cpu_percentages else 0

        assert avg_cpu < 80.0, f"Average CPU usage {avg_cpu}% exceeds 80% threshold"
        assert max_cpu < 95.0, f"Max CPU usage {max_cpu}% exceeds 95% threshold"

        logger.info(f"✅ CPU usage - Avg: {avg_cpu:.1f}%, Max: {max_cpu:.1f}%")
'''

        with open(test_file, "w") as f:
            f.write(performance_test_content)

        logger.info(f"✅ Created performance test: {test_file}")

    def _analyze_coverage(self):
        """Analyze test coverage"""
        try:
            # Load coverage data
            self.cov.load()

            # Get coverage statistics
            total_statements = 0
            covered_statements = 0

            # Get coverage data for all files
            coverage_data = self.cov.get_data()

            for filename in coverage_data.measured_files():
                if filename.startswith("src/"):
                    analysis = self.cov.analysis2(filename)
                    if analysis:
                        statements, missing, excluded, missing_branches, excluded_branches = analysis
                        total_statements += len(statements)
                        covered_statements += len(statements) - len(missing)

            if total_statements > 0:
                coverage_percentage = (covered_statements / total_statements) * 100
                self.coverage_data = {
                    "total_statements": total_statements,
                    "covered_statements": covered_statements,
                    "coverage_percentage": coverage_percentage,
                    "meets_threshold": coverage_percentage >= self.config.coverage_threshold,
                }

                logger.info(f"📊 Coverage: {coverage_percentage:.1f}% ({covered_statements}/{total_statements})")

                if not self.coverage_data["meets_threshold"]:
                    logger.warning(
                        f"⚠️ Coverage {coverage_percentage:.1f}% below threshold {self.config.coverage_threshold}%"
                    )

        except Exception as e:
            logger.error(f"❌ Coverage analysis failed: {e}")

    def _run_security_scan(self):
        """Run security scanning"""
        logger.info("🔒 Running security scan...")

        try:
            # Run bandit security scan
            result = subprocess.run(["bandit", "-r", "src/", "-f", "json"], capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                security_data = json.loads(result.stdout)
                self.security_issues = security_data.get("results", [])

                high_severity = [issue for issue in self.security_issues if issue.get("issue_severity") == "HIGH"]
                medium_severity = [issue for issue in self.security_issues if issue.get("issue_severity") == "MEDIUM"]

                logger.info(f"🔒 Security scan complete - High: {len(high_severity)}, Medium: {len(medium_severity)}")

                if high_severity:
                    logger.warning(f"⚠️ {len(high_severity)} high severity security issues found")

            else:
                logger.warning("⚠️ Security scan failed")

        except Exception as e:
            logger.error(f"❌ Security scan error: {e}")

    def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "passed"])
        failed_tests = len([r for r in self.results if r.status == "failed"])
        skipped_tests = len([r for r in self.results if r.status == "skipped"])

        # Calculate performance metrics
        avg_duration = sum(r.duration for r in self.results) / total_tests if total_tests > 0 else 0
        avg_memory = sum(r.memory_usage for r in self.results) / total_tests if total_tests > 0 else 0
        avg_cpu = sum(r.cpu_usage for r in self.results) / total_tests if total_tests > 0 else 0

        # Test duration
        test_duration = 0
        if self.test_end_time and self.test_start_time:
            test_duration = (self.test_end_time - self.test_start_time).total_seconds()

        report = {
            "test_suite_info": {
                "name": "Comprehensive Test Suite T-4.1",
                "start_time": self.test_start_time.isoformat() if self.test_start_time else None,
                "end_time": self.test_end_time.isoformat() if self.test_end_time else None,
                "duration_seconds": test_duration,
            },
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            },
            "performance_metrics": {
                "average_duration_seconds": avg_duration,
                "average_memory_mb": avg_memory,
                "average_cpu_percent": avg_cpu,
                "meets_performance_threshold": avg_duration <= self.config.performance_threshold,
            },
            "coverage_data": self.coverage_data,
            "security_scan": {
                "total_issues": len(self.security_issues),
                "high_severity": len([i for i in self.security_issues if i.get("issue_severity") == "HIGH"]),
                "medium_severity": len([i for i in self.security_issues if i.get("issue_severity") == "MEDIUM"]),
                "low_severity": len([i for i in self.security_issues if i.get("issue_severity") == "LOW"]),
            },
            "test_results": [asdict(result) for result in self.results],
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # Coverage recommendations
        if self.coverage_data and not self.coverage_data.get("meets_threshold", True):
            recommendations.append("Increase test coverage to meet threshold requirements")

        # Performance recommendations
        if self.performance_metrics.get("average_duration_seconds", 0) > self.config.performance_threshold:
            recommendations.append("Optimize test execution time to meet performance thresholds")

        # Security recommendations
        high_severity_issues = len([i for i in self.security_issues if i.get("issue_severity") == "HIGH"])
        if high_severity_issues > 0:
            recommendations.append(f"Address {high_severity_issues} high severity security issues")

        # Test failure recommendations
        failed_tests = [r for r in self.results if r.status == "failed"]
        if failed_tests:
            recommendations.append(f"Investigate and fix {len(failed_tests)} failed tests")

        return recommendations

    def _save_report(self, report: Dict[str, Any]):
        """Save test report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"test_report_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"📄 Test report saved: {report_file}")

        # Also save a human-readable summary
        summary_file = f"test_summary_{timestamp}.txt"
        with open(summary_file, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("COMPREHENSIVE TEST SUITE REPORT\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Test Suite: {report['test_suite_info']['name']}\n")
            f.write(f"Duration: {report['test_suite_info']['duration_seconds']:.1f} seconds\n\n")

            f.write("TEST SUMMARY:\n")
            f.write(f"  Total Tests: {report['test_summary']['total_tests']}\n")
            f.write(f"  Passed: {report['test_summary']['passed_tests']}\n")
            f.write(f"  Failed: {report['test_summary']['failed_tests']}\n")
            f.write(f"  Success Rate: {report['test_summary']['success_rate']:.1f}%\n\n")

            if report["coverage_data"]:
                f.write("COVERAGE:\n")
                f.write(f"  Coverage: {report['coverage_data']['coverage_percentage']:.1f}%\n")
                f.write(f"  Meets Threshold: {report['coverage_data']['meets_threshold']}\n\n")

            f.write("SECURITY:\n")
            f.write(f"  Total Issues: {report['security_scan']['total_issues']}\n")
            f.write(f"  High Severity: {report['security_scan']['high_severity']}\n")
            f.write(f"  Medium Severity: {report['security_scan']['medium_severity']}\n\n")

            if report["recommendations"]:
                f.write("RECOMMENDATIONS:\n")
                for rec in report["recommendations"]:
                    f.write(f"  - {rec}\n")

        logger.info(f"📄 Test summary saved: {summary_file}")


def main():
    """Main entry point for comprehensive test suite"""
    import argparse

    import pytest

    # Import our marker utilities
    try:
        from framework.selectors import build_marker_expression, get_suggested_markers, validate_marker_expression
    except ImportError:
        # Fallback if framework not available
        def build_marker_expression(*args, **kwargs) -> Optional[str]:
            return None

        def validate_marker_expression(expr: str) -> bool:
            return True

        def get_suggested_markers() -> dict:
            return {}

    parser = argparse.ArgumentParser(description="Comprehensive Test Suite T-4.1")

    # Legacy arguments (preserved for backward compatibility)
    parser.add_argument(
        "--categories",
        nargs="+",
        choices=["unit", "integration", "e2e", "performance", "security"],
        default=["unit", "integration", "e2e", "performance", "security"],
        help="Test categories to run (legacy mode)",
    )

    # New marker-based arguments
    parser.add_argument("--tiers", nargs="*", default=[], help="Select tiers: 1 2 3 or tier1 tier2 tier3")
    parser.add_argument("--kinds", nargs="*", default=[], help="Test kinds: unit integration e2e smoke")
    parser.add_argument("--markers", default="", help="Raw pytest -m expression to combine/override")
    parser.add_argument("--legacy-files", action="store_true", help="Force legacy file-list selection")
    parser.add_argument(
        "--min-cov", type=float, help="Minimum coverage threshold (forwards to pytest --cov-fail-under)"
    )
    parser.add_argument("--strict-markers", action="store_true", help="Enable strict marker validation")

    # Existing arguments
    parser.add_argument("--parallel", action="store_true", default=True, help="Run tests in parallel")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=300, help="Test timeout in seconds")
    parser.add_argument("--coverage-threshold", type=float, default=80.0, help="Coverage threshold percentage")
    parser.add_argument("--no-security-scan", action="store_true", help="Skip security scanning")
    parser.add_argument("--no-report", action="store_true", help="Skip report generation")
    parser.add_argument("--show-suggestions", action="store_true", help="Show suggested marker combinations")

    args, unknown = parser.parse_known_args()

    # Handle suggestions
    if args.show_suggestions:
        suggestions = get_suggested_markers()
        print("Suggested marker combinations:")
        print("=" * 50)
        for desc, expr in suggestions.items():
            print(f"{desc:25} -> --markers '{expr}'")
        print("\nExamples:")
        print("  Fast PR Gate:     --tiers 1 --kinds smoke")
        print("  Critical Units:   --tiers 1 --kinds unit")
        print("  Production Tests: --tiers 1 2 --kinds integration")
        print("  Custom:           --markers 'tier1 and not e2e'")
        return

    # Build marker expression
    marker_expr = None
    if args.tiers or args.kinds or args.markers:
        marker_expr = build_marker_expression(tiers=args.tiers, kinds=args.kinds, extra_expr=args.markers)
        logger.info(
            f"🔧 Built marker expression: '{marker_expr}' from tiers={args.tiers}, kinds={args.kinds}, markers={args.markers}"
        )

        if marker_expr:
            logger.info(f"🎯 Using marker expression: {marker_expr}")

            # Validate marker expression
            if not validate_marker_expression(marker_expr):
                logger.warning("⚠️ Invalid marker expression, falling back to legacy mode")
                marker_expr = None
        else:
            logger.info("ℹ️ No marker filter specified, running all tests")

    # Handle legacy mode
    if args.legacy_files:
        logger.info("🔄 Legacy file-based selection active")
        marker_expr = None

    # Determine execution mode
    logger.info(f"🔍 Execution decision: marker_expr='{marker_expr}', legacy_files={args.legacy_files}")
    if marker_expr and not args.legacy_files:
        # Marker-based execution
        logger.info("🚀 Running marker-based test selection")

        # Build pytest arguments
        pytest_args = ["-q", "-ra"]  # Quiet with summary, as suggested by ChatGPT

        # Add strict markers if requested
        if args.strict_markers:
            pytest_args.append("--strict-markers")

        if marker_expr:
            pytest_args.extend(["-m", marker_expr])

        # Add coverage if requested
        if args.min_cov:
            pytest_args.extend(["--cov=src", f"--cov-fail-under={args.min_cov}"])
        else:
            pytest_args.extend(["--cov=src", "--cov-report=term-missing"])

        # Add unknown arguments (pass through to pytest)
        pytest_args.extend(unknown)

        # Run pytest directly
        logger.info(f"🔧 pytest args: {' '.join(pytest_args)}")
        exit_code = pytest.main(pytest_args)

        # Generate basic report for marker-based runs
        print("\n" + "=" * 60)
        print("MARKER-BASED TEST EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Marker Expression: {marker_expr}")
        print(f"Exit Code: {exit_code}")
        print("=" * 60)

        sys.exit(exit_code)
    else:
        # Legacy execution (existing comprehensive suite)
        logger.info("🔄 Running legacy comprehensive test suite")

        config = TestSuiteConfig(
            test_categories=args.categories,
            parallel_execution=args.parallel,
            max_workers=args.workers,
            timeout_seconds=args.timeout,
            coverage_threshold=args.coverage_threshold,
            security_scan=not args.no_security_scan,
            generate_report=not args.no_report,
        )

        test_suite = ComprehensiveTestSuite(config)
        report = test_suite.run_comprehensive_suite()

    # Print summary
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST SUITE SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {report['test_summary']['total_tests']}")
    print(f"Passed: {report['test_summary']['passed_tests']}")
    print(f"Failed: {report['test_summary']['failed_tests']}")
    print(f"Success Rate: {report['test_summary']['success_rate']:.1f}%")

    if report["coverage_data"]:
        print(f"Coverage: {report['coverage_data']['coverage_percentage']:.1f}%")

    print(f"Security Issues: {report['security_scan']['total_issues']}")
    print("=" * 60)

    # Exit with appropriate code
    if report["test_summary"]["failed_tests"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
